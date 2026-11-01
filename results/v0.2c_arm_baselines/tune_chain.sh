#!/usr/bin/env bash
# The arm tuning protocol of SELECTION_RULE.md, in order. Usage: tune_chain.sh <workers> [controller...]
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
W=$1; shift
CTRLS=${*:-spiral spiral_rcc correction_rcc}
FROM=${FROM:-coarse}  # resume a controller at this stage (amendment 1: D resumed at speed2)
T="--backend arm --out v0.2c_arm_baselines/tuning --workers $W"
for C in $CTRLS; do
  if [ "$C" = correction_rcc ]; then
    $PY -m experiments.tune_baselines $T --controller $C --stage coarse --trials 3
    $PY -m experiments.tune_baselines $T --controller $C --stage confirm --trials 10 --top 3
  else
    if [ "$FROM" = coarse ]; then
      $PY -m experiments.tune_baselines $T --controller $C --stage coarse --trials 3
      $PY -m experiments.tune_baselines $T --controller $C --stage fine --trials 3 --top 3
      $PY -m experiments.tune_baselines $T --controller $C --stage speed --trials 3 --top 1
    fi
    $PY -m experiments.tune_baselines $T --controller $C --stage speed2 --trials 3 --top 1
    $PY -m experiments.tune_baselines $T --controller $C --stage confirm --trials 10 --top 3
  fi
  FROM=coarse
done
