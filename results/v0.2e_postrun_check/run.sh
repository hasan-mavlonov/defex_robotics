set -e
cd ~/projects/defex_robotics-d-integration
PY=../defex_robotics/.venv/bin/python
echo "start $(date '+%H:%M:%S')"
$PY -m experiments.robustness --suite heldout --backend gantry --trials 100 --seed 20261130 --workers 9 --no-plots --name v0.2e_postrun_check/gantry_heldout --controllers adaptive,adaptive_learned --conditions heldout_mischar_2mm,heldout_worst_case
$PY -m experiments.robustness --suite latching --backend arm --trials 200 --seed 20261130 --workers 9 --no-plots --name v0.2e_postrun_check/arm_latching --controllers adaptive --conditions mf_noise_1mm
echo "done $(date '+%H:%M:%S')"
