# Hardware test protocol (W7 draft, for Hasan's approval)

Nothing has been bought, no vendor has been contacted and no rig has been chosen.
Choosing a rig, buying parts and contacting vendors all need Hasan's approval
(ASK HASAN).

Goal: compare the simulation's predictions with real results on the same parts and the
same trial list, with intervals. The predictions were frozen before any rig exists, in
[`results/v0.2f_rig_predictions`](../results/v0.2f_rig_predictions/PREREGISTRATION.md)
(seed 20261201). The rule for comparing a rig result with them is fixed there.

## Controllers

| Ctrl | What it is | Why it is in the rig test |
|---|---|---|
| C `adaptive` | the product candidate | the controller under test |
| I `spiral_rcc_pull` | spiral search on an RCC wrist, plus a pull test | the strongest fair baseline: in the benchmarks it passes no bad part and matches C on latching parts |
| J `spiral_rcc_verify` | F's insertion plus C's VERIFY | separates C's insertion from C's verification (not a fair baseline) |
| F `spiral_rcc` | spiral search on an RCC wrist, no pull test | the conventional cell; fastest, passes most bad parts in simulation |
| A `fixed` | fixed program | sanity check, 20 trials per condition |
| H `spiral_pull` | spiral search on a rigid wrist, plus a pull test | optional |

The earlier draft compared C with F only. In benchmark_v0.2d, v0.2d_rep and v0.2e, F
matches or beats C on latching good parts, and I and J pass no deliberately bad part
(`results/benchmark_v0.2e/REPORT.md`). Comparing with F alone would test a weaker
baseline than the evidence needs.

## 1. Setup

- **Rig.** One option from [BOM.md](BOM.md), driven through
  `defex.hardware.backend.HardwareBackend` (the same harness, controllers and scoring
  code as the simulation). Control period 2 ms.
- **Parts.** Two, as in the simulation:
  1. **Housing-only test part**: a plug and socket made to
     `assets/connectors/rect_12x8.json` (12 x 8 mm plug, 0.5 mm radial clearance,
     15 mm depth, 0.8 mm lead-in). No terminals, no latch. The material pair is not
     chosen. The simulation assumes friction 0.3; the rig's friction is measured in
     calibration (section 4).
  2. **Molex Micro-Fit 3.0, 4 circuits, dual row**: receptacle housing 43025-0408 with
     crimp terminals, into vertical header 43045-0429. These are the part numbers in
     `assets/connectors/microfit3_4ckt.json`. The pilot customer's part replaces it once
     Hasan names one; that part then needs its own connector file and a new prediction.
- **Socket jig.** It must set, for every trial, the socket offset x and y (up to 3 mm),
  yaw (up to 5 deg) and tilt (up to 3 deg about any horizontal axis). The earlier draft
  had a two-axis table and a rotary stage, which cannot set tilt. Without tilt,
  `noise_1mm`, `noise_2mm`, `mf_moderate` and `mf_noise_1mm` could not be set. Ways to
  set tilt are listed in BOM.md ("Socket jig"). The set pose is measured and logged for
  every trial. Tolerance: 0.02 mm and 0.05 deg from the drawn pose; trials outside it
  are reported separately (pre-registration, "Comparison", item 1).
- **Wrist.** A, C and H run on a rigid wrist. F, I and J run on a passive RCC (the
  simulation uses ATI 9115-001-A values). The wrist cannot change between trials, so
  trials run in wrist blocks (section 2).
- **Plug in hand.** The plug's in-hand pose is measured once per batch.

## 2. Trial design (paired with the simulation)

