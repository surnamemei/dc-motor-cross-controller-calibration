# Cross-platform assessment: three real DC-motor platforms

**Date:** 2026-10-08.
**Scope:** compares the frozen manuscript results (original USYD rig) with the two pre-registered external analyses.
Nothing in the manuscript or the frozen results was changed.

**Sources:**

| Platform | Source |
|---|---|
| USYD | `PROJECT_STATE.md`, `reviewer/CLAIMS_INDEX.md`, `research_motor_detectability/methods/MONITOR_DEFINITION.md` |
| Lizarraga | `results_A/RESULTS_A.md` |
| STM32 | `STM32_RESULTS.md` |

## 1. The platforms and analyses side by side

| | USYD original (frozen manuscript) | Lizarraga (results A) | STM32 (results C) |
|---|---|---|---|
| Controlled variable | speed [rad/s] | **position** [deg] | speed [RPM] |
| Rig / loop | Teensy 4.1, 200 Hz | ESP32-S3 + L298N, 40 Hz (25 ms) | STM32F407 + BTS7960, 200 Hz (5 ms) |
| Controllers | 9 PI configurations (11 runs; only C01 and C04 repeated) | K\* (source) and 42 single-run, optimizer-chosen PID targets | 4 fixed PI arms in a fixed chronological chain |
| Sessions used | archival lab runs (controller and session partly confounded) | 1 (2026-04-04; the other two days STOP) | 1 (2026-07-01) |
| **Residual class** | **closed-loop free-run simulation:** reference → replayed PI → identified plant (M2) → predicted speed and command | **one-step-ahead ARX(2,2,1)** on measured position and applied command | **one-step-ahead ARX(2,2,1)+c** on measured filtered speed and logged command |
| Channels | speed, effort (Vm), joint | position only | speed only |
| Threshold | 99th percentile (`higher`), 1 % target | same | same |
| Uncertainty unit | 4 s cycles | 6 generation pairs | runs within one block (n = 1 block per controller) |
| Same-controller held-out FAR | max **1.29 %** (speed), 1.39 % (effort), 1.38 % (joint) | **0.17 %** (K\*, 6 runs) | **0.79–1.18 %** (8 controller × scenario cells) |
| Controller-distinct FAR | worst **2.58 %** speed, **14.07 %** effort, 4.24 % joint | **0.74 %** mean over 42 targets | **0.59–1.89 %** in the 6 predefined comparisons (descriptive cells up to 6.86 %) |
| Difference from same-controller baseline | across-controller calibration error 5.20× / 3.31× / 3.26× the across-run error (median absolute) | D = +0.57 pp [0.00, 1.81] | D = −0.27 to +1.03 pp; 2 of 6 intervals exclude 0, in opposite directions |

## 2. Replicated findings (in direction, with the stated limits)

1. **Same-controller recalibration stays near the nominal rate.**
   - On every platform, a threshold calibrated on one controller's runs gave held-out runs of the *same* controller
     FARs close to or below the 1 % target: USYD at most 1.29 %, STM32 0.79–1.18 %, Lizarraga 0.17 %.
   - This is the most consistent cross-platform finding.
2. **Transfer to other controllers is not uniform.**
   - On STM32 the differences from the same-controller baseline vary in sign and size across predefined pairs (−0.27 to
     +1.03 pp). One pair exceeds the baseline with an interval excluding 0 (S3 PT→GS, +0.30 pp), and target FARs reach
     1.89 %.
   - On Lizarraga the targets exceed the source holdout slightly in 5 of 6 generations.
   - This reproduces the manuscript's qualitative statement that a single-controller calibration "does not transfer
     uniformly".
   - It does **not** reproduce its magnitudes (see §3).

## 3. Findings not replicated

1. **No large cross-controller inflation of a speed-type residual.**
   - The USYD worst-case controller-distinct speed FAR (2.58 %) was not exceeded in any predefined external comparison
     (Lizarraga 0.74 %, STM32 at most 1.89 %).
   - Four of the six STM32 comparisons go the *opposite* way (targets alarm less than the source holdout).
2. **No consistent excess of across-controller over across-run error.**
   - USYD's across-controller calibration error is 3.3–5.2 times its across-run error.
   - Externally, with the protocols' metrics, cross-controller differences were similar in size to same-controller
     time-separation effects (STM32: largest |Δ_time| 0.73 pp against |D| ≤ 1.03 pp), or statistically
     indistinguishable from zero (Lizarraga).
