# benchmark_v0.2d pre-registration

Written and committed before the run. Nothing below changes after the first trial
of the reported seed has run. If the run exposes a bug, the bug gets a fix, a new
pre-registration and a fresh seed, and this run moves to `earlier_runs/` with its
report. No result is read until all eight runs have finished; a run that stops early
is repeated with the same command, and `RUN_LOG.md` says so.

## Question

benchmark_v0.2c found a fair baseline matching or beating C in four of eight cells
(the brief's stop condition; Hasan decides the pitch). Its results and headline stand;
this run is reported next to them, not in place of them. It was run at Husan's request
on 2026-11-01 to test three things v0.2c left open: the Micro-Fit insert target (30 N)
was below the datasheet's 32 N maximum mating force; C had a push after a slide-out that
H and I lacked; and C's VERIFY had never been tried on a fast cell. The first two were
changed, and J was added to test the third:

1. Does C seat more good connectors, pass fewer bad ones, or handle part-to-part
   variation better than the best fair baseline (D, E, F, H, I), on the gantry and
   on the UR5e arm? Does G add anything over C?
2. Does J (F's insertion, then C's VERIFY, which on latching parts can hand control to
   C's proof push and insertion) seat as many good parts as C and as I, and pass as few
   bad units as C?

## Frozen code

- Commit **42df5c8** on branch `v0.2d/integration`. The run may start from a later
  commit that changes only `results/`. Every `config.json` must show
  `git_dirty: false` (which ignores `results/` and untracked files,
  `experiments/runner.py:137`). `RUN_LOG.md` records an empty
  `git status --porcelain --untracked-files=all` outside `results/` at the start, and
  the environment: Python 3.12.11, MuJoCo 3.17.0, NumPy 2.5.4, 10 cores.
- Model files used by G (unchanged since benchmark_v0.2c, fixed by content; trained on
  C at 30 N without the tilt check, not retrained):
  - `assets/models/contact_prior_gantry.json`, sha256 `650bfd824020594afbe5a579f61942e26d00011fc90943a6695cd78af795269b`
  - `assets/models/contact_prior_arm.json`, sha256 `c17fdb80fbd305431c7e7cb7d0e7be48d6354822abef543c11a4aebc8065b3b2`
- Changes since benchmark_v0.2c (code b94b971), reports under `results/v0.2d_*`:
  - **Insert target 35.2 N** (1.1 x the datasheet's 32 N maximum) for every
    controller on the Micro-Fit (`v0.2d_force_budget`). Abort 40 N, protective stop
    48 N, damage 58 N unchanged.
  - **A, B, E on the arm**: taught overtravel uses the stiffness along the push at the
    home pose (10.8 N/mm), not the weakest direction (8.0 N/mm) (`v0.2d_axial_stiffness`).
  - **H and I**: after a failed pull, one push again at the insert target and one more
    pull, built as C's proof push (`v0.2d_pull_retry`, rule version 4, on for both on
    both machines).
  - **C and G**: a tilt check at the start of the latching VERIFY (`v0.2d_tilt_check`:
    fails when the plug axis is more than 2.5 deg off C's socket-axis estimate and the
    bottoming CoP is beyond 0.875 of the half-width; within an attempt it has already
    failed, a plug still turned more than 2.5 deg fails again whatever the CoP).
  - **J (new)**: F's insertion up to F's seat declaration, then C's VERIFY with C's
    settings and two RCC terms. After a failed check, (b) re-search: F's jam retry
    descends again at the position it found and searches, within F's 2 attempts (both
    machines); a check that fails on F's last attempt rejects the part. On a latching
    part, a hand-over after a slide-out first runs C's proof push at 35.2 N and, if the
    plug advances more than 0.1 mm, C's INSERT and DETECT. Every hand-over starts with
    C's sample window, diagnosis and fold empty (a1fc73e). Picked in `v0.2d_j_verify`,
    re-picked on this code in `v0.2d_j_repick` (dev 2026, validated on 4005).
  - Report scripts: J rules in `experiments/checkpoint_report.py`; J in
    `experiments/v02c_paired.py` and `experiments/cp2_audit.py`; new
    `experiments/v02d_headline.py`; `experiments/v02d_j_tables.py` pairs within run and
    machine.
- **Dev check before the freeze**: all ten controllers ran on dev seed 2027, 20 trials
  per condition, both machines, all four suites, at 43c8b6b (`results/v0.2d_dev_check`).
  Nothing was ranked or tuned on it. Code changes after it, all made after seeing it and
  after four review agents read the code, reports and this draft:
  - `defex/control/spiral_verify.py` (a1fc73e): the hand-over reset above. J equals
    J(b) on all 1,640 dev-2026 trials after it (`v0.2d_j_repick/equiv/COMPARE.txt`).
  - Report scripts only (`experiments/`, `tests/`); `checkpoint_report` output on
    `results/benchmark_v0.2c` and `results/v0.2d_dev_check` is byte-identical to the
    committed TABLES.md files.
- Seeds used in v0.2d development: 2026 and 2027 (every decision and the dev check),
  3001-3030 (tilt-check design), 3033-3040 (tilt-check selection), 4003 (validated J's
  first pick, the tilt check, and the withdrawn v2 retry pick), 4004 (retry v4) and 4005
  (J re-pick). 3031 and 3032 were not used in v0.2d.

## Design

- Base seed **20261123**. No controller has run on it: no `config.json` under
  `results/` uses it, and none of the trial seeds it generates appears in any
  `trials.csv` under `results/` (checked at 03dcd2c). The number appears only in
  reports that name it as reserved.
- Backends: `gantry` and `arm`.
- Controllers: A fixed, B correction, C adaptive, D spiral, E correction_rcc,
  F spiral_rcc, G adaptive_learned, H spiral_pull, I spiral_rcc_pull,
  J spiral_rcc_verify. Paired: every controller sees the same scenario for a given
  condition and trial index.
- Suites and trials per condition and controller, as benchmark_v0.2c: `standard`
  100, `latching` 200, `heldout` 100, `latch_spread` 100.
- Total: 8 runs, 2 x 10 x (20 x 100 + 7 x 200 + 5 x 100 + 9 x 100) = 96,000 trials.
  Estimated 2 to 2.5 hours (benchmark_v0.2c: 86,400 trials in 1.6 hours; J costs about
  as much per trial as C, and H and I pull twice on rejected parts). The arm runs are
  about 60% of it. The brief's 4-hour limit is not expected to be reached; if the run
  passes 4 hours, `RUN_LOG.md` says so.
- Commands, in this order, from the repository root:

```
for B in gantry arm; do
  for S in standard:100 latching:200 heldout:100 latch_spread:100; do
    python -m experiments.robustness --suite ${S%%:*} --backend $B --trials ${S##*:} \
      --seed 20261123 --workers 9 --no-plots --name benchmark_v0.2d/${B}_${S%%:*} \
      --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
  done
done
python -m experiments.checkpoint_report results/benchmark_v0.2d > results/benchmark_v0.2d/TABLES.md
python -m experiments.cp2_audit results/benchmark_v0.2d > results/benchmark_v0.2d/AUDIT_TABLES.md
python -m experiments.v02c_paired results/benchmark_v0.2d > results/benchmark_v0.2d/PAIRED_TABLES.md
python -m experiments.v02d_headline results/benchmark_v0.2d --compare results/benchmark_v0.2c > results/benchmark_v0.2d/HEADLINE_TABLES.md
```

## Metrics

Primary, per backend and suite:

1. Success rate per controller with Wilson 95% intervals; exact McNemar against C on
   paired trials. On `latching` and `latch_spread`, success on good-part conditions.
2. Bad parts passed as good on the bad-part conditions: count, Wilson 95% upper bound,
   exact McNemar of C against the fair baseline with the fewest.
3. G against C, paired.
4. J against C and J against I, paired: success on good parts; bad units passed on
   good-part trials; bad parts passed.
5. Bad units passed on good-part trials: C against H and against I, paired exact McNemar
   (`PAIRED_TABLES.md`).

Secondary: false rejects, protective stops, cycle time p50/p95/p99 of successes, good
units per hour (0 s and 60 s per protective stop), median cycle per bad part, p95 peak
force and wrist torque, per-condition successes. Good units per hour on the latching
suites count good-part cycles only, so the H/I retry's and J's extra time on rejected
parts shows only in the median cycle per bad part. p95 peak force is the ground-truth
contact force, which does not see terminal loads. Every number comes from the scripts
above; for every bad unit C, G or J passes, from `cp2_audit.py`.

## Decision rules, fixed in advance

The fair baselines are D, E, F, H and I. J is not a fair baseline: it contains C's
VERIFY. "Best" = highest success rate on that backend and suite, chosen on good parts
even if it passes most bad parts; "fewest" = fewest bad parts passed. Ties go to the
first of D, E, F, H, I (on housing-only parts F and I are identical, so F).

- If the best fair baseline matches C (McNemar p >= 0.05, or C ahead by less than 1
  point), that goes in the README headline, and Hasan decides how the pitch changes.
- If C is below the best fair baseline with p < 0.05, that goes in the README headline.
- C is reported as ahead only where it beats the best fair baseline with p < 0.05.
- Bad parts: the comparison is computed against the fair baseline with the fewest
  passed. A difference against D, E or F alone is the effect of having a pull test, not
  of C. If that baseline passes fewer than C with p < 0.05, that goes in the README
  headline.
- Bad units on good-part trials: C is reported as passing fewer than H or I only where
  p < 0.05 (metric 5).
- The part-variation question is `latch_spread`, all good parts, C against the best
  fair baseline, by the rules above. The set without `mf_terminal_max` is descriptive.
- G is reported as helping only where it beats C with p < 0.05; otherwise "no
  measurable gain", or "worse" where C beats it with p < 0.05.
- J against C and against I, per backend and suite: seated "J ahead" or "J below" only
  with p < 0.05 (direction from the discordant pairs), otherwise "J matches". There is no
  1-point margin, unlike C's rule. Bad units, on good-part trials and on bad parts
  separately: "J passes fewer" or "J passes more" only with p < 0.05, otherwise "no
  significant difference", always with counts and Wilson upper bounds. "Matches" means no
  significant difference, not equal. Whether J or C would be the product is not decided
  by this run.
- Totals pooled over suites or machines are descriptive and get no test.
- There is no correction for multiple comparisons (TABLES.md applies about 60 tests,
  PAIRED_TABLES.md about 40). Any outcome resting on 0.01 <= p < 0.05 is marked as such
  in the report.
- Zero escapes are always given with their Wilson upper bound (the upper end of the
  two-sided 95% interval).
- C's and J's cycle time and throughput are reported next to their success rate in
  every summary, including where they are worse.

## Expected from development, stated so they are not found later

- **Housing-only suites repeat benchmark_v0.2c for A-I.** No v0.2d change reaches the
  housing-only connector (`v0.2d_force_budget/EQUIVALENCE.txt`, A-I, 1,800 trials, 0
  differences; `v0.2d_tilt_check/equivalence`, C and G, 0 differences). Expect C ahead on
  `standard` and a fair baseline matching C on `heldout`, as in benchmark_v0.2c and the
  dev check (standard: C 397 vs F 384 of 400 gantry, p = 0.00024; 389 vs 381 arm,
  p = 0.039; heldout: 86 vs 81 and 83 vs 77, p = 0.38 and 0.34).
- **C's latch_spread lead is expected to close.** After the H/I retry, C-only /
  other-only on latch_spread good parts were gantry H 1 / 0, I 0 / 0; arm H 2 / 2,
  I 0 / 2 (seeds 2026 and 2027, `v0.2d_pull_retry/dev4`). Dev check: C 120 and 119 of
  120, I 120 and 120. Expect a fair baseline to match C on latch_spread on both
  machines, so that C is ahead only on `standard` and the stop condition holds in six of
  eight cells.
- **Latching good parts**: expect F or I to match or beat C (dev check: C 58 and 54 of
  60, F 60 and 56).
- **Deliberately bad parts**: C, G, H, I and J passed none in v0.2d development (dev
  check: 0 of 280 each). D and F without a pull pass most (dev check F 98 and 105 of 140).
- **Bad units on good parts**: C 0 in every v0.2d run. I 38 of 1,360 (dev 2026) and 42
  (dev check), all on housing-only conditions. H passed one latch_spread good part at
  7.39 mm (arm, seed 2027). J: 0 on dev 2026 and 4005, 1 in the dev check (gantry
  `noise_2mm` trial 11, seed 2027, also passed on the 30 N code: F's widened seat window,
  14.49 mm, 4.7 deg; the housing-only VERIFY has no tilt check or depth gate). Expect J to
  pass a few tilted housing-only plugs, far fewer than I.
- **J against C**: below C on gantry standard (dev 2026: 390 vs 400, p = 0.002; dev
  check: 387 vs 397, p = 0.002), no significant difference elsewhere in development.
  Pooled dev 2026: J 1,295, C 1,307, I 1,281 of 1,360 (J vs C 26 / 38, p = 0.17; J vs I
  30 / 16, p = 0.054).
- **Cycle**: median good cycle on dev 2026: C 7.87 s, J 7.55, I 4.77, F 4.50; good
  units per hour 400, 427, 571, 676. J costs about C's cycle on housing-only parts and
  I's on latching parts. E is slow on the gantry (2 mm/s insert).
- **Protective stops on gantry bad parts**: F and I 2 -> 38 of 280 at 35.2 N, C 11 -> 16
  (seeds 2026 and 2027); J(b) 27 against F and I's 20 of 140 (dev 2026), 23 against 18 in
  the dev check. These do not enter good units per hour.
- **G**: in the dev check (G's first run with the tilt check at 35.2 N), G helped only on
  gantry heldout (p = 0.021). In benchmark_v0.2c it helped on six of eight suites.
- **A** is mostly protective stops on the latching suites, as in benchmark_v0.2c; A, B
  and E pass most bad parts.

## Disclosed before the run

- **35.2 N is C's own factor** (1.1 x 32 N, `proof_push_factor`), chosen after
  benchmark_v0.2c. The margin is assumed; whether a real terminal tolerates 35.2 N is not
  modelled. Abort and stop were kept after development showed more stops; the
  target-to-abort margin fell from 10 N to 4.8 N.
- **Baselines not re-tuned at 35.2 N**: D, E and F's per-machine settings and the seat
  rule of D, F, H and I were selected at 30 N.
- **H and I's seat rule** is F's: a depth reading once 0.8 x 35.2 N = 28.2 N is held for
  0.08 s. A part at the datasheet's maximum terminal force (`mf_terminal_max`) crosses a
  32-33 N terminal peak; in development H and I declared these seated at 6.2-7.2 mm,
  short of the 7.5 mm snap. The pull catches these.
- **The H/I retry was designed knowing C**: it copies C's proof push (hold, speed cap,
  advance rule), built after benchmark_v0.2c showed that push was most of C's
  latch_spread lead. Four versions; each version's rule was written after seeing the
  previous version on the same dev seeds. A review found v2 ended re-pushes at 9-16 N,
  and its pick was withdrawn. H and I's re-push may run up to 6 s; C's proof push gives
  up after 1.5 s. Found by review, not changed (no good part was lost to them in
  development or validation; changing them would need a new selection):
  - after the re-push, the second pull starts wherever the re-push stopped, with no
    depth check (C gates the same case); all 1,199 re-pushes in dev4 and val4004 ended
    at 28.7 N or more;
  - on the arm, H's re-push has no lateral compliance (INSERT updates it, the pull and
    re-push do not), so side load left by the pull trips the lateral limit: 12 arm H
    re-pushes on bad parts aborted within 50 ms;
  - the pull retry is not counted in the `retries` column for H and I (C's slide-out
    retry is).
