### gantry, seed 4002, ranking families, 100 trials per condition

Sources: `results/v0.2c_integration/prior/validation/gantry/ranking`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 400 | 378 (91.8-96.3%) | 0 | 0 | 7.08 / 15.24 | - | 15 / 6 (0.078) |
| g_v1 | 400 | 387 (94.5-98.1%) | 0 | 0 | 7.47 / 12.44 | 6 / 15 (0.078) | - |
| g_lp | 400 | 391 (95.8-98.8%) | 0 | 0 | 7.51 / 13.73 | 6 / 19 (0.015) | 3 / 7 (0.34) |
| g_residual_k2_tempered | 400 | 386 (94.2-97.9%) | 0 | 0 | 7.33 / 11.60 | 11 / 19 (0.2) | 8 / 7 (1) |
| g_residual_k2 | 400 | 388 (94.8-98.3%) | 1 | 0 | 7.44 / 12.92 | 7 / 17 (0.064) | 4 / 5 (1) |
| g_posterior_k3 | 400 | 392 (96.1-99.0%) | 0 | 0 | 7.51 / 12.26 | 5 / 19 (0.0066) | 1 / 6 (0.12) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_lp | g_residual_k2_tempered | g_residual_k2 | g_posterior_k3 |
|---|---|---|---|---|---|---|
| noise_0.5mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) |
| noise_1mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) |
| noise_2mm | 90/100 (0, 0) | 92/100 (0, 0) | 93/100 (0, 0) | 92/100 (0, 0) | 91/100 (1, 0) | 95/100 (0, 0) |
| mf_noise_1mm | 88/100 (0, 0) | 95/100 (0, 0) | 98/100 (0, 0) | 94/100 (0, 0) | 97/100 (0, 0) | 97/100 (0, 0) |

### gantry, seed 4002, safety suite, 30 trials per condition

Sources: `results/v0.2c_integration/prior/validation/gantry/safety`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 180 | 60 (26.9-40.5%) | 0 | 6 | 5.69 / 8.05 | - | 0 / 0 (1) |
| g_v1 | 180 | 60 (26.9-40.5%) | 0 | 5 | 5.69 / 8.20 | 0 / 0 (1) | - |
| g_lp | 180 | 60 (26.9-40.5%) | 0 | 5 | 5.69 / 8.05 | 0 / 0 (1) | 0 / 0 (1) |
| g_residual_k2_tempered | 180 | 60 (26.9-40.5%) | 0 | 6 | 5.69 / 8.06 | 0 / 0 (1) | 0 / 0 (1) |
| g_residual_k2 | 180 | 60 (26.9-40.5%) | 0 | 6 | 5.69 / 8.05 | 0 / 0 (1) | 0 / 0 (1) |
| g_posterior_k3 | 180 | 60 (26.9-40.5%) | 0 | 6 | 5.69 / 8.05 | 0 / 0 (1) | 0 / 0 (1) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_lp | g_residual_k2_tempered | g_residual_k2 | g_posterior_k3 |
|---|---|---|---|---|---|---|
| mf_nominal | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_moderate | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_half_latched | 0/30 (0, 6) | 0/30 (0, 5) | 0/30 (0, 5) | 0/30 (0, 6) | 0/30 (0, 6) | 0/30 (0, 6) |
| mf_broken_latch | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_stubbed_terminal | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_wrong_polarization | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |

