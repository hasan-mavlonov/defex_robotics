#!/usr/bin/env bash
# Development snapshot A-G, both backends, standard (20 conditions), latching and heldout suites,
# 20 trials per cell. Usage: snapshot.sh <seed> <workers>   (2026 dev; 3032 once, out of sample)
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
SEED=$1; W=$2
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
R=v0.2c_integration/snapshot_seed$SEED
for B in gantry arm; do
  for S in standard latching heldout; do
    $PY -m experiments.robustness --suite $S --backend $B --trials 20 --seed $SEED --workers $W \
        --controllers $ALL --name $R/${B}_$S --no-plots
  done
done
$PY -m experiments.checkpoint_report results/$R > results/$R/TABLES.md
