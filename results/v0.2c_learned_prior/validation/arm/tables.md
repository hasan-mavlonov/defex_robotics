### Arm (UR5e), seed 4002, ranking families (100 trials each)

Sources: `results/v0.2c_learned_prior/validation/arm/ranking_a`, `results/v0.2c_learned_prior/validation/arm/ranking_b`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 500 | 391 (74.4-81.6%) | 0 | 18 | 9.30 / 19.79 | - | 28 / 6 (0.0002) |
| g_v1 | 500 | 413 (79.0-85.7%) | 0 | 23 | 9.54 / 19.73 | 6 / 28 (0.0002) | - |
| g_residual_k2_tempered | 500 | 415 (79.5-86.0%) | 0 | 22 | 9.55 / 21.15 | 8 / 32 (0.00018) | 12 / 14 (0.85) |
| g_posterior_k3 | 500 | 425 (81.6-87.9%) | 1 | 19 | 9.73 / 19.69 | 3 / 37 (1.9e-08) | 5 / 17 (0.017) |
| g_residual_k3 | 500 | 417 (79.9-86.4%) | 0 | 24 | 9.55 / 20.21 | 6 / 32 (2.4e-05) | 13 / 17 (0.58) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_residual_k2_tempered | g_posterior_k3 | g_residual_k3 |
|---|---|---|---|---|---|
| noise_0.5mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) |
| noise_1mm | 96/100 (0, 0) | 97/100 (0, 0) | 97/100 (0, 0) | 97/100 (0, 0) | 97/100 (0, 0) |
| noise_2mm | 45/100 (0, 6) | 56/100 (0, 5) | 56/100 (0, 5) | 58/100 (1, 6) | 59/100 (0, 7) |
| friction_1 | 87/100 (0, 7) | 90/100 (0, 7) | 92/100 (0, 6) | 92/100 (0, 6) | 89/100 (0, 6) |
| mf_noise_1mm | 63/100 (0, 5) | 70/100 (0, 11) | 70/100 (0, 11) | 78/100 (0, 7) | 72/100 (0, 11) |

### Arm (UR5e), seed 4002, latching safety suite (30 trials each)

Sources: `results/v0.2c_learned_prior/validation/arm/safety_a`, `results/v0.2c_learned_prior/validation/arm/safety_b`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 180 | 59 (26.3-39.9%) | 0 | 0 | 8.31 / 11.88 | - | 0 / 0 (1) |
| g_v1 | 180 | 59 (26.3-39.9%) | 0 | 0 | 8.31 / 11.78 | 0 / 0 (1) | - |
| g_residual_k2_tempered | 180 | 59 (26.3-39.9%) | 0 | 1 | 8.31 / 11.88 | 0 / 0 (1) | 0 / 0 (1) |
| g_posterior_k3 | 180 | 59 (26.3-39.9%) | 0 | 1 | 8.31 / 11.78 | 0 / 0 (1) | 0 / 0 (1) |
| g_residual_k3 | 180 | 59 (26.3-39.9%) | 0 | 4 | 8.31 / 11.78 | 0 / 0 (1) | 0 / 0 (1) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_residual_k2_tempered | g_posterior_k3 | g_residual_k3 |
|---|---|---|---|---|---|
| mf_nominal | 29/30 (0, 0) | 29/30 (0, 0) | 29/30 (0, 0) | 29/30 (0, 0) | 29/30 (0, 0) |
| mf_moderate | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_half_latched | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_broken_latch | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_stubbed_terminal | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_wrong_polarization | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 1) | 0/30 (0, 1) | 0/30 (0, 4) |

