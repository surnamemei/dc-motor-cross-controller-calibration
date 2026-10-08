# External-data feasibility audit: eligibility report

**Purpose.** Decide whether two public DC-motor datasets can serve as external validation for the cross-controller
residual-monitor calibration study ("Cross-Controller Validity of Residual-Monitor Calibration in a PI-Controlled DC
Motor").
**Audit date:** 2026-10-08. **Scope:** evidence only.

No residual monitor was built and no threshold was calibrated. No false-alarm rate (FAR) or other detector statistic was
computed. Controllers were not selected, paired or ranked on any monitor outcome. The only signal-level computations are
integrity checks: sample counts, timing, non-finite values, saturation, divergence/motion, tracking at the end of a
step, and a replay of the logged command from the documented controller equation.

Nothing outside `external_validation/` was created or changed. That includes the frozen manuscript, the research
results, the ELEC3304 data, the public release and `prospective_validation/`.

| | Candidate A | Candidate B |
|---|---|---|
| Source | GitHub `DrLizarraga/Closed-Loop-Learning-Based-PID-Tuning-for-DC-Motor-Actuators` @ `8c74893a15c2` | Mendeley Data `10.17632/5xvg43r9r8.2` (v2), plus the v1 text files for provenance |
| Controlled variable | **position** (deg) | **speed** (RPM) |
| Decision | **SUITABLE WITH RESTRICTED CLAIMS** | **NOT SUITABLE** |

Machine-readable outputs:
- `manifests/run_manifest.csv`: one row per record, common schema, eligibility and role.
- `manifests/controller_summary.csv`
- `manifests/dataset_summary.json`
- `manifests/eligibility_decisions.json`
- the raw per-dataset inventories `manifests/candidate_A_runs.csv` and `manifests/candidate_B_runs.csv`

`SOURCES.md` records the retrieval and hashes.

---

## Candidate A: closed-loop learning-based PID tuning (Lizarraga et al.)

### 1. Inventory of real experimental runs
There are 2942 single-experiment MAT files (`E` struct), all from the physical rig according to `data/README.md`. All
2942 load, contain the embedded ACK and END lines, have 121 samples on an exact 25 ms grid, and contain no non-finite
values. There are also 81 CEM checkpoint files, `gen_XXX_state.mat` plus `adaptive_history.mat`. These are optimiser
state, not runs.

| Campaign folder | Runs | Dates | Content |
|---|---:|---|---|
| `data_experiments_L298N_A90` | 2160 | 2026-04-04, 05-23, 05-24 | CEM learning campaign, 90° step |
| `data_experiments_DC_L298N_A90` | 364 | 2026-06-01 | second CEM campaign; **every run fails** (below) |
| `validation_amplitudes_L298N` | 418 | 2026-06-13 | amplitude sweep (72 amplitudes, -1000° … +980°) with two fixed controllers |

### 2. Recovered signals
Each run records:
- gains: requested values and the values echoed by the firmware's ACK;
- reference `r` (deg) and measured position `y` (deg, 1336 CPR);
- controller command `u` (PWM counts, ±255);
- sample time 25 ms and time vector `t_ms`;
- experiment start timestamp (`E.meta.created_at`, 1 s resolution), serial port, raw serial lines, deadband 0.5°,
  encoder direction.

The firmware in the repository fully specifies the controller: Euler PID with conditional integration, rounding, a ±255
clamp, and an integrator/derivative reset inside the ±0.5° deadband. **A float32 replay of the firmware reproduces the
logged `u` exactly in all 2942 runs** (0 mismatching samples). One caveat: `u` is logged *before* the deadband policy,
so inside |e| < 0.5° the motor input is 0 while `u` may be non-zero. That applied input can be reconstructed exactly
from `r` and `y`.

### 3. Distinct controller configurations
There are 2448 distinct (Kp, Ki, Kd) triples, broken down by campaign:
- learning campaign: 2101 triples;
- DC campaign: 346 triples;
- validation sweep: 2 triples. K1 = (2.983711, 6.224762, 0.079279) and K2 = (4.99901, 8.003378, 0.156947). K2 is the
  learning-campaign best controller **K\***.

### 4. Genuine independent repetitions per controller
- **K\*: 57 runs** in the learning campaign, one per generation (gen 1–60, minus three), spread over 2026-04-04 (17),
  05-23 (17) and 05-24 (23). These are the only repeated runs under matched conditions that are spread over sessions.
- 2089 of the 2092 learning-campaign controllers with eligible runs have **exactly one run**.
- Two early controllers have 2–3 runs, all within one minute of each other on 2026-04-04.
- In the validation sweep, K1 and K2 have **3 consecutive back-to-back repeats per amplitude** (K2 has none at
  +30…+150°). These are short-interval repeats, not independent sessions.

### 5. Matched reference and sampling conditions
All learning-campaign runs share the same conditions: a 90° step at 0.5 s, Tf = 3 s, Ts = 25 ms, 1336 CPR, 0.5°
deadband, ±255 limits. That gives **2151 eligible runs in one matched group**: K\* with 57 runs and about 2090
single-run controllers.

Each validation amplitude forms its own matched group of 3 + 3 runs (K1/K2). There are few eligible cells:

| Controller | Eligible validation runs | Amplitude range |
|---|---:|---|
| K1 | 10 | -370° … 320° |
| K2 | 31 | -310° … 290° |

### 6. Flags
- **Failed control.** The whole `DC_L298N_A90` campaign (364 runs, path label `DC12V280RPM`) is a sign/positive-feedback
  runaway: `u` is held at +255 while `y` drifts to between -1141° and -2581° for a +90° step. These runs are excluded.
  Divergence (|y| > 1.5|A|) also occurs in 8 learning runs and 41 validation runs. 1 validation run shows no motion.
- **Saturation.** More than 10 % of post-step samples are at ±255 in 4 learning runs and 259 validation runs
  (mostly the large amplitudes).
- **Tracking.** The final |error| exceeds 2° in 753 learning runs. These are kept as `ELIGIBLE_WITH_NOTE`, because the
  CEM deliberately explores poor controllers.
- **Missing data.** None in the time series.
- **Chronology confounding.**
  - *Day effect.* K\*, with identical gains, reference and sampling, has a median overshoot of **16.5 % on 2026-04-04
    versus 37.7–38.6 % on 05-23/24**, and a median final error of 0.27° versus 1.9–3.0°. The rig changed between
    sessions.
  - *Protocol change.* Day 1 ran 8 candidates per generation (gen 1–20); the later days ran 50 per generation
    (gen 21–60).
  - *Adaptive sampling.* CEM sampling means controller identity is tied to time: gains drift with generation and
    cluster around K\* late in the campaign.
  - *Validation sweep.* All 216 K1 runs (16:15–16:42) came before all 202 K2 runs (17:20–17:41), and amplitudes were
    swept in monotone order. Controller and time are fully confounded there.
- **Rig identity.** The stored original paths of the validation sweep and the failed campaign are
  `…DC12V280RPM_L298N…`, while the README describes one JGB37-520 rig and the learning-campaign path carries no such
  label. Whether the validation sweep was run on the same motor is not documented.
- **Documentation inconsistencies.**
  - `amplitude_validation_summary.csv` (201 rows) contains only K2, and labels every row `divergence` or `no_settling`.
    The trajectories contradict that.
  - Neither `README.md` nor `data/README.md` mentions K1.
  - The README's DOI is a placeholder (see 9).

### 7. Can a fixed residual monitor be built without held-out controller data?
**Yes, conditionally.** There are no open-loop identification records, so a nominal model would have to be identified
from closed-loop data: for example from K\*'s runs, or from a designated calibration subset of controllers or sessions
fixed in advance. The plant input is exactly reconstructable (logged `u` plus the deadband rule), and the controller is
exactly known.

Constraints:
- the plant is an integrating position plant with deadband and saturation;
- each run is a single transient with 20 pre-step and 101 post-step samples, so sample-level statistics are dominated by
  one step response;
- the day effect means the calibration day must be fixed in advance, and transfer must be assessed within and across days
  separately;
- K\* was chosen by the authors' CEM tracking objective, not by any residual quantity, so it is not selected on FAR.

### 8. Speed or position
**Position control only** (y in degrees, step references). There are no speed-control records.

### 9. Licensing and provenance
- **Code licence.** `LICENSE` is MIT (copyright 2026, the nine authors). GitHub's licence detector reports `NOASSERTION`.
- **Data licence.** The README states the licence "applies only to the code and data files it contains", so the data
  are MIT-licensed by that statement. MIT is a software licence, so reuse terms for data are workable but not
  data-specific.
- **Paper.** "Closed-Loop Learning-Based PID Tuning for DC Motor Actuators Using Experimental Data", *Eng* 2026, 7(8),
  397, CC BY 4.0, published 2026-08-07, **DOI 10.3390/eng7080397** (Crossref; same authors). The README's DOI
  `10.3390/eng1010000` is a placeholder and does not resolve (HTTP 404).
- **Repository.** Created 2026-08-06, 2 commits, no releases. `data/README.md` itself warns that it was "not
  re-derived" which folder corresponds to the published campaign (Table 6: Ng = 60, Np = 8; but generations 21–60 hold
  50 runs each).

