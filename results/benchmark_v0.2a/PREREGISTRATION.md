# benchmark_v0.2a pre-registration

Written and committed before the run. Nothing below may change after the first
trial of the reported seed has run. If the run exposes a bug, the fix gets a new
pre-registration and a fresh seed, and this run's report moves to
`earlier_runs/`.

## Question

Does controller C still beat conventional cells once those cells get the tools
real connector lines use: force-controlled spiral search (D), a passive remote
centre compliance device (E), and both (F)? And if the success gap closes, what
is left: bad units passed, cycle time, throughput, contact force?

## Frozen code

- Controller commit: **56707fa** (the run may start from a later commit that changes only results/) (branch `v0.2/w1-fair-baselines`). The
  run's `config.json` must show this commit and `git_dirty: false`.
- C is V0.1's controller unchanged, except that every controller now uses the
  payload identified from F/T readings (W0) instead of the simulator's mass.
- D, E and F use the settings selected by the tuning in
  [`tuning/`](tuning) and recorded in [`BASELINE_TUNING.md`](BASELINE_TUNING.md).
  Tuning used development seed 2026 only.

## Design

- Seed: **20261031**. It has never been run with any controller.
- Conditions: the 20 standard conditions of V0.1 (`defex/tasks/conditions.py`),
  unchanged, including the two generalization conditions.
- Controllers: A `fixed`, B `correction`, C `adaptive`, D `spiral`,
  E `correction_rcc`, F `spiral_rcc`.
- Trials: 100 per condition and controller, paired (identical socket, grasp and
  sensor noise per trial index across controllers): 12,000 trials.
- Command: `python -m experiments.robustness --trials 100 --seed 20261031 --name benchmark_v0.2a --record 1`
- Physics, sensing, safety limits and success criteria: unchanged from V0.1.
  E and F run on the RCC stage in `CompliantStageConfig`; the others on the
  stiff wrist.

## Metrics

Primary:

1. Overall success rate per controller, with Wilson 95% intervals.
2. Paired comparison of each controller with C: discordant pair counts and the
   two-sided exact McNemar p-value.

Secondary (all reported, none used to pick a winner after the fact):

3. Bad units passed (escapes): failed, no protective stop, no declared failure.
4. Detected failures, protective stops, false accepts, false rejects.
5. Cycle time of successes: p50, p95, p99.
6. Good units per hour of cell time, with 0 s and with an assumed 60 s of
   operator time per protective stop.
7. 95th percentile of peak contact force, peak wrist torque.
8. Per-condition success with Wilson intervals.

## Decision rules, fixed in advance

- **A fair baseline matches C** if, for D, E or F, the McNemar test against C
  gives p >= 0.05, or C's overall success exceeds it by less than 1.0
  percentage point. If that happens the work stops and Hasan decides how the
  pitch changes (brief, section 7). The README headline is then about
  verification, escapes and contact force, not success rate.
- Otherwise the README states C's success advantage over the strongest of
  D, E, F, with its paired p-value, next to the escape, throughput and cycle-time
  numbers, including any where C is worse.
- Results worse than V0.1 for C (it cannot be compared on the same seed, so
  this means rates outside V0.1's intervals) are reported in the README.

## Known limits of this run

- No terminal or latch physics yet (W3). Verification is still the wall probe.
- Vision accuracy is still correctly characterized (W2 adds the mis-characterized case).
- One connector family; gantry fixture only.
