# benchmark_v0.2e pre-registration

Written and committed before the run. Nothing below changes after the first trial of
the reported seed has run. If the run exposes a bug, the bug gets a fix, a new
pre-registration and a fresh seed. No result is read until all eight runs have
finished; a run that stops early is repeated with the same command, and `RUN_LOG.md`
says so.

## Question

benchmark_v0.2d (seed 20261123) and its replication (seed 20261124) found C ahead of
every fair baseline only on the standard suite, below F on gantry latching good parts,
and matched elsewhere; the stop condition holds and Hasan decides the pitch. Their
results and headline stand; this run is reported next to them. It was run at Husan's
request on 2026-11-02 to fix three things the v0.2d review found and disclosed but did
not fix:

1. the arm's fixture dynamics depended on the previous trial in the same worker;
2. H and I's pull retry had no depth check before the second pull, no lateral
   compliance in the pull and re-push, and was not counted in `retries`;
3. C's latching tilt check had no force guard on its low-force paths.

The questions are benchmark_v0.2d's, unchanged: does C seat more good connectors, pass
fewer bad ones, or handle part-to-part variation better than the best fair baseline
(D, E, F, H, I), on both machines; does G add anything over C; and how J compares with C
and with I.

## Frozen code

- Commit **ddd0d34** on branch `v0.2e/integration`. The run may start from a later
  commit that changes only `results/`. Every `config.json` must show
  `git_dirty: false`. `RUN_LOG.md` records an empty
  `git status --porcelain --untracked-files=all` outside `results/` at the start, and
  the environment.
- Model files used by G: unchanged (sha256 values in
  `results/benchmark_v0.2d/PREREGISTRATION.md`), not retrained.
- Changes since benchmark_v0.2d (code 42df5c8), each developed on seeds 2026 and 2027
  only:
  - **Simulator** (`results/v0.2e_arm_reset`, 951c62a): payload and fixture dynamics
    are derived with the nominal grasp, then the trial's own grasp is set. On 966a5f5
    the effective mass was computed with the previous trial's grasp offset whenever a
    worker switched between a rigid-wrist and an RCC-wrist model; only
    `generalization_combined` has a grasp offset. Expected to change no outcome.
  - **H and I, pull retry rule version 5** (`results/v0.2e_pull_retry`, 78f3963): after
    the re-push, the second pull runs only if the re-push held (0.8 x 35.2 N for 0.4 s)
    and the plug is inside the depth window INSERT used to declare the seat, else the
    part is rejected; INSERT's lateral admittance also runs during the pull, re-push and
    re-seat; a pull retry adds 1 to `retries`. D and F unchanged.
  - **C, G and J, tilt-check force guard** (`results/v0.2e_tilt_guard`, c60e2a5): no
    tilt verdict when the window's mean axial force is under 11.75 N
    (= 1.0 mm x 35.2 N / (0.875 x 3.425 mm)) or the window is empty.
- **Validation on seed 4006** (`results/v0.2e_validation`, rule committed at 9113842
  before any run on it): all ten controllers, both machines, the four
  suites, 20 trials per condition, benchmark_v0.2d code against v0.2e code, 16,400
  paired trials. All three fixes kept: no controller seated fewer good parts or passed
  more bad parts or bad units; arm H seated one more good part (611 -> 612 of 680); no
  other outcome changed (`results/v0.2e_validation/REPORT.md`). Seed 4006 is spent.

## Design

- Base seed **20261130**. No `config.json` under `results/` uses it; the number
  appears only in session notes that name it as reserved.
- As benchmark_v0.2d: backends `gantry` and `arm`; controllers A-J; suites and trials
  `standard` 100, `latching` 200, `heldout` 100, `latch_spread` 100; 96,000 paired
  trials; estimated 2.3 hours (benchmark_v0.2d 2 h 16 min, the replication 2 h 18 min).
- Commands, in this order, from the repository root:

