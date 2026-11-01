#!/usr/bin/env bash
# Seed-4002 closed-loop validation (SELECTION_RULE.md). B=gantry|arm, CANDS="model names", PART=run label.
# REFS=1 also runs C and g_v1. Trials are fixed by (seed, condition, index, variant), so parts pool exactly.
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
B=${B:?}; W=${W:-3}; PART=${PART:?}; REFS=${REFS:-1}
R=results/v0.2c_learned_prior
M=$R/models
mkdir -p $R/validation/$B
python3 - "$B" "$M" "$R/validation/$B/variants_$PART.json" "$REFS" ${CANDS:?} <<'PYEOF'
import json, sys
b, m, out, refs, *cands = sys.argv[1:]
v = {"adaptive": {"controller": "adaptive"}}
if refs == "1":
    v["g_v1"] = {"controller": "adaptive_learned", "model_path": f"{m}/v1_contact_prior_{b}.json", "weight": 1.0}
for c in cands:
    v["g_" + c.removeprefix(b + "_")] = {"controller": "adaptive_learned", "model_path": f"{m}/{c}.json", "weight": 1.0}
json.dump(v, open(out, "w"), indent=2)
PYEOF
FAM=noise_0.5mm,noise_1mm,noise_2mm,mf_noise_1mm
[ "$B" = arm ] && FAM=noise_0.5mm,noise_1mm,noise_2mm,friction_1,mf_noise_1mm
$PY -m experiments.eval_learned_prior $R/validation/$B/variants_$PART.json --backend $B --seed 4002 --trials 100 \
    --conditions $FAM --name validation/$B/ranking_$PART --root $R --workers $W
$PY -m experiments.eval_learned_prior $R/validation/$B/variants_$PART.json --backend $B --seed 4002 --trials 30 \
    --conditions mf_nominal,mf_moderate,mf_half_latched,mf_broken_latch,mf_stubbed_terminal,mf_wrong_polarization \
    --name validation/$B/safety_$PART --root $R --workers $W
# Pooled tables (with REFS=0 the part's own C rows duplicate part a's: the table script keys on variant name)
