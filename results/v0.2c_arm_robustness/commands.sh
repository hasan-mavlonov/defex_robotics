#!/usr/bin/env bash
# Every command behind results/v0.2c_arm_robustness, in the order it was run. Seeds: 2026 (diagnosis and
# development), 4002 (validation, pre-registered selection), 2027 (confirmation). No other seed was run.
# Runs were made from detached worktrees at the commit named in each output folder (config.json), so that
# editing the branch could not change a running job; outputs were copied here unchanged.
# Arm runs need the Menagerie UR5e (scripts/fetch_menagerie.py).
set -euo pipefail
PY=${PY:-python}
W=${W:-2}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
S5=nominal,lateral_3mm,noise_1mm,noise_2mm,friction_1
R=v0.2c_arm_robustness

# 1. Before: untouched code, commit 54f3097 (v0.2/checkpoint2 frozen state), detached worktree.
$PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 --controllers $ALL --name $R/before/gantry_rule3_standard_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers $ALL --name $R/before/gantry_rule3_latching_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 20 --conditions $S5 --controllers $ALL --name $R/before/arm_standard5_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 20 --controllers adaptive,adaptive_learned --name $R/before/arm_latching_seed2026 --workers $W --no-plots

# 2. Development, seed 2026 (failure diagnosis: experiments/trace_trial.py, experiments/c_arm_failures.py on
#    results/checkpoint2_prep/arm_prior/dev2026, which C's before-run reproduces field for field).
#    At 9818d18 (first four rules):
$PY -m experiments.robustness --backend arm --seed 2026 --trials 60 --conditions noise_1mm,noise_2mm,friction_1 --controllers adaptive --name $R/dev2026/arm_standard_60_9818d18 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 60 --conditions mf_noise_1mm --controllers adaptive --name $R/dev2026/arm_latching_60_9818d18 --workers $W --no-plots
#    Ablation at 75e1585 (latching only; the standard part was stopped and superseded by step 3):
DEFEX_CONTROLLER_VARIANTS=results/$R/dev2026/ablation_variants.json $PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 60 --conditions mf_noise_1mm \
    --controllers adaptive@all,adaptive@no_timeout,adaptive@no_impact,adaptive@no_cavity_tilt,adaptive@no_seat_walls,adaptive@no_reaim,adaptive@no_reprobe,adaptive@no_skip_noise \
    --name $R/dev2026/ablation_latching_75e1585 --workers $W --no-plots

# 3. Ablation at 110f7e1, one rule off at a time (variants in dev2026/ablation2_variants.json).
V=$(python3 -c "import json;print(','.join('adaptive@'+k for k in json.load(open('results/$R/dev2026/ablation2_variants.json'))))")
for c in noise_2mm noise_1mm friction_1; do
  DEFEX_CONTROLLER_VARIANTS=results/$R/dev2026/ablation2_variants.json $PY -m experiments.robustness --backend arm --seed 2026 --trials 60 --conditions $c \
      --controllers $V --name $R/dev2026/ablation2_${c}_110f7e1 --workers $W --no-plots
done
DEFEX_CONTROLLER_VARIANTS=results/$R/dev2026/ablation2_variants.json $PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 60 --conditions mf_noise_1mm \
    --controllers adaptive@all,adaptive@none,adaptive@no_unjam,adaptive@no_limit_wait --name $R/dev2026/ablation2_latching_110f7e1 --workers $W --no-plots

# 4. Validation on seed 4002 (rule committed first: validation4002/SELECTION_RULE.md), commit a5bd452.
VV=adaptive@base,adaptive@settle01,adaptive@limit6,adaptive@settle01_limit6
DEFEX_CONTROLLER_VARIANTS=results/$R/validation4002/variants.json $PY -m experiments.robustness --backend arm --seed 4002 --trials 30 \
    --conditions noise_1mm,noise_2mm,friction_1 --controllers $VV --name $R/validation4002/standard_a5bd452 --workers $W --no-plots
DEFEX_CONTROLLER_VARIANTS=results/$R/validation4002/variants.json $PY -m experiments.robustness --backend arm --suite latching --seed 4002 --trials 30 \
    --conditions mf_noise_1mm --controllers $VV --name $R/validation4002/latching_a5bd452 --workers $W --no-plots
#    validation4002/RESULT.md was written from those two files by the rule (base selected).

# 5. Before on seed 2027 and the arm baseline latching set (untouched 54f3097, detached worktree):
$PY -m experiments.robustness --backend arm --seed 2027 --trials 20 --conditions $S5 --controllers adaptive,adaptive_learned --name $R/before/arm_standard5_seed2027 --workers 1 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2027 --trials 20 --controllers adaptive,adaptive_learned --name $R/before/arm_latching_seed2027 --workers 1 --no-plots
$PY -m experiments.robustness --backend arm --seed 2027 --trials 5 --controllers adaptive,adaptive_learned --name $R/before/arm_standard_all_seed2027 --workers 1 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 10 --controllers fixed,correction,spiral,correction_rcc,spiral_rcc --name $R/before/arm_latching_baselines_seed2026 --workers 1 --no-plots

# 6. After, commit a5bd452 (final controller code), detached worktree:
A=$R/after_a5bd452
$PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 --controllers $ALL --name $A/gantry_rule3_standard_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers $ALL --name $A/gantry_rule3_latching_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 20 --conditions $S5 --controllers $ALL --name $A/arm_standard5_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 20 --controllers adaptive,adaptive_learned --name $A/arm_latching_seed2026 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2027 --trials 20 --conditions $S5 --controllers adaptive,adaptive_learned --name $A/arm_standard5_seed2027 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2027 --trials 20 --controllers adaptive,adaptive_learned --name $A/arm_latching_seed2027 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --seed 2027 --trials 5 --controllers adaptive,adaptive_learned --name $A/arm_standard_all_seed2027 --workers $W --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 10 --controllers fixed,correction,spiral,correction_rcc,spiral_rcc --name $A/arm_latching_baselines_seed2026 --workers $W --no-plots

# 7. Tables.
PY=$PY results/$R/make_tables.sh
