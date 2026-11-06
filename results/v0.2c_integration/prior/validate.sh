#!/usr/bin/env bash
# Seed-4002 closed-loop validation (SELECTION_RULE.md). B=gantry|arm, CANDS="model names" (in prior/models),
# W=workers. Runs adaptive, g_v1, g_lp and the candidates in one paired run per suite.
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
B=${B:?}; W=${W:-3}
R=results/v0.2c_integration/prior
M=$R/models
mkdir -p $R/validation/$B
python3 - "$B" "$M" "$R/validation/$B/variants.json" ${CANDS:?} <<'PYEOF'
import json, sys
b, m, out, *cands = sys.argv[1:]
v = {"adaptive": {"controller": "adaptive"},
     "g_v1": {"controller": "adaptive_learned", "model_path": f"results/v0.2c_learned_prior/models/v1_contact_prior_{b}.json", "weight": 1.0},
     "g_lp": {"controller": "adaptive_learned", "model_path": f"{m}/lp_contact_prior_{b}.json", "weight": 1.0}}
for c in cands:
    v["g_" + c.removeprefix(b + "_")] = {"controller": "adaptive_learned", "model_path": f"{m}/{c}.json", "weight": 1.0}
json.dump(v, open(out, "w"), indent=2)
PYEOF
FAM=noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm
[ "$B" = arm ] && FAM=noise_0.5mm,noise_1mm,noise_2mm,friction_1,mf_noise_1mm
$PY -m experiments.eval_learned_prior $R/validation/$B/variants.json --backend $B --seed 4002 --trials 100 \
    --conditions $FAM --name validation/$B/ranking --root $R --workers $W
$PY -m experiments.eval_learned_prior $R/validation/$B/variants.json --backend $B --seed 4002 --trials 30 \
    --conditions mf_nominal,mf_moderate,mf_half_latched,mf_broken_latch,mf_stubbed_terminal,mf_wrong_polarization \
    --name validation/$B/safety --root $R --workers $W
$PY -m experiments.v02c_prior_tables closed-loop $R/validation/$B/ranking --refs adaptive,g_v1 \
    --title "$B, seed 4002, ranking families, 100 trials per condition" > $R/validation/$B/tables.md
$PY -m experiments.v02c_prior_tables closed-loop $R/validation/$B/safety --refs adaptive,g_v1 \
    --title "$B, seed 4002, safety suite, 30 trials per condition" >> $R/validation/$B/tables.md
