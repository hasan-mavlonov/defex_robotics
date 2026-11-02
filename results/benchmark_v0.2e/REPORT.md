# benchmark_v0.2e report

Seed 20261130 and code ddd0d34, run from e0006a1, which adds only the
pre-registration. 96,000 trials: all ten controllers on the gantry and on the UR5e arm.
Run details are in `RUN_LOG.md`. Every number below comes from `TABLES.md`,
`PAIRED_TABLES.md`, `AUDIT_TABLES.md` or `HEADLINE_TABLES.md` in this folder, or from
`trials.csv` and `events.json.gz` where a section says so. The tables were made from the
per-trial rows with the pre-registered commands. Comparisons with earlier runs use
`../benchmark_v0.2d/TABLES.md` (seed 20261123) and `../benchmark_v0.2d_rep/TABLES.md`
(seed 20261124); those runs used the v0.2d code. Simulation only.

## Result in one paragraph

C is ahead of every fair baseline (D, E, F, H, I) on 2 of 8 cells: standard on both
machines. A fair baseline matches C on 5 cells. On arm latching good parts C is below F
(92.0% vs 95.2%, p = 0.014). The other two seeds matched there. On gantry latching good
parts, where both earlier seeds had C below F, they now match (p = 0.12).

C's (and G's) trials in the conditions where C fell most were rerun on the v0.2d code:
two of the five gantry mis-characterized vision conditions and one of the three arm
latching conditions, 600 trials. They gave identical rows (`../v0.2e_postrun_check/`).
So C's drop on these two cells comes from the seed, not the fixes. F was not rerun, and
neither was gantry latching.

No controller with a pull test or C's VERIFY (C, G, H, I, J) passed a deliberately bad
part: 0 of 2,200 each. On good-part trials C passed no bad units, while H passed 101 and
I 138. C makes fewer good units per hour than F and I on every cell (gantry standard:
601 against 1,100).

The stop condition still holds. Hasan decides how the pitch changes.

## Pre-registered verdicts

