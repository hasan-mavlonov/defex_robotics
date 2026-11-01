#!/usr/bin/env bash
# Every command behind results/v0.2c_learned_prior, in order, from the worktree root of
# v0.2c/learned-prior. Seeds: 2026 (dev), 3001-3030 and 3033-3040 (training), 4002 (validation).
# The scripts named here are committed next to this file; this is the order they were run in.
set -euo pipefail
R=results/v0.2c_learned_prior

# 0. Equivalence baseline on the untouched branch point 54f3097 (run in a detached temporary
#    worktree of 54f3097 with ROOT=<that worktree>; outputs copied to $R/equivalence/before_*).
ROOT=<detached worktree of 54f3097> $R/equiv_before.sh

# 1. DAgger-style re-collection: current G (v1 models) on training seeds 3033-3040, both backends.
$R/collect_dagger.sh

# 2. Train the candidates. Recipe (all models): contact features (38, translation-invariant),
#    tanh MLP 32x32, Adam lr 3e-3, L2 1e-3, batch 128, numpy seed 11, early stopping on the
#    stopping split (base seeds 3026-3030 of C's data, 3039-3040 of the DAgger data), patience
#    30, max 300 epochs; fit split 3001-3025 (C) + 3033-3038 (DAgger). Floor e fitted (init 0.1,
#    min 1e-3); tempered mode also fits tau on C's posterior (init 0.9, min 0.05).
#    gantry_residual_k2_conly (C data only, L2 grid 1e-4/1e-3) was the first run:
python -m experiments.train_contact_likelihood fit --backend gantry --mode residual --components 2 \
    --sources "results/w9_development/data:train_main,train_noise05" --name gantry_residual_k2_conly
B=gantry $R/train_models.sh          # residual K=2, K=1, posterior K=3 (+ ratio); the tempered run crashed (Adam bug, fixed in 1ede44c)
Q=1 $R/train_models_arm.sh &         # arm residual K=2 (K=3 killed, re-run below)
Q=2 $R/train_models_arm.sh; wait     # arm posterior K=3 (+ ratio) (tempered killed, re-run below)
bash $R/gantry_rest.sh               # gantry tempered K=2 (its K=3 run was killed, re-run below)
Q=gantry $R/train_rest.sh & Q=arm $R/train_rest.sh; wait

# 3. Offline evaluation (stopping split = OFFLINE_RULE score; dev 2026 reported).
M=$R/models
python -m experiments.train_contact_likelihood evaluate --backend gantry \
    --sources "results/w9_development/data:train_main,train_noise05,dev_seed2026;$R/data:dagger_g_main,dagger_g_noise05" \
    --models "g_v1=$M/v1_contact_prior_gantry.json@1,residual_k2_tempered=$M/gantry_residual_k2_tempered.json@1,residual_k2=$M/gantry_residual_k2.json@1,residual_k3=$M/gantry_residual_k3.json@1,residual_k1=$M/gantry_residual_k1.json@1,residual_k2_conly=$M/gantry_residual_k2_conly.json@1,posterior_k3=$M/gantry_posterior_k3.json@1,ratio_k3=$M/gantry_ratio_k3.json@1" \
    --splits stop,dev --out $R/offline/gantry.json
python -m experiments.train_contact_likelihood evaluate --backend arm \
    --sources "results/checkpoint2_prep/arm_prior/data:train_main,train_noise05,dev_seed2026;$R/data:dagger_g_main,dagger_g_noise05" \
    --models "g_v1=$M/v1_contact_prior_arm.json@1,residual_k2_tempered=$M/arm_residual_k2_tempered.json@1,residual_k2=$M/arm_residual_k2.json@1,residual_k3=$M/arm_residual_k3.json@1,posterior_k3=$M/arm_posterior_k3.json@1,ratio_k3=$M/arm_ratio_k3.json@1" \
    --splits stop,dev --out $R/offline/arm.json
python -m experiments.v02c_tables offline $R/offline/gantry.json $R/offline/arm.json > $R/offline/tables.md

# 4. Seed-4002 validation (SELECTION_RULE.md committed before; run in parts, pooled by the table script).
B=gantry W=2 PART=a CANDS="gantry_residual_k2_tempered gantry_residual_k2" $R/validate.sh
B=gantry W=1 PART=b REFS=0 CANDS="gantry_residual_k3" $R/validate.sh
B=arm W=3 PART=a CANDS="arm_residual_k2_tempered arm_posterior_k3" $R/validate.sh
B=arm W=3 PART=b REFS=0 CANDS="arm_residual_k3" $R/validate.sh
for b in gantry arm; do V=$R/validation/$b
  python -m experiments.v02c_tables closed-loop $V/ranking_a $V/ranking_b --refs adaptive,g_v1 --title "..." > $V/tables.md
  python -m experiments.v02c_tables closed-loop $V/safety_a $V/safety_b --refs adaptive,g_v1 --title "..." >> $V/tables.md
done

# 5. Dev-2026 check of each chosen variant.
B=gantry W=1 CHOSEN=gantry_residual_k2 $R/dev_check.sh
