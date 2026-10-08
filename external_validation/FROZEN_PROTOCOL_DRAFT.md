# Frozen protocol draft: external position-residual qualification on Candidate A (Lizarraga et al.)

**Status:** DRAFT, frozen on 2026-10-08, before any residual, threshold or false-alarm quantity was computed on any
holdout or target run.

**Decision: RESTRICTED.** Confirmatory analysis is permitted for **one stratum only, 2026-04-04**. Strata 2026-05-23 and
2026-05-24 are **STOP**: both were checked against rules fixed beforehand, and their splits were not adapted.

## What has and has not been done

**Done:**
- the ARX coefficients were fitted on the designated source-calibration runs only (§6);
- the split, the exclusions and the target sets were derived from metadata only (§§1–5).

**Not done:**
- no residual was computed on any holdout or target run;
- no threshold was computed;
- no FAR (false-alarm rate) was computed;
- no residual-monitor performance was inspected;
- no controller was selected, paired or ranked on any monitor outcome.

The manuscript, the research results and the existing data are untouched.

| Artefact | Content |
|---|---|
| `protocol/kstar_verification.json` | Task 1.1–1.2 evidence |
| `protocol/candidate_A_split.json` | split rules, per-stratum decisions, metadata-bias summary |
| `protocol/candidate_A_protocol_units.csv` | every learning-campaign run with its role (the exact sample units) |
| `protocol/candidate_A_arx_frozen.json` | frozen coefficients, calibration file hashes, acceptance checks; `coefficients_sha256 = 985e833953f9d0cff93e42e2a360dbbb53197b31fa8aff277aa9f3b22c0cf489` |
| `protocol/optimizer_history.csv` | the authors' optimizer history (`adaptive_history.mat`), metadata only |
| `tools/kstar_verification.py`, `tools/protocol_split.py`, `tools/fit_arx_calibration.py` | the scripts that produced the above |

---

## 1. K\* identity: exact (Task 1.1)

Every one of the 57 nominal K\* runs in `data_experiments_L298N_A90` was checked from the raw MAT files. The following
are each single-valued across the 57 runs:

- requested gains (double): `Kp = 4.999010254763151`, `Ki = 8.00337810067222`, `Kd = 0.15694720663178266`;
- the host `RUN` command and the firmware `ACK` echo: `4.999010, 8.003378, 0.156947`.

No other run carries these gains. All 2160 learning runs share one acquisition-condition string:

- A_applied = 89.999992°;
- step at 500 ms, Tf = 3000 ms, Ts = 25 ms;
- CPR = 1336, DPP = 0.269461066°, deadband 0.5°;
- u limits ±255, encoder direction −1;
- 121 samples.

The optimizer history (`adaptive_history.mat`, 2160 rows) matches the saved files generation by generation, so no
evaluation was dropped.

## 2. K\* repetitions by day and generation (Task 1.2)

| Calendar day | Generations with K\* | K\* runs | Eligible after the run-integrity screen | Notes |
|---|---|---:|---:|---|
| 2026-04-04 | 4–20 | 17 | 17 (all ELIGIBLE) | gen 4: **discovery run** (position 5); gen 5: run holding the optimizer's recorded **best J = 489.3** |
| 2026-05-23 | 21–37 | 17 | 17 (9 ELIGIBLE + 8 WITH_NOTE: final error > 2°) | |
| 2026-05-24 | 38–60 | 23 | 23 (5 ELIGIBLE + 18 WITH_NOTE) | |

Generations 1–3 contain no K\*. Every later generation contains exactly one K\* run, at position 1 (56 of 57 runs).
Day 1 has 8 runs per generation; the later days have 50.

**Acquisition sessions** (inter-run gap > 10 min):

| Session | Time span | Generations | Runs |
|---|---|---|---:|
| 1 | 2026-04-04 09:28–09:45 | 1–20 | 160 |
| 2 | 2026-05-23 22:33 → 2026-05-24 00:16 | 21–40 | 1000 (continuous across midnight) |
| 3 | 2026-05-24 07:00–08:43 | 41–60 | 1000 (after a 6.7 h break) |

