set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
CDATA="results/w9_development/data:train_main,train_noise05"
DAG="results/v0.2c_learned_prior/data:dagger_g_main,dagger_g_noise05"
T="$PY -m experiments.train_contact_likelihood fit --backend gantry --weight-decay 1e-3"
$T --mode residual --components 2 --temper --sources "$CDATA;$DAG" --name gantry_residual_k2_tempered
$T --mode residual --components 3 --sources "$CDATA;$DAG" --name gantry_residual_k3
