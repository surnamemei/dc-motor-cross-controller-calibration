#!/usr/bin/env python3
"""Fixed splits for the STM32 (Candidate C) protocol. Metadata only, no residuals.
Per scenario (S1, S3 kept separate), fixed-PI blocks in chronological order ZN -> PT -> GS -> PSO.
Primary chain pairs (source -> next block): source calibration = runs 02-07, source holdout = runs 08-11,
target = next block runs 02-05 (immediately following the source holdout in time)."""
import json, hashlib
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent
U = pd.read_csv(ROOT / "manifests" / "candidate_C_units.csv", parse_dates=["v2_file_mtime"])
E = U[U.eligibility == "ELIGIBLE_fixed_PI_nominal"]
ORDER = ["ZN", "PT", "GS", "PSO"]
def files(s, a, runs):
    d = E[(E.scenario == s) & (E.arm == a) & E.run.isin(runs)].sort_values("run")
    assert len(d) == len(runs), (s, a, runs)
    return [dict(file=r.file, run=int(r.run), sha256=r.sha256, time=str(r.v2_file_mtime)) for _, r in d.iterrows()]
out = {"rules": __doc__, "scenarios": {}}
for s in ["S1", "S3"]:
    sc = {"chain_pairs": [], "sources": {}}
    for a in ORDER:
        sc["sources"][a] = {"calibration": files(s, a, range(2, 8)), "holdout": files(s, a, range(8, 12)),
                            "interleaved_pass_run01": files(s, a, [1])}
    for a, b in zip(ORDER[:-1], ORDER[1:]):
        sc["chain_pairs"].append({"source": a, "target": b, "target_runs": files(s, b, range(2, 6))})
    out["scenarios"][s] = sc
p = ROOT / "protocol" / "candidate_C_splits.json"
p.write_text(json.dumps(out, indent=2) + "\n")
print(p, hashlib.sha256(p.read_bytes()).hexdigest())
