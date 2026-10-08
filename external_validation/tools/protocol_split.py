#!/usr/bin/env python3
"""Candidate A frozen-protocol split (Tasks 1.3-1.5). Metadata only.

Rules (fixed in FROZEN_PROTOCOL_DRAFT.md, applied here mechanically):
  strata      calendar days 2026-04-04, 2026-05-23, 2026-05-24 (separate experiments)
  source      K* = (4.999010254763151, 8.00337810067222, 0.15694720663178266)
  eligible    run_eligibility in {ELIGIBLE, ELIGIBLE_WITH_NOTE}
  excluded    K* runs of generations 4 (discovery) and 5 (best-J record): selection-conditioned
  split       per day, eligible K* runs in time order: first ceil(0.6 n) = calibration, rest = source holdout
  sufficiency n_cal >= 8 and n_hold >= 5 per day, else STOP for that day (no adaptation)
  matching    all calibration, holdout and target runs of a stratum must lie in ONE contiguous
              acquisition session (no inter-run gap > 10 min); otherwise STOP for that day
              (the stratum is not re-defined by session: that would adapt the split)
  targets     eligible non-K* runs of the same day, in a generation whose K* run is a source-holdout run,
              recorded after that K* run and before the next K* run (same generation)
No residual, threshold, exceedance or FAR quantity is computed.
"""
import json, math, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "protocol"
R = pd.read_csv(P / "learning_campaign_runs_ordered.csv", parse_dates=["t"])
R = R.sort_values("t").reset_index(drop=True)
R["session"] = (R.t.diff().dt.total_seconds() > 600).cumsum() + 1    # contiguous acquisition sessions
H = pd.read_csv(P / "optimizer_history.csv")
KSTAR = "A_Kstar"
ELIG = {"ELIGIBLE", "ELIGIBLE_WITH_NOTE"}
EXCL_GENS = {4, 5}
N_CAL_MIN, N_HOLD_MIN, FRAC = 8, 5, 0.6

# optimizer outcome per run (History rows are in file order within generation)
R["pos_in_gen"] = R.sort_values("t").groupby("gen").cumcount() + 1
H["pos_in_gen"] = H.groupby("gen").cumcount() + 1
R = R.merge(H[["gen", "pos_in_gen", "J", "P"]], on=["gen", "pos_in_gen"], how="left")
R["opt_failure_penalty"] = R.J >= 1e12
R["role"] = "unused"
ks = R.controller_id == KSTAR
R.loc[ks & R.gen.isin(EXCL_GENS), "role"] = "excluded_selection_conditioned_Kstar"
R.loc[ks & ~R.run_eligibility.isin(ELIG), "role"] = "excluded_ineligible_Kstar"
out = {"rules": {"n_cal_min": N_CAL_MIN, "n_hold_min": N_HOLD_MIN, "cal_fraction": FRAC,
                 "excluded_kstar_generations": sorted(EXCL_GENS)}, "strata": {}}
