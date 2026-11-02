#!/bin/sh
# results/v0.2d_j_repick: the exact commands, run from the repository root.
# PHASE=dev: dev seed 2026, ranks J's candidates (SELECTION_RULE.md, committed before this run).
# PHASE=val: validation seed 4005, once, after the pick is committed.
set -e
PY=${PY:-python}
W=${W:-9}
case "$PHASE" in
  dev) SEED=2026; RUN=dev2026; CTRL=adaptive,spiral_rcc,spiral_rcc_pull,spiral_rcc_verify_reject,spiral_rcc_verify_research ;;
  val) SEED=4005; RUN=val4005; CTRL=spiral_rcc,spiral_rcc_verify_reject,spiral_rcc_verify_research ;;
  *) echo "PHASE=dev or PHASE=val"; exit 2 ;;
esac
for B in gantry arm; do
  for S in standard latching heldout latch_spread; do
    $PY -m experiments.robustness --suite $S --backend $B --trials 20 --seed $SEED --workers $W --no-plots \
      --name v0.2d_j_repick/$RUN/${B}_${S} --controllers $CTRL
  done
done
