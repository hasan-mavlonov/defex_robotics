# W2 pre-registration: held-out vision families and simulator randomization

Committed before either run. Nothing below changes after the first trial of
either seed has run.

## Frozen code

Commit **fe48eca** (branch `v0.2/w2-robustness`); a run may start from a later
commit that changes only `results/`. Controllers are unchanged from
benchmark_v0.2a: C was refactored in W2 (constants moved into AdaptiveConfig)
and is identical to the reported run trial for trial; D, E and F keep their W1
settings. No controller has been run on the families or seeds below.

## Run 1: held-out vision families

- Command: `python -m experiments.robustness --suite heldout --trials 100 --seed 20261109 --name heldout_v0.2`
- Conditions (`heldout_conditions()` in `defex/tasks/conditions.py`), all on the
  moderate disturbance of the noise sweep (up to 3 mm, 5 deg yaw, 3 deg tilt):
  1. `heldout_mischar_1mm`: controllers told vision sigma 0.5 mm, true 1.0 mm.
  2. `heldout_mischar_2mm`: told 0.5 mm, true 2.0 mm.
  3. `heldout_handeye_bias_1.5mm`: unknown 1.5 mm bias, controllers told none.
  4. `heldout_vision_outliers`: 5% of shots off by 3-6 mm, controllers told the nominal accuracy.
  5. `heldout_worst_case`: friction 0.8, 0.2 mm clearance, told 0.5 mm, true 1.0 mm.
- Controllers A-F, 100 paired trials each: 3,000 trials.
- Metrics: as benchmark_v0.2a (success with Wilson intervals, paired McNemar
  against C, bad units passed, stops, cycle percentiles, throughput, force).

## Run 2: simulator randomization

- Command: `python -m experiments.sim_randomization --variants 12 --trials 20 --seed 20261108 --name sim_randomization_v0.2`
- 12 randomized simulators plus the nominal one. Bands in
  `experiments/sim_randomization.py`: normal-contact time constant 1.5-4 ms,
  damping ratio 0.7-1.3, friction time constant 10-40 ms, solimp dmin
  0.90-0.97, dmax 0.98-0.995, width 0.1-0.5 mm, impratio 3-20, elliptic or
  pyramidal cone, linear servo stiffness 5-20 N/mm, wrist servo stiffness
  10-25 N m/rad.
- Conditions: nominal, lateral_3mm, noise_1mm, noise_2mm, friction_1,
  generalization_tight; controllers A-F; 20 paired trials: 9,360 trials.
- Primary metric: C's success minus the best of D, E, F, per variant.

## What gets reported, decided in advance

- Every number from both runs, including any where C does worse.
- Run 1: C's success on each family and its change from the matching
  correctly-characterized condition of benchmark_v0.2a (`noise_1mm`,
  `noise_2mm`); whether C's lead over the best of D, E, F holds per family
  (McNemar p < 0.05) or reverses.
- Run 2: the range of C's lead across variants, and the number of variants in
  which a conventional controller beats C.
- If C's lead over the best fair baseline reverses in any held-out family or in
  more than 2 of 12 simulator variants, that is stated in the README headline.
