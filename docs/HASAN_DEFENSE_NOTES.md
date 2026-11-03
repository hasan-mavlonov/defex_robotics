# Hard questions, with answers (draft for Hasan)

Short answers you can give yourself, each with the file that backs it. Simulation only.

Sources, unless an answer says otherwise:
- benchmark_v0.2e: seed 20261130, code ddd0d34, `results/benchmark_v0.2e/REPORT.md`.
- "Three seeds" adds benchmark_v0.2d (20261123) and benchmark_v0.2d_rep (20261124),
  both on the v0.2d code (42df5c8). Each seed is reported on its own; no p-value is
  pooled across seeds.
- The per-condition and tolerance analysis is in `results/v0.2f_evidence/REPORT.txt`.
- heldout2: seed 20261207, the same ddd0d34 controllers,
  `results/heldout2_v0.2f/REPORT.txt`.

POST HOC marks anything chosen after the results were seen.

**In one paragraph (benchmark_v0.2e).**
- C is ahead of every fair baseline (D, E, F, H, I) on `standard` on both machines. It
  is ahead there on all three seeds.
- A fair baseline matches C on 5 cells.
- C is below F on arm latching good parts (92.0% against 95.2%, p = 0.014).
- C, G, H, I and J pass 0 of 2,200 deliberately bad parts.
- On 7,400 good-part trials, unseated plugs passed as good: C 0, G 1, J 2, H 101,
  I 138.
- C makes fewer good units per hour than F and I on every cell.

heldout2, a new held-out test: C is ahead in 5 of 10 machine-family cells, matched in 2
and below in 3. There C passed 8 bad units, all on the arm under F/T drift. They are its
first in a reported run since Checkpoint 2 (benchmark_v0.2b). The stop condition holds; the pitch is your call.

## 1. "How does it compare with spiral search?"

Mixed.
- **Standard suite.** C seats more on both machines (gantry 99.1% against F/I 96.8%,
  arm 98.1% against 96.2%), on all three seeds.
- **Where that lead sits (POST HOC).** The lead is in the camera-error conditions:
  noise_1mm, noise_2mm and generalization_combined hold 53 of C's 53 wins on the
  gantry and 53 of 54 on the arm (seed 20261130). In nominal, noise_0mm and noise_0.5mm
  (camera sigma 0.3, 0 and 0.5 mm), C and I seat exactly the same trials on every
  seed. More than half of
  C's wins (30 of 53, 30 of 54) are plugs that I passed out of tolerance.
- **Other suites.** On latching, heldout and latch_spread, a spiral cell with a pull
  test (I) or without one (F) matches or beats C. F seats more arm latching good parts
  (95.2% against 92.0%, p = 0.014).
- **Bad parts and bad units.** Both C and I pass 0 of 2,200 bad parts. C passed no
  out-of-tolerance plug in 7,400 good-part trials; I passed 138.
- **heldout2.** C is well ahead on unseen receptacle yaw (100% against 37.5% on the
  gantry). It is below F on an unseen grasp offset (gantry 75.0% against 98.8%).

Files: `results/benchmark_v0.2e/REPORT.md`, `results/v0.2f_evidence/CONCENTRATION.md`,
`PERCOND.md`, `results/heldout2_v0.2f/REPORT.txt`.

## 2. "So why not just use spiral search?"

In simulation the spiral cell is faster. F and I make more good units per hour than C
on every cell. On gantry standard that is 1,100 against 601, and on arm standard 593
against 387 (`results/benchmark_v0.2e/HEADLINE_TABLES.md` (c)).
- About two-thirds of C's extra time on gantry standard is VERIFY: 1.89 s of 2.94 s
  (POST HOC, `results/v0.2f_evidence/PHASES.md`).
- What C buys is fewer out-of-tolerance housing-only plugs leaving the cell, in the
  high-camera-error trials.
- J (F's insertion plus C's VERIFY) gets most of that: 2 bad units against F's 178.
  J makes 643 good units per hour on gantry standard.
- Whether the trade pays depends on what a mis-seated connector costs the customer,
  which is not priced. It also depends on whether the customer's spec is as tight as
  the assumed 3 deg (question 11).

