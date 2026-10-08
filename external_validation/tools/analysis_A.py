#!/usr/bin/env python3
"""First external validation analysis, Candidate A stratum 2026-04-04.

Implements FROZEN_PROTOCOL_DRAFT.md as amended by results_A/PROTOCOL_AMENDMENT_01.md.
Order: verify hashes -> calibration threshold written -> THEN holdout/target residuals.
Nothing in this file may be changed after its first execution (see results_A/run_log.txt).
"""
import hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, scipy.io as sio
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "raw" / "candidate_A_github"
P, OUT = ROOT / "protocol", ROOT / "results_A"
EXPECTED = {
    "protocol/candidate_A_arx_frozen.json": "cf6997608312e1e52e20050acf24f910d949b7ef61ce2722dc07936da0341709",
    "protocol/candidate_A_protocol_units.csv": "60de3592bf2f7e4450dbfb0f8134899967fb797e35d34f446c399b6c5dedc61c",
    "FROZEN_PROTOCOL_DRAFT.md": "24a846c361a3f0688a98c59a3be6c19adec6a4993ce2e63e4e44902eae22a41f",
    "results_A/PROTOCOL_AMENDMENT_01.md": "b083da6d1e743bd34a6b5cee6d6c2d1717700efeb99abff2d83c3beffe39fb09",
}
DAY, DEADBAND, STEP_K = "2026-04-04", 0.5, 20
B, SEED = 600, 33043
LOG = []


def log(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}  {msg}"
    LOG.append(line)
    print(line)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- step 1: integrity
for rel, h in EXPECTED.items():
    if sha(ROOT / rel) != h:
        sys.exit(f"ABORT: {rel} changed since the amendment")
frozen = json.load(open(P / "candidate_A_arx_frozen.json"))
chk = {k: v for k, v in frozen.items() if k != "coefficients_sha256"}
if hashlib.sha256(json.dumps(chk, indent=2, sort_keys=True).encode()).hexdigest() != frozen["coefficients_sha256"]:
    sys.exit("ABORT: frozen coefficient hash mismatch")
th = frozen["strata"][DAY]["theta"]
THETA = np.array([float(th[k]) for k in ("a1", "a2", "b1", "b2")])
U = pd.read_csv(P / "candidate_A_protocol_units.csv")
U = U[U.day == DAY]
man = pd.read_csv(ROOT / "manifests" / "run_manifest.csv", low_memory=False).set_index("file")
CAL = U[U.role == "source_calibration"].sort_values("t")
HOLD = U[U.role == "source_holdout"].sort_values("t")
TGT = U[U.role == "target_evaluation"].sort_values("t")
assert len(CAL) == 9 and len(HOLD) == 6 and len(TGT) == 42
assert sorted(CAL.gen) == list(range(6, 15)) and sorted(HOLD.gen) == list(range(15, 21))
assert TGT.groupby("gen").size().eq(7).all()
for f in pd.concat([CAL, HOLD, TGT]).file:
    if sha(REPO / f) != man.loc[f, "sha256"]:
        sys.exit(f"ABORT: data file hash mismatch {f}")
log(f"integrity verified: {len(CAL)+len(HOLD)+len(TGT)} MAT files, frozen inputs, amendment")


def load(f):
    E = sio.loadmat(REPO / f, squeeze_me=True, struct_as_record=False)["E"]
    r, y, u = (np.asarray(getattr(E.data, k), float) for k in ("r", "y", "u"))
    ua = u.copy(); ua[0] = 0.0; ua[np.abs(r - y) < DEADBAND] = 0.0
    return dict(r=r, y=y, u=u, ua=ua)


def design(run, k0=21, k1=120):
    y, ua = run["y"], run["ua"]
    k = np.arange(k0, k1 + 1)
    return np.column_stack([-y[k - 1], -y[k - 2], ua[k - 1], ua[k - 2]]), y[k]


def scores(theta, run, k0=21, k1=120):
    X, Y = design(run, k0, k1)
    return np.abs(Y - X @ theta)


def fit(runs):
    X = np.vstack([design(r)[0] for r in runs]); Y = np.concatenate([design(r)[1] for r in runs])
    theta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    poles = np.roots([1.0, theta[0], theta[1]])
    reasons = []
    if not (np.isfinite(X).all() and np.isfinite(Y).all()): reasons.append("nonfinite_rows")
    if len(Y) < 800: reasons.append("rows_lt_800")
    if np.linalg.cond(X) >= 1e6: reasons.append("cond_ge_1e6")
    if np.any(np.abs(poles) > 1.02): reasons.append("pole_gt_1.02")
    if theta[2] + theta[3] <= 0: reasons.append("b1_plus_b2_le_0")
    return theta, reasons


def far(s, thr):
    return float(np.mean(s > thr))


