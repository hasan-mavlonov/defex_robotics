#!/usr/bin/env bash
# Runs on this branch (results/v0.2c_defect_verdict/after/), as run (code at afa08a4), then the
# field-by-field comparisons. Development seeds 2026 and 2027 only. Run from the repository root.
set -euo pipefail
PY=${PY:-python}
W=${W:-2}
R=v0.2c_defect_verdict/after
EQ=fixed,correction,spiral,correction_rcc,spiral_rcc
for s in 2026 2027; do
  $PY -m experiments.robustness --backend arm --suite latching --seed $s --trials 30 --controllers adaptive,adaptive_learned --name $R/arm_latching_s$s --workers $W --no-plots
  $PY -m experiments.robustness --suite latching --seed $s --trials 30 --controllers adaptive,adaptive_learned --name $R/gantry_latching_s$s --workers $W --no-plots
done
$PY -m experiments.robustness --seed 2026 --trials 10 --controllers adaptive,adaptive_learned --name $R/gantry_standard_cg --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 5 --controllers adaptive,adaptive_learned --name $R/arm_standard_cg --workers $W --no-plots
$PY -m experiments.robustness --seed 2026 --trials 10 --controllers $EQ --name $R/gantry_standard_abdef --workers $W --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers $EQ --name $R/gantry_latching_abdef --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 5 --controllers $EQ --name $R/arm_standard_abdef --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 10 --controllers $EQ --name $R/arm_latching_abdef --workers $W --no-plots
B=results/v0.2c_defect_verdict/before
A=results/v0.2c_defect_verdict/after
mkdir -p results/v0.2c_defect_verdict/equivalence
for r in gantry_standard_cg arm_standard_cg gantry_standard_abdef gantry_latching_abdef arm_standard_abdef arm_latching_abdef; do
  $PY scripts/compare_trials.py $B/$r/trials.csv $A/$r/trials.csv --ignore wall_time_s || true
done > results/v0.2c_defect_verdict/equivalence/comparison.txt
$PY -m experiments.v02c_tables > results/v0.2c_defect_verdict/tables.md
