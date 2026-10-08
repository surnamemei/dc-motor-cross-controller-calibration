#!/usr/bin/env python3
"""Supplementary derivation steps that were first executed as inline commands during the
external-validation work (2026-10-08). The code below is the same logic, collected into
named stages so that every committed output has a scripted derivation. No stage changes
a model, threshold, split, exclusion or FAR value; stages either prepare inputs or
re-derive descriptive tables from already-computed outputs.

  python3 tools/derive_supplementary.py <stage>
Stages: extract_c, c_versions, c_units, a_optimizer_history, a_units_gap, a_posthoc, c_quant
"""
import datetime as dt
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent
CZ = ROOT / "raw" / "candidate_C_zenodo"


def extract_c():
    """Extract the Zenodo v1.0.0 archive unmodified (raw input, not redistributed)."""
    out = CZ / "extracted"
    out.mkdir(parents=True, exist_ok=True)
    zipfile.ZipFile(CZ / "etrls-str-stm32-v1.0.zip").extractall(out)


def c_versions():
    """v1.0.0 vs v2.0.0 run-log comparison and v2 per-file modification times."""
    z1 = zipfile.ZipFile(CZ / "etrls-str-stm32-v1.0.zip")
    z2 = zipfile.ZipFile(CZ / "etrls-str-stm32-v2.0.zip")

    def runs(z):
        return {n[n.index("hw_results"):]: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()
                if n.endswith(".csv") and "/run" in n and "hw_results" in n}
    r1, r2 = runs(z1), runs(z2)
    common = set(r1) & set(r2)
    same = [k for k in common if r1[k] == r2[k]]
    diff = [k for k in common if r1[k] != r2[k]]
    json.dump({"v1_runs": len(r1), "v2_runs": len(r2), "common": len(common), "identical": len(same),
               "changed": sorted(diff), "only_v1": sorted(set(r1) - set(r2)), "only_v2": sorted(set(r2) - set(r1))},
              open(CZ / "_v1_v2_run_comparison.json", "w"), indent=1)
    rows = []
    for i in z2.infolist():
        n = i.filename
        if "/hw_results/data/" in n and "/run" in n and n.endswith(".csv"):
            p = n[n.index("hw_results/data/"):].split("/")
            rows.append(dict(arm=p[2], scen=p[3], run=int(p[4][3:5]), t=dt.datetime(*i.date_time)))
    pd.DataFrame(rows).sort_values("t").to_csv(CZ / "_v2_run_mtimes.csv", index=False)


def c_units():
    """manifests/candidate_C_units.csv: benchmark runs with eligibility and recovered chronology."""
    R = pd.read_csv(ROOT / "manifests" / "candidate_C_runs.csv")
    M = pd.read_csv(CZ / "_v2_run_mtimes.csv", parse_dates=["t"])
    D = R[R.group == "data"].copy()
    D["run"] = D.file.str.extract(r"run(\d+)\.csv").astype(int)
    D = D.merge(M.rename(columns={"scen": "scenario", "t": "v2_file_mtime"}), on=["arm", "scenario", "run"], how="left")
    fixed = D.arm.isin(["ZN", "PT", "GS", "PSO"])
    nominal = D.scenario.isin(["S1", "S3"])
    D["eligibility"] = "EXCLUDED_scenario_disturbance_or_glitch"
    D.loc[nominal & ~fixed, "eligibility"] = "RESTRICTED_adaptive_controller_not_fixed_identity"
    D.loc[nominal & fixed, "eligibility"] = "ELIGIBLE_fixed_PI_nominal"
    D["acquisition_block"] = D.run.map(lambda r: "interleaved_pass_run01" if r == 1 else "arm_block_run02_11")
    D = D.sort_values("v2_file_mtime")
    cols = ["file", "sha256", "arm", "scenario", "run", "controller_type", "Kp", "Ki", "v2_file_mtime",
            "acquisition_block", "n_rows", "setpoint_profile", "output_min", "output_max", "eligibility"]
    D[cols].to_csv(ROOT / "manifests" / "candidate_C_units.csv", index=False)


def a_optimizer_history():
    """protocol/optimizer_history.csv: the authors' CEM history (adaptive_history.mat), metadata only."""
    h = sio.loadmat(ROOT / "raw" / "candidate_A_github" / "data" / "data_experiments_L298N_A90" / "adaptive_history.mat",
                    squeeze_me=True, struct_as_record=False)
    H = h["History"]
    D = pd.DataFrame({k: np.atleast_1d(getattr(H, k)) for k in ["gen", "idx", "Kp", "Ki", "Kd", "J", "P", "Mp", "Ts", "ef", "sat"]})
    D["kstar"] = D.Kp == 4.999010254763151
    D["opt_fail"] = D.J >= 1e12
    D.to_csv(ROOT / "protocol" / "optimizer_history.csv", index=False)


