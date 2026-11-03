# v0.2f checkpoint report for Hasan

Simulation only. No controller behaviour changed in v0.2f: every reported run used the
frozen v0.2e controllers (ddd0d34). The brief's stop condition still holds, so the pitch
is your decision. This report does not pick it.

## Words used here

- **C**: the adaptive controller (the product). **G**: C plus a learned contact prior.
- **Fair baselines**: D (force-controlled spiral search), E (vision correction on a
  passive RCC compliance stage), F (spiral on the RCC), and H and I (D and F plus C's
  retention pull test). I is the strongest.
- **J**: F's insertion followed by C's VERIFY (C's post-seat checks). Not a fair
  baseline. It shows what C's VERIFY alone buys.
- **Bad unit**: a good part that ends out of tolerance (short, offset, or more than
  3 deg off in tilt or yaw) but is declared seated. **Bad part**: a deliberately
  defective part (half latched, broken latch, stubbed pin, wrong polarity).
- **Cell**: one machine (gantry or UR5e arm) and one suite. **C-only / I-only**: paired
  trials that only C seats, and only I seats.
- **Pre-registered**: rules and seed committed before the run. **POST HOC**: an analysis
  chosen after seeing the results; it explains, it does not count as a test.

## Scorecard

Seated good parts, C against the best fair baseline. Pre-registered unless marked.

| Where | C | Best fair | Verdict | Other seeds |
|---|---|---|---|---|
| standard (housing-only part), gantry | 99.1% | F/I 96.8% | **C ahead** (p < 1e-6) | same on 3 of 3 seeds |
| standard, arm | 98.1% | F/I 96.2% | **C ahead** (p = 5.9e-6) | same on 3 of 3 |
| latching Micro-Fit good parts, gantry | 97.5% | F 98.8% | matches (p = 0.12) | C below F on both earlier seeds |
| latching good parts, arm | 92.0% | F 95.2% | **C below F** (p = 0.014) | matches on both earlier seeds |
| old `heldout` (camera worse than told), gantry | 81.4% | 83.8% | matches | C ahead on one earlier seed (p = 0.044) |
| old `heldout`, arm | 76.8% | 78.4% | matches | matches |
| latch_spread (parts varied within the datasheet), gantry / arm | 100% / 99.5% | 100% / 99.8% | matches | matches |
| heldout2: unseen socket tilt, gantry / arm | 100% / 100% | E 92.5% / 85.0% | **C ahead** | one seed only |
| heldout2: unseen socket yaw, gantry / arm | 100% / 97.5% | 37.5% / 37.5% | **C ahead** | one seed only |
| heldout2: tight-tolerance Micro-Fit, gantry / arm | 95.0% / 93.8% | F 88.8% / 80.0% | matches / **C ahead** | one seed only |
| heldout2: F/T drift, gantry / arm | 100% / 76.2% | D 100% / 100% | matches / **C below D** | one seed only |
| heldout2: plug offset in the fingers, gantry / arm | 75.0% / 76.2% | F 98.8% / 95.0% | **C below F** | one seed only |

Sources:
- the first seven rows: `results/benchmark_v0.2e/HEADLINE_TABLES.md` (a), seed
  20261130, with the earlier seeds 20261123 and 20261124 in `docs/TECHNICAL_BRIEF.md`
  section 1;
- the heldout2 rows: `results/heldout2_v0.2f/HELDOUT2_TABLES.md` (a), seed 20261207,
  40 trials per condition.

The other numbers that decide the pitch:

| | C | I | F | J |
|---|---|---|---|---|
| Bad parts passed, of 2,200 (v0.2e) | 0 | 0 | 1,510 | 0 |
| Bad units, of 7,400 good-part trials (three seeds) | 0 / 0 / 0 | 161 / 138 / 138 | 197 / 176 / 178 | 3 / 2 / 2 |
| Bad units, heldout2 (gantry / arm, of 400 each) | 0 / 8 | 57 / 63 | | 0 / 5 |
| Good units per hour, standard (gantry / arm, v0.2e) | 601 / 387 | 1,100 / 593 | 1,100 / 593 | 643 / 381 |
| Good units per hour, latching (gantry / arm, v0.2e) | 449 / 280 | 498 / 320 | 861 / 495 | 498 / 322 |

Sources:
- `results/v0.2f_evidence/BAD_UNITS.md`;
- `results/heldout2_v0.2f/HELDOUT2_TABLES.md` (b) and (c);
- `results/benchmark_v0.2e/HEADLINE_TABLES.md` (c), at 0 s per protective stop.

I's and H's bad units, in the benchmarks and in heldout2's tilt and yaw families, are
mostly plugs at about full depth, just past the assumed 3 deg limit (item 2 below).

**C or J?** J is a conventional spiral + RCC insertion with C's VERIFY bolted on.
- It matches C's protection against bad units almost exactly (2-3 against 0 per 7,400),
  at about C's cycle time.
- Its success against C is mixed:
  - J is below C on standard on both machines (gantry 98.0% against 99.1%, arm 96.8%
    against 98.1%).
  - J is ahead of C on arm latching (95.3% against 92.0%) and on gantry `heldout`.
  - On heldout2, J is ahead on the gantry whole suite (97.2% against 94.0%, p = 0.019),
    mostly in the plug-offset family (98.8% against 75.0%). On the arm it matches C.

Read POST HOC, most of C's edge over the fair baselines is its VERIFY step, not its
search. These runs do not decide whether the product is C, or a check sold on top of a
conventional cell.

## What lies under the scorecard

1. **The standard lead is concentrated** (POST HOC, `results/v0.2f_evidence`).
   - Almost all of C's wins over I sit in three conditions with 1-2 mm camera error:
     noise_1mm, noise_2mm and generalization_combined.
     - Gantry: all of C's wins on each seed (60, 62 and 53).
     - Arm: 49 of 51, 49 of 51 and 53 of 54.
   - In nominal, noise_0mm and noise_0.5mm, C and I seat exactly the same trials.
   - More than half of those wins are trials where I declared a bad unit. On seed
     20261130 that is 30 of 53 (gantry) and 30 of 54 (arm).
   - C loses arm friction_1 (nominal camera) on all three seeds.
2. **The bad-unit gap depends on the seating spec** (POST HOC, exact replays of all three
   benchmark seeds, `results/v0.2f_evidence/TOLERANCE.md` (4)-(5); p per seed, not pooled).
   - I's standard bad units at 3 / 4 / 5 deg: gantry 48/13/2, 39/9/2, 32/8/3; arm
     43/15/4, 39/10/4, 32/7/3 (seeds 20261123, 20261124, 20261130). C passes none at
     2.5-5 deg, except 1 on the arm at 2.5 deg on one seed.
   - Gantry standard: C's lead over I holds at 4 deg on every seed (C-only / I-only
     28/5, 32/3, 31/10) and at 5 deg (18/6, 26/4, 26/10; p = 0.023, 5.9e-5, 0.011).
   - Arm standard: the lead is still significant at 3.5 deg, but not at 4 deg on any
     seed (27/21, 24/13, 30/17; p = 0.47, 0.099, 0.079).
   - At 2 deg the lead widens on every seed (gantry 113/0, 114/1, 122/2), and C then
     passes 0-3 bad units.
   - Old `heldout` at 5 deg: I has more discordant wins than C on both machines and all
     seeds.
   - The v0.2d-code replays reproduce 12,400 of 12,800 rows exactly; the other 400 (I and
     J, arm generalization_combined) differ only in final-digit drift that the v0.2d
     pre-registration disclosed, with identical outcomes.
