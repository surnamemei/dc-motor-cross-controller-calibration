#!/usr/bin/env python3
"""Unified run manifest and controller summary for the external-data audit.

Inputs:  manifests/candidate_A_runs.csv, manifests/candidate_B_runs.csv
Outputs: manifests/run_manifest.csv        one row per experimental record, common schema
         manifests/controller_summary.csv  one row per distinct controller configuration
         manifests/dataset_summary.json    counts behind the eligibility report

Run eligibility uses only acquisition-integrity and control-validity criteria that
were fixed before any monitor was built (no residual, threshold or false-alarm
quantity is computed or used anywhere in this audit):
  EXCLUDED_FAILED_CONTROL   divergence (|y| > 1.5|A|), no motion, missing END/ACK,
                            non-finite values, wrong sample count, irregular sampling
  RESTRICTED_SATURATION     command at the limit for > 10 % of post-step samples
  ELIGIBLE_WITH_NOTE        final |error| > 2 deg (A) or any sample at PWM 255 (B)
  ELIGIBLE                  none of the above
  NOT_CONTROLLER_RUN        open-loop identification / calibration records (model building only)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
M = ROOT / "manifests"
K_STAR = "4.99901,8.003378,0.156947"


def a_rows() -> pd.DataFrame:
    d = pd.read_csv(M / "candidate_A_runs.csv")
    d["gain_key"] = d[["Kp", "Ki", "Kd"]].round(6).astype(str).agg(",".join, axis=1)
    order = d.sort_values("created_at").drop_duplicates("gain_key")["gain_key"].tolist()
    cid = {k: f"A_K{i + 1:04d}" for i, k in enumerate(order)}
    cid[K_STAR] = "A_Kstar"                          # learning-campaign best K*, = validation K2
    cid["2.983711,6.224762,0.079279"] = "A_VAL_K1"     # validation K1 (also run in the failed DC campaign)
    d["controller_id"] = d.gain_key.map(cid)
    f = d["flags"].fillna("")
    status = pd.Series("ELIGIBLE", index=d.index)
    status[f.str.contains("final_error_gt2deg")] = "ELIGIBLE_WITH_NOTE"
    status[f.str.contains("saturation_gt10pct")] = "RESTRICTED_SATURATION"
    failed = f.str.contains("divergence|no_motion|no_END|no_ACK|nonfinite|sample_count|irregular_time")
    status[failed] = "EXCLUDED_FAILED_CONTROL"
    role = pd.Series("single_run_controller", index=d.index)
    role[d.gain_key == K_STAR] = "repeated_controller"
    role[d.campaign == "validation_amplitudes_L298N"] = "amplitude_sweep_two_controllers"
    role[d.campaign == "data_experiments_DC_L298N_A90"] = "failed_campaign_sign_runaway"
    group = ("A" + d.A_requested_deg.astype(str) + "_Ts" + d.Ts_ms.astype(str) + "_Tf" + d.Tf_ms.astype(str)
             + "_step" + d.t_step_ms.astype(str) + "_db" + d.deadband_deg.astype(str) + "_" + d.campaign)
    out = pd.DataFrame({
        "dataset": "A_Lizarraga_github", "source_version": "git 8c74893a15c2", "file": d.file, "sha256": d.sha256,
        "recorded_at": d.created_at, "campaign": d.campaign, "subfolder": d.subfolder,
        "stored_original_path": d.stored_file_path, "rig_label": d.stored_file_path.str.split("\\\\").str[0],
        "control_variable": "position", "output_unit": "deg", "command_unit": "PWM counts (-255..255, pre-deadband)",
        "controller_id": d.controller_id, "controller_structure": "PID (Euler D, conditional integration, deadband reset)",
        "Kp": d.Kp, "Ki": d.Ki, "Kd": d.Kd, "Ts_ms": d.Ts_ms, "n_samples": d.n_samples,
        "duration_s": d.Tf_ms / 1000, "reference_type": "single step at 0.5 s",
        "reference_amplitude": d.A_applied_deg, "matched_condition_group": group,
        "frac_command_saturated": d.frac_u_saturated_post_step, "final_abs_error": d.final_abs_error_deg,
        "overshoot_pct": d.overshoot_pct, "command_replay_max_abs_err": d.replay_max_abs_err,
        "integrity_flags": d["flags"].fillna(""), "run_eligibility": status, "role": role,
    })
    out["n_runs_same_controller"] = out.groupby(["controller_id", "matched_condition_group"]).file.transform("size")
    out["replicate_index"] = out.sort_values("recorded_at").groupby(
        ["controller_id", "matched_condition_group"]).cumcount().reindex(out.index) + 1
    return out


def b_rows() -> pd.DataFrame:
    d = pd.read_csv(M / "candidate_B_runs.csv")
    closed = d.run_type.str.startswith("closed_loop")
    f = d["flags"].fillna("")
    status = pd.Series("NOT_CONTROLLER_RUN", index=d.index)
    status[closed] = "ELIGIBLE"
    status[closed & f.str.contains("pwm_saturation_present")] = "ELIGIBLE_WITH_NOTE"
    status[closed & f.str.contains("nonfinite|irregular_DT")] = "EXCLUDED_FAILED_CONTROL"
    group = pd.Series("", index=d.index)
    group[closed] = ("Ts" + d.nominal_Ts_ms.fillna(0).astype(int).astype(str) + "_phase"
                     + d.ref_phase_samples.astype(str) + "samples_v" + d.dataset_version.astype(str))
    role = d.run_type.where(~closed, "single_run_controller")
    role[closed & (d.run_type == "closed_loop_speed_discrete")] = "controller_repeated_across_versions_unmatched_protocol"
    out = pd.DataFrame({
        "dataset": "B_OpenMCT_mendeley", "source_version": "v" + d.dataset_version.astype(str), "file": d.file,
        "sha256": d.sha256, "recorded_at": d.recorded_at, "campaign": d.run_type, "subfolder": "",
        "stored_original_path": "", "rig_label": "OpenMCT Teensy4.0 DRV8874 TS-25GA370H-20",
        "control_variable": d.run_type.map(lambda t: "speed" if t.startswith("closed_loop") else "open-loop speed"),
        "output_unit": "RPM (integer-valued in log)", "command_unit": "PWM counts (0..255, applied)",
        "controller_id": d.controller_id.fillna(""), "controller_structure": d.get("controller_structure", ""),
        "Kp": d.Kp, "Ki": d.Ki, "Kd": d.Kd, "Ts_ms": d.nominal_Ts_ms, "n_samples": d.n_samples,
        "duration_s": d.duration_s_from_DT, "reference_type": d.run_type.map(
            lambda t: "zero/random-level APRBS steps" if t.startswith("closed_loop") else t),
        "reference_amplitude": d.ref_active_levels, "matched_condition_group": group,
        "frac_command_saturated": d.frac_pwm_255, "final_abs_error": "", "overshoot_pct": "",
        "command_replay_max_abs_err": "", "integrity_flags": f, "run_eligibility": status, "role": role,
    })
    out["n_runs_same_controller"] = out.groupby("controller_id").file.transform("size").where(closed, 0)
    out["n_runs_same_controller_matched"] = out.groupby(["controller_id", "matched_condition_group"]).file.transform(
        "size").where(closed, 0)
    out["replicate_index"] = (out.sort_values("recorded_at").groupby("controller_id").cumcount()
                              .reindex(out.index) + 1).where(closed, 0)
    return out


def main() -> int:
    a, b = a_rows(), b_rows()
    a["n_runs_same_controller_matched"] = a["n_runs_same_controller"]
    allr = pd.concat([a, b], ignore_index=True)
    allr.to_csv(M / "run_manifest.csv", index=False)
    ctrl = (allr[allr.controller_id != ""]
            .groupby(["dataset", "controller_id"])
            .agg(control_variable=("control_variable", "first"), Kp=("Kp", "first"), Ki=("Ki", "first"),
                 Kd=("Kd", "first"), Ts_ms=("Ts_ms", "first"), n_runs=("file", "size"),
                 n_eligible=("run_eligibility", lambda s: int(s.isin(["ELIGIBLE", "ELIGIBLE_WITH_NOTE"]).sum())),
                 n_condition_groups=("matched_condition_group", "nunique"),
                 first_run=("recorded_at", "min"), last_run=("recorded_at", "max"),
                 n_days=("recorded_at", lambda s: pd.to_datetime(s).dt.date.nunique()))
            .reset_index())
    ctrl.to_csv(M / "controller_summary.csv", index=False)
    summ = {}
    for name, g in allr.groupby("dataset"):
        c = ctrl[ctrl.dataset == name]
        summ[name] = {
            "records": int(len(g)),
            "controller_runs": int((g.controller_id != "").sum()),
            "run_eligibility": g.run_eligibility.value_counts().to_dict(),
            "distinct_controllers": int(len(c)),
            "controllers_with_>=2_runs": int((c.n_runs >= 2).sum()),
            "controllers_with_>=2_eligible_runs": int((c.n_eligible >= 2).sum()),
            "max_runs_one_controller": int(c.n_runs.max()) if len(c) else 0,
            "roles": g.role.value_counts().to_dict(),
        }
    (M / "dataset_summary.json").write_text(json.dumps(summ, indent=2, default=str) + "\n")
    print(json.dumps(summ, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
