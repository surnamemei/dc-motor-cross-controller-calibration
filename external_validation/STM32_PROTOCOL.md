# Frozen protocol: STM32 speed-control dataset (Candidate C, Zenodo 10.5281/zenodo.21201595)

**Status:** FROZEN on 2026-10-08, before any residual, threshold or false-alarm quantity was computed on these data. The
confirmatory analysis is **not** run here.

So far the only things done with the data are integrity metadata (`manifests/candidate_C_runs.csv`) and the
channel-resolution checks in §3. No model has been fitted.

**Frozen inputs:**

| File | SHA-256 |
|---|---|
| `raw/candidate_C_zenodo/etrls-str-stm32-v1.0.zip` | `2df790e4e2f1fba74022e2f3fad2d7f3d8f9dad4f1a4b02dd6f40b7425fb9af6` |
| `manifests/candidate_C_units.csv` | `4e4ed2efd05f732873d21efdf8875f9188a7f4f7ad1e5079aec156b17265a62e` |
| `protocol/candidate_C_splits.json` | `0ef7f6a8311ea46c1751b42d3df443252047e81b9112198467a274bcb18a7d2e` |

The split file is produced by `tools/protocol_split_C.py` from the rules below. Every run file is also checked against
its own hash.

## 1. Eligible units (88 real experimental runs)

Arms ZN, PT, GS and PSO (fixed PI, Kd = 0, gains from the acquisition harness) × scenarios S1 and S3 × runs 01–11.

| Arm | Kp | Ki |
|---|---|---|
| ZN | 0.0089 | 0.0280 |
| PT | 0.0393 | 0.8491 |
| GS | 0.1000 | 0.0010 |
| PSO | 0.0073 | 0.0388 |

- Each run lasts 24 s, with 4799–4800 rows at 5 ms.
- STR and RL (adaptive), S2/S4/S5 (emulated disturbances), the S5 pilot and the misseed runs are **excluded**.
- **S1 and S3 are separate experiments.** They are never pooled, and no quantity uses both.

## 2. Chronology (recovered from the v2 archive's file times; the same session on 2026-07-01)

| Time | Content |
|---|---|
| 13:49:34–13:51:46 | S1 interleaved pass: run01 of ZN, PT, GS, PSO (STR, RL) |
| 13:52:12–13:54:24 | S3 interleaved pass: run01 of ZN, PT, GS, PSO (STR, RL) |
| — | **gap of 9 min 58 s** |
| 14:04:26–14:21:30 | S1 blocks, run02–11 each: ZN (14:04–14:08), PT (14:08–14:12), GS (14:13–14:17), PSO (14:17–14:21); then STR and RL |
| 14:30:42–14:47:46 | S3 blocks, run02–11 each: ZN (14:30–14:34), PT (14:35–14:39), GS (14:39–14:43), PSO (14:43–14:47); then STR and RL |

Within a block, runs follow each other at a 26 s cadence (24 s run plus 2 s rest), and every run starts from rest.

**The block order is identical for every scenario and was never counterbalanced.**

## 3. Signals: what is and is not assumed

| Column | Use | Resolution / meaning (checked in the files) |
|---|---|---|
| `feedback` | **Model output `f`** | the controller's measured speed [RPM]: an exact EMA of raw speed (`f[k] = 0.05·speed[k] + 0.95·f[k−1]`; fitted coefficients 0.0500 / 0.9500); 0.1 RPM resolution |
| `output` | **Model input `u`** | the controller's voltage *command* [V], quantised to 0.1 V. It is **a quantised command, not a measured terminal voltage**; the PWM conversion and the H-bridge output are not logged |
| `setpoint` | not used by the monitor | the *logged target*. The controller tracks an internal `ramped_setpoint` that is not logged, and its ramp law is not archived, so the logged target is **not** treated as the reference |
| `speed` | not used | raw speed quantised at about 62.2 RPM per encoder count per 5 ms (11 distinct values in a run) |
| `pos` | not used | encoder angle |

The monitor is therefore a **plant-side residual**, from command to measured speed. It does not depend on the controller
law, on the reference, or on knowing the (unarchived) PI implementation.

## 4. Model and source-only fitting

```
f[k] = -a1*f[k-1] - a2*f[k-2] + b1*u[k-1] + b2*u[k-2] + c + e[k]     ARX(2,2,1) with intercept
```

- **Rows:** k = 2 … N−1 (0-based) of each run; every sample with two lags available.
- **Estimator:** OLS (`numpy.linalg.lstsq`), pooled over the source arm's **calibration runs only** (§5).
  No holdout, target or other-arm file is read while fitting.
- **Acceptance**, fixed now; failure means STOP for that source, with no re-specification:
  - all rows finite, and at least 20 000 rows;
  - regressor condition number below 1e8;
  - both poles |p| ≤ 0.9999 (a stable speed plant);
  - b1 + b2 > 0.
