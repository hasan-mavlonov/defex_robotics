#!/bin/sh
# Every comparison REPORT.md quotes. Run from the repository root: sh results/v0.2e_arm_reset/compare.sh
PY=${PY:-python}
R=results/v0.2e_arm_reset
C="$PY $R/compare.py"
DEV=results/v0.2d_dev_check
FI="spiral_rcc spiral_rcc_pull"

echo "== 2. arm generalization_combined, F/H/I, 20 trials"
for side in after before; do
  for run in gen_FHI_w1 gen_FHI_w2 gen_IHF_w1 gen_FI_w1; do
    f=$R/$side/$run/trials.csv
    [ -f $f ] || continue
    echo "$side/$run  F vs I: $($C pair $f $FI)"
  done
  echo "$side  FHI_w1 vs FHI_w2: $($C runs $R/$side/gen_FHI_w1/trials.csv $R/$side/gen_FHI_w2/trials.csv)"
  echo "$side  FHI_w1 vs IHF_w1: $($C runs $R/$side/gen_FHI_w1/trials.csv $R/$side/gen_IHF_w1/trials.csv)"
done
echo "after/gen_FHI_w1 vs before/gen_FHI_w1: $($C runs $R/after/gen_FHI_w1/trials.csv $R/before/gen_FHI_w1/trials.csv)"

echo
echo "== 3. arm latching suite, F/H/I, 5 trials"
echo "after  FHI_w1 vs FHI_w2: $($C runs $R/after/latching_FHI_w1/trials.csv $R/after/latching_FHI_w2/trials.csv)"
echo "after  FHI_w1 vs IHF_w1: $($C runs $R/after/latching_FHI_w1/trials.csv $R/after/latching_IHF_w1/trials.csv)"
echo "after vs before FHI_w1:  $($C runs $R/after/latching_FHI_w1/trials.csv $R/before/latching_FHI_w1/trials.csv)"

echo
echo "== 4. before (966a5f5) vs after, A-J, seed 2027, 1 worker"
for run in arm_gen_AJ gantry_gen_AJ arm_standard_rest_1 gantry_standard_rest_1 arm_heldout_1 arm_latching_1 arm_latch_spread_1; do
  echo "$run: $($C runs $R/after/$run/trials.csv $R/before/$run/trials.csv)"
done
echo "arm_gen_AJ after vs before, per controller:"
$C by-controller $R/after/arm_gen_AJ/trials.csv $R/before/arm_gen_AJ/trials.csv
for side in after before; do
  echo "$side/arm_gen_AJ  F vs I: $($C pair $R/$side/arm_gen_AJ/trials.csv $FI)"
  echo "$side/gantry_gen_AJ  F vs I: $($C pair $R/$side/gantry_gen_AJ/trials.csv $FI)"
done

echo
echo "== against results/v0.2d_dev_check (966a5f5-era code, 9 workers, seed 2027, 20 trials)"
$PY - "$DEV" "$R" <<'EOF'
import csv, sys
dev, r = sys.argv[1], sys.argv[2]
for backend in ("arm", "gantry"):
    rows = [x for x in csv.DictReader(open(f"{dev}/{backend}_standard/trials.csv")) if x["condition"] == "generalization_combined"]
    with open(f"{r}/dev_{backend}_gen.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
EOF
for B in arm gantry; do
  echo "dev_check ${B} gen_combined (9 workers) vs before/${B}_gen_AJ (1 worker): $($C runs $R/dev_${B}_gen.csv $R/before/${B}_gen_AJ/trials.csv)"
  echo "dev_check ${B} gen_combined (9 workers) vs after/${B}_gen_AJ:            $($C runs $R/dev_${B}_gen.csv $R/after/${B}_gen_AJ/trials.csv)"
  echo "dev_check ${B} gen_combined  F vs I: $($C pair $R/dev_${B}_gen.csv $FI)"
done
echo "dev_check arm gen_combined vs after/arm_gen_AJ, per controller:"
$C by-controller $R/dev_arm_gen.csv $R/after/arm_gen_AJ/trials.csv
rm -f $R/dev_arm_gen.csv $R/dev_gantry_gen.csv
