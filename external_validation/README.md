# External-data assessments (2026-10-08)

This folder holds the protocols, run manifests, scripts and numerical outputs of the external-data assessments made
**after** the pilot study. They are kept separate from the original study: nothing here changes
`../manuscript/paper.pdf`, `../manuscript/manuscript_v3.md`, `../data/processed/` or `../results/`.

**Start with:** [`../docs/EXTERNAL_VALIDATION.md`](../docs/EXTERNAL_VALIDATION.md) for the public summary, and
[`../docs/RESEARCH_STATUS.md`](../docs/RESEARCH_STATUS.md) for the overall status.

## Contents

| Path | Content |
|---|---|
| `ELIGIBILITY_REPORT.md` | Eligibility audit of Candidates A (Lizarraga, GitHub) and B (OpenMCT, Mendeley) |
| `THIRD_DATASET_AUDIT.md` | Eligibility audit of Candidate C (STM32, Zenodo) |
| `FROZEN_PROTOCOL_DRAFT.md`, `results_A/PROTOCOL_AMENDMENT_01.md` | Candidate A protocol and its uncertainty amendment (hashed before held-out results existed) |
| `results_A/RESULTS_A.md` + `results_A/*` | Candidate A results and all numerical outputs |
| `STM32_PROTOCOL.md` | Candidate C frozen protocol |
| `STM32_RESULTS.md` + `results_C/*` | Candidate C confirmatory results and all numerical outputs |
| `CROSS_PLATFORM_ASSESSMENT.md` | Comparison with the original pilot study |
| `EXTERNAL_VALIDATION_STATUS.md` | Status table at the end of the work |
| `manifests/`, `protocol/` | Run-level eligibility, frozen splits, frozen model coefficients, decisions |
| `tools/` | All scripts (see Reproduction) |
| `sources.json`, `SOURCES.md` | Source URLs, versions, commits, DOIs and checksums |
| `FILE_PROVENANCE.csv` | SHA-256 and original modification time (UTC) of every file copied from the working directory, plus the files added for this release |
| `THIRD_PARTY_NOTICES.md` | Licences and attributions of the external sources |

## Reproduction

The third-party inputs are **not** redistributed here; they are fetched from their public sources and verified by
checksum.

```bash
cd external_validation
python3 tools/reproduce_external.py /path/to/new/workdir
```

The wrapper copies the scripts and the three hashed protocol documents into an empty work directory. It downloads the
inputs (`tools/fetch_public_inputs.py`), runs the full chain, and byte-compares each regenerated output with the copy
committed here. On 2026-10-08 a run from freshly downloaded inputs regenerated **34 of 34** computed outputs
identically.

**Not compared:**
- run logs, which contain execution timestamps;
- `manifests/eligibility_decisions.json`, a hand-authored decision record.

**Requirements:** Python 3.12 with numpy, pandas and scipy; git; network access to GitHub, Mendeley Data and Zenodo.
`tools/analysis_A.py` and `tools/analysis_C.py` check the hashes of their frozen inputs and stop if anything differs.

**Two kinds of scripts:**
- The scripts already used during the 2026-10-08 work are kept **byte-identical**; their hashes are recorded in the run
  logs.
- `tools/derive_supplementary.py` collects steps first run as inline commands, using the same logic. Together with
  `fetch_public_inputs.py` and `reproduce_external.py`, it was added for this release.

## Notes for readers
- **Verbatim documents.** The protocols and reports are reproduced as written during the work. Some mention internal
  working paths that are not part of this public repository, for example `research_motor_detectability/`,
  `prospective_validation/`, `ELEC3304/`, `PROJECT_STATE.md` and `paper/main_v2.pdf`. The public equivalents of the
  original study are `../manuscript/`, `../data/processed/` and `../results/`. The private originals (university course
  material and raw MAT recordings) remain unreleased, as stated in `../docs/DATA_AVAILABILITY.md`.
- **Time zone.** Times in the documents are local laboratory or record times as stated; the run logs use UTC.
