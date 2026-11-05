# v0.2f checkpoint report for Hasan

Simulation only. No controller behaviour changed in v0.2f. Every v0.2f benchmark-type run
(heldout2, simulator randomization, rig predictions, the seed-20261130 replay) used the frozen
v0.2e controllers (ddd0d34). The exact replays of seeds 20261123 and 20261124 in item 2 used
those benchmarks' own v0.2d code (42df5c8) plus logging only. Two development runs also
exercised new default-off code with its flag on: the tilt options' seed-4007 check and the
baseline retract cap. The brief's stop condition still holds, so the pitch
is your decision. This report does not pick it.

## Words used here

- **C**: the adaptive controller (the product). **G**: C plus a learned contact prior.
- **Fair baselines**: D (force-controlled spiral search), E (vision correction on a
  passive RCC compliance stage), F (spiral on the RCC), and H and I (D and F plus C's
  retention pull test). F and I seat about equally; I also rejects bad parts.
- **J**: F's insertion followed by C's VERIFY (C's post-seat checks). Not a fair
  baseline. It shows what C's VERIFY alone buys.
- **Bad unit**: a good part that is declared seated but is not: short, offset, more
  than 3 deg off in tilt or yaw, not settled, or (latching parts) not latched. **Bad part**: a deliberately
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
| Bad units, heldout2 (gantry / arm, of 400 each) | 0 / 8 | 57 / 63 | 57 / 63 | 0 / 5 |
| Good units per hour, standard (gantry / arm, v0.2e) | 601 / 387 | 1,100 / 593 | 1,100 / 593 | 643 / 381 |
| Good units per hour, latching (gantry / arm, v0.2e) | 449 / 280 | 498 / 320 | 861 / 495 | 498 / 322 |

Sources:
- `results/v0.2f_evidence/BAD_UNITS.md`;
- `results/heldout2_v0.2f/HELDOUT2_TABLES.md` (b) and (c);
- `results/benchmark_v0.2e/HEADLINE_TABLES.md` (c), at 0 s per protective stop.

Good units per hour count good-part trials only. On the same latching suites F also
passes 518 of 800 (gantry) and 468 of 800 (arm) deliberately bad parts as good.

I's and H's bad units in the benchmarks are mostly plugs at about full depth, just past
the assumed 3 deg limit (item 2 below). In heldout2's 4 deg unseen-yaw condition they sit
further out (medians 3.77-3.99 deg, up to 4.87 deg; POST HOC, from trials.csv).

**C or J?** J is a conventional spiral + RCC insertion with C's VERIFY bolted on.
- On the benchmarks it nearly matches C's protection against bad units (2-3 against 0
  per 7,400), at about C's cycle time. Not everywhere:
  - across simulators on the arm J passed 30 of 2,210 against C's 1, all 30 under the
    pyramidal cone (`results/sim_randomization_v0.2f`; that report's rule also counts one
    over-penetrated J plug, giving 31);
  - on heldout2 arm it passed 5 against C's 8.
- Its success against C is mixed:
  - J is below C on standard on both machines (gantry 98.0% against 99.1%, arm 96.8%
    against 98.1%).
  - On gantry `heldout`, J's rate is above C's on all three seeds, but the difference is
    significant on one (J-only / C-only 71/34, p = 0.00039, seed 20261130; 46/37, p = 0.38
    and 47/31, p = 0.089 on 20261123 and 20261124).
  - J is ahead of C on gantry latching on seed 20261124 (592 against 579 of 600, 18/5,
    p = 0.011), and on arm latching on seed 20261130 (95.3% against 92.0%). It is level
    with C in those cells on the other seeds.
  - On heldout2, J is ahead on the gantry whole suite (97.2% against 94.0%, p = 0.019),
    mostly in the plug-offset family (98.8% against 75.0%). On the arm whole suite it
    matches C, but it is ahead on plug offset (96.2% against 76.2%) and below on the
    tight-tolerance Micro-Fit (80.0% against 93.8%).

Read POST HOC (`results/v0.2f_evidence/CONCENTRATION.md` (d)):
- most of C's bad-unit edge, and its heldout2 tilt and yaw edge, is its VERIFY step;
- on standard success, VERIFY accounts for about half of C's gantry lead over F (net trials
  35 of 58, 30 of 59 and 23 of 45 on seeds 20261123, 20261124 and 20261130) and half or
  less of its arm lead (17 of 34, 12 of 40, 11 of 38). The rest is C's own insertion.