## 3. "Why should I trust MuJoCo contact?"

You should not trust absolute numbers.
- The contact model is pinned by tests against stated physics
  (`tests/test_mating_physics.py`).
- <!-- PENDING: sim_randomization_v0.2f -->
- The only randomized-simulator run so far (`results/sim_randomization_v0.2/REPORT.md`)
  used the v0.2a code (frozen at fe48eca). That was before the baselines were re-tuned,
  before the latching parts and the arm, and before H, I and J. Do not cite it for the
  current code.
- One known way the simulator flatters C: its F/T bias is constant and tared out. Under
  drift, C's VERIFY can lift a seated plug (question 9).
- The real answer is a rig. Measured success will be compared with frozen predictions
  on the same trial list, with intervals (`hardware/TEST_PROTOCOL.md`).

## 4. "What happens with a stubbed pin, or a part at the edge of the datasheet?"

**Stubbed pin.** C passed 0 of 400 stubbed-terminal parts, and so did I. F passed 259
and D 117. The plug stops short and the pull test moves it. C's median cycle on a bad
part is 8.9 s on the gantry and 13.0 s on the arm (`results/benchmark_v0.2e/TABLES.md`,
latching).

**Edge of the datasheet.** Every controller pushes to 35.2 N (1.1 x the 32 N maximum
mating force). At maximum terminal friction (`mf_terminal_max`), C seated 100 and 99
of 100. I seated 100 and 100, and H 99 and 100. D and F, with the same push but no
pull, seated 89 and 74-95, and passed 5-26 unseated plugs as good
(`results/benchmark_v0.2e/TABLES.md`, latch_spread). The old latch_spread lead in
benchmark_v0.2c came from a push setting, not the method. It went away once every cell
got the same push and H and I got a re-push. The spread itself is assumed.

## 5. "Why not learning?"

We tried a learned piece where it can help without hardware data: G, a small network
that predicts where the hole is from a blocked contact.
- In benchmark_v0.2e, G beats C on 6 of 8 cells (for example arm standard, 98.8%
  against 98.1%, p = 0.0044). It shows no gain on latch_spread.
- G passed one bad unit (question 9).
- On heldout2, G gave no measurable gain in any cell. Its gains come from the same
  camera-error conditions as C's lead.
- End-to-end learned policies need real force traces, which we do not have.

## 6. "What is the cycle time on a real line?"

Unknown.
- In simulation, the median good cycle on the standard suite is 5.30 s on the gantry
  and 8.15 s on the arm. F's is 2.43 s and 4.77 s.
- C's VERIFY costs 1.89 s and 2.49 s per housing-only success. The pull test costs I
  3.04 s and 3.93 s on a latching part, the same as C's latch check (POST HOC,
  `results/v0.2f_evidence/PHASES.md`).
- C's p95 is 1.63 x its median on gantry standard, against a 1.5 target. The slow tail
  is retries.
- The simulated UR5e lags 0.2 s, which may be more than a real one. The rig measures it.

## 7. "Did you tune C on the test?"

Not on a reported seed. Every benchmark was pre-registered with a fresh seed, frozen
code and decision rules written before the first trial. But the method was refined
between benchmarks, and the honest answer has to say how:

- **Each benchmark prompted the next fix.** Checkpoint 2 (v0.2b) led to the v0.2c
  fixes. v0.2c led to the 35.2 N push and the H and I re-push. The v0.2d review led to
  the three v0.2e fixes. Each fix was then tested on a new seed. But the frozen v0.2e
  code was written after the results of benchmark_v0.2a-v0.2d and the replication had
  been read.
- **The baselines' retry was designed with sight of C and of the results.** The v0.2d
  H and I re-push copies C's proof push. Its version 5 fixes problems that the review
  of the v0.2d results found (`results/v0.2e_pull_retry/REPORT.md`).
- **`heldout` is no longer held out.** It was used in W4 development
  (`results/w4_development/REPORT.md`, lines 7-10). The `latch_spread` suite was added
  after development showed C ahead there.
