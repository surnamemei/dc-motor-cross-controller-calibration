# Research status (archival closure, October 2026)

**Status:** archived pilot study, with a separate record of later external-data assessments. No further analysis of the
archival data is planned. The manuscript, processed data and results in this repository are frozen.

## 1. Original findings (pilot study; unchanged)

The pilot covers one physical DC motor, 11 nominal-operation runs, 9 PI configurations and 85 complete 4 s cycles, at a
nominal 1 % sample-exceedance target.
- **Transfer is not uniform.** A calibration made under one PI configuration does not transfer uniformly to the others.
  - The maximum effort-residual FAR among 32 eligible controller-distinct transfers was **14.07 %** (C04 → C01).
  - The worst-case speed FAR was 2.58 %, and the worst-case joint FAR 4.24 %.
- **Same-controller runs stay close to target.** The maxima across runs of the same controller were 1.29 % (speed),
  1.39 % (effort) and 1.38 % (joint).
- **Across-controller error is larger.** The median absolute calibration error was 5.20× (speed), 3.31× (effort) and
  3.26× (joint) larger across controllers than across repeated runs.
- **Diverse calibration helps.** Controller-diverse calibration reduced several archive-specific unseen-controller
  extremes.
- **Simulation only.** A model-level simulation found a robustness–sensitivity trade-off. It is not physical-fault
  evidence.

**Limitations, as stated in the manuscript:**
- one motor;
- only C01 and C04 have independent repeated runs;
- controller and session are partly confounded;
- FAR means sample-level score exceedance, not an alarm probability;
- positive-severity sensitivity is simulated;
- the raw recordings are not public.

## 2. External findings (after the pilot; see [EXTERNAL_VALIDATION.md](EXTERNAL_VALIDATION.md))
- **Dataset A (Lizarraga, position PID; one usable session):**
  - target-controller FAR 0.74 %, against 0.17 % for the source controller's own held-out runs;
  - paired difference **+0.57 pp [0.00, 1.81]** over 6 generation pairs, with every sensitivity interval including 0.
- **Dataset C (STM32, speed PI; one session, fixed block order):**
  - same-controller held-out FAR 0.79–1.18 %;
  - in the six predefined comparisons, target FAR 0.59–1.89 % and differences **−0.27 to +1.03 pp**;
  - two intervals exclude zero, in opposite directions;
  - descriptive cells outside the predefined set reach 6.9 %.
- **Dataset B (OpenMCT):** not suitable, because it has no repeated runs per controller under matched conditions.

## 3. What was and was not replicated

| Statement | External outcome |
|---|---|
| Same-controller calibration roughly holds for later runs of the same controller | **Consistent**: all three platforms near or below 1 % |
| Transfer to other controllers is not uniform | **Consistent in direction only**: STM32 differences vary in sign and size by pair |
| Large controller-transfer failures (effort channel, 14.07 %) | **Not replicated, and not testable**: no external effort or voltage residual exists |
| Across-controller error several times the across-run error | **Not replicated**: external differences were similar in size to time effects or indistinguishable from zero |
| Pooled / leave-one-controller-out benefit; simulated trade-off | **Not tested externally** |

The predictor architectures differ:
- the pilot uses a controller-dependent closed-loop simulation residual;
- both external monitors use one-step-ahead input–output predictors.

The external results therefore bound a different monitor class. They are **not** a multi-platform replication, and a
non-significant external difference is not evidence of equivalence.

## 4. Experimental confounding (unresolved)
- **Pilot:** controller and session partly confounded; archival data, not prospective.
- **Dataset A:** target controllers were chosen by an optimizer, each run once, always after the source controller,
  and with different transients; one session.
- **Dataset C:** controller fully confounded with time (fixed block order, one block per controller, one session).
  The internal reference is unlogged and the PI law is not archived.
- **Common to all three:** one rig each, effectively one session each, and no randomised controller assignment.
  **No causal claim about controller gains is supported.**

## 5. Publication status
- **Preprint.** The PDF is in [`../manuscript/paper.pdf`](../manuscript/paper.pdf) (Version 3, unchanged). It has not
  been submitted to a journal and has not been peer-reviewed or accepted.
- **Identifiers.** No DOI, arXiv identifier or journal identifier exists for the paper or this repository.
  `ZENODO_METADATA.md` is a preparation note only.
- **Manuscript.** The external assessments are not part of the manuscript, which has not been edited to include them.

## 6. Requirements for future hardware validation

A confirmatory test of the pilot's claims would need:
1. the **same monitor class** as the pilot: a closed-loop simulation residual with speed, effort and joint channels,
   on a speed loop;
2. **an independent effort measurement**, or an explicit restriction to the commanded-voltage channel;
3. **randomised controller order** across several sessions, with each controller repeated in every session, so that
   controller and session or time can be separated;
4. a **pre-registered** protocol: fixed calibration and holdout splits, threshold rule, exclusions, unit of resampling
   (runs or cycles) and, ideally, a held-out final session;
5. matched references and sampling, and logged reference, command, measured output and timestamps for every run;
6. enough runs per controller and session for run-level and session-level uncertainty, not only sample-level.

A prospective acquisition package with this design (four controllers, three randomised sessions, the third held out)
was prepared outside this repository. It has not been run on hardware, and its hardware-specific Simulink models are not
published here.