These runs do not decide whether the product is C, or a check sold on top of a
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
     passes 0-3 bad units on standard. On latching good parts C does not hold zero under a
     tighter spec: it passes 10-21 bad units at 2 deg and 0-8 at 2.5 deg (I: 20-48 and 4-11).
   - Old `heldout` at 5 deg: I has more discordant wins than C on both machines and all
     seeds.
   - The v0.2d-code replays reproduce 12,400 of 12,800 rows exactly; the other 400 (I and
     J, arm generalization_combined) differ by up to 0.022 mm or deg in final pose and up
     to 8 ms in cycle time. That drift is the v0.2d code's disclosed limit, and the
     outcomes are identical.
3. **C's zero bad units rests partly on the simulator.**
   - Under F/T drift (heldout2, arm), VERIFY's 1 N force-target preload lifts a seated
     plug, and nothing re-checks depth (`results/v0.2f_h2_diagnosis`).
     - It was traced POST HOC in 4 of the 8 heldout2 bad units (arm trials 4, 12, 19 and
       28) and in 2 development-seed trials; the depth and drift ranges cover all 8.
     - G passed the same 8, and J passed 5.
   - Everywhere else the simulated sensor bias is constant and tared out. A real sensor
     drifts.
4. **Where C fails, and why** (POST HOC traces; each mechanism reproduces on the
   development seeds).
   - **Plug offset in the fingers.** An edge contact is relabelled as a jam, and C retries
     from the same probe. F's spiral passes over the offset
     (`results/v0.2f_h2_diagnosis`).
   - **Arm friction 1.0** (`results/v0.2f_friction_diagnosis`).
     - On the nominal (elliptic-cone) benchmarks, C's 18 friction_1 losses over three
       seeds are 11 torque protective stops just over the 0.6 N m limit, 5 wall-probe
       stalls, 1 time-limit failure after a correct wall-yaw reject (true yaw 3.95 deg) and
       1 mouth stall.
     - In a wall-probe stall, the probe stops on floor friction before it reaches the
       wall, so C rejects a seated plug.
     - Under MuJoCo's pyramidal cone the stall decides the result: C seats 1 of 90,
       against 89-90 for F, H and I (cone split POST HOC).
     - MuJoCo's documentation calls the elliptic cone, the nominal setting, the closer
       model (quotes in `results/v0.2f_friction_diagnosis`). The simulator-randomization
       report, written before that reading, treats the two cones as equally plausible.
   - **The tilt check.** It compares the plug with the axis C aimed it along, so it
     cannot see an error in C's socket-axis estimate (`results/v0.2f_tilt_diagnosis`).
     - G's 3.01 deg bad unit is this case.
     - The Micro-Fit cavity keeps such plugs near 3 deg. On the development seeds the
       under-read shows (234 of 8,320 verdicts read more than 1 deg low), but no bad unit
       does.
     - The gantry housing-only VERIFY has no yaw check.
5. **Across simulators** (pre-registered, seed 20261205, 12 randomized contact and servo
   models plus the nominal one per machine, `results/sim_randomization_v0.2f`).
   - Gantry: every primary comparison keeps its benchmark direction in at least 10 of
     the 12 models (29 of 29).
   - Arm: 24 of 29.
     - C's high-camera-error lead keeps its direction in exactly 10 of 12 against F and I,
       the minimum (12 of 12 against H). Pooled, it is not significant.
     - The friction_1 loss above appears (cone split POST HOC).
     - "C below F" on arm latching keeps its direction in 9 of 12 (pooled still C
       below F, p = 0.038).
   - C's bad units are not exactly zero across simulators: 1 on the arm (a latched plug at
     3.11 deg). On the gantry C declared 1 seated plug good that had over-penetrated: a
     failed trial, but not a bad unit by the definition above. The simulator-randomization
     report's own rule counts it as one, so that report gives 1 per machine. C still passed fewer than
     F, H and I in every model.
