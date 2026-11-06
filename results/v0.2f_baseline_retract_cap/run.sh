#!/bin/zsh
# v0.2f baseline retract cap: uncapped and capped D/F/H/I/J on the same trials.
# usage: zsh results/v0.2f_baseline_retract_cap/run.sh <folder: dev|validation> <seeds...>
set -e
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
W=${WORKERS:-8}
OUT=$1; shift
export DEFEX_CONTROLLER_VARIANTS=results/v0.2f_baseline_retract_cap/variants.json
CTRL=spiral,spiral@cap,spiral_rcc,spiral_rcc@cap,spiral_pull,spiral_pull@cap,spiral_rcc_pull,spiral_rcc_pull@cap,spiral_rcc_verify,spiral_rcc_verify@cap
for SEED in "$@"; do
  for B in gantry arm; do
    for S in latching latch_spread; do
      $PY -m experiments.robustness --suite $S --backend $B --trials 20 --seed $SEED --workers $W --no-plots \
        --name v0.2f_baseline_retract_cap/$OUT/${B}_${S}_s${SEED} --controllers $CTRL
    done
  done
done
