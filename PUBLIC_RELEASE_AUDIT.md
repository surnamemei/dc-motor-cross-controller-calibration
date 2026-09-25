# Public release audit

**Decision: READY FOR PUBLIC GITHUB WITH DATA LIMITATION.** This refers to the curated contents of this directory only. No Git repository was initialized and nothing was pushed. The parent/private research repository and its history must not be published. The research manuscript and numerical methods remain frozen.

## SAFE TO PUBLISH

- Research-authored public statistical script, seven tests, configuration record, manuscript Version 3 with only figure-path and data-availability additions, README, and reproducibility/data notes.
- Ten compact processed CSVs containing controller/run descriptors, aggregate exceedance counts, subset–target FAR summaries, simulation summary counts, reciprocal score statistics, FAR-target ablation counts, and archived interval endpoints. Their per-file derivation, source class, and manuscript mapping are in `data/README.md`. They contain no waveform, sampled speed, sampled command, or per-sample residual sequence.
- Seven research-authored final figures. Figures 2–4 and 6–7 regenerate from public data. Figure 1 is a schematic. Figure 5 is a static ECDF; its score sequences are excluded and this limit is explicit.
- The public script and tests read only paths under this tree. From a standalone copy outside the private repository, isolated Python reproduced 14.07% C04→C01 effort FAR, 1.29/1.39/1.38% same-controller maxima, 5.20/3.31/3.26× calibration-error contrasts, 45.86% and 3.76% balanced diversity effort extrema, and the C07 simulation illustration. Seven tests passed. The main run took 2.39 seconds in the audit environment.

## EXCLUDED FROM RELEASE

- All original experimental MAT files, university/lecturer teaching materials, MATLAB/Simulink files, templates, firmware/build artifacts, unrelated coursework, and the private repository's `.git` history.
- Original acquisition pipeline, Lab 2 identification inputs, individual speed/command/residual waveforms, score sequences, cycle-bootstrap resampling draws, and calibration-diversity selection draws. The public pipeline can aggregate their frozen derived summaries but cannot independently reconstruct them.
- Machine-specific environments, local absolute paths, private usernames, and original course filenames. The only reference to excluded file types in the public code is the test's forbidden-extension list.

## REQUIRES RIGHTS CLARIFICATION

- Redistribution of the original MAT files and university/course materials remains unestablished. They stay excluded; the release does not need them for Level A statistical reproduction.
- No reuse license was selected. `LICENSE` is an explicit no-license placeholder; select a license for original code and separately decide terms for data/manuscript/figures if reuse permission is desired. It does not cover excluded material. Finalize author names in `CITATION.cff` before treating it as publication metadata.
- Figure 5's derived static plot is included as research-authored expression, while its underlying score data remain excluded. If the project owner has any contractual restriction on derived aggregate plots or statistics, withhold that item and update the data statement before release.

## Checks performed

- A recursive check found **no `.git` directory inside the curated tree**. Its future public repository must begin with fresh history.
- A recursive file-extension check found no `.mat`, `.slx`, `.m`, `.bin`, `.elf`, or `.hex` payload.
- Text scans found no course directory names, original MAT filenames, private absolute Windows/Linux paths, usernames, or common API-key/private-key signatures; the forbidden-extension strings in the test are intentional.
- All seven manuscript figure links resolve within the curated tree. Principal generated figures were visually checked for labelled axes and legibility.
- The public pipeline and seven tests passed from a standalone temporary copy with isolated Python import paths. Fixed seed 33043 is recorded; Level A performs no random draw, and tests compare repeated output bytes.

## Data limitation

**Level A public statistical reproduction** is available. **Level B full raw-data reproduction** is not: original experimental files and teaching materials are withheld because redistribution rights are unknown. The archived 13.34–14.71% cycle-bootstrap interval and Figure 5 ECDF are traceable in the public release, but their raw-score generation is outside Level A. Do not describe this package as a public raw-data replication.
