#!/usr/bin/env python3
"""Run inventory for Candidate C (Zenodo 10.5281/zenodo.21201595, ET-RLS-STR STM32 benchmark).

Reads every run log of benchmark/hw_results/{data,S5_pilot_n10_20260702,misseed,compare_500}
and records: columns, rows, time grid, non-physical rows, setpoint profile, output range,
exact-duplicate content, and the arm's controller definition from run_all_hw.py.
Integrity only: no residual, threshold or false-alarm statistic is computed.
"""
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "raw" / "candidate_C_zenodo" / "extracted" / "benchmark" / "hw_results"
OUT = ROOT / "manifests" / "candidate_C_runs.csv"
FIXED = {"ZN": (0.0089, 0.0280), "PT": (0.0393, 0.8491), "GS": (0.1000, 0.0010), "PSO": (0.0073, 0.0388)}
NOMINAL_PROFILE = {"S1": "500 -> 600 @ 8 s", "S3": "300 -> 500 @ 6 s -> 700 @ 12 s -> 400 @ 18 s"}


def profile(t, sp):
    ch = np.flatnonzero(np.diff(sp) != 0) + 1
    segs = [f"{sp[0]:g}"] + [f"{sp[i]:g}@{t[i]:.3f}s" for i in ch]
    return " -> ".join(segs)


rows = []
for f in sorted(BASE.rglob("*.csv")):
    rel = f.relative_to(BASE).as_posix()
    parts = rel.split("/")
    if parts[0] in ("analysis", "timing") or not f.name.startswith("run"):
        continue
    raw = f.read_bytes()
    d = pd.read_csv(f)
    num = d.apply(pd.to_numeric, errors="coerce")
    t = num["time"].to_numpy(float)
    sp = num["setpoint"].to_numpy(float)
    fb = num["feedback"].to_numpy(float)
    u = num["output"].to_numpy(float)
    dt = np.diff(t)
    group = parts[0]
    arm = parts[1] if group in ("data", "S5_pilot_n10_20260702") else parts[1] if len(parts) > 2 else ""
    scen = parts[2] if group in ("data", "S5_pilot_n10_20260702") and len(parts) > 3 else ""
    rows.append({
        "group": group, "file": rel, "sha256": hashlib.sha256(raw).hexdigest(), "arm": arm, "scenario": scen,
        "controller_type": ("fixed PI" if arm in FIXED else "adaptive STR (gains time-varying)" if arm == "STR"
                            else "learned RL PI-tuner (gains time-varying)" if arm == "RL" else ""),
        "Kp": FIXED.get(arm, ("", ""))[0], "Ki": FIXED.get(arm, ("", ""))[1],
        "columns": ";".join(d.columns), "n_rows": len(d),
        "n_nonnumeric_cells": int(num.isna().sum().sum()),
        "t_first": t[0], "t_last": t[-1],
        "dt_median_s": float(np.median(dt)), "n_dt_off_grid": int(np.sum(np.abs(dt - 0.005) > 1e-6)),
        "n_time_nonmonotone": int(np.sum(dt <= 0)),
        "setpoint_profile": profile(t, sp),
        "feedback_min": np.nanmin(fb), "feedback_max": np.nanmax(fb),
        "output_min": np.nanmin(u), "output_max": np.nanmax(u),
        "frac_output_at_abs_max": float(np.mean(np.abs(u) >= np.nanmax(np.abs(u)) - 1e-9)),
        "n_feedback_nonphysical": int(np.sum((fb < -50) | (fb > 1500))),
    })
R = pd.DataFrame(rows)
R["exact_duplicate_of"] = R.groupby("sha256").file.transform(lambda s: ";".join(s) if len(s) > 1 else "")
R.to_csv(OUT, index=False)
print(f"{len(R)} run logs -> {OUT}")
