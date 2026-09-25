# Data availability and provenance boundary

The public repository provides compact derived research data and analysis code sufficient to reproduce the reported primary calibration-transfer matrices, main tables, repeated-run comparison, controller-diversity summaries, residual scale/tail ratios, FAR-target appendix maxima, and principal statistical figures. Original experimental MAT files and university teaching materials are not redistributed because their redistribution rights have not been established. The processed release supports statistical reproduction, not reconstruction of the original experimental acquisition or Lab 2 identification pipeline.

**Level A — public statistical reproduction:** use only the files under `data/processed/` with `python scripts/reproduce_public_results.py`. The script recomputes FARs from exceedance counts, calibration-error summaries, matrix entries, pooling extrema, diversity quantiles, and simulation summary curves.

**Level B — full raw-data reproduction:** would require the original experimental MAT recordings and source acquisition context to regenerate predictive residuals and score sequences. Those inputs are not part of this release. No path or download to them is supplied here.

The 13.34–14.71% cycle-bootstrap interval is carried as a frozen derived summary in `archived_cycle_bootstrap_intervals.csv`; its 600 resampling draws cannot be regenerated from these aggregate public inputs. Figure 5 is a research-authored static ECDF image; the underlying per-sample scores are withheld to avoid a near-waveform release. All other principal numeric tables and Figures 2–4, 6–7 regenerate from the public processed package. Figure 1 is a research-authored schematic.

No physical fault-injection recordings are present. Positive-severity values in `simulation_exceedance_counts.csv` are deterministic model-level overlays on archived nominal-operation residuals, not experimental fault-detection probabilities.

Per-file derivation and output mapping are in [data/README.md](../data/README.md). The release contains no raw waveforms, MATLAB/Simulink projects, lab manuals, or compiled course assets.
