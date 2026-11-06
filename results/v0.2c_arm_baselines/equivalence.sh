#!/usr/bin/env bash
# Field identity of everything not meant to change (scripts/compare_trials.py, wall_time_s ignored).
# Gantry: all seven controllers on the rule-3 set. Arm: A, B, C and G on every arm set.
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
R=results/v0.2c_arm_baselines
mkdir -p $R/equivalence
for s in gantry_rule3_standard gantry_rule3_latching; do
  $PY scripts/compare_trials.py $R/before/$s/trials.csv $R/after/$s/trials.csv --ignore wall_time_s
done > $R/equivalence/gantry_all_controllers.txt
for s in arm_dev2026_standard5 arm_dev2026_latching arm_dev2027_standard5 arm_dev2027_latching arm_dev2027_standard20; do
  for c in fixed correction adaptive adaptive_learned; do
    $PY scripts/compare_trials.py $R/before/$s/trials.csv $R/after/$s/trials.csv --ignore wall_time_s --pair $c,$c | sed "s/^/$c: /"
  done
done > $R/equivalence/arm_A_B_C_G.txt
cat $R/equivalence/*.txt