3. **C's zero bad units rests partly on the simulator.**
   - Under F/T drift (heldout2, arm), VERIFY's 1 N force-target preload lifts a seated
     plug, and nothing re-checks depth (`results/v0.2f_h2_diagnosis`).
     - It was traced POST HOC in 6 of the 8 bad units; the depth and drift ranges cover
       all 8.
     - G passed the same 8, and J passed 5.
   - Everywhere else the simulated sensor bias is constant and tared out. A real sensor
     drifts.
4. **Where C fails, and why** (POST HOC traces; each reproduces on the development seeds).
   - **Plug offset in the fingers.** An edge contact is relabelled as a jam, and C retries
     from the same probe. F's spiral passes over the offset
     (`results/v0.2f_h2_diagnosis`).
   - **Arm friction 1.0.** VERIFY's wall probe stops on floor friction before it reaches
     the wall, so C rejects a seated plug (`results/v0.2f_friction_diagnosis`).
     - Under MuJoCo's pyramidal friction cone this decides the arm friction_1 result:
       C seats 1 of 90, against 89-90 for F, H and I.
     - MuJoCo's documentation calls the elliptic cone, the nominal setting, the closer
       model.
   - **The tilt check.** It compares the plug with the axis C aimed it along, so it
     cannot see an error in C's socket-axis estimate (`results/v0.2f_tilt_diagnosis`).
     - G's 3.01 deg bad unit is this case.
     - The Micro-Fit cavity keeps such plugs near 3 deg.
     - The gantry housing-only VERIFY has no yaw check.