# ---------------------------------------------------------------- step 2: calibration only
cal_runs = [load(f) for f in CAL.file]
CONFIGS = {"primary": (0.99, 21), "sens_b_5pct": (0.95, 21), "sens_c_k25": (0.99, 25)}
cal_scores = {c: [scores(THETA, r, k0) for r in cal_runs] for c, (q, k0) in CONFIGS.items()}
thr = {c: float(np.quantile(np.concatenate(cal_scores[c]), CONFIGS[c][0], method="higher")) for c in CONFIGS}
cal_far = {c: [far(s, thr[c]) for s in cal_scores[c]] for c in CONFIGS}
calrec = {"threshold": thr, "n_calibration_samples": {c: int(sum(len(s) for s in cal_scores[c])) for c in CONFIGS},
          "calibration_far_per_run": cal_far, "calibration_far_mean": {c: float(np.mean(v)) for c, v in cal_far.items()},
          "theta_frozen": THETA.tolist(), "calibration_files": CAL.file.tolist()}
(OUT / "calibration_threshold.json").write_text(json.dumps(calrec, indent=2) + "\n")
log(f"calibration threshold written BEFORE opening holdout/target: primary theta_99 = {thr['primary']!r}; "
    f"sha256 {sha(OUT / 'calibration_threshold.json')}")

# ---------------------------------------------------------------- step 3: holdout + targets
hold_runs = {f: load(f) for f in HOLD.file}
tgt_runs = {f: load(f) for f in TGT.file}
log("holdout and target files opened")
EXCL_A = set(TGT[TGT.run_eligibility == "ELIGIBLE_WITH_NOTE"].file)


def point(config, theta=THETA, threshold=None, exclude=()):
    q, k0 = CONFIGS["primary" if config == "sens_a_excl_note" else config]
    t_ = thr["primary" if config == "sens_a_excl_note" else config] if threshold is None else threshold
    rows = []
    for _, r in HOLD.iterrows():
        rows.append(dict(file=r.file, gen=r.gen, role="source_holdout", far=far(scores(theta, hold_runs[r.file], k0), t_)))
    for _, r in TGT.iterrows():
        if r.file in exclude: continue
        rows.append(dict(file=r.file, gen=r.gen, role="target", far=far(scores(theta, tgt_runs[r.file], k0), t_)))
    return pd.DataFrame(rows)


def summarise(df):
    g = df.pivot_table(index="gen", columns="role", values="far", aggfunc="mean")
    d = g["target"] - g["source_holdout"]
    return dict(holdout=float(g["source_holdout"].mean()), target=float(g["target"].mean()), D=float(d.mean()),
                d_g={int(k): float(v) for k, v in d.items()})


results = {}
for config in ["primary", "sens_a_excl_note", "sens_b_5pct", "sens_c_k25"]:
    excl = EXCL_A if config == "sens_a_excl_note" else ()
    df = point(config, exclude=excl)
    s = summarise(df)
    s["calibration_far"] = calrec["calibration_far_mean"]["primary" if config == "sens_a_excl_note" else config]
    s["threshold"] = thr["primary" if config == "sens_a_excl_note" else config]
    # ---- bootstrap (amendment 01)
    rng = np.random.default_rng(SEED)
    q, k0 = CONFIGS["primary" if config == "sens_a_excl_note" else config]
    gens = sorted(HOLD.gen.unique())
    draws, fails = [], {}
    for b in range(B):
        ci = rng.integers(0, 9, size=9)
        gi = rng.choice(gens, size=len(gens), replace=True)
        theta_b, reasons = fit([cal_runs[i] for i in ci])
        if reasons:
            for rr in reasons: fails[rr] = fails.get(rr, 0) + 1
            draws.append(dict(draw=b, ok=False, reason=";".join(reasons))); continue
        thr_b = float(np.quantile(np.concatenate([scores(theta_b, cal_runs[i], k0) for i in ci]), q, method="higher"))
        dfb = point(config, theta=theta_b, threshold=thr_b, exclude=excl)
        per_gen = dfb.pivot_table(index="gen", columns="role", values="far", aggfunc="mean")
        sel = per_gen.loc[gi]
        stat = dict(holdout=float(sel["source_holdout"].mean()), target=float(sel["target"].mean()),
                    D=float((sel["target"] - sel["source_holdout"]).mean()), threshold=thr_b)
        ok = all(np.isfinite(v) for v in stat.values())
        draws.append(dict(draw=b, ok=ok, reason="" if ok else "nonfinite_statistic", **stat))
        if not ok: fails["nonfinite_statistic"] = fails.get("nonfinite_statistic", 0) + 1
    bd = pd.DataFrame(draws); good = bd[bd.ok]
    s["bootstrap"] = {"B": B, "seed": SEED, "n_success": int(len(good)), "n_failed": int((~bd.ok).sum()),
                      "failure_reasons": fails,
                      **{f"{k}_ci95": [float(np.percentile(good[k], 2.5)), float(np.percentile(good[k], 97.5))]
                         for k in ("holdout", "target", "D", "threshold")},
                      "D_frac_draws_gt_0": float(np.mean(good.D > 0)), "D_frac_draws_lt_0": float(np.mean(good.D < 0))}
    bd.to_csv(OUT / f"bootstrap_draws_{config}.csv", index=False)
    if config == "primary":
        df.to_csv(OUT / "per_run_far_primary.csv", index=False)
    results[config] = s
    log(f"{config}: holdout {s['holdout']:.4f} target {s['target']:.4f} D {s['D']:+.4f} "
        f"CI {s['bootstrap']['D_ci95']} success {s['bootstrap']['n_success']}/{B}")

