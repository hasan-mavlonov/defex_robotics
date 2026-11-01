#!/usr/bin/env bash
# Dev seed 2027 on the gantry, A-G. Usage: run_set.sh <before|after> <workers>
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
$PY -m experiments.robustness --backend gantry --seed 2027 --trials 10 --controllers $ALL --workers $2 --no-plots \
  --name v0.2c_gantry_baselines/$1/gantry_dev2027_standard
$PY -m experiments.robustness --suite latching --backend gantry --seed 2027 --trials 20 --controllers $ALL --workers $2 --no-plots \
  --name v0.2c_gantry_baselines/$1/gantry_dev2027_latching
