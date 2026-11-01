#!/usr/bin/env bash
# Rule-5 equivalence set on this branch (same set as equiv_before.sh). TAG names the state:
#   code    after the v2 code changes, v1 models still installed: all seven controllers must match
#   install after installing the chosen models: A-F must match, G changes where a new model is installed
set -euo pipefail
cd ~/projects/defex_robotics-c-learned-prior
PY=~/projects/defex_robotics/.venv/bin/python
W=${W:-2}
TAG=${TAG:?set TAG=code or TAG=install}
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned
R=v0.2c_learned_prior/equivalence
for b in gantry arm; do
  $PY -m experiments.robustness --backend $b --seed 2026 --trials 10 --conditions noise_1mm,noise_2mm,friction_1 \
      --controllers $ALL --name $R/after_${TAG}_${b}_standard --workers $W --no-plots
  $PY -m experiments.robustness --backend $b --suite latching --seed 2026 --trials 5 --controllers $ALL \
      --name $R/after_${TAG}_${b}_latching --workers $W --no-plots
done
E=results/$R
for b in gantry arm; do for s in standard latching; do
  $PY scripts/compare_trials.py $E/before_${b}_$s/trials.csv $E/after_${TAG}_${b}_$s/trials.csv --ignore wall_time_s || true
  for c in fixed correction adaptive spiral correction_rcc spiral_rcc adaptive_learned; do
    python3 - "$E/before_${b}_$s/trials.csv" "$E/after_${TAG}_${b}_$s/trials.csv" "$c" <<'PYEOF'
import csv, sys
a, b, c = sys.argv[1:]
def load(p):
    return {(r["condition"], r["trial_index"], r["seed"]): r for r in csv.DictReader(open(p)) if r["controller"] == c}
A, B = load(a), load(b)
diff = sum(any(A[k][f] != B[k][f] for f in A[k] if f != "wall_time_s") for k in A)
fields = sum(len(A[k]) - 1 for k in A)
print(f"  {c}: {len(A)} trials, {fields} fields, {diff} trials differ")
PYEOF
  done
done; done > $E/comparison_${TAG}.txt
cat $E/comparison_${TAG}.txt
