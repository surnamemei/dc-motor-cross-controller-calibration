# Cross-Controller Validity of Residual-Monitor Calibration in a PI-Controlled DC Motor

This repository accompanies an independent research preprint / manuscript. It has not been represented as peer-reviewed or accepted for publication.

## Research question

How portable is a fixed residual monitor's nominal-operation sample false-alarm calibration across different PI configurations exercised on the same physical DC motor?

## Results in brief

The maximum effort-residual sample FAR among 32 eligible controller-distinct transfers was **14.07%** at a nominal 1% calibration target. The maximum effort FAR across four independent same-controller cross-run directions was **1.39%**. Controller-diverse calibration reduced several archive-specific unseen-controller extremes. A separate model-level simulation found a substantial sensitivity cost in selected gain-change cases; it does not establish real fault-detection performance.

## Reproduce the public statistical results

Python 3.12 is recommended. From this repository root:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_public_results.py
python -m unittest discover -s tests -v
```

The command reads only `data/processed/` and creates `results/tables/` and Figures 2–4, 6–7 in `results/figures/`. Figures 1 and 5 are included as research-authored static figures; Figure 5's underlying per-sample scores are not released. See [reproducibility levels](docs/REPRODUCIBILITY.md).

## Repository structure

- `config/`: fixed target, sample rate, cycle size, and seed record.
- `data/processed/`: compact derived research quantities, with per-file provenance in [data README](data/README.md).
- `scripts/`: public statistical reproduction from processed inputs only.
- `tests/`: public-only integrity, headline, and determinism tests.
- `results/tables/` and `results/figures/`: reproduced tables and final research figures.
- `manuscript/`: frozen Version 3 manuscript with a public-release data statement.
- `docs/`: data-availability, reproduction, and licensing notes.

## Data availability

Original experimental MAT files and university teaching materials are excluded because redistribution rights have not been established. This package supports statistical reproduction from derived inputs, not reconstruction of the original acquisition or Lab 2 identification pipeline. See [data availability](docs/DATA_AVAILABILITY.md).

## Manuscript and limitations

[Manuscript Version 3](manuscript/manuscript_v3.md) reports a restricted pilot on one physical motor. Only two controller configurations have independent repeated runs; run chronology and controller identity remain partly confounded. FAR means nominal-operation **sample-level score exceedance**, not a per-cycle or independent-event alarm probability. Positive-severity degradation sensitivity is simulated, not physical-fault evidence.

## Citation

Citation metadata are provided in CITATION.cff. A preprint identifier or DOI will be added if the manuscript is publicly archived or published. 

## License

Original research software in this repository is released under the
[MIT License](LICENSE).

The license does not apply to excluded university teaching materials,
unreleased original experimental MAT files, or third-party copyrighted
content. See [licensing notes](docs/LICENSING_NOTES.md) for the scope of the
public release.