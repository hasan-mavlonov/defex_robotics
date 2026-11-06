#!/usr/bin/env bash
# Seed-4002 validation (SELECTION_RULE.md committed first, at f1ad138). Code at afa08a4.
set -euo pipefail
PY=${PY:-python}
V=results/v0.2c_defect_verdict/validation
$PY -m experiments.v02c_variants $V/variants.json --suite latching --seed 4002 --trials 20 --backend gantry --name v0.2c_defect_verdict/validation/gantry --workers 1
$PY -m experiments.v02c_variants $V/variants.json --suite latching --seed 4002 --trials 20 --backend arm --name v0.2c_defect_verdict/validation/arm --workers 3
$PY -m experiments.v02c_selection $V/gantry $V/arm > $V/selection.md