3. **Not replicated, and not refuted:**
   - **the effort-channel result** (14.07 %) and the joint-channel result;
   - **pooled / leave-one-controller-out calibration** (1.85–2.72 %; 45.86 % → 3.76 %);
   - **the FR13 robustness–sensitivity trade-off.**

   None was tested externally: no external platform has an independent effort or voltage residual, and no pooled-source
   analysis was pre-registered.

Statistical non-significance in any external comparison is **not evidence of equivalence**. The external intervals are
compatible with differences of up to about 1.8 pp (Lizarraga) and 1.3 pp (STM32, the largest upper bound among the
predefined comparisons).

## 4. Incomparable metrics

1. **Residual class, which is the main incomparability.**
   - The USYD residuals compare measurements with a **closed-loop simulation driven by the reference through the replayed
     controller**, so the prediction itself depends on the controller.
   - Both external monitors are **one-step-ahead input–output predictors** fed by the measured output and the logged
     command. That largely removes the controller from the prediction path.
   - Transfer failures should therefore be expected to be smaller for the external monitors whatever happens to the
     plant. The external results bound how a *controller-agnostic predictor* transfers; they do not test the manuscript's
     monitor.
2. **Controlled variable and timescale:**
   - USYD: speed, with 4 s reference cycles;
   - Lizarraga: position, a single 3 s step transient with 101 post-step samples;
   - STM32: an EMA-filtered speed, with 24 s steps and staircases.
3. **Effort and joint channels.** They have no external counterpart.
   - Lizarraga's command is a PWM count fully determined by the firmware.
   - STM32's command is quantised to 0.1 V, under a control law that is not archived.
   - No platform measures terminal voltage.
4. **Quantisation regime.**
   - The STM32 thresholds (2.87–3.09 RPM) sit at about one encoder count's contribution to the filtered speed
     (3.11 RPM), so its exceedances partly measure count-arrival timing.
   - The Lizarraga threshold is about 19 counts.
   - The USYD residual scale is set by model mismatch.
   - Exceedance rates of 1–2 % mean different things in these regimes.
5. **Uncertainty units** are not interchangeable: cycles (USYD), generation pairs (Lizarraga) and runs within one
   controller block (STM32). Interval widths are not comparable across platforms.
6. **Target populations.**
   - USYD: hand-designed PI configurations spanning bandwidths.
   - Lizarraga: optimizer-chosen PID near the source.
   - STM32: four fixed tunings, one of which (GS) holds a large steady-state offset.

## 5. Unresolved confounding

| Platform | Confounding that remains |
|---|---|
| USYD | Controller and session partly confounded (only C01 and C04 repeated); archival rather than prospective; one motor |
| Lizarraga | Targets chosen by the optimizer, run once each and always after K\*, with different transient envelopes; K\*'s winner's-curse origin; one session usable (the other two STOP: model acceptance failure; two sessions in one day stratum) |
| STM32 | Controller fully confounded with block and time (fixed order ZN → PT → GS → PSO, one block per controller, one session); internal reference ramp unlogged; PI law not archived; speed-level-dependent quantisation; earlier sessions withheld by the authors |
| All three | One rig and effectively one session each; no randomised controller assignment; no between-session replication of the cross-controller contrast |

The largest descriptive transfer values on STM32 (4.4–6.9 % for ZN- and PSO-calibrated models on GS in S1) lie
**outside** the predefined comparisons. They are reported as descriptive and are not counted as replication. They
coincide with the arm that operates at a different speed level, which could equally be a quantisation or operating-point
effect.

## 6. Overall assessment
- **Supported across platforms:**
  - a single-controller threshold is approximately valid for later runs of the same controller;
  - its transfer to other controllers varies by pair.
- **Not supported by the external data (and not contradicted, because the metrics differ):**
  - large controller-transfer failures of the kind reported for the effort channel;
  - an across-controller calibration error that is several times the across-run error.
- **No platform supports causal statements about controller gains.**
- The remaining confounds are the same structural gap noted in the manuscript's limitations. The prospective package
  (`prospective_validation/`) addresses that gap for the original rig by acquiring randomised, multi-session,
  matched-condition runs, to which the original closed-loop residual definition can then be applied under a
  pre-registered analysis. It, not further archival datasets, is the route to a confirmatory replication.
- The journal manuscript has not been edited. Any mention of these external results would need a separate, reviewed
  change limited to the statements in §§2–5.
