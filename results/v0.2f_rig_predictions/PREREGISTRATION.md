# v0.2f rig predictions: pre-registration

Written and committed before the run. Nothing below changes after the first trial of
seed 20261201 has run. No rig exists yet. These are the simulation's predictions for
the conditions in `hardware/TEST_PROTOCOL.md`, frozen so that a later rig result can
be compared with them. Simulation only.

## Frozen code

- The simulation code is benchmark_v0.2e's frozen code, ddd0d34. The run starts from
  this commit, which adds only files under `results/v0.2f_rig_predictions/` to
  4df8cae (branch `v0.2f/hw`).
- Check made before writing this file, at 4df8cae:
  `git diff --stat ddd0d34 HEAD -- . ':(exclude)results' ':(exclude)README.md' ':(exclude)docs'`
  printed nothing. `RUN_LOG.md` repeats the check at the start of the run.
- Every `config.json` must show `git_dirty: false`. No tracked file outside `results/`
  is edited while the run is going.
- The model files used by G are not used (G is not run).

## Seed

- Base seed **20261201**. No `config.json` under `results/` uses it, and it is not in
  the spent list.
- It is also the rig's seed: trial i of condition c on the rig uses the socket pose,
  grasp and injected vision error of `sample_scenario(c, i, 20261201)`, so every rig
  trial is paired with one simulated trial. A trial is fixed by (base seed, condition,
  trial index), whatever controllers, conditions or trial count are selected.

## Conditions: protocol to simulation

| TEST_PROTOCOL condition | Part | Simulation condition (suite) | Notes |
|---|---|---|---|
| nominal | housing-only test part (rect_12x8 geometry) | `nominal` (standard) | |
| lateral 3 mm | housing-only | `lateral_3mm` (standard) | socket 3 mm off in a random direction |
| vision 1 mm | housing-only | `noise_1mm` (standard) | socket up to 3 mm / 5 deg yaw / 3 deg tilt off; injected vision error sigma 1 mm |
| vision 2 mm | housing-only | `noise_2mm` (standard) | as above, sigma 2 mm |
| Micro-Fit nominal | Micro-Fit 3.0, 4 circuits | `mf_nominal` (latching) | |
| Micro-Fit moderate | Micro-Fit | `mf_moderate` (latching) | socket up to 3 mm / 5 deg / 3 deg off, nominal vision |
| Micro-Fit vision 1 mm | Micro-Fit | `mf_noise_1mm` (latching) | |
| bad part: half latched | Micro-Fit | `mf_half_latched` (latching) | sim: hard stop 0.3 mm before the snap |
| bad part: broken latch | Micro-Fit | `mf_broken_latch` (latching) | sim: no latch ramp, no retention |
| bad part: stubbed terminal | Micro-Fit | `mf_stubbed_terminal` (latching) | sim: hard stop 0.2 mm after the terminals start |
| bad part: wrong polarization | Micro-Fit | `mf_wrong_polarization` (latching) | sim: hard stop 1 mm into the cavity |

Protocol items with no simulation counterpart (none is built here):

- **The real part's friction and contact stiffness.** The simulation uses the asset
  values (friction 0.3 for both parts). A calibrated prediction with the fitted values
  would be a second, separate prediction (see "Comparison", item 6).
- **Real lot-to-lot spread of the Micro-Fit mating forces.** The `latch_spread` suite
  models it, but a rig cannot set it. Not run here.
- **The physical bad parts are approximations.** A shim, a cut latch, a bent pin and a
  rotated plug will not stop at exactly the simulated depths.
- **The damage measure.** The simulation's damage criterion is a 10 ms average of the
  ground-truth housing contact force. A rig has only the wrist F/T sensor.
- **The rig machine.** `gantry` is the simulator's desk gantry with its remote-centre
  wrist and the modelled RCC stage (ATI 9115-001-A values). `arm` is the MuJoCo
  Menagerie UR5e model. BOM.md's arm options (UR3e, Franka, UFactory 850) are not
  modelled. Their predictions would come from the `arm` rows, labelled "different arm".

## Controllers

A `fixed`, C `adaptive`, F `spiral_rcc`, H `spiral_pull`, I `spiral_rcc_pull`,
J `spiral_rcc_verify`. Both machines.

## Trials and commands

50 trials per condition and controller, on both machines: 4 housing-only conditions
plus 7 Micro-Fit conditions, 6 controllers, 2 machines, so **6,600 trials**. The trial
count was sized to fit about 45 minutes at `--workers 2`. The basis is the v0.2e wall
times (`results/benchmark_v0.2e/*/trials.csv`, `wall_time_s`) and a 2-worker timing
check on development seed 2026: 96 gantry trials took 11 s and 84 arm latching trials
33 s. Estimate: about 30 minutes on an idle machine.

From the repository root, in this order:

```
PY=python
C=fixed,adaptive,spiral_rcc,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
for B in gantry arm; do
  $PY -m experiments.robustness --suite standard --backend $B --trials 50 --seed 20261201 \
    --workers 2 --no-plots --name v0.2f_rig_predictions/${B}_standard --controllers $C \
    --conditions nominal,lateral_3mm,noise_1mm,noise_2mm
  $PY -m experiments.robustness --suite latching --backend $B --trials 50 --seed 20261201 \
    --workers 2 --no-plots --name v0.2f_rig_predictions/${B}_latching --controllers $C
done
PYTHONPATH=. $PY results/v0.2f_rig_predictions/tables.py results/v0.2f_rig_predictions \
  > results/v0.2f_rig_predictions/TABLES.md
PYTHONPATH=. $PY results/v0.2f_rig_predictions/tables.py results/benchmark_v0.2e \
  > results/v0.2f_rig_predictions/CONTEXT_v0.2e.md
```

