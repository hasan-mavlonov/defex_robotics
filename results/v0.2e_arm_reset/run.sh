#!/bin/sh
# results/v0.2e_arm_reset: a trial's fixture dynamics no longer depend on what the worker ran before.
# Run from the repository root on branch v0.2e/arm-reset. The "before" runs use the 966a5f5 code,
# exported with git archive into $OLD (a plain directory, not a git worktree). Seed 2027 (dev seed)
# everywhere. Single worker unless the run name ends in _w2. Writes COMPARE.txt at the end.
set -e
PY=${PY:-python}
R=results/v0.2e_arm_reset
OLD=${OLD:-/tmp/defex_966a5f5}
HERE=$(pwd)
ALL=fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
FHI=spiral_rcc,spiral_pull,spiral_rcc_pull
IHF=spiral_rcc_pull,spiral_pull,spiral_rcc
export OMP_NUM_THREADS=1

rm -rf "$OLD" && mkdir -p "$OLD"
git archive 966a5f5 defex experiments assets scripts tests pyproject.toml | tar -x -C "$OLD"
cp tests/test_backend_reset.py "$OLD/tests/"

new() { name=$1; shift; $PY -m experiments.robustness --seed 2027 --no-plots --name v0.2e_arm_reset/after/$name "$@"; }
old() {
  name=$1; shift
  (cd "$OLD" && $PY -m experiments.robustness --seed 2027 --no-plots --name before/$name "$@")
  mkdir -p $R/before && rm -rf $R/before/$name && cp -R "$OLD/results/before/$name" $R/before/$name
}

# 1. Minimal reproduction, backend level and trial level.
mkdir -p $R/repro
for B in arm gantry; do
  PYTHONPATH="$HERE" $PY $R/repro_dynamics.py $B > $R/repro/after_$B.txt
  PYTHONPATH="$OLD" $PY $R/repro_dynamics.py $B > $R/repro/before_$B.txt
done
$PY -m pytest -p no:cacheprovider -vv tests/test_backend_reset.py > $R/repro/after_test.txt 2>&1
(cd "$OLD" && $PY -m pytest -p no:cacheprovider -vv tests/test_backend_reset.py) > $R/repro/before_test.txt 2>&1 || true

# 2. Proof on the affected condition. H (spiral_pull, rigid wrist) sits between F and I as in the
#    benchmark's A-J order, so the worker switches models between F and I.
G="--backend arm --suite standard --conditions generalization_combined --trials 20"
new gen_FHI_w1 $G --workers 1 --controllers $FHI
new gen_FHI_w2 $G --workers 2 --controllers $FHI
new gen_IHF_w1 $G --workers 1 --controllers $IHF
new gen_FI_w1 $G --workers 1 --controllers spiral_rcc,spiral_rcc_pull
old gen_FHI_w1 $G --workers 1 --controllers $FHI
old gen_FHI_w2 $G --workers 2 --controllers $FHI
old gen_IHF_w1 $G --workers 1 --controllers $IHF

# 3. One more arm suite (latching connector, no grasp error), same three orders.
L="--backend arm --suite latching --trials 5"
new latching_FHI_w1 $L --workers 1 --controllers $FHI
new latching_FHI_w2 $L --workers 2 --controllers $FHI
new latching_IHF_w1 $L --workers 1 --controllers $IHF
old latching_FHI_w1 $L --workers 1 --controllers $FHI

# 4. Before/after on seed 2027, all ten controllers A-J, single worker.
for B in arm gantry; do
  new ${B}_gen_AJ --backend $B --suite standard --conditions generalization_combined --trials 20 --workers 1 --controllers $ALL
  old ${B}_gen_AJ --backend $B --suite standard --conditions generalization_combined --trials 20 --workers 1 --controllers $ALL
done
REST=nominal,lateral_1mm,lateral_3mm,lateral_5mm,yaw_2deg,yaw_5deg,yaw_10deg,tilt_2deg,tilt_5deg,tilt_10deg,noise_0mm,noise_0.5mm,noise_1mm,noise_2mm,friction_0.1,friction_0.3,friction_0.6,friction_1,generalization_tight
for B in arm gantry; do
  new ${B}_standard_rest_1 --backend $B --suite standard --conditions $REST --trials 1 --workers 1 --controllers $ALL
  old ${B}_standard_rest_1 --backend $B --suite standard --conditions $REST --trials 1 --workers 1 --controllers $ALL
done
for S in heldout latching latch_spread; do
  new arm_${S}_1 --backend arm --suite $S --trials 1 --workers 1 --controllers $ALL
  old arm_${S}_1 --backend arm --suite $S --trials 1 --workers 1 --controllers $ALL
done

sh $R/compare.sh > $R/COMPARE.txt
