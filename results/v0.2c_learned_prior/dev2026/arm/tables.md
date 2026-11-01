### arm, dev seed 2026, 60 trials per condition

Sources: `results/v0.2c_learned_prior/dev2026/arm`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 660 | 357 (50.3-57.9%) | 0 | 12 | 8.72 / 18.14 | - | 19 / 1 (4e-05) |
| g_v1 | 660 | 375 (53.0-60.5%) | 0 | 16 | 8.81 / 17.04 | 1 / 19 (4e-05) | - |
| g_residual_k3 | 660 | 372 (52.6-60.1%) | 0 | 19 | 8.80 / 17.19 | 4 / 19 (0.0026) | 7 / 4 (0.55) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_residual_k3 |
|---|---|---|---|
| noise_0.5mm | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| noise_1mm | 52/60 (0, 0) | 54/60 (0, 1) | 53/60 (0, 1) |
| noise_2mm | 32/60 (0, 5) | 41/60 (0, 5) | 41/60 (0, 5) |
| friction_1 | 54/60 (0, 3) | 55/60 (0, 3) | 53/60 (0, 3) |
| mf_nominal | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| mf_moderate | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| mf_noise_1mm | 39/60 (0, 4) | 45/60 (0, 4) | 45/60 (0, 5) |
| mf_half_latched | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_broken_latch | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_stubbed_terminal | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_wrong_polarization | 0/60 (0, 0) | 0/60 (0, 3) | 0/60 (0, 5) |

