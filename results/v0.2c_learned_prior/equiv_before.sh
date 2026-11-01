#!/usr/bin/env bash
# Rule-5 equivalence set, run on the untouched branch (54f3097) before any edit.
set -euo pipefail
cd ${ROOT:-~/projects/defex_robotics-c-lp-before}
PY=~/projects/defex_robotics/.venv/bin/python
W=${W:-2}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
R=v0.2c_learned_prior/equivalence
for b in gantry arm; do
  $PY -m experiments.robustness --backend $b --seed 2026 --trials 10 --conditions noise_1mm,noise_2mm,friction_1 \
      --controllers $ALL --name $R/before_${b}_standard --workers $W --no-plots
  $PY -m experiments.robustness --backend $b --suite latching --seed 2026 --trials 5 --controllers $ALL \
      --name $R/before_${b}_latching --workers $W --no-plots
done
