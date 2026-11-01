#!/usr/bin/env bash
# Re-run of the trainings whose processes were killed at 01:17 (no traceback; the machine was
# short of memory with three trainings, the benchmark and other jobs). Same commands as
# train_models.sh / train_models_arm.sh; one queue per backend (Q=gantry|arm).
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
DAG="results/v0.2c_learned_prior/data:dagger_g_main,dagger_g_noise05"
if [ "${Q:?}" = gantry ]; then
  T="$PY -m experiments.train_contact_likelihood fit --backend gantry --weight-decay 1e-3"
  $T --mode residual --components 3 --sources "results/w9_development/data:train_main,train_noise05;$DAG" --name gantry_residual_k3
else
  T="$PY -m experiments.train_contact_likelihood fit --backend arm --weight-decay 1e-3"
  C="results/checkpoint2_prep/arm_prior/data:train_main,train_noise05"
  $T --mode residual --components 2 --temper --sources "$C;$DAG" --name arm_residual_k2_tempered
  $T --mode residual --components 3 --sources "$C;$DAG" --name arm_residual_k3
fi
