# Public processed research data

These files contain **derived metadata or statistical quantities**, not raw waveforms or converted MAT files. The source class is private experimental recordings plus research-generated analysis outputs. No original source filename, university model, or sample-by-sample speed/command/residual sequence is included. The private packaging utility verifies that sample-level FAR fractions can be represented as exact integer exceedance counts before export.

| Public file | Derivation from private/original class | Why this is a derived research artifact | Reproduces |
|---|---|---|---|
| `controllers.csv` | Research-extracted controller manifest from recorded PI settings; selected fields only | Nine gain/bandwidth/count descriptors, no course model or waveform | Table 1; Figure 2; controller-ID checks |
| `runs.csv` | Inclusion-screened run manifest from original recordings | Run IDs, controller IDs, sample rate, cycle counts only; no original source path or hashes | 11-run/85-cycle checks; repeated-run identity |
| `primary_transfer_counts.csv` | Frozen research transfer FARs computed from private residual scores | Integer exceedance counts per source–target/channel, plus evaluation sample count; no score series | 14.07%; 32-pair Table 2; Figure 3 matrices |
| `run_transfer_counts.csv` | Frozen run-level research comparisons | Aggregate exceedance counts per run direction/channel; no time series | Table 3; same-controller maxima; 3.26–5.20× contrast; Figure 4 |
| `pooled_evaluation_counts.csv` | Frozen pooled/LOCO research results | Aggregate counts by target/strategy, without calibration samples | Table 4 pooled maxima |
| `diversity_cells.csv` | Frozen subset–target results from private calibration-diversity analysis | One FAR summary per controller subset/target/weighting, with balanced selection already summarized over 40 choices; no cycle scores | Diversity medians, 95th percentiles, worst FAR; Figure 6 |
| `simulation_exceedance_counts.csv` | FR13 research model-level overlay summaries | Aggregate counts by controller/mode/severity/strategy/channel, with explicit simulation/observed quantity flag | Simulation summary; Figure 7; C07 39.10%→0% example |
| `reciprocal_score_statistics.csv` | Research-generated C04/C01 score-distribution statistics | MAD, q99, threshold, Wasserstein, and KS summaries; no empirical score sequence | §8 scale/tail ratios and distributional mechanism summary |
| `far_target_ablation_counts.csv` | Frozen 0.5%, 1%, 2%, 5% nominal-FAR target comparisons | Aggregate exceedance counts for each eligible source–target/channel/target | Appendix C maxima |
| `archived_cycle_bootstrap_intervals.csv` | Frozen cycle-block bootstrap output from private scores | Interval endpoints and 600-draw count only, no draws or residual sequences | Traces 13.34–14.71% interval; **does not rerun the bootstrap** |

`primary_transfer_counts.csv`, `run_transfer_counts.csv`, and `pooled_evaluation_counts.csv` use **800 evaluated samples per complete four-second cycle**. Counts and denominators support recomputation of the displayed FARs. Diversity cell values are already selection medians in the balanced condition; the public pipeline recomputes the cross-cell summaries but cannot redo the underlying selection. Figure 5's ECDF per-sample input is excluded. These limits are stated in [data availability](../docs/DATA_AVAILABILITY.md).
