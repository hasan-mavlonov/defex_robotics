# DAIE technical brief (draft for Hasan's review)

Simulation results for the Defex Adaptive Insertion Engine (controller C), as of
benchmark_v0.2b (Checkpoint 2). Not validated on hardware. Every claim names the
file it comes from; unless stated otherwise that is a benchmark_v0.2b file:
results committed at 667ac0c, code frozen at 8e29f2e, pre-registered at 54f3097,
seed 20261102.

## What was tested

Connector insertion in MuJoCo on two machines, a gantry fixture and a UR5e arm
(MuJoCo Menagerie), with noisy vision, a 6-axis wrist force/torque sensor and
bounded actuators. Three suites per machine: 20 standard conditions (displacement,
rotation, tilt, vision noise, friction, tighter clearance) on a housing-only
12 x 8 mm connector; a Molex Micro-Fit 3.0 with terminal and latch forces, three
good-part conditions and four deliberately bad parts; five conditions where the
camera is worse than the cell is told. 54,600 trials, paired across controllers.
([`PREREGISTRATION.md`](../results/benchmark_v0.2b/PREREGISTRATION.md))

C was compared with the conventional cells an integrator would build: D,
force-controlled spiral search as cobot vendors ship it; E, vision correction on
a passive remote centre compliance (RCC) device; F, spiral search on the RCC
device. They were tuned on a development seed with about 68,000 trials
([`BASELINE_TUNING.md`](../results/benchmark_v0.2a/BASELINE_TUNING.md)). G is C
plus a learned contact prior.

## 1. Against the fair baselines

| Machine, suite | C | Best of D, E, F | McNemar p |
|---|---|---|---|
| gantry, standard | 99.1% | F 97.0% | < 1e-6 |
| gantry, latching good parts | 95.7% | F 89.0% | 2.4e-6 |
| gantry, mis-characterized vision | 87.4% | F 84.2% | 0.13 |
| arm, standard | 96.7% | F 96.3% | 0.3 |
| arm, latching good parts | 90.8% | F 95.2% | 0.0003 |
| arm, mis-characterized vision | 75.4% | F 81.4% | 0.0018 |

([`TABLES.md`](../results/benchmark_v0.2b/TABLES.md), last table)

C seats more units than F on the gantry under correctly characterized vision. On
the arm, and on the gantry when the camera is worse than believed, F matches or
beats C. The arm comparison favours C: C's arm rules were set on a development
seed and D, E and F got no arm tuning
([`REPORT.md`](../results/benchmark_v0.2b/REPORT.md), Fairness).

## 2. False accepts on deliberately bad parts

| Defect, 200 per machine | C, gantry / arm | D, gantry / arm | F, gantry / arm |
|---|---|---|---|
| half latched | 0 / 0 | 81 / 44 | 120 / 200 |
| broken latch | 0 / 0 | 132 / 134 | 197 / 200 |
| stubbed terminal | 0 / 0 | 37 / 14 | 171 / 174 |
| wrong polarization | 0 / 0 | 0 / 0 | 0 / 0 |

C passed **0 of 1,600** bad parts as good (Wilson 95% upper bound 0.24%). F passed
1,062, D 442. ([`TABLES.md`](../results/benchmark_v0.2b/TABLES.md), latching
sections.) C does this with a guarded pull at half the rated retention force
after insertion. Its "click" check turned out not to see the latch (it fires on
the terminal-friction drop), so the pull does the work.

**Caveats found after the run** (development seeds,
[`REPORT.md`](../results/benchmark_v0.2b/REPORT.md#after-the-run-review-findings-not-pre-registered)):

- Only C and G run a pull test; D, E and F check depth only. Given the same
  pull in development (dev seed 2026), D and F also pass 0 of 80 bad parts. The
  gap measures having a pull test. C's remaining edge in that run: good parts
  whose latch and terminal forces vary within the datasheet range, C 120 of 120
  per machine against F's 91-93 (`results/v0.2c_integration/review_fixes/REVIEW_TABLES.md`
  on branch `v0.2c/integration`; not pre-registered).
- C's pull limit comes from the simulator's assumed latch geometry. If the
  simulated latch engages 0.15 mm earlier, C seats 4 of 60 good parts on the
  gantry instead of 54; F is unaffected
  ([`results/v0.2b_latch_spread`](../results/v0.2b_latch_spread/REPORT.md)).

On good-part conditions C is not free of escapes: 6 bad units in 6,200 trials
(G: 9). Five come from one identified bug in the arm's yaw check at 0.2 mm
clearance, one is a plug seated just over the 3 degree tilt limit
([`AUDIT_TABLES.md`](../results/benchmark_v0.2b/AUDIT_TABLES.md)).

## 3. Throughput

| Machine, suite | Good units/h, C / F | Median good cycle, C / F |
|---|---|---|
| gantry, standard | 608 / 862 | 5.30 s / 3.54 s |
| gantry, latching | 476 / 527 | 5.72 s / 3.26 s |
| arm, standard | 371 / 474 | 8.21 s / 6.50 s |
| arm, latching | 289 / 458 | 8.36 s / 5.35 s |

Good units per hour of simulated cell time, counting failed cycles, no reset time
per protective stop ([`TABLES.md`](../results/benchmark_v0.2b/TABLES.md)). C makes
10-37% fewer good units per hour than F. It rejects a bad part only by running out of time or retries,
median 26 s per bad part.

## What this supports

- In simulation, C's retention pull test rejected every one of 1,600 deliberately
  bad parts; depth-only conventional cells passed hundreds.
- On a gantry with correctly characterized vision, C seats more housing-only
  connectors than the conventional cells tested.

## What this does not support yet

- That C seats more connectors than a well-built conventional cell in general:
  on the arm it does not, and on latching parts a re-tuned F seats more on a dev
  seed (60 against 54 of 60, `results/v0.2c_gantry_baselines` on branch
  `v0.2c/gantry-baselines`).
- That C's bad-part advantage would survive a conventional cell with a pull test,
  or real latch-to-latch variation.
- Any hardware number. There is no rig yet; the latch model's snap force is
  assumed, and the arm is one simulated model whose servos may lag more than a
  real UR5e. Rig options and a test protocol are in
  [`hardware/BOM.md`](../hardware/BOM.md) and
  [`hardware/TEST_PROTOCOL.md`](../hardware/TEST_PROTOCOL.md).
- Whether C's cell is cheaper per good unit. That depends on the cost of a passed
  bad connector, which is not priced here.

## Robustness of the comparison (earlier code, gantry)

On 12 randomized simulators plus the nominal one (contact stiffness, damping,
solver softness, friction cone, servo stiffness), C led the best of D, E and F in
all 13, by 8.3 to 12.5 points
([`results/sim_randomization_v0.2`](../results/sim_randomization_v0.2/REPORT.md)).
That run used the code of benchmark_v0.2a, not the current code.
