# v0.2g drift-stream fix: correction rerun plan

Written and committed before the rerun. This is a correction check of a code defect found in
review, not a pre-registered test, and it selects nothing.

## The defect
In `heldout2_v0.2f` (seed 20261207, commit 6ea164e), `SensorSuite` drew each F/T-drift trial's
drift direction from `SeedSequence(trial_seed).spawn(4)` followed by `spawn(1)`, which is child
spawn_key (4,). `sample_scenario` draws the socket disturbance (phi, r, yaw, tilt) from
`SeedSequence(trial_seed).spawn(5)[4]`, the same child. So the drift direction was a fixed
function of the disturbance draws, not an independent random direction as the
pre-registration said. Each direction is still uniform on the sphere, and pairing across
controllers is unaffected.

## The fix
`defex/perception/sensors.py`: the drift stream is now
`SeedSequence(trial_seed, spawn_key=(16,))`, apart from the sensor children (0-3) and the
disturbance stream (4). New test:
`tests/test_heldout2_conditions.py::test_ft_drift_direction_is_independent_of_the_scenario_disturbance_stream`.
Only trials with drift on change. `experiments/v02f_h2_drift_axes.drift_rates` keeps the
v0.2f stream by default, so the v0.2f diagnosis still reproduces.

## The rerun
Same pre-registered command as heldout2_v0.2f, restricted to the two drift conditions:
`--suite heldout2 --backend {gantry,arm} --trials 40 --seed 20261207 --conditions
h2_ft_drift_0.1,h2_ft_drift_0.3`, all ten controllers, `--workers 2`. 1,600 trials.

## What will be reported
For each machine and drift condition, and for the drift family as a whole, side by side with
the heldout2_v0.2f rows: seated good parts and bad units for every controller, and the
pre-registered heldout2 comparisons for the drift family (C against the best fair
baseline, and J against C), computed exactly as in `HELDOUT2_TABLES.md`. Whether any
heldout2 verdict for the drift family changes. Both runs are reported whatever they show;
neither replaces the pre-registered result, which stays as it is in `results/heldout2_v0.2f/`.
