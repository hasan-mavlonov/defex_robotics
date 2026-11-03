# DAIE technical brief (draft for Hasan's review)

Simulation results for the Defex Adaptive Insertion Engine (controller C). Not
validated on hardware. Every number names its file. POST HOC marks an analysis chosen
after the results were seen; it explains the pre-registered verdicts and does not
replace them. No p-value is pooled across seeds or corrected for multiple comparisons.
The pitch is Hasan's decision, and the stop condition holds: a fair baseline matches or
beats C on 6 of the 8 benchmark_v0.2e cells.

Sources:
- benchmark_v0.2e: seed 20261130, code ddd0d34, 96,000 trials,
  [`REPORT.md`](../results/benchmark_v0.2e/REPORT.md).
- Two earlier seeds on the v0.2d code (42df5c8): benchmark_v0.2d (20261123) and
  benchmark_v0.2d_rep (20261124).
- The evidence analysis of all three:
  [`v0.2f_evidence/REPORT.md`](../results/v0.2f_evidence/REPORT.md).
- heldout2: seed 20261207, the same ddd0d34 controllers, 8,000 trials,
  [`heldout2_v0.2f/REPORT.md`](../results/heldout2_v0.2f/REPORT.md).

## What was tested

Connector insertion in MuJoCo on a gantry fixture and a UR5e arm model, with noisy
vision, a 6-axis wrist F/T sensor and bounded actuators. Four suites per machine:
- `standard`: 20 conditions on a housing-only 12 x 8 mm part.
- `latching`: a Molex Micro-Fit 3.0, with 3 good-part conditions and 4 deliberately bad
  parts.
- `heldout`: five families where the camera is worse than the cell is told. They were
  used in W4 development, so they are no longer out of sample.
- `latch_spread`: good and bad Micro-Fit parts with varied latch and terminal forces.

