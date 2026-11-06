#!/usr/bin/env bash
# Usage: run_set.sh <label> <workers> [part...]
# Runs the before/after measurement set from the repository root at the current commit.
# Parts: arm2026 gantry_equiv arm2027 arm2027_full20 (default: all, in that order).
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
L=$1; W=$2; shift 2
PARTS=${*:-arm2026 gantry_equiv arm2027 arm2027_full20}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
STD5=nominal,lateral_3mm,noise_1mm,noise_2mm,friction_1
R=v0.2c_arm_baselines/$L
for P in $PARTS; do
  case $P in
    arm2026)
      $PY -m experiments.robustness --backend arm --seed 2026 --trials 20 --conditions $STD5 --controllers $ALL --name $R/arm_dev2026_standard5 --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 20 --controllers $ALL --name $R/arm_dev2026_latching --workers $W --no-plots ;;
    gantry_equiv)
      $PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 --controllers $ALL --name $R/gantry_rule3_standard --workers $W --no-plots
      $PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers $ALL --name $R/gantry_rule3_latching --workers $W --no-plots ;;
    arm2027)
      $PY -m experiments.robustness --backend arm --seed 2027 --trials 20 --conditions $STD5 --controllers $ALL --name $R/arm_dev2027_standard5 --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --suite latching --seed 2027 --trials 20 --controllers $ALL --name $R/arm_dev2027_latching --workers $W --no-plots ;;
    arm2027_full20)
      $PY -m experiments.robustness --backend arm --seed 2027 --trials 5 --controllers $ALL --name $R/arm_dev2027_standard20 --workers $W --no-plots ;;
  esac
done
