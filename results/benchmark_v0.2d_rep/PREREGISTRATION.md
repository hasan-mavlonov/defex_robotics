# benchmark_v0.2d_rep pre-registration

Written and committed before the run, and after benchmark_v0.2d's results were seen.
Nothing below changes after the first trial of the reported seed has run.

## Question

Do benchmark_v0.2d's verdicts hold on a second fresh seed, with the same code? This run
does not replace benchmark_v0.2d: the README headline and every pre-registered verdict
come from benchmark_v0.2d. This run is reported next to it.

## Frozen code

- Code as benchmark_v0.2d: commit **42df5c8** (branch `v0.2d/integration`). The run starts
  from the commit that adds this file, which changes only `results/`. Every `config.json`
  must show `git_dirty: false`.
- Model files used by G: as benchmark_v0.2d (sha256 values in its PREREGISTRATION.md).

## Design

- Base seed **20261124**. No `config.json` under `results/` uses it.
- Everything else as benchmark_v0.2d: backends `gantry` and `arm`; controllers A-J; suites
  and trials `standard` 100, `latching` 200, `heldout` 100, `latch_spread` 100; 96,000
  trials; `--workers 9`.
- Commands, in this order, from the repository root:

```
for B in gantry arm; do
  for S in standard:100 latching:200 heldout:100 latch_spread:100; do
    python -m experiments.robustness --suite ${S%%:*} --backend $B --trials ${S##*:} \
      --seed 20261124 --workers 9 --no-plots --name benchmark_v0.2d_rep/${B}_${S%%:*} \
      --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
  done
done
python -m experiments.checkpoint_report results/benchmark_v0.2d_rep > results/benchmark_v0.2d_rep/TABLES.md
python -m experiments.cp2_audit results/benchmark_v0.2d_rep > results/benchmark_v0.2d_rep/AUDIT_TABLES.md
python -m experiments.v02c_paired results/benchmark_v0.2d_rep > results/benchmark_v0.2d_rep/PAIRED_TABLES.md
python -m experiments.v02d_headline results/benchmark_v0.2d_rep --compare results/benchmark_v0.2d > results/benchmark_v0.2d_rep/HEADLINE_TABLES.md
```

## Metrics and decision rules

Exactly benchmark_v0.2d's metrics 1-5 and decision rules, applied to this seed alone.

## How the two seeds are compared, fixed in advance

- For each verdict benchmark_v0.2d's rules produce (per backend and suite: C against
  the best fair baseline on success; C against H and I on bad parts passed; C against H
  and I on good-part escapes; G against C; J against C and against I, seated and bad
  units), the report gives the verdict on each seed side by side.
- A verdict **replicates** if both seeds give the same class (ahead, matches, below; or
  passes fewer, no significant difference, passes more). Otherwise it is reported as
  **not replicated**, with both results.
- "Best fair baseline" is chosen on each seed separately by benchmark_v0.2d's rule; where
  the two seeds pick different baselines, the report says so.
- No test is run on the two seeds pooled. No multiple-comparison correction.
- benchmark_v0.2d's verdicts are not changed by this run. If a v0.2d verdict does not
  replicate, the README says so next to it.

## Disclosed before the run

- Everything disclosed in benchmark_v0.2d's pre-registration applies unchanged.
- This file was written after benchmark_v0.2d's results were seen. The seed, design and
  comparison rule do not depend on them.
- The arm `generalization_combined` load-history limit (benchmark_v0.2d, Known limits)
  applies: results on that condition depend on worker order in the last digits.