- **J's RCC terms** give C's VERIFY the plug position as encoders + F/k and enlarge the
  probe allowance by 0.346 mm; they use the F/T reading and the stage's datasheet
  stiffness (the same `CompliantStageConfig` the simulator builds the stage from, so
  J's stage model has no error), which F does not use. They were added after seed-2026
  smoke trials of C's VERIFY on F's stage; without them J(a) seated 65.6% and passed 22
  bad units (30 N code). J also uses F's uncorrected face contact as C's touch
  calibration, and C's drawing-based checks and fixture rates (not re-tuned for the RCC
  stage). J has no depth gate. The re-search retries at the same position, so it cannot
  fix yaw.
- **J's tilt check is inert in practice.** C's sample window is empty at each hand-over,
  so the check cannot fail on J's first latch check; it is live on later latch checks
  within a hand-over (after a proof push or held re-seat). On J it has never measured
  more than 0.69 deg: F aims along the camera axis and the RCC stage is modelled stiff in
  tilt, so J's tilt protection is F's insertion plus push, click and pull.
- **J's retries column** counts F's jam retries and the re-searches after a failed check
  together (dev 2026, J(b): 360 = 146 jam retries + 214 re-searches). Held re-seats and
  proof pushes inside VERIFY are not retries, for C or for J.