Fair baselines: D (spiral search), E (vision correction on an RCC), F (spiral on an
RCC), and H and I (D and F with C's retention pull). Every controller pushes the
Micro-Fit to 35.2 N. G is C plus a learned contact prior. J is F's insertion followed by
C's VERIFY. J contains C's VERIFY, so it is not a fair baseline.

## 1. Pre-registered verdicts on three seeds

| Machine, suite | 20261123 (v0.2d) | 20261124 (v0.2d) | 20261130 (v0.2e): C vs best fair |
|---|---|---|---|
| gantry, standard | C ahead | C ahead | 99.1% vs F/I 96.8%, p < 1e-6, C ahead |
| gantry, latching good parts | C below F, p = 0.012 | C below F, p = 0.0026 | 97.5% vs F 98.8%, p = 0.12, matches |
| gantry, heldout | C ahead, p = 0.044 | matches | 81.4% vs 83.8%, p = 0.29, matches |
| gantry, latch_spread good parts | matches | matches | 100% vs I 100%, matches |
| arm, standard | C ahead | C ahead | 98.1% vs F/I 96.2%, p = 5.9e-6, C ahead |
| arm, latching good parts | matches | matches | 92.0% vs F 95.2%, p = 0.014, C below F |
| arm, heldout | matches | matches | 76.8% vs 78.4%, p = 0.51, matches |
| arm, latch_spread good parts | matches | matches | 99.5% vs I 99.8%, matches |

([`benchmark_v0.2e/REPORT.md`](../results/benchmark_v0.2e/REPORT.md)). C is ahead on
all three seeds only on `standard`. C's drop on gantry heldout and arm latching on
seed 20261130 comes from the seed, not the v0.2e fixes: the same trials, rerun on the
v0.2d code, gave identical rows
([`v0.2e_postrun_check`](../results/v0.2e_postrun_check/REPORT.md); that check was
not pre-registered).

## 2. Where C's standard lead comes from (POST HOC)

- On every seed, the trials that C seats and I does not are almost all in three
  high-camera-error conditions: noise_1mm, noise_2mm (camera sigma 1 and 2 mm) and
  generalization_combined (0.8 mm sigma plus a 0.8 mm bias). Gantry: 60 of 60, 62 of
  62, 53 of 53. Arm: 49 of 51, 49 of 51, 53 of 54
  ([`CONCENTRATION.md`](../results/v0.2f_evidence/CONCENTRATION.md) (b)).
- In the nominal (0.3 mm), noise_0mm and noise_0.5mm conditions, C and I seat exactly
  the same trials on every seed and both machines
  ([`PERCOND.md`](../results/v0.2f_evidence/PERCOND.md)).
- More than half of C's wins are I's bad units: I declared success on a plug that was
  out of tolerance (seed 20261130: 30 of 53 gantry, 30 of 54 arm).
- I seats more than C on all three seeds in four places: heldout_worst_case, the
  1.5 mm hand-eye bias (both machines), arm friction_1, and gantry latching
  mf_noise_1mm. C runs out of retries or time there, or hits a protective stop.

## 3. Bad units, and what the zero rests on

Good-part trials passed as good when not seated, of 7,400 per seed
([`BAD_UNITS.md`](../results/v0.2f_evidence/BAD_UNITS.md) (a)):

| | C | G | J | H | I | F |
|---|---|---|---|---|---|---|
| 20261123 / 20261124 / 20261130 | 0 / 0 / 0 | 0 / 0 / 1 | 3 / 2 / 2 | 118 / 112 / 101 | 161 / 138 / 138 | 197 / 176 / 178 |

Deliberately bad parts passed, of 2,200 per seed: C, G, H, I and J 0 on every seed;
D 1,275-1,287 and F 1,504-1,510. Rejecting bad parts is the pull test's work, and H and
I have it too.

What C's zero rests on:
- **C's VERIFY, not C's insertion.** J is F's insertion plus C's VERIFY. J passed 3, 2
  and 2 bad units where F passed 197, 176 and 178. On housing-only parts VERIFY squares
  the plug to the floor and centres its yaw. No fair baseline has a seat-and-align step;
  that is an open fairness item.
- **An assumed 3 deg spec.** I's bad units on seed 20261130 sit just past it: gantry
  standard 32 plugs, 14.38-14.98 mm deep, 3.00-5.53 deg in yaw or tilt. A POST HOC
  rescoring of seed 20261130 only, from an exact replay (6,000 rows, identical to the
  benchmark), allowed looser and tighter limits
  ([`TOLERANCE.md`](../results/v0.2f_evidence/TOLERANCE.md)):

  | POST HOC, seed 20261130 | 2 deg | 3 deg (as run) | 4 deg | 5 deg |
  |---|---|---|---|---|
  | gantry standard, C-only / I-only | 122 / 2 | 53 / 8 | 31 / 10 (p = 0.0015) | 26 / 10 (p = 0.011) |
  | arm standard, C-only / I-only | 119 / 7 | 54 / 16 | 30 / 17 (p = 0.079) | 27 / 18 (p = 0.23) |
  | I's bad units, gantry / arm standard | 110 / 107 | 32 / 32 | 8 / 7 | 3 / 3 |
  | C's bad units, gantry / arm standard | 3 / 1 | 0 / 0 | 0 / 0 | 0 / 0 |

- **A constant F/T bias.** In heldout2 the F/T zero drifts. C passed 8 bad units on the
  arm at 0.3 N/s; H passed 0 and I 1 (section 4). A POST HOC trace found the cause.
  VERIFY holds a 1 N preload on the *read* axial force. Once the zero has drifted more
  than 1 N in the push-out direction, that preload is about 0 N or a pull in truth.
  The seated plug then rises 0.6-1.8 mm, and nothing re-checks depth before SUCCESS
  ([`v0.2f_h2_diagnosis/REPORT.md`](../results/v0.2f_h2_diagnosis/REPORT.md)). In
  standard and latching the bias is constant and tared out, so this cannot happen
  there. Part of C's zero comes from that simulator assumption, not from C.
- **The latching tilt check.** G's one bad unit (seed 20261130) was a latched plug at
  3.01 deg tilt that the tilt check passed. J's arm latching bad unit came from a first
  latch check with an empty tilt window.
  Tilt check, POST HOC diagnosis (`results/v0.2f_tilt_diagnosis/REPORT.md`, development seeds 2026/2027): the latching tilt check compares the plug with C's own socket-axis estimate, the axis C aimed it along, so it cannot see tilt that comes from an error in that estimate. G's 3.01 deg unit is this case (estimate 2.87 deg off the true axis after a wrong 'flat' fold). On the development seeds 234 of 8,320 C/G verdicts read more than 1 deg under the true tilt; none became a bad unit. What keeps tilted bad units rare is the Micro-Fit cavity, which stops a latched plug at about 3.2 deg, and a camera tilt error rarely over 3 deg. Near misses (declared, 2.5-3.0 deg) were 5 in about 3,540 declared latching trials. J's empty first tilt window comes from its hand-over code and cannot happen to C. On the gantry the housing-only VERIFY has no yaw check (its sweep always ends in SUCCESS); on the arm the wall-yaw check bounds |yaw| at 2.0 deg. Two default-off options (push below the force floor; J's hand-over window) passed a no-harm rule on validation seed 4007 but changed no outcome; whether to use them is Hasan's call.

## 4. heldout2: a clean held-out test

