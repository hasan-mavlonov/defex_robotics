#!/bin/zsh
# v0.2f pull overshoot, development seeds only. One machine per chain, single process each.
# usage: zsh results/v0.2f_realtime/pull/run.sh gantry|arm
set -e
cd "$(dirname "$0")/../../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
B=$1
for SEED in 2026 2027; do
  for SUITE in latching latch_spread; do
    PYTHONPATH=. $PY -m experiments.v02f_pull_overshoot --backend $B --suite $SUITE --seed $SEED --trials 20 \
      --traces 3 --out results/v0.2f_realtime/pull/${B}_${SUITE}_s${SEED}
  done
done