# ---------------------------------------------------------------- diagnostics (descriptive)
prim = pd.read_csv(OUT / "per_run_far_primary.csv")
kref = np.array([4.999010254763151, 8.00337810067222, 0.15694720663178266]); span = np.array([15, 10, 0.5])
diag = []
allruns = {**hold_runs, **tgt_runs}
for _, r in prim.iterrows():
    run = allruns[r.file]; m = U.set_index("file").loc[r.file]
    k = np.arange(21, 121); post = np.arange(STEP_K, 121)
    diag.append(dict(file=r.file, gen=r.gen, role=r.role, far=r.far,
                     sat_frac_post=float(np.mean(np.abs(run["u"][post]) >= 255)),
                     deadband_frac_window=float(np.mean(np.abs(run["r"][k] - run["y"][k]) < DEADBAND)),
                     peak_abs_u=float(np.max(np.abs(run["u"]))), overshoot_pct=float(m.overshoot_pct),
                     final_abs_error=float(m.final_abs_error), pos_in_gen=int(m.pos_in_gen),
                     gain_distance_to_kstar=float(np.sqrt((((np.array([m.Kp, m.Ki, m.Kd]) - kref) / span) ** 2).sum())),
                     Kp=m.Kp, Ki=m.Ki, Kd=m.Kd, opt_failure_penalty=bool(m.opt_failure_penalty)))
D_ = pd.DataFrame(diag); D_.to_csv(OUT / "diagnostics_per_run.csv", index=False)
corr = []
for col in ["sat_frac_post", "deadband_frac_window", "peak_abs_u", "overshoot_pct", "final_abs_error",
            "gain_distance_to_kstar", "Kp", "Ki", "Kd", "pos_in_gen"]:
    for subset, d in [("targets", D_[D_.role == "target"]), ("holdout+targets", D_)]:
        x = d[col].to_numpy(float)
        rho, p = spearmanr(x, d.far) if np.ptp(x) > 0 and np.ptp(d.far) > 0 else (np.nan, np.nan)
        corr.append(dict(diagnostic=col, subset=subset, n=len(d), spearman_rho=rho, p_unadjusted=p))
pd.DataFrame(corr).to_csv(OUT / "diagnostic_correlations.csv", index=False)

# ---------------------------------------------------------------- effective units
def lag1(score_lists, threshold):
    xs = [(s > threshold).astype(float) for s in score_lists]
    num = sum(np.sum((x[1:] - x.mean()) * (x[:-1] - x.mean())) for x in xs)
    den = sum(np.sum((x - x.mean()) ** 2) for x in xs)
    return float(num / den) if den > 0 else float("nan")


t_ = thr["primary"]
tg = prim[prim.role == "target"]
grp = tg.groupby("gen").far
k_ = 7; n_g = tg.gen.nunique()
msb = k_ * ((grp.mean() - tg.far.mean()) ** 2).sum() / (n_g - 1)
msw = ((tg.far - tg.gen.map(grp.mean())) ** 2).sum() / (len(tg) - n_g)
icc = float((msb - msw) / (msb + (k_ - 1) * msw)) if (msb + (k_ - 1) * msw) > 0 else float("nan")
units = {"calibration_runs": 9, "calibration_controllers": 1, "calibration_samples": 900,
         "holdout_runs": 6, "holdout_samples": 600, "target_runs": 42, "target_controllers": 42, "target_samples": 4200,
         "generation_pairs_independent_units_for_D": 6,
         "lag1_autocorr_exceedance": {"calibration": lag1(cal_scores["primary"], t_),
                                      "holdout": lag1([scores(THETA, r) for r in hold_runs.values()], t_),
                                      "targets": lag1([scores(THETA, r) for r in tgt_runs.values()], t_)},
         "target_far_icc_within_generation": icc,
         "target_effective_units_from_icc": float(42 / (1 + (k_ - 1) * max(icc, 0))) if np.isfinite(icc) else None,
         "runs_with_any_exceedance": {"holdout": int((prim[prim.role == 'source_holdout'].far > 0).sum()),
                                      "targets": int((tg.far > 0).sum())}}
summary = {"stratum": DAY, "amendment": "PROTOCOL_AMENDMENT_01.md", "results": results, "effective_units": units}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float) + "\n")
log("analysis complete")
(OUT / "run_log.txt").write_text("\n".join(LOG) + "\n" + f"analysis_A.py sha256 {sha(Path(__file__))}\n")