Calendar-day strata therefore do not coincide with sessions.

## 3. Split rules and per-stratum decisions (Tasks 1.3, 1.9)

These rules were fixed before any split was computed and were applied mechanically by `tools/protocol_split.py`.
Days are separate experimental strata, and nothing is pooled across strata.

1. **Source controller:** K\* only.
2. **Selection-conditioned runs are removed from every role:** the gen-4 discovery run and the gen-5 best-J run.
3. **Eligible runs:** `run_eligibility` ∈ {ELIGIBLE, ELIGIBLE_WITH_NOTE}, as frozen in `manifests/run_manifest.csv`.
4. **Chronological split per stratum:** the first ⌈0.6 n⌉ eligible K\* runs in time order form the **source
   calibration** set; the rest form the **source holdout**.
5. **Sufficiency:** at least 8 calibration and 5 holdout runs, else STOP.
6. **Matching:** all source and target runs of a stratum must lie in one contiguous acquisition session, else STOP.
   The stratum is **not** redefined by session, because that would adapt the split.
7. **Model acceptance** (§6, fixed before fitting): failure means STOP, with no re-specification.

| Stratum | Calibration K\* | Source-holdout K\* | Targets | Session | Decision |
|---|---|---|---|---|---|
| **2026-04-04** | **9** (gens 6–14, 09:32:38–09:39:25) | **6** (gens 15–20, 09:40:16–09:44:32) | **42** | 1 only | **GO** |
| 2026-05-23 | 11 (gens 21–31) | 6 (gens 32–37) | 284 | 2 only | **STOP**: ARX pole 1.0342 > 1.02 (model acceptance) |
| 2026-05-24 | 14 (3 in session 2, 11 in session 3) | 9 | 441 | 2 + 3 | **STOP**: source runs span two sessions |

STOP strata keep their `STOPPED_*` roles in `candidate_A_protocol_units.csv` for transparency and must not be analysed.

## 4. Time-adjacent target runs (Task 1.4)

**Rule.** A target run is an eligible non-K\* run of the same calendar day that belongs to a generation whose K\* run is
a source-holdout run. It must have been recorded after that K\* run and before the next K\* run.

**Result for stratum 2026-04-04.** There are 42 target runs: 7 per generation in generations 15–20, at positions 2–8.
Each comes from a distinct controller, and each controller was run once. All lie within 45 s after the generation's
holdout K\* run. 40 are ELIGIBLE and 2 are ELIGIBLE_WITH_NOTE:
- `gen_017/experiment_2026_04_04_09_42_05_L298N.mat`
- `gen_018/experiment_2026_04_04_09_43_15_L298N.mat`

No target was excluded for ineligibility. Runs of other generations of the day are not used, so source holdout and
targets cover the same 5.0-minute window (09:40:16–09:45:16).

## 5. Biases documented from metadata only (Task 1.5)

The figures below are for the GO stratum 2026-04-04. They come from run metadata and step-response descriptors, never
from residuals.

