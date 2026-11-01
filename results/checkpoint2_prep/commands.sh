#!/usr/bin/env bash
# Every command behind results/checkpoint2_prep, in the order it was run (development
# seeds 2026, 3001-3030 and 4001 only). Run from the repository root of v0.2/checkpoint2.
# Arm runs need the Menagerie UR5e (scripts/fetch_menagerie.py).
set -euo pipefail
PY=${PY:-python}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned

# 1. Rule-3 gantry equivalence. "before" ran in a temporary detached worktree of
#    v0.2/w3-latch-physics (fe80689) with --name cp2_equiv_before/{standard,latching};
#    its outputs were copied to equivalence/before_* and the worktree removed.
$PY -m experiments.robustness --seed 2026 --trials 20 --conditions noise_1mm,noise_2mm,friction_1 \
    --controllers adaptive,spiral_rcc --name checkpoint2_prep/equivalence/after_standard --workers 4 --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 10 --controllers adaptive,spiral_rcc \
    --name checkpoint2_prep/equivalence/after_latching --workers 4 --no-plots
E=results/checkpoint2_prep/equivalence
for s in standard latching; do
    $PY scripts/compare_trials.py $E/before_$s/trials.csv $E/after_$s/trials.csv --ignore wall_time_s
done > $E/comparison.txt

# 2. Gantry G vs C after the merge (the W9 dev-2026 runs repeated).
R=checkpoint2_prep/gantry_g_recheck
$PY -m experiments.robustness --seed 2026 --trials 60 --conditions noise_0.5mm,noise_1mm,noise_2mm \
    --controllers adaptive,adaptive_learned --name $R/standard --workers 4 --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 60 --conditions mf_noise_1mm \
    --controllers adaptive,adaptive_learned --name $R/latching --workers 4 --no-plots
for s in standard latching; do
    $PY scripts/compare_trials.py results/w9_development/dev2026/$s/trials.csv results/$R/$s/trials.csv --ignore wall_time_s
done > results/$R/comparison_vs_w9_dev2026.txt
$PY -m experiments.eval_learned_prior --analyze results/$R/standard results/$R/latching --out results/$R/pooled

# 3. Arm contact data (C on the UR5e, offline labels).
A=results/checkpoint2_prep/arm_prior
$PY -m experiments.collect_contacts --backend arm --seeds 3001 --trials 10 --name family_probe_seed3001 --root $A --workers 4
$PY -m experiments.collect_contacts --backend arm --seeds 3001-3030 --conditions noise_1mm,noise_2mm,friction_1,mf_noise_1mm \
    --trials 40 --name train_main --root $A --workers 4
$PY -m experiments.collect_contacts --backend arm --seeds 3001-3030 --conditions noise_0.5mm --trials 10 \
    --name train_noise05 --root $A --workers 4
$PY -m experiments.collect_contacts --backend arm --seeds 4001 --conditions noise_0.5mm,noise_1mm,noise_2mm,friction_1,mf_noise_1mm \
    --trials 100 --name validation --root $A --workers 4
$PY -m experiments.collect_contacts --backend arm --seeds 2026 --conditions noise_0.5mm,noise_1mm,noise_2mm,friction_1,mf_noise_1mm \
    --trials 60 --name dev_seed2026 --root $A --workers 4

# 4. Train both input sets, validation sweep, install the candidate the rule picks.
$PY -m experiments.train_contact_prior --backend arm --feature-set contact --root $A
$PY -m experiments.train_contact_prior --backend arm --feature-set all --root $A
$PY -m experiments.eval_learned_prior $A/validation/variants.json --backend arm --seed 4001 --trials 60 \
    --conditions noise_0.5mm,noise_1mm,noise_2mm,friction_1,mf_noise_1mm --name validation/weights --root $A --workers 4
$PY -m experiments.train_contact_prior --backend arm --feature-set contact --install-existing --weight 1 \
    --weight-source $A/validation/weights/paired.md --root $A

# 5. Arm G vs C with the installed model: dev seed 2026, and the validation latching suite.
$PY -m experiments.robustness --backend arm --seed 2026 --trials 60 --conditions noise_0.5mm,noise_1mm,noise_2mm,friction_1 \
    --controllers adaptive,adaptive_learned --name checkpoint2_prep/arm_prior/dev2026/standard --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 60 \
    --controllers adaptive,adaptive_learned --name checkpoint2_prep/arm_prior/dev2026/latching --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 4001 --trials 30 \
    --controllers adaptive,adaptive_learned --name checkpoint2_prep/arm_prior/validation/latching_suite --workers 4 --no-plots
$PY -m experiments.eval_learned_prior --analyze $A/dev2026/standard
$PY -m experiments.eval_learned_prior --analyze $A/dev2026/latching
$PY -m experiments.eval_learned_prior --analyze $A/dev2026/standard $A/dev2026/latching --out $A/dev2026/pooled
$PY -m experiments.eval_learned_prior --analyze $A/validation/latching_suite

# 6. Development snapshot, A-G, dev seed 2026, 20 trials per cell.
$PY -m experiments.robustness --seed 2026 --trials 20 --controllers $ALL \
    --name checkpoint2_prep/snapshot/gantry_standard --workers 4 --no-plots
$PY -m experiments.robustness --suite latching --seed 2026 --trials 20 --controllers $ALL \
    --name checkpoint2_prep/snapshot/gantry_latching --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --seed 2026 --trials 20 --conditions nominal,lateral_3mm,noise_1mm,noise_2mm,friction_1 \
    --controllers $ALL --name checkpoint2_prep/snapshot/arm_standard5 --workers 4 --no-plots
$PY -m experiments.robustness --backend arm --suite latching --seed 2026 --trials 20 --controllers $ALL \
    --name checkpoint2_prep/snapshot/arm_latching --workers 4 --no-plots

# 7. Tables.
$PY -m experiments.cp2_tables > results/checkpoint2_prep/tables.md
