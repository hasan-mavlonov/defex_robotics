# v0.2f checkpoint report for Hasan

Simulation only. No controller behaviour changed in v0.2f. Every reported run used the
frozen v0.2e controllers (ddd0d34). Two default-off options were added on `v0.2f/tilt`
and are not used by any run here. Each section names its results folder. POST HOC marks
anything decided after the results it explains were seen.

## Result

The brief's stop condition still holds: a fair baseline matches or beats C on most cells.
How to pitch is your decision. This round measured where C's remaining edge comes from
and found where C fails.

1. **C's success lead is concentrated** (POST HOC). On `standard`, C's wins over spiral +
   RCC + pull test (I) sit in three conditions with 1-2 mm camera error (noise_1mm,
   noise_2mm, generalization_combined): all of them on the gantry (60/60, 62/62, 53/53
   on the three seeds) and 49 of 51, 49 of 51 and 53 of 54 on the arm (the rest are
   generalization_tight). In nominal, noise_0mm and noise_0.5mm, C and I seat exactly the
   same trials on every seed and both machines. C loses arm friction_1 (nominal camera)
   on all three seeds.
   (`results/v0.2f_evidence`)
2. **C's zero bad units come from its VERIFY step and an assumed 3 deg spec.**
   - J, which is F's insertion plus C's VERIFY, passes 2-3 bad units per 7,400 good-part
     trials, against F's 176-197.
   - Rescored exactly (POST HOC, all three seeds, p per seed), at a 4 deg spec:
     - I's standard bad units fall to 13, 9, 8 (gantry; 48, 39, 32 at 3 deg) and to
       15, 10, 7 (arm; 43, 39, 32). C's stay at 0.
     - On the arm, C's lead over I loses significance on every seed: 27/21, 24/13,
       30/17 (p = 0.47, 0.099, 0.079).
     - On the gantry it holds on every seed: 28/5, 32/3, 31/10 (p <= 0.0015). It also
       holds at 5 deg (18/6, 26/4, 26/10).
   (`results/v0.2f_evidence/TOLERANCE.md`)
3. **A clean held-out test (heldout2, pre-registered, seed 20261207) is mixed.**
   - C is ahead in 5 of 10 cells: unseen socket tilt and yaw, and the arm tight-tolerance
     Micro-Fit. J matches C on tilt and yaw, so that lead likely comes mostly from VERIFY
     (POST HOC reading).
   - C is below the best fair baseline in 3 cells:
     - a plug offset in the fingers that nothing measures, on both machines (C 75-76%
       against F 95-99%);
     - F/T drift on the arm, where C passed 8 bad units (G passed the same 8; J 5).
       No benchmark since Checkpoint 2 had a C bad unit on a good part.
   (`results/heldout2_v0.2f`)
4. **Both heldout2 losses are traced (POST HOC), and both reproduce on development seeds.**
   - Under F/T drift, VERIFY's 1 N force-target preload lifts a seated plug, and nothing
     re-checks depth (traced in 6 of the 8 bad units; the depth and drift ranges cover
     all 8). So C's zero-bad-unit record relies partly on the simulator's
     constant, tared-out sensor bias.
   - Under an unseen grasp offset, an edge contact is relabelled as a jam, and C retries
     from the same probe.
   (`results/v0.2f_h2_diagnosis`)
5. **Simulator randomization on the current code (pre-registered, seed 20261205, 12
   variants plus nominal per machine):**
   - gantry: 29 of 29 primary comparisons hold;
   - arm: 24 of 29.
   - On the arm under MuJoCo's pyramidal friction cone (split POST HOC), C seats 1 of 90
     friction_1 parts against 89-90 for F, H and I. Traced POST HOC: in 85 of C's 89
     failures, a VERIFY wall-probe false reject.
     Floor friction stops the probe before the wall, and recovery repeats the same probe.
     (`results/v0.2f_friction_diagnosis`)
   - C's zero is not exact across simulators. On the arm C passed 1 latched plug at
     3.11 deg; on the gantry 1 seated plug that over-penetrated (a failed trial declared
     good, not a mis-seat). C still passed fewer than F, H and I in every variant.
   (`results/sim_randomization_v0.2f`)
6. **The rig test can now check the claim.**
   - The protocol and the BOM are fixed against the 35.2 N force budget. Several listed
     sensors and stages were under-rated, and the BOM listed the wrong Micro-Fit part.
   - A power analysis replaces the old 100-trials-per-condition guess. C vs I on the
     housing-only part needs 70-100 paired trials for 80% power. Micro-Fit good-part
     differences need 780 or more, so the protocol reports rates only for that part.
   - The simulation's predictions for the rig conditions are frozen, with the rule for
     judging a rig result (seed 20261201, 100 per condition).
   - A latch-model fitter exists. It fails its own synthetic rule on hook stiffness
     (6 of 10 parts against 8 required).
   (`hardware/`, `results/v0.2f_rig_predictions`, `results/v0.2f_latch_fit`)
7. **The tilt check is weaker than it looks** (POST HOC, development seeds):
   - It compares the plug with the axis C aimed it along, so it cannot see a socket-axis
     estimate error. G's 3.01 deg unit is this case.
   - The Micro-Fit cavity keeps such plugs near 3 deg.
   - The gantry housing-only VERIFY has no yaw check.
   (`results/v0.2f_tilt_diagnosis`)

