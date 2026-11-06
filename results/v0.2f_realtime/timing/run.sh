#!/bin/zsh
# v0.2f tick timing, development seeds only, single process. usage: zsh run.sh <label>  (e.g. run1, run2)
set -e
cd "$(dirname "$0")/../../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
RAW=${RAW:-/private/tmp/claude-501/v02f_timing_raw}
for B in gantry arm; do
  uptime
  PYTHONPATH=. $PY -m experiments.v02f_tick_timing --backend $B --seeds 2026,2027 \
    --suites standard,latching,latch_spread --trials 2 --replays 3 \
    --out results/v0.2f_realtime/timing/$1_$B --raw $RAW/$1_$B.npz
  uptime
done
