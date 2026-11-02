#!/usr/bin/env bash
# v0.2d tilt check: the commands behind every reported number, in the order they were run.
# From the repository root. PY defaults to the shared venv of the main checkout.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PY:-../defex_robotics/.venv/bin/python}
R=results/v0.2d_tilt_check
export DEFEX_CONTROLLER_VARIANTS=$R/variants.json
STEP=${1:-all}

if [ "$STEP" = design ]; then
  # Design data (before SELECTION_RULE.md), C only, training seeds 3001-3030. The arm files were written with
  # the collector of 598dfc7 while it was still untracked on b94b971 (same content); the gantry files at 598dfc7.
  for B in arm gantry; do
    $PY -m experiments.v02d_tilt_features --backend $B --suite latching --conditions mf_noise_1mm --seeds 3001-3030 \
        --trials 40 --workers 3 --out $R/design/${B}_train_mf.jsonl.gz
    $PY -m experiments.v02d_tilt_features --backend $B --suite standard --conditions noise_1mm,noise_2mm,friction_1 \
        --seeds 3001-3030 --trials 40 --workers 3 --out $R/design/${B}_train_std.jsonl.gz
  done
fi

if [ "$STEP" = all ] || [ "$STEP" = selection ]; then
  # S1 and S2 (SELECTION_RULE.md): C and G with the check off, evidence recorded.
  for B in arm gantry; do
    $PY -m experiments.v02d_tilt_features --backend $B --suite latching,latch_spread --seeds 2026,2027 --trials 100 \
        --controllers adaptive,adaptive_learned --workers 3 --out $R/selection/${B}_s1.jsonl.gz
    $PY -m experiments.v02d_tilt_features --backend $B --suite latching --conditions mf_noise_1mm --seeds 3033-3040 \
        --trials 100 --controllers adaptive,adaptive_learned --workers 3 --out $R/selection/${B}_s2.jsonl.gz
  done
  # The trials a candidate acts on, re-run with it switched on.
  $PY -m experiments.v02d_tilt_select fired --variants $R/variants.json --out "$R/selection/reruns_{backend}.json" \
      $R/selection/arm_s1.jsonl.gz $R/selection/arm_s2.jsonl.gz $R/selection/gantry_s1.jsonl.gz $R/selection/gantry_s2.jsonl.gz
  for B in arm gantry; do
    $PY -m experiments.v02d_tilt_features --backend $B --jobs-file $R/selection/reruns_$B.json --workers 3 \
        --out $R/selection/${B}_reruns.jsonl.gz
  done
  $PY -m experiments.v02d_tilt_select table --variants $R/variants.json \
      --base $R/selection/arm_s1.jsonl.gz,$R/selection/arm_s2.jsonl.gz,$R/selection/gantry_s1.jsonl.gz,$R/selection/gantry_s2.jsonl.gz \
      --reruns $R/selection/arm_reruns.jsonl.gz,$R/selection/gantry_reruns.jsonl.gz > $R/selection/TABLES.md
fi

if [ "$STEP" = all ] || [ "$STEP" = selection_addendum ]; then
  # The collector of 91bfd9a missed latch checks after a held re-seat (92 gantry trials, none on the arm).
  # Re-run every trial a candidate acts on or with an unrecorded check, with the collector of 44ea9a7.
  $PY -m experiments.v02d_tilt_select fired --variants $R/variants.json --out "$R/selection/reruns2_{backend}.json" \
      $R/selection/arm_s1.jsonl.gz $R/selection/arm_s2.jsonl.gz $R/selection/gantry_s1.jsonl.gz $R/selection/gantry_s2.jsonl.gz
  for B in arm gantry; do
    $PY -m experiments.v02d_tilt_features --backend $B --jobs-file $R/selection/reruns2_$B.json --workers 3 \
        --out $R/selection/${B}_reruns2.jsonl.gz
  done
  $PY -m experiments.v02d_tilt_select table --variants $R/variants.json \
      --base $R/selection/arm_s1.jsonl.gz,$R/selection/arm_s2.jsonl.gz,$R/selection/gantry_s1.jsonl.gz,$R/selection/gantry_s2.jsonl.gz \
      --reruns $R/selection/arm_reruns2.jsonl.gz,$R/selection/gantry_reruns2.jsonl.gz > $R/selection/TABLES.md
fi

if [ "$STEP" = all ] || [ "$STEP" = validation ]; then
  # Validation seed 4003, once, the candidate the selection picked (selection/TABLES.md: tilt_k2).
  K=tilt_k2
  for B in arm gantry; do
    $PY -m experiments.v02d_tilt_features --validation --backend $B --suite latching,latch_spread --seeds 4003 \
        --trials 100 --controllers adaptive,adaptive_learned --workers 3 --out $R/validation/${B}.jsonl.gz
  done
  $PY -m experiments.v02d_tilt_select fired --variants $R/variants.json --candidates $K \
      --out "$R/validation/reruns_{backend}.json" $R/validation/arm.jsonl.gz $R/validation/gantry.jsonl.gz
  for B in arm gantry; do
    $PY -m experiments.v02d_tilt_features --validation --backend $B --jobs-file $R/validation/reruns_$B.json \
        --workers 3 --out $R/validation/${B}_reruns.jsonl.gz
  done
  $PY -m experiments.v02d_tilt_select table --validation --variants $R/variants.json --candidates $K \
      --base $R/validation/arm.jsonl.gz,$R/validation/gantry.jsonl.gz \
      --reruns $R/validation/arm_reruns.jsonl.gz,$R/validation/gantry_reruns.jsonl.gz > $R/validation/TABLES.md
fi
