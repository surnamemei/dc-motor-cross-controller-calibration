# Third candidate: eligibility audit of Zenodo record 21201595 (ET-RLS-STR STM32 benchmark)

**Audit date:** 2026-10-08.
**Method:** the archive was downloaded and every run log was opened. The findings below rest on the files, the
acquisition harness and the archive metadata, not on the record's description. No residual monitor was built, and no
threshold or false-alarm rate was computed.

**Decision: RESTRICTED.**

**Machine-readable outputs:**
- `manifests/candidate_C_runs.csv`: all 459 run logs, with integrity metrics.
- `manifests/candidate_C_units.csv`: the 384 benchmark runs, with eligibility, acquisition block and recovered file time.
- `raw/candidate_C_zenodo/_v1_v2_run_comparison.json` and `_v2_run_mtimes.csv`.
- `tools/inventory_candidate_C.py`.

## Provenance

| Item | Finding |
|---|---|
| Record | 10.5281/zenodo.21201595, version 1.0.0, published 2026-07-05; concept DOI 10.5281/zenodo.21201594 |
| Newer version | **v2.0.0, record 21389722, 2026-07-16**, re-titled "… + MIG: Measurement-Integrity-Gated …" |
| Creators | Thanh Trang Tran (HCMC University of Industry and Trade), Nhut Tam Tran (HCMUT, VNU-HCM) |
| Type / licence | Zenodo resource type "Software"; MIT (`LICENSE`: "Copyright (c) 2026 Tam Nhut Tran and contributors"), covering code and data alike |
| File | `etrls-str-stm32-v1.0.zip`, 20 079 919 B; MD5 `5854bc25…` matches Zenodo; SHA-256 `2df790e4…af6` |
| Companion paper | Referred to as "available from the journal" but not identified; Crossref finds no matching publication |
| Rig | STM32F407, BTS7960 H-bridge, JGA25-370 12 V gearmotor, 5 ms loop (README) |
| Withheld data | `hardware/README.md`: earlier pilot campaigns are "local-only", excluded from the package, and "superseded" after being found glitch-contaminated. The released campaign followed this outcome-informed curation. |

**v1 versus v2.** All 399 run logs common to both versions differ byte-for-byte, but only in line endings: v2 uses
CRLF, and all are identical after CRLF→LF normalisation. The measured data are unchanged.

v1's ZIP stamps every file with one packaging time (2026-07-05 16:42:54). v2's ZIP preserves distinct per-file
modification times, which is the only available source of per-run chronology. These are filesystem metadata, not
authenticated timestamps. They agree with the harness's 24 s run plus 2 s rest cadence (median inter-file gap 26 s).

## Inventory (v1 archive)

459 run logs, all with the 6 columns `time, setpoint, feedback, output, pos, speed` and no non-numeric cells:

| Group | Runs | Content |
|---|---:|---|
| `data/<ARM>/S1–S4` | 6 arms × 4 scenarios × 11 = 264 | S1 nominal step, S2 load (emulated), S3 reference staircase, S4 supply sag (emulated) |
| `data/<ARM>/S5` | 6 × 20 = 120 | measurement glitches (emulated), dedicated session of 2026-07-04 |
| `S5_pilot_n10_20260702` | 60 | earlier S5 session of 2026-07-02 |
| `misseed` | 15 | STR started from deliberately wrong seeds |

The arms are ZN, PT, GS and PSO (fixed PI), plus STR (adaptive) and RL (learned PI tuner).

## The six requested properties, checked in the files

1. **Timestamped real output measurements: PARTIAL.**
   - Present per sample: relative `time` on an exact 5 ms grid (S1–S4: 0 off-grid steps; 4799–4800 rows = 24 s),
     `feedback` (speed in RPM), `speed` and `pos`.
   - No absolute timestamp exists inside any file.
   - Run chronology is available only through the v2 file times (S1/S3: 2026-07-01, 13:49–14:56).
   - S1–S4 contain no non-physical rows; all 15 486 non-physical rows are in S5, where the glitches are intended.
   - Every run starts from rest, with `feedback = speed = pos = 0` at t = 0.
   - The `feedback` signal the controller uses is heavily filtered (EMA α = 0.05, per the firmware notes).
   - Logged resolution is 0.1 RPM.
2. **Logged control inputs: PARTIAL.**
   - `output` is the controller's voltage command `control_output` (V), logged at **0.1 V resolution**. That is about 2 %
     of the operating range (max ≈ 5.1–5.7 V in S1).
   - The PWM-duty conversion is not archived, and there is no actuator voltage or current measurement.
3. **Reference trajectories: PARTIAL.**
   - `setpoint` logs the commanded target: S1 is 500 → 600 RPM at 8 s; S3 is 300 → 500 → 700 → 400 RPM at 6/12/18 s.
     In 17 of 66 runs the step falls one sample later (8.010 s rather than 8.005 s).
   - The controller actually tracks an internal **`ramped_setpoint` that is not logged**. Its ramp law is in firmware
     that is not archived; the simulation assumes a 1.5 s ramp.
