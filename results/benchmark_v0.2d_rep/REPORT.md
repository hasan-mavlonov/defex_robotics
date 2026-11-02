# benchmark_v0.2d_rep report: benchmark_v0.2d on a second seed

Same code as benchmark_v0.2d (42df5c8), seed 20261124, 96,000 trials. Run details in
`RUN_LOG.md`. Numbers come from this folder's `TABLES.md`, `PAIRED_TABLES.md`,
`AUDIT_TABLES.md` and `HEADLINE_TABLES.md`, and from `../benchmark_v0.2d/TABLES.md` for
the first seed. The comparison rule is the one pre-registered: a verdict replicates if
both seeds give the same class. No test on the two seeds pooled. This run does not change
benchmark_v0.2d's verdicts. Simulation only.

## Result

Of the 60 verdicts benchmark_v0.2d's rules produce in `TABLES.md`, 57 replicate. Three do not:

| Verdict | seed 20261123 | seed 20261124 |
|---|---|---|
| gantry mis-characterized vision, C vs best fair baseline (F) | C ahead, 87.6% vs 83.4%, p = 0.044 | matches, 87.2% vs 86.2%, p = 0.67 |
| arm standard, G vs C | no measurable gain, p = 0.11 | G helps, 98.7% vs 98.2%, p = 0.0074 |
| gantry latching good parts, J vs C | matches, 98.0% vs 96.5%, p = 0.093 | J ahead, 98.7% vs 96.5%, p = 0.011 |

The first is the pre-registered headline verdict that rested on 0.01 <= p < 0.05 and
was flagged as most likely to change. With it, C is ahead of every fair baseline only
on the standard suite, on both seeds and both machines, and a fair baseline matches or
beats C on the other six cells on this seed.

## Replicated, both seeds

- **C ahead on standard**: gantry 99.2% / 99.4% against F and I 96.3% / 96.5%, arm
  97.8% / 98.2% against 96.1% / 96.2% (p < 1e-6 on this seed both machines).
- **C below F on gantry latching good parts**: 96.5% against 98.5% (p = 0.012) and
  96.5% against 99.0% (p = 0.0026).
- **A fair baseline matches C** on arm latching, arm mis-characterized vision and
  latch_spread good parts on both machines.
- **Bad parts**: C, G, H, I and J passed 0 of 2,200 on both seeds.
- **Bad units on good-part trials**: C 0 of 7,400 on both seeds; H 118 / 112, I 161 /
  138, J 3 / 2. C passes fewer than H and than I on all four housing-only cells on both
  seeds (this seed: p <= 3.8e-6 each, `PAIRED_TABLES.md`).
- **J**: below C on standard on both machines (this seed gantry 98.0% vs 99.4%,
  p = 1.1e-6; arm 96.8% vs 98.2%, p = 9e-5); ahead of I on standard on both machines and
  on gantry mis-characterized vision; passes fewer bad units than I on every
  housing-only cell; no significant difference from C in bad units anywhere.
- **G helps** on gantry standard, gantry and arm mis-characterized vision and arm
  latching on both seeds.
- **Throughput**: C makes fewer good units per hour than I on every cell on both seeds
  (this seed gantry standard 614 against 1,096; `HEADLINE_TABLES.md` section (c)).

J's two bad units on this seed (`AUDIT_TABLES.md`): gantry `heldout_worst_case` trial
98 (full depth, no tilt, as both of seed 20261123's heldout ones) and gantry
`noise_2mm` trial 41 (13.68 mm, 4.1 deg tilt: F's widened seat window, the kind the
pre-registration expected).

## What this does not show

Everything disclosed in benchmark_v0.2d's pre-registration applies. Two seeds of the
same simulator do not test the simulator: they show that the verdicts are not an
accident of one draw of scenarios.
