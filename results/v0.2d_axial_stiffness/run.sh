#!/usr/bin/env bash
# v0.2d: taught overtravel along the insertion axis (commit 4748791). Arm only; the gantry is 10 N/mm
# on every axis, so nothing changes there. Compared with results/v0.2d_force_budget/after (34520aa).
# adaptive and spiral_rcc_pull do not read the overtravel and must come out field-identical.
set -euo pipefail
PY=${PY:-python}
W=${W:-3}
for SEED in 2026 2027; do
  for S in latching latch_spread; do
    $PY -m experiments.robustness --backend arm --suite $S --seed $SEED --trials 20 \
        --controllers fixed,correction,correction_rcc,adaptive,spiral_rcc_pull --workers $W --no-plots \
        --name v0.2d_axial_stiffness/arm_${S}_s${SEED}
  done
done
