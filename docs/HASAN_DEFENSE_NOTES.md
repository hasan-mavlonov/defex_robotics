# Hard questions, with answers (draft for Hasan)

Short answers you can give yourself, each with the file that backs it. Simulation only.

Sources, unless an answer says otherwise:
- benchmark_v0.2e: seed 20261130, code ddd0d34, `results/benchmark_v0.2e/REPORT.md`.
- "Three seeds" adds benchmark_v0.2d (20261123) and benchmark_v0.2d_rep (20261124),
  both on the v0.2d code (42df5c8). Each seed is reported on its own; no p-value is
  pooled across seeds.
- The per-condition and tolerance analysis is in `results/v0.2f_evidence/REPORT.md`.
- heldout2: seed 20261207, the same ddd0d34 controllers,
  `results/heldout2_v0.2f/REPORT.md`.

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
- **heldout2.** C is ahead on unseen receptacle yaw (100% against 37.5% on the
  gantry). It is below F on an unseen grasp offset (gantry 75.0% against 98.8%).

Files: `results/benchmark_v0.2e/REPORT.md`, `results/v0.2f_evidence/CONCENTRATION.md`,
`PERCOND.md`, `results/heldout2_v0.2f/REPORT.md`.

## 2. "So why not just use spiral search?"

In simulation the spiral cell is faster. F and I make more good units per hour than C
on every cell. On gantry standard that is 1,100 against 601, and on arm standard 593
against 387 (`results/benchmark_v0.2e/HEADLINE_TABLES.md` (c)).
- About two-thirds of C's extra time on gantry standard is VERIFY: 1.89 s of 2.94 s
  (POST HOC, `results/v0.2f_evidence/PHASES.md`).
- What C buys is fewer out-of-tolerance housing-only plugs leaving the cell, in the
  high-camera-error trials (POST HOC per-condition breakdown).
- J (F's insertion plus C's VERIFY) gets most of that: 2 bad units against F's 178.
  J makes 643 good units per hour on gantry standard.
- Whether the trade pays depends on what a mis-seated connector costs the customer,
  which is not priced. It also depends on whether the customer's spec is as tight as
  the assumed 3 deg (question 11).

## 3. "Why should I trust MuJoCo contact?"

You should not trust absolute numbers.
- The contact model is pinned by tests against stated physics
  (`tests/test_mating_physics.py`).
- 12 randomized simulators plus the nominal one per machine, on the current
  controllers (`results/sim_randomization_v0.2f/REPORT.md`, seed 20261205; G pinned
  to its nominal model, a configuration of this run):
  - Gantry: 29 of 29 primary comparisons hold.
  - Arm: 24 of 29. C's high-camera-error lead holds narrowly (10 of 12 against F and
    I, pooled not significant). Neutral success does not hold: C loses friction_1 in
    the 6 pyramidal-cone variants, seating 1 of 90 against 89-90 of 90 (the split by
    cone is POST HOC). Arm latching C below F does not hold per simulator (9 of 12;
    pooled still C below F, p = 0.038). C against I there is not resolved (low power).
  - C's zero bad units does not hold on every simulator (arm: a 3.11 deg plug; gantry: an over-penetrated seated plug): 1 per machine, both in
    variant 10. C still passes fewer than F, H and I in all 12 variants.
  - Cause (POST HOC, `results/v0.2f_friction_diagnosis/REPORT.md`): in 85 of C's 89 failures C seats the part correctly, then VERIFY rejects it. At mu = 1 the floor friction under the 1 N preload reaches the wall probe's 2 N stop before the plug meets a wall, so the wall-yaw check reads too little free travel; recovery repeats the same probe until the time limit. Under the pyramidal cone MuJoCo ignores the repo's 20 ms friction time constant (solreffriction); setting only that to 2 ms on the nominal elliptic arm gives the same failure. MuJoCo's documentation calls the elliptic cone the closer model. On the nominal arm, C's 18 friction_1 losses over three seeds are 6 of these wall-probe stalls, 11 torque protective stops at 0.61-0.71 N m (limit 0.6) and 1 mouth stall. J (same VERIFY on F's RCC stage) seated 300 of 300. A rig test of C's wall probe at C's preload settles whether it transfers.
