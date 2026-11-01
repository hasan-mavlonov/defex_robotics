#!/bin/sh
# Review: C (and G) on the latching good parts with the simulator's latch ramp perturbed
# (sim side only; the controller keeps the connector JSON values). Dev seed 2026.
set -e
PY=~/projects/defex_robotics/.venv/bin/python
COND=mf_nominal,mf_moderate,mf_noise_1mm
run() { # name scale shift backend
  DEFEX_REVIEW_LATCH_PEAK_SCALE=$2 DEFEX_REVIEW_LATCH_SHIFT_MM=$3 $PY -m experiments.robustness --suite latching \
    --backend $4 --seed 2026 --trials 20 --workers 3 --conditions $COND --controllers adaptive,spiral_rcc \
    --name v0.2c_review_fairness/latch_spread/$4_$1 --no-plots
}
for b in gantry arm; do
  run nominal 1 0 $b
  run peak0.5 0.5 0 $b
  run peak0.35 0.35 0 $b
  run shift-0.2 1 -0.2 $b
  run shift+0.2 1 0.2 $b
done