- **The per-condition and tolerance analyses are POST HOC.** They explain the
  verdicts; they do not replace them.

What heldout2 adds: five families that no one had developed against, fixed before any
trial of them ran, and one fresh seed (20261207). The expectation ("matches in most
cells") was pre-registered, and it was wrong. C was ahead in 5 of 10 cells and below in
3, and it passed 8 bad units. heldout2 is now used once. Any development against those
families makes them in-sample too.

The rules force us to publish losses. C below F on arm latching and C below a fair
baseline in 3 heldout2 cells are in the README.

## 8. "Does C cheat by knowing things a real cell would not?"

It gets what an integrator knows in advance: the connector drawing and datasheet, the
programmed socket pose, the fixture limits, the camera's characterized accuracy, and
the fixture's wrist stiffness and servo lag. It never sees the true socket pose or
contact state. A test fails the build if controller code imports the simulator or
ground truth (`tests/test_motion_and_estimation.py::test_controller_code_cannot_reach_the_simulator`).

Being told the camera's accuracy cuts both ways. C sizes its search from that figure.
- When the camera is worse than told (`heldout`), F and I match C on both machines in
  benchmark_v0.2e (gantry 81.4% against 83.8%, arm 76.8% against 78.4%).
- With a 1.5 mm hand-eye bias, I seats more than C on all three seeds.
- On heldout2's unseen grasp offset, C was not told the offset and fell below F. A
  POST HOC trace found that the cause is C's in-hand estimate. With the true grasp
  given to C, 5 of 5 replays seat (`results/v0.2f_h2_diagnosis/REPORT.txt`).

C's latch check uses datasheet values only: a pull at 1.1 x the 32 N maximum mating
force and a movement limit of 0.6 x the 1.75 mm terminal wipe.

## 9. "Has C ever passed a bad part?"

- **Deliberately bad parts:** none, on any of the three seeds (0 of 2,200 each). H, I
  and J pass none either.
- **Good parts passed out of tolerance:**
  - **benchmark_v0.2c, v0.2d, v0.2d_rep, v0.2e:** C 0 of 7,400 on each seed. G passed
    one in v0.2e: arm latching `mf_noise_1mm` trial 130, latched at 7.75 mm with
    3.01 deg of true tilt. G's tilt check read 0.47 deg and passed it
    (`results/benchmark_v0.2e/REPORT.md`, "G's one bad unit"). C, on the same trial,
    hit its time limit.
  - **Checkpoint 2 (v0.2b):** C passed 6 in 6,200. Five came from a bug in the arm's
    yaw check at 0.2 mm clearance, since fixed (`results/v0.2c_verify_fixes/REPORT.md`).
  - **heldout2:** C passed 8 of 400 on the arm, all at 0.3 N/s F/T drift. They are
    short plugs at 13.05-14.40 mm, against the 14.5 mm limit. H passed 0 and I 1 in
    that cell (p = 0.0078 and 0.016).
- **Why heldout2's 8 happened (POST HOC trace,
  `results/v0.2f_h2_diagnosis/REPORT.txt`).**
  - The plug was at the floor when C saw the bottoming force.
  - VERIFY then holds a 1 N preload on the *read* axial force. With more than 1 N of
    push-out drift since C's last tare, that is about 0 N or a pull in truth. The plug
    rose 0.6-1.8 mm during the wall probes.
  - The wall probes still found both walls, and nothing re-checks depth before SUCCESS.
  - All 8 have push-out axial drift of +0.19 to +0.30 N/s.
  - D has no low-force phase after the seat, so it is not affected.
  - It happens only on the arm, because C's contact moves are slower there.
- **What that means for the record.** In standard and latching, the F/T bias is
  constant and tared out, so VERIFY cannot lift a plug there. C's zero-bad-unit record
  relies partly on that simulator assumption. A real sensor drifts. A depth re-check
  before SUCCESS is a candidate fix for a later, pre-registered round. It is not
  implemented.
- <!-- PENDING: tilt diagnosis -->
- The housing-only VERIFY has no tilt check. Squaring the plug to the floor is what
  keeps housing-only tilt in spec.