| Condition | Part | Simulation condition | What the jig sets |
|---|---|---|---|
| nominal | housing-only | `nominal` | aligned socket |
| lateral 3 mm | housing-only | `lateral_3mm` | 3 mm offset, random direction |
| vision 1 mm | housing-only | `noise_1mm` | up to 3 mm, 5 deg yaw, 3 deg tilt; injected vision error sigma 1 mm |
| vision 2 mm | housing-only | `noise_2mm` | as above, sigma 2 mm |
| Micro-Fit nominal | Micro-Fit | `mf_nominal` | aligned socket |
| Micro-Fit moderate | Micro-Fit | `mf_moderate` | up to 3 mm, 5 deg, 3 deg; nominal vision |
| Micro-Fit vision 1 mm | Micro-Fit | `mf_noise_1mm` | as above, sigma 1 mm |
| half latched | Micro-Fit bad part | `mf_half_latched` | a hard stop (shim) that holds the plug about 0.3 mm short of the latch snap |
| broken latch | Micro-Fit bad part | `mf_broken_latch` | latch arm cut off the receptacle |
| stubbed terminal | Micro-Fit bad part | `mf_stubbed_terminal` | one header pin bent so it butts the receptacle |
| wrong polarization | Micro-Fit bad part | `mf_wrong_polarization` | plug turned 180 deg in the gripper |

- The physical bad parts only approximate the simulated ones: the stop depths will not
  match exactly, and a bent pin may buckle where the simulated one is rigid. Each bad
  part's stop depth is measured once by hand and logged.
- The real friction is whatever the part has; there is no friction condition. The
  simulation's `latch_spread` suite (lot-to-lot mating forces) cannot be set on a rig and
  is not part of the test.
- **Trial list.** Trial i of condition c uses `sample_scenario(c, i, 20261201)`: the
  operator sets the jig to that trial's socket pose, and the controller gets the
  "vision" estimate drawn exactly as in the simulation (a known, injected camera error).
  Every controller sees the same trial list. Trial indices 50 and up need the
  simulation extended first (pre-registration, item 7).
- **Order.** Trials run in wrist blocks: rigid (A, C, H) and RCC (F, I, J). Within a
  block the jig is set once per trial and each controller runs it in a random order.
  Blocks alternate across sessions to spread drift. Payload identification is repeated
  after every wrist change.
- **Trial counts** (from [RIG_POWER.md](RIG_POWER.md), simulation rates; real rates will
  differ):
  - Housing-only part: **100 trials per condition** (400 per controller). In the
    simulation, C against I needs about 90-100 paired trials for 80% power on bad units
    and 70-100 on success, and C against J needs 170-290 on success. 100 per condition is
    enough for these if the rig's rates are near the simulation's.
  - Micro-Fit good parts: **100 trials per condition** (300 per controller). This cannot
    separate C from I, J or F. The simulation needs about 780-1,200 paired trials on
    the gantry, and 7,800 or more on the arm, for 80% power. The rig reports rates with
    intervals and makes no between-controller claim on this part.
  - Micro-Fit bad parts: **25 per defect** (100 per controller). If a controller passes
    none, the Wilson 95% upper bound is 3.7%. F, which passes about 60% in the
    simulation, separates from C at this count.
  - Zero bad units in n trials gives a Wilson 95% upper bound of 3.7% at n = 100, 1.9%
    at 200, 0.76% at 500 and 0.38% at 1,000. The earlier draft's 100 per condition could
    not tell 99% from 97% success (power about 0.06 for C against I on the full standard
    suite), or 0 bad units from about 2% (power about 0.01).
  - **I and F are the same program on the housing-only part.** I's pull test runs only
    after a latching insertion (`defex/control/spiral_search.py`, controller I), so on
    the housing-only part I's simulated rows equal F's (RIG_POWER.md: identical counts).
    The rig runs that program once on the housing-only part and scores it as both F and
    I. H and D are likewise the same there.
  - The total is about 3,000 insertions (C, F, J: 800 each; I: 400, Micro-Fit only;
    A: 220), or 3,800 with H.
    Micro-Fit receptacles and headers are replaced every 25 insertions, which comes to
    about 70 sets. The jig is set about 1,600 times (once per trial index per block). At
    an assumed 1 minute per setting (unsourced), that is about 27 hours of setting alone.
    A motorized jig would cut this.
- Pre-register the rig run in `results/hil_<name>/PREREGISTRATION.md` before the first
  insertion: rig, parts, lots, conditions, trials, and the comparison rule from the
  prediction's pre-registration, unchanged.
- Use `hardware_noise()`: no synthetic noise on top of the real sensors.

