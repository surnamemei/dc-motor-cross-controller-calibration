# Cross-Controller Validity of Residual-Monitor Calibration in a PI-Controlled DC Motor

This repository accompanies an independent research preprint / manuscript. It has not been represented as peer-reviewed or accepted for publication.

> **Archival status (October 2026).** This is an archived **pilot study**. Its manuscript, processed data, results and
> reproduction scripts are frozen and unchanged. Later external-data assessments are recorded separately, including
> their null and negative results, in [docs/EXTERNAL_VALIDATION.md](docs/EXTERNAL_VALIDATION.md). The overall status is
> in [docs/RESEARCH_STATUS.md](docs/RESEARCH_STATUS.md).

## Author

Jinghang Mei<br>
The University of Sydney<br>
ORCID: https://orcid.org/0009-0007-2901-3285

The affiliation identifies the author and does not imply institutional endorsement.

## Research question

How portable is a fixed residual monitor's nominal-operation sample false-alarm calibration across different PI configurations exercised on the same physical DC motor?

## Results in brief

The maximum effort-residual sample FAR among 32 eligible controller-distinct transfers was **14.07%** at a nominal 1% calibration target. The maximum effort FAR across four independent same-controller cross-run directions was **1.39%**. Controller-diverse calibration reduced several archive-specific unseen-controller extremes. A separate model-level simulation found a substantial sensitivity cost in selected gain-change cases; it does not establish real fault-detection performance.

These results come from one motor. Only two configurations have independent repeated runs, and controller and session
remain partly confounded (see Manuscript and limitations below).

## External-data assessments (after the pilot)

Three public DC-motor datasets were assessed later under pre-registered protocols. The details are in
[docs/EXTERNAL_VALIDATION.md](docs/EXTERNAL_VALIDATION.md); protocols, manifests, scripts and outputs are in
[external_validation/](external_validation/).

- **Lizarraga et al. (position PID, one usable session):** target-controller FAR 0.74 %, against 0.17 % on the source
  controller's own held-out runs. Paired difference +0.57 pp [0.00, 1.81] over 6 generation pairs.
- **STM32 speed-PI benchmark (one session, fixed controller order):** in six predefined comparisons, target FAR
  0.59–1.89 %. Differences from the same-controller baseline were −0.27 to +1.03 pp, with mixed signs.
- **OpenMCT dataset:** not suitable, because it has no repeated runs per controller.

**These are not a multi-platform replication.**
- The external monitors use a **different predictor architecture**: one-step-ahead input–output predictors, which
  largely remove the controller from the prediction. The pilot uses a controller-dependent closed-loop simulation
  residual.
- No external dataset allows an effort/voltage residual, so the 14.07 % effort result was neither replicated nor
  tested.
- No external result supports a causal claim about controller gains.

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
- `docs/`: data-availability, reproduction, and licensing notes; [research status](docs/RESEARCH_STATUS.md) and [external assessments](docs/EXTERNAL_VALIDATION.md).
- `external_validation/`: later external-data assessments (protocols, manifests, scripts and outputs; third-party raw data are fetched, not redistributed).

## Data availability

Original experimental MAT files and university teaching materials are excluded because redistribution rights have not been established. This package supports statistical reproduction from derived inputs, not reconstruction of the original acquisition or Lab 2 identification pipeline. See [data availability](docs/DATA_AVAILABILITY.md).

## Manuscript and limitations

**Preprint PDF:** [paper.pdf](manuscript/paper.pdf)

[Manuscript Version 3](manuscript/manuscript_v3.md) reports a restricted pilot on one physical motor. Only two controller configurations have independent repeated runs; run chronology and controller identity remain partly confounded. FAR means nominal-operation **sample-level score exceedance**, not a per-cycle or independent-event alarm probability. Positive-severity degradation sensitivity is simulated, not physical-fault evidence.

## Citation

Software citation metadata are provided in [CITATION.cff](CITATION.cff). A preprint, arXiv, or journal identifier can be added if one is issued; none is asserted here. Manual paper-deposit fields are recorded in [Zenodo metadata notes](docs/ZENODO_METADATA.md).

## License

Original research software in this repository is released under the
[MIT License](LICENSE).

The license does not apply to excluded university teaching materials,
unreleased original experimental MAT files, or third-party copyrighted
content. See [licensing notes](docs/LICENSING_NOTES.md) for the scope of the
public release.