- **The tilt check** was selected and validated at 30 N. At 35.2 N it logged about 5,800
  verdicts in `v0.2d_j_repick` and the dev check and failed once (arm,
  `mf_terminal_max_broken_latch` trial 12, seed 2026, C). Its socket-axis estimate
  includes C's flat-face folds and jam re-aims, so a wrong fold or re-aim defeats it. On
  C's arm floor-impact path its window can be at a few newtons (no force guard). It has
  acted only on the arm; housing-only tilt escapes remain (about 1 per 3,100-3,400 noisy
  passes per machine).
- **The arm's axial stiffness** (10.76 N/mm) is computed from the simulator's arm model
  (Menagerie servo gains) at the home pose; at the seat pose, 68 mm lower, it is
  10.3-11.0 N/mm, so A, B and E's static push is about 33.7-36.0 N against the 35.2 N
  target. It stands in for a one-off push test at the work pose.
- **The damage measure does not see terminal loads**: terminal, latch and obstruction
  forces from `defex/sim/mating.py` are applied to the plug and are not in the
  ground-truth contact force.
- **A, B and E pass more bad parts** at 35.2 N (fixed overtravel, no pull); D and F also
  pass more broken-latch parts (arm latch_spread, D 79 -> 110, F 93 -> 118 of 120).