## 3. Safety limits

The harness enforces the connector's own force budget on the measured wrench, as in the
simulation (`defex/tasks/insertion.py`; `results/v0.2d_force_budget/REPORT.md`):

| Part | Insert force | Controller abort | Protective stop | Damage |
|---|---|---|---|---|
| Micro-Fit (`microfit3_4ckt.json`) | 35.2 N (1.1 x the 32 N datasheet maximum mating force) | 40 N | 48 N | 58 N (minimum latch strength) |
| Housing-only (`SafetyConfig`, C's `AdaptiveConfig`) | 3-8 N (per controller) | C: 20 N | 30 N | 45 N |

Torque stop 0.6 N m on both parts. The earlier draft gave 30 N / 20 N for every part.
On the Micro-Fit, every controller pushes at 35.2 N, so a 30 N stop would end every
insertion.

- **Damage on the rig.** The simulation's damage measure is a 10 ms average of the
  ground-truth housing contact force; a rig has no such sensor. On the rig, a 10 ms
  average of the measured force above the damage value counts as damage, and the part is
  replaced.
- **Sensor range.** The F/T saturation check aborts if any channel exceeds 80% of its
  range. So the axial range must be at least 58 / 0.8 = 72.5 N, or the check fires below
  the damage bound. A 60 N range is the bare minimum: its 80% point is the 48 N stop.
  BOM.md flags the sensors that do not meet this.
- Hardware layer: a workspace box of +/-10 mm around the jig in x and y; a hard lower z
  limit 1 mm below the seat; a hardware e-stop within reach; speeds capped at the
  simulation values.
- **Replacements.** Replace the Micro-Fit receptacle and header after 25 insertions (the
  datasheet durability is 30 cycles), after any protective stop or damage, or on visible
  damage. Inspect the housing-only part every 100 insertions; its wear life is unknown.
  Log every replacement.

## 4. Calibration moves (before each session)

- **F/T sign check (first, for every new sensor or driver setting).** With the tool in
  free space and tared, press up on the plug tip by hand. The harness's estimated
  external force must point up (positive along the insertion axis, away from the
  socket). If it points down, the `NetFTDriver` `convention` is wrong: every contact
  force would be reversed, and the force loop would push harder on contact. Do not run
  any controller until this check passes.
- **Payload identification**: the harness's nine-pose routine
  (`defex.tasks.calibration.identify_payload`), after every wrist change.
- **Contact calibration**: five moves of `defex.calibration.contact_fit.CalibrationMove`
  (1 mm onto the lead-in, 2 mm/s descent), logged as `t_s,depth_mm,fz_n`. Fit them with
  `fit_contact` and save the overlay report. The fitted friction and contact stiffness
  can feed a second, calibrated prediction. That prediction needs its own
  pre-registration (prediction pre-registration, item 6).
- **Pose measurement check (section 5)**: before each session, measure a reference plug
  at known tilts and yaws (0, 2, 3 and 4 deg) and depths, set with gauge blocks.

## 5. Ground truth on hardware

The harness's "ground truth" on hardware is the encoders plus the wrist sensor. The
connector pose is the TCP pose times the nominal grasp. It does not see in-hand slip,
the RCC's deflection or the plug's pose in the socket. The latch photo, pull test and
continuity check also do not measure yaw or tilt.

C's main measured difference from I and F is bad units: plugs at full depth but 3-5 deg
off in yaw or tilt. Over the three benchmark seeds, 392 of I's 433 housing-only bad units
were at full depth, and every one of the 392 was over 3 deg in tilt or yaw (median
3.45 deg, maximum 5.0 deg; [RIG_POWER.md](RIG_POWER.md), last table). A rig without a
pose measurement cannot test that difference. The rig therefore measures the plug's
final pose relative to the socket. Target resolution: 0.1 deg in yaw and tilt near
3 deg, 0.05 mm in depth and lateral offset.

### Measurement options for the final plug pose

Cost classes are rough and unsourced: low under $1k, medium $1k-10k, high over $10k.

| Method | What it resolves | Notes | Cost class |
|---|---|---|---|
| Encoders x nominal grasp (the harness now) | TCP pose only | misses slip, RCC deflection and socket-side error | none |
| Laser triangulation displacement sensors, 4-6 heads on a bridge fixed to the jig | depth, tilt about two axes, yaw, lateral offset, from plug and socket faces; um-class distance, so better than 0.05 deg over a 15 mm baseline | non-contact; dark or glossy plastic and face flatness limit accuracy; layout is tight with the gripper closed | medium |
| Contact probes (LVDT or digital indicators) on the same bridge | as above | the probe force can move a plug that is not latched; low-force probes needed | low to medium |
| Two calibrated cameras with fiducial markers on plug and socket | full relative pose; about 0.1-0.5 deg, depending on lens and marker size (to be shown on the reference plug) | non-contact; works with the gripper closed and after release; images give an audit trail | low |
| Go/no-go gauge that fits over the seated plug only within 3 deg and the depth limit | pass or fail at the limit only | fast; independent of the other methods | low |
| Offline measurement (CMM or measuring microscope) of the removed assembly | best accuracy | slow; removal can disturb the pose; for samples only | high per sample, or a lab service |
| Latch photo, pull test, continuity (earlier draft) | latch engaged, retention, circuits | does not measure yaw or tilt | low |

**Primary: laser triangulation displacement sensors**, read at the end of the trial with
the gripper still closed (the simulation scores the plug while the fixture holds its
last setpoint), and again after release. They resolve the 3 deg limit with margin. If
the reference-plug check shows they cannot see a face with the gripper closed, that
angle is measured after release, and the report says so.

**Checks:**
- the camera pair on every trial (an independent method, with an image per trial);
- the go/no-go gauge on every trial;
- offline measurement of a random 5% of trials, and of every trial where the primary
  and a check disagree on pass or fail.

On the Micro-Fit, these also run on every trial, as in the earlier draft:
1. a visual check of the latch (photo saved);
2. a pull test at 50% of the rated retention force (29 N) for 1 s, passed if the plug
   moves less than 0.2 mm;
3. electrical continuity on all circuits.

All checks are done by an operator blind to the controller.

**Scoring.** A trial succeeds only if all of these hold:
- the primary measurement puts the plug inside the simulation's limits (depth >= full
  depth - 0.5 mm, lateral offset <= clearance + 0.15 mm per axis, tilt and yaw within
  3 deg);
