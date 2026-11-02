# Replay plan (written before the replay ran)

POST HOC: the replay and the rescoring were decided after the benchmark results were seen.

Code: 9197b9c (v0.2f/pack), which only adds five logged columns to trials.csv:
`final_x_mm`, `final_y_mm` (socket frame), `final_tcp_speed_mm_s`, `final_latched`,
`final_latch_intact`. Seed 20261130 (benchmark_v0.2e). Controllers: adaptive (C),
spiral_rcc (F), spiral_rcc_pull (I), spiral_rcc_verify (J). `--workers 2`. All 100 trials
of each condition replayed (200 on latching).

## Why not every condition

A full replay of standard and heldout for the four controllers is about 91 minutes at 2
workers (sum of the committed `wall_time_s` / 2; a 16-trial smoke run matched the
committed wall time within 6%). The cap is about 60 minutes. So only the conditions whose
rows the logs cannot rescore are replayed. The argument, from `evaluate_final_state`:

    seated(tol) = depth(tol) AND angles(tol) AND R,   R = lateral per axis AND settled AND latched

R does not depend on the depth or angle tolerance and is not in the old logs. If a row was
seated as run, R is true, so seated(tol) = depth(tol) AND angles(tol), known. If it was not
seated but passed depth and angles as run, R is false, so it stays unseated, known. Only
rows not seated as run, failing depth or angles as run, and passing both at the loosest
tolerance (5 deg, 1.0 mm), with a radius under sqrt 2 x the lateral limit, are unknown.
Those rows (C, F, I, J) sit in these conditions only:

| Run | Conditions | Estimated minutes at 2 workers |
|---|---|---|
| gantry standard | noise_1mm, noise_2mm, generalization_combined | 6 |
| gantry heldout | heldout_mischar_1mm, heldout_mischar_2mm, heldout_worst_case | 7 |
| arm standard | noise_1mm, noise_2mm, generalization_combined | 11 |
| arm heldout | heldout_mischar_1mm, heldout_mischar_2mm | 8 |
| gantry latching | mf_noise_1mm | 7 |
| arm latching | mf_noise_1mm | 13 |
| total | | about 52 |

Latching runs go last and are dropped if the total runs past about 60 minutes. The bad-part
condition mf_half_latched also has unknown rows (at the looser depth tolerance) but is not
replayed: bad parts are not rescored.

## Checks and rescoring, fixed now

1. Every existing column of every replayed row must equal the committed benchmark_v0.2e row
   (string-equal), `wall_time_s` excepted.
2. gt_seated recomputed from the new columns at the as-run tolerances must equal the logged
   gt_seated on every replayed row.
3. Rescoring grid: yaw and tilt tolerance 2, 2.5, 3, 3.5, 4, 5 deg (the same value for both),
   crossed with depth tolerance 0.5 mm (as run) and 1.0 mm. Lateral margin and settled speed
   as run. Replayed conditions use the replayed rows; all other rows are rescored by the rule
   above, which needs no unlogged value. Success = rescored seated AND the logged outcome
   flags (no stop, penetration, damage, joint limit or timeout, and not declared failure).
4. Reported per machine, for standard, heldout and latching good parts: C, F, I, J seated;
   C-only / I-only and C-only / F-only (McNemar, descriptive); bad units of C, F, I, J.
