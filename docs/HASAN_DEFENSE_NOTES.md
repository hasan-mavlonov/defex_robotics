# Ten hard questions, with answers (draft for Hasan)

Short answers you can give yourself, each with the file that backs it. Numbers
are from benchmark_v0.2b (seed 20261102, results at 667ac0c, code 8e29f2e)
unless marked. Simulation only.

## 1. "How does it compare with spiral search?"

On a gantry with honest vision C seats more housing-only connectors (99.1%
against 97.0% for spiral search on a compliance device, F; p < 1e-6). On the UR5e
arm F matches or beats C: 96.3% against 96.7% on standard conditions, 95.2%
against 90.8% on latching parts. C passed 0 of 1,600 deliberately bad parts, F
1,062. Be careful with that number: spiral search here checks depth only and C
ends with a pull test, so the fair answer is "a spiral cell with a pull test has
not been run yet". On latching parts, F re-tuned for that connector seats 60 of
60 on a dev seed against C's 54 (`results/v0.2c_gantry_baselines`, branch
`v0.2c/gantry-baselines`). `results/benchmark_v0.2b/REPORT.md`, `TABLES.md`.

## 2. "So why not just use spiral search?"

Today, in simulation, a well-tuned spiral search on a compliance device is the
faster cell, with 10-37% more good units per hour than C, and it seats as many
parts on the arm. C's measured edge is bad parts not passed, and that comes from a
pull test a spiral cell could add. The honest answer: C's case is not proven yet.
The next run should put a pull test on F and vary the latch geometry
(`results/benchmark_v0.2b/REPORT.md`, "After the run").

## 3. "Why should I trust MuJoCo contact?"

You should not trust absolute numbers. Two things limit the risk. The comparison
held on 12 randomized simulators (contact stiffness, damping, solver softness,
friction cone, servo stiffness): C led the best baseline in all 13, by 8.3 to
12.5 points (gantry, earlier code, `results/sim_randomization_v0.2/REPORT.md`).
And the contact model is pinned by tests against stated physics
(`tests/test_mating_physics.py`). The real answer is a rig: sim-predicted
success against measured success on the same connector, with confidence
intervals (`hardware/TEST_PROTOCOL.md`).

## 4. "What happens with a stubbed pin?"

In simulation C passed 0 of 400 stubbed-terminal parts; F passed 345, D 51. In the
model a bent pin butts the header 0.2 mm after the terminals start, so the plug
stops short and C's pull test moves it; C does not declare success
(`defex/sim/mating.py`). A depth check with a tighter seat margin also catches
many: tuned F's stubbed-terminal escapes fell when its margin went from 1.0 to
0.5 mm (`results/v0.2c_arm_baselines/REPORT.md`). C is slow about it: about 26 s
per rejected part in Checkpoint 2 (about 8-12 s with the v0.2c defect verdict,
development). `results/benchmark_v0.2b/TABLES.md` (latching).

## 5. "Why not learning?"

We tried a learned piece where it can help without needing hardware data: a
small network that predicts where the hole is from a blocked contact (G).
It helps on four of six suites (for example arm standard 97.5% against 96.7%,
p = 0.002) and is never worse, but it does not close the gap to F on the arm.
End-to-end learned policies need real force traces we do not have yet, and they
would make the false-accept number hard to defend. `results/w9_development/REPORT.md`,
`results/benchmark_v0.2b/REPORT.md` (G against C).

## 6. "What is the cycle time on a real line?"

Unknown. In simulation, the median good cycle is 5.3 s on the gantry and 8.2 s
on the arm; spiral search is 3.5 s and 6.5 s. A real UR5e may lag less than the
simulated one (0.2 s servo lag), which would change both cells' cycle times; it
must be measured on the rig. Bad parts cost about 26 s each.
`results/benchmark_v0.2b/TABLES.md`, `results/w5b_development/REPORT.md`.

## 7. "Did you tune C on the test?"

No. Every reported run is pre-registered with a fresh seed, frozen code and
decision rules written before the first trial (`PREREGISTRATION.md` in each
benchmark folder). C's development used seeds 2026, 2027, 3001-3031 and 4001.
The rules also force us to publish losses: F matching C on the arm is in the
README headline because the pre-registration required it.

## 8. "Does C cheat by knowing things a real cell would not?"

It gets what an integrator knows in advance: the connector drawing, the
programmed socket pose, fixture limits, the camera's characterized accuracy, and
the fixture's wrist stiffness and servo lag. It never sees the true socket pose
or contact state; a test fails the build if controller code imports the
simulator or ground truth
(`tests/test_motion_and_estimation.py::test_controller_code_cannot_reach_the_simulator`). When the camera is
worse than its stated accuracy, C does worse: F matches or beats it
(`results/benchmark_v0.2b/REPORT.md`, mis-characterized vision).

One exception, found after Checkpoint 2: on latching parts C's click window and
pull limit use the connector file's assumed latch geometry, which is exactly what
the simulator builds parts from. That is a soft form of knowing the simulator, and
it is why C fails when the simulated latch moves 0.15 mm
(`results/v0.2b_latch_spread/REPORT.md`).

## 9. "Has C ever passed a bad part?"

Yes: 6 in 6,200 good-part trials. Five are one bug: on the arm, in a 0.2 mm
clearance cavity, the yaw check that replaces the yaw sweep has no effect, and a
plug wedged short of full depth passes (fixed on `v0.2c/verify-fixes`; dev seeds:
10 escapes to 0). One plug was seated just over the 3 degree tilt limit; tilt is
not checked on either machine. `results/benchmark_v0.2b/AUDIT_TABLES.md`.

The harder version: "does your latch check overfit your own simulator?" Partly,
yes. The pull limit uses the model's assumed 0.5 mm post-snap stroke, and a
simulated latch that engages 0.15 mm earlier makes C reject most good parts
(`results/v0.2b_latch_spread/REPORT.md`). Fixing it needs the real force-depth
curve from the rig and a tolerance band from the datasheet.

## 10. "What would you need to prove it on hardware, and what does it cost?"

A cobot with a 500 Hz external loop (UR3e, about $33,000) or a desktop gantry,
a fast 6-axis wrist sensor (Bota or ATI, $3,700 and up), the target connector and
a fixture. Then the protocol in `hardware/TEST_PROTOCOL.md`: measure the real
force-depth curve, re-fit the latch model, and compare predicted with measured
success. Nothing has been bought. `hardware/BOM.md`.
