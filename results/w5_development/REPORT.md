# W5: serial-arm backend (development measurements)

`defex/sim/arm_backend.py` runs the unchanged harness, controllers, perception
and scoring on a UR5e (MuJoCo Menagerie, BSD-3-Clause, fetched at a pinned
commit by `scripts/fetch_menagerie.py`; not in git). The workcell's socket,
24 contact pairs, tool, F/T sensor and payload are the gantry's, byte for byte;
only the fixture changes. Joint servos are Menagerie's PD actuators (series-
elastic joints: 2000 N m/rad shoulder/elbow, 500 N m/rad wrist), gravity is
compensated in the joints as the UR controller does, setpoints go through
damped least-squares IK at 500 Hz with 6 ms command latency. Payload
identification on the arm: 0.12 g and 0.16 mm error. Run with
`python -m experiments.robustness --backend arm ...`.

## Unchanged controllers on the arm (seed 2026, 5 conditions x 20 trials)

Conditions: nominal, lateral_3mm, noise_1mm, noise_2mm, friction_1.

| Controller | Success | Bad units passed | Protective stops | Median cycle (s) |
|---|---|---|---|---|
| fixed | 25% | 0 | 75 | 4.32 |
| correction | 63% | 5 | 32 | 4.31 |
| adaptive | 1% | 0 | 46 | 24.09 |
| spiral | 4% | 0 | 5 | 3.93 |
| correction_rcc | 76% | 2 | 22 | 6.32 |
| spiral_rcc | 2% | 1 | 0 | 5.48 |

The position programs (A, B, E) behave much as on the gantry. **Every
force-controlled controller fails** (C 1%, D 4%, F 2%). This is the gap the brief
asked W5 to expose, not a bug in the backend:

- C reaches full depth (15.0 mm) and seats, then trips its 20 N limit on the
  bottoming impact or the cell's 0.6 N m stop during VERIFY's yaw probing.
- Cause: stiffness times speed times delay. The gantry's wrist yaw servo is
  15 N m/rad; the UR wrist joint is 500 N m/rad. Rotating at 10 deg/s against a
  wall, torque rises about 87 N m/s on the arm against 2.6 N m/s on the gantry,
  so the 40 Hz sensor filter plus command latency overshoot the stop before the
  controller reacts. Same in translation at the floor.
- Not the latency itself: 2 ms and 6 ms give the same result (0 of 10 each with
  default speeds). Slower speeds (insert 4 mm/s, near-floor 2 mm/s) cut the peak
  force from 33 N to 12 N but still trip the torque stop in yaw probing (2 of 10).
- Root cause in the design: controllers receive `ControllerContext.fixture`,
  which describes the gantry even when they run on the arm, so C cannot scale its
  probing to the stiffness it is pushing against.

Fix (next): give controllers the actual fixture's Cartesian stiffness and command
latency through the protocol, and bound every guarded move by a force/torque
budget (speed <= budget / (stiffness x reaction time)); a real UR cell would also
run the insertion in force mode with reduced joint gains. Then re-run A-F on both
backends for Checkpoint 2.
