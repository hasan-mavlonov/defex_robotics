#!/bin/sh
# results/v0.2d_j_verify: the exact commands, run from the repository root with --workers 3.
# Each config.json names its commit and shows git_dirty false.
set -e
PY=${PY:-python}
CTRL=adaptive,spiral_rcc,spiral_rcc_pull,spiral_rcc_verify_reject,spiral_rcc_verify_research,spiral_rcc_verify_reject_no_rcc

# 1. C and G across the structural refactor of adaptive_fsm.py (_begin_attempt):
#    "before" at b94b971, "after" at ca19980 (the refactor alone).
for W in before after; do
  for B in gantry arm; do
    for S in standard latching; do
      $PY -m experiments.robustness --suite $S --backend $B --trials 10 --seed 2026 --workers 3 --no-plots \
        --name v0.2d_j_verify/equivalence/$W/${B}_${S} --controllers adaptive,adaptive_learned
    done
  done
done
for B in gantry arm; do
  for S in standard latching; do
    $PY scripts/compare_trials.py results/v0.2d_j_verify/equivalence/before/${B}_${S}/trials.csv \
      results/v0.2d_j_verify/equivalence/after/${B}_${S}/trials.csv
  done
done > results/v0.2d_j_verify/equivalence/COMPARE.txt

# 2. Dev seeds. 2026 ranks J's two candidates (SELECTION_RULE.md, committed before this run).
for SEED in 2026 2027; do
  for B in gantry arm; do
    for S in standard latching heldout latch_spread; do
      $PY -m experiments.robustness --suite $S --backend $B --trials 20 --seed $SEED --workers 3 --no-plots \
        --name v0.2d_j_verify/dev$SEED/${B}_${S} --controllers $CTRL
    done
  done
done

# 3. Validation seed 4003, once, after the pick is committed: both candidates (F for the hand-over check).
for B in gantry arm; do
  for S in standard latching heldout latch_spread; do
    $PY -m experiments.robustness --suite $S --backend $B --trials 20 --seed 4003 --workers 3 --no-plots \
      --name v0.2d_j_verify/val4003/${B}_${S} --controllers spiral_rcc,spiral_rcc_verify_reject,spiral_rcc_verify_research
  done
done

# 4. Tables.
$PY -m experiments.v02d_j_tables results/v0.2d_j_verify > results/v0.2d_j_verify/TABLES.md
