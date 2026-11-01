### gantry, dev seed 2026, 60 trials per condition

Sources: `results/v0.2c_integration/prior/dev2026/gantry`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 600 | 350 (54.3-62.2%) | 0 | 13 | 5.94 / 13.05 | - | 8 / 3 (0.23) |
| g_v1 | 600 | 355 (55.2-63.0%) | 0 | 12 | 5.97 / 11.36 | 3 / 8 (0.23) | - |
| g_installed | 600 | 357 (55.5-63.4%) | 0 | 12 | 5.98 / 11.77 | 2 / 9 (0.065) | 1 / 3 (0.62) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_installed |
|---|---|---|---|
| noise_0.5mm | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| noise_1mm | 59/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| noise_2mm | 57/60 (0, 0) | 57/60 (0, 0) | 57/60 (0, 0) |
| mf_nominal | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| mf_moderate | 60/60 (0, 0) | 60/60 (0, 0) | 60/60 (0, 0) |
| mf_noise_1mm | 54/60 (0, 0) | 58/60 (0, 0) | 60/60 (0, 0) |
| mf_half_latched | 0/60 (0, 13) | 0/60 (0, 12) | 0/60 (0, 12) |
| mf_broken_latch | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_stubbed_terminal | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |
| mf_wrong_polarization | 0/60 (0, 0) | 0/60 (0, 0) | 0/60 (0, 0) |

