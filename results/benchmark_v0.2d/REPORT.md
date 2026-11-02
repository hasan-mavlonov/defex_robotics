# benchmark_v0.2d report

Seed 20261123, code 42df5c8 (run from 966a5f5, which adds only the pre-registration),
96,000 trials, all ten controllers on the gantry and the UR5e arm. Run details in
`RUN_LOG.md`. Every number below comes from `TABLES.md`, `PAIRED_TABLES.md`,
`AUDIT_TABLES.md` or `HEADLINE_TABLES.md` in this folder, made from the per-trial rows
with the pre-registered commands. Simulation only.

## Result in one paragraph

C is ahead of every fair baseline (D, E, F, H, I) on 3 of 8 cells: gantry standard,
arm standard and gantry mis-characterized vision (the last at p = 0.044). A fair baseline
matches C on 4 cells (arm latching, arm mis-characterized vision, latch_spread on both
machines). On gantry latching good parts C is below F (96.5% vs 98.5%, p = 0.012). No
controller with a pull test or C's VERIFY (C, G, H, I, J) passed a deliberately bad part:
0 of 2,200 each. On good-part trials C passed no bad units while H and I passed 18-48 per
housing-only cell (p <= 7.6e-6 in every such cell). C is the slowest of the competitive
controllers: on gantry standard 608 good units per hour against F and I's 1,128. The
stop condition holds: a fair baseline matches or beats C in 5 of 8 cells. Hasan decides
how the pitch changes.

## Pre-registered verdicts

C against the best fair baseline (metric 1; `TABLES.md`, "Pre-registered decision
rules, applied"):

| Machine, suite | C | Best fair baseline | C-only / other-only | p | Verdict |
|---|---|---|---|---|---|
| gantry, standard | 99.2% | F 96.3% | 60 / 2 | < 1e-6 | C ahead |
| gantry, latching good parts | 96.5% | F 98.5% | 4 / 16 | 0.012 * | **C below F** |
| gantry, mis-characterized vision | 87.6% | F 83.4% | 60 / 39 | 0.044 * | C ahead |
| gantry, latch_spread good parts | 100.0% | I 99.8% | 1 / 0 | 1 | **a fair baseline matches C** |
| arm, standard | 97.8% | F 96.1% | 51 / 17 | 4.5e-5 | C ahead |
| arm, latching good parts | 94.3% | F 93.7% | 23 / 19 | 0.64 | **a fair baseline matches C** |
| arm, mis-characterized vision | 79.0% | F 79.4% | 50 / 52 | 0.92 | **a fair baseline matches C** |
| arm, latch_spread good parts | 99.8% | H 99.7% | 1 / 0 | 1 | **a fair baseline matches C** |

\* 0.01 <= p < 0.05. There is no multiple-comparison correction (about 60 tests in
`TABLES.md`, about 40 in `PAIRED_TABLES.md`); these two verdicts are the ones most
likely to change on another seed. `benchmark_v0.2d_rep` (seed 20261124, same code) was
pre-registered to check this.

Part-to-part variation (`latch_spread`, good parts): a fair baseline matches C on both
machines. C's lead there in benchmark_v0.2c (C 100.0% and 99.5% vs 78.8-86.8% for the fair
baselines) is gone. The 35.2 N insert target, applied to every controller, and the H/I
pull retry closed it (`HEADLINE_TABLES.md` section (d): F 79.0% -> 99.2% gantry,
79.0% -> 94.5% arm; I 78.8% -> 99.8% and 79.0% -> 99.5%). The two runs use different
seeds and are not paired.

Deliberately bad parts passed (metric 2): C, G, H, I and J 0 of 800 on each machine's
latching suite and 0 of 300 on each latch_spread suite, 0 of 2,200 each in all (Wilson 95%
upper bound 0.17%). No difference between C and H or I. Without a pull test D and F pass
most bad parts (gantry latching D 399, F 510 of 800; arm D 376, F 473). The headline
script prints a p for the pooled row; pooled totals get no test under the
pre-registration, so it is not used.

Bad units on good-part trials, C against H and I (metric 5, `PAIRED_TABLES.md`):

| Cell | C | H | I | p, C vs H / C vs I |
|---|---|---|---|---|
| gantry standard (2,000 trials) | 0 | 37 | 48 | 1.5e-11 / 7.1e-15 |
| gantry mis-characterized vision (500) | 0 | 28 | 39 | 7.5e-9 / 3.6e-12 |
| arm standard (2,000) | 0 | 35 | 43 | 5.8e-11 / 2.3e-13 |
| arm mis-characterized vision (500) | 0 | 18 | 31 | 7.6e-6 / 9.3e-10 |
| latching and latch_spread good parts, both machines | 0 | 0 | 0 | 1 |

