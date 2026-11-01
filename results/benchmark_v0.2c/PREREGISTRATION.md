# benchmark_v0.2c pre-registration

Written and committed before the run. Nothing below changes after the first trial
of the reported seed has run. If the run exposes a bug, the bug gets a fix, a new
pre-registration and a fresh seed, and this run moves to `earlier_runs/` with its
report.

## Question

After the v0.2c work, and with the conventional cells given the same retention
pull test as C, does Defex's controller C seat more good connectors, pass fewer
bad ones, or handle part-to-part variation better than a well-built conventional
cell, on the gantry and on the UR5e arm? Does G add anything over C?

Checkpoint 2 (benchmark_v0.2b) and its review found that C's bad-part advantage
came from having a pull test the baselines lacked, that C's latch check used the
simulator's assumed latch geometry, and that the gantry baselines were never tuned
with the latching connector. This run is built to test what is left.

## Frozen code

- Commit **45f8b06** on branch `v0.2c/next`. The run may start from a later commit
  that changes only `results/`. Every `config.json` must show `git_dirty: false`.
- Model files used by G (fixed by content):
  - `assets/models/contact_prior_gantry.json`, sha256 `650bfd824020594afbe5a579f61942e26d00011fc90943a6695cd78af795269b`
  - `assets/models/contact_prior_arm.json`, sha256 `c17fdb80fbd305431c7e7cb7d0e7be48d6354822abef543c11a4aebc8065b3b2`