C against the best fair baseline (metric 1; `TABLES.md`, "Pre-registered decision
rules, applied"; `HEADLINE_TABLES.md` (a)):

| Machine, suite | C | Best fair baseline | C-only / other-only | p | Verdict |
|---|---|---|---|---|---|
| gantry, standard | 99.1% | F and I 96.8% | 53 / 8 | < 1e-6 | C ahead |
| gantry, latching good parts | 97.5% | F 98.8% | 6 / 14 | 0.12 | **a fair baseline matches C** |
| gantry, mis-characterized vision | 81.4% | F and I 83.8% | 48 / 60 | 0.29 | **a fair baseline matches C** |
| gantry, latch_spread good parts | 100.0% | I 100.0% | 0 / 0 | 1 | **a fair baseline matches C** |
| arm, standard | 98.1% | F and I 96.2% | 54 / 16 | 5.9e-6 | C ahead |
| arm, latching good parts | 92.0% | F 95.2% | 18 / 37 | 0.014 * | **C below F** |
| arm, mis-characterized vision | 76.8% | F and I 78.4% | 52 / 60 | 0.51 | **a fair baseline matches C** |
| arm, latch_spread good parts | 99.5% | I 99.8% | 0 / 2 | 0.5 | **a fair baseline matches C** |

\* 0.01 <= p < 0.05. There is no multiple-comparison correction. Two more verdicts in
this run are in that band: G helps on gantry latching (p = 0.021), and J is ahead of C on
arm latching (`TABLES.md` prints p = 0.01; exact McNemar on 38 / 18 discordant
pairs gives 0.0105).

## The same verdicts on three seeds

Different seeds, not paired, no test across runs. The v0.2d and replication runs used
the v0.2d code; this run uses the v0.2e code.

| Machine, suite | seed 20261123 (v0.2d) | seed 20261124 (replication) | seed 20261130 (v0.2e) |
|---|---|---|---|
| gantry, standard | C ahead | C ahead | C ahead |
| gantry, latching good parts | C below F, p = 0.012 | C below F, p = 0.0026 | matches, p = 0.12 |
| gantry, mis-characterized vision | C ahead, p = 0.044 | matches, p = 0.67 | matches, p = 0.29 |
| gantry, latch_spread good parts | matches | matches | matches |
| arm, standard | C ahead | C ahead | C ahead |
| arm, latching good parts | matches, p = 0.64 | matches, p = 1 | C below F, p = 0.014 |
| arm, mis-characterized vision | matches | matches | matches |
| arm, latch_spread good parts | matches | matches | matches |

C is ahead of every fair baseline on all three seeds only on `standard`, on both
machines. On every other cell a fair baseline matches or beats C on every seed, except
gantry mis-characterized vision on seed 20261123 (C ahead, p = 0.044).

Of the 60 verdicts the pre-registered rules give in `TABLES.md`, 51 have the same class
on all three seeds. The nine that differ on at least one seed are:

| Verdict | 20261123 | 20261124 | 20261130 |
|---|---|---|---|
| gantry latching, C vs best fair | below, 96.5 vs 98.5 | below, 96.5 vs 99.0 | matches, 97.5 vs 98.8 |
| arm latching, C vs best fair | matches, 94.3 vs 93.7 | matches, 93.7 vs 93.8 | below, 92.0 vs 95.2 |
| gantry heldout, C vs best fair | ahead, 87.6 vs 83.4 | matches, 87.2 vs 86.2 | matches, 81.4 vs 83.8 |
| arm standard, G vs C | no gain, p = 0.11 | helps, p = 0.0074 | helps, p = 0.0044 |
| gantry latching, G vs C | no gain, p = 0.11 | no gain, p = 0.064 | helps, p = 0.021 |
| gantry latching, J vs C | matches, p = 0.093 | ahead, p = 0.011 | matches, p = 0.19 |
| arm latching, J vs C | matches, p = 0.43 | matches, p = 1 | ahead, p = 0.0105 |
| gantry heldout, J vs C | matches, p = 0.38 | matches, p = 0.089 | ahead, 88.8 vs 81.4, p = 0.00039 |
| arm standard, J vs I | ahead, p = 0.0095 | ahead, p = 0.043 | matches, p = 0.071 |

Four of the nine follow from C's own lower success on this seed's gantry
mis-characterized vision (81.4%) and arm latching (92.0%) trials. The post-run check
(`../v0.2e_postrun_check/REPORT.md`) reran those trials on the v0.2d code:

- C and G on the two gantry heldout conditions where C lost most: 400 trials;
- C on arm latching `mf_noise_1mm`: 200 trials.

All 600 rows are identical to this run's in every field but wall time. That check was not pre-registered.

## Bad parts and bad units

Deliberately bad parts passed (metric 2): C, G, H, I and J passed 0 of 800 on each
machine's latching suite and 0 of 300 on each latch_spread suite. That is 0 of 2,200
each (Wilson 95% upper bound 0.17%), as on both earlier seeds. Without a pull test, D
passed 1,275 of 2,200 and F 1,510 (counted from `trials.csv`, latching and latch_spread,
both machines).

Bad units on good-part trials, C against H and I (metric 5, `PAIRED_TABLES.md`):

| Cell | C | H | I | p, C vs H / C vs I |
|---|---|---|---|---|
| gantry standard (2,000 trials) | 0 (<= 0.19%) | 30 | 32 | 1.9e-9 / 4.7e-10 |
| gantry mis-characterized vision (500) | 0 (<= 0.76%) | 28 | 37 | 7.5e-9 / 1.5e-11 |
| arm standard (2,000) | 0 (<= 0.19%) | 27 | 32 | 1.5e-8 / 4.7e-10 |
| arm mis-characterized vision (500) | 0 (<= 0.76%) | 16 | 34 | 3.1e-5 / 1.2e-10 |
| arm latching good parts (600) | 0 (<= 0.64%) | 0 | 3 | 1 / 0.25 |
| other latching and latch_spread good parts | 0 | 0 | 0 | 1 |

C passes fewer bad units than H and I on every housing-only cell, as on both earlier
seeds. In all, over 7,400 good-part trials:

- C 0 (Wilson upper bound 0.052%), G 1, J 2;
- H 101 and I 138 (seed 20261123: 118 and 161; seed 20261124: 112 and 138);
- D 136, F 178.

I's three on arm latching are `mf_noise_1mm` plugs at 7.79-7.85 mm with tilt
3.02-3.22 deg (trials 46, 72 and 197 in `trials.csv`).

**G's one bad unit** is the first bad unit C or G has passed on any of the three seeds.
It is arm latching `mf_noise_1mm` trial 130 (`AUDIT_TABLES.md`): 7.75 mm, true tilt
3.01 deg against the 3.0 deg limit. G's own tilt check gave a verdict, reading 0.47 deg
with the CoP at 0.09 of the half-width (`events.json.gz`), and passed. The force guard
did not act on this trial. C on the same trial aborted on its time limit.

## G and J

G against C (metric 3):

- G helps on 6 cells: gantry standard (p = 1.5e-5), gantry latching (p = 0.021 *),
  gantry mis-characterized vision (p < 1e-6), arm standard (p = 0.0044), arm latching
  (p < 1e-6) and arm mis-characterized vision (p = 3.3e-6).
- No measurable gain on latch_spread on either machine.

J against C and against I (metric 4, `HEADLINE_TABLES.md` (b)):

| Cell | J vs C, seated | J vs I, seated | J's bad units vs C / vs I |
|---|---|---|---|
| gantry, standard | below (98.0% vs 99.1%, p = 0.00094) | ahead (98.0% vs 96.8%, p = 0.00043) | 0 vs 0 / 0 vs 32, fewer |
| gantry, latching | matches (p = 0.19) | matches (identical) | 0 / 0 |
| gantry, mis-characterized vision | ahead (88.8% vs 81.4%, p = 0.00039) | ahead (88.8% vs 83.8%, p = 0.00017) | 1 vs 0, n.s. / 1 vs 37, fewer |
| gantry, latch_spread | matches (identical) | matches (identical) | 0 / 0 |
| arm, standard | below (96.8% vs 98.1%, p = 0.00058) | matches (p = 0.071) | 0 vs 0 / 0 vs 32, fewer |
| arm, latching | ahead (95.3% vs 92.0%, p = 0.0105 *, printed 0.01) | matches (p = 0.5) | 1 vs 0, n.s. / 1 vs 3, n.s. |
| arm, mis-characterized vision | matches (p = 0.66) | matches (p = 0.098) | 0 vs 0 / 0 vs 34, fewer |
| arm, latch_spread | matches (p = 0.25) | matches (p = 1) | 0 / 0 |

J passed no deliberately bad part. J's two bad units (`AUDIT_TABLES.md`):

- gantry `heldout_mischar_2mm` trial 35: 15.01 mm, yaw -3.61 deg.
- arm latching `mf_noise_1mm` trial 46: 7.80 mm, tilt 3.10 deg. J's first latch check
  had an empty tilt window, so it gave no tilt verdict (`events.json.gz`: "window at
  0.0 N, under the 11.7 N floor -> no verdict"). This is post-freeze review item 3
  below. It predates v0.2e: before the guard, the v0.2d code treated an empty window
  as no wall load and passed the check the same way.

Whether J or C would be the product is not decided by this run.

## Cycle time and throughput

Median successful cycle, then good units per hour at 0 s / 60 s per protective stop
(`HEADLINE_TABLES.md` (c)):

| Cell | C | J | I | F |
|---|---|---|---|---|
| gantry, standard | 5.30 s, 601 | 4.78 s, 643 | 2.43 s, 1,100 | 2.43 s, 1,100 |
| gantry, latching good parts | 6.16 s, 449 | 5.46 s, 498 / 491 | 5.46 s, 498 / 484 | 2.40 s, 861 / 841 |
| arm, standard | 8.15 s, 387 / 377 | 7.99 s, 381 | 4.77 s, 593 | 4.77 s, 593 |
| arm, latching good parts | 8.99 s, 280 / 267 | 8.62 s, 322 / 313 | 8.63 s, 320 / 309 | 4.66 s, 495 / 474 |

As on both earlier seeds, C's median cycle on housing-only parts is 1.6-2.2 times F's
and I's (including mis-characterized vision, `HEADLINE_TABLES.md` (c)). On latching parts J, I and H take about C's cycle. F is 2.3-2.6 times as fast as
all of them on the gantry and 1.8-1.9 times on the arm, and it passes most bad parts.

Protective stops on bad parts, latching and latch_spread together (`trials.csv`), on
the gantry:

| Seed | J | F | I | C |
|---|---|---|---|---|
| 20261130 (this run) | 172 | 115 | 115 | 72 |
| 20261123 (v0.2d) | 182 | 123 | 125 | 68 |

None of C, F, I or J stopped on arm bad parts.

## What the three fixes did in this run

- **Fix 1, simulator reset.** It changes only arm trials with a grasp offset, which
  only `generalization_combined` has. The evidence is the seed-4006 validation
  (`../v0.2e_validation/REPORT.md`), not the post-run check, which ran no such trial.
- **Fix 2, H and I pull retry, rule version 5.** The pull test failed and a retry ran
  on 1,312 of H's trials and 1,593 of I's (`events.json.gz`):
  - none was stopped by the new hold or depth gate (`repush_not_held` 0,
    `repush_short_of_seat` 0, `trials.csv`);
  - H 1,305 and I 1,592 went on to the second pull;
  - 7 and 1 ended in an abort or protective stop during the re-push (H: 3
    `aborted:excess_force`, 4 `protective_stop`; I: 1 `aborted:excess_force`).

  On good parts the second pull let H seat 26 and I 82 that had failed the first pull.
  `retries` now counts the pull retry. H's total over all trials went from 1,608
  (v0.2d) to 2,994, and I's from 857 to 2,473. These counts, and `recovered`, are not
  comparable with v0.2d.
- **Fix 3, C/G/J tilt-check force guard.** On C and G the guard gave no tilt verdict
  on 14 trials, all on arm latching:
  - C 6, all seated;
  - G 8: 7 good parts seated and 1 bad part rejected.

  Four of C's six are in the post-run check, with rows identical to the v0.2d code. On
  J the guard reports no verdict at the first latch check on 3,877 of its 4,600
  latching and latch_spread trials, because the window is empty (review item 3).

## Against what development predicted (pre-registration, "Expected from development")

- Headline: C ahead on standard on both machines, as expected.
  - Expected C below F on gantry latching good parts; this seed gives a match
    (p = 0.12).
  - Expected a fair baseline to match C elsewhere; arm latching gives C below F
    (p = 0.014), which neither earlier seed showed.
  - The post-run check covers arm latching only (C on `mf_noise_1mm`): it puts C's
    drop there on the seed. Gantry latching was not rerun.
- "Outcomes as benchmark_v0.2d for A-G and J": that expectation is about the code. On
  the 600 trials checked, the code gives the v0.2d rows. Across seeds, outcomes differ
  as the table above shows.
- "Arm H seats a few more latching good parts": not testable across seeds. Arm H
  latching good parts were 79.0% here and 81.0% on seed 20261123, unpaired. The second
  pull seated 14 arm H good parts on latch_spread and none on latching.
- "H and I's `retries` roughly triple": I's went up 2.9 times and H's 1.9 times.
- "The depth gate and the tilt guard are expected not to change outcomes": the gate
  never fired. The guard fired on 14 C/G trials; the 4 that were rechecked did not
  change.
- Bad parts: C, G, H, I and J passed none, as on v0.2d. The pre-registration states
  this only through "Outcomes as benchmark_v0.2d".
- Bad units: C 0, as on v0.2d. G passed 1, where v0.2d had 0; see above.

## Post-freeze review findings

A code review after the freeze (ddd0d34) found five items. None was fixed, because the
code was frozen. What this run shows about each:

1. **H/I `repush_not_held` is stricter than C.** C's bottom proof push goes on to the
   latch check after a 1.5 s timeout; H and I reject the part. This can only cost H/I
   good parts. It fired 0 times.
2. **The tilt guard also drops correct tilt catches** when C's or G's arm floor-impact
   settle is under 11.75 N, so it could add a rare C/G tilt escape. It fired on 14 C/G
   trials, none an escape. G's one bad unit had a real tilt verdict.
3. **J's first latch check never gets a tilt verdict** (empty window; this predates
   v0.2e). J's arm latching bad unit, at 3.10 deg tilt, is this case.
4. **The `_seat_window` docstring is wrong** (`defex/control/spiral_search.py`
   324-325, "and F/k on the RCC stage"). Text only, no effect on results.
5. **An import, and a timing side effect of fix 1.**
   - `defex/control/base.py:12` imports the `FixtureDynamics` dataclass from
     `defex.sim.backend`. That is the simulator-agnostic interface module, not MuJoCo
     or a backend implementation. The import has been there since ff86b16, so it
     predates v0.2e.
   - Fix 1 changes forces and final pose in the last digits on arm
     `generalization_combined` trials. In the validation, 10 G and J rows changed and
     one cycle time moved, by 14 ms.

## What this does not show

Everything listed under "Disclosed before the run" in `PREREGISTRATION.md`, and the
v0.2d pre-registration's known limits that it carries over, still applies. In
particular:

- 35.2 N is C's own factor, and D, E and F were not re-tuned at 35.2 N.
- The H/I retry (fix 2) was designed after the v0.2d results were seen.
- The damage measure does not see terminal loads.
- There is no cost model for a passed bad unit.

Three seeds of one simulator do not test the simulator. They show which verdicts hold
across draws of scenarios. The ones that hold on all three: C ahead on standard; C's
zero bad units; no bad parts passed; C's lower throughput.
