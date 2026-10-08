# Third-party notices for the external-validation material

**No third-party raw data, firmware, archives or documents are redistributed in this repository.**
`tools/fetch_public_inputs.py` obtains them from their original public locations. The checksums are in `sources.json`.

This folder does contain *derived metadata* computed from those sources: run manifests, file hashes, acquisition
parameters, summary statistics, an optimizer-history table, and residual/FAR outputs. The sources and their licences
are:

## Candidate A: Closed-Loop Learning-Based PID Tuning for DC Motor Actuators
- **Source:** https://github.com/DrLizarraga/Closed-Loop-Learning-Based-PID-Tuning-for-DC-Motor-Actuators, commit
  `8c74893a15c2c110e880d41eabd0d648bd2dcc93`.
- **Licence:** MIT. Its README states that the licence covers the code and data files in that repository.
  > Copyright (c) 2026 Jorge A. Lizarraga, Luis F. Luque-Vega, Javier Ruiz-Leon, Rocío Carrasco-Navarro,
  > Marcela E. Mata-Romero, Jesús Antonio Nava-Pintor, Fabián García-Vázquez, Luis O. Solís-Sánchez,
  > Héctor A. Guerrero-Osuna.
  > Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  > documentation files … The above copyright notice and this permission notice shall be included in all copies or
  > substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
  >
  > (Full text: the `LICENSE` file at the commit above.)
- **Associated article:** Lizarraga J.A. et al., "Closed-Loop Learning-Based PID Tuning for DC Motor Actuators Using
  Experimental Data", *Eng* 2026, 7(8), 397, https://doi.org/10.3390/eng7080397 (CC BY 4.0).
- **Derived here:**
  - `manifests/candidate_A_runs.csv`, `manifests/run_manifest.csv`, `manifests/controller_summary.csv`;
  - `protocol/*candidate_A*`, `protocol/kstar_verification.json`, `protocol/learning_campaign_runs_ordered.csv`;
  - `protocol/optimizer_history.csv` (numeric fields of the repository's `adaptive_history.mat`);
  - `results_A/*`.

## Candidate B: OpenMCT end-to-end DC motor workflow dataset
- **Source:** Von Chong, A.; Cardenas, D. (2026), "Dataset for an end-to-end open-source DC motor control workflow:
  current calibration, system identification, and controller validation", Mendeley Data, V2,
  https://doi.org/10.17632/5xvg43r9r8.2 (V1: 10.17632/5xvg43r9r8.1).
- **Licence:** CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- **Changes made:** only inventory metadata and integrity statistics were derived (`manifests/candidate_B_runs.csv` and
  the rows for this dataset in `manifests/run_manifest.csv` and `manifests/controller_summary.csv`); no data values
  were altered. The derived material was used only for an eligibility assessment, which concluded that the dataset was
  not suitable for this purpose. That is not a statement about the dataset's quality for its intended uses.

## Candidate C: ET-RLS-STR STM32 reproducibility package
- **Source:** Tran, T. T.; Tran, N. T. (2026), Zenodo, https://doi.org/10.5281/zenodo.21201595 (v1.0.0). Version 2.0.0
  (https://zenodo.org/records/21389722) was used only for file times and a content comparison.
- **Licence:** MIT.
  > Copyright (c) 2026 Tam Nhut Tran and contributors.
  > The MIT permission notice and warranty disclaimer apply (full text: `LICENSE` inside the archive).
- **Derived here:** `manifests/candidate_C_runs.csv`, `manifests/candidate_C_units.csv`,
  `protocol/candidate_C_splits.json`, `protocol/candidate_C_preflight.txt`, `results_C/*`.

## Our own material
The protocols, reports, scripts and analysis outputs in this folder are original work for this repository. The code is
under the repository's MIT licence (see `../LICENSE` and `../docs/LICENSING_NOTES.md`). None of the third-party
authors has reviewed or endorsed these assessments.