- The earlier run (`results/sim_randomization_v0.2/REPORT.md`) used the v0.2a code
  (fe48eca), gantry only. Do not cite its "C led in all 13" for the current code.
- One known way the simulator flatters C: its F/T bias is constant and tared out. Under
  drift, C's VERIFY can lift a seated plug (question 9).
- The real answer is a rig. Measured success will be compared with frozen predictions
  on the same trial list, with intervals (`hardware/TEST_PROTOCOL.md`).

## 4. "What happens with a stubbed pin, or a part at the edge of the datasheet?"

**Stubbed pin.** C passed 0 of 400 stubbed-terminal parts, and so did I. F passed 259
and D 117. The plug stops short and the pull test moves it. C's median cycle on a
stubbed-terminal part is 8.46 s on the gantry and 12.04 s on the arm (8.9 s and 13.0 s
over all four latching defects; `results/benchmark_v0.2e/TABLES.md` and `trials.csv`,
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
- G passed one bad unit in benchmark_v0.2e (question 9). On heldout2 it passed the
  same 8 F/T-drift bad units as C.
- On heldout2, G gave no measurable gain in any cell. Its benchmark gains come from the
  same camera-error conditions as C's lead (POST HOC).
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
- With a 1.5 mm hand-eye bias, I seats more than C on all three seeds (per-condition,
  POST HOC).
- On heldout2's unseen grasp offset, C was not told the offset and fell below F. A
  POST HOC trace found that the cause is C's in-hand estimate. With the true grasp
  given to C, 5 of 5 replays seat (`results/v0.2f_h2_diagnosis/REPORT.md`).

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
  - **sim_randomization_v0.2f:** C passed 1 on each machine, both in variant 10:
    a seated gantry plug that over-penetrated, and an arm latched plug at 3.11 deg
    tilt (`results/sim_randomization_v0.2f/TABLES.md`).
  - **heldout2:** C passed 8 of 400 on the arm, all at 0.3 N/s F/T drift. They are
    short plugs at 13.05-14.40 mm, against the 14.5 mm limit. H passed 0 and I 1 in
    that cell (p = 0.0078 and 0.016).
- **Why heldout2's 8 happened (POST HOC trace of 6 of the 8,
  `results/v0.2f_h2_diagnosis/REPORT.md`; the depth and drift ranges cover all 8).**
  G passed the same 8 and J 5.
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
- Tilt check, POST HOC diagnosis (`results/v0.2f_tilt_diagnosis/REPORT.md`, development seeds 2026/2027): the latching tilt check compares the plug with C's own socket-axis estimate, the axis C aimed it along, so it cannot see tilt that comes from an error in that estimate. G's 3.01 deg unit is this case (estimate 2.87 deg off the true axis after a wrong 'flat' fold). On the development seeds 234 of 8,320 C/G verdicts read more than 1 deg under the true tilt; none became a bad unit. What keeps tilted bad units rare is the Micro-Fit cavity, which stops a latched plug at about 3.2 deg, and a camera tilt error rarely over 3 deg. Near misses (declared, 2.5-3.0 deg) were 5 in about 3,540 declared latching trials. J's empty first tilt window comes from its hand-over code and cannot happen to C. On the gantry the housing-only VERIFY has no yaw check (its sweep always ends in SUCCESS); on the arm the wall-yaw check bounds |yaw| at 2.0 deg. Two default-off options (push below the force floor; J's hand-over window) passed a no-harm rule on validation seed 4007 but changed no outcome; whether to use them is Hasan's call.
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
  result. At 100 trials per condition, the housing-only prediction is C 387/400 against
  F/I 336/400 on the gantry, with 0 against 33 bad units; on gantry Micro-Fit good parts C is
  predicted below F (284 against 297 of 300).

Rig options in `hardware/BOM.md`. A desk gantry is about $23.3k plus the F/T sensor. A
UR3e with a Bota SensONE T5 is about $39.8k, and a UFactory 850 hybrid about $13.6k.
None of these totals includes the RCC, the socket jig, the pose measurement or the test
parts. The F/T sensor needs at least about 72.5 N of axial range for the Micro-Fit
force budget, so an ATI Mini40 SI-20-1 or a Bota MiniONE Pro does not fit. Nothing has
been bought.

