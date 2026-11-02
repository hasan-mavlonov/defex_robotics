# DAIE technical brief (draft for Hasan's review)

Simulation results for the Defex Adaptive Insertion Engine (controller C):
benchmark_v0.2d first, then benchmark_v0.2c. Not validated on hardware. Every claim names the file it comes
from; unless stated otherwise that is a benchmark_v0.2c file: results committed
at c3884c6, code frozen at 45f8b06, pre-registered at b479e17, seed 20261116,
Micro-Fit insert target 30 N.

**benchmark_v0.2d** (seed 20261123, code 42df5c8, pre-registered at 966a5f5,
96,000 trials, insert target 35.2 N for every controller;
[`REPORT.md`](../results/benchmark_v0.2d/REPORT.md)) changes four of the eight
cell verdicts of benchmark_v0.2c: gantry mis-characterized vision (matches -> C
ahead), arm latching (C below -> matches) and latch_spread on both machines (C
ahead -> matches).

| Machine, suite | C | Best of D, E, F, H, I | p | Verdict |
|---|---|---|---|---|
| gantry, standard | 99.2% | F/I 96.3% | < 1e-6 | C ahead |
| gantry, latching good parts | 96.5% | F 98.5% | 0.012 | C below |
| gantry, mis-characterized vision | 87.6% | F/I 83.4% | 0.044 | C ahead |
| gantry, latch_spread good parts | 100.0% | I 99.8% | 1 | matches |
| arm, standard | 97.8% | F/I 96.1% | 4.5e-5 | C ahead |
| arm, latching good parts | 94.3% | F 93.7% | 0.64 | matches |
| arm, mis-characterized vision | 79.0% | F/I 79.4% | 0.92 | matches |
| arm, latch_spread good parts | 99.8% | H 99.7% | 1 | matches |

C's latch_spread lead is gone: with the same 35.2 N push and a re-push after a
failed pull, H and I match C on varied parts (gantry 597 and 599 against 600, arm
598 and 597 against 599). Bad parts passed: C, H and
I 0 of 2,200 each. Good-part trials passed as good when not seated: C 0 of 7,400,
H 118, I 161. C makes fewer good units per hour than I on every suite (gantry
standard 608 against 1,128). J, F's insertion followed by C's verification,
passed 3 such units, seats as many latching parts as I and fewer standard parts
than C, at 381-655 good units per hour on the standard suite against C's 386-608
(`HEADLINE_TABLES.md`). No multiple-comparison correction; the three verdicts at
0.01 <= p < 0.05 (the two above, and J below C on arm standard, p = 0.03) are being
re-checked on seed 20261124 with the same
code.

## What was tested

Connector insertion in MuJoCo on two machines, a gantry fixture and a UR5e arm
(MuJoCo Menagerie), with noisy vision, a 6-axis wrist force/torque sensor and
bounded actuators. Four suites per machine: 20 standard conditions
(displacement, rotation, tilt, vision noise, friction, tighter clearance) on a
housing-only 12 x 8 mm connector; a Molex Micro-Fit 3.0 with terminal and latch
forces, three good-part conditions and four deliberately bad parts; five
conditions where the camera is worse than the cell is told; and `latch_spread`,
good and bad Micro-Fit parts whose latch position, latch force and terminal
friction vary within or at the edge of the datasheet. 86,400 trials, paired
across controllers ([`PREREGISTRATION.md`](../results/benchmark_v0.2c/PREREGISTRATION.md)).

C was compared with the conventional cells an integrator would build: D,
force-controlled spiral search as cobot vendors ship it; E, vision correction on
a passive remote centre compliance (RCC) device; F, spiral search on the RCC
device; H and I, D and F with the same retention pull test as C. D, E and F were
tuned on development seeds for each machine, on the gantry with the latching
connector, by selection rules committed before the runs
([`v0.2c_arm_baselines`](../results/v0.2c_arm_baselines/REPORT.md),
[`v0.2c_gantry_baselines`](../results/v0.2c_gantry_baselines/REPORT.md)). G is C
plus a learned contact prior.

The v0.2d code, which benchmark_v0.2d ran, changes the method. The Micro-Fit's insert target is 35.2 N (1.1 x the datasheet's 32 N maximum
mating force) for every controller, up from 30 N; abort 40 N, protective stop 48 N
and damage 58 N are unchanged
([`v0.2d_force_budget`](../results/v0.2d_force_budget/REPORT.md)). A, B and E's
taught overtravel on the arm uses the stiffness along the push, 10.8 N/mm,
instead of the weakest direction, 8.0 N/mm
([`v0.2d_axial_stiffness`](../results/v0.2d_axial_stiffness/REPORT.md)). After a
failed pull, H and I push again at the insert target and pull once more, built
as C's proof push ([`v0.2d_pull_retry`](../results/v0.2d_pull_retry/REPORT.md)).
C's latching VERIFY, which G shares, has a tilt check
([`v0.2d_tilt_check`](../results/v0.2d_tilt_check/REPORT.md)). J is new: F's
insertion, then C's VERIFY, searching again after a failed check. J contains C's
VERIFY, so it is not a fair baseline
([`v0.2d_j_verify`](../results/v0.2d_j_verify/REPORT.md),
[`v0.2d_j_repick`](../results/v0.2d_j_repick/REPORT.md)).

## 1. Good parts seated, against the conventional cells

