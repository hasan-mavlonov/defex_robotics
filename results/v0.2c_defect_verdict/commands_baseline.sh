#!/usr/bin/env bash
# Baseline runs on the untouched code (commit 54f3097), in a temporary detached worktree
# (~/projects/defex_robotics-c-defect-verdict-base). Outputs were copied to
# results/v0.2c_defect_verdict/before/. Development seeds 2026 and 2027 only. The first run of this
# script was killed from outside during gantry_standard_abdef (BrokenProcessPool); that run and the
# three after it were run again with --workers 1. Run-to-run results do not depend on the worker count.
set -euo pipefail
PY=${PY:-python}
W=${W:-2}
R=v0.2c_defect_verdict/before
EQ=fixed,correction,spiral,correction_rcc,spiral_rcc
for s in 2026 2027; do
  $PY -m experiments.robustness --suite latching --seed $s --trials 30 --controllers adaptive,adaptive_learned \
      --name $R/gantry_latching_s$s --workers $W --no-plots
  $PY -m experiments.robustness --backend arm --suite latching --seed $s --trials 30 --controllers adaptive,adaptive_learned \
      --name $R/arm_latching_s$s --workers $W --no-plots
done
# Standard suite, C and G (must stay field-identical): all 20 conditions.
$PY -m experiments.robustness --seed 2026 --trials 10 --controllers adaptive,adaptive_learned \
    --name $R/gantry_standard_cg --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 5 --controllers adaptive,adaptive_learned \
    --name $R/arm_standard_cg --workers $W --no-plots
# A, B, D, E, F on both backends and both suites (must stay field-identical).
$PY -m experiments.robustness --seed 2026 --trials 10 --controllers $EQ --name $R/gantry_standard_abdef --workers $W --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers $EQ --name $R/gantry_latching_abdef --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 5 --controllers $EQ --name $R/arm_standard_abdef --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 10 --controllers $EQ --name $R/arm_latching_abdef --workers $W --no-plots
