# benchmark_v0.2b (Checkpoint 2): report

Pre-registered in [`PREREGISTRATION.md`](PREREGISTRATION.md) (commit 54f3097,
code frozen at 8e29f2e). Seed 20261102, two machines (gantry fixture and UR5e arm),
seven controllers, 54,600 paired trials. Every number below is in
[`TABLES.md`](TABLES.md) (`python -m experiments.checkpoint_report
results/benchmark_v0.2b`) or [`AUDIT_TABLES.md`](AUDIT_TABLES.md)
(`python -m experiments.cp2_audit results/benchmark_v0.2b`). All six
`config.json` files record commit 54f3097 and `git_dirty: false`. One run was
restarted after an external kill; see [`RUN_LOG.md`](RUN_LOG.md).

Simulation only. Not validated on hardware.

## Headline

The pre-registered rules put three results in the README headline:

1. **On the arm, the strongest conventional cell (F, spiral search on a
   compliance device) seats as many or more good units than C.** Standard
   conditions: F 96.3%, C 96.7% (p = 0.3, a match). Latching connector, good
   parts: F 95.2%, C 90.8% (F ahead, p = 0.0003). Camera worse than the cell
   believes: F 81.4%, C 75.4% (F ahead, p = 0.0018).
2. **On the gantry, with the camera worse than the cell believes, F matches C**
   (84.2% against 87.4%, p = 0.13), and in the combined worst case F seats 83
   of 100 against C's 56.
3. **C passed none of the 1,600 deliberately bad parts** (half-latched, broken
   latch, stubbed terminal, wrong polarization; 800 per machine, Wilson 95%
   upper bound 0.24% of bad parts). F passed 488 of 800 on the gantry and 574 of
   800 on the arm. The fair baseline with the fewest, D, passed 250 and 192.

C is ahead of every fair baseline on the gantry under the standard conditions
(99.1% against F's 97.0%, p < 1e-6) and on latching good parts (95.7% against
89.0%, p = 2.4e-6).

C is slower everywhere. Good units per hour of cell time, C against F: gantry
standard 608 against 862, gantry latching 476 against 527, arm standard 371
against 474, arm latching 289 against 458. Median successful cycle: gantry 5.30 s
against 3.54 s, arm 8.21 s against 6.50 s.

So the measured difference between C and the conventional cells is mostly
**what leaves the cell as good**, not how many units get seated. Whether that is
worth C's lower throughput depends on what a passed bad connector costs, which
this benchmark does not price.

**Read the bad-part and latching results with the post-run review below.** After
this run, an independent review found that only C and G run a retention pull
test (the baselines check depth only), that C's pull test is set from the
simulator's own assumed latch geometry, and that the gantry baselines were never
tuned with the latching connector. The numbers above are what was measured; the
section "After the run" says what they do and do not show.

## Success, bad units passed, throughput (all conditions per suite)

| Machine, suite | C success | Best fair baseline | p (C vs it) | Bad units passed, C / F | Good units/h, C / F | Rule outcome |
|---|---|---|---|---|---|---|
| gantry, standard (2,000 per controller) | 99.1% | F 97.0% | < 1e-6 | 0 / 42 | 608 / 862 | C ahead |
| gantry, latching good parts (600) | 95.7% | F 89.0% | 2.4e-6 | 0 / 3 | 476 / 527 | C ahead |
| gantry, mis-characterized vision (500) | 87.4% | F 84.2% | 0.13 | 0 / 47 | 342 / 454 | F matches C |
| arm, standard (2,000) | 96.7% | F 96.3% | 0.3 | 1 / 39 | 371 / 474 | F matches C |
| arm, latching good parts (600) | 90.8% | F 95.2% | 0.0003 | 0 / 5 | 289 / 458 | C below F |
| arm, mis-characterized vision (500) | 75.4% | F 81.4% | 0.0018 | 5 / 52 | 193 / 271 | C below F |

"Bad units passed" on these suites counts failed insertions that the cell did not
flag (no stop, no declared failure). Zero-count figures with their Wilson 95%
upper bounds: gantry standard 0 of 2,000 (<= 0.19%), gantry latching good parts
0 of 600 (<= 0.64%), gantry mis-characterized vision 0 of 500 (<= 0.76%), arm
latching good parts 0 of 600 (<= 0.64%).

## Deliberately bad parts (latching suite, 200 of each per machine)

