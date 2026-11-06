#!/usr/bin/env bash
# v0.2d force budget: the exact commands, run from the repository root on a clean tree.
#   results/v0.2d_force_budget/run.sh before   # at b94b971 (benchmark_v0.2c code, insert target 30 N)
#   results/v0.2d_force_budget/run.sh after    # at 34520aa, the fix (insert target 35.2 N)
#   results/v0.2d_force_budget/run.sh tables   # equivalence check and before/after tables
# Development seeds 2026 and 2027 only; 3 workers (the machine is shared).
set -euo pipefail
PY=${PY:-python}
W=${W:-3}
R=v0.2d_force_budget
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull
STD=nominal,lateral_3mm,tilt_5deg,friction_1,generalization_combined

run_phase() {
  P=$1
  for B in gantry arm; do
    # Housing-only connector (no force budget): must be field-identical before and after.
    $PY -m experiments.robustness --backend $B --suite standard --seed 2026 --trials 10 --conditions $STD \
        --controllers $ALL --workers $W --no-plots --name $R/$P/${B}_standard_s2026
    $PY -m experiments.robustness --backend $B --suite heldout --seed 2026 --trials 10 \
        --controllers $ALL --workers $W --no-plots --name $R/$P/${B}_heldout_s2026
    for SEED in 2026 2027; do
      for S in latching latch_spread; do
        $PY -m experiments.robustness --backend $B --suite $S --seed $SEED --trials 20 \
            --controllers $ALL --workers $W --no-plots --name $R/$P/${B}_${S}_s${SEED}
      done
    done
  done
}

case "${1:-}" in
  before|after) run_phase "$1" ;;
  tables)
    for B in gantry arm; do
      for S in standard heldout; do
        $PY scripts/compare_trials.py results/$R/before/${B}_${S}_s2026/trials.csv \
            results/$R/after/${B}_${S}_s2026/trials.csv --ignore wall_time_s || true
      done
    done > results/$R/EQUIVALENCE.txt
    $PY -m experiments.v02d_force_budget_tables results/$R > results/$R/TABLES.md
    ;;
  *) echo "usage: $0 before|after|tables" >&2; exit 2 ;;
esac
