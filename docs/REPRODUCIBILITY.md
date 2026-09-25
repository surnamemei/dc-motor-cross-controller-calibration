# Public reproducibility

## Levels

- **Level A — public statistical reproduction:** derived metadata, exceedance counts, and subset–target summaries under `data/processed/` reproduce the main transfer, repeated-run, pooled calibration, diversity, residual-mechanism, FAR-target appendix, and simulation-summary tables plus Figures 2–4, 6–7.
- **Level B — full raw-data reproduction:** recreating Lab 2 identification, M2 residuals, and score sequences from original MAT recordings. Level B is unavailable publicly because redistribution rights for those recordings and teaching materials have not been established.

The archived cycle-bootstrap interval is reported but cannot be rerun from aggregate counts; the released Figure 5 ECDF likewise has no public per-sample score input. These are explicit Level A limits, not claims of raw-data reproduction.

## Environment and command

Tested with Python **3.12.3**. Install the listed Python dependencies in a clean environment:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_public_results.py
python -m unittest discover -s tests -v
```

No MATLAB, Simulink, GPU, private file, or local absolute path is used by the public script. The command reads only this tree's `data/processed/` directory. The output directory may be changed with `--output PATH`; inputs remain inside this tree.

## Expected outputs and runtime

- `results/tables/table1_controllers.csv`, `table2_primary_transfer.csv`, `table3_same_controller_runs.csv`, `table4_calibration_strategies.csv`.
- Three `far_matrix_*.csv` files; category, diversity, reciprocal-score, FAR-target ablation, and simulation summaries; `headline_results.json`.
- `results/figures/figure2_controller_coverage.png`, `figure3_far_heatmaps.png`, `figure4_transfer_categories.png`, `figure6_diversity_pooling.png`, `figure7_simulated_tradeoff.png`.
- Research-authored Figure 1 schematic and Figure 5 ECDF are packaged as static files.

The public reproduction took **2.39 seconds** in the audit environment; allow roughly 2–10 seconds on a standard workstation. The seven-test suite took about **4 seconds**. Different graphics backends may change PNG bytes without changing plotted values.

## Seed and numerical policy

`config/release_analysis.json` records seed **33043**, the frozen upstream selection/bootstrapping seed. Level A performs no random draws; it deterministically aggregates fixed derived inputs. Tests rerun the command and compare all generated table bytes. FAR is exceedance count divided by evaluated sample count. Diversity 95th percentiles use NumPy's standard linear interpolation, matching the frozen analysis. `0.0` labels in heatmaps are one-decimal rounding, not proof of exact zero.