8. **Real-time fit and pull test** (development measurements, `results/v0.2f_realtime`).
   - C's per-tick work fits a 2 ms loop on this laptop: median about 45 us, worst
     0.6-0.9 ms at low load (1.2-1.5 ms under heavy load). Misses came from Python garbage collection and preemption.
   - The gantry pull's force ringing is the simulator's undamped latch hook.
   - Fairness item against the baselines: C caps its retract pull on a latching part
     at 36 N, and D, F, H and I do not. H's retry retract tore 2 good latches on the
     development seeds.

## Results table

benchmark_v0.2e, seed 20261130 (unchanged; `results/v0.2f_evidence/CHECKPOINT_TABLE.md`):

| Ctrl | Seated, standard (gantry / arm) | p95 cycle, standard (s) | Good units/h, standard, 60 s per stop | Bad parts passed | Bad units, 7,400 good-part trials | Protective stops |
|---|---|---|---|---|---|---|
| C | 99.05% / 98.1% | 8.65 / 13.96 | 601 / 377 | 0 / 2,200 | 0 | 104 |
| I | 96.8% / 96.2% | 4.59 / 9.94 | 1,100 / 593 | 0 / 2,200 | 138 | 136 |
| F | 96.8% / 96.2% | 4.59 / 9.94 | 1,100 / 593 | 1,510 / 2,200 | 178 | 134 |
| H | 96.4% / 94.3% | 5.90 / 8.29 | 895 / 573 | 0 / 2,200 | 101 | 166 |
| J | 98.0% / 96.8% | 7.46 / 13.60 | 643 / 381 | 0 / 2,200 | 2 | 191 |
| G | 99.9% / 98.8% | 8.58 / 13.66 | 624 / 384 | 0 / 2,200 | 1 | 116 |

heldout2, seed 20261207, whole suite (`results/heldout2_v0.2f/HELDOUT2_TABLES.md`):

| Machine | C seated | Best fair | C-only / other-only | C bad units / H / I |
|---|---|---|---|---|
| gantry | 94.0% | F 83.2% | 63 / 20 (p = 2.4e-6) | 0 / 59 / 57 of 400 |
| arm | 88.8% | F 79.2% | 74 / 36 (p = 0.00037) | 8 / 52 / 63 of 400 |

Most of the pooled heldout2 lead comes from the unseen-yaw family.

## What got worse, or is weaker than the docs said

- The old "C led in all 13 simulators by 8-12 points" claim (v0.2a code, gantry only)
  is replaced. On the current code the arm has losses (item 5).
- The old `heldout` suite was used in W4 development, so it is not a clean held-out test.
  heldout2 is.
- "Did you tune C on the test? No." was too strong. The defense notes now give the
  honest answer (Q7).
- C's p95 cycle is still above 1.5 x median on every run but gantry latch_spread. The
  tail is retries, mostly in the high-camera-error trials (POST HOC); without retries the
  ratio is 1.04-1.19 (1.11 on gantry standard).
- C makes fewer good units per hour than F and I everywhere: 55% of F's on gantry
  standard, 65% on arm standard, 87-90% of I's on latching and latch_spread. VERIFY is
  about two-thirds of the gap on gantry standard (POST HOC phase split).

## Open questions for you

1. The pitch, given items 1-8.
2. Customer facts that decide the claim:
   - their camera's real position error at the insertion point;
   - their seating spec (angle, depth, and whether acceptance is by click, pull or
     angle);
   - whether their current cell already squares the part after seating;
   - whether their F/T sensor drifts over a cycle;
   - whether the gripper centres the plug.
3. Whether to start a C design round on the diagnosed failures:
   - a VERIFY depth hold and re-check;
   - a wall-probe stop on a wall signature, not a force level alone;
   - jam-branch progress after repeated same-probe attempts;
   - a socket-axis reference for the tilt check.
   Each would need its own pre-registration and fresh seed. None is implemented.
4. Whether a fair "seat-and-align" baseline should be built. No conventional baseline
   squares the part after seating today.
5. Whether to switch on either default-off tilt option. Each passed a no-harm rule on
   one validation seed (4007), is identical to v0.2e with the flag off, and changed no
   outcome.
6. Whether to keep committing `events.json.gz`. The brief asked to stop adding binaries;
   v0.2f mostly did not commit them.
7. The rig: which option, the budget, and the target connector. The BOM lists options;
   nothing is bought.

## Branches (local only; no push access)

All are in the bundle `defex_robotics_v0.2_branches_2026-11-02.bundle`.

- `v0.2f/integration`: everything below merged on top of `v0.2e/integration` (4df8cae).
  Fast tests pass.
- Its parts:
  - `v0.2f/pack` (evidence, logging columns);
  - `v0.2f/hw` (protocol, BOM, power, rig predictions);
  - `v0.2f/latchfit`;
  - `v0.2f/simrand`;
  - `v0.2f/heldout2` (suite code, harness only);
  - `v0.2f/h2-diagnosis`;
  - `v0.2f/friction-diagnosis`;
  - `v0.2f/tilt` (default-off options);
  - `v0.2f/docs` (README, technical brief, defense notes);
  - `v0.2f/realtime` (controller tick timing, pull overshoot).
- Merging `v0.2f/integration` alone brings in all of v0.2f. The earlier chain (`v0.2/*`
  through `v0.2e/*`) is unchanged.