The latch-model fitter that will turn rig force-depth curves into a connector model
passes 13 of 14 quantities on synthetic curves. It fails its own rule on hook
stiffness (`results/v0.2f_latch_fit/REPORT.md`), and it has not seen a real curve.

## 11. "Is the 3 deg spec doing the work?"

Partly, yes. The 3 deg limit on yaw and tilt is an assumed seating spec (README,
"Success tolerances"). Most of the baselines' bad units sit just past it. On seed
20261130, I's gantry standard bad units are 14.38-14.98 mm deep with 3.00-5.53 deg of
yaw or tilt. Over three seeds, 392 of I's 433 housing-only bad units are at full depth
and over 3 deg, median 3.45 deg (`hardware/RIG_POWER.md`).

The rescoring below is POST HOC, on all three benchmark seeds (p per seed, not pooled).
It comes from exact replays of the conditions that matter, with extra logging
(`results/v0.2f_evidence/TOLERANCE.md`):

| POST HOC; per seed 20261123 / 20261124 / 20261130 | 2 deg | 3 deg (as run) | 4 deg | 5 deg |
|---|---|---|---|---|
| gantry standard, C-only / I-only | 113/0, 114/1, 122/2 | 60/2, 62/3, 53/8 | 28/5, 32/3, 31/10 (p 6.6e-5, <1e-6, 0.0015) | 18/6, 26/4, 26/10 (p 0.023, 5.9e-5, 0.011) |
| arm standard, C-only / I-only | 114/15, 111/9, 119/7 | 51/17, 51/11, 54/16 | 27/21, 24/13, 30/17 (p 0.47, 0.099, 0.079) | 22/27, 20/15, 27/18 (p 0.57, 0.5, 0.23) |
| I's bad units, gantry standard | 104, 93, 110 | 48, 39, 32 | 13, 9, 8 | 2, 2, 3 |
| I's bad units, arm standard | 109, 101, 107 | 43, 39, 32 | 15, 10, 7 | 4, 4, 3 |
| C's bad units, gantry / arm standard | 1/1, 0/0, 3/1 | 0 | 0 | 0 |

- A looser spec shrinks C's standard lead. On the gantry it holds at 4 and 5 deg on
  every seed; on the arm it is not significant at 4 deg on any seed.
- A tighter spec widens the lead, and at 2 deg C passes some bad units too.
- On `heldout`, the comparison turns against C as the spec loosens (gantry C-only /
  I-only at 5 deg: 32/44, 21/44, 23/69 on the three seeds).
- A 1.0 mm depth tolerance instead of 0.5 mm changes any bad-unit count by at most 5.

The rescored numbers do not replace the pre-registered ones. The question for a pilot
customer is their real spec: angle and depth, and whether acceptance is by angle, by
click or by pull test.

## 12. "Does a Python state machine fit a 2 ms control loop?"

On this development laptop (Apple M5, shared with other jobs; not the rig PC), the
controller's own per-tick work takes about 43-50 us at the median for C and G. In about
12.6 million ticks its replayed cost never exceeded 2 ms; the slowest tick (0.6-0.9 ms at
low load) is the planning tick after a blocked attempt (hole-localizer update), taken
with the tool at rest. Wall-clock misses of 2 ms came from Python garbage collection and
operating-system preemption, not controller logic (66 of 1.0 million gantry ticks at low
load). On a rig: run the loop on an isolated core, keep garbage collection out of the
cycle, and measure the planning tick on the rig PC
(`results/v0.2f_realtime/REPORT.md`, development measurement).

Related, same report: the gantry pull test's force ringing (up to 1.11 x the 35.2 N
command) comes from the simulator's undamped latch hook. No pull exceeded the 58 N
retention force. One fairness item runs against the baselines: C caps any retract pull
on a latching part at 36 N, and D, F, H and I have no such cap. H's retry retract tore
the latch of 2 good gantry parts on the development seeds (POST HOC observation).