| Machine | Defect | C | G | D | F |
|---|---|---|---|---|---|
| gantry | half latched | 0 | 0 | 81 | 120 |
| gantry | broken latch | 0 | 0 | 132 | 197 |
| gantry | stubbed terminal | 0 | 0 | 37 | 171 |
| gantry | wrong polarization | 0 | 0 | 0 | 0 |
| arm | half latched | 0 | 0 | 44 | 200 |
| arm | broken latch | 0 | 0 | 134 | 200 |
| arm | stubbed terminal | 0 | 0 | 14 | 174 |
| arm | wrong polarization | 0 | 0 | 0 | 0 |
| both | all four, passed as good | **0 of 1,600 (<= 0.24%)** | 0 of 1,600 | 442 | 1,062 |

C against the fair baseline with the fewest escapes (D): exact McNemar p < 1e-6 on
both machines.

How C rejects them is slow. It has no "this part is defective" verdict; it runs
out of time or retries. Median cycle on a bad part: 25.9 s on the gantry, 26.4 s
on the arm, against 5-8 s for a good part. On the gantry, 60 of C's 200
half-latched parts ended in a protective stop (retracting against the latch after
a failed check), each a cell reset. F spends 5.3 s per bad part on the arm and
passes most of them.

## Where C loses

- **Arm, latching good parts.** All of C's 54 losses are on `mf_noise_1mm`
  (146 of 200 against F's 172): 19 protective stops, 19 time limits, 16 retry
  limits. The other two good-part conditions are level (200 and 199 of 200 for
  both).
- **Arm and gantry, mis-characterized vision.** The gap is
  `heldout_worst_case` (friction 0.8, 0.2 mm clearance, camera twice as noisy as
  C is told): gantry F 83, C 56; arm F 78, C 34. C ran out of retries on 43 of
  the 100 gantry trials. F's search has no retry budget, so it keeps going until
  the time limit. On the other four held-out families C is level with F or ahead.
- **Speed.** See the throughput figures above. C spends the time on wall probes
  and on its latch push-click-pull check.

## The bad units C and G did pass (audit)

On the good-part conditions C passed 6 bad units in 6,200 trials and G passed 9.
`AUDIT_TABLES.md` lists every one with its final pose and the controller's own
seat and verify events. There are two failure modes:

1. **The arm's wall-geometry yaw check has no effect at 0.2 mm clearance**
   (5 of C's 6, 7 of G's 9, all `heldout_worst_case` on the arm). The plug stuck
   0.5-1.5 mm short of full depth (true depth 13.00-14.47 mm against the required
   14.5 mm) and C took the stop as a seat (insert timeout or bottoming at a
   measured 12.85-15.36 mm; the seat threshold is 15 - 1 - 2.5 sigma mm, 12.75 mm
   when sigma is the 0.5 mm vision sigma C is told).
   On the arm, VERIFY checks yaw from the free travel between two wall contacts
   (added in W5b because the arm cannot sweep yaw in time). With 0.2 mm
   clearance a plug yawed 2 degrees does not fit at all, so the travel the check
   requires is negative (-0.007 mm), and the measured travel of a wedged plug,
   0.000 mm, passes. The check never fails in that cavity. C passed through this
   path 139 times on the arm (`AUDIT_TABLES.md`, second table); most of those
   plugs were seated. The gantry sweeps yaw and passed no unit this way.
2. **Tilt just over 3 degrees** (1 of C's, 2 of G's: arm `noise_2mm`, gantry
   `noise_2mm` and `heldout_mischar_2mm`). Fully inserted, yaw within 0.5 degrees,
   tilt 3.00-3.61 degrees against the 3.0 degree limit. The wall probes passed;
   they do not measure tilt directly.

Both are development items for v0.2c. The first was found here, on the
reported seed, so any fix must be tested on a seed that has not been run.

## G (learned contact prior) against C

| Machine, suite | C | G | C-only / G-only | p | Rule outcome |
|---|---|---|---|---|---|
| gantry, standard | 99.1% | 99.5% | 5 / 13 | 0.096 | no measurable gain |
| gantry, latching good parts | 95.7% | 98.5% | 6 / 23 | 0.0023 | G helps |
| gantry, mis-characterized vision | 87.4% | 90.8% | 17 / 34 | 0.024 | G helps |
| arm, standard | 96.7% | 97.5% | 6 / 23 | 0.0023 | G helps |
| arm, latching good parts | 90.8% | 92.8% | 10 / 22 | 0.0501 | no measurable gain |
| arm, mis-characterized vision | 75.4% | 78.8% | 10 / 27 | 0.0076 | G helps |

G helps on four of six suites and is never worse. It does not close the gap to F
on the arm (latching 92.8% against 95.2%, mis-characterized vision 78.8% against
81.4%). As stated in advance, G raises protective stops on wrong-polarization
parts: gantry 2 to 34 of 200, arm 1 to 4. G passed 9 bad units against C's 6;
all of G's are in the two failure modes above.

## Other controllers

- **A (fixed program) and B (vision correction)** are reported for continuity.
  A passed 235 bad units on the gantry standard suite.
- **E (B on a compliance device)** reaches the 30 N protective stop in 9% of
  standard trials on both machines.
- **D (spiral search)** seats only 56.7% (gantry) and 55.3% (arm) of latching good
  parts; 228 of its 260 gantry failures and 223 of 268 arm failures are time
  limits. Its settings were chosen on the housing-only connector by the W1
  ranking rule; it got no latching-specific tuning.

## Fairness

- On the arm, C's rules were diagnosed and set by hand on dev seed 2026 (W5b),
  and G has an arm-trained model. D, E and F got no arm-specific work. The
  comparison favours C and G, and F still matches or beats C on the arm.
- On the gantry, D, E and F were tuned on the development seed with more effort
  than C got (`results/benchmark_v0.2a/BASELINE_TUNING.md`); D now uses the
  setting the W1 rule selects.
- The mis-characterized-vision families were first run on seed 20261109, and C's
  yaw re-centring (W4) was developed after that run. They are reported as
  robustness conditions, not as held out.

## After the run: review findings (not pre-registered)

Found by the v0.2c reviews and checked on dev seeds; none of this changes a
pre-registered number, it changes what they can be taken to mean.

1. **The bad-part gap measures having a pull test.** C and G finish a latching
   insertion with a guarded pull at half the rated retention force. D, E and F
   check depth only (`defex/control/spiral_search.py`, `baselines.py`); none was
   given a pull test, which a conventional integrator could add. So "C 0 of 1,600,
   F 1,062" compares a cell with a retention test against cells without one. A
   baseline with a pull test has not been measured.
2. **C's pull test depends on the assumed latch geometry.** It passes only if the
   plug moves at most the model's 0.5 mm post-snap stroke plus 0.3 mm. That 0.5 mm
   is listed as assumed in `assets/connectors/microfit3_4ckt.json` and is the value
   the simulator builds every part with. With the simulated latch engaging 0.15 mm
   earlier (controller unchanged), C seats 4 of 60 good parts on the gantry
   (54 as modelled) and 30 of 60 on the arm (52); F is unaffected (53, 57). A snap
   0.1 mm early, 0.2 mm late, or a latch peak force x0.5 or x1.5 changes nothing
   ([`results/v0.2b_latch_spread`](../v0.2b_latch_spread/REPORT.md), dev seed 2027,
   confirming the review's seed-2026 result).
3. **C's "click" check does not detect the latch.** Its window contains the 8 N
   terminal-friction drop on every part, so it passes on broken-latch parts too;
   bad parts are rejected by the pull test alone.
4. **The latching results hold only for the modelled terminal friction.** At the
   datasheet's maximum (8 N per circuit, 32 N for four), no controller seats a
   good part: every insert budget is 30 N.
5. **The gantry baselines were never tuned with the latching connector.** W1
   predates it. Re-tuned with the same protocol the arm got, F seats 60 of 60
   latching good parts on dev seed 2027 against C's 54 (p = 0.031), and D 51
   against 29 before (`v0.2c/gantry-baselines`,
   `results/v0.2c_gantry_baselines/REPORT.md`). So C's gantry latching lead above
   (95.7% against 89.0%) reflects untuned baselines more than C.
6. **Seat tilt is not checked on either machine.** The tilt escapes above are not
   arm-specific; the gantry training data has one more (v0.2c integration review).

What still holds: C seats more units than F on the gantry under the standard
conditions with honest vision (99.1% against 97.0%; against the re-tuned F on dev
seed 2027, 198 against 193 of 200, p = 0.062), and in no tested spread did C or G
pass a bad part.

## Known limits

- Simulation only. The latch model is partly assumed (`results/w3_development/`);
  there is no measured force-depth curve yet.
- One latching connector family and one arm model. Menagerie's UR5e servo lags
  0.2 s, possibly more than a real UR5e under servoj.
- No cost model for a passed bad unit, so no single "better cell" verdict.

## Reproduce

```
for B in gantry arm; do
  for S in standard:100 latching:200 heldout:100; do
    python -m experiments.robustness --suite ${S%%:*} --backend $B --trials ${S##*:} \
      --seed 20261102 --workers 9 --name benchmark_v0.2b/${B}_${S%%:*} \
      --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
  done
done
python -m experiments.checkpoint_report results/benchmark_v0.2b > results/benchmark_v0.2b/TABLES.md
python -m experiments.cp2_audit results/benchmark_v0.2b > results/benchmark_v0.2b/AUDIT_TABLES.md
```