def a_units_gap():
    """Append the descriptive inter-run gap column (seconds) to the Candidate A unit file."""
    p = ROOT / "protocol" / "candidate_A_protocol_units.csv"
    U = pd.read_csv(p, parse_dates=["t"]).sort_values("t")
    U["gap_before_s"] = U.t.diff().dt.total_seconds()
    U.to_csv(p, index=False)


def _arx_scores_A(T, f):
    E = sio.loadmat(ROOT / "raw" / "candidate_A_github" / f, squeeze_me=True, struct_as_record=False)["E"]
    rr, y, u = (np.asarray(getattr(E.data, k), float) for k in "ryu")
    ua = u.copy(); ua[0] = 0; ua[np.abs(rr - y) < 0.5] = 0
    k = np.arange(21, 121)
    return k, np.abs(y[k] - np.column_stack([-y[k - 1], -y[k - 2], ua[k - 1], ua[k - 2]]) @ T)


def a_posthoc():
    """results_A: generation-pair table and the POST-HOC descriptive exceedance-location table."""
    p = pd.read_csv(ROOT / "results_A" / "per_run_far_primary.csv")
    g = p.pivot_table(index="gen", columns="role", values="far", aggfunc="mean")
    g["n_target_runs_with_exceedance"] = p[p.role == "target"].groupby("gen").far.apply(lambda s: (s > 0).sum())
    g["target_exceedance_samples"] = p[p.role == "target"].groupby("gen").far.sum() * 100
    g["d_g"] = g.target - g.source_holdout
    g.to_csv(ROOT / "results_A" / "generation_pairs_primary.csv")
    thr = json.load(open(ROOT / "results_A" / "calibration_threshold.json"))["threshold"]["primary"]
    th = json.load(open(ROOT / "protocol" / "candidate_A_arx_frozen.json"))["strata"]["2026-04-04"]["theta"]
    T = np.array([float(th[k]) for k in ("a1", "a2", "b1", "b2")])
    U = pd.read_csv(ROOT / "protocol" / "candidate_A_protocol_units.csv")
    U = U[U.day == "2026-04-04"]
    rows = []
    for _, r in U[U.role.isin(["source_calibration", "source_holdout", "target_evaluation"])].iterrows():
        k, s = _arx_scores_A(T, r.file)
        for kk in k[s > thr]:
            rows.append(dict(role=r.role, k=int(kk), t_after_step_s=(kk - 20) * 0.025))
    X = pd.DataFrame(rows)
    X["phase"] = pd.cut(X.t_after_step_s, [0, 0.1, 0.25, 0.5, 1.0, 2.6],
                        labels=["0-0.1s", "0.1-0.25s", "0.25-0.5s", "0.5-1s", "1-2.5s"])
    X.groupby(["role", "phase"], observed=False).size().unstack(fill_value=0).to_csv(
        ROOT / "results_A" / "posthoc_exceedance_location.csv")


def c_quant():
    """results_C: calibration-only quantisation diagnostic (descriptive)."""
    m = json.load(open(ROOT / "results_C" / "calibration_models.json"))["models"]
    S = json.load(open(ROOT / "protocol" / "candidate_C_splits.json"))
    base = CZ / "extracted" / "benchmark" / "hw_results"
    out = {}
    for s in ["S1", "S3"]:
        for A in ["ZN", "PT", "GS", "PSO"]:
            th = np.array([float(v) for v in m[f"{s}|{A}|primary"]["theta"]])
            thr = m[f"{s}|{A}|primary"]["threshold"]
            res, raw = [], []
            for x in S["scenarios"][s]["sources"][A]["calibration"]:
                d = pd.read_csv(base / x["file"])
                f = d.feedback.values; u = d.output.values; k = np.arange(2, len(f))
                X = np.column_stack([-f[k - 1], -f[k - 2], u[k - 1], u[k - 2], np.ones(len(k))])
                res.append(f[k] - X @ th)
                raw.append(np.abs(np.diff(d.speed.values))[k - 1] > 1)
            r = np.concatenate(res); rc = np.concatenate(raw)
            exc = np.abs(r) > thr
            out[f"{s}|{A}"] = dict(thr=round(thr, 3), thr_over_one_count_ema=round(thr / (0.05 * 62.2), 3),
                                   frac_exceed_coinciding_raw_speed_change=round(float(rc[exc].mean()), 3),
                                   frac_all_samples_with_raw_speed_change=round(float(rc.mean()), 3))
    json.dump(out, open(ROOT / "results_C" / "quantization_diagnostic_calibration.json", "w"), indent=1)


STAGES = {f.__name__: f for f in (extract_c, c_versions, c_units, a_optimizer_history, a_units_gap, a_posthoc, c_quant)}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in STAGES:
        sys.exit(f"usage: derive_supplementary.py {{{'|'.join(STAGES)}}}")
    STAGES[sys.argv[1]]()
