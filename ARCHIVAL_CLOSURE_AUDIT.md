# Archival closure audit (branch `archival-closure-2026-10`)

**Date:** 2026-10-08.
**Base:** `main` at `26d1710c551fc3a8af1a9470c94c4fa018fd4536`. Before branching, the local HEAD was verified identical to
`origin/main`, with no uncommitted changes.
**Scope:** documentation of the archival status, and a public, separated record of the later external-data
assessments.
**Not done:** no scientific experiment was run; no model, FAR value, interval, protocol, exclusion or result was
changed; nothing was pushed, merged, tagged or published.

## 1. Changed files

| File | Change |
|---|---|
| `README.md` | Archival-status notice. Limitations sentence repeated under the results. New "External-data assessments" section (honest summary, predictor-architecture caveat, no replication or causal claim). Links to the new docs and folder. The original 14.07 % result and every original section are kept. |
| `docs/LICENSING_NOTES.md` | Appended a section on the external-validation material (derived third-party metadata; raw files not redistributed) |
| `CITATION.cff` | Version 0.1.0 → 0.2.0, `date-released` 2026-09-25 → 2026-10-08, one abstract sentence on the archival closure. No DOI added. |
| `.gitignore` | Added `external_validation/raw/`, so fetched third-party inputs can never be committed |

## 2. New files
- **`docs/RESEARCH_STATUS.md`:** original findings, external findings, replication table, confounding, publication
  status, hardware-validation requirements.
- **`docs/EXTERNAL_VALIDATION.md`:**
  - eligibility;
  - the Lizarraga protocol and results for 2026-04-04 (calibration, holdout and targets, all six generation
    comparisons);
  - the STM32 protocol, with all six predefined S1/S3 comparisons;
  - negative findings and uncertainty limits;
  - predictor and measurement differences;
  - source references.
- **`ARCHIVAL_CLOSURE_AUDIT.md`:** this file.
- **`external_validation/`** (67 files):
  - **Copied unchanged** from the working directory (57 files): protocols, eligibility audits, result reports,
    manifests, frozen splits and coefficients, all numerical outputs, and the original scripts. Each is byte-identical
    to its working original; SHA-256 values and original modification times (UTC) are in
    `external_validation/FILE_PROVENANCE.csv`.
  - **Added for this release** (10 files):
    - `README.md` (index);
    - `THIRD_PARTY_NOTICES.md`;
    - `sources.json` (URLs, versions, commits, DOIs, checksums);
    - `FILE_PROVENANCE.csv`;
    - `tools/fetch_public_inputs.py` (pinned, checksum-verified download);
    - `tools/derive_supplementary.py` (steps first run as inline commands, collected as scripted stages with the same
      logic);
    - `tools/reproduce_external.py` (end-to-end regeneration and byte comparison).
  - **Not included:**
    - `raw/` (third-party data);
    - all university MATLAB/Simulink course assets;
    - `prospective_validation/` (hardware models and acquisition package);
    - private working notes.

## 3. Unchanged scientific files (SHA-256 identical to `main` at `26d1710`)

All 43 files below were hashed before branching and again after all edits; every hash is identical. They include
`manuscript/paper.pdf`, `manuscript/manuscript_v3.md`, all of `data/processed/`, all original results, the reproduction
script, the tests and the configuration. (`CITATION.cff`, originally
`9ed88491…a90c95`, was changed only for the 0.2.0 version bump; see section 7.)

