### arm, seed 4002, ranking families, 100 trials per condition

Sources: `results/v0.2c_integration/prior/validation/arm/ranking`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 500 | 435 (83.8-89.7%) | 0 | 14 | 9.69 / 19.20 | - | 31 / 5 (1.3e-05) |
| g_v1 | 500 | 461 (89.5-94.2%) | 1 | 10 | 9.98 / 18.29 | 5 / 31 (1.3e-05) | - |
| g_lp | 500 | 461 (89.5-94.2%) | 0 | 14 | 9.98 / 18.93 | 8 / 34 (6.9e-05) | 12 / 12 (1) |
| g_residual_k2_tempered | 500 | 455 (88.2-93.2%) | 1 | 16 | 9.80 / 18.23 | 12 / 32 (0.0037) | 19 / 13 (0.38) |
| g_residual_k3 | 500 | 460 (89.3-94.1%) | 0 | 14 | 9.93 / 19.57 | 9 / 34 (0.00017) | 8 / 7 (1) |
| g_posterior_k3 | 500 | 465 (90.4-94.9%) | 1 | 15 | 10.07 / 18.59 | 6 / 36 (2.8e-06) | 10 / 14 (0.54) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_lp | g_residual_k2_tempered | g_residual_k3 | g_posterior_k3 |
|---|---|---|---|---|---|---|
| noise_0.5mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) |
| noise_1mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 99/100 (0, 0) | 100/100 (0, 0) | 99/100 (0, 0) |
| noise_2mm | 69/100 (0, 6) | 79/100 (1, 2) | 80/100 (0, 4) | 78/100 (0, 7) | 82/100 (0, 4) | 81/100 (0, 8) |
| friction_1 | 89/100 (0, 6) | 93/100 (0, 4) | 92/100 (0, 5) | 95/100 (0, 4) | 93/100 (0, 4) | 95/100 (0, 4) |
| mf_noise_1mm | 77/100 (0, 2) | 89/100 (0, 4) | 89/100 (0, 5) | 83/100 (1, 5) | 85/100 (0, 6) | 90/100 (1, 3) |

### arm, seed 4002, safety suite, 30 trials per condition

Sources: `results/v0.2c_integration/prior/validation/arm/safety`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 180 | 60 (26.9-40.5%) | 0 | 0 | 8.32 / 11.88 | - | 0 / 0 (1) |
| g_v1 | 180 | 60 (26.9-40.5%) | 0 | 0 | 8.32 / 11.78 | 0 / 0 (1) | - |
| g_lp | 180 | 60 (26.9-40.5%) | 0 | 0 | 8.32 / 11.78 | 0 / 0 (1) | 0 / 0 (1) |
| g_residual_k2_tempered | 180 | 59 (26.3-39.9%) | 0 | 0 | 8.32 / 11.75 | 1 / 0 (1) | 1 / 0 (1) |
| g_residual_k3 | 180 | 60 (26.9-40.5%) | 0 | 0 | 8.32 / 12.07 | 0 / 0 (1) | 0 / 0 (1) |
| g_posterior_k3 | 180 | 60 (26.9-40.5%) | 0 | 0 | 8.32 / 11.78 | 0 / 0 (1) | 0 / 0 (1) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_lp | g_residual_k2_tempered | g_residual_k3 | g_posterior_k3 |
|---|---|---|---|---|---|---|
| mf_nominal | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_moderate | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 29/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_half_latched | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_broken_latch | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_stubbed_terminal | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_wrong_polarization | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |

