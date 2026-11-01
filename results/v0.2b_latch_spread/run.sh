#!/usr/bin/env bash
# Checkpoint 2 code (883db25) on dev seed 2027 with simulator-side latch spread. Controllers keep the drawing values.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
W=${W:-7}
CTRL=adaptive,adaptive_learned,spiral,spiral_rcc
run() {  # backend name shift peak_scale terminal_scale
  DEFEX_REVIEW_LATCH_SHIFT_MM=$3 DEFEX_REVIEW_LATCH_PEAK_SCALE=$4 DEFEX_REVIEW_TERMINAL_SCALE=$5 \
    $PY -m experiments.robustness --suite latching --backend $1 --seed 2027 --trials 20 --controllers $CTRL \
    --workers $W --no-plots --name v0.2b_latch_spread/$1_$2 > /dev/null 2>&1
  echo "$1 $2 shift=$3 peak=$4 terminal=$5" >> results/v0.2b_latch_spread/settings.txt
}
for B in gantry arm; do
  run $B nominal 0 1 1
  run $B shift-0.15 -0.15 1 1
  run $B terminal1.6 0 1 1.6
done
for S in -0.2 -0.1 0.2; do run gantry shift$S $S 1 1; done
run gantry peak0.5 0 0.5 1
run gantry peak1.5 0 1.5 1
