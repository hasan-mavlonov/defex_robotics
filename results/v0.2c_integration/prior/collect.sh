#!/usr/bin/env bash
# Contact data with the integrated C (and DAgger data with G, installed models), SELECTION_RULE.md "Data".
# B=gantry|arm  W=workers  PARTS="c dagger dev"
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
B=${B:?}; W=${W:-3}; PARTS=${PARTS:-c dagger dev}
R=results/v0.2c_integration/prior
FAM=noise_1mm,noise_2mm,mf_noise_1mm
[ "$B" = arm ] && FAM=noise_1mm,noise_2mm,friction_1,mf_noise_1mm
for P in $PARTS; do
  case $P in
    c)
      $PY -m experiments.collect_contacts --backend $B --seeds 3001-3030 --conditions $FAM --trials 40 --name train_main --root $R --workers $W
      $PY -m experiments.collect_contacts --backend $B --seeds 3001-3030 --conditions noise_0.5mm --trials 10 --name train_noise05 --root $R --workers $W ;;
    dagger)
      $PY -m experiments.collect_contacts --backend $B --controller adaptive_learned --seeds 3033-3040 --conditions $FAM --trials 40 --name dagger_g_main --root $R --workers $W
      $PY -m experiments.collect_contacts --backend $B --controller adaptive_learned --seeds 3033-3040 --conditions noise_0.5mm --trials 10 --name dagger_g_noise05 --root $R --workers $W ;;
    dev)
      $PY -m experiments.collect_contacts --backend $B --seeds 2026 --conditions noise_0.5mm,$FAM --trials 60 --name dev_seed2026 --root $R --workers $W ;;
  esac
done
