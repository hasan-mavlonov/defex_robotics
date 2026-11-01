#!/usr/bin/env bash
# The five candidates for one backend (SELECTION_RULE.md "Candidates"); recipe hyperparameters.
# B=gantry|arm  Q=1|2|3 (queues that can run side by side) or all
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
B=${B:?}; Q=${Q:-all}
export DEFEX_PRIOR_OUT=results/v0.2c_integration/prior
D=$DEFEX_PRIOR_OUT/data
SRC="$D:train_main,train_noise05,dagger_g_main,dagger_g_noise05"
T="$PY -m experiments.train_contact_likelihood fit --backend $B --weight-decay 1e-3"
if [ $Q = 1 ] || [ $Q = all ]; then
  $T --mode residual --components 2 --sources "$SRC" --name ${B}_residual_k2
  $T --mode residual --components 3 --sources "$SRC" --name ${B}_residual_k3
fi
if [ $Q = 2 ] || [ $Q = all ]; then
  $T --mode posterior --components 3 --sources "$SRC" --name ${B}_posterior_k3
  $PY -m experiments.train_contact_likelihood to-ratio --model $DEFEX_PRIOR_OUT/models/${B}_posterior_k3.json \
      --out $DEFEX_PRIOR_OUT/models/${B}_ratio_k3.json
fi
if [ $Q = 3 ] || [ $Q = all ]; then
  $T --mode residual --components 2 --temper --sources "$SRC" --name ${B}_residual_k2_tempered
fi
