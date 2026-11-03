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
  # Frozen code (flags off). C and G: latching + latch_spread 50 trials; J latching + latch_spread 20;
  # C and G standard 25 (cut from 50 while running: the machine was shared, load average over 50).
  for B in arm gantry; do
    PYTHONPATH=. $PY $D run --backend $B --suite latching,latch_spread --trials 50 --workers 2 \
        --controllers adaptive,adaptive_learned --out $R/runs/${B}_latch_cg.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B --suite latching,latch_spread --trials 20 --workers 2 \
        --controllers spiral_rcc_verify --out $R/runs/${B}_latch_j.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B --suite standard --trials 25 --workers 2 \
        --controllers adaptive,adaptive_learned --out $R/runs/${B}_standard_cg.jsonl.gz
  done
fi

if [ "$STEP" = all ] || [ "$STEP" = candidates ]; then
  # RULE.md (2f95377): P by the re-run shortcut (acting trials + 40 controls per machine), JW and JP on every J trial.
  for B in arm gantry; do
    PYTHONPATH=. $PY experiments/v02f_tilt_select.py $R/runs/${B}_latch_cg.jsonl.gz > $R/runs/P_${B}_trials.json
    PYTHONPATH=. $PY $D run --backend $B --only $R/runs/P_${B}_trials.json --workers 2 \
        --cfg tilt_check_push_below_floor=true --out $R/runs/fix_P_$B.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B --suite latching,latch_spread --trials 20 --workers 2 \
        --controllers spiral_rcc_verify --j handover_window=true --out $R/runs/fix_JW_$B.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B --suite latching,latch_spread --trials 20 --workers 2 \
        --controllers spiral_rcc_verify --cfg tilt_check_push_below_floor=true --out $R/runs/fix_JP_$B.jsonl.gz
  done
  X="$PY experiments/v02f_tilt_compare.py"
  $X --base $R/runs/arm_latch_cg.jsonl.gz,$R/runs/gantry_latch_cg.jsonl.gz \
     --cand $R/runs/fix_P_arm.jsonl.gz,$R/runs/fix_P_gantry.jsonl.gz --bound 3 --name P > $R/CAND_P.md
  for C in JW JP; do
    $X --base $R/runs/arm_latch_j.jsonl.gz,$R/runs/gantry_latch_j.jsonl.gz \
       --cand $R/runs/fix_${C}_arm.jsonl.gz,$R/runs/fix_${C}_gantry.jsonl.gz --bound 1 --name $C > $R/CAND_$C.md
  done
fi

if [ "$STEP" = all ] || [ "$STEP" = validation ]; then
  # Seed 4007, once: P (C, G) and JW (J; the tie-break pick over JP). 20 trials per condition.
  V="--seeds 4007 --validation --suite latching,latch_spread --trials 20 --workers 2"
  for B in arm gantry; do
    PYTHONPATH=. $PY $D run --backend $B $V --controllers adaptive,adaptive_learned --out $R/runs/val_base_cg_$B.jsonl.gz
    PYTHONPATH=. $PY experiments/v02f_tilt_select.py $R/runs/val_base_cg_$B.jsonl.gz --controls 20 > $R/runs/val_P_${B}_trials.json
    PYTHONPATH=. $PY $D run --backend $B --seeds 4007 --validation --only $R/runs/val_P_${B}_trials.json --workers 2 \
        --cfg tilt_check_push_below_floor=true --out $R/runs/val_P_$B.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B $V --controllers spiral_rcc_verify --out $R/runs/val_base_j_$B.jsonl.gz
    PYTHONPATH=. $PY $D run --backend $B $V --controllers spiral_rcc_verify --j handover_window=true --out $R/runs/val_JW_$B.jsonl.gz
  done
fi

if [ "$STEP" = all ] || [ "$STEP" = identity ]; then
  # Flags off against the v0.2e code: BASE = 4df8cae exported (git archive 4df8cae defex experiments assets pyproject.toml).
  BASE=${BASE:?export 4df8cae first}
  CT="--controllers adaptive,adaptive_learned,spiral_rcc_verify,spiral_rcc --trials 10 --seed 2026 --workers 2 --no-plots"
  for B in arm gantry; do
    for S in "latching mf_noise_1mm,mf_nominal,mf_half_latched" "standard noise_1mm,tilt_5deg,yaw_5deg"; do
      set -- $S
      (cd $BASE && PYTHONPATH=$BASE $PY -m experiments.robustness --suite $1 --backend $B --conditions $2 $CT --name identity/v02e_${B}_$1)
      PYTHONPATH=. $PY -m experiments.robustness --suite $1 --backend $B --conditions $2 $CT --name v0.2f_tilt_diagnosis/identity/branch_${B}_$1
      mkdir -p $R/identity/v02e_${B}_$1 && cp $BASE/results/identity/v02e_${B}_$1/{trials.csv,summary.json,summary.csv,config.json} $R/identity/v02e_${B}_$1/
    done
  done
  $PY experiments/v02f_identity.py $R/identity $R/identity > $R/identity/IDENTITY.md
fi

if [ "$STEP" = all ] || [ "$STEP" = yaw ]; then
  # Gantry standard again with the yaw_centering events kept (collector change 2702250); rows identical to the first run.
  PYTHONPATH=. $PY $D run --backend gantry --suite standard --trials 25 --workers 2 --controllers adaptive,adaptive_learned \
      --out $R/runs/gantry_standard_cg_yaw.jsonl.gz
fi

if [ "$STEP" = all ] || [ "$STEP" = tables ]; then
  $PY experiments/v02f_tilt_tables.py $R/runs > $R/TABLES.md
  X="$PY experiments/v02f_tilt_compare.py"
  $X --base $R/runs/val_base_cg_arm.jsonl.gz,$R/runs/val_base_cg_gantry.jsonl.gz \
     --cand $R/runs/val_P_arm.jsonl.gz,$R/runs/val_P_gantry.jsonl.gz --bound 1 --name "P, seed 4007" > $R/VAL_P.md
  $X --base $R/runs/val_base_j_arm.jsonl.gz,$R/runs/val_base_j_gantry.jsonl.gz \
     --cand $R/runs/val_JW_arm.jsonl.gz,$R/runs/val_JW_gantry.jsonl.gz --bound 1 --name "JW, seed 4007" > $R/VAL_JW.md
fi
