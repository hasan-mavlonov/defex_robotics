# benchmark_v0.2c: report

Pre-registered in [`PREREGISTRATION.md`](PREREGISTRATION.md) (commit b479e17,
code frozen at 45f8b06). Seed 20261116, gantry and UR5e arm, nine controllers,
four suites, 86,400 paired trials. Run record: [`RUN_LOG.md`](RUN_LOG.md). Every
number below comes from the per-trial files in this folder:
[`TABLES.md`](TABLES.md) (`python -m experiments.checkpoint_report results/benchmark_v0.2c`)
and [`AUDIT_TABLES.md`](AUDIT_TABLES.md) (`python -m experiments.cp2_audit results/benchmark_v0.2c`),
and [`PAIRED_TABLES.md`](PAIRED_TABLES.md) (`python -m experiments.v02c_paired results/benchmark_v0.2c`:
C paired against H and I, escapes on good-part trials, latch_spread without
`mf_terminal_max`; same exact McNemar test).

Simulation only. Controllers: A fixed, B vision correction, C Defex adaptive,
D spiral search, E B on an RCC device, F spiral search on an RCC device, G C plus
a learned contact prior, H D plus C's retention pull, I F plus C's retention
pull. The fair baselines are D, E, F, H and I.

## Headline

The pre-registered rules, applied ([`TABLES.md`, last section](TABLES.md#pre-registered-decision-rules-applied)):

| Machine, suite | C | Best fair baseline | p | Rule outcome |
|---|---|---|---|---|
| gantry, standard | 99.0% | F/I 96.6% | < 1e-6 | C ahead |
| gantry, latching good parts | 95.7% | F/I 99.2% | 4.9e-5 | **C below** |
| gantry, mis-characterized vision | 85.8% | F/I 84.0% | 0.4 | **baseline matches C** |
| gantry, latch_spread good parts | 100.0% | E 83.0% | < 1e-6 | C ahead |
| arm, standard | 97.6% | F/I 96.4% | 0.0027 | C ahead |
| arm, latching good parts | 93.7% | F 96.5% (I 96.2%) | 0.012 (I: 0.028) | **C below** |
| arm, mis-characterized vision | 78.0% | F/I 78.8% | 0.78 | **baseline matches C** |
| arm, latch_spread good parts | 99.5% | E 86.8% | < 1e-6 | C ahead |
| both, deliberately bad parts passed | 0 of 2,200 | H 0, I 0 of 2,200 | 1 | no difference |

1. **With the same pull test, the conventional cells pass no bad parts either.**
   C, H and I each passed 0 of 2,200 deliberately bad latching parts (Wilson 95%
   upper bound 0.17%). D and F, the same cells without the pull, check depth
   only and passed 1,174 and 1,468 of 2,200. The Checkpoint 2 gap in bad parts
   was the pull test, and a conventional cell can run it.
2. **On latching good parts, C seats fewer than F and I on both machines**
   (gantry 95.7% against 99.2%; arm 93.7% against 96.5% and 96.2%). The losses
   are in `mf_noise_1mm`: C 174 and 162 of 200, F 195 and 180.
3. **With the camera worse than the cell believes, F and I match C** on both
   machines (gantry 85.8% against 84.0%, arm 78.0% against 78.8%).
4. **C seats more on the standard suite on both machines** (gantry 99.0% against
   96.6%, arm 97.6% against 96.4%) and **passes no mis-seated connector there**:
   F and I passed 33 (gantry) and 34 (arm) of 2,000 as good, C 0 (paired p < 1e-9). The pull test
   does not apply to this housing-only connector, so this is C's verification,
   not the pull. The same holds in the mis-characterized-vision suite (F/I 34 and
   31 of 500, C 0).
5. **On latch_spread good parts C seats nearly all and the baselines with the
   pull do not** (C 600 and 597 of 600; I 473 and 474; H 481 and 475). Most of
   this gap comes from a push C has and the baselines lack, like the pull at
   Checkpoint 2: see [below](#latch_spread-what-the-gap-is).
6. **C is slower everywhere** (table below). On the standard suite it makes 45%
   (gantry) and 37% (arm) fewer good units per hour than F/I.
7. **G (learned prior) beats C on six of eight suites** (p < 0.05) and shows no
   measurable gain on latch_spread. It passed one bad unit.

## Throughput

Good units per hour of cell time, 60 s per protective stop; median successful
cycle in brackets. From `TABLES.md`.

| Machine, suite | C | F | I | H |
|---|---|---|---|---|
| gantry, standard | 606 (5.30 s) | 1,101 (2.43 s) | 1,101 (2.43 s) | 895 (2.87 s) |
| gantry, latching good parts | 438 (5.95 s) | 866 (2.43 s) | 513 (5.33 s) | 343 (5.92 s) |
| gantry, mis-characterized vision | 322 (6.45 s) | 468 (3.54 s) | 468 (3.54 s) | 396 (3.73 s) |
| gantry, latch_spread good parts | 527 (5.96 s) | 1,068 (2.41 s) | 538 (5.31 s) | 481 (5.87 s) |
| arm, standard | 373 (8.14 s) | 596 (4.77 s) | 596 (4.77 s) | 576 (4.77 s) |
| arm, latching good parts | 282 (8.70 s) | 515 (4.58 s) | 334 (8.25 s) | 263 (8.16 s) |
| arm, mis-characterized vision | 171 (9.67 s) | 268 (6.14 s) | 268 (6.14 s) | 212 (5.21 s) |
| arm, latch_spread good parts | 351 (8.71 s) | 540 (4.52 s) | 341 (8.18 s) | 349 (8.08 s) |

The pull test costs I about 3 s (gantry) and 3.7 s (arm) per latching cycle
against F. With it, I still makes more good units per hour than C on every suite
except arm latch_spread (341 against 351). F's figures count only good units;
it also passes the bad parts.

Median cycle per deliberately bad part: C 8.4 s (gantry latching) and 12.8 s
(arm latching), 10.4 s and 17.2 s on latch_spread; I 4.4, 7.6, 4.3 and 6.7 s.

## latch_spread: what the gap is

`latch_spread` was added after development showed C ahead there, and the
pre-registration names it as the part-variation question. C is ahead by the
rule. Where the baselines lose:

* **`mf_terminal_max` (terminal friction at the datasheet's maximum): H and I
  seat 0 of 100 on both machines, C 100.** Every controller gets the connector
  file's force budget (insert target 30 N, abort 40 N). D, F, H and I push at the
  30 N target, which is below the datasheet's 32 N maximum mating force; at this
  friction they stall short (peak measured force 29.8-30.1 N), fail and back out.
  C, when it stalls short of depth, pushes at 1.1 x the datasheet maximum
  (35.2 N, `proof_push_factor`, the same force as its pull test) and seats them.
* **`mf_spread` (latch position, latch force and terminal friction drawn
  together): I seats 73 and 75 of 100, H 82 and 75, C 100 and 99.** Most of I's
  failures are `retention_failed` (24 of 27 on the gantry, 14 of 25 on the arm):
  the pull test found the latch not engaged. The rest are jams.
* Without `mf_terminal_max`, C still leads (paired C vs I: 500 against 473 of
  500 on the gantry, p = 1.5e-8; 497 against 474 on the arm, p = 5.6e-6).

So this run does not separate C's method from one rule: push above the
datasheet's maximum mating force when the plug stalls short. A conventional cell
could run that rule, as it can run the pull test. H and I with that push have
not been tested; that would be development work and, for a claim, a new
pre-registration and seed. The connector file's 30 N insert target is itself
below the datasheet's 32 N maximum, which is worth fixing for every controller.

None of the baselines' latch_spread failures is an escape: with the pull test,
H and I declare these parts failed. D and F, without it, pass 37-93 of the
`mf_terminal_max` good parts as seated when they are not.

## Bad units passed on good-part conditions

| All good-part trials (3,700 per machine) | C | G | D | F | H | I |
|---|---|---|---|---|---|---|
| gantry | 0 | 0 | 117 | 183 | 59 | 67 |
| arm | 0 | 1 | 103 | 124 | 43 | 68 |

D's and F's counts include latch_spread good parts they declared seated short of
the latch (gantry 51 and 116, arm 49 and 57); the pull test removes those, so
H's and I's counts are what a depth check lets through on the other suites.

C: 0 of 7,400 (Wilson 95% upper bound 0.05%). Paired C vs I, standard suite:
gantry 0 against 33 (p = 2.3e-10), arm 0 against 34 (p = 1.2e-10); with the
camera worse than believed: 0 against 34 and 0 against 31 (p < 1e-9).

I's escapes on the standard and mis-characterized-vision suites are all
`false_accept`: plugs 11.0-15.0 mm deep (full depth is 15 mm), up to 4.96
degrees of tilt and 0.73 mm lateral offset. 102 of 132 are under `noise_2mm` and
`heldout_mischar_2mm`, where the camera error is largest. I's 3 on arm latching
good parts are plugs 7.80 mm deep tilted up to 3.07 degrees, over the 3.0 degree
limit.

G's one escape ([audit](AUDIT_TABLES.md)): arm latching, `mf_noise_1mm`, trial
113, 7.73 mm deep at 3.21 degrees of tilt. This is the tilt mode
named in the pre-registration and in `results/v0.2c_verify_fixes/REPORT.md`
("Not fixed"); tilt is not checked on either machine.

The wall-yaw fix held: C and G had 4,735 wall-yaw passes on the arm, none with a
negative required free travel, and no escape through that path (it caused 5 of
C's 6 escapes in benchmark_v0.2b).

## G against C

| Machine, suite | G | C | C-only / G-only | p |
|---|---|---|---|---|
| gantry, standard | 99.7% | 99.0% | 0 / 14 | 0.00012 |
| gantry, latching good parts | 98.7% | 95.7% | 3 / 21 | 0.00028 |
| gantry, mis-characterized vision | 92.4% | 85.8% | 12 / 45 | 1.3e-5 |
| gantry, latch_spread good parts | 99.8% | 100.0% | 1 / 0 | 1 |
| arm, standard | 98.4% | 97.6% | 4 / 20 | 0.0015 |
| arm, latching good parts | 97.5% | 93.7% | 6 / 29 | 0.00012 |
| arm, mis-characterized vision | 85.0% | 78.0% | 6 / 41 | < 1e-6 |
| arm, latch_spread good parts | 99.8% | 99.5% | 0 / 2 | 0.5 |

G helps on six suites and shows no measurable gain on latch_spread. Against the
best fair baseline, G is ahead on gantry standard, gantry mis-characterized
vision (92.4% against 84.0%), arm standard and arm mis-characterized vision
(85.0% against 78.8%), and level with F/I on latching good parts (gantry 98.7%
against 99.2%, arm 97.5% against 96.5%; these comparisons are not
pre-registered). Its cost per cycle is the same as C's or up to 1.1 s higher.

## Against development

What the pre-registration expected, and what happened:

* H/I bad-part gap to C small: it is zero.
* F or I to match or beat C on latching: they beat it on both machines.
* latch_spread gap of the size seen on dev seed 2026 (C 120/120, F with pull 91
  and 93): C 600 and 597 of 600, I 473 and 474.
* E slow on the gantry (2 mm/s insert): 10.8 s per cycle on the standard suite.
* C slower than D and F on both machines: yes, on every suite.

Changes against benchmark_v0.2b (seed 20261102, before the v0.2c work), C
against F:

* arm standard: from level (96.7% against 96.3%) to C ahead (97.6% against 96.4%);
* gantry latching good parts: from C ahead (95.7% against 89.0%) to C below (95.7%
  against 99.2%), after the gantry baselines were re-tuned with latching parts;
* arm mis-characterized vision: from F ahead (75.4% against 81.4%) to level
  (78.0% against 78.8%).

## What this means for the claims

* The bad-part result of Checkpoint 2 does not belong to C. A conventional cell
  with the same pull test passes no bad parts.
* What remains for C, measured here: it does not pass mis-seated connectors
  that a depth check accepts (0 against I's 67 and 68 of 3,700 good-part trials per
  machine), and it seats more housing-only connectors under the
  standard conditions. It seats more latch_spread parts, mainly because it
  pushes above the datasheet's maximum mating force when a plug stalls, which
  the baselines do not.
* C seats fewer latching good parts than F and I, and is matched when the camera
  is worse than believed. It is slower on every suite.
* Whether the escapes C prevents are worth its lower throughput depends on what
  a mis-seated connector costs, which this benchmark does not price.

## Known limits

As pre-registered: simulation only; the latch model and the spread around it are
assumed; one latching connector family; one arm model with Menagerie's 0.2 s
servo lag; no cost model for a passed bad unit. Added by this run: the
connector file's insert target (30 N), which D, F, H and I push at, is below the
datasheet's 32 N maximum mating force. The tuned insert forces of F on the gantry
(8 N) apply only to the housing-only connector; on the Micro-Fit the force
budget replaces them for every controller.

## Reproduce

```
results/benchmark_v0.2c/PREREGISTRATION.md      # the eight commands, at b479e17
python -m experiments.checkpoint_report results/benchmark_v0.2c > results/benchmark_v0.2c/TABLES.md
python -m experiments.cp2_audit results/benchmark_v0.2c > results/benchmark_v0.2c/AUDIT_TABLES.md
python -m experiments.v02c_paired results/benchmark_v0.2c > results/benchmark_v0.2c/PAIRED_TABLES.md
```