### Decision: **SUITABLE WITH RESTRICTED CLAIMS**
It can support a *conceptual* external replication of "calibration under one controller does not transfer uniformly
to other controllers" under these restrictions:
- **Position control only**: no claim about speed control or about our effort/joint channels as defined.
- **One matched group**: the learning campaign (A = 90°, Ts = 25 ms).
- **Calibration controller K\***: the only within-controller cross-run comparator. Its runs are interleaved one per
  generation, which allows stratification by day.
- **Comparison controllers are single runs, adaptively chosen** (CEM, not randomised) and concentrated near K\* later in
  the campaign. Cross-controller differences cannot be separated from run-to-run variation for any controller except
  K\*.
- **Day effects stratified, protocol change disclosed.** The day effect must be modelled or stratified; the change from
  8 to 50 runs per generation must be disclosed.
- **Excluded or secondary data.** The failed `DC_L298N_A90` campaign is excluded. The validation sweep is secondary:
  its rig identity is undocumented and controller and time are fully confounded.
- **Claim level.** Statements are about sample-level exceedance over single 3 s step transients, not alarm
  probabilities.

---

## Candidate B: OpenMCT end-to-end DC motor workflow (Von Chong & Cárdenas)

### 1. Inventory of real experimental runs
Version 2 contains **14 raw logs**:
- 1 current calibration;
- 1 static triangular sweep;
- 4 open-loop APRBS identification logs (2/10/20/50 ms);
- **4 continuous-PI speed validations** (5/10/20/50 ms);
- **3 discrete-controller speed validations** (20 ms);
- 1 open-loop chirp.

