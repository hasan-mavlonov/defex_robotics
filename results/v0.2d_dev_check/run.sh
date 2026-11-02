#!/bin/sh
# results/v0.2d_dev_check: all ten controllers (A-J) on the integrated v0.2d code, dev seed 2027, before the
# benchmark_v0.2d freeze. Not a selection: nothing is ranked or tuned on these runs. Run from the repository root.
set -e
PY=${PY:-python}
W=${W:-9}
CTRL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
for B in gantry arm; do
  for S in standard latching heldout latch_spread; do
    $PY -m experiments.robustness --suite $S --backend $B --trials 20 --seed 2027 --workers $W --no-plots \
      --name v0.2d_dev_check/${B}_${S} --controllers $CTRL
  done
done
$PY -m experiments.checkpoint_report results/v0.2d_dev_check > results/v0.2d_dev_check/TABLES.md
