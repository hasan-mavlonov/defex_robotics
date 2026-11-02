# v0.2f latch fit: synthetic recovery pass rule

Written and committed before the recovery run (`experiments/latch_fit_recovery.py`).
The fitter (`defex/calibration/latch_fit.py`) was developed on curves from development
seed 2027 only (part variations not in the list below). The tolerance floors below were
set after those development runs; the recovery sets use seed 2026 and had not been
simulated or fitted when this file was committed.

## Data

- Connector: `microfit3_4ckt`. Simulator: MuJoCo gantry (default `FixtureConfig`,
  10 N/mm servo), `experiments/latch_fit_sim.py`: plug on the socket axis 0.5 mm above
  the mouth, setpoint descends at 1 mm/s until the tared axial force passes the insert
  target (35.2 N), holds 0.1 s, climbs at 1 mm/s until the pull reaches 29 N (50% of the
  rated retention) or the setpoint has climbed 8 mm. Logged every 2 ms through
  `SensorSuite(SensorNoiseConfig())` (F/T bias 0.3 N sigma per axis, untared; white
  noise 0.03 N; encoder 0.002 mm), plus a depth offset.
- Parameter sets, drawn from `np.random.default_rng(2026)` in this order (offset first
  for the nominal set; then per set: latch shift, latch peak scale, terminal scale,
  depth offset, sensor seed), uniform within the `latch_spread` bands
  (`defex/tasks/conditions.py`: shift -0.2..0.2 mm, latch peak 0.5..1.5, terminals
  0.8..1.6) and depth offset -0.5..0.5 mm:

| set | latch shift mm | latch peak x | terminals x | depth offset mm | sensor seed |
|---|---|---|---|---|---|
| nominal | 0 | 1 | 1 | -0.321 | 56731231 |
| off01 | -0.013 | 0.871 | 1.084 | 0.291 | 1374203059 |
| off02 | 0.162 | 0.677 | 1.322 | -0.202 | 355781144 |
| off03 | 0.168 | 1.136 | 1.402 | 0.015 | 2076535513 |
| off04 | 0.130 | 0.948 | 1.071 | -0.222 | 313805771 |
| off05 | 0.010 | 0.931 | 1.331 | -0.487 | 486046538 |
| off06 | -0.021 | 0.865 | 0.956 | 0.095 | 701295860 |
| off07 | -0.080 | 0.709 | 1.500 | 0.297 | 934827884 |
| off08 | 0.043 | 0.845 | 1.557 | 0.063 | 1277876284 |
| off09 | 0.160 | 0.819 | 1.357 | -0.186 | 929350906 |
| off10 | -0.095 | 1.201 | 0.982 | -0.007 | 1015247637 |

The latch_spread knobs move the latch depths, the latch peak and the terminal forces.
The other parameters (wipe, lead, rise, fall, play, latch stiffness, bristle) stay at
the model's values in every set; their recovery is still judged.

## Judged design

`main`: one push-click plus guarded pull at 1 mm/s per part, fitted alone with
`fit_latch(spec, [move], seed=2026)` and its default free set (all 12 part
parameters when a latched pull is present).

## Judged parameters and tolerances

A parameter is recovered when |fit - truth| <= max(0.15 x |truth|, floor).
Floors: 0.03 mm for depths and lengths, 0.5 N for forces, 0.15 for snap drop
(a fraction, truth 1.0), none for latch stiffness (N/mm).

Depth parameters are judged as distances back from the seat, because a free depth
offset makes absolute depths unidentifiable (see REPORT.md):

terminal wipe, terminal lead, terminal peak (all circuits), terminal slide, latch
onset-to-seat distance (rise + fall + post-snap), latch rise, latch peak force, latch
fall, snap drop, post-snap stroke, latch play, latch stiffness, bristle, and the
depth offset (fitted seat minus true seat; truth 0, floor 0.03 mm).

## Pass rule

A parameter passes if it is recovered on the nominal set and on at least 8 of the 10
off-nominal sets. The fitter passes if every judged parameter passes. A parameter
that fails is reported as failing; the rule is not changed after the run.

## Diagnostics (reported, not judged)

Same 11 sets, same seeds and offsets:

- `noise10`: F/T white noise x10 (0.3 N);
- `push_only`: no pull (play, latch stiffness, bristle and snap drop then stay fixed);
- `speed_0.5`, `speed_2`, `speed_5`: the main move at other speeds;
- `stiff_rig`: gantry servo 200 N/mm instead of 10 N/mm;
- `plus_disabled`: the main move plus one latch-disabled push and pull of the same
  part (simulated as `broken_latch`), fitted jointly.

Plus a local identifiability study (Gauss-Newton correlations from the fitter's own
model at the nominal part) and the worked example (nominal curve as "real" data,
and the same curve with rounded corners), both described in REPORT.md.
