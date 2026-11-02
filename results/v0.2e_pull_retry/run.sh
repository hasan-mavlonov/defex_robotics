#!/usr/bin/env bash
# v0.2e: H and I pull retry, rule version 5. Run from the repository root on a clean tree.
# Dev seeds 2026 and 2027 only. Seeds 4006, 20261124 and 20261130 are reserved and not used here.
#
#   PHASE=after results/v0.2e_pull_retry/run.sh      # at the v5 code: C, H, I, 20 trials per condition
#   PHASE=identity results/v0.2e_pull_retry/run.sh   # all ten controllers, seed 2027, 2 trials per condition
#
# "before" for H and I is results/v0.2d_pull_retry/dev4 (run at 1f1ca4a). H and I code is unchanged from
# 1f1ca4a to 966a5f5 (one docstring line), and identity/before (below) reproduces those rows.
# identity/before is the identity phase at 966a5f5, run from a detached worktree at that commit:
#   (in that worktree) PHASE=identity results/v0.2e_pull_retry/run.sh
# then copy its results/v0.2e_pull_retry/identity into results/v0.2e_pull_retry/identity/before here.
set -euo pipefail
PY=${PY:-python}
W=${W:-1}
case ${PHASE:-after} in
  after)
    for B in gantry arm; do
      for SEED in 2026 2027; do
        for S in latching latch_spread; do
          $PY -m experiments.robustness --backend $B --suite $S --seed $SEED --trials 20 \
              --controllers adaptive,spiral_pull,spiral_rcc_pull --workers $W --no-plots \
              --name v0.2e_pull_retry/after/${B}_${S}_s${SEED}
        done
      done
    done
    ;;
  identity)
    for B in gantry arm; do
      for S in latching latch_spread; do
        $PY -m experiments.robustness --backend $B --suite $S --seed 2027 --trials 2 \
            --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify \
            --workers $W --no-plots --name v0.2e_pull_retry/identity/${IDENT:-after}/${B}_${S}_s2027
      done
    done
    ;;
esac
# Tables: python -m experiments.v02e_pull_retry_tables > results/v0.2e_pull_retry/TABLES.md
