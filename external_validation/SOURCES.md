# Sources and retrieval (2026-10-08)

This folder is separate from the frozen study. Nothing under `paper/`, `research_motor_detectability/`, `ELEC3304/`,
`public_release/` or `prospective_validation/` was modified.

## Candidate A
- Retrieved: `git clone https://github.com/DrLizarraga/Closed-Loop-Learning-Based-PID-Tuning-for-DC-Motor-Actuators`
  into `raw/candidate_A_github/` (unmodified working tree).
- Commit: `8c74893a15c2c110e880d41eabd0d648bd2dcc93` (2026-08-06, 2 commits in total).
- Repository created 2026-08-06; licence file MIT; GitHub licence field `NOASSERTION`.
- Publication: *Eng* 2026, 7(8), 397, DOI `10.3390/eng7080397` (CC BY 4.0). The DOI cited in the README,
  `10.3390/eng1010000`, returns HTTP 404.
- Per-file SHA-256 of the 2942 experiment files: `manifests/candidate_A_runs.csv`.

## Candidate B
- Retrieved with `tools/fetch_mendeley.py 5xvg43r9r8 2 raw/candidate_B_mendeley`, which uses the Mendeley public API
  and verifies every file against the SHA-256 it reports: 161/161 match.
- The dataset's own `SHA256SUMS.txt` also verifies: 160/160.
- Metadata: `raw/candidate_B_mendeley/_mendeley_metadata.json` and `_mendeley_files.json`.
- DOI `10.17632/5xvg43r9r8.2` (v2, published 2026-09-06; v1 published 2026-05-11); licence CC BY 4.0.
- Version 1: the text files only (raw logs, READMEs, CSVs; hash-verified against Mendeley) are in
  `raw/candidate_B_mendeley_v1/`. They are used only to check repetitions and provenance.
- Related articles: *HardwareX* `10.1016/j.ohx.2026.e00794` (2026-06), *Data in Brief* `10.1016/j.dib.2026.113274`
  (2026-08).
- Firmware source: `https://github.com/AlejoBSmith/DC_Motor` (no GitHub licence), archived snapshot inside the dataset.

## Reproducing the manifests
```bash
python3 tools/inventory_candidate_A.py
python3 tools/inventory_candidate_B.py
python3 tools/build_manifest.py
```
They use only `numpy`, `pandas` and `scipy`, and compute integrity metrics only, with no monitor or false-alarm
statistics.

## Candidate C (added 2026-10-08)
- Zenodo record 21201595 (v1.0.0, DOI `10.5281/zenodo.21201595`), retrieved with the Zenodo REST API.
  Archive `raw/candidate_C_zenodo/etrls-str-stm32-v1.0.zip` (MD5 matches Zenodo); extracted unmodified to
  `raw/candidate_C_zenodo/extracted/`.
- Newer version v2.0.0 (record 21389722): its archive is kept only to compare run-log contents (identical data,
  line endings differ) and to read per-file modification times.
- Reproduce with `python3 tools/inventory_candidate_C.py`.

## Protocol artefacts (Candidate A)
- `tools/kstar_verification.py`, `tools/protocol_split.py` and `tools/fit_arx_calibration.py`, writing to `protocol/`.
  They use metadata plus the calibration-only ARX fit. No residual or threshold is computed on any holdout or target run.
