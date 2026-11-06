#!/usr/bin/env bash
# v0.2c candidate models for one backend (B=gantry|arm). Hyperparameters fixed: tanh 32x32, Adam lr 3e-3,
# L2 1e-3, batch 128, early stopping on the stopping split (patience 30, max 300 epochs), numpy seed 11.
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
B=${B:?set B=gantry or B=arm}
if [ "$B" = gantry ]; then CDATA="results/w9_development/data:train_main,train_noise05"
else CDATA="results/checkpoint2_prep/arm_prior/data:train_main,train_noise05"; fi
DAG="results/v0.2c_learned_prior/data:dagger_g_main,dagger_g_noise05"
T="$PY -m experiments.train_contact_likelihood fit --backend $B --weight-decay 1e-3"
$T --mode residual --components 2 --sources "$CDATA;$DAG" --name ${B}_residual_k2
$T --mode residual --components 1 --sources "$CDATA;$DAG" --name ${B}_residual_k1
$T --mode posterior --components 3 --sources "$CDATA;$DAG" --name ${B}_posterior_k3
$PY -m experiments.train_contact_likelihood to-ratio --model results/v0.2c_learned_prior/models/${B}_posterior_k3.json \
    --out results/v0.2c_learned_prior/models/${B}_ratio_k3.json
# Added after the first gantry results: residual K=2 with a fitted temperature on C's posterior.
if [ "${TEMPER:-1}" = 1 ]; then
  $T --mode residual --components 2 --temper --sources "$CDATA;$DAG" --name ${B}_residual_k2_tempered
fi
# Added after K=1 scored well below K=2 on the gantry stopping split: K=3.
$T --mode residual --components 3 --sources "$CDATA;$DAG" --name ${B}_residual_k3