Version 1 (2026-05-11) contains 13 logs with the same names. **12 of them differ from v2** (re-acquired). Only the chirp
is byte-identical. In total there are 14 closed-loop speed runs: 7 in v2 and 7 in v1. All 161 v2 files match
Mendeley's SHA-256 values, and the 160 files listed in the dataset's own `SHA256SUMS.txt` all match.

### 2. Recovered signals
Each row holds REF (RPM), MEAS (RPM, **integer-valued**), DT_ms (constant nominal), current (raw and filtered), applied
PWM (0–255) and DMM current. Gains and coefficients come from the parameter CSVs and READMEs, not from the logs.
Timestamps are one start time per log (1 s resolution) plus the nominal per-row DT; there is no per-sample clock.

The firmware is archived (Teensy 4.0, `main.cpp`). A replay of the logged PWM from the documented equations is only
approximate:

| Run set | Median abs(ΔPWM) | Exact-match fraction | Max abs(ΔPWM) |
|---|---:|---:|---:|
| PI (v2) | 2–3 | 6–11 % | 10 |
| Discrete (v2) | 0–2 | 14–56 % | 36 |

The likely cause is that the firmware uses float speed while the log stores rounded speed. Speed resolution is one
encoder count: 12.5 / 6.25 / 3.125 / 1.25 RPM at 5 / 10 / 20 / 50 ms. The controller state is reset whenever the
reference is 0.

