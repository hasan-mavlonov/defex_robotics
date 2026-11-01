### gantry, dev seed 2026, 60 trials per condition

Sources: `results/v0.2c_learned_prior/dev2026/gantry`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 600 | 349 (54.2-62.0%) | 0 | 21 | 5.94 / 13.06 | - | 9 / 3 (0.15) |
| g_v1 | 600 | 355 (55.2-63.0%) | 0 | 35 | 5.97 / 11.36 | 3 / 9 (0.15) | - |
| g_residual_k2 | 600 | 355 (55.2-63.0%) | 0 | 26 | 5.97 / 10.71 | 2 / 8 (0.11) | 3 / 3 (1) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_residual_k2 |
|---|---|---|---|
| noise_0.5mm | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| noise_1mm | 59/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| noise_2mm | 57/60 (0, 0) | 57/60 (0, 0) | 57/60 (0, 0) |
| mf_nominal | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| mf_moderate | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| mf_noise_1mm | 53/60 (0, 1) | 58/60 (0, 0) | 58/60 (0, 1) |
| mf_half_latched | 0/60 (0, 19) | 0/60 (0, 18) | 0/60 (0, 18) |
| mf_broken_latch | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_stubbed_terminal | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_wrong_polarization | 0/60 (0, 1) | 0/60 (0, 17) | 0/60 (0, 7) |