The last command lists the same conditions and controllers in benchmark_v0.2e (seed
20261130, 100 or 200 trials per condition). They are a context check with more
trials. They are not paired with the rig and are not the prediction.

A run that stops early is repeated with the same command, and `RUN_LOG.md` says so. If
the run goes well past 45 minutes, it is still finished, and `RUN_LOG.md` records the
time.

## Metrics (per machine, controller and condition, and pooled per part)

- **Success**: the simulation's scoring (`README.md`, "Scoring and safety"), with a
  Wilson 95% interval.
- **Bad units passed**: on good-part trials, a failed trial with no protective stop
  where the controller did not declare failure (`escape`). Wilson interval.
- **Bad parts passed**: the same on the four deliberately bad parts. Wilson interval.
- **Cycle time p50 and p95**: of successful good-part trials; for bad parts, the time
  to reject (all trials that did not pass the part).
- **Protective stops**: count and rate, with a Wilson interval.
- **Predicted differences between controllers**, paired on the same trials: C against
  I, J and F, for success, bad units and bad parts passed. The tables give C-only and
  other-only counts, exact McNemar p, and C minus the other with a Newcombe paired 95%
  interval.
- The final depth, tilt and yaw of every bad unit passed, to show what the rig's pose
  measurement has to resolve.

`tables.py` computes all of them from `trials.csv`.

## Comparison with a rig result (fixed now)

The rig's rows go in `results/hil_<name>/<machine>_<suite>/trials.csv` with the same
columns. On the rig, `success`, `protective_stop` and `declared_success` are set by
TEST_PROTOCOL.md section 5: measured final pose within the simulation's success limits,
no stop, the controller did not declare failure, and for the Micro-Fit the latch, pull
and continuity checks.
`PYTHONPATH=. python results/v0.2f_rig_predictions/tables.py results/v0.2f_rig_predictions --rig results/hil_<name>`
prints the comparison.

1. **Pairing.** Each rig trial is paired with the simulated trial with the same
   machine model, condition, controller and trial index. Only paired trials are
   compared. Trials whose set socket pose missed the drawn pose by more than the
   protocol's tolerance are reported separately and left out.
2. **Rates** (success, bad units, bad parts passed, protective stops), per machine,
   part and controller, pooled over that part's conditions. The difference is
   d = rig rate - simulated rate on the same trials, with a 95% Newcombe paired
   interval (Newcombe 1998, method 10). With δ = 5 percentage points:
   - **agrees**: the interval lies inside [-δ, +δ];
   - **disagrees**: the interval excludes 0 and does not lie inside [-δ, +δ];
   - **inconclusive**: otherwise.

   Per-condition rows are reported the same way, as secondary results. When both
   counts are 0, the interval is about plus or minus the Wilson upper bound for 0/n, so
   "agrees" needs about 73 or more paired trials.
3. **Cycle times** (p50, p95 of successful good-part trials): the ratio rig / sim, with
   a 95% percentile-bootstrap interval (10,000 resamples of each set, seed 20261201).
   It **agrees** if the interval lies inside [0.8, 1.25], **disagrees** if it excludes 1
   and does not lie inside that band, and is **inconclusive** otherwise. The rig must
   use the simulation's speed caps; a ratio says nothing about the controllers if it
   does not.
4. **Between-controller predictions** (C against I, J and F). For each, the rig's paired
   difference and its Newcombe interval, with exact McNemar p. The rig **reproduces** a
   predicted difference if its interval contains the simulated difference and its sign
   is the same. It **confirms the direction** if McNemar p < 0.05 with the same sign. It
   **contradicts** it if p < 0.05 with the opposite sign. `hardware/RIG_POWER.md` gives
   the trials needed to have an 80% chance of a confirmation.
5. **Which prediction applies.** A desk-gantry rig (BOM option 1) is compared with the
   `gantry` rows. A cobot rig is compared with the `arm` rows, labelled "UR5e model" or
   "different arm". A hybrid is compared with both, labelled.
6. **Calibrated re-prediction.** If the protocol's contact calibration is used to re-run
   the simulation with fitted friction and stiffness, that run is a second prediction.
   It needs its own pre-registration, committed before any rig outcome is tabulated.
   This frozen, uncalibrated prediction is reported in every case.
7. **More rig trials than 50 per condition.** The prediction for trial indices 50 and up
   comes from re-running the commands above with a larger `--trials` on this commit. The
   first 50 rows of each cell must then be identical to these. If they are not, the
   extension is not used.
8. No result from the rig may change this file, `tables.py` or the rule above.

## Expected, stated so it is not found later

From benchmark_v0.2e on the same conditions (seed 20261130, read before this file was
written; `CONTEXT_v0.2e.md` will list it), roughly:
- **Housing-only part:** C seats more than F and I, and passes no bad unit, while F and
  I pass some (about 7%).
- **Micro-Fit good parts:** F, I and J seat as many as C or more.
- **Micro-Fit bad parts:** C, H, I and J pass none, and F passes most.
- **Cycle time:** C's median is about twice F's on the housing-only part.

With 50 trials per condition, most between-controller differences will not reach
p < 0.05 in this run. That is expected and does not change the predictions.
