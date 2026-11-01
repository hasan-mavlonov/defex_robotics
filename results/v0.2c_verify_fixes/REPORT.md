# v0.2c: wall-yaw check fails a clamped plug (development)

Development measurement on dev seeds 2026 and 2027, controller C on the UR5e.
Not a reported benchmark.

## Why

The benchmark_v0.2b audit (`results/benchmark_v0.2b/AUDIT_TABLES.md`) found that
5 of C's 6 escapes (and 7 of G's 9) came from one path. On the arm, VERIFY checks
yaw from the free travel between two wall contacts. In the 0.2 mm cavity a plug
yawed by the 2 degree tolerance does not fit, so the required half travel was
negative (-0.007 mm), and a plug wedged 0.5-1.5 mm short of full depth, with zero
free travel, passed. This fix was motivated by the reported seed, so its effect
has to be measured on a seed that has not been run (the v0.2c test).

## Change

`AdaptiveConfig.wall_yaw_min_free_fraction = 0.1`: the check also needs a half
free travel of at least 10% of an aligned plug's (0.02 mm in the 0.2 mm cavity,
0.05 mm in the standard one, where the yaw bound of 0.293 mm already dominates).
A plug the walls clamp is treated as wedged: the check fails and C recovers.
Commit e84bbbf on `v0.2c/verify-fixes`.

## Evidence used to set it (before the change)

`python experiments/wall_yaw_travel.py results/v0.2c_verify_fixes/before_*`:
every wall-yaw pass that ended in an escape had a half free travel of at most
0.001 mm (10 of 10); passes of good plugs in `generalization_tight` had at least
0.032 mm (192 of 192). In `heldout_worst_case` some good plugs also read near zero.

## Result (C, 100 trials per cell)

| Seed, condition | Successes before / after | Escapes before / after |
|---|---|---|
| 2026, heldout_worst_case | 22 / 22 | 6 / 0 |
| 2027, heldout_worst_case | 30 / 27 | 3 / 0 |
| 2026, generalization_tight | 96 / 96 | 1 / 0 |
| 2027, generalization_tight | 96 / 96 | 0 / 0 |
| 2026 and 2027, noise_2mm | 53, 41 / 53, 41 | 0 / 0 |

10 escapes removed. Seed 2027's worst case loses 3 successes: the plugs were within
tolerance but clamped by the walls, and C now rejects them. No false rejects
(a plug seated in ground truth and declared failed) in any cell. Of the three
lost units, two ran out of time after the recovery and one ended in a protective
stop during it (a cell reset).

Gantry: the wall-yaw check is arm-only. C and G on seed 2026,
generalization_tight / noise_2mm / friction_1 x 20 trials: 120 trials, 0 field
differences against the code before the change (`equiv_before`, `equiv_after`).

## Not fixed

The second escape mode in the audit, plugs fully inserted at 3.0-3.6 degrees of
tilt that pass the wall probes (1 for C, 2 for G in 12,400 good-part trials), is
not addressed. In those trials the seat conform turned the plug 1.3-1.8 degrees
and one wall was touched almost at once (0.04 mm of travel); the cause is not
yet diagnosed.
