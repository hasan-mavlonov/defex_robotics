#!/bin/sh
# Review, second batch: smaller snap shifts, and terminal friction at the datasheet maximum
# (8 N per circuit peak instead of the model's 5 N: scale 1.6). Sim side only. Dev seed 2026.
set -e
PY=~/projects/defex_robotics/.venv/bin/python
COND=mf_nominal,mf_moderate,mf_noise_1mm
run() { # name scale shift tscale backend
  DEFEX_REVIEW_LATCH_PEAK_SCALE=$2 DEFEX_REVIEW_LATCH_SHIFT_MM=$3 DEFEX_REVIEW_TERMINAL_SCALE=$4 $PY -m experiments.robustness \
    --suite latching --backend $5 --seed 2026 --trials 20 --workers 3 --conditions $COND --controllers adaptive,spiral_rcc \
    --name v0.2c_review_fairness/latch_spread/$5_$1 --no-plots
}
for b in gantry arm; do
  run shift-0.1 1 -0.1 1 $b
  run shift-0.15 1 -0.15 1 $b
  run terminal1.6 1 0 1.6 $b
done