### 3. Distinct controller configurations
11 in total:
- v2 PI: 4, one per loop time; tuned on four different identified plants.
- v1 PI: 4. Different gains from v2, and implemented as positional PID (bilinear) rather than v2's incremental PI.
- Discrete: 3 (A: K = 3.86278; B: K = 13; C: integrator + zero at 0.66, K = 9.9). The coefficients are identical in v1
  and v2.

### 4. Genuine independent repetitions per controller
- **Within v2, every controller has one run.**
- Discrete A/B/C each have a second run in v1 (2026-05-05 vs 2026-09-03). Those pairs differ in protocol:

| | v1 | v2 |
|---|---|---|
| Reference phase | 2.5 s | 1.5 s |
| Reference levels | 42–231 | 80–240 |
| Duration | 48.6 s | 30 s |
| Firmware | state not archived | "revised" release |

  Also, v1 documents a 2000 ms reference period, which contradicts the 2.5 s phases observed in its own logs.
- No controller has two runs under matched protocol.

### 5. Matched reference and sampling conditions
- **Sampling.** Only the 20 ms runs share Ts: v2 PI_20ms (09-02) and v2 D_A/D_B/D_C (09-03, within 6 minutes), each
  with 1.5 s phases.
- **Reference levels are never matched.** Every run draws its own random sequence of active levels (seeded from
  `analogRead`).
- **PI controllers are fully confounded with sample time** and with the plant model used for tuning.

### 6. Flags
- **Saturation.** Negligible: v2 D_B reaches PWM 255 in 0.13 % of samples; nothing else.
- **Failed control.** None detected.
- **Missing data.** None in REF/MEAS/PWM. DMM columns are NaN where no DMM sample existed, which is expected.
- **Chronology.** v2 PI runs were on 09-02 (17:47–18:09, out of loop-time order) and discrete runs on 09-03. The v1
  runs were four months earlier, under a different firmware state.
- **Provenance timing.** The *Data in Brief* article (Aug 2026) and the *HardwareX* article (Jun 2026) predate the v2
  recordings (2026-09-02/03, published 2026-09-06). The peer-reviewed data article therefore describes v1, not the v2
  logs.

### 7. Can a fixed residual monitor be built without held-out controller data?
**Yes for the model.** The open-loop APRBS identification logs (and the dataset's 12 archived models) give a plant
model that uses no controller run.

**No meaningful calibration/validation split.** There is one run per controller under matched conditions. A threshold
calibrated on one controller's run cannot be compared with a same-controller cross-run baseline, which is the
comparator our study's central claim needs.

### 8. Speed or position
**Speed control.** Position mode exists in the firmware but is not recorded.

### 9. Licensing and provenance
- **Data licence.** CC BY 4.0 (`LICENSE`, Mendeley metadata).
- **Dataset DOI.** `10.17632/5xvg43r9r8.2` resolves to the dataset. Authors A. Von Chong and D. Cárdenas, Universidad
  Tecnológica de Panamá.
- **Related articles.** *HardwareX* `10.1016/j.ohx.2026.e00794` and *Data in Brief* `10.1016/j.dib.2026.113274`.
- **Firmware source.** GitHub `AlejoBSmith/DC_Motor`, commit `ebdb564`. It has no licence on GitHub; the archived
  snapshot is distributed inside the CC BY dataset.

### Decision: **NOT SUITABLE**
The dataset is well documented, licensed and integrity-checked, and it is the right physical domain (speed control).
It cannot support the external-validation claim:
- no controller has independent repeated runs under matched reference and sampling conditions, so there is no
  within-controller cross-run comparator;
- the PI controllers are confounded with sample time;
- the reference levels are randomised per run;
- the only cross-version repeats differ in protocol and firmware.

Possible non-confirmatory uses: checking that a nominal speed model identified from open-loop APRBS transfers to
closed-loop records, and a descriptive single-session illustration across the three 20 ms discrete controllers.
Neither tests the study's claims.

---

## 10. Confirmatory testing
No FAR or monitor test was run on either dataset, and no controller pairs were chosen. Any later confirmatory analysis
of Candidate A should be pre-specified before residuals are inspected:
- which records calibrate (for example K\* on one fixed day);
- which records validate;
- the model structure;
- the day stratification;
- the exclusion rules, which are already fixed in `manifests/run_manifest.csv`.