## 10. "What would you need to prove it on hardware, and what does it cost?"

The test is fixed in `hardware/TEST_PROTOCOL.md`.
- **What it runs.** C, I, J and F, plus A as a check, on a housing-only part and a
  Molex Micro-Fit 3.0.
- **The jig and the pose.** A jig sets each trial's socket x, y, yaw and tilt, and the
  final plug pose is measured.
- **Trial counts.** 100 trials per condition, and 25 per bad-part defect: about 3,000
  insertions.
- **Why those counts** (`hardware/RIG_POWER.md`). On the housing-only part, at the
  simulated rates, C against I needs 70-100 paired trials in all for 80% power on
  success, and 90-100 on bad units; 100 per condition gives 400 per controller. On
  Micro-Fit good parts the simulated differences are too small to test on a rig
  (780-1,200 pairs on the gantry, 7,800 or more on the arm), so the rig reports rates
  only there.
- **Predictions.** The simulation's predictions are frozen
  (`results/v0.2f_rig_predictions`, seed 20261201) with the rule for judging a rig
  result. At 50 trials per condition, the housing-only prediction is C 194/200 against
  F/I 175/200 on the gantry, with 0 against 13 bad units.
  <!-- RIGPRED: update to 100 -->

Rig options in `hardware/BOM.md`. A desk gantry is about $23.3k plus the F/T sensor. A
UR3e with a Bota SensONE T5 is about $39.8k, and a UFactory 850 hybrid about $13.6k.
None of these totals includes the RCC, the socket jig, the pose measurement or the test
parts. The F/T sensor needs at least about 72.5 N of axial range for the Micro-Fit
force budget, so an ATI Mini40 SI-20-1 or a Bota MiniONE Pro does not fit. Nothing has
been bought.

The latch-model fitter that will turn rig force-depth curves into a connector model
passes 13 of 14 quantities on synthetic curves. It fails its own rule on hook
stiffness (`results/v0.2f_latch_fit/REPORT.txt`), and it has not seen a real curve.

## 11. "Is the 3 deg spec doing the work?"

Partly, yes. The 3 deg limit on yaw and tilt is an assumed seating spec (README,
"Success tolerances"). Most of the baselines' bad units sit just past it. On seed
20261130, I's gantry standard bad units are 14.38-14.98 mm deep with 3.00-5.53 deg of
yaw or tilt. Over three seeds, 392 of I's 433 housing-only bad units are at full depth
and over 3 deg, median 3.45 deg (`hardware/RIG_POWER.md`).

The rescoring below is POST HOC, on seed 20261130 only. It comes from an exact replay
of the conditions that matter, 6,000 rows identical to the benchmark
(`results/v0.2f_evidence/TOLERANCE.md`):

| Yaw/tilt limit | 2 deg | 3 deg (as run) | 4 deg | 5 deg |
|---|---|---|---|---|
| gantry standard, C-only / I-only | 122 / 2 | 53 / 8 | 31 / 10 (p = 0.0015) | 26 / 10 (p = 0.011) |
| arm standard, C-only / I-only | 119 / 7 | 54 / 16 | 30 / 17 (p = 0.079) | 27 / 18 (p = 0.23) |
| I's bad units, gantry / arm standard | 110 / 107 | 32 / 32 | 8 / 7 | 3 / 3 |
| C's bad units, gantry / arm standard | 3 / 1 | 0 / 0 | 0 / 0 | 0 / 0 |

- A looser spec shrinks C's standard lead. On the arm the lead is no longer significant
  at 4 deg.
- A tighter spec widens the lead, and at 2 deg C passes some bad units too.
- On `heldout`, the comparison turns against C as the spec loosens (gantry C-only /
  I-only 48/60 at 3 deg, 23/69 at 5 deg).
- A 1.0 mm depth tolerance instead of 0.5 mm changes at most two trials per cell.

The rescored numbers do not replace the pre-registered ones. The question for a pilot
customer is their real spec: angle and depth, and whether acceptance is by angle, by
click or by pull test.
