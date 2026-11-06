# Replay plan, seeds 20261123 and 20261124 (written before the replay ran)

POST HOC: the replay and the rescoring were decided after the benchmark results were seen.
This repeats `results/v0.2f_evidence/replay_20261130/RUN_PLAN.md` (branch v0.2f/pack) on
the two benchmark seeds that ran the v0.2d code.

Code: branch v0.2f/replay-v02d = 42df5c8 (the v0.2d benchmark code) plus 22ef683, a
cherry-pick of 9197b9c that only adds five logged columns (`final_x_mm`, `final_y_mm`,
`final_tcp_speed_mm_s`, `final_latched`, `final_latch_intact`). Its defex/ changes are
byte-identical to 9197b9c. Seeds 20261123 (benchmark_v0.2d) and 20261124
(benchmark_v0.2d_rep). Controllers adaptive (C), spiral_rcc (F), spiral_rcc_pull (I),
spiral_rcc_verify (J). Workers: 8 if `uptime` load is under 4 at start, else fewer.

Conditions: the same rule as for seed 20261130. Replay every good-part condition holding a
row of C, F, I or J that the old columns cannot rescore (not seated as run, failing depth or
angle as run, passing both at 5 deg and 1.0 mm, radius under sqrt 2 x the lateral limit):

| Run | 20261123 | 20261124 |
|---|---|---|
| gantry standard | noise_1mm, noise_2mm, generalization_combined | same |
| gantry heldout | heldout_mischar_1mm, heldout_mischar_2mm, heldout_worst_case | same |
| arm standard | noise_1mm, noise_2mm, generalization_combined | same |
| arm heldout | heldout_mischar_1mm, heldout_mischar_2mm | same |
| gantry latching | mf_noise_1mm | same |
| arm latching | mf_noise_1mm, **mf_nominal** (one undecided row on this seed) | mf_noise_1mm |

Arm latching mf_nominal on seed 20261123 is the only addition to the seed-20261130 list;
without it the rescoring would not be exact.

Estimate: about 17 min (20261123) + 15 min (20261124) at 8 workers, from the committed
`wall_time_s` / 8.

Checks and rescoring as in the seed-20261130 plan: every committed column but
`wall_time_s` identical to `results/benchmark_v0.2d/*/trials.csv` or
`results/benchmark_v0.2d_rep/*/trials.csv`; gt_seated recomputed exactly; yaw/tilt 2, 2.5,
3, 3.5, 4, 5 deg x depth 0.5, 1.0 mm; per-seed McNemar only, never pooled.
