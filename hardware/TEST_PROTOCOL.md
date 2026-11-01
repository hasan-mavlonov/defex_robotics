# Hardware test protocol (W7 draft, for Hasan's approval)

Goal: the headline experiment V0.2 prepares for: **simulation-predicted success
against real success on the same connector, with confidence intervals**, for the
controllers that matter (C and the strongest conventional cell, F; A as a sanity
check).

## 1. Setup

- Rig: one option from [BOM.md](BOM.md), driven through
  `defex.hardware.backend.HardwareBackend` (same harness, controllers and scoring
  code as simulation). Control period 2 ms.
- Connector: the pilot customer's part once Hasan names it; until then a Molex
  Micro-Fit 3.0 header and receptacle (BOM section "Test connectors").
- Socket held in a precision jig on a two-axis micrometer table plus a rotary
  stage, so the true socket pose of every trial is set, not estimated.
- Plug held in a gripper whose in-hand pose is measured once per batch.

## 2. Trial design (paired, as in simulation)

- Conditions: `nominal`, `lateral_3mm`, `noise_1mm`, `noise_2mm`, `friction`-free
  (real friction is whatever the part has), plus the target connector's own
  latching behaviour once W3's model exists.
- **100 insertions per condition and controller.** At 100 trials a 95% Wilson
  interval is at most +/-10 points wide, enough to tell 85% from 99%.
- Trial *i* of a condition uses `sample_scenario(condition, i, seed)` from the
  pre-registered seed: the operator sets the jig to that trial's socket offset and
  yaw; the "vision" estimate the controller receives is drawn exactly as in
  simulation (a deliberate, known camera error). Every controller sees the same
  trial list, in a randomized controller order per trial to spread drift.
- Pre-register the seed, conditions, controllers and analysis in
  `results/hil_<name>/PREREGISTRATION.md` before the first insertion, as for the
  simulation benchmarks.
- Use `hardware_noise()`: no synthetic noise on top of the real sensors.

## 3. Safety limits

- Same limits as simulation, enforced by the harness on the measured wrench:
  protective stop at 30 N or 0.6 N m, controller aborts at 20 N.
- Hardware layer adds: workspace box of +/-10 mm around the jig in x/y and a
  hard lower z limit 1 mm below the seat; F/T saturation check (abort if any
  channel exceeds 80% of range); a hardware e-stop within reach; speeds capped at
  the simulation values.
- Replace the receptacle after any protective stop, after 25 insertions (Micro-Fit
  durability), or if it shows visible damage; log replacements.

## 4. Calibration moves (before each session)

- **F/T sign check (first, every new sensor or driver setting):** with the tool
  in free space and tared, press up on the plug tip by hand. The harness's
  estimated external force must point up (positive along the insertion axis
  away from the socket). If it points down, the `NetFTDriver` `convention` is
  wrong: every contact force would be reversed and the force loop would push
  harder on contact. Do not run any controller until this check passes.

- Payload identification: the harness's nine-pose routine
  (`defex.tasks.calibration.identify_payload`).
- Contact calibration: five moves of `defex.calibration.contact_fit.CalibrationMove`
  (1 mm onto the lead-in, 2 mm/s descent), logged as `t_s,depth_mm,fz_n`; fit with
  `fit_contact` and save the overlay report. The fitted friction and contact
  stiffness feed the simulator for the paired prediction.

## 5. Ground truth on hardware

The harness's measured "ground truth" is encoders plus the wrist sensor. Seating
is confirmed after every trial, by an operator blind to the controller:

1. visual check of the latch (photo saved per trial);
2. pull test at 50% of the rated retention force for 1 s: pass if the plug
   moves less than 0.2 mm;
3. electrical continuity on all circuits (simple fixture).

A trial succeeds only if the controller succeeded by the harness's criteria and
all three checks pass. A controller-declared success that fails a check is a false
accept (a bad unit passed).

## 6. Data format

Per trial: the harness's `TrialResult` row (`trials.csv`), the event log
(`events.json.gz`), the decimated trajectory (`.npz`, not committed: attach to a
release), the inspection row (`inspection.csv`: trial id, latch ok, pull
displacement mm, continuity ok, operator, photo file), and the session's
calibration files. Session metadata: rig, sensor serial, connector lot, room
temperature, operator.

## 7. Analysis

- Success per controller and condition with Wilson intervals; paired McNemar
  between controllers.
- **Sim-to-real:** for each controller and condition, simulated success (same
  seed, calibrated contact parameters) against real success; report the
  difference with its interval. The simulator is trusted for a claim only where
  that difference is inside the interval.
- Bad units passed, protective stops, cycle times, force traces against the
  simulated ones.
