#!/usr/bin/env bash
# Every command behind results/v0.2c_integration, in the order it was run, from the root of the worktree
# of branch v0.2c/integration. Seeds: 2026, 2027 (dev), 3001-3030 and 3033-3040 (training), 4002 (validation),
# 3032 (one out-of-sample snapshot). Workers: 3 throughout (the Checkpoint 2 benchmark had finished).
set -euo pipefail
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
T="$PY -m pytest -p no:cacheprovider -o addopts= -q ."

# 0. Branch and merges (full test suite after each merge: 110, 122, 130, 140 passed).
git worktree add ~/projects/defex_robotics-c-integration -b v0.2c/integration v0.2/checkpoint2   # tip 883db25
git merge --no-ff v0.2c/arm-baselines;   $T
git merge --no-ff v0.2c/defect-verdict;  $T
git merge --no-ff v0.2c/arm-robustness   # conflict in experiments/v02c_tables.py -> v02c_robustness_tables.py
$T
git merge --no-ff v0.2c/learned-prior    # conflict in experiments/v02c_tables.py -> v02c_prior_tables.py
$T

# 1. Each workstream's after-runs on the merged code (commit 8d343f8), and the comparison.
results/v0.2c_integration/claims.sh claims_merged 3 ab dv
results/v0.2c_integration/claims_tables.sh            # -> claims_merged/comparison.md

# 2. G retrained on the integrated C (prior/SELECTION_RULE.md committed first, at 0ace479).
B=gantry W=3 results/v0.2c_integration/prior/collect.sh   # at 0ace479
B=arm W=3 results/v0.2c_integration/prior/collect.sh
cp assets/models/contact_prior_gantry.json results/v0.2c_integration/prior/models/lp_contact_prior_gantry.json
cp assets/models/contact_prior_arm.json results/v0.2c_integration/prior/models/lp_contact_prior_arm.json
printf "%s\n" "gantry k2" "gantry temper" "gantry post" "gantry k3" "arm k2" "arm temper" "arm post" "arm k3" |
  xargs -P 3 -L 1 bash -c 'B=$0 Q=$1 results/v0.2c_integration/prior/train.sh'   # at 0692c04
results/v0.2c_integration/prior/offline.sh               # -> prior/offline/*.json, OFFLINE_RESULT.md
B=gantry W=3 CANDS="gantry_residual_k2_tempered gantry_residual_k2 gantry_posterior_k3" results/v0.2c_integration/prior/validate.sh  # at dfbbdb9
B=arm W=3 CANDS="arm_residual_k2_tempered arm_residual_k3 arm_posterior_k3" results/v0.2c_integration/prior/validate.sh
for b in gantry arm; do
  $PY -m experiments.v02c_integration_select results/v0.2c_integration/prior/validation/$b > results/v0.2c_integration/prior/validation/$b/selection.md
done
$PY -m experiments.train_contact_likelihood install --model results/v0.2c_integration/prior/models/gantry_posterior_k3.json \
    --rule results/v0.2c_integration/prior/SELECTION_RULE.md --result results/v0.2c_integration/prior/validation/gantry/selection.md
cp results/v0.2c_learned_prior/models/v1_contact_prior_arm.json assets/models/contact_prior_arm.json   # the rule kept v1 on the arm
$T                                                       # 147 passed
B=gantry W=3 CHOSEN=results/v0.2c_integration/prior/models/gantry_posterior_k3.json results/v0.2c_integration/prior/dev_check.sh  # at 96a4be3

# 3. Snapshots A-G, 20 trials per cell, standard / latching / heldout, both backends.
results/v0.2c_integration/snapshot.sh 2026 3             # at 96a4be3
results/v0.2c_integration/snapshot_vs_cp2.sh             # -> snapshot_seed2026/vs_checkpoint2_prep.md
results/v0.2c_integration/snapshot.sh 3032 3             # at 586caed (results-only commit after 96a4be3); run once
