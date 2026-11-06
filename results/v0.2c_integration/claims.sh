#!/usr/bin/env bash
# Re-runs each workstream's own after-runs on the integrated code, same seeds, conditions and trial counts.
# Usage: claims.sh <label> <workers> [part...]   Output: results/v0.2c_integration/<label>/
# Parts: ab (arm-baselines' run_set: all 7 controllers), dv (defect-verdict's C/G runs). Dev seeds 2026, 2027 only.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
L=$1; W=$2; shift 2
PARTS=${*:-ab dv}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
STD5=nominal,lateral_3mm,noise_1mm,noise_2mm,friction_1
R=v0.2c_integration/$L
for P in $PARTS; do
  case $P in
    ab)
      $PY -m experiments.robustness --backend arm --seed 2026 --trials 20 --conditions $STD5 --controllers $ALL --name $R/arm_dev2026_standard5 --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 20 --controllers $ALL --name $R/arm_dev2026_latching --workers $W --no-plots
      $PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 --controllers $ALL --name $R/gantry_rule3_standard --workers $W --no-plots
      $PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers $ALL --name $R/gantry_rule3_latching --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --seed 2027 --trials 20 --conditions $STD5 --controllers $ALL --name $R/arm_dev2027_standard5 --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --suite latching --seed 2027 --trials 20 --controllers $ALL --name $R/arm_dev2027_latching --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --seed 2027 --trials 5 --controllers $ALL --name $R/arm_dev2027_standard20 --workers $W --no-plots ;;
    dv)
      for s in 2026 2027; do
        $PY -m experiments.robustness --backend arm --suite latching --seed $s --trials 30 --controllers adaptive,adaptive_learned --name $R/arm_latching_s$s --workers $W --no-plots
        $PY -m experiments.robustness --suite latching --seed $s --trials 30 --controllers adaptive,adaptive_learned --name $R/gantry_latching_s$s --workers $W --no-plots
      done
      $PY -m experiments.robustness --seed 2026 --trials 10 --controllers adaptive,adaptive_learned --name $R/gantry_standard_cg --workers $W --no-plots
      $PY -m experiments.robustness --backend arm --seed 2026 --trials 5 --controllers adaptive,adaptive_learned --name $R/arm_standard_cg --workers $W --no-plots ;;
  esac
done
