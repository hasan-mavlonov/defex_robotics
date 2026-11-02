# v0.2e arm reset: a trial no longer depends on what its worker ran before

Branch `v0.2e/arm-reset`, fix in commit 951c62a (on top of 966a5f5). Dev seed 2027 everywhere.
Every number below is in `COMPARE.txt`, produced by `compare.sh` from the runs in `after/` (fixed
code; their `config.json` records commit 951c62a, not dirty) and `before/` (the 966a5f5 code,
exported with `git archive` into a plain directory, so their `config.json` says
`git_commit: unknown`). `run.sh` recreates everything. Only `wall_time_s` (wall clock) is left out
of the comparisons; every other column, including `cycle_time_s` and `sim_time_s`, is compared exactly.

## Cause

Each backend caches one compiled MuJoCo model per connector and wrist (rigid or RCC) and reuses it
across trials. `load()` writes the trial's in-hand grasp offset into that model
(`body_pos` / `body_quat` of the `connector` body). When the worker switches to another model and
later comes back, `_index_model()` derives the payload and the `FixtureDynamics` again, and it did
that before `load()` set the new trial's grasp, so with the previous trial's grasp offset still in the
model. The effective mass along z (`_tool_effective_mass_z`, from the mass matrix) depends on where
the connector's mass sits, so it changed in the last digits with worker history.

Only `generalization_combined` has a grasp offset, so only its trials can see a stale one. A worker
switches models whenever a rigid-wrist controller and an RCC controller follow each other, which
happens all the time in the A-J order and with several workers. Nothing else in the model is
changed per trial: friction and grasp are written on every load, and `mj_resetData` resets the rest.

Minimal reproduction (`repro_dynamics.py`, output in `repro/`): load the RCC model with a grasp
error, switch to the rigid model, switch back to the RCC model with the nominal grasp.

| backend | effective_mass_kg, fresh | after the other trial, 966a5f5 | after, fixed |
|---|---|---|---|
| arm | 6.320843419144047 | 6.320808466203506 | 6.320843419144047 |
| gantry | 0.8839999999999999 | 0.8839999862943175 | 0.8839999999999999 |

All other `FixtureDynamics` fields were the same. At trial level, `tests/test_backend_reset.py`
runs F on trial 0 fresh, then the same trial after F trial 1 and H trial 1 in the same task. On
966a5f5 the rows differ (final depth, pose, forces; `repro/before_test.txt`: 3 of 3 tests fail). With
the fix they are equal (`repro/after_test.txt`: 3 of 3 pass).

## Fix

`defex/sim/mujoco_backend.py`: `_index_model()` puts the nominal grasp (the identity, which is also
the compiled model's default) back into the connector body before it derives anything. `load()` then
sets the trial's own grasp, as before, through a new small helper `_set_grasp()`, which the arm backend
uses too. The dynamics are now those of the cell with a nominal grasp. A fresh worker always computed
them that way, so the values do not change; only the stale case goes away. Controller, recovery and
perception code are unchanged.

## Proof: the order and number of workers no longer matter

Arm, `generalization_combined`, 20 trials. H (`spiral_pull`, rigid wrist) is run between F and I, as
in the benchmark's A-J order, so the worker switches models between them. With only F and I there is
no model switch, so even 966a5f5 would match (`gen_FI_w1` is that run).

| comparison | 966a5f5 | fixed |
|---|---|---|
| F vs I, order F,H,I, 1 worker | 20 / 20 rows differ | 0 / 20 |
| F vs I, order F,H,I, 2 workers | 20 / 20 | 0 / 20 |
| F vs I, order I,H,F, 1 worker | 20 / 20 | 0 / 20 |
| F vs I, F and I only, 1 worker | not run | 0 / 20 |
| all rows: 1 worker vs 2 workers | 15 / 60 | 0 / 60 |
| all rows: order F,H,I vs I,H,F | 40 / 60 | 0 / 60 |

On 966a5f5 the differing columns are final depth, lateral, tilt, yaw, penetration and the peak
forces and torque. No outcome and no cycle time differed in these runs.

A second arm suite, `latching` (7 conditions, 5 trials, F, H, I; no grasp offset): with the fix, 1 vs 2
workers 0 / 105 rows differ, order F,H,I vs I,H,F 0 / 105, and fixed vs 966a5f5 0 / 105.

## Before/after on seed 2027, 966a5f5 vs fixed, 1 worker, all ten controllers A-J

| run | trials | rows that change | outcomes that change | largest cycle-time change |
|---|---|---|---|---|
| arm `generalization_combined` | 20 x 10 | 80 / 200 | 0 | 46 ms |
| gantry `generalization_combined` | 20 x 10 | 0 / 200 | 0 | 0 |
| arm standard, the other 19 conditions | 1 x 10 | 0 / 190 | 0 | 0 |
| gantry standard, the other 19 conditions | 1 x 10 | 0 / 190 | 0 | 0 |
| arm `heldout` (5 conditions) | 1 x 10 | 0 / 50 | 0 | 0 |
| arm `latching` (7) | 1 x 10 | 0 / 70 | 0 | 0 |
| arm `latch_spread` (9) | 1 x 10 | 0 / 90 | 0 | 0 |

On the arm's `generalization_combined`, the 80 rows are all 20 trials of G, H, I and J: in this order on
one worker those are the controllers that come back to a model after a switch. A-F do not change. G's
cycle times move by at most 46 ms and H's by at most 26 ms; I's and J's cycle times do not move, only
their last digits do. With the fix, F and I are identical in all 20 trials; on 966a5f5 they differ in 20 / 20.

Gantry: its effective mass also had the stale value (table above), but it does not change any gantry
row. The only consumer is `contact_speed_scale`, `min(1, sqrt(1 kg / m_eff))`, and the gantry's
0.884 kg is below 1 kg, so the scale is 1 either way.

Against `results/v0.2d_dev_check` (9 workers, commit 43c8b6b; same simulation code as 966a5f5, only J's controller had a reset added
since): arm `generalization_combined` differs from the fixed 1-worker run in 40 / 200 rows,
10 each for G, H, I and J, cycle times by up to 56 ms; there F vs I differ in 10 / 20, as the
pre-registration states. Gantry: 0 / 200.

Which conditions can change, in short: only `generalization_combined`, on the arm, and only in the
last digits. The cycle time changes by tens of milliseconds for some controllers, but no outcome
changed in any run here. Every other condition has no grasp offset, so its model never holds a stale
one. The 1-trial runs above check this by experiment, not only by argument.

## Not run

- The other arm suites and the other 19 standard conditions were run with 1 trial per cell, not 20
  (CPU budget: one free core). `generalization_combined` was run with 20.
- No multi-worker before/after for A-J. Workers 2 were used only on F, H, I (the
  `generalization_combined` and `latching` runs above).
- benchmark_v0.2c and benchmark_v0.2d were not rerun. Their arm `generalization_combined` rows will
  differ from a rerun on the fixed code in the last digits and in cycle times for the controllers that
  had a stale grasp in their worker. On the evidence here, no outcome changes.
