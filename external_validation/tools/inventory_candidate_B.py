#!/usr/bin/env python3
"""Run inventory for Candidate B (Mendeley Data 10.17632/5xvg43r9r8.2, OpenMCT kit).

Reads every primary raw text log (two metadata lines, a header line, comma
rows) and writes manifests/candidate_B_runs.csv. Controller parameters come
from the dataset's own parameter CSVs. No monitor, threshold or false-alarm
statistic is computed.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "raw" / "candidate_B_mendeley" / "files"
DS1 = ROOT / "raw" / "candidate_B_mendeley_v1" / "files"   # version 1 (2026-05-11), text files only
OUT = ROOT / "manifests" / "candidate_B_runs.csv"

PI = pd.read_csv(DS / "04_continuous_PID_validation" / "continuous_PI_controller_parameters.csv")
# version 1 deployed PI gains (positional PID, bilinear), from the v1 README table
PI_V1 = {5: (0.3085177468, 11.4739417375), 10: (0.7175107925, 14.1569402152),
         20: (0.3058791726, 9.7531024765), 50: (0.54971, 9.51492)}
DISC = pd.read_csv(DS / "05_discrete_controller_validation" / "discrete_controller_parameters.csv")


def classify(rel: str, version: int = 2):
    p = rel.split("/")
    if p[0] == "04_continuous_PID_validation" and version == 1:
        ts = int(p[1].split("_")[0])
        kp, ki = PI_V1[ts]
        return dict(run_type="closed_loop_speed_PI", controller_id=f"PIv1_{ts}ms", controller_structure="positional PID (bilinear), Kd=0",
                    Kp=kp, Ki=ki, Kd=0, controller_coefficients="", nominal_Ts_ms=ts,
                    tuning_plant="v1 identification (see v1 README)", tuning_plant_id_Ts_ms=2 if ts == 5 else ts,
                    anti_windup="positional Tustin with clamp (v1 firmware state not archived)")
    if p[0] == "04_continuous_PID_validation":
        ts = int(p[1].split("_")[0])
        g = PI[PI.NominalSamplingTime_ms == ts].iloc[0]
        return dict(run_type="closed_loop_speed_PI", controller_id=f"PI_{ts}ms", controller_structure="incremental PI",
                    Kp=g.Kp, Ki=g.Ki, Kd=g.Kd, controller_coefficients="", nominal_Ts_ms=ts,
                    tuning_plant=f"{g.PlantNumeratorCoefficients}/{g.PlantDenominatorCoefficients}",
                    tuning_plant_id_Ts_ms=g.PlantIdentificationSamplingTime_ms,
                    anti_windup=f"back-calculation Tr={g.AntiWindupResetTime_s} s")
    if p[0] == "05_discrete_controller_validation":
        case = p[1].split("_")[1].upper()
        g = DISC[DISC.Case == case].iloc[0]
        return dict(run_type="closed_loop_speed_discrete", controller_id=f"D_{case}",
                    controller_structure=g.ControllerStructure, Kp="", Ki="", Kd="",
                    controller_coefficients=f"num={g.NumeratorCoefficients_zinv} den={g.DenominatorCoefficients_zinv} K={g.RootLocusGain}",
                    nominal_Ts_ms=int(round(g.SamplingTime_s * 1000)),
                    tuning_plant=f"{g.PlantSourceNumeratorCoefficients_s}/{g.PlantSourceDenominatorCoefficients_s}",
                    tuning_plant_id_Ts_ms=20, anti_windup="output clamp 0..255 only")
    if p[0] == "03_system_identification":
        return dict(run_type="open_loop_APRBS_identification", controller_id="", nominal_Ts_ms=int(p[1].split()[0]))
    if p[0] == "01_current_calibration":
        return dict(run_type="current_calibration", controller_id="")
    if p[0] == "02_static_characterization":
        return dict(run_type="open_loop_static_triangular", controller_id="")
    if p[0] == "optional_characterization":
        return dict(run_type="open_loop_chirp", controller_id="", nominal_Ts_ms=20)
    return dict(run_type="unknown", controller_id="")


def main() -> int:
    logs = [(2, DS, f) for f in sorted(DS.rglob("*.txt")) if f.name.startswith("raw")]
    logs += [(1, DS1, f) for f in sorted(DS1.rglob("*.txt")) if f.name.startswith("raw")]
    rows = []
    for version, base, f in logs:
        rel = f.relative_to(base).as_posix()
        lines = f.read_text().splitlines()
        mode = lines[0].split(":", 1)[1].strip()
        date = lines[1].split(":", 1)[1].strip()
        d = pd.read_csv(f, skiprows=2)
        row = {"dataset_version": version, "file": rel, "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
               "gui_mode": mode, "recorded_at": date, **classify(rel, version)}
        r, y, u, dt = d.REF.to_numpy(float), d.MEAS.to_numpy(float), d.PWM.to_numpy(float), d.DT_ms.to_numpy(float)
        tr = np.flatnonzero(np.diff(r) != 0) + 1
        active = r != 0
        row.update({
            "speed_or_position": "speed (MEAS in RPM)" if "Speed" in mode or row["run_type"] != "closed_loop" else "",
            "columns": ";".join(d.columns), "n_samples": len(d),
            "dt_ms_unique": ";".join(f"{v:g}" for v in np.unique(dt)),
            "duration_s_from_DT": float(np.sum(dt) / 1000),
            "n_nonfinite_REF_MEAS_PWM": int(np.sum(~np.isfinite(np.r_[r, y, u]))),
            "ref_n_transitions": len(tr),
            "ref_phase_samples": ";".join(str(int(v)) for v in np.unique(np.diff(tr))) if len(tr) > 1 else "",
            "ref_active_levels": ";".join(f"{v:g}" for v in pd.unique(r[active])) if active.any() else "",
            "ref_n_distinct_active_levels": int(len(np.unique(r[active]))) if active.any() else 0,
            "meas_min": y.min(), "meas_max": y.max(), "meas_integer_valued": bool(np.all(y == np.round(y))),
            "pwm_min": u.min(), "pwm_max": u.max(),
            "frac_pwm_255": float(np.mean(u >= 255)),
            "frac_pwm_0_while_ref_active": float(np.mean((u <= 0) & active)) if active.any() else np.nan,
            "dmm_rows_with_sample": int(np.sum(d.DMM_SAMPLE_ID.to_numpy() >= 0)),
        })
        flags = []
        if row["n_nonfinite_REF_MEAS_PWM"]:
            flags.append("nonfinite")
        if len(np.unique(dt)) > 1:
            flags.append("irregular_DT")
        if row["frac_pwm_255"] > 0:
            flags.append("pwm_saturation_present")
        if row["run_type"].startswith("closed_loop"):
            if row["run_type"] == "closed_loop_speed_discrete":
                flags.append("controller_repeated_across_versions_v1_2026-05-05_v2_2026-09-03")
            else:
                flags.append("single_run_for_controller")
            flags.append("random_reference_levels_per_run")
            if row["run_type"] == "closed_loop_speed_PI":
                flags.append("controller_confounded_with_sampling_time")
        row["flags"] = ";".join(flags)
        rows.append(row)
    keys = []
    for r_ in rows:
        for k in r_:
            if k not in keys:
                keys.append(k)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} raw logs -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
