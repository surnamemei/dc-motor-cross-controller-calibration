#!/usr/bin/env python3
"""Fit the frozen ARX(2,2,1) position model on SOURCE-CALIBRATION runs only (Task 1.7).

Model (per GO stratum, coefficients estimated once and frozen):
    y[k] = -a1*y[k-1] - a2*y[k-2] + b1*ua[k-1] + b2*ua[k-2] + e[k]
y   measured position [deg] (encoder, 1336 CPR, DPP = 0.269461066 deg)
ua  applied motor command [PWM counts]: the logged controller output u[k], set to 0 at k = 0
    and wherever |r[k] - y[k]| < 0.5 deg (firmware deadband policy stops the motor there)
rows k = 21..120 (0-based; the step is applied at k = 20, t = 500 ms), 100 rows per run;
regressors at k-1, k-2 use the recorded pre-step zeros.
Estimator: ordinary least squares (numpy.linalg.lstsq) pooled over the stratum's calibration runs.

Acceptance checks fixed before fitting (failure -> stratum STOP, no re-specification):
  * every regression row finite; at least 800 rows
  * condition number of the regressor matrix < 1e6
  * all model poles |p| <= 1.02 (integrating position plant: one pole near 1 expected)
  * b1 + b2 > 0 (positive command produces positive motion)
Only coefficients, poles and conditioning are written. No residual statistic, threshold,
holdout or target quantity is computed; holdout and target files are never opened.
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd, scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "raw" / "candidate_A_github"
P = ROOT / "protocol"
U = pd.read_csv(P / "candidate_A_protocol_units.csv")
SPLIT = json.load(open(P / "candidate_A_split.json"))
DEADBAND, STEP_K, K_FIRST, K_LAST = 0.5, 20, 21, 120


def applied_input(r, y, u):
    ua = u.astype(float).copy()
    ua[0] = 0.0
    ua[np.abs(r - y) < DEADBAND] = 0.0
    return ua


def rows(f):
    E = sio.loadmat(REPO / f, squeeze_me=True, struct_as_record=False)["E"]
    r, y, u = (np.asarray(getattr(E.data, k), float) for k in ("r", "y", "u"))
    assert len(y) == 121 and r[STEP_K] != 0 and r[STEP_K - 1] == 0
    ua = applied_input(r, y, u)
    k = np.arange(K_FIRST, K_LAST + 1)
    X = np.column_stack([-y[k - 1], -y[k - 2], ua[k - 1], ua[k - 2]])
    return X, y[k]


out = {"model": "ARX(2,2,1): y[k] = -a1 y[k-1] - a2 y[k-2] + b1 ua[k-1] + b2 ua[k-2]",
       "rows_per_run": K_LAST - K_FIRST + 1, "strata": {}}
for day, s in SPLIT["strata"].items():
    if s["decision"] != "GO":
        out["strata"][day] = {"decision": "STOP (split)", "fitted": False}
        continue
    files = U[(U.day == day) & (U.role == "source_calibration")].sort_values("t").file.tolist()
    assert len(files) == s["n_calibration"]
    Xs, Ys = zip(*(rows(f) for f in files))
    X, Y = np.vstack(Xs), np.concatenate(Ys)
    theta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    a1, a2, b1, b2 = theta
    poles = np.roots([1.0, a1, a2])
    cond = float(np.linalg.cond(X))
    checks = {"finite_rows": bool(np.isfinite(X).all() and np.isfinite(Y).all()),
              "rows_ge_800": bool(len(Y) >= 800), "cond_lt_1e6": cond < 1e6,
              "poles_abs_le_1.02": bool(np.all(np.abs(poles) <= 1.02)), "b1_plus_b2_gt_0": bool(b1 + b2 > 0)}
    out["strata"][day] = {
        "decision": "GO" if all(checks.values()) else "STOP (model acceptance)",
        "calibration_files": files,
        "calibration_file_sha256": [hashlib.sha256((REPO / f).read_bytes()).hexdigest() for f in files],
        "n_rows": int(len(Y)),
        "theta": {"a1": repr(float(a1)), "a2": repr(float(a2)), "b1": repr(float(b1)), "b2": repr(float(b2))},
        "poles": [complex(p).__repr__() for p in poles], "pole_abs": [float(abs(p)) for p in poles],
        "regressor_condition_number": cond, "acceptance_checks": checks,
    }
blob = json.dumps(out, indent=2, sort_keys=True)
out["coefficients_sha256"] = hashlib.sha256(blob.encode()).hexdigest()
(P / "candidate_A_arx_frozen.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({d: {k: v for k, v in s.items() if k not in ("calibration_files", "calibration_file_sha256")}
                  for d, s in out["strata"].items()}, indent=2))
print("coefficients_sha256", out["coefficients_sha256"])
