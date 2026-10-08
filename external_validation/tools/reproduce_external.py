#!/usr/bin/env python3
"""Regenerate every committed external-validation output from public inputs and compare.

  python3 tools/reproduce_external.py WORKDIR [--cache RAWDIR]

WORKDIR must not exist. It receives only the scripts, sources.json and the three hashed
protocol documents; public inputs are fetched (or copied from RAWDIR) and verified by
checksum; the full chain is executed; and each regenerated output is byte-compared with
the committed copy in this repository. Run logs (timestamps) are excluded from the
comparison. Exit status 0 = everything identical.
"""
import argparse, filecmp, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # external_validation/
INPUTS = ["sources.json", "FROZEN_PROTOCOL_DRAFT.md", "STM32_PROTOCOL.md", "results_A/PROTOCOL_AMENDMENT_01.md"]
CHAIN = [
    ["tools/fetch_public_inputs.py"],
    ["tools/inventory_candidate_A.py"], ["tools/inventory_candidate_B.py"], ["tools/build_manifest.py"],
    ["tools/kstar_verification.py"], ["tools/derive_supplementary.py", "a_optimizer_history"],
    ["tools/protocol_split.py"], ["tools/derive_supplementary.py", "a_units_gap"],
    ["tools/fit_arx_calibration.py"], ["tools/analysis_A.py"], ["tools/derive_supplementary.py", "a_posthoc"],
    ["tools/derive_supplementary.py", "extract_c"], ["tools/inventory_candidate_C.py"],
    ["tools/derive_supplementary.py", "c_versions"], ["tools/derive_supplementary.py", "c_units"],
    ["tools/protocol_split_C.py"], ["tools/analysis_C.py", "--verify-only"], ["tools/analysis_C.py"],
    ["tools/derive_supplementary.py", "c_quant"],
]
NOT_COMPARED = {"results_A/run_log.txt", "results_C/run_log.txt", "protocol/candidate_C_preflight.txt",
                "manifests/eligibility_decisions.json"}   # logs carry timestamps; the decisions file is hand-authored


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("workdir"); ap.add_argument("--cache"); a = ap.parse_args()
    W = Path(a.workdir).resolve()
    if W.exists():
        sys.exit("WORKDIR must not exist")
    shutil.copytree(HERE / "tools", W / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    for d in ("manifests", "protocol", "results_A"):      # created by hand in the original workflow
        (W / d).mkdir(parents=True, exist_ok=True)
    for rel in INPUTS:
        (W / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / rel, W / rel)
    for step in CHAIN:
        cmd = [sys.executable] + [str(W / step[0])] + step[1:]
        if step[0].endswith("fetch_public_inputs.py") and a.cache:
            cmd += ["--cache", a.cache]
        print(">>", " ".join(step), flush=True)
        subprocess.run(cmd, check=True, cwd=W, stdout=subprocess.DEVNULL)
    committed = [p for d in ("manifests", "protocol", "results_A", "results_C") for p in (HERE / d).rglob("*") if p.is_file()]
    same, diff, missing = [], [], []
    for p in sorted(committed):
        rel = p.relative_to(HERE).as_posix()
        if rel in NOT_COMPARED or rel in INPUTS or rel == "results_A/AMENDMENT_01.sha256" or rel == "results_A/RESULTS_A.md":
            continue
        q = W / rel
        if not q.exists():
            missing.append(rel)
        elif filecmp.cmp(p, q, shallow=False):
            same.append(rel)
        else:
            diff.append(rel)
    print(f"\nidentical: {len(same)}   different: {len(diff)}   not regenerated: {len(missing)}")
    for r in diff: print("  DIFF", r)
    for r in missing: print("  MISSING", r)
    sys.exit(0 if not diff and not missing else 1)


if __name__ == "__main__":
    main()
