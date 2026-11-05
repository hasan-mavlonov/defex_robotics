# v0.2g drift-stream fix: report

## Result

Fixing the F/T-drift random stream changes no pre-registered heldout2 verdict, in the drift
family or on the whole suite. This is a correction check, written up after an independent
code review found the defect; it is not a pre-registered test (plan: `PLAN.md`, committed
before the rerun at c3f967a).

## The defect

In `results/heldout2_v0.2f` (commit 6ea164e, seed 20261207), each F/T-drift trial's drift
direction came from the same child random stream as the socket disturbance (spawn_key (4,)
of the trial seed). The pre-registration said "random directions". The direction was a
fixed function of the disturbance draws. The reviewer measured, over 40,000 trial seeds,
a correlation of 0.34 between |drift x| and the lateral offset angle, and +0.09 between
|drift z| and the yaw draw. Each direction was still uniform on the sphere and pairing
across controllers was intact.

Fix: `defex/perception/sensors.py` draws the drift from spawn_key (16,). Only trials with
drift on change. `experiments/v02f_h2_drift_axes.drift_rates` keeps the old stream by
default, so the v0.2f drift diagnosis still reproduces.

## Rerun

The pre-registered heldout2 command restricted to `h2_ft_drift_0.1` and `h2_ft_drift_0.3`:
40 trials each, all ten controllers, seed 20261207, gantry and arm, 1,600 trials. Both
`config.json` files record commit c3f967a, `git_dirty: false`.

## Numbers

`TABLES.md` (drift family, before and after) and `WHOLE_SUITE.md` (whole suite with the
drift rows replaced), made by `experiments/v02g_drift_stream_compare.py` and
`experiments/v02g_drift_stream_whole_suite.py`.

| Cell | Before (v0.2f) | After (fixed stream) | Verdict |
|---|---|---|---|
| arm drift, C vs best fair (D) | 76.2% vs 100%, 0/19, p 3.8e-6 | 80.0% vs 100%, 0/16, p 3.1e-5 | C below D, unchanged |
| gantry drift, C vs best fair (D) | 100% vs 100% | 100% vs 100% | matches, unchanged |
| arm drift, bad units C / H / I / J | 8 / 0 / 1 / 5 of 80 | 8 / 0 / 0 / 4 of 80 | C passes more than H and I, unchanged |
| arm drift, J vs C seated | 82.5% vs 76.2%, p 0.23 | 83.8% vs 80.0%, p 0.51 | J matches C, unchanged |
| gantry drift, J vs C seated | 100% vs 100% | 98.8% vs 100%, p 1 | J matches C, unchanged |
| arm whole suite, C vs best fair (F) | 88.8% vs 79.2%, p 0.00037 | 89.5% vs 79.5%, p 0.00015 | C ahead, unchanged |
| gantry whole suite, J vs C seated | 97.2% vs 94.0%, p 0.019 | 97.0% vs 94.0%, p 0.036 | J ahead, unchanged |
| arm whole suite, bad units C / I / J | 8 / 63 / 5 of 400 | 8 / 62 / 4 of 400 | unchanged |

C passes 8 bad units in arm drift with the fixed stream too, so the VERIFY preload
mechanism in `results/v0.2f_h2_diagnosis` does not depend on the shared stream.

## What this does not change

`results/heldout2_v0.2f` stays as the pre-registered result. Its drift rows reproduce at
6ea164e and at any commit before this fix. After this fix they no longer reproduce at
HEAD; use 6ea164e (recorded in its `config.json`).

## Files

`PLAN.md`, `REPORT.md`, `TABLES.md`, `WHOLE_SUITE.md`; `gantry_drift/` and `arm_drift/`
(`trials.csv`, `summary.json`, `summary.csv`, `config.json`). `events.json.gz` not
committed. Code: `defex/perception/sensors.py`, `experiments/v02f_h2_drift_axes.py`,
`experiments/v02g_drift_stream_compare.py`, `experiments/v02g_drift_stream_whole_suite.py`,
`tests/test_heldout2_conditions.py`.
