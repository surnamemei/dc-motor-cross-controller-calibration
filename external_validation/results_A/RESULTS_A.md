# External validation analysis A: Lizarraga position-PID data, stratum 2026-04-04

**Protocol:** `FROZEN_PROTOCOL_DRAFT.md`, amended by `results_A/PROTOCOL_AMENDMENT_01.md` (generation-paired
bootstrap). This is the first and only execution, with nothing changed after results were seen.

## Execution record

| Step | Time (UTC, 2026-10-08) | Evidence |
|---|---|---|
| Amendment hashed (`b083da6d…`), before any holdout or target residual existed | 04:11:41 | `AMENDMENT_01.sha256` |
| Integrity: 57 MAT files, frozen coefficients, protocol, amendment | 04:12:42 | `run_log.txt` |
| Calibration threshold written **before** holdout and target files were opened (θ₉₉ = 5.1368°) | 04:12:42 | `calibration_threshold.json` (sha `53265ea0…`) |
| Holdout and targets evaluated; bootstrap (600 draws × 4 configurations) | 04:12:42–04:12:51 | `summary.json`, `bootstrap_draws_*.csv` |

Analysis script: `tools/analysis_A.py`, sha `686afa7f…`.

**Unchanged from the frozen draft:** the ARX(2,2,1) coefficients (fitted on calibration only), the 99th-percentile
`higher` threshold, the roles (calibration: K\* generations 6–14, 9 runs; holdout: K\* generations 15–20, 6 runs;
targets: 42 runs, 7 per generation) and the exclusions.

## 1. Calibration FAR
- **0.89 %**: 8 exceedances in 900 in-sample calibration samples. Per run: 0–2 %; 5 of the 9 runs have at least one
  exceedance.
- Threshold θ₉₉ = 5.137° (about 19 encoder counts).
- Bootstrap range of the refitted and recalibrated threshold (95 %): 3.94–5.89°.

## 2. Held-out K\* FAR
- **0.17 %**: 1 exceedance in 600 samples (generation 15, one run). The other 5 holdout runs have none.
- 95 % CI: **0.00–2.00 %** (600 of 600 draws successful).

## 3. Target-controller FAR
- **0.74 %**: 31 exceedances in 4200 samples. 23 of the 42 target runs have at least one exceedance; per-run FAR ranges
  from 0 to 2 %.
- 95 % CI: **0.24–2.36 %**.
- This is **below the nominal 1 % target**.

## 4. Generation-level paired differences (target mean − holdout K\*)

| Generation | Holdout K\* FAR | Target mean FAR (7 runs) | Targets with ≥ 1 exceedance | d_g |
|---:|---:|---:|---:|---:|
| 15 | 1.00 % | 1.00 % | 4 / 7 | **0.00 pp** |
| 16 | 0.00 % | 1.14 % | 6 / 7 | **+1.14 pp** |
| 17 | 0.00 % | 0.71 % | 4 / 7 | **+0.71 pp** |
| 18 | 0.00 % | 0.43 % | 3 / 7 | **+0.43 pp** |
| 19 | 0.00 % | 0.57 % | 3 / 7 | **+0.57 pp** |
| 20 | 0.00 % | 0.57 % | 3 / 7 | **+0.57 pp** |

Each run has 100 scored samples, so one exceedance moves a run's FAR by 1 percentage point (pp). Five of the six
differences are positive. Every positive one occurs in a generation whose K\* run had **zero** exceedances, so the
differences mostly reflect the low K\* baseline.

## 5. Overall paired difference
**D = +0.57 pp, 95 % CI [0.00, 1.81] pp.**
- Bootstrap: B = 600, with 600 successful draws and **0 failures**. 97.5 % of draws have D > 0.
- The lower bound lies at zero. The interval does **not** exclude a null difference with any margin.

Pre-declared sensitivities, all with 600/600 successful draws:

| Sensitivity | Holdout FAR | Target FAR | D [95 % CI] |
|---|---:|---:|---|
| (a) without the 2 ELIGIBLE_WITH_NOTE targets | 0.17 % | 0.74 % | +0.58 pp [−0.15, 1.69] |
| (b) 5 % exceedance target (θ = 2.45°) | 3.50 % | 6.60 % | +3.10 pp [−0.17, 7.10] |
| (c) rows k = 25…120 (θ = 4.35°) | 0.69 % | 1.41 % | +0.72 pp [−0.67, 1.64] |

