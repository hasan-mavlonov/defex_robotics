#!/usr/bin/env bash
# v0.2e tilt guard: the commands behind every reported number, in the order they were run.
# From the repository root. PY defaults to the shared venv of the main checkout. Dev seeds 2026 and 2027 only.
# The collector is run by path, so the code under test is the one on PYTHONPATH:
#   before = 966a5f5 exported to $BASE (git archive), after = this tree.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-../defex_robotics/.venv/bin/python}
R=results/v0.2e_tilt_guard
BASE=${BASE:?export 966a5f5 first: mkdir -p \$BASE; git archive 966a5f5 defex experiments assets pyproject.toml | tar -x -C \$BASE}
HERE=$(pwd)
G="experiments/v02e_tilt_guard.py run --suite latching,latch_spread --seeds 2026,2027 --trials 20 --workers 1"
STEP=${1:-all}
# As run: arm before/after and gantry before at --workers 1; gantry after at --workers 6 (CPU freed); the
# "others" runs at --workers 2 (arm) and 1 (gantry), before and after at the same time (each trial builds its own controller and scenario).

if [ "$STEP" = all ] || [ "$STEP" = c_family ]; then
  # C, G and J, both machines, latching + latch_spread (16 conditions), 20 trials, seeds 2026 and 2027.
  for B in arm gantry; do
    PYTHONPATH=$BASE $PY $G --backend $B --controllers adaptive,adaptive_learned,spiral_rcc_verify \
        --out $R/runs/${B}_before.jsonl.gz
    PYTHONPATH=$HERE $PY $G --backend $B --controllers adaptive,adaptive_learned,spiral_rcc_verify \
        --out $R/runs/${B}_after.jsonl.gz
  done
  PYTHONPATH=$HERE $PY experiments/v02e_tilt_guard.py table \
      --before $R/runs/arm_before.jsonl.gz,$R/runs/gantry_before.jsonl.gz \
      --after $R/runs/arm_after.jsonl.gz,$R/runs/gantry_after.jsonl.gz > $R/TABLES.md
fi

if [ "$STEP" = all ] || [ "$STEP" = others ]; then
  # Every other controller of the benchmark (A, B, D, E, F, H, I): latching + latch_spread, 2 trials, seed 2026.
  O="--seeds 2026 --trials 2 --chunk 2 --controllers fixed,correction,spiral,correction_rcc,spiral_rcc,spiral_pull,spiral_rcc_pull"
  for B in arm gantry; do
    PYTHONPATH=$BASE $PY $G $O --backend $B --out $R/runs/others_${B}_before.jsonl.gz
    PYTHONPATH=$HERE $PY $G $O --backend $B --out $R/runs/others_${B}_after.jsonl.gz
  done
  PYTHONPATH=$HERE $PY experiments/v02e_tilt_guard.py table \
      --before $R/runs/others_arm_before.jsonl.gz,$R/runs/others_gantry_before.jsonl.gz \
      --after $R/runs/others_arm_after.jsonl.gz,$R/runs/others_gantry_after.jsonl.gz > $R/OTHERS.md
fi