| File | SHA-256 |
|---|---|
| `LICENSE` | `1abcd710c96bb5c52644cdcedbd09c19171f8a9b183890112b4fb967138c9642` |
| `config/release_analysis.json` | `42d816d1fa9b14bbf885415e8a18fba9bf70ecce57d6166b4ac1644fa31bee36` |
| `data/README.md` | `f98f73af11bf22b5b9071dad5630dd8f45ad9614f4e83fc5beeadb9b0f9d483c` |
| `data/processed/archived_cycle_bootstrap_intervals.csv` | `f3a6d01d422db7a5556a4adaba00ec5c15498a325c61fbd95847948d6b07fe5b` |
| `data/processed/controllers.csv` | `82a411826c0209d2388b363bb01df589ba095e71505118871682eabe3ad09149` |
| `data/processed/diversity_cells.csv` | `f051d1b4db05074c72e0bcd5cad97010d712e55d23768a66cb0d03e2b75d3c31` |
| `data/processed/far_target_ablation_counts.csv` | `e81d7a2516abc86b09b868b29400b8d4fb91d94cfd34a00a502e03c62a2d5b99` |
| `data/processed/pooled_evaluation_counts.csv` | `c2f91569868be1039982633c2dc10a86f61bfbdc28e9b93af5b74034baf10d65` |
| `data/processed/primary_transfer_counts.csv` | `6a9decaea6183226b5f3406afcbfb4ca82f93c0ba1ac88ada15aaafc37681a86` |
| `data/processed/reciprocal_score_statistics.csv` | `c83e13e44c37e04f88a471d8eeaae4aaa830dc9ca4276576afbbc9c5ccb911dc` |
| `data/processed/run_transfer_counts.csv` | `04c958a086d83dc38acb0371d8a619e039fd8d7d376d25e2a5ffe069c6987ee7` |
| `data/processed/runs.csv` | `c9d02c9e81b0e0c283317630612eb952628da102ef43996f19ba07427c54a75d` |
| `data/processed/simulation_exceedance_counts.csv` | `7a8338412e63ac1d851e80ecb6b039a88dc9c348e33c4ee214a4d50a4d2e11cf` |
| `docs/DATA_AVAILABILITY.md` | `e7d1aa8d41b6b6f4d2fddfce2027bf58b7cc8382ebca20388f3904e5cd5294c4` |
| `docs/GITHUB_METADATA.md` | `3dc8662d83eb43eeae6f112286fdca5d34e252c046efabd4cb1b00258b903689` |
| `docs/PUBLIC_RELEASE_AUDIT.md` | `d8cc4865c3a27b4583861f50cde318bafd679e2e16da27814f85612736e63347` |
| `docs/REPRODUCIBILITY.md` | `c5ab8b952e2050f89af8f50f76a3c1625c7d5d03d141e1a6a4594f3b30743ce1` |
| `docs/ZENODO_METADATA.md` | `675e1259d2c7ded9e6887403d98c376913ef03105474ea09a043407f27d5ebe2` |
| `manuscript/manuscript_v3.md` | `64b452affc3b4fa364a52cc9c666ec450bb20aea0d29b0b76c40da9823395821` |
| `manuscript/paper.pdf` | `daf23d89d21133c60fa57c36e865c7f021024fe6e33037f5c8b3efa54695610f` |
| `requirements.txt` | `35cf8c20f7999ec3cdf7cc07f2793446106de0bd71b614b6f04ff148b4d5ba25` |
| `results/figures/figure1_pipeline.png` | `f53c136289bd1a8f1df09d3571968d01ae69d2e5411170785d913dd850cb1b60` |
| `results/figures/figure2_controller_coverage.png` | `169e9544447402cc3cc619439845f4764f06a1d8c9ba2ac9d74e98ecd58f8cfe` |
| `results/figures/figure3_far_heatmaps.png` | `3cc63dd90866cb854a67f3ecdb9bf822e7f07a7d6238681cd2503752debe625c` |
| `results/figures/figure4_transfer_categories.png` | `0b41d6062009ae0541af0cac4e7f21d174b70e8208288383bf86c14eade8ef60` |
| `results/figures/figure5_reciprocal_ecdf.png` | `231e7df21f81b47f6de1a1a6e2fe276524110860038a19d44cd420f47ac4c4af` |
| `results/figures/figure6_diversity_pooling.png` | `e1afc6c93b129afc33eaa958eaad3c5836542c88112e993e72844edd4640b07b` |
| `results/figures/figure7_simulated_tradeoff.png` | `ef94f2fb174e98e01c699a0bef1cbcbbf3ea847fd46c975a7b8a4f29651b4fb7` |
| `results/tables/appendix_c_far_target_ablation.csv` | `2959bdc5d4db58dadda313801fa24dbc5ab594b68d196b2a8071214e056d0e2a` |
| `results/tables/calibration_diversity_summary.csv` | `d31dce8c90b3ae469e5285fcfe60a64e77a3ba8a8fcaf91c3d7101fb3e48a4ce` |
| `results/tables/far_matrix_joint.csv` | `c946c55524497fc3784668748c2ff8947504d2d04bc54db0fde809b3b6df6927` |
| `results/tables/far_matrix_r_u.csv` | `6e2bce018c076a34b10bf0166c5bc820fdce08a624cb948c25be389e29f01a6f` |
| `results/tables/far_matrix_r_y.csv` | `28acd00ab34705e62018b3600a4722768c17db20d736cbfa1f2d9ec161a919ae` |
| `results/tables/headline_results.json` | `f5fdec6ce660d00166ee2f6c6e0c789346ae695b78eb865aa8856872d59b9be7` |
| `results/tables/reciprocal_score_mechanism.csv` | `ecb9743e0d2c4e4e4d2d2b1e155432b3d0805a0705b2591c4e48934883e0328a` |
| `results/tables/simulation_sensitivity_summary.csv` | `894a1b090e7c0d4d1199ad767c29f1a81cae17e2179e88931bd0bbe02cf50dab` |
| `results/tables/table1_controllers.csv` | `82a411826c0209d2388b363bb01df589ba095e71505118871682eabe3ad09149` |
| `results/tables/table2_primary_transfer.csv` | `861b2208f1df104c8431a4821342a1e31ca8bcbc7f3ce103b38847b9e6d320a5` |
| `results/tables/table3_same_controller_runs.csv` | `a7dfeaf32f3179764d9e1b4468019ab2fc0ec8101b882bc6d6cfcbfee9693514` |
| `results/tables/table4_calibration_strategies.csv` | `129f2ca6ed1b19db9d7bdbee8c0b1cd12575c055b88fa0015c6bbe5f627d5573` |
| `results/tables/transfer_category_summary.csv` | `acccfb9475a4baed50a611dca360ae7cdb7a97972f8a9b8864e14f06f22c8dc9` |
| `scripts/reproduce_public_results.py` | `3bc363107d33e023f12b07f9903927dd124c04599f0680ecfddde59f6b17d135` |
| `tests/test_public_reproduction.py` | `03280e819a804134c6bf931976c28ccd64561fb32f6bd02a4c631b9b2d2acabe` |