6. **Throughput.** In every benchmark cell, C makes fewer good units per hour than F and
   I. On heldout2 it makes more than both in the unseen-yaw family (gantry 714 against
   490). In tight tolerance it makes more than I but fewer than F (gantry 416 against 570,
   arm 279 against 301).
   - On standard: 55% of F's on the gantry and 65% on the arm.
   - On latching and latch_spread: 87.0-90.2% of I's.
   - On gantry standard, about two-thirds of the gap is VERIFY's 1.89 s (POST HOC phase
     split).
   - C's p95 cycle is above 1.5 x its median almost everywhere, and the tail is retries.
7. **Rig readiness** (`hardware/`, `results/v0.2f_rig_predictions`,
   `results/v0.2f_latch_fit`, `results/v0.2f_realtime`).
   - The protocol and the BOM are fixed against the 35.2 N force budget. Several listed
     sensors and stages were under-rated, and the BOM named the wrong Micro-Fit part.
   - Power analysis:
     - C vs I on the rig's four housing-only conditions needs 70-100 paired trials for
       80% power. The full standard suite would need 350 (gantry) and 810 (arm).
     - Micro-Fit good-part differences need 780 or more, so the rig reports rates only
       for that part.
   - The simulation's predictions for the rig conditions are frozen (seed 20261201, 100
     per condition), with the rule for judging a rig result.
   - The latch fitter fails its own synthetic rule on hook stiffness (6 of 10 parts
     against 8 required).
   - Development measurement on this laptop: C's own per-tick work fits a 2 ms loop.
     - Its worst replayed tick is 0.62-0.64 ms at low load and 1.21-1.28 ms under heavy
       load (G's: 0.81-0.89 and up to 1.50 ms).
     - In the loop, ticks over 2 ms still occur from Python garbage collection and
       preemption: C had 29 at low load and 1,341 under heavy load.
8. **Fairness items, both ways.**
   - **Against C:** no fair baseline re-zeroes the F/T sensor during contact, or squares
     the part after seating. A conventional "seat-and-align" step might close much of
     C's tilt, yaw and bad-unit edge.
   - **Against the baselines:** C caps its retract pull on a latching part at 36 N, and
     D, F, H and I do not. D's and H's retry retracts each tore 2 good latches on the
     development seeds (POST HOC observation). A port of C's cap to D, F, H and I was tried under a
     committed rule and dropped by it: at the baselines' 40 mm/s retract it moved a tear
     rather than preventing one (`results/v0.2f_baseline_retract_cap`). The item stays
     open; a slower baseline retract would need your approval.

## What the docs said before, and what changed

- "C led in all 13 simulators by 8.3-12.5 points" (v0.2a code, gantry only) is replaced by
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
4. Whether to build a fair seat-and-align baseline, and give D, F, H and I a gentle
   retract (the direct port of C's cap failed its rule; see item 8).
5. Whether to switch on either default-off tilt option. Each passed a no-harm rule on
   validation seed 4007, gives rows identical to v0.2e with the flag off, and changed no
   outcome. (The v0.2e side of that identity check ran from a git archive of 4df8cae, so its
   config.json records no commit; `results/v0.2f_tilt_diagnosis/run.sh` shows how.)
6. Whether to keep committing `events.json.gz`. The brief asked to stop adding binaries.
7. The rig: which option, what budget, which target connector. Nothing is bought.

## Branches

All 45 v0.2 branches are on GitHub (pushed 2026-11-05). PR #2 merges `v0.2f/integration` into
`main`.

- **`v0.2f/integration`** holds all of v0.2f on top of `v0.2e/integration` (4df8cae).
  - It fast-forwards `main`.
  - Fast tests pass in a fresh clone.
  - The final docs and this report live only there.
- Its parts:
  - `v0.2f/pack`, `v0.2f/hw`, `v0.2f/latchfit`, `v0.2f/simrand`;
  - `v0.2f/heldout2`, `v0.2f/h2-diagnosis`, `v0.2f/friction-diagnosis`;
  - `v0.2f/tilt` (default-off options), `v0.2f/docs`, `v0.2f/realtime`,
    `v0.2f/tolerance-3seeds`, `v0.2f/baseline-retract-cap` (inert, default off).
- `v0.2f/replay-v02d` is in the bundle as the record of how the v0.2d-code replays
  were made. Do not merge it: it is built on the v0.2d code.
- The earlier chain (`v0.2/*` through `v0.2e/*`) is unchanged, and
  `results/benchmark_v0.1` is untouched.
