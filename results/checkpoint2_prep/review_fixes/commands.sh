#!/usr/bin/env bash
# Every command behind results/checkpoint2_prep/review_fixes, in the order it was run
# (development seed 2026, unused training seed 3031; offline scripts read the committed data).
# Run from the repository root of v0.2/checkpoint2. Arm runs need the Menagerie UR5e.
set -euo pipefail
PY=${PY:-python}
R=checkpoint2_prep/review_fixes
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
S5=nominal,lateral_3mm,noise_1mm,noise_2mm,friction_1

# 1. Before the fixes, on detached worktrees: TREE = fe80689 (v0.2/w3-latch-physics, name w3)
#    and 0251a75 (this branch before the review fixes, name cp2_before). From each tree's root,
#    with PYTHONPATH=<tree> and a copy of experiments/rand_equivalence.py (commit 34fbd8e):
#      $PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 \
#          --controllers adaptive,spiral_rcc --name rf_eq_standard --workers 4 --no-plots
#      $PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers adaptive,spiral_rcc \
#          --name rf_eq_latching --workers 4 --no-plots
#      $PY rand_equivalence.py --seed 2026 --variants 2,4,6,11,12 --controllers adaptive,spiral_rcc --trials 10 \
#          --out <scratch>/<name>_rand --workers 4
#    Outputs copied to equivalence/<name>_{standard,latching} and rand_slice/<name>; worktrees removed.

# 2. Installed models: complete their fixture dynamics from the backend (weights unchanged).
$PY -m experiments.train_contact_prior --backend gantry --feature-set all --install-existing --weight 1 \
    --weight-source "results/w9_development/validation/weights (SELECTION_RULE.md: G_all_w1, 235/240 vs C 218/240)" \
    --complete-fixture-dynamics
$PY -m experiments.train_contact_prior --backend arm --feature-set contact --install-existing --weight 1 \
    --weight-source results/checkpoint2_prep/arm_prior/validation/weights/paired.md \
    --root results/checkpoint2_prep/arm_prior --complete-fixture-dynamics

# 3. After the fixes (commit acaa858): rule-3 set and the randomized slice.
$PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 \
    --controllers adaptive,spiral_rcc --name $R/equivalence/cp2_after_standard --workers 4 --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers adaptive,spiral_rcc \
    --name $R/equivalence/cp2_after_latching --workers 4 --no-plots
$PY -m experiments.rand_equivalence --seed 2026 --variants 2,4,6,11,12 --controllers adaptive,spiral_rcc --trials 10 \
    --out results/$R/rand_slice/cp2_after --workers 4

# 4. G with the completed models, and C / F on the arm: the same trials as the snapshot.
$PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm \
    --controllers adaptive_learned --name $R/model_check/gantry_standard --workers 4 --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 20 --conditions mf_noise_1mm,mf_wrong_polarization \
    --controllers adaptive_learned --name $R/model_check/gantry_latching --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 \
    --controllers adaptive,adaptive_learned,spiral_rcc --name $R/model_check/arm_standard --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 20 --conditions mf_noise_1mm,mf_wrong_polarization \
    --controllers adaptive,adaptive_learned,spiral_rcc --name $R/model_check/arm_latching --workers 4 --no-plots

# 5. Offline: calibration of the posterior G acts on (no simulation).
$PY -m experiments.cp2_posterior_calibration --out results/$R/posterior_calibration.json

# 6. All controllers on seed 3031 (unused by any development, training or selection step).
$PY -m experiments.robustness --backend arm --seed 3031 --trials 20 --conditions $S5 --controllers $ALL \
    --name $R/seed3031/arm_standard5 --workers 4 --no-plots
$PY -m experiments.robustness --seed 3031 --trials 20 --conditions $S5 --controllers $ALL \
    --name $R/seed3031/gantry_standard5 --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 3031 --trials 20 --controllers $ALL \
    --name $R/seed3031/arm_latching --workers 4 --no-plots
$PY -m experiments.robustness --suite latching --seed 3031 --trials 20 --controllers $ALL \
    --name $R/seed3031/gantry_latching --workers 4 --no-plots

# 7. Comparisons and tables.
E=results/$R
{
for s in standard latching; do
    $PY scripts/compare_trials.py $E/equivalence/w3_$s/trials.csv results/checkpoint2_prep/equivalence/before_$s/trials.csv --ignore wall_time_s
    $PY scripts/compare_trials.py $E/equivalence/w3_$s/trials.csv $E/equivalence/cp2_before_$s/trials.csv --ignore wall_time_s
    $PY scripts/compare_trials.py $E/equivalence/w3_$s/trials.csv $E/equivalence/cp2_after_$s/trials.csv --ignore wall_time_s
done
for k in 2 4 6 11 12; do
    $PY scripts/compare_trials.py $E/rand_slice/w3/variant_$k/trials.csv $E/rand_slice/cp2_before/variant_$k/trials.csv --ignore wall_time_s | head -1 || true
    $PY scripts/compare_trials.py $E/rand_slice/w3/variant_$k/trials.csv $E/rand_slice/cp2_after/variant_$k/trials.csv --ignore wall_time_s | head -1
done
} > $E/comparison.txt
$PY -m experiments.cp2_review_tables > $E/tables.md
$PY -m experiments.cp2_tables > results/checkpoint2_prep/tables.md
