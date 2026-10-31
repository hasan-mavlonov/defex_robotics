# Replication of benchmark_v0.2a on a second seed (development check)

Not pre-registered and not a reported benchmark: an evaluation run made after
benchmark_v0.2a to see whether its result depends on the seed. Same code as the
reported run (commit `5865e58` differs from the frozen `56707fa` only in the CI
workflow file and results), seed 20261107, 12,000 paired trials.

| Controller | benchmark_v0.2a (seed 20261031) | This run (seed 20261107) |
|---|---|---|
| C | 99.75%, 0 bad units passed | 99.30% (98.8-99.6), 1 bad unit passed |
| F | 96.15%, 57 bad units passed | 96.65% (95.8-97.4), 45 bad units passed |
| C vs F, discordant pairs | 73 / 1 | 59 / 6 (exact McNemar p = 5e-12) |

The ranking and the size of the gap replicate. C's "no bad units passed" does
not: in `friction_1` trial 31, C's own yaw search (-3 deg after five blocked
attempts) let the plug seat at full depth with 3.36 deg of yaw, over the 3 deg
tolerance. Yaw centering was skipped because it only runs when the vision yaw
sigma exceeds 1 deg (0.5 deg here), and the wall-probe VERIFY cannot see yaw. It
passed with 0.70 mm of total travel. Fix planned for W3/W4: run yaw centering
whenever the yaw search changed the yaw, and check yaw in VERIFY.
