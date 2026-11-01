# Ten hard questions, with answers (draft for Hasan)

Short answers you can give yourself, each with the file that backs it. Numbers
are from benchmark_v0.2b (seed 20261102, results at 667ac0c, code 8e29f2e)
unless marked. Simulation only.

## 1. "How does it compare with spiral search?"

On a gantry with honest vision C seats more (99.1% against 97.0% for spiral
search on a compliance device, F; p < 1e-6). On the UR5e arm F matches or beats
C: 96.3% against 96.7% on standard conditions, 95.2% against 90.8% on latching
parts. Where C clearly wins is bad parts: it passed 0 of 1,600 deliberately bad
parts, F passed 1,062. Spiral search checks depth only; it cannot tell a
half-latched or broken-latch part from a good one.
`results/benchmark_v0.2b/REPORT.md`, `TABLES.md`.

## 2. "So why not just use spiral search?"

If a passed bad connector costs nothing, spiral search on a compliance device
is the faster cell: 10-37% more good units per hour than C. C's case is the cost
of a bad connector that leaves the cell. We have not priced that; the pilot
customer's escape cost decides it. `results/benchmark_v0.2b/REPORT.md`
(Headline).

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
never reaches the latch: no snap appears in the force-depth trace and C does not
declare success (`defex/sim/mating.py`).
It is slow: C rejects the part by running out of time, about 26 s.
`results/benchmark_v0.2b/TABLES.md` (latching), `results/w3_development/REPORT.md`.

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

## 9. "Has C ever passed a bad part?"

Yes: 6 in 6,200 good-part trials. Five are one bug: on the arm, in a 0.2 mm
clearance cavity, the yaw check that replaces the yaw sweep has no effect, and a
plug wedged short of full depth passes. One plug was seated just over the 3
degree tilt limit. Both are being fixed and will be tested on a new seed.
`results/benchmark_v0.2b/AUDIT_TABLES.md`.

## 10. "What would you need to prove it on hardware, and what does it cost?"

A cobot with a 500 Hz external loop (UR3e, about $33,000) or a desktop gantry,
a fast 6-axis wrist sensor (Bota or ATI, $3,700 and up), the target connector and
a fixture. Then the protocol in `hardware/TEST_PROTOCOL.md`: measure the real
force-depth curve, re-fit the latch model, and compare predicted with measured
success. Nothing has been bought. `hardware/BOM.md`.