- **Optimizer selection (winner's curse).** K\* is "best" only because one run reached J = 489.3 (gen 5). In 52 of its 57
  runs the optimizer gave K\* its failure penalty (J = 1e12). In this stratum that applies to 5 of 6 holdout runs and to
  93 % of target runs.
  - Handling: the discovery and best-J runs are excluded.
  - Remaining bias: K\* is still a controller chosen by the authors' objective. Its "source" status is a design choice,
    not a random draw.
- **Targets are not a random sample of controllers.** They are CEM draws from a distribution fitted to earlier elites.
  - Gains: Kp 3.59–7.38, Ki 3.95–9.66, Kd 0.164–0.311.
  - Normalised gain distance to K\* (search-box units): interquartile range (IQR) 0.15–0.27.
  - Each target has one run, so controller identity and run-to-run variation cannot be separated for any target.
- **Control performance differs systematically.**
  - Overshoot: K\* median 16.5 %; targets IQR 7.5–11.7 %.
  - Final |error|: K\* calibration median 0.54°, K\* holdout 0.27°, targets IQR 0–0.54°.
  - Targets and K\* therefore explore different parts of the operating envelope during each transient.
- **Saturation.** The median is 2 of 101 post-step samples (1.98 %) at ±255 for K\* calibration, K\* holdout and targets alike
  (the step-onset samples).
  Runs with more than 10 % are excluded upstream.
- **Deadband.** The logged `u` is pre-deadband; the applied input is reconstructed as 0 wherever |r − y| < 0.5°. The
  fraction of samples inside the deadband depends on the controller and is not balanced.
- **Run position.** K\* is always first in its generation (inter-run gap 7 s, against 6 s for other runs). Position is
  confounded with source/target role.
- **Chronology.** Calibration (09:32–09:39) precedes holdout and targets (09:40–09:45). Holdout and targets are
  interleaved by generation; a within-session drift would affect calibration-versus-evaluation, not holdout-versus-target.
- **Day/rig effects** (outside the GO stratum). K\* overshoot is about 16 % in session 1 against about 38 % in sessions
  2–3. This is the reason sessions are never pooled.

## 6. External position-residual monitor (Tasks 1.6–1.7)

**Model.** Fixed discrete ARX(2,2,1), with coefficients estimated once per stratum and then frozen:

```
y[k] = -a1*y[k-1] - a2*y[k-2] + b1*ua[k-1] + b2*ua[k-2] + e[k]
```

- `y`: measured position [deg].
- `ua`: applied motor command [PWM counts] = logged `u[k]`, set to 0 at k = 0 and wherever |r[k] − y[k]| < 0.5°
  (the firmware deadband policy).
- Rows: k = 21…120 (0-based; the step is applied at k = 20), 100 per run. Regressors may use the recorded pre-step
  zeros.
- Estimator: ordinary least squares, pooled over the stratum's calibration runs only. Holdout and target files are never
  opened by the fitting script.
- Acceptance checks (fixed before fitting):
  - all regression rows finite, and at least 800 rows;
  - regressor condition number below 1e6;
  - all poles |p| ≤ 1.02;
  - b1 + b2 > 0.

**Frozen fit, stratum 2026-04-04** (900 rows from 9 calibration runs):

| a1 | a2 | b1 | b2 | poles | condition number |
|---|---|---|---|---|---|
| −1.667396718497659 | 0.6663068520648273 | 0.017660328514098312 | 0.037302546899035 | 1.0032451, 0.6641516 | 47.9 |

All checks pass. Stratum 2026-05-23 failed the pole check (1.0342), so it is STOP and is not re-specified.

**Residual and score.**
- One-step-ahead prediction error `ε[k] = y[k] − ŷ[k|k−1]`, using measured past `y` and reconstructed `ua`.
- Window: k = 21…120.
- Score: `s[k] = |ε[k]|`, with no normalisation. This is the position analogue of the frozen study's absolute speed
  residual.

## 7. Threshold calibration, holdout, target evaluation, uncertainty (Task 1.8)

This section was fixed before any of it was computed.

1. **Threshold.** `θ = numpy.quantile(S_cal, 0.99, method="higher")`, where `S_cal` is the pooled score of all
   calibration runs in the stratum (900 samples). This is the 1 % sample-exceedance target, matching the frozen study.
   The threshold is computed and written, with its hash, **before** any holdout or target file is opened.
2. **Exceedance.** A sample exceeds when `s[k] > θ` (strict, because encoder quantisation produces ties).
3. **Source-holdout rate.** For each holdout run, the exceedance fraction over its 100 samples. Stratum value: the mean
   over the 6 holdout runs.
4. **Target rate.** The same per-run fraction for each of the 42 target runs. Stratum value: the mean over target runs.
   The per-run distribution (median, IQR, minimum, maximum) is reported **descriptively**.
5. **Primary contrast.** `Δ = mean target rate − mean source-holdout rate`. It is the only inferential quantity.
6. **Uncertainty.** Run-level bootstrap with B = 600 and seed 33043, 95 % percentile intervals.
   - Each replicate resamples calibration runs (and **refits the ARX and the threshold**), holdout runs and target runs
     independently, with replacement.
   - Intervals are reported for the holdout rate, the target rate and Δ.
   - Samples within a run are never resampled independently.
   - With only 6 holdout runs the intervals will be wide. That is a property of the data and does not justify
     re-splitting.
7. **Exclusions** are fixed and use no residuals or outcomes:
   - the manifest's EXCLUDED_FAILED_CONTROL and RESTRICTED_SATURATION runs;
   - the two selection-conditioned K\* runs;
   - STOP strata;
   - any file whose SHA-256 differs from the manifest.
   There is no outlier removal and no exclusion based on residuals or exceedances.
8. **Pre-declared sensitivities** (reported beside the primary result and never replacing it):
   - (a) exclude ELIGIBLE_WITH_NOTE runs (2 targets);
   - (b) a 5 % exceedance target;
   - (c) window k = 25…120, which drops the step-onset samples.
9. **No other analyses.** No per-target hypothesis tests, no ranking of targets, no search for "transferable"
   controllers, and no post-hoc model or window changes. Any change requires a new, dated protocol version written
   before the changed analysis is run.

## 8. Prohibited claims (Task 1.10)

- **No causal controller effects.**
  - Targets are single runs, chosen adaptively by the optimizer, fixed in run position, and confounded with time.
  - A difference between source holdout and targets describes this calibration's transfer *to these runs*. It is not an
    effect of controller gains.
- **No independent actuator-voltage residual validation.**
  - `u` is a PWM count that the published firmware reproduces exactly from `r` and `y` (2942 of 2942 runs), so an
    "effort" residual is determined by the position data and is not independent evidence.
  - Neither the motor voltage nor the supply voltage is measured.
  - The joint and effort channels of the frozen study therefore have **no** external counterpart here.
- **No speed-control claim.** This is position control: single 90° steps of 3 s, with 101 post-step samples.
- **No pooling or generalisation across days or sessions,** and no use of STOP strata.
- **Exceedance is sample-level,** not an alarm probability.
- **No claim that K\* is a typical controller,** or that the 42 targets represent PID controllers in general.

## 9. Eligible sample units (exact)

| Role | Count | Files |
|---|---:|---|
| Source calibration (2026-04-04) | 9 runs (900 samples) | gens 6–14, `role = source_calibration` |
| Source holdout (2026-04-04) | 6 runs (600 samples) | gens 15–20, `role = source_holdout` |
| Target evaluation (2026-04-04) | 42 runs from 42 controllers (4200 samples) | gens 15–20 positions 2–8, `role = target_evaluation` |
| Excluded selection-conditioned | 2 K\* runs | gens 4, 5 |
| Stopped (not analysable) | 23 K\* + 725 targets | strata 05-23, 05-24 |

The exact file lists are in `protocol/candidate_A_protocol_units.csv`.

## 10. Unavoidable confounders (cannot be removed by design)

1. Single session, single rig and a single transient type in the GO stratum.
2. Source/target role is confounded with controller-selection mechanism, run position and K\*'s winner's-curse origin.
3. One run per target controller.
4. Different operating envelopes for K\* and targets (overshoot, deadband occupancy).
5. Six source-holdout runs, so precision is limited.
6. The model is identified from closed-loop K\* data, with no open-loop excitation.

## Decision

**RESTRICTED.** Proceed only with stratum 2026-04-04, exactly as specified, and only after this draft is accepted and
frozen.

Strata 2026-05-23 and 2026-05-24: **STOP**. They can only be revisited through a new, pre-registered protocol version
written before any residual is computed, for example with a re-justified model structure or session-based strata.