- **Seed reuse**: seeds 2026 and 2027 were used for every v0.2d decision (four retry
  versions, J's pick twice, the tilt selection, both fixes). The tilt validation on 4003
  had already started when its collector fix (44ea9a7) landed.
- **The import rule**: older `defex.sim.backend` imports in `defex/control` and
  `defex/perception` (data classes `FixtureDynamics`, `PayloadModel`, `RawSensorData`;
  the module imports no MuJoCo) break the letter of the rule "nothing under control,
  recovery or perception imports the backend". Unchanged in v0.2d.
- `config.json` records `SafetyConfig`'s 30 N / 45 N and the controller configs before
  the connector budget is applied, not the Micro-Fit's 35.2 / 40 / 48 / 58 N.
- README.md (lines 72 and 923), docs/TECHNICAL_BRIEF.md (line 52) and
  docs/HASAN_DEFENSE_NOTES.md (line 49) on this branch still describe the 30 N target;
  the update is on branch `v0.2d/docs` (577bc70), merged after the run.

## Known limits

- Simulation only. The latch model and its spread are assumed; there is no measured
  force-depth curve. The 1.1 margin over the datasheet maximum is assumed.
- One latching connector family; one arm model with Menagerie's 0.2 s servo lag.
- On the arm's `generalization_combined`, results are reproducible only to the last
  digits: the arm's fixture dynamics are computed after the previous trial's grasp offset
  in the same worker. F and I, whose code is identical on that connector, differ in 100 of
  100 trials in benchmark_v0.2c and in 10 of 20 in the dev check (cycles by milliseconds);
  no outcome has differed. The run uses 9 workers, as benchmark_v0.2c.
- No cost model for a passed bad unit.
