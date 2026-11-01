# v0.2c: gantry re-tuning of D, E and F with latching parts (development)

Development measurements in simulation. Tuning on dev seed 2026; before/after on
dev seed 2027, which no choice used. Tables: `tables.md`
(`python -m experiments.v02c_gantry_tables`). Before = 0300106 (the arm-tuned
v0.2c baselines, gantry settings from W1), after = 0ae06ba. All `config.json`
files show `git_dirty: false`.

## Result

The gantry baselines were never tuned with the latching connector, because W1
came before it. Tuned now, with the protocol the arm got
([`SELECTION_RULE.md`](SELECTION_RULE.md), committed before any run), **F seats
every latching good part on dev seed 2027, and C does not**:

| Dev seed 2027 | C | F before -> after | D before -> after |
|---|---|---|---|
| Latching good parts (60) | 54 | 53 -> **60** (F vs C: 0 / 6, p = 0.031) | 29 -> 51 |
| Standard suite (200) | 198 | 192 -> 193 (C vs F: 5 / 0, p = 0.062) | 188 -> 192 |
| Bad parts passed as good (80) | **0** | 51 -> 52 | 30 -> 36 |
| Good units/h, standard (60 s per stop) | 614 | 870 -> 1,145 | 679 -> 895 |
| Good units/h, latching good parts | 312 | 507 -> 971 | 111 -> 502 |
| Median good cycle, standard (s) | 5.29 | 3.54 -> 2.43 | 3.53 -> 2.87 |

This changes how benchmark_v0.2b's gantry latching result should be read. There
C seated 95.7% of latching good parts against F's 89.0% (p = 2.4e-6), but F and D
ran at settings tuned without that connector. On this dev seed, tuned F is level
with or ahead of C on every good-part measure on the gantry too. What remains of
C's lead is bad parts: C passed 0 of 80, tuned F 52 and tuned D 36.

Only a pre-registered run on a fresh seed can confirm this; seed 2027 has 20
trials per latching condition.

## What changed (confirm rank 1 of each controller)

| | Gantry setting before (W1) | After |
|---|---|---|
| D | search 2 N, pitch 1.0 mm, spiral 2.5 mm/s, stiff search, one speed | search 3 N, pitch 0.5 mm, spiral 5 mm/s, search stiffness 2 N/mm, free speed 25 mm/s in the cavity |
| F | search 3 N, pitch 1.0, spiral 5, insert 3 N, 3 attempts, push 0.5, guarded 10 mm/s | search 2 N, pitch 0.5, spiral 2.5, insert 8 N, 2 attempts, push 0.3, guarded 25 mm/s, continue from the measured position when the hole is found |
| E | insert speed 4 mm/s | 2 mm/s |

Confirm stage (21 conditions x 20 trials, seed 2026): D 403/420, median 2.88 s;
F 403/420, median 2.43 s; E 371/420, median 10.8 s.

**E got slower, not better.** The rule ranks on success first. 2 mm/s seated 371
against 370 at 4 mm/s, one trial, at 10.8 s against 6.3 s per cycle. On seed 2027
E's success is unchanged (179 and 38) and its throughput falls (269 to 200, 86 to
78 good units per hour). The rule was committed before the runs and is followed;
a human integrator would keep 4 mm/s.

**D passes more bad parts** (30 to 36 of 80) and stops more on them (1 to 8): a
better search pushes more defective parts to depth, which its depth check accepts.
F's bad-part stops fell from 8 to 0.

## Field identity

- Arm: the stiff-fixture configs of D, E and F are unchanged field by field
  (the gantry classes are their parents, so every inherited field that moved is
  pinned to its old value). A-G on the arm, seed 2026, standard 5-condition set
  (700 trials) and latching suite (980): 0 differences against the arm-baselines
  after-runs at e054ff0 (`arm_identity/`; controller code identical to 0300106).
- Gantry: A, B, C and G identical before and after on both seed-2027 runs (see
  `tables.md`, lost / gained 0 / 0).
- Full test suite passes; two tests in `tests/test_arm_baselines.py` that asserted
  the old gantry defaults (no two-speed moves, hole at the commanded position) now
  assert the new ones.

## Effort

Tuning trials on seed 2026: D 14,000, F 14,000, E 2,700 (about 31,000), with W1's
trial counts. The grid is the v0.2c arm grid (81 coarse settings), not W1's 324;
it includes the values W1's winners took.

## Reproduce

```
results/v0.2c_gantry_baselines/run_set.sh before 6    # at 0300106
results/v0.2c_gantry_baselines/tune_chain.sh 6        # at 0300106
results/v0.2c_gantry_baselines/run_set.sh after 5     # at 0ae06ba
python -m experiments.v02c_gantry_tables > results/v0.2c_gantry_baselines/tables.md
```