- no protective stop and no damage;
- the controller did not declare failure;
- on the Micro-Fit, all three checks pass.

A trial that fails, with no protective stop, where the controller did not declare failure,
is a **bad unit passed** (on a deliberately bad part, a **bad part passed**). This is the
simulation's definition.

## 6. Data format

Per trial:
- the harness's `TrialResult` row (`trials.csv`, same columns as the simulation, with
  `success` set by section 5);
- the event log (`events.json.gz`);
- the decimated trajectory (`.npz`; not committed, attach to a release);
- `pose.csv`: trial id, state (held / released), method, depth mm, lateral x and y mm,
  tilt deg, yaw deg, gauge pass, operator;
- `jig.csv`: trial id, drawn and measured socket x, y, yaw, tilt and tilt azimuth;
- `inspection.csv` (Micro-Fit): trial id, latch ok, pull displacement mm, continuity ok,
  operator, photo file;
- the session's calibration files.

Session metadata: rig, wrist (rigid or RCC), sensor serial, connector lot, room
temperature, operator.

## 7. Analysis

- Success, bad units passed, bad parts passed and protective stops, per controller and
  condition, with Wilson intervals. Cycle time p50 and p95.
- Between controllers: C against I, J and F, paired, with exact McNemar tests, on the
  housing-only part. On the Micro-Fit good parts, rates only (section 2).
- **Sim against real**: the rule in
  `results/v0.2f_rig_predictions/PREREGISTRATION.md`, "Comparison with a rig result"
  (paired difference with a Newcombe interval and a 5-point agreement band; cycle-time
  ratios with a bootstrap interval and a 0.8-1.25 band), run by
  `results/v0.2f_rig_predictions/tables.py --rig`.
- Force traces against the simulated ones, for the same trials.
