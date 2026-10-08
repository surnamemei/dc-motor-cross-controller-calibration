# External-data assessments after the pilot study

After the pilot study was frozen, three public DC-motor datasets were assessed as possible external validation. This
document summarises the eligibility decisions, the pre-registered protocols, and **all** results, including the null and
negative ones.

The full protocols, run manifests, scripts and numerical outputs are in [`../external_validation/`](../external_validation/).
None of this work changes the pilot study's manuscript, processed data or results.

> **Read this first.** The external monitors use a **different predictor architecture** from the pilot study (see
> section 5). The external results are **not** a multi-platform replication of the pilot's numbers, and none of them is
> causal evidence about controller gains.

## 1. Datasets and eligibility

| Dataset | Source | Controlled variable | Decision |
|---|---|---|---|
| A: Lizarraga et al. | [GitHub](https://github.com/DrLizarraga/Closed-Loop-Learning-Based-PID-Tuning-for-DC-Motor-Actuators) @ `8c74893a`, MIT; article [10.3390/eng7080397](https://doi.org/10.3390/eng7080397) | position (deg) | **Restricted**: one usable stratum (2026-04-04) |
| B: OpenMCT, Von Chong & Cárdenas | Mendeley Data [10.17632/5xvg43r9r8.2](https://doi.org/10.17632/5xvg43r9r8.2), CC BY 4.0 | speed (RPM) | **Not suitable**: one run per controller under matched conditions |
| C: ET-RLS-STR, Tran & Tran | Zenodo [10.5281/zenodo.21201595](https://doi.org/10.5281/zenodo.21201595) v1.0.0, MIT | speed (RPM) | **Restricted**: 88 fixed-PI runs, one session, fixed block order |

Eligibility used only acquisition metadata and integrity checks, never residual or FAR values. The details are in
`ELIGIBILITY_REPORT.md` and `THIRD_DATASET_AUDIT.md`.

## 2. Dataset A (Lizarraga, position PID)

**Eligibility and frozen protocol.**
- **Data.** 2942 experiment files, all complete, at Ts = 25 ms. A float32 replay of the published firmware reproduced
  the logged command exactly in all 2942.
- **Source controller K\*.** One controller has 57 runs across three days, with identical gains in every run. The
  optimizer chose it on a single run, and the runs that conditioned that selection (generations 4 and 5) were excluded.
- **Strata.** Three calendar days were treated as separate strata.
  - 2026-05-23: **STOP**. The pre-specified model check failed (ARX pole 1.034 > 1.02).
  - 2026-05-24: **STOP**. Its source runs span two acquisition sessions.
  - 2026-04-04: the only stratum analysed.
- **Monitor.** Fixed ARX(2,2,1), a one-step-ahead predictor of position from the applied command, fitted on calibration
  runs only. Threshold: 99th percentile (`higher`), 1 % target.
- **Uncertainty.** A generation-paired bootstrap with refitting, 600 draws. The amendment that introduced it was hashed
  before any held-out residual existed.

**Results for 2026-04-04** (single execution; 600/600 draws successful):

| Quantity | Value |
|---|---|
| Calibration FAR (9 K\* runs, in-sample) | 0.89 % |
| Held-out K\* FAR (6 runs) | 0.17 % [0.00, 2.00] (one exceedance in 600 samples) |
| Target FAR (42 single-run controllers) | 0.74 % [0.24, 2.36] |
| Overall paired difference D | **+0.57 pp [0.00, 1.81]** |

**All six generation-level comparisons** (target mean minus held-out K\*):

| Generation | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|
| d_g (pp) | 0.00 | +1.14 | +0.71 | +0.43 | +0.57 | +0.57 |

**Pre-declared sensitivities.** All three intervals include zero:
- (a) without the two flagged targets: +0.58 [−0.15, 1.69];
- (b) 5 % target: +3.10 [−0.17, 7.10];
- (c) step-onset samples dropped: +0.72 [−0.67, 1.64].

**Diagnostics.**
- Saturation is identical across groups.
- No run property is notably associated with FAR (all |ρ| ≤ 0.22).
- Post-hoc, descriptive only: 13 of the 31 target exceedances fall within 0.1 s of the step.

## 3. Dataset C (STM32, speed PI)

**Eligibility and frozen protocol.**
- **Units.** 88 runs: four fixed-PI arms × scenarios S1 and S3 × 11 runs. S1 and S3 are kept separate.
- **Chronology.** Recovered from the v2.0.0 archive's file times. Each controller ran in one fixed-order block per
  scenario, in a single session.
- **Monitor.** One-step-ahead ARX(2,2,1) + intercept, from the logged 0.1 V-quantised command (treated as a command, not
  a measured voltage) to the controller's filtered speed. The logged setpoint is not used, because the controller tracks
  an unlogged internal ramp.
- **Splits.** Per source controller: runs 02–07 for calibration and 08–11 as a same-controller holdout.
- **Six predefined comparisons**, fixed by recording order: each source is compared with the next controller's runs
  02–05 (ZN→PT, PT→GS, GS→PSO, in each of S1 and S3).
- **Execution.** A single run with B = 600, giving 0 model-fit failures and 0 of 42 000 bootstrap failures.

**Same-controller held-out FAR** (95 % whole-run intervals):

| | ZN | PT | GS | PSO |
|---|---|---|---|---|
| S1 | 0.96 % [0.86, 1.12] | 1.07 % [0.96, 1.11] | 0.86 % [0.71, 1.03] | 1.18 % [1.02, 1.36] |
| S3 | 1.13 % [0.82, 1.36] | 1.17 % [0.98, 1.31] | 0.86 % [0.72, 0.97] | 0.79 % [0.69, 0.94] |

**All six predefined comparisons:**

| Scenario | Pair | Source holdout | Target FAR | D = target − holdout [95 % CI] |
|---|---|---|---|---|
| S1 | ZN → PT | 0.96 % | 0.71 % | −0.24 pp [−0.36, −0.14] |
| S1 | PT → GS | 1.07 % | 1.03 % | −0.04 pp [−0.14, +0.09] |
| S1 | GS → PSO | 0.86 % | 0.59 % | −0.27 pp [−0.57, +0.04] |
| S3 | ZN → PT | 1.13 % | 0.92 % | −0.20 pp [−0.45, +0.05] |
| S3 | PT → GS | 1.17 % | 1.46 % | +0.30 pp [+0.19, +0.62] |
| S3 | GS → PSO | 0.86 % | 1.89 % | +1.03 pp [−0.21, +1.29] |

- **Signs:** four differences are negative and two positive.
- **Intervals excluding zero:** two, in opposite directions.
- **Time-drift check.** The same-controller change over 10–40 min was −0.21 to +0.73 pp. No comparison exceeds it
  clearly.
- **Sensitivities depend on the predictor.** Without the intercept, D reaches +3.92 pp. The frozen model was not
  changed.
- **Outside the predefined set** (descriptive only): models calibrated on ZN or PSO reach 4.4–6.9 % on GS in S1. GS is
  the arm that operates at a different speed level.

## 4. Negative findings and uncertainty limits
- **Pilot-study magnitudes were not reproduced.**
  - Neither external platform showed the large controller-transfer failures reported for the pilot's effort channel
    (14.07 %).
  - Neither showed an across-controller calibration error several times the across-run error.
  - The predefined external target FARs stayed between 0.59 % and 1.89 %.
- **Non-significance is not equivalence.** The external intervals still allow differences up to about 1.8 pp (A) and
  1.3 pp (C).
- **Small effective samples.**
  - Dataset A's contrast rests on **6 generation pairs**, and its source baseline on a single exceedance.
  - Dataset C has **one session and one block per controller**, so its intervals cover run-to-run variation only.
- **Time confounding in C.** Every target block follows its source block in a fixed order, so controller and time
  cannot be separated.

## 5. Predictor and measurement differences (why the numbers are not comparable)
- **Residual class.**
  - The pilot compares measurements with a **closed-loop free-run simulation**: reference → replayed PI controller →
    identified plant. Its prediction depends on the controller.
  - Both external monitors are **one-step-ahead input–output predictors** driven by the measured output and the logged
    command, which largely removes the controller from the prediction.
  - Smaller transfer failures are therefore to be expected externally, whatever the plant does.
- **Channels.** The pilot has speed, effort and joint channels. Externally there is position only (A) or filtered speed
  only (C). No external platform has an independent effort or voltage measurement:
  - A's command is a firmware-determined PWM count;
  - C's command is a 0.1 V-quantised command with an unarchived control law.
- **Quantisation.** In C, every threshold sits at about one encoder count's effect on the filtered speed (0.92–1.00 ×
  3.11 RPM), so exceedances partly measure count timing.
- **Timescales and units.**
  - Timescales: 4 s cycles (pilot), a 3 s step (A), 24 s steps and staircases (C).
  - Bootstrap units: cycles (pilot), generation pairs (A), runs within one block (C).

## 6. Dataset sources

| Dataset | Reference |
|---|---|
| A | Lizarraga J.A. et al. (2026). *Eng* 7(8):397, https://doi.org/10.3390/eng7080397. Data and code: https://github.com/DrLizarraga/Closed-Loop-Learning-Based-PID-Tuning-for-DC-Motor-Actuators (commit `8c74893a15c2c110e880d41eabd0d648bd2dcc93`, MIT) |
| B | Von Chong A., Cárdenas D. (2026). Mendeley Data V2, https://doi.org/10.17632/5xvg43r9r8.2 (CC BY 4.0); related articles https://doi.org/10.1016/j.ohx.2026.e00794 and https://doi.org/10.1016/j.dib.2026.113274 |
| C | Tran T. T., Tran N. T. (2026). Zenodo, https://doi.org/10.5281/zenodo.21201595 (v1.0.0, MIT); v2.0.0 https://zenodo.org/records/21389722 |

Checksums are in [`../external_validation/sources.json`](../external_validation/sources.json), and licences and
attributions in [`../external_validation/THIRD_PARTY_NOTICES.md`](../external_validation/THIRD_PARTY_NOTICES.md).
