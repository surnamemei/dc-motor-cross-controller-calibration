#!/usr/bin/env python3
"""Task 1.1-1.4 evidence for Candidate A: exact K* identity, counts by day and
generation, chronological split feasibility, and time-adjacent target runs.
Metadata only: no residual, threshold or exceedance quantity is computed."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "raw" / "candidate_A_github"
OUT = ROOT / "protocol"
man = pd.read_csv(ROOT / "manifests" / "run_manifest.csv", low_memory=False)
A = man[(man.dataset == "A_Lizarraga_github") & (man.campaign == "data_experiments_L298N_A90")].copy()

def load(f):
    return sio.loadmat(REPO / f, squeeze_me=True, struct_as_record=False)["E"]

rows = []
for f in A.file:
    E = load(f)
    ack = E.command.ackLine
    a = ack.split(",")
    rows.append(dict(file=f, created_at=E.meta.created_at, run_cmd=E.command.runCmd, ack=ack,
                     req_Kp=repr(float(E.request.Kp)), req_Ki=repr(float(E.request.Ki)), req_Kd=repr(float(E.request.Kd)),
                     ack_Kp=a[3], ack_Ki=a[4], ack_Kd=a[5],
                     cond="|".join([a[2]] + a[6:15]),   # A_applied, t_step, Tf, Ts, CPR, DPP, deadband, u_min, u_max, dir
                     n=int(E.summary.nSamples)))
R = pd.DataFrame(rows).merge(A[["file", "controller_id", "subfolder", "run_eligibility", "integrity_flags",
                                "frac_command_saturated", "final_abs_error", "overshoot_pct", "Kp", "Ki", "Kd"]], on="file")
R["t"] = pd.to_datetime(R.created_at)
R["day"] = R.t.dt.date.astype(str)
R["gen"] = R.subfolder.str[4:].astype(int)
R["ack_gains"] = R.ack_Kp + "," + R.ack_Ki + "," + R.ack_Kd
R["run_gains"] = R.run_cmd.str.split(",").str[2:5].str.join(",")
R["req_gains"] = R.req_Kp + "," + R.req_Ki + "," + R.req_Kd
R = R.sort_values("t").reset_index(drop=True)
R["order_in_day"] = R.groupby("day").cumcount() + 1
K = R[R.controller_id == "A_Kstar"]
res = {}
res["kstar_n"] = int(len(K))
res["kstar_distinct_ack_gains"] = sorted(K.ack_gains.unique().tolist())
res["kstar_distinct_RUN_command_gains"] = sorted(K.run_gains.unique().tolist())
res["kstar_distinct_requested_doubles"] = sorted(K.req_gains.unique().tolist())
res["matched_conditions_distinct_all_learning_runs"] = R.cond.value_counts().to_dict()
res["n_samples_distinct"] = sorted(R.n.unique().tolist())
# runs of other controllers whose ACK gains equal K*'s ACK gains (would be hidden K* repeats)
res["non_kstar_runs_with_kstar_ack_gains"] = int(((R.controller_id != "A_Kstar") & R.ack_gains.isin(K.ack_gains)).sum())
res["kstar_by_day"] = K.groupby("day").size().to_dict()
res["kstar_by_day_eligibility"] = K.groupby(["day", "run_eligibility"]).size().unstack(fill_value=0).to_dict("index")
res["kstar_per_generation_counts"] = K.groupby("gen").size().value_counts().to_dict()
res["generations_without_kstar"] = sorted(set(range(1, 61)) - set(K.gen))
res["generations_by_day"] = R.groupby("day").gen.agg(["min", "max", "nunique"]).to_dict("index")
res["kstar_generation_list_by_day"] = {d: g.gen.tolist() for d, g in K.groupby("day")}
res["kstar_position_in_generation"] = (R.assign(pos=R.groupby("gen").cumcount() + 1)
                                       .loc[lambda x: x.controller_id == "A_Kstar", "pos"].value_counts().sort_index().to_dict())
json.dump(res, open(OUT / "kstar_verification.json", "w"), indent=2, default=str)
R.drop(columns=["ack", "run_cmd"]).to_csv(OUT / "learning_campaign_runs_ordered.csv", index=False)
print(json.dumps(res, indent=2, default=str))
