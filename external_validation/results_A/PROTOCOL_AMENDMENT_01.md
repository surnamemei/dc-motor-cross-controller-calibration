# Protocol amendment 01: uncertainty procedure (Candidate A, stratum 2026-04-04)

**Written:** 2026-10-08. **Status at the time of writing:** no residual has been computed on any source-holdout or target
run. The only residual-related quantities that exist are the frozen ARX coefficients, which were fitted on calibration
rows only. No threshold or FAR (false-alarm rate) has been computed for any role.

**Amends:** `FROZEN_PROTOCOL_DRAFT.md` §7 item 6, the uncertainty procedure only.

**Unchanged:**
- model: ARX(2,2,1) on applied input `ua` and position `y`, rows k = 21…120;
- coefficients: `protocol/candidate_A_arx_frozen.json`;
- score `|ε|`, threshold `numpy.quantile(…, 0.99, method="higher")`, strict exceedance `>`;
- the stratum and the roles (calibration K\* generations 6–14, 9 runs; source holdout K\* generations 15–20, 6 runs;
  42 targets in generations 15–20, 7 per generation);
- the exclusions;
- the three pre-declared sensitivity analyses.

**Frozen inputs:**

| File | SHA-256 |
|---|---|
| `protocol/candidate_A_arx_frozen.json` | `cf6997608312e1e52e20050acf24f910d949b7ef61ce2722dc07936da0341709` |
| `protocol/candidate_A_protocol_units.csv` | `60de3592bf2f7e4450dbfb0f8134899967fb797e35d34f446c399b6c5dedc61c` |
| `FROZEN_PROTOCOL_DRAFT.md` | `24a846c361a3f0688a98c59a3be6c19adec6a4993ce2e63e4e44902eae22a41f` |

## Reason

The draft resampled holdout runs and target runs independently. In the data, every generation g ∈ {15,…,20} contains one
source-holdout K\* run followed within 45 s by its seven target runs, so the two are paired in time. Resampling them
independently ignores that pairing, along with any variation shared within a generation (drift, temperature, optimizer
state). The amendment makes the generation the resampling unit for validation data, matching the design. It was decided
on design grounds alone, before any held-out result existed.

## Amended procedure

1. **Point estimates.**
   - Calibration FAR: the mean in-sample exceedance fraction over the 9 calibration runs.
   - Held-out K\* FAR: the mean over the 6 holdout runs.
   - Target FAR: the mean over the 6 generations of each generation's mean over its 7 target runs. With equal generation
     sizes this equals the mean over all 42 runs.
   - Generation-paired difference: `d_g = mean target FAR in g − K* holdout FAR in g`.
   - Overall paired difference: `D = mean over g of d_g`, which is the primary contrast.
   - Everything uses the frozen coefficients and the threshold from the 9 calibration runs.
2. **Bootstrap.** **B = 600** draws (unchanged), seed **33043**, `numpy.random.default_rng`. Each draw does the
   following:
   - (a) Resamples **complete calibration runs**: 9 of the 9, with replacement.
   - (b) **Refits** the ARX by OLS on the resampled runs' rows.
   - (c) Applies the frozen acceptance checks to the refit: finite rows, at least 800 rows, condition number < 1e6, all
     |p| ≤ 1.02, b1 + b2 > 0.
   - (d) **Recalibrates** the threshold as the 99th percentile (`higher`) of the resampled calibration runs' scores
     under the refit model.
   - (e) Resamples **generations**: 6 of {15,…,20}, with replacement. Each drawn generation contributes its K\* holdout
     run and all 7 of its target runs together, so the pairing is preserved.
   - (f) Computes the held-out K\* FAR, the target FAR, each `d_g` and `D`, using the refit model and the recalibrated
     threshold.
3. **Bootstrap failures.** A draw whose refit fails any check in 2(c), or produces a non-finite statistic, is a
   **failure**.
   - It is not redrawn or replaced.
   - All 600 draws are attempted.
   - The number of failures and their reasons are reported.
   - Percentile intervals (95 %: 2.5th and 97.5th percentiles) use the successful draws, and the number of successful
     draws is stated beside each interval.
4. **Generation-level differences.** The six `d_g` are reported individually as point estimates.
   - A run-level bootstrap within a generation would rest on one K\* run, so no per-generation interval is computed.
   - The only per-generation uncertainty statement is the spread of the six `d_g`.
5. **Effective units.** Reported counts:
   - 9 calibration runs (one controller, one session);
   - 6 holdout runs;
   - 42 target runs from 42 controllers;
   - **6 generation pairs, which are the independent units for `D`**;
   - samples per role, with lag-1 autocorrelation of exceedance indicators (descriptive);
   - a within-generation intraclass correlation of target-run FAR, with the implied effective number of target units
     (descriptive).
6. **Sensitivities.** The three pre-declared sensitivities use this same procedure. They are reported beside the primary
   result and do not replace it:
   - (a) excluding the 2 ELIGIBLE_WITH_NOTE targets (generations 17 and 18 then have 6 targets);
   - (b) a 5 % exceedance target;
   - (c) rows k = 25…120.
7. **Diagnostics.** Saturation and performance diagnostics are descriptive only. Spearman correlations between per-run
   FAR and each diagnostic are reported without adjustment, selection or testing for significance. They are never used
   to exclude runs or to re-define the analysis.

## Order of execution
1. Verify the SHA-256 of every input MAT file against the manifest, and of the frozen coefficient file.
2. Compute and write the calibration residuals and threshold (`results_A/calibration_threshold.json`).
3. Only then load the holdout and target runs and compute every reported quantity.
4. No step may change after step 3 begins.