4. **Fixed controller identities: PARTIAL.**
   - Four fixed PI arms are defined in the harness (`run_all_hw.py`): ZN (Kp 0.0089, Ki 0.0280), PT (0.0393, 0.8491),
     GS (0.1000, 0.0010) and PSO (0.0073, 0.0388), all with Kd = 0.
   - The logs carry **no gain echo**.
   - The PI implementation is **not archived**. It is Simulink-generated code with an "anti-windup clamp as before"
     inside a Keil project, `Vidu/ES_Exam4_PID`; only the STR and RL modules are included. The control law therefore
     cannot be replayed or verified.
   - STR and RL have time-varying gains, so they are not fixed identities.
5. **Genuine repeated experiments: YES, within one session.**
   - Each arm has 11 runs per nominal scenario.
   - Recovered order for S1 and S3:
     - one interleaved pass with run01 of all six arms (13:49–13:54);
     - then **per-arm blocks of 10 consecutive runs** (run02–run11) in the fixed order ZN → PT → GS → PSO → STR → RL,
       first for S1 and then for S3.
   - Each run re-sends STOP / MODE / PID with the gains, starts from rest, and is followed by a 2 s rest.
   - Whether controller state is reset cannot be verified, because the firmware is missing.
6. **Matched operating conditions: YES within S1 and within S3** (same profile, same session, same rig). There are none
   across scenarios. S2, S4 and S5 apply emulated disturbances; S5 and its pilot are separate sessions.

## Can a fixed residual monitor be built without held-out controller data?
**Possibly, with restrictions.**
- A speed model can be identified from the `output` → `speed`/`feedback` relation of one designated fixed-PI arm's
  calibration runs and applied to other arms, so no implementation knowledge of the target controllers is needed.
- The harness's "offline" plant seed (K = 116.89, τ = 0.1095 s) could serve as a model fitted on no controller run.
  However, its identification records are not archived.
- An effort/command residual cannot be validated, because the PI law is unknown and the command is quantised at 0.1 V.

## Exact eligible sample units

| Eligibility | Runs | Definition |
|---|---:|---|
| **ELIGIBLE** | **88** | arms ZN, PT, GS, PSO × scenarios S1, S3 × runs 01–11. Each run is 24 s (≈ 4800 samples at 5 ms). Per arm and scenario: 1 interleaved-pass run (run01) and 10 block runs (run02–11). |
| RESTRICTED | 44 | STR and RL in S1/S3. The controller adapts, so there is no fixed identity; usable only as descriptive targets. |
| EXCLUDED | 252 | S2, S4, S5 (emulated disturbances/glitches) |
| Not used | 75 | S5 pilot (60) and misseed (15) |

The file list, hashes and recovered times are in `manifests/candidate_C_units.csv`.

## Unavoidable confounders

1. **Arm × time confounding.** Apart from the single interleaved run01 pass, each arm's runs form one contiguous
   block in a fixed order (3.9 min between the block's first and last file write). Arm differences cannot be separated from drift within the session (temperature,
   supply).
2. **One session, one day, one rig.** There is no between-session replication of S1/S3.
3. **Controller implementation not archived,** and gains are not echoed per run, so controller identity rests on harness
   constants.
4. **Effective reference not logged** (internal setpoint ramp).
5. **Coarse logging:** 0.1 V command and 0.1 RPM speed; the controller feedback is heavily filtered.
6. **Outcome-informed curation:** earlier pilot sessions were withheld after inspection.
7. **Chronology from unauthenticated file metadata** (v2 only).
8. **No identified companion publication.**

## Decision: **RESTRICTED**
Every requested property is present at least partially in the files. The dataset has genuine within-session repeats of
four fixed-PI speed controllers under matched references, which is more than Candidates A and B offer for speed
control.

It is not GO, because:
- controller identity and the control law cannot be verified (firmware missing, no gain echo);
- the true reference is unlogged;
- arm and time are confounded.

It is not KILL, because the measured output, the command, the target reference and the repetitions do exist and are
internally consistent. That holds across 132 nominal runs, two archive versions and the recovered 26 s cadence.

**If used:**
- **Scope:** fixed-PI arms in S1 and S3 only, per scenario.
- **Calibration and holdout:** source-arm calibration and holdout taken chronologically within the source arm's block.
- **Targets:** the time-adjacent ones only, meaning the run01 interleaved pass and the neighbouring block boundaries.
- **Pre-registration:** a frozen protocol like `FROZEN_PROTOCOL_DRAFT.md`, written before any residual is computed.
- **Claims:** no causal arm effect, and no command or voltage residual claim.
