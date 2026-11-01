# W5: serial-arm backend (development measurements)

`defex/sim/arm_backend.py` runs the unchanged harness, controllers, perception
and scoring on a UR5e (MuJoCo Menagerie, BSD-3-Clause, fetched at a pinned
commit by `scripts/fetch_menagerie.py`; not in git). The workcell's socket,
24 contact pairs, tool, F/T sensor and payload are the gantry's, byte for byte;
only the fixture changes. Joint servos are Menagerie's PD actuators (series-
elastic joints: 2000 N m/rad shoulder/elbow, 500 N m/rad wrist), gravity is
compensated in the joints as the UR controller does, setpoints go through
damped least-squares IK at 500 Hz with 6 ms command latency (the first version
delayed commands by 4 ms because of an off-by-one in the buffer; fixed in review
and pinned by a check of when a command first reaches the actuators). Payload
identification on the arm: 0.12 g and 0.16 mm error. Run with
`python -m experiments.robustness --backend arm ...`.

## Unchanged controllers on the arm (seed 2026, 5 conditions x 20 trials)

Conditions: nominal, lateral_3mm, noise_1mm, noise_2mm, friction_1. Data:
`data/arm_unchanged_controllers` (copied from the development run, which used
an uncommitted working tree at the W5 backend commit).

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

## Fix through the protocol (done) and what is left

Backends now report `fixture_dynamics` (effective mass at the tool along the
insertion axis, weakest translational stiffness, yaw stiffness, command latency):

| | Gantry | UR5e |
|---|---|---|
| effective mass, insertion axis | 0.88 kg | 6.32 kg |
| translational stiffness | 10.0 N/mm | 8.0 N/mm |
| yaw stiffness | 15 N m/rad | 400 N m/rad |
| command latency | 0 | 6 ms |

Controllers C, D and F scale contact speeds by sqrt(1 kg / effective mass) and
C caps yaw probing so that stiffness x speed x reaction time stays within 80% of
its torque limit. Both rules are inactive on the gantry: 120 development trials
of C and F are identical to the W6 branch in every field.

Re-run on the arm after review fixes (6 ms latency, wall probes also scaled;
same 100 development trials per controller; data: `data/arm_after_review`,
committed code):

| Controller | unchanged controllers | with fixture dynamics |
|---|---|---|
| A fixed | 25% | 25% |
| B vision | 63% | 63% |
| E vision + RCC | 76% | 76% |
| D spiral | 4% | **84%** (7 bad units) |
| F spiral + RCC | 2% | **85%** (9 bad units) |
| C adaptive | 1% | **40%** (43 protective stops) |

(The first version of this report gave C 13% with the 4 ms latency bug and
unscaled wall probes, from an unsaved run.)

C is still not usable on the arm. Two problems remain, both in VERIFY (seen in
the first run; to be re-checked on the saved run):

1. Yaw probing still trips the 0.6 N m stop in some trials even at the capped
   rate (0.72 N m in nominal trial 0), so stiffness x speed x delay does not fully
   explain the overshoot on the arm.
2. The lateral wall probe does not find the far wall (e.g. reactions 2.0 and
   0.3 N at 0.28 and 1.35 mm, repeated on every retry until the time limit):
   pushed sideways at the tip, the arm tilts the plug about its floor contact
   instead of translating it.

On a serial arm, C's wall-probe verification needs a redesign; W3's
push-click-pull verification (latch signature plus pull test) avoids lateral
probing altogether and is the planned route. Checkpoint 2 (A-F on both
backends, with latching physics) waits for W3.
