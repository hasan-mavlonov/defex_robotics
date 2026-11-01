#!/usr/bin/env bash
# Arm candidates, the same recipe as train_models.sh, split into two queues run side by side
# (Q=1 or Q=2). Residual K=1 is not trained on the arm: on the gantry stopping split it scored
# 2.865 nats against 2.547 for K=2 (results/v0.2c_learned_prior/models/gantry_residual_k*_search.json).
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
B=arm
CDATA="results/checkpoint2_prep/arm_prior/data:train_main,train_noise05"
DAG="results/v0.2c_learned_prior/data:dagger_g_main,dagger_g_noise05"
T="$PY -m experiments.train_contact_likelihood fit --backend $B --weight-decay 1e-3"
if [ "${Q:?}" = 1 ]; then
  $T --mode residual --components 2 --sources "$CDATA;$DAG" --name ${B}_residual_k2
  $T --mode residual --components 3 --sources "$CDATA;$DAG" --name ${B}_residual_k3
else
  $T --mode posterior --components 3 --sources "$CDATA;$DAG" --name ${B}_posterior_k3
  $PY -m experiments.train_contact_likelihood to-ratio --model results/v0.2c_learned_prior/models/${B}_posterior_k3.json \
      --out results/v0.2c_learned_prior/models/${B}_ratio_k3.json
  $T --mode residual --components 2 --temper --sources "$CDATA;$DAG" --name ${B}_residual_k2_tempered
fi
