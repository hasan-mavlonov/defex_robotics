#!/usr/bin/env bash
# Dev seed 2026 check of the chosen variant (SELECTION_RULE.md, "After selection"). B, CHOSEN (model name), W.
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
B=${B:?}; W=${W:-3}; CHOSEN=${CHOSEN:?}
R=results/v0.2c_learned_prior
M=$R/models
mkdir -p $R/dev2026/$B
cat > $R/dev2026/$B/variants.json <<JSON
{"adaptive": {"controller": "adaptive"},
 "g_v1": {"controller": "adaptive_learned", "model_path": "$M/v1_contact_prior_$B.json", "weight": 1.0},
 "g_${CHOSEN#${B}_}": {"controller": "adaptive_learned", "model_path": "$M/$CHOSEN.json", "weight": 1.0}}
JSON
FAM=noise_0.5mm,noise_1mm,noise_2mm
[ "$B" = arm ] && FAM=noise_0.5mm,noise_1mm,noise_2mm,friction_1
LATCH=mf_nominal,mf_moderate,mf_noise_1mm,mf_half_latched,mf_broken_latch,mf_stubbed_terminal,mf_wrong_polarization
$PY -m experiments.eval_learned_prior $R/dev2026/$B/variants.json --backend $B --seed 2026 --trials 60 \
    --conditions $FAM,$LATCH --name dev2026/$B --root $R --workers $W
$PY -m experiments.v02c_tables closed-loop $R/dev2026/$B --refs adaptive,g_v1 \
    --title "$B, dev seed 2026, 60 trials per condition" > $R/dev2026/$B/tables.md