## 4. Tests

| Check | Result |
|---|---|
| Original test suite (`python -m unittest discover -s tests`, run on an export of this branch without `.git`, as the payload test requires) | **PASS**: 7/7, both before and after re-running the reproduction |
| Original reproduction (`scripts/reproduce_public_results.py`) | **PASS**: 20/20 result files regenerated byte-identically; headline 14.07 % C04→C01 effort; same-controller maxima 1.29 / 1.39 / 1.38 %; contrasts 5.20 / 3.31 / 3.26× |
| `data/processed/` hashes (10 files) | **PASS**: identical to `main` |
| `manuscript/paper.pdf` SHA-256 `daf23d89d21133c60fa57c36e865c7f021024fe6e33037f5c8b3efa54695610f` | **PASS**: unchanged |
| External reproduction from **freshly downloaded** public inputs (`external_validation/tools/reproduce_external.py`) | **PASS**: 34/34 computed outputs byte-identical. The analysis scripts' internal hash checks of the frozen protocol inputs passed, so the regenerated protocol units, splits and ARX coefficients matched exactly. |
| Live fetch of all public inputs (GitHub commit, 29 Mendeley files, two Zenodo archives) with checksum verification | **PASS** (one HTTP-header issue in the new fetch script was fixed before the final run) |
| Relative links in the new and changed documents | **PASS**: all resolve |
| New files: forbidden payloads (`.mat`, `.slx`, `.bin`, `.elf`, `.hex`, `.m`), archives, binaries | **PASS**: none |
| New files: absolute local paths, e-mail addresses, machine or user identifiers | **PASS**: none |

No test failed in the final state.

## 5. Public-data redistribution safety

| Source | Licence | What is in this repository | Raw files redistributed? |
|---|---|---|---|
| Lizarraga et al., GitHub `8c74893a` | MIT (README extends it to the data files); article CC BY 4.0 | Derived manifests, metadata, optimizer-history numbers, analysis outputs; MIT notice in `THIRD_PARTY_NOTICES.md` | **No** (fetched) |
| OpenMCT, Mendeley 10.17632/5xvg43r9r8 v2/v1 | CC BY 4.0 | Inventory metadata only; attribution and description of changes | **No** (fetched) |
| ET-RLS-STR, Zenodo 10.5281/zenodo.21201595 (+ v2.0.0) | MIT | Derived manifests, chronology, analysis outputs; MIT notice | **No** (fetched) |
| University of Sydney ELEC3304 course material and original MAT recordings | rights not established | nothing | **No** (unchanged policy) |
| `prospective_validation/` hardware models (derived from course models) | not public | nothing | **No** |

Redistributing the third-party raw files would be permitted under MIT and CC BY 4.0 with notice. It was **not judged
desirable**: fetching pinned, checksum-verified originals keeps the authoritative copies at their sources and avoids
re-hosting about 80 MB of other authors' data.

## 6. Reproducibility limitations
- **External inputs depend on third-party hosting** (GitHub, Mendeley Data, Zenodo). If a source disappears, the
  committed checksums identify the exact files that would be needed.
- **Inline steps.** Some derivation steps were first executed as inline commands. They are reproduced by
  `derive_supplementary.py` with the same logic, and their outputs regenerate byte-identically. The original inline
  executions themselves are not otherwise logged.
- **STM32 chronology** relies on per-file modification times stored in the Zenodo v2.0.0 archive, which are
  unauthenticated metadata.
- **Pilot-study limits are unchanged.** Level-A statistical reproduction from processed data only: raw MAT files,
  Simulink models and the Figure 5 per-sample scores are not public, as stated in `docs/DATA_AVAILABILITY.md`.
- **Verbatim internal references.** The external documents are kept verbatim (several are hash-referenced by the
  analysis scripts) and mention internal working paths that are not public. `external_validation/README.md` explains
  this.

## 7. Citation and version metadata
- **Released version: 0.2.0** (software). It adds documentation and the separated external-assessment material, with
  no change to the original scientific content.
- `CITATION.cff` was updated after approval: `version: 0.2.0`, `date-released: 2026-10-08`, and one abstract sentence.
  Title, authors, ORCID, licence and repository URL are unchanged.
- `docs/ZENODO_METADATA.md` is unchanged: a preparation note for a planned paper record, with no DOI reserved.
- No DOI, journal submission or acceptance is asserted anywhere, and no previously issued identifier was altered (none
  exists).

## 8. Status
Approved by the author on 2026-10-08. Merged into `main` and released as tag `v0.2.0`.
