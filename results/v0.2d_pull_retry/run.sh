#!/usr/bin/env bash
# v0.2d: H and I retry a failed pull once. Run from the repository root on a clean tree.
#   PHASE=dev  results/v0.2d_pull_retry/run.sh               # seeds 2026, 2027 (retry on, both machines)
#   PHASE=val4003 SEEDS=4003 results/v0.2d_pull_retry/run.sh  # once, with the pick registered
# v1/ holds the first retry version (02ece67, run at fd77f86), before the stall rule.
# D (spiral) and C (adaptive) do not run the H/I pull and must come out field-identical.
set -euo pipefail
PY=${PY:-python}
W=${W:-3}
SEEDS=${SEEDS:-"2026 2027"}
for B in gantry arm; do
  for SEED in $SEEDS; do
    for S in latching latch_spread; do
      $PY -m experiments.robustness --backend $B --suite $S --seed $SEED --trials 20 \
          --controllers ${CTRL:-spiral,adaptive,spiral_pull,spiral_rcc_pull} --workers $W --no-plots \
          --name v0.2d_pull_retry/${PHASE:-dev}/${B}_${S}_s${SEED}
    done
  done
done
# Retry off on seed 4003 (validation comparator, gantry I only), at 34520aa in a separate worktree:
#   for S in latching latch_spread; do python -m experiments.robustness --backend gantry --suite $S --seed 4003 \
#     --trials 20 --controllers spiral_rcc_pull --workers 3 --no-plots --name val4003_off/gantry_${S}_s4003; done
# then copy results/val4003_off into results/v0.2d_pull_retry/val4003_off.