Five new families, two levels each, on nominal vision. No one had developed against
them. They were pre-registered before the run
([`PREREGISTRATION.md`](../results/heldout2_v0.2f/PREREGISTRATION.md)). Each family
cell has 80 paired trials:

| Family | gantry: C vs best fair | arm: C vs best fair |
|---|---|---|
| unseen receptacle tilt (2, 3 deg) | 100% vs E 92.5%, p = 0.031, C ahead | 100% vs E 85.0%, p = 0.00049, C ahead |
| unseen receptacle yaw (2.5, 4 deg) | 100% vs D 37.5%, p < 1e-6, C ahead | 97.5% vs F 37.5%, p < 1e-6, C ahead |
| F/T drift (0.1, 0.3 N/s) | 100% vs D 100%, matches | 76.2% vs D 100%, p = 3.8e-6, **C below** |
| Micro-Fit tighter than drawn | 95.0% vs F 88.8%, p = 0.12, matches | 93.8% vs F 80.0%, p = 0.0034, C ahead |
| Micro-Fit unseen grasp offset | 75.0% vs F 98.8%, p = 3.8e-6, **C below** | 76.2% vs F 95.0%, p = 0.00073, **C below** |

C is ahead in 5 of 10 cells, matched in 2 and below in 3. The pre-registered
expectation ("matches in most cells") was wrong.
- Unseen tilt and yaw: F's and I's plugs go to full depth still rotated. J seats
  96-100% there, so most of C's lead likely comes from C's VERIFY (POST HOC).
- Unseen grasp offset: a POST HOC trace found that the offset moves C's
  centre-of-pressure reference 0.8 mm. A plug resting on one edge then reads as jammed
  inside the cavity. C's jam branch retries from the same probe until the retry or
  time limit. F's spiral does not use the centre of pressure and finds the hole.

G gave no measurable gain in any cell. One seed and 40 trials per condition, so a
"matches" verdict is weak evidence of equality.

## 5. Throughput

C makes fewer good units per hour than F and I on every cell of benchmark_v0.2e.
On gantry standard it makes 601 against 1,100, with a median successful cycle of
5.30 s against 2.43 s. On arm standard it is 387 against 593, and 8.15 s against 4.77 s
([`HEADLINE_TABLES.md`](../results/benchmark_v0.2e/HEADLINE_TABLES.md) (c)).

POST HOC phase split, seed 20261130
([`PHASES.md`](../results/v0.2f_evidence/PHASES.md)):
- VERIFY costs C 1.89 s (gantry) and 2.49 s (arm) per success on the housing-only part.
  On the gantry that is about two-thirds of C's 2.94 s over F.
- On latching parts, I's pull test costs 3.04 s and 3.93 s, the same as C's latch
  check.
- C's p95 is 1.63 x its median on gantry standard, against a 1.5 target. The slow tail
  is C's retries, which sit in the same high-camera-error trials. Over the successes
  that did not retry, p95 / median is 1.11.

## 6. Rig plan

Nothing has been bought and no vendor contacted.
- [`hardware/TEST_PROTOCOL.md`](../hardware/TEST_PROTOCOL.md) fixes the rig test. It
  runs C, I, J and F (plus A, optionally H) on a housing-only part and a Micro-Fit 3.0,
  with a jig that sets the socket's x, y, yaw and tilt. It also measures the final plug
  pose, because most baseline bad units are full-depth plugs just over 3 deg.
- [`hardware/RIG_POWER.md`](../hardware/RIG_POWER.md) sets the trial counts.
  On the housing-only part, at the simulated rates, C against I needs 70-100 paired
  trials in all for 80% power on success, and 90-100 on bad units. The protocol uses
  100 per condition, 400 per controller. On Micro-Fit good parts it would take
  780-1,200 pairs (gantry) and 7,800 or more (arm). The rig therefore reports rates
  only there and makes no between-controller claim.
- Frozen simulation predictions for those conditions: seed 20261201, code ddd0d34,
  [`v0.2f_rig_predictions/REPORT.md`](../results/v0.2f_rig_predictions/REPORT.md).
  At 100 trials per condition (extension on the same commit; trials 0-49 identical), housing-only C seats 387/400 against F/I 336/400 on the gantry and 370/400 against 329/400 on the arm. Its bad units are 0/400 against 33/400 and 39/400. On gantry Micro-Fit good parts C is predicted below F (284 against 297 of 300, p = 0.00024). Arm Micro-Fit good parts: no difference (p = 0.20-0.36). The rule for judging
  a rig result against these predictions is fixed there.
