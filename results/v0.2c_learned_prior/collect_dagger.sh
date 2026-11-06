#!/usr/bin/env bash
# DAgger-style re-collection: the CURRENT G (installed v1 models, commit a23862e+) probing on
# training seeds 3033-3040, records labelled offline as in W9. Same families and trial counts per
# seed as the W9 / Checkpoint 2 C data.
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
W=${W:-2}
R=results/v0.2c_learned_prior
$PY -m experiments.collect_contacts --backend gantry --controller adaptive_learned --seeds 3033-3040 \
    --conditions noise_1mm,noise_2mm,mf_noise_1mm --trials 40 --name dagger_g_main --root $R --workers $W
$PY -m experiments.collect_contacts --backend gantry --controller adaptive_learned --seeds 3033-3040 \
    --conditions noise_0.5mm --trials 10 --name dagger_g_noise05 --root $R --workers $W
$PY -m experiments.collect_contacts --backend arm --controller adaptive_learned --seeds 3033-3040 \
    --conditions noise_1mm,noise_2mm,friction_1,mf_noise_1mm --trials 40 --name dagger_g_main --root $R --workers $W
$PY -m experiments.collect_contacts --backend arm --controller adaptive_learned --seeds 3033-3040 \
    --conditions noise_0.5mm --trials 10 --name dagger_g_noise05 --root $R --workers $W
