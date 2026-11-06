# benchmark_v0.2b (Checkpoint 2) pre-registration

Written and committed before the run. Nothing below changes after the first
trial of the reported seed has run. If the run exposes a bug, the bug gets a fix,
a new pre-registration and a fresh seed, and this run moves to `earlier_runs/`
with its report.

## Question

With latching physics, on two machines (the gantry fixture and a UR5e arm), how
do the conventional cells (A, B, D, E, F) compare with Defex's controller C, and
does the learned contact prior (G) add anything over C?

## Frozen code

- Commit **8e29f2e** on branch `v0.2/checkpoint2`. The run may start from a
  later commit that changes only `results/`. Every `config.json` must show
  `git_dirty: false`.
- Model files used by G (fixed by content):
  - `assets/models/contact_prior_gantry.json`, sha256 `e9a82d00137ffc801f96b786a6c07a93daf26dacf14e096473edb57ca2cdc66c`
  - `assets/models/contact_prior_arm.json`, sha256 `c17fdb80fbd305431c7e7cb7d0e7be48d6354822abef543c11a4aebc8065b3b2`
- Changes since benchmark_v0.2a, all developed on seeds 2026, 2027, 3001-3031
  and 4001 only:
  - W3: terminal and latch physics, four deliberately bad parts, C's
    push-click-pull check (`results/w3_development/`).
  - W4: C re-centres yaw every cycle (`results/w4_development/`).
  - W5 and W5b: fixture-aware speed and loop-gain rules; C on a stiff,
    lagging wrist (`results/w5_development/`, `results/w5b_development/`).
    These rules only switch on for wrists at least 4x stiffer or servos at
    least 2x slower than the gantry's, and are exact no-ops on the gantry,
    including the sim-randomization bands (`results/checkpoint2_prep/review_fixes/`).
  - W6: faster probing (`results/w6_development/`).
  - W9: controller G (`results/w9_development/`, `results/checkpoint2_prep/`).
    Gantry model trained on base seeds 3001-3030, selected on 4001; arm model the
    same, trained after the W5b arm fixes.
  - D now uses the setting the W1 ranking rule selects (edge-stage setting 5:
    search 2 N, spiral speed 2.5 mm/s, seat margin 0.5 mm), correcting the
    deviation disclosed in `results/benchmark_v0.2a/BASELINE_TUNING.md`. F keeps
    its tuned values. A, B and E are unchanged.

## Design

- Base seed **20261102**. No controller has run on it before this commit
  (`grep -r 20261102 results/` finds nothing but this file).
- Backends: `gantry` and `arm` (UR5e from MuJoCo Menagerie).
- Controllers: A fixed, B correction, C adaptive, D spiral, E correction_rcc,
  F spiral_rcc, G adaptive_learned. Every controller sees the same scenario for
  a given condition and trial index (paired).
- Suites, trials per condition and controller:
  - `standard`: 20 conditions, housing-only connector, 100 trials.
  - `latching`: Micro-Fit 3.0, 3 good-part conditions and 4 deliberately bad
    parts, 200 trials.
  - `heldout`: the 5 mis-characterized-vision families (the camera is worse
    than the controller is told). They were first run on seed 20261109 and C's
    yaw re-centring (W4) was developed after seeing that run, so they are
    reported as robustness conditions, not as held out. 100 trials.
- Total: 6 runs, 2 x 7 x (20 x 100 + 7 x 200 + 5 x 100) = 54,600 trials.
- Commands, run in this order from the repository root:

```
for B in gantry arm; do
  for S in standard:100 latching:200 heldout:100; do
    python -m experiments.robustness --suite ${S%%:*} --backend $B --trials ${S##*:} \
      --seed 20261102 --workers 9 --name benchmark_v0.2b/${B}_${S%%:*} \
      --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
  done
done
python -m experiments.checkpoint_report results/benchmark_v0.2b > results/benchmark_v0.2b/TABLES.md
```

## Metrics

Primary, per backend and suite:

1. Success rate per controller with Wilson 95% intervals; exact McNemar against
   C on paired trials. On the latching suite, success is measured on the three
   good-part conditions.
2. Bad parts passed as good on the four defects: count, Wilson 95% upper bound
   of the false-accept rate, exact McNemar of C against the fair baseline with
   the fewest.
3. G against C, paired.

Secondary: bad units passed on good-part conditions (failed, not stopped, not
declared failed), false rejects (seated in ground truth, declared failed),
protective stops, cycle time p50/p95/p99 of successes, good units per hour (all
cycles, plus 0 s or 60 s per protective stop), p95 peak contact force and wrist
torque, per-condition successes.

All tables come from `experiments/checkpoint_report.py`, which recomputes
everything from `trials.csv`.

## Decision rules, fixed in advance

The fair baselines are D, E and F (B and A are reported but are not what a
competent integrator would ship for this task). "Best" means the highest
success rate on that backend and suite.

- If the best fair baseline matches C (McNemar p >= 0.05, or C ahead by less
  than 1 point), that goes in the README headline, and Hasan decides how the
  pitch changes.
- If C is below the best fair baseline with p < 0.05, that goes in the README
  headline.
- G is reported as helping only where it beats C with p < 0.05; otherwise "no
  measurable gain", or "worse" where C beats it with p < 0.05.
- C's false-accept rate on bad parts is always given with its Wilson upper
  bound. The word "zero" is used only with that bound next to it.
- C's cycle time and throughput are reported next to its success rate in every
  summary, including where they are worse than a baseline's.

## Expected from development, stated so they are not found later

- G raises protective stops on wrong-polarization parts (gantry dev 1 -> 6 of
  20 force trips; arm 0 -> 3 of 60 torque trips). These flag the unit as failed,
  so they are not escapes, but each costs a cell reset.
- On the arm, C's rules were diagnosed and set by hand on dev seed 2026, and G
  has a model trained on arm data. D, E and F received no arm-specific work.
  The arm comparison is therefore C and G after two arm passes against
  baselines after none.
- On the arm, F seated as many good units as C on out-of-sample dev seed 3031
  (87 against 86 of 100) while passing 6 bad units; C's advantage there was
  bad units passed, not seating rate.
- C is slower per cycle than D and F on both machines (arm dev median 8.4 s
  against 6.5 s).

## Known limits

- Simulation only. The latch model is partly assumed (`results/w3_development/`);
  no measured force-depth curve yet.
- One latching connector family; one arm model; Menagerie's UR5e servo
  (0.2 s following lag) may lag more than a real UR5e under servoj.
- Labels for G come from simulation; there is no hardware label source yet.