- The latch-model fitter for rig curves
  ([`v0.2f_latch_fit/REPORT.md`](../results/v0.2f_latch_fit/REPORT.md)) recovers 13
  of 14 quantities on synthetic curves. It fails its own rule on hook stiffness (6 of
  10 off-nominal parts, the rule needs 8). It has not seen a real curve.

## What this supports (simulation, with its scope)

- On `standard`, C seats more housing-only parts than every fair baseline, on both
  machines and all three seeds. Scope: the lead sits in the conditions with camera sigma
  1-2 mm or the combined condition. In nominal, noise_0mm and noise_0.5mm (sigma 0.3, 0
  and 0.5 mm), C and I seat exactly the same trials. It shrinks under a looser seating
  spec (POST HOC, one seed). Across 12 randomized simulators it holds on the gantry,
  and narrowly on the arm (10 of 12 against F and I).
- C passed no bad unit in 7,400 good-part trials on each of three seeds. Scope: this
  rests on C's VERIFY (J has the same edge), on the assumed 3 deg spec, and on a
  constant, tared-out F/T bias. Under F/T drift on the arm (heldout2), C passed 8.
  Across 12 randomized simulators it passed 1 per machine, still fewer than F, H and I
  in every variant.
- On heldout2, C seats more than every fair baseline on unseen receptacle tilt and yaw,
  on both machines. Scope: one seed. J matches C there, so VERIFY likely carries it.

## What this does not support yet

- That C rejects bad parts better than a fair cell with a pull test: H and I pass 0 of
  2,200, as C does.
- That C seats more latching parts or handles part-to-part variation better.
- That C copes better with a camera worse than told, an unseen grasp offset or F/T
  drift. A fair baseline matches or beats it there.
- That C's results hold on every contact model on the arm: under the pyramidal
  friction cone C fails friction_1 (above).
- That C is cheaper per good unit. It is slower, and a passed bad unit is not priced.
- That C or J is the better product. These runs do not decide it.
- Any hardware number.

## Robustness across simulators

[`sim_randomization_v0.2f`](../results/sim_randomization_v0.2f/REPORT.md) is
pre-registered. Seed 20261205, controllers unchanged since ddd0d34, 12 randomized
MuJoCo simulators plus the nominal one per machine, C, F, H, I, J and G (G pinned to
its nominal model, a configuration of this run), 26,052 trials. Counts are randomized
variants keeping benchmark_v0.2e's verdict, of 12; 10 are needed
([`TABLES.md`](../results/sim_randomization_v0.2f/TABLES.md)).
- **Gantry:** 29 of 29 primary comparisons hold, including C's success lead in the
  high-camera-error conditions and its bad-unit lead (12 of 12 against F, H and I).
- **Arm:** 24 of 29 hold.
  - The high-camera-error lead holds narrowly: 10 of 12 against F and I, pooled 8 / 7,
    not significant.
  - Neutral success, C against F, H and I, does not hold (6 of 12; pooled C worse,
    0 / 15, p = 6.1e-05). POST HOC split: the 6 failing variants are the 6 with the
    pyramidal friction cone. On friction_1 there C seats 1 of 90 against 89-90 of 90.
    Cause (POST HOC, `results/v0.2f_friction_diagnosis/REPORT.md`): C seats the part correctly, then VERIFY rejects it. At mu = 1 the floor friction under the 1 N preload reaches the wall probe's 2 N stop before the plug meets a wall, so the wall-yaw check reads too little free travel; recovery repeats the same probe until the time limit. Under the pyramidal cone MuJoCo ignores the repo's 20 ms friction time constant (solreffriction); setting only that to 2 ms on the nominal elliptic arm gives the same failure. MuJoCo's documentation calls the elliptic cone the closer model. On the nominal arm, C's 18 friction_1 losses over three seeds are 6 of these wall-probe stalls, 11 torque protective stops at 0.61-0.71 N m (limit 0.6) and 1 mouth stall. J (same VERIFY on F's RCC stage) seated 300 of 300. A rig test of C's wall probe at C's preload settles whether it transfers.
  - Latching good parts, C below F, does not hold per simulator (9 of 12). Pooled, C is
    still below F (p = 0.038). C against I is not resolved (low power).
- **Bad units:** C passed 1 per machine, both in variant 10 (gantry: a seated plug
  over-penetrated; arm: a latched plug at 3.11 deg). Gantry C 1, H 73, I 75, F 75 of
  1,820; arm C 1, H 30, I 56, F 59 of 2,210. C passes fewer than F, H and I in all 12
  variants on both machines.

The earlier randomization
([`sim_randomization_v0.2`](../results/sim_randomization_v0.2/REPORT.md)) used the
v0.2a code (fe48eca) on the gantry only. Its "C leads in all 13" is not repeated in
that form.