C passes fewer than H and I on every housing-only cell. All of I's are seat declarations
ground truth calls unseated (`false_accept`), at 11.7-15.0 mm depth with up to 5.0 deg
tilt, mostly on `noise_2mm` and `heldout_mischar_2mm` (`PAIRED_TABLES.md`, last table).
On the latching suites the pull test catches these and no one passes any.

G against C (metric 3): G helps on 4 cells, gantry standard (p = 0.0063), gantry
mis-characterized vision (p = 0.00016), arm latching (p = 0.00012) and arm
mis-characterized vision (p < 1e-6); no measurable gain on the other 4. G passed no bad
unit. In the dev check G had helped only on gantry heldout.

J against C and against I (metric 4):

| Cell | J vs C, seated | J vs I, seated | J's bad units vs C / vs I |
|---|---|---|---|
| gantry, standard | below (98.0% vs 99.2%, p = 0.00012) | ahead (98.0% vs 96.3%, p = 7.7e-6) | 1 vs 0, n.s. / 1 vs 48, fewer |
| gantry, latching | matches (p = 0.093) | matches (identical) | 0 vs 0 / 0 vs 0 |
| gantry, mis-characterized vision | matches (p = 0.38) | ahead (89.4% vs 83.4%, p = 1.5e-5) | 2 vs 0, n.s. / 2 vs 39, fewer |
| gantry, latch_spread | matches | matches | 0 / 0 |
| arm, standard | below (97.0% vs 97.8%, p = 0.03 *) | ahead (p = 0.0095) | 0 vs 0 / 0 vs 43, fewer |
| arm, latching | matches (p = 0.43) | matches (identical) | 0 / 0 |
| arm, mis-characterized vision | matches (p = 0.58) | matches (p = 0.28) | 0 vs 0 / 0 vs 31, fewer |
| arm, latch_spread | matches (p = 0.5) | matches (identical) | 0 / 0 |

On the latching suites J's seated results are trial for trial the same as I's: F's
insertion decides, and VERIFY and the pull reject the same parts. On housing-only parts J
keeps nearly all of C's protection against bad units (3 against I's 87 on the gantry, 0
against 74 on the arm) and seats fewer than C on `standard`. J passed no deliberately
bad part. J's three bad units (`AUDIT_TABLES.md`) are at full depth (15.00 mm) and under
0.01 deg tilt (gantry `heldout_worst_case` trials 28 and 46, `friction_1` trial 13);
ground truth failed them on its final-state check, and `trials.csv` does not record
which part of that check. Whether J or C would be the product is not decided by this run.

## Cycle time and throughput

Median successful cycle and good units per hour (0 s / 60 s per protective stop),
`HEADLINE_TABLES.md` section (c):

| Cell | C | J | I | F |
|---|---|---|---|---|
| gantry, standard | 5.30 s, 608 | 4.77 s, 655 | 2.43 s, 1,128 | 2.43 s, 1,128 |
| gantry, latching good parts | 6.16 s, 438 | 5.47 s, 494 | 5.47 s, 494 / 474 | 2.40 s, 854 |
| arm, standard | 8.14 s, 386 / 374 | 7.98 s, 381 | 4.77 s, 593 | 4.77 s, 593 |
| arm, latching good parts | 9.00 s, 289 / 287 | 8.63 s, 311 / 303 | 8.55 s, 313 / 299 | 4.68 s, 474 / 454 |

On housing-only parts C and J take about twice F and I's cycle. On latching parts J,
I and H take about C's cycle; F is about twice as fast as all of them and passes most
bad parts. Protective stops on gantry bad parts: J 129 of 800, F and I 74, C 33, G 34
(`TABLES.md`, gantry latching); none of C, F, I or J stopped on arm bad parts (latching and latch_spread). Bad-part
stops do not enter good units per hour.

## Against what development predicted (pre-registration, "Expected from development")

- Housing-only cells: C ahead on `standard` as expected. C ahead on gantry
  mis-characterized vision (p = 0.044) was not expected (dev check: p = 0.38). Arm
  mis-characterized vision matched, as expected.
- latch_spread: matched on both machines, as expected.
- Latching good parts: F matches or beats C, as expected; on the gantry it beats C.
- Bad parts: C, G, H, I and J passed none, as expected.
- Bad units on good parts: C 0, as expected. J 3 on the gantry and 0 on the arm ("a few,
  far fewer than I"), as expected.
- J below C on gantry standard, as expected. J below C on arm standard (p = 0.03) was
  not seen in development.
- G helped on 4 cells; the dev check had 1.
- Protective stops: J above F and I on gantry bad parts, as in development.

## What this does not show

Everything listed under "Disclosed before the run" and "Known limits" in
`PREREGISTRATION.md` applies. In particular: 35.2 N is C's own factor; D, E and F were
not re-tuned at 35.2 N; the H/I retry was designed knowing C and has three review items
not fixed in this code (being fixed in v0.2e); the damage measure does not see terminal
loads; there is no cost model for a passed bad unit; the arm `generalization_combined`
results depend on worker order in the last digits.
