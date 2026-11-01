# Ten hard questions, with answers (draft for Hasan)

Short answers you can give yourself, each with the file that backs it. Numbers
are from benchmark_v0.2c (seed 20261116, results at c3884c6, code 45f8b06)
unless marked. Simulation only.

## 1. "How does it compare with spiral search?"

Mixed, and the losses are in the README headline. Spiral search on a compliance
device with a pull test (I) seats more latching good parts than C on both
machines (gantry 99.2% against 95.7%, arm 96.2% against 93.7%) and matches C when
the camera is worse than believed. C seats more housing-only connectors under
standard conditions (gantry 99.0% against 96.6%, arm 97.6% against 96.4%). Both
pass 0 of 2,200 deliberately bad parts. Where C clearly differs: it called no
mis-seated connector good in 7,400 good-part trials; I did so 135 times.
`results/benchmark_v0.2c/REPORT.md`, `PAIRED_TABLES.md`.

## 2. "So why not just use spiral search?"

In simulation, spiral search with a pull test is the faster cell: it makes more
good units per hour than C on seven of eight suites (standard: gantry 1,101
against 606, arm 596 against 373), and seats as many or more latching parts.
What C buys is fewer mis-seated connectors leaving the cell, mostly when the
camera error is large. Whether that is worth the lower throughput depends on
what a mis-seated connector costs the customer, which we have not priced. C's
lead on parts at the edge of the datasheet comes mostly from a stall push a
spiral cell could add (question 4). `results/benchmark_v0.2c/REPORT.md`.

## 3. "Why should I trust MuJoCo contact?"

You should not trust absolute numbers. Two things limit the risk. The comparison
held on 12 randomized simulators (contact stiffness, damping, solver softness,
friction cone, servo stiffness): C led the best baseline in all 13, by 8.3 to
12.5 points (gantry, earlier code and untuned baselines,
`results/sim_randomization_v0.2/REPORT.md`; not repeated since). And the contact
model is pinned by tests against stated physics (`tests/test_mating_physics.py`).
The real answer is a rig: sim-predicted success against measured success on the
same connector, with confidence intervals (`hardware/TEST_PROTOCOL.md`).

## 4. "What happens with a stubbed pin, or a part at the edge of the datasheet?"

Stubbed pin: C passed 0 of 400 stubbed-terminal parts, I 0, F 250, D 153. The
plug stops short and the pull test moves it. C rejects a bad part in a median
8.4 s (gantry) and 12.8 s (arm), down from about 26 s at Checkpoint 2
(`results/benchmark_v0.2c/TABLES.md`, latching).

Edge of the datasheet: at the maximum terminal friction, the conventional cells
seat none of 100 parts and C all 100, on both machines. That is because they
push at the connector file's 30 N insert target, below the datasheet's 32 N
maximum mating force, while C pushes at 35.2 N when a plug stalls. A spiral cell
with that push has not been tested; the fair answer is that this is a setting,
not proof of the method (`REPORT.md`, "latch_spread: what the gap is").

## 5. "Why not learning?"

We tried a learned piece where it can help without hardware data: a small
network that predicts where the hole is from a blocked contact (G). It beats C on
six of eight suites (for example arm standard 98.4% against 97.6%, p = 0.0015;
arm with the camera worse than believed 85.0% against 78.0%) and shows no gain on
latch_spread. On latching good parts it is level with I (not a pre-registered
comparison). End-to-end learned policies need real force traces we do not have,
and would make the false-accept number hard to defend.
`results/benchmark_v0.2c/REPORT.md` (G against C).

## 6. "What is the cycle time on a real line?"

Unknown. In simulation the median good cycle on the standard suite is 5.3 s on
the gantry and 8.1 s on the arm; spiral search is 2.4 s and 4.8 s. The pull test
adds about 3-3.7 s to a latching cycle for any cell. A real UR5e may lag less than
the simulated one (0.2 s servo lag), which would change both cells' cycle times;
it must be measured on the rig. `results/benchmark_v0.2c/TABLES.md`,
`results/w5b_development/REPORT.md`.

## 7. "Did you tune C on the test?"

No. Every reported run is pre-registered with a fresh seed, frozen code and
decision rules written before the first trial (`PREREGISTRATION.md` in each
benchmark folder). Development used seeds 2026, 2027, 3001-3040, 4001, 4002 and
3032. Two things to say before someone else does: the fixes in v0.2c were
motivated by what Checkpoint 2 found, and the `latch_spread` suite was added
after development showed C ahead there. That is why both were tested on a new
seed, and why the run also gave the baselines the pull test. The rules force us
to publish losses: C below F and I on latching parts is in the README headline.

## 8. "Does C cheat by knowing things a real cell would not?"

It gets what an integrator knows in advance: the connector drawing and
datasheet, the programmed socket pose, fixture limits, the camera's characterized
accuracy, and the fixture's wrist stiffness and servo lag. It never sees the true
socket pose or contact state; a test fails the build if controller code imports
the simulator or ground truth
(`tests/test_motion_and_estimation.py::test_controller_code_cannot_reach_the_simulator`).
When the camera is worse than its stated accuracy, C does worse and F and I
match it.

At Checkpoint 2, C's latch check used the simulator's assumed latch geometry. It
now uses datasheet values only: a pull at 1.1 x the 32 N maximum mating force and
a movement limit of 0.6 x the 1.75 mm terminal wipe. With latch position and
force varied within and at the edge of the datasheet, C seats 600 and 597 of 600
good parts (`latch_spread`), including 100 of 100 per machine in the
early-latch condition (`mf_latch_early`). The spread itself is assumed, not
measured.

## 9. "Has C ever passed a bad part?"

Not in benchmark_v0.2c: 0 of 7,400 good-part trials and 0 of 2,200 deliberately
bad parts. At Checkpoint 2 it passed 6 in 6,200 good-part trials, five from a bug
in the arm's yaw check at 0.2 mm clearance, now fixed
(`results/v0.2c_verify_fixes/REPORT.md`). One known hole remains: VERIFY does not
check tilt. G passed one plug at 3.21 degrees of tilt in this run, and C passed
one just over 3 degrees at Checkpoint 2 (`results/benchmark_v0.2c/AUDIT_TABLES.md`).

## 10. "What would you need to prove it on hardware, and what does it cost?"

A cobot with a 500 Hz external loop (UR3e, about $33,000) or a desktop gantry,
a fast 6-axis wrist sensor (Bota or ATI, $3,700 and up), the target connector and
a fixture. Then the protocol in `hardware/TEST_PROTOCOL.md`: measure the real
force-depth curve, re-fit the latch model, and compare predicted with measured
success. Nothing has been bought. `hardware/BOM.md`.