All three intervals include zero. The direction (target ≥ held-out K\*) is the same in every configuration, but the
magnitude is small and not distinguishable from zero.

## 6. Saturation and performance confounding (descriptive)
- **Saturation.** The median is 2 of 101 post-step samples at ±255, identical across K\* calibration, holdout and targets.
  Every run reaches |u| = 255 at the step, so peak command has no variation.
- **Per-run correlations** of FAR across the 42 targets (Spearman, unadjusted; `diagnostic_correlations.csv`):

  | Diagnostic | ρ |
  |---|---:|
  | deadband occupancy | −0.19 |
  | overshoot | +0.16 |
  | final error | −0.06 |
  | gain distance to K\* | −0.06 |
  | Kp | +0.08 |
  | Ki | −0.05 |
  | Kd | +0.09 |
  | position in generation | +0.04 |
  | saturation fraction | +0.01 |

  No |ρ| exceeds 0.22, and no association is notable even without adjustment.
- **Operating envelope.** The two groups follow different trajectories: K\* overshoot is 16.5 % against a target
  interquartile range of 7.5–11.7 %.
- **Where exceedances occur** (post-hoc, descriptive only; `posthoc_exceedance_location.csv`): 13 of the 31 target
  exceedances fall in the first 0.1 s after the step. That compares with 2 of the 8 calibration exceedances and 0 of the
  1 holdout exceedance. The extra target exceedances are partly concentrated in the step-onset transient, where target
  and K\* trajectories differ most. This is consistent with an operating-envelope difference, and the analysis cannot
  separate that from a controller attribute.
- **Selection.** K\* is the optimizer's winner and its 2 selection-conditioned runs were excluded; targets are
  single-run CEM draws. Neither group is a random sample of controllers.

## 7. Effective independent units

| Quantity | Count |
|---|---|
| Independent units for **D** | **6 generation pairs** |
| Calibration | 9 runs of 1 controller, 1 session (900 samples) |
| Holdout | 6 runs (600 samples); only **1** run has any exceedance |
| Targets | 42 runs of 42 controllers (4200 samples); 23 runs with ≥ 1 exceedance |
| Within-generation ICC of target FAR | −0.01, so there is no clustering; about 42 effective target runs |
| Lag-1 autocorrelation of exceedance indicators | calibration 0.24, holdout −0.01, targets 0.05 |

Sample counts overstate the information. The holdout baseline rests on **one** exceedance.

## Interpretation

**Descriptive.**
- On this rig and in this session, a position residual calibrated on 9 K\* runs gave a target-controller FAR of 0.74 %,
  below the 1 % design target.
- It gave 0.17 % on later runs of K\* itself.
- The target-minus-source difference is small (+0.57 pp), positive in 5 of 6 generations, and statistically
  indistinguishable from zero in the primary analysis and all sensitivities.
- There is **no evidence here of a material FAR inflation when calibration is transferred to other controllers.** There
  is a weak, unstable indication that targets exceed slightly more often than the source's own later runs.

**Not causal.**
- Targets were chosen by the optimizer, run once each, and always ran after K\* in their generation. Their transients
  also differ from K\*'s.
- So none of these results is an effect of the controller gains.

**Relation to the frozen manuscript.**
- This is a position-control residual. The manuscript's claims concern speed, effort and joint channels of a speed loop
  (for example, a worst-case controller-distinct transfer of 2.58 % speed and 14.07 % effort at a 1 % target).
- The external analysis neither replicates nor contradicts those numbers directly.
- It shows that on an independent rig, for a position residual and controllers drawn close to the source by an
  optimizer, transfer failure was small.
- There is no independent actuator-voltage validation: the logged command is a firmware-determined PWM count.

## Files
- `summary.json`
- `calibration_threshold.json`
- `per_run_far_primary.csv`
- `generation_pairs_primary.csv`
- `bootstrap_draws_{primary,sens_a_excl_note,sens_b_5pct,sens_c_k25}.csv`
- `diagnostics_per_run.csv`
- `diagnostic_correlations.csv`
- `posthoc_exceedance_location.csv`
- `run_log.txt`
- `PROTOCOL_AMENDMENT_01.md`
- `AMENDMENT_01.sha256`
