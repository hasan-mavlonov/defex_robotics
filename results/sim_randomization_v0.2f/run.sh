#!/bin/zsh
# sim_randomization_v0.2f: the pre-registered commands (PREREGISTRATION.md, "Commands"), with run-log lines.
set -e
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/projects/defex_robotics/.venv/bin/python}
LOG=results/sim_randomization_v0.2f/run_log_raw.txt
{
  echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ) ($(date))"
  echo "HEAD $(git rev-parse HEAD)"
  echo "git status outside results/ (untracked included):"
  git status --porcelain --untracked-files=all -- . ':(exclude)results'
  echo "(end of git status)"
  echo "load average at start: $(sysctl -n vm.loadavg)"
  echo "python $($PY -c 'import sys; print(sys.version.split()[0])'), mujoco $($PY -c 'import mujoco; print(mujoco.__version__)'), $(uname -sm)"
} > $LOG
H=standard:noise_1mm:15,standard:noise_2mm:15,standard:generalization_combined:15,\
standard:nominal:15,standard:lateral_3mm:15,standard:friction_1:15,\
heldout:heldout_worst_case:15,heldout:heldout_handeye_bias_1.5mm:15
BAD=latching:mf_half_latched:4,latching:mf_broken_latch:4,latching:mf_stubbed_terminal:4
for B in gantry:20 arm:50; do
  echo "${B%%:*} start $(date -u +%Y-%m-%dT%H:%M:%SZ), load $(sysctl -n vm.loadavg)" >> $LOG
  $PY -m experiments.sim_randomization_v02f --backend ${B%%:*} --variants 12 --seed 20261205 --workers 4 \
    --g-model pinned --cells $H,latching:mf_noise_1mm:${B##*:},$BAD \
    --controllers adaptive,spiral_rcc,spiral_pull,spiral_rcc_pull,spiral_rcc_verify,adaptive_learned \
    --name sim_randomization_v0.2f/${B%%:*}
  echo "${B%%:*} end $(date -u +%Y-%m-%dT%H:%M:%SZ), load $(sysctl -n vm.loadavg)" >> $LOG
done
$PY -m experiments.sim_randomization_v02f_tables results/sim_randomization_v0.2f > results/sim_randomization_v0.2f/TABLES.md
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ) ($(date))" >> $LOG