- Changes since benchmark_v0.2b, all developed on seeds 2026, 2027, 3001-3040,
  4002 and 3032 only (reports under `results/v0.2c_*`):
  - D, E, F: arm tuning (`v0.2c_arm_baselines`) and gantry re-tuning with the
    Micro-Fit good parts (`v0.2c_gantry_baselines`), each by a selection rule
    committed before its runs.
  - **H and I (new): D and F with C's retention pull** after a latching insertion,
    the same pull force (1.1 x the datasheet's 32 N maximum mating force) and the
    same movement limit (0.6 x the datasheet's 1.75 mm terminal wipe). Identical to
    D and F on the housing-only connector.
  - C: defect verdict, gentle retract and polarization guard
    (`v0.2c_defect_verdict`); arm robustness rules (`v0.2c_arm_robustness`); a
    datasheet-based latch check chosen on seed 4002 (click logged, not required;
    `v0.2c_integration/review_fixes`); the arm's wall-yaw check now fails a plug the
    walls clamp (`v0.2c_verify_fixes`); a depth gate on the re-seat path.
  - G: contact model retrained on the integrated C; the seed-4002 rule installed a
    new gantry model and kept the Checkpoint 2 arm model (`v0.2c_integration/prior`).
  - A new simulator-side suite, `latch_spread`: good parts whose latch position,
    latch force and terminal friction vary within or at the edge of the
    datasheet's range, plus three bad parts built the same way. The controllers
    keep the connector file's values.

## Design

- Base seed **20261116**. No controller has run on it before this commit (no
  `config.json` under `results/` uses it; the word appears only in reports that
  name it as reserved).
- Backends: `gantry` and `arm` (UR5e from MuJoCo Menagerie).
- Controllers: A fixed, B correction, C adaptive, D spiral, E correction_rcc,
  F spiral_rcc, G adaptive_learned, H spiral_pull, I spiral_rcc_pull. Paired:
  every controller sees the same scenario for a given condition and trial index.
- Suites, trials per condition and controller:
  - `standard`: 20 conditions, housing-only connector, 100 trials.
  - `latching`: Micro-Fit 3.0, 3 good-part conditions and 4 deliberately bad parts, 200 trials.
  - `heldout`: the 5 mis-characterized-vision families, 100 trials (robustness
    conditions, not held out: they have been run before).
  - `latch_spread`: 6 good-part and 3 bad-part conditions, 100 trials.
- Total: 8 runs, 2 x 9 x (20 x 100 + 7 x 200 + 5 x 100 + 9 x 100) = 86,400 trials.
  Estimated 3.5 hours on this machine (benchmark_v0.2b: 54,600 trials in about 2.2 hours).
- Commands, run in this order from the repository root:

```
for B in gantry arm; do
  for S in standard:100 latching:200 heldout:100 latch_spread:100; do
    python -m experiments.robustness --suite ${S%%:*} --backend $B --trials ${S##*:} \
      --seed 20261116 --workers 9 --no-plots --name benchmark_v0.2c/${B}_${S%%:*} \
      --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull
  done
done
python -m experiments.checkpoint_report results/benchmark_v0.2c > results/benchmark_v0.2c/TABLES.md
python -m experiments.cp2_audit results/benchmark_v0.2c > results/benchmark_v0.2c/AUDIT_TABLES.md
```

## Metrics

Primary, per backend and suite:

1. Success rate per controller with Wilson 95% intervals; exact McNemar against
   C on paired trials. On `latching` and `latch_spread`, success is measured on
   the good-part conditions.
2. Bad parts passed as good on the bad-part conditions: count, Wilson 95% upper
   bound, exact McNemar of C against the fair baseline with the fewest.
3. G against C, paired.

Secondary: bad units passed on good-part conditions, false rejects, protective
stops, cycle time p50/p95/p99 of successes, good units per hour (0 s and 60 s per
protective stop), median cycle per bad part, p95 peak force and wrist torque,
per-condition successes. All from `experiments/checkpoint_report.py` and, for
every bad unit C or G passes, `experiments/cp2_audit.py`.

## Decision rules, fixed in advance

The fair baselines are D, E, F, H and I. "Best" means the highest success rate on
that backend and suite; "fewest" the fewest bad parts passed.

- If the best fair baseline matches C (McNemar p >= 0.05, or C ahead by less
  than 1 point), that goes in the README headline, and Hasan decides how the pitch
  changes.
- If C is below the best fair baseline with p < 0.05, that goes in the README headline.
- C is reported as ahead only where it beats the best fair baseline with p < 0.05.
- **The bad-part comparison that counts is C against H and I**, which run the same
  pull test. A difference against D, E or F alone is reported as the effect of
  having a pull test, not of C.
- **The part-variation question is `latch_spread`, good parts: C against the best
  fair baseline**, by the rules above. This is the one place where development
  showed C ahead of a baseline with the same pull test.
- G is reported as helping only where it beats C with p < 0.05; otherwise "no
  measurable gain", or "worse" where C beats it with p < 0.05.
- Zero escapes are always given with their Wilson upper bound.
- C's cycle time and throughput are reported next to its success rate in every
  summary, including where they are worse.

## Expected from development, stated so they are not found later

- With the same pull test, H and I passed 0 bad parts on dev seed 2026 (D and F
  without it: 24-45 of 80). Expect the bad-part gap between C and H/I to be small.
- On dev seed 2026 (latch check installed), C seated 58 and 56 of 60 latching
  good parts (gantry, arm), F 54 and 58. Re-tuned gantry F seated 60 of 60 on dev
  seed 2027 against the old C's 54. Expect F or I to match or beat C on `latching`.
- On `latch_spread` (dev seed 2026, before the gantry re-tune), C seated 120 of
  120 per machine and F with the pull 91 and 93. The gantry D and F settings have
  changed since, so that gap may differ.
- E's gantry insert speed is 2 mm/s (the rule's pick by one trial), so E is slow.
- C passed 4 of 4,800 arm training trials seated just over 3 degrees of tilt; tilt
  is not checked on either machine.
- C is slower per cycle than D and F on both machines.
- The seed-3032 snapshot was on code before the review fixes; G's contact models
  were trained before C's latch check changed.

## Known limits

- Simulation only. The latch model and the spread around it are assumed; there is
  no measured force-depth curve.
- One latching connector family; one arm model with Menagerie's 0.2 s servo lag.
- At the datasheet's maximum terminal force, controllers whose insert budget is
  30 N cannot seat the part; `latch_spread` includes that case (`mf_terminal_max`).
- No cost model for a passed bad unit.
