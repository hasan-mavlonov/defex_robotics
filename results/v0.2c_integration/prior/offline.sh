#!/usr/bin/env bash
# OFFLINE_RULE score (stopping split) and dev 2026, every candidate plus v1 and the merge-time models.
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
R=results/v0.2c_integration/prior
M=$R/models
V1=results/v0.2c_learned_prior/models
for B in ${BACKENDS:-gantry arm}; do
  $PY -m experiments.train_contact_likelihood evaluate --backend $B \
    --sources "$R/data:train_main,train_noise05,dev_seed2026,dagger_g_main,dagger_g_noise05" \
    --models "g_v1=$V1/v1_contact_prior_$B.json@1,g_lp=$M/lp_contact_prior_$B.json@1,residual_k2=$M/${B}_residual_k2.json@1,residual_k3=$M/${B}_residual_k3.json@1,residual_k2_tempered=$M/${B}_residual_k2_tempered.json@1,posterior_k3=$M/${B}_posterior_k3.json@1,ratio_k3=$M/${B}_ratio_k3.json@1" \
    --splits stop,dev --out $R/offline/$B.json
done
$PY -m experiments.v02c_prior_tables offline $R/offline/gantry.json $R/offline/arm.json > $R/offline/tables.md
