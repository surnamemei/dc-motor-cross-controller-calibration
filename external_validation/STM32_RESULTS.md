# STM32 external validation: confirmatory results (Candidate C)

**Protocol:** `STM32_PROTOCOL.md` (sha `3421f408…`), executed **once** on 2026-10-08 with no changes. Model order,
intercept, rows, thresholds, splits, exclusions and comparisons are exactly as frozen.

## Execution record (`results_C/run_log.txt`)

| Step | Time (UTC) | Detail |
|---|---|---|
| Pre-flight (`--verify-only`) | 04:21:22 | 4 frozen inputs unchanged; 88/88 eligible files identical in the extracted copy, the ZIP and the manifest; the 6 comparisons = (ZN→PT, PT→GS, GS→PSO) × (S1, S3); splits as frozen; every target run later than its source holdout |
| Execution start | 04:21:38 | `tools/analysis_C.py` sha `3c893208…`; the script refuses a second execution |
| Stage 1 | 04:21:39 | **only the 48 calibration files opened**; 40 source models (8 sources × primary + 4 sensitivities) and thresholds written to `results_C/calibration_models.json` (sha `68e5622f…`) |
| Stage 2 | 04:21:39–04:23:15 | holdout, target and pass files opened; 88 files used in total |

**Failures:** **0** model-fit failures (all 40 source fits passed every acceptance check) and **0** bootstrap failures
(every analysis used 600 of 600 draws).

## 1. Calibration FAR by controller and scenario (primary; in-sample, target 1 %)

| Scenario | ZN | PT | GS | PSO |
|---|---:|---:|---:|---:|
| S1 | 1.00 % | 0.99 % | 0.99 % | 0.98 % |
| S3 | 1.00 % | 0.98 % | 0.99 % | 0.97 % |

- Per-run calibration FAR: 0.81–1.42 %.
- Thresholds: 2.87–3.09 RPM.
- Models: poles 0.955–0.968 and 0.27–0.61; DC gain 131.7–134.1 RPM/V; condition numbers 1.6–4.0 × 10⁴.

## 2. Same-controller held-out FAR (runs 08–11; whole-run bootstrap, 95 %)

| Scenario | ZN | PT | GS | PSO |
|---|---|---|---|---|
| S1 | 0.96 % [0.86, 1.12] | 1.07 % [0.96, 1.11] | 0.86 % [0.71, 1.03] | 1.18 % [1.02, 1.36] |
| S3 | 1.13 % [0.82, 1.36] | 1.17 % [0.98, 1.31] | 0.86 % [0.72, 0.97] | 0.79 % [0.69, 0.94] |

Same-controller transfer to later runs of the same block stays within 0.79–1.18 % of a 1 % target.

## 3–4. The six predefined cross-controller comparisons

Each target is the next block's run02–05, compared against the source's own holdout. Intervals come from a whole-run
bootstrap: calibration runs are resampled with refitting and recalibration, and holdout and target runs are resampled.

| Scenario | Source → target | Source holdout FAR | **Target FAR** [95 % CI] | **D = target − holdout** [95 % CI] | Draws with D > 0 |
|---|---|---:|---|---|---:|
| S1 | ZN → PT | 0.96 % | **0.71 %** [0.62, 0.79] | **−0.24 pp** [−0.36, −0.14] | 0 % |
| S1 | PT → GS | 1.07 % | **1.03 %** [0.92, 1.14] | **−0.04 pp** [−0.14, +0.09] | 33 % |
| S1 | GS → PSO | 0.86 % | **0.59 %** [0.38, 0.88] | **−0.27 pp** [−0.57, +0.04] | 5 % |
| S3 | ZN → PT | 1.13 % | **0.92 %** [0.84, 0.96] | **−0.20 pp** [−0.45, +0.05] | 7 % |
| S3 | PT → GS | 1.17 % | **1.46 %** [1.32, 1.87] | **+0.30 pp** [+0.19, +0.62] | 100 % |
| S3 | GS → PSO | 0.86 % | **1.89 %** [0.52, 2.21] | **+1.03 pp** [−0.21, +1.29] | 85 % |

Per-run FARs (`results_C/chain_pairs.csv`) are homogeneous within each group. For S3 GS→PSO all four target runs lie at
1.77–2.02 %, against 0.81–0.92 % for the source holdout. Its interval is wide because the bootstrap refits shift the GS
threshold, not because one run is extreme.