5. **Across simulators** (pre-registered, seed 20261205, 12 randomized contact and servo
   models plus the nominal one per machine, `results/sim_randomization_v0.2f`).
   - Gantry: every primary comparison keeps its benchmark direction in at least 10 of
     the 12 models (29 of 29).
   - Arm: 24 of 29.
     - C's high-camera-error lead keeps its direction in exactly 10 of 12, the minimum.
       Pooled, it is not significant.
     - The friction_1 loss above appears.
     - "C below F" on arm latching keeps its direction in 9 of 12 (pooled still C
       below F, p = 0.038).
   - C's bad units are not exactly zero across simulators (1 per machine), but they are
     fewer than F's, H's and I's in every model.
6. **Throughput.** C makes fewer good units per hour than F and I everywhere.
   - On standard: 55% of F's on the gantry and 65% on the arm.
   - On latching: 87-90% of I's.
   - On gantry standard, about two-thirds of the gap is VERIFY's 1.89 s (POST HOC phase
     split).
   - C's p95 cycle is above 1.5 x its median almost everywhere, and the tail is retries.
7. **Rig readiness** (`hardware/`, `results/v0.2f_rig_predictions`,
   `results/v0.2f_latch_fit`, `results/v0.2f_realtime`).
   - The protocol and the BOM are fixed against the 35.2 N force budget. Several listed
     sensors and stages were under-rated, and the BOM named the wrong Micro-Fit part.
   - Power analysis:
     - C vs I on the housing-only part needs 70-100 paired trials for 80% power.
     - Micro-Fit good-part differences need 780 or more, so the rig reports rates only
       for that part.
   - The simulation's predictions for the rig conditions are frozen (seed 20261201, 100
     per condition), with the rule for judging a rig result.
   - The latch fitter fails its own synthetic rule on hook stiffness (6 of 10 parts
     against 8 required).
   - C's per-tick work fits a 2 ms loop on this laptop: worst 0.6-0.9 ms at low load,
     and 1.2-1.5 ms under heavy load.
8. **Fairness items, both ways.**
   - **Against C:** no fair baseline re-zeroes the F/T sensor during contact, or squares
     the part after seating. A conventional "seat-and-align" step might close much of
     C's tilt, yaw and bad-unit edge.
   - **Against the baselines:** C caps its retract pull on a latching part at 36 N, and
     D, F, H and I do not. H's retry retract tore 2 good latches on the development
     seeds.

## What the docs said before, and what changed

- "C led in all 13 simulators by 8-12 points" (v0.2a code, gantry only) is replaced by
  item 5.
- The old `heldout` suite was used in W4 development, so it is not a clean held-out
  test. heldout2 is.
- "Did you tune C on the test? No." was too strong. Defense notes Q7 now gives the
  honest answer.

## Open questions for you

1. The pitch: C, J (VERIFY on a conventional cell), or something else.
2. Customer facts that decide it:
   - their camera's real error at the insertion point;
   - their seating spec: angle and depth, and acceptance by click, pull or angle;
   - whether their cell already squares the part after seating;
   - whether their F/T sensor drifts over a cycle;
   - whether their gripper centres the plug.
3. Whether to start a C design round on the four diagnosed failures:
   - a VERIFY depth hold and re-check;
   - a wall-probe stop on a wall signature, not on force alone;
   - jam-branch progress after repeated same-probe attempts;
   - a socket-axis reference for the tilt check.
   Each needs its own pre-registration and fresh seed. None is implemented.
4. Whether to build a fair seat-and-align baseline, and give D, F, H and I C's retract
   cap.
5. Whether to switch on either default-off tilt option. Each passed a no-harm rule on
   validation seed 4007, gives rows identical to v0.2e with the flag off, and changed no
   outcome.
6. Whether to keep committing `events.json.gz`. The brief asked to stop adding binaries.
7. The rig: which option, what budget, which target connector. Nothing is bought.

## Branches (local only; no push access)

All are in the bundle `defex_robotics_v0.2_branches_2026-11-02.bundle`.

- **`v0.2f/integration`** holds all of v0.2f on top of `v0.2e/integration` (4df8cae).
  - It fast-forwards `main`.
  - Fast tests pass in a fresh clone.
  - The final docs and this report live only there.
- Its parts:
  - `v0.2f/pack`, `v0.2f/hw`, `v0.2f/latchfit`, `v0.2f/simrand`;
  - `v0.2f/heldout2`, `v0.2f/h2-diagnosis`, `v0.2f/friction-diagnosis`;
  - `v0.2f/tilt` (default-off options), `v0.2f/docs`, `v0.2f/realtime`.
- The earlier chain (`v0.2/*` through `v0.2e/*`) is unchanged, and
  `results/benchmark_v0.1` is untouched.