- **Score:** one-step-ahead residual `ε[k] = f[k] − f̂[k|k−1]`; `s[k] = |ε[k]|`.
- **Threshold:** `θ = numpy.quantile(pooled calibration scores, 0.99, method="higher")`.
- **Exceedance:** `s > θ` (strict).
- **Per-run FAR:** the exceedance fraction over the run's rows.
- **Firewall:** θ and the coefficients are written to disk, with hashes, before any holdout, target or pass run is opened.

## 5. Fixed splits (per scenario; listed exactly in `protocol/candidate_C_splits.json`)

For every source arm A in {ZN, PT, GS, PSO}:

| Role | Runs | Rationale |
|---|---|---|
| Source calibration | A run02–07 (6 runs, the first 6 of A's block) | earliest block runs |
| Source holdout | A run08–11 (4 runs, the last 4 of A's block) | same controller, later in time |
| Source pass run | A run01 (the interleaved pass, 10–40 min earlier) | same controller, distant in time |

**Primary chain pairs**, fixed by chronology so that no pair is chosen. Each source block is paired with the next
fixed-PI block in time:
- **ZN → PT**, **PT → GS**, **GS → PSO**;
- target = the next block's **run02–05** (4 runs), which immediately follow the source holdout (run11 → run02 is 26 s);
- that gives 3 pairs × 2 scenarios = **6 primary analyses, all reported**.

## 6. Analyses

**P. Primary.** For each chain pair:
- `D = mean FAR(target run02–05) − mean FAR(source holdout run08–11)`.
- Uncertainty: B = 600, seed 33043.
  - Each draw resamples the 6 calibration runs with replacement, refits, applies the acceptance checks and recalibrates
    θ.
  - It then resamples the 4 holdout runs and the 4 target runs independently, with replacement. Their times differ, so
    there is no natural pairing.
- **Failures** (refits that fail acceptance) are counted, reported, and not redrawn.
- Report: the 95 % percentile interval from successful draws, alongside the calibration FAR, holdout FAR and target FAR.
- No pooling across pairs or scenarios. Within a scenario the three D values may be summarised **descriptively** (all
  values, median, range).

**T. Time-separation diagnostic** (pre-specified; it bounds the time confound). For each source arm:
- `Δ_time = FAR(source run01 pass) − mean FAR(source holdout)`.
- This is the change in FAR for the **same controller** at a different time.
- A primary D that is not clearly larger than |Δ_time| for the same scenario cannot be attributed to the change of
  controller.

**I. Interleaved-pass comparison** (descriptive). For each source arm's model and threshold:
- report FAR on run01 of all four arms, which were recorded within 1.5 min of each other;
- the result is a 4 × 4 matrix per scenario with n = 1 per cell, so no interval and no inference.

**R. Full rotation** (descriptive). For each source arm, report FAR on every other fixed arm's run02–11, as a 4 × 4
matrix per scenario. No intervals, and no inference.

**Pre-declared sensitivities** (reported beside P and never replacing it):
- (a) ARX(2,2,1) without the intercept;
- (b) a 5 % exceedance target;
- (c) scoring rows with t ≥ 2 s only (start-up from rest excluded);
- (d) scoring rows outside 1.5 s after every logged setpoint change, because the internal ramp is unknown.

**Exclusions.** Only the fixed eligibility in §1, plus any file whose hash mismatches. There is no outlier removal, and
nothing is excluded on residuals or FAR.

**Effective units, to be reported.** Per chain pair: 6 calibration, 4 holdout and 4 target runs. Also the samples per
role, and the lag-1 autocorrelation of exceedances. The **run** is the unit of uncertainty; samples are not independent.

## 7. What the block design allows and does not allow

**Can be inferred (descriptively, for this session and rig):**
- Whether a command-to-speed model and threshold calibrated on one fixed PI controller's runs give a different exceedance
  rate on the runs of the next controller in time than on the source controller's own later runs.
- Whether that pattern is consistent across the three chain pairs, and separately in S1 and S3.
- How large the same-controller time effect (Δ_time) is compared with D.
- Whether the descriptive interleaved-pass matrix, where all controllers ran within 1.5 min, shows the same direction.

**Cannot be inferred:**
- **Any causal effect of controller gains.** Controller identity is completely confounded with block position and time.
  Every target block comes *after* its source block. Drift (motor temperature, supply, friction) would produce the same
  pattern as a controller effect.
- **Order or carry-over effects.** The order ZN → PT → GS → PSO is the same in both scenarios, so they cannot be
  estimated.
- **Session-to-session reproducibility.** There is one session only.
- **Validation of a voltage or effort channel.** The command is quantised, the control law is not archived, and no
  terminal voltage is measured.
- **Reference-tracking residuals.** The internal ramped reference is not logged.
- **Results for STR and RL,** or under disturbances (S2/S4/S5).
- **Alarm probabilities.** Exceedance is sample-level.

## 8. Prohibited

- Choosing a "favourable" source or target.
- Changing the model order, intercept, rows, threshold level, splits or exclusions after the first residual is computed.
- Pooling S1 and S3.
- Presenting I or R as inferential.
- Reporting only some chain pairs.

Any change requires a new, dated version of this protocol written before the changed analysis is run.
