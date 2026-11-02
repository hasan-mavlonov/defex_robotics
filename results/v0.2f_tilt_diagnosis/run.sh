#!/usr/bin/env bash
# v0.2f tilt diagnosis: the commands behind every reported number, in the order they were run.
# From the repository root. Dev seeds 2026 and 2027 unless a step says otherwise. --workers 2.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-../defex_robotics/.venv/bin/python}
R=results/v0.2f_tilt_diagnosis
D="experiments/v02f_tilt_diag.py"
STEP=${1:-all}

if [ "$STEP" = all ] || [ "$STEP" = trace ]; then
  # The three trials results/benchmark_v0.2e/REPORT.md names (seed 20261130, diagnosis only).
  PYTHONPATH=. $PY $D trace --backend arm --condition mf_noise_1mm --controller adaptive_learned --index 130 \
      --seed 20261130 --events --ticks $R/traces/g_mf_noise_1mm_130.json.gz > $R/traces/g_mf_noise_1mm_130.txt
  PYTHONPATH=. $PY $D trace --backend arm --condition mf_noise_1mm --controller adaptive --index 130 \
      --seed 20261130 --events > $R/traces/c_mf_noise_1mm_130.txt
  PYTHONPATH=. $PY $D trace --backend arm --condition mf_noise_1mm --controller spiral_rcc_verify --index 46 \
      --seed 20261130 --events > $R/traces/j_mf_noise_1mm_46.txt
fi

if [ "$STEP" = all ] || [ "$STEP" = dev ]; then
  # Frozen code (flags off). C and G: latching + latch_spread 50 trials, standard 50 trials; J latching 20.
  for B in arm gantry; do
    PYTHONPATH=. $PY $D run --backend $B --suite latching,latch_spread --trials 50 --workers 2 \
        --controllers adaptive,adaptive_learned --out $R/runs/${B}_latch_cg.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B --suite latching,latch_spread --trials 20 --workers 2 \
        --controllers spiral_rcc_verify --out $R/runs/${B}_latch_j.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B --suite standard --trials 50 --workers 2 \
        --controllers adaptive,adaptive_learned --out $R/runs/${B}_standard_cg.jsonl.gz
  done
fi