```
for B in gantry arm; do
  for S in standard:100 latching:200 heldout:100 latch_spread:100; do
    python -m experiments.robustness --suite ${S%%:*} --backend $B --trials ${S##*:} \
      --seed 20261130 --workers 9 --no-plots --name benchmark_v0.2e/${B}_${S%%:*} \
      --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
  done
done
python -m experiments.checkpoint_report results/benchmark_v0.2e > results/benchmark_v0.2e/TABLES.md
python -m experiments.cp2_audit results/benchmark_v0.2e > results/benchmark_v0.2e/AUDIT_TABLES.md
python -m experiments.v02c_paired results/benchmark_v0.2e > results/benchmark_v0.2e/PAIRED_TABLES.md
python -m experiments.v02d_headline results/benchmark_v0.2e --compare results/benchmark_v0.2d > results/benchmark_v0.2e/HEADLINE_TABLES.md
```

## Metrics and decision rules

Exactly benchmark_v0.2d's "Metrics" and "Decision rules, fixed in advance"
(`results/benchmark_v0.2d/PREREGISTRATION.md`), including: fair baselines D, E, F, H, I;
"matches" = McNemar p >= 0.05 or C ahead by less than 1 point; C reported ahead only
with p < 0.05; bad parts against the fair baseline with the fewest; bad units on
good-part trials C against H and I; G and J rules; no multiple-comparison correction,
outcomes at 0.01 <= p < 0.05 marked; Wilson upper bounds for zero counts; C's and J's
cycle time and throughput in every summary; pooled totals get no test. The report
also sets each verdict next to benchmark_v0.2d's and the replication's (different
seeds, not paired, no test across runs).

## Expected from development, stated so they are not found later

- **Outcomes as benchmark_v0.2d for A-G and J.** Fix 1 changed no outcome on seed 2027
  (all ten controllers); fix 3 changed no row on 3,840 dev trials of C, G and J and none
  of 448 trials of the other controllers.
- **Arm H seats a few more latching good parts** (dev: 336 -> 339 of 360, three
  `mf_noise_1mm` parts whose old pull pushed sideways into a protective stop). C's arm
  latching lead over H narrows; arm latching was already "matches" for the best fair
  baseline (F).
- **H and I's `retries` roughly triple** (every re-push now counts) and `recovered`
  changes accordingly; these columns are not comparable with v0.2d.
- **The depth gate and the tilt guard are expected not to change outcomes**: neither
  fired on a dev seed in a way that changed a trial (0 of 806 re-pushes failed the
  gate; the 1,120 blocked tilt verdicts were all passes).
- Headline expected as v0.2d's replication: C ahead on standard on both machines, below
  F on gantry latching good parts, a fair baseline matching C elsewhere.

## Disclosed before the run

- Everything disclosed under "Disclosed before the run" and "Known limits" in
  benchmark_v0.2d's pre-registration applies, except the three items fixed above and
  the arm `generalization_combined` reproducibility limit, which fix 1 removes.
- **Seed reuse**: seeds 2026 and 2027 have now been used for five versions of the H/I
  retry and for every v0.2e decision.
- **Fix 2 was made after benchmark_v0.2d's and the replication's results were seen**,
  as were this file's expectations. Its rule follows C's proof-push gate; the depth
  window is H and I's own INSERT window, not C's threshold (C's uses C's touch
  calibration, which H and I do not have).
- **The lateral compliance in fix 2 is lateral only**: one dev arm H part still aborts
  on torque 2 ms into the re-push. On the gantry one bad part aborted on the lateral
  limit 2.3 s into a held re-push (rejected either way), which suggests the
  zero-stiffness admittance can drift while the plug is held.
- **The tilt guard removes a failure mode that did not occur on any dev seed**; its
  value is shown only by unit tests.
- Most H and I rows differ from v0.2d at float level (final pose, peak forces), with
  few outcome changes.