**Reading the six comparisons:**
- **Signs:** four are negative (targets alarm *less* than the source's own holdout) and two are positive.
- **Excluding zero:** two intervals do, in opposite directions: S1 ZN→PT is negative and S3 PT→GS is positive. The other
  four include zero, and that does **not** establish equivalence.
- **Worst case:** the largest target FAR among the predefined comparisons is **1.89 %** (S3 GS→PSO).
- **No consistent pattern:** there is no consistent cross-controller FAR inflation, and S1 and S3 differ in direction.

**Pre-declared sensitivities** (all with 600/600 draws; `chain_pairs.csv`):

| Sensitivity | D range across the six comparisons | Comparisons whose interval excludes 0 |
|---|---|---|
| (a) ARX without intercept | −0.01 to **+3.92 pp** (S3 PT→GS target 4.86 %) | 4, all positive |
| (b) 5 % target | −2.61 to **+7.04 pp** (S3 GS→PSO target 12.0 %) | 4 (3 positive, 1 negative) |
| (c) t ≥ 2 s | −0.35 to +1.05 pp | 4 (2 negative, 2 positive) |
| (d) 1.5 s after setpoint changes excluded | −0.51 to +1.30 pp | 5 (3 negative, 2 positive) |

The result depends on the predictor: dropping the intercept (which models the friction offset) turns modest differences
into large positive ones. This is reported, not used to choose a model; the primary model stays as frozen.

## 5. Early-versus-later time-drift diagnostic

`Δ_time = FAR(interleaved-pass run01) − FAR(source holdout)` is the same controller recorded 10–40 minutes apart.

| Scenario | ZN | PT | GS | PSO |
|---|---:|---:|---:|---:|
| S1 | −0.10 pp | +0.06 pp | −0.17 pp | −0.05 pp |
| S3 | +0.06 pp | −0.21 pp | +0.25 pp | **+0.73 pp** |

**Rule, as frozen:** a D that is not clearly larger than |Δ_time| in the same scenario cannot be attributed to the change
of controller.
- **S1:** the largest |Δ_time| is 0.17 pp, and the S1 differences are −0.24, −0.04 and −0.27 pp, all of similar size.
- **S3:** the largest |Δ_time| is 0.73 pp, against S3 differences of −0.20, +0.30 and +1.03 pp. Only GS→PSO exceeds it,
  and only by 0.3 pp, while its own interval includes 0.
- **Conclusion:** no comparison passes the time-drift criterion clearly. Each Δ_time is a single run, so the criterion
  is itself imprecise.

## 6. Predictor diagnostics and quantisation limitations
- **Predictor.** One-step-ahead ARX(2,2,1)+c from the controller command to the controller's feedback speed.
  - In-sample residual standard deviation: 1.21–1.36 RPM.
  - Lag-1 residual autocorrelation: −0.16 to +0.02.
  - Ties at the threshold: 1–11 of about 28 800 scores per source (strict `>` used).
- **The threshold sits at the encoder-quantisation scale.**
  - The feedback is an EMA (α = 0.05) of raw speed quantised at 62.2 RPM per count per 5 ms, so one count changes the
    feedback by 3.11 RPM. Every threshold is **0.92–1.00 × that one-count step**.
  - In calibration data, 55–83 % of exceedances coincide with a raw-speed count change, against a 47–54 % base rate
    (`results_C/quantization_diagnostic_calibration.json`).
  - The monitor therefore partly detects count-arrival timing, which depends on the speed level. Controllers holding
    different speeds can produce different exceedance rates without any change in the plant.
- **The command is a quantised 0.1 V command, not a measured voltage.** There are 57–64 distinct levels per scenario
  (0–6.3 V), and the quantisation standard deviation is about 0.029 V. No terminal voltage, current or effort residual
  is assessed.
- **Reference.** The logged target is not used. The internal ramped reference is unknown; sensitivity (d) excludes
  1.5 s after each logged change.

## 7. Failures
- Model fits: **0 of 40** failed acceptance.
- Bootstrap draws: **0 of 42 000** failed (70 analyses × 600 draws).
- No run was excluded beyond the fixed eligibility rule, and no execution was repeated.

## 8. Effective number of independent experimental units

| Level | Count |
|---|---|
| Session / rig | **1** (2026-07-01, 13:49–14:56) |
| Controller blocks per scenario | 4 fixed-PI blocks in one fixed order. Each comparison has **one** source block and **one** target block, so n = 1 at the block level |
| Runs per comparison | 6 calibration, 4 holdout, 4 target (the unit of the bootstrap) |
| Samples per comparison | about 28 785 calibration, 19 190 holdout and 19 190 target. Not independent: lag-1 autocorrelation of exceedance indicators is 0.04–0.36 |

The intervals describe **run-to-run** variation within a block. They do not cover block-level or session-level
variation, which cannot be estimated with one block per controller and one session.

## Descriptive analyses (not inferential; outside the six predefined comparisons)
- **Interleaved pass** (all four controllers within 1.5 min): FAR 0.42–6.86 %.
- **Full rotation** (run02–11): FAR 0.55–6.03 %.
- **The largest values sit outside the confirmatory comparisons.** They are models calibrated on **ZN or PSO evaluated
  on GS in S1**: 4.37 % and 6.03 % in the rotation, and 4.86 % and 6.86 % on the interleaved run.
  - GS is the arm that the dataset's authors describe as holding a large steady-state offset, so it operates at a
    different speed level.
  - The pattern appears in the time-matched interleaved pass as well, which makes pure drift an unlikely sole cause. But
    those are single runs, the cell was not predefined, and speed-level-dependent quantisation offers a non-controller
    explanation.
- **Not promoted:** these values are not a confirmatory finding and were not used to choose any comparison.

## Conclusion (descriptive; not causal)
- On this rig, in one session, a command-to-speed residual calibrated on one fixed PI controller transferred to the
  chronologically next controller with target FARs of **0.59–1.89 %** (1 % target).
- Its differences from the source's own held-out runs were **−0.27 to +1.03 pp**: mixed in sign, with no consistent
  inflation.
- None passes the time-drift criterion clearly, and several are similar in size to quantisation-scale effects.
- Non-significant differences are **not** evidence of equivalence.
- **No controller causality can be claimed.** Every target block follows its source block in a fixed order, there is one
  block per controller, and there is one session.
