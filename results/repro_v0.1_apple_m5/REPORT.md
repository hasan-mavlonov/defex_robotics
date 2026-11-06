# Reproduction of benchmark_v0.1 on Apple Silicon

Purpose: check that the reported V0.1 numbers do not depend on the machine
(README limitation 9). This is a reproduction, not a new benchmark: same code,
same seed, same conditions.

| | Reported run | This run |
|---|---|---|
| Code | commit `4510f7f` (results-only commits after it) | commit `ad47676` (main, same controller and physics code) |
| Seed | 20261025 | 20261025 |
| Machine | Linux x86-64, 4 vCPU | Apple M5, 10 cores, macOS 27.0.1 (arm64) |
| Python / MuJoCo / NumPy | 3.12.3 / 3.16.0 / 2.5.4 | 3.12.11 / 3.17.0 / 2.5.4 |
| Trials | 6,000 | 6,000 |
| Wall time | 27 min on 4 workers | 3 min 57 s on 9 workers |

Command: `python -m experiments.robustness --trials 100 --seed 20261025 --name dev_repro_m5 --workers 9 --no-plots`

## Result

| Controller | Successes, reported | Successes, this run | Same success outcome, trial by trial | Trials with identical cycle time and peak force |
|---|---|---|---|---|
| A: fixed | 470 / 2,000 | 470 / 2,000 | 2,000 / 2,000 | 0 |
| B: correction | 1,718 / 2,000 | 1,718 / 2,000 | 2,000 / 2,000 | 48 |
| C: adaptive | 1,985 / 2,000 | 1,985 / 2,000 | 2,000 / 2,000 | 0 |

C: 0 protective stops and 0 false accepts in both runs.

Every trial has the same success outcome on both machines. No trial is identical
in every field (B has 48 trials whose cycle time and peak force match exactly);
floating-point values differ in the last digits, as expected across CPU
architectures and MuJoCo 3.16 vs 3.17, so the runs are not bit-identical. The
rates agree exactly, which is stronger than "within their confidence intervals".

Files: `trials.csv`, `summary.json`, `summary.csv`, `config.json` from this run.
