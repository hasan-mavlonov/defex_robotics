#!/usr/bin/env bash
# v0.2d: H and I retry a failed pull once (commit 02ece67). Compared with results/v0.2d_force_budget/after (34520aa).
# D (spiral) and C (adaptive) do not run the H/I pull and must come out field-identical.
set -euo pipefail
PY=${PY:-python}
W=${W:-3}
for B in gantry arm; do
  for SEED in 2026 2027; do
    for S in latching latch_spread; do
      $PY -m experiments.robustness --backend $B --suite $S --seed $SEED --trials 20 \
          --controllers spiral,adaptive,spiral_pull,spiral_rcc_pull --workers $W --no-plots \
          --name v0.2d_pull_retry/${B}_${S}_s${SEED}
    done
  done
done