for day, g in R.groupby("day"):
    S = g[(g.controller_id == KSTAR) & g.run_eligibility.isin(ELIG) & ~g.gen.isin(EXCL_GENS)].sort_values("t")
    n = len(S); n_cal = math.ceil(FRAC * n); n_hold = n - n_cal
    cal, hold = S.iloc[:n_cal], S.iloc[n_cal:]
    sessions_used = sorted(set(S.session))
    ok_n = n_cal >= N_CAL_MIN and n_hold >= N_HOLD_MIN
    ok_session = len(sessions_used) == 1
    ok = ok_n and ok_session
    pre = "" if ok else "STOPPED_"
    R.loc[cal.index, "role"] = pre + "source_calibration"
    R.loc[hold.index, "role"] = pre + "source_holdout"
    tgt_idx, gaps = [], []
    allk = g[g.controller_id == KSTAR].sort_values("t")
    for _, h in hold.iterrows():
        nxt = allk[allk.t > h.t].t.min()
        cand = g[(g.gen == h.gen) & (g.controller_id != KSTAR) & (g.t > h.t)
                 & ((g.t < nxt) if pd.notna(nxt) else True)]
        el = cand[cand.run_eligibility.isin(ELIG)]
        tgt_idx += el.index.tolist()
        R.loc[cand.index.difference(el.index), "role"] = "excluded_ineligible_target"
        if len(el):
            gaps.append((el.t.max() - h.t).total_seconds())
    R.loc[tgt_idx, "role"] = pre + "target_evaluation"
    T = R.loc[tgt_idx]
    def d(x):
        return {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in x.items()}
    kp_ref = np.array([4.999010254763151, 8.00337810067222, 0.15694720663178266])
    span = np.array([15, 10, 0.5])   # CEM search box widths (Kmax - Kmin)
    if len(T):
        dist = np.sqrt((((T[["Kp", "Ki", "Kd"]].to_numpy() - kp_ref) / span) ** 2).sum(1))
    out["strata"][day] = {
        "decision": "GO" if ok else "STOP",
        "stop_reasons": ([] if ok_n else ["too few eligible K* runs"]) + ([] if ok_session else
                         [f"source runs span acquisition sessions {sessions_used} (matched conditions not met)"]),
        "acquisition_sessions_of_source_runs": sessions_used,
        "calibration_runs_per_session": cal.session.value_counts().sort_index().to_dict(),
        "target_sessions": sorted(set(R.loc[tgt_idx, "session"])) if tgt_idx else [],
        "kstar_eligible_after_exclusions": n, "n_calibration": n_cal, "n_source_holdout": n_hold,
        "calibration_generations": cal.gen.tolist(), "holdout_generations": hold.gen.tolist(),
        "calibration_time_span": [str(cal.t.min()), str(cal.t.max())],
        "holdout_time_span": [str(hold.t.min()), str(hold.t.max())],
        "n_target_runs": int(len(T)), "n_target_distinct_controllers": int(T.controller_id.nunique()),
        "target_ineligible_excluded": int((R.loc[g.index, "role"] == "excluded_ineligible_target").sum()),
        "max_gap_holdout_kstar_to_last_target_s": max(gaps) if gaps else None,
        "metadata_bias": {
            "kstar_cal_overshoot_median": float(cal.overshoot_pct.median()),
            "kstar_hold_overshoot_median": float(hold.overshoot_pct.median()),
            "kstar_cal_final_err_median": float(cal.final_abs_error.median()),
            "kstar_hold_final_err_median": float(hold.final_abs_error.median()),
            "kstar_hold_with_note": int((hold.run_eligibility == "ELIGIBLE_WITH_NOTE").sum()),
            "target_overshoot_quartiles": d(T.overshoot_pct.quantile([.25, .5, .75]).to_dict()) if len(T) else {},
            "target_final_err_quartiles": d(T.final_abs_error.quantile([.25, .5, .75]).to_dict()) if len(T) else {},
            "target_sat_frac_quartiles": d(T.frac_command_saturated.quantile([.25, .5, .75]).to_dict()) if len(T) else {},
            "target_with_note": int((T.run_eligibility == "ELIGIBLE_WITH_NOTE").sum()),
            "target_opt_failure_penalty_frac": float(T.opt_failure_penalty.mean()) if len(T) else None,
            "kstar_hold_opt_failure_penalty_frac": float(hold.opt_failure_penalty.mean()),
            "target_normalised_gain_distance_to_kstar_quartiles":
                d(pd.Series(dist).quantile([.25, .5, .75]).to_dict()) if len(T) else {},
            "target_Kp_range": [float(T.Kp.min()), float(T.Kp.max())] if len(T) else [],
            "target_Ki_range": [float(T.Ki.min()), float(T.Ki.max())] if len(T) else [],
            "target_Kd_range": [float(T.Kd.min()), float(T.Kd.max())] if len(T) else [],
        }}
out["overall_decision"] = ("GO" if all(s["decision"] == "GO" for s in out["strata"].values())
                           else "STOP" if all(s["decision"] == "STOP" for s in out["strata"].values()) else "PARTIAL")
out["sessions"] = {int(k): v for k, v in R.groupby("session").agg(start=("t", "min"), end=("t", "max"), runs=("t", "size"),
                   first_gen=("gen", "min"), last_gen=("gen", "max")).astype(str).to_dict("index").items()}
out["role_counts"] = R.role.value_counts().to_dict()
cols = ["file", "t", "day", "session", "gen", "pos_in_gen", "controller_id", "Kp", "Ki", "Kd", "run_eligibility", "role",
        "frac_command_saturated", "final_abs_error", "overshoot_pct", "J", "opt_failure_penalty"]
R[cols].sort_values("t").to_csv(P / "candidate_A_protocol_units.csv", index=False)
json.dump(out, open(P / "candidate_A_split.json", "w"), indent=2, default=str)
print(json.dumps(out, indent=2, default=str))