| Machine, suite | C | Best of D, E, F, H, I | McNemar p |
|---|---|---|---|
| gantry, standard | 99.0% | F/I 96.6% | < 1e-6 |
| gantry, latching good parts | 95.7% | F/I 99.2% | 4.9e-5 |
| gantry, mis-characterized vision | 85.8% | F/I 84.0% | 0.4 |
| gantry, latch_spread good parts | 100.0% | E 83.0% | < 1e-6 |
| arm, standard | 97.6% | F/I 96.4% | 0.0027 |
| arm, latching good parts | 93.7% | F 96.5% | 0.012 |
| arm, mis-characterized vision | 78.0% | F/I 78.8% | 0.78 |
| arm, latch_spread good parts | 99.5% | E 86.8% | < 1e-6 |

([`TABLES.md`](../results/benchmark_v0.2c/TABLES.md), last table)

C seats more housing-only connectors under the standard conditions on both
machines. F and I seat more latching good parts than C on both machines, and
match C when the camera is worse than believed (benchmark_v0.2c; see the v0.2d
table above for what changed).

In benchmark_v0.2c, C's latch_spread lead came mostly from one rule. When a plug
stalls short, C pushes at 1.1 x the datasheet's 32 N maximum mating force; the
conventional cells pushed at the connector file's 30 N insert target and seated
none of the 100 parts at maximum terminal friction on either machine. Without
that condition C still led (500 against 473 of 500 on the gantry, 497 against 474
on the arm, against I). A conventional cell with the same push was not in the run
([`REPORT.md`](../results/benchmark_v0.2c/REPORT.md#latch_spread-what-the-gap-is));
the v0.2d code gives every controller the 35.2 N insert target.

## 2. Bad units passed as good

**Deliberately bad parts** (half latched, broken latch, stubbed terminal, wrong
polarization, and three latch_spread defects; 1,100 per machine):

| | C | H | I | D | F |
|---|---|---|---|---|---|
| passed as good, of 2,200 | 0 | 0 | 0 | 1,174 | 1,468 |

C, and the conventional cells with the same pull test, passed none (Wilson 95%
upper bound 0.17%). Checkpoint 2's bad-part gap was the pull test, which a
conventional cell can run.

**Mis-seated good parts** (the part is good but ends short, tilted or offset,
and the cell calls it seated), all good-part trials, 3,700 per machine:

| | C | G | I | F |
|---|---|---|---|---|
| gantry | 0 | 0 | 67 | 183 |
| arm | 0 | 1 | 68 | 124 |

([`PAIRED_TABLES.md`](../results/benchmark_v0.2c/PAIRED_TABLES.md)). This is
where C's verification shows. I's escapes are plugs 11-15 mm deep (full depth
15 mm), up to 5 degrees of tilt, 102 of 132 of them under 2 mm of camera error;
its depth check accepts them. G's one escape is a plug at 3.21 degrees of tilt;
benchmark_v0.2c's VERIFY did not check tilt (the v0.2d code adds a tilt check to
the latching VERIFY).

## 3. Throughput

| Machine, suite | Good units/h, C / F / I | Median good cycle, C / F / I |
|---|---|---|
| gantry, standard | 606 / 1,101 / 1,101 | 5.30 / 2.43 / 2.43 s |
| gantry, latching good parts | 438 / 866 / 513 | 5.95 / 2.43 / 5.33 s |
| arm, standard | 373 / 596 / 596 | 8.14 / 4.77 / 4.77 s |
| arm, latching good parts | 282 / 515 / 334 | 8.70 / 4.58 / 8.25 s |

Good units per hour of simulated cell time, counting every cycle plus 60 s per
protective stop ([`TABLES.md`](../results/benchmark_v0.2c/TABLES.md)). I makes
more good units per hour than C on seven of eight suites. C rejects a
deliberately bad part in a median 8.4 s (gantry) and 12.8 s (arm) on the
latching suite.

## What this supports

- In simulation, C did not call a mis-seated connector good in 7,400 good-part
  trials (upper bound 0.05%), in benchmark_v0.2c and again in benchmark_v0.2d;
  the conventional cells with a pull test did so 118 (H) and 161 (I) times in
  benchmark_v0.2d.
- C seats more housing-only connectors under standard conditions than the
  conventional cells tested, on both machines, in both benchmarks.

## What this does not support yet

- That C rejects bad parts better than a conventional cell with a pull test.
- That C seats more latching parts, or handles part-to-part variation better,
  than a conventional cell given the same pull and the same push: in
  benchmark_v0.2d F beats C on gantry latching good parts and a conventional cell
  matches C on latch_spread on both machines.
- That C is cheaper per good unit. It is slower, and the cost of a mis-seated
  connector is not priced here.
- That C or J is the better product. J keeps most of C's protection against
  mis-seated units at about C's cycle; this run does not decide between them.
- Any hardware number. There is no rig yet; the latch model and its spread are
  assumed, and the arm is one simulated model whose servos may lag more than a
  real UR5e. Rig options and a test protocol are in
  [`hardware/BOM.md`](../hardware/BOM.md) and
  [`hardware/TEST_PROTOCOL.md`](../hardware/TEST_PROTOCOL.md).

## Robustness of the comparison (earlier code, gantry)

On 12 randomized simulators plus the nominal one (contact stiffness, damping,
solver softness, friction cone, servo stiffness), C led the best of D, E and F in
all 13, by 8.3 to 12.5 points
([`results/sim_randomization_v0.2`](../results/sim_randomization_v0.2/REPORT.md)).
That run used the code of benchmark_v0.2a, before the v0.2c baseline tuning; it
has not been repeated.
