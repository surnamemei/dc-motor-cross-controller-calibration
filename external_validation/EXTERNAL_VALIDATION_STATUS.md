# External validation status (2026-10-08)

The journal manuscript, the frozen archival data and the research results are **unchanged**:
- `paper/main_v2.pdf` sha256 begins `daf23d89…`;
- the ELEC3304 source MAT hashes still match the data freeze.

All external work is in `external_validation/`.

| Dataset | Domain | Eligibility | Protocol | Analysis | Outcome |
|---|---|---|---|---|---|
| A: Lizarraga (GitHub, position PID, ESP32) | position | RESTRICTED: stratum 2026-04-04 only. 2026-05-23 STOP (ARX pole 1.034); 2026-05-24 STOP (two sessions) | `FROZEN_PROTOCOL_DRAFT.md` + `results_A/PROTOCOL_AMENDMENT_01.md` | **Done** (one execution) | Target FAR 0.74 % (below the 1 % target); held-out K\* FAR 0.17 %; D = +0.57 pp [0.00, 1.81]; sensitivities include 0 |
| B: OpenMCT (Mendeley, speed, Teensy) | speed | NOT SUITABLE: no matched repeats per controller | — | none | — |
| C: ET-RLS-STR (Zenodo 21201595, speed PI, STM32) | speed | RESTRICTED: 88 fixed-PI runs, one session, block order | `STM32_PROTOCOL.md` (frozen, sha `3421f408…`) | **Done** (one execution, 2026-10-08) | Same-controller holdout 0.79–1.18 %; 6 predefined comparisons: target 0.59–1.89 %, D −0.27 to +1.03 pp (2 intervals exclude 0, in opposite directions); 0 model-fit and 0 bootstrap failures; see `STM32_RESULTS.md` |
| Prospective rig (own motor) | speed | Package READY FOR DRY RUN | `prospective_validation/` | not started | — |

## What can be said now
- On one independent rig, for a position residual, calibration on one controller transferred to 42 nearby,
  optimizer-selected controllers **without exceeding the nominal 1 % FAR**.
- The difference from the source controller's own held-out runs was small and statistically indistinguishable from zero.
  It rests on 6 generation pairs, and the source baseline on a single exceedance.
- This is **not** a replication of the manuscript's speed/effort/joint claims, and it is **not** causal evidence about
  controller gains.

## What cannot be said
- Anything causal about controllers on STM32: its block design confounds controller with time. Effort-channel transfer
  is untestable externally.
- Anything about independent actuator-voltage residuals, for any external dataset.
- Generalisation across sessions or rigs: Candidate A has one usable session, and Candidate C has one session.

## Next steps (each needs an explicit go-ahead)
1. Done: STM32 confirmatory analysis (`STM32_RESULTS.md`); cross-platform comparison in `CROSS_PLATFORM_ASSESSMENT.md`.
2. **Prospective validation:** dry run and then hardware runs on the original motor (`prospective_validation/`). This is
   the only route to randomised, multi-session, speed-loop evidence with matched controllers.
3. **Manuscript:** only after these, and as a separately reviewed change. Results A would at most support a short,
   explicitly limited external-validity paragraph.

## Integrity references
- `results_A/run_log.txt`: execution order and hashes.
- `results_A/AMENDMENT_01.sha256`: the amendment hashed before any held-out residual existed.
- `protocol/*.json`: frozen splits, coefficients and decisions.
- `manifests/*.csv`: run-level eligibility for A, B and C.
