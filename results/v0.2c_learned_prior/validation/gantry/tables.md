### Gantry, seed 4002, ranking families (100 trials each)

Sources: `results/v0.2c_learned_prior/validation/gantry/ranking_a`, `results/v0.2c_learned_prior/validation/gantry/ranking_b`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 400 | 374 (90.6-95.5%) | 0 | 4 | 7.04 / 15.08 | - | 17 / 9 (0.17) |
| g_v1 | 400 | 382 (93.0-97.1%) | 0 | 5 | 7.38 / 12.03 | 9 / 17 (0.17) | - |
| g_residual_k2_tempered | 400 | 379 (92.1-96.5%) | 0 | 3 | 7.20 / 11.53 | 11 / 16 (0.44) | 10 / 7 (0.63) |
| g_residual_k2 | 400 | 389 (95.1-98.5%) | 0 | 1 | 7.51 / 13.51 | 7 / 22 (0.0081) | 4 / 11 (0.12) |
| g_residual_k3 | 400 | 388 (94.8-98.3%) | 0 | 3 | 7.51 / 13.26 | 6 / 20 (0.0094) | 7 / 13 (0.26) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_residual_k2_tempered | g_residual_k2 | g_residual_k3 |
|---|---|---|---|---|---|
| noise_0.5mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) |
| noise_1mm | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) | 100/100 (0, 0) |
| noise_2mm | 90/100 (0, 0) | 92/100 (0, 0) | 89/100 (0, 0) | 93/100 (0, 0) | 96/100 (0, 0) |
| mf_noise_1mm | 84/100 (0, 4) | 90/100 (0, 5) | 90/100 (0, 3) | 96/100 (0, 1) | 92/100 (0, 3) |

### Gantry, seed 4002, latching safety suite (30 trials each)

Sources: `results/v0.2c_learned_prior/validation/gantry/safety_a`, `results/v0.2c_learned_prior/validation/gantry/safety_b`

| Variant | Trials | Successes (95% CI) | Bad units | Stops | Median / p95 cycle (s) | vs adaptive: ref-only / this-only (p) | vs g_v1: ref-only / this-only (p) |
|---|---|---|---|---|---|---|---|
| adaptive | 180 | 60 (26.9-40.5%) | 0 | 13 | 5.69 / 8.05 | - | 0 / 0 (1) |
| g_v1 | 180 | 60 (26.9-40.5%) | 0 | 17 | 5.69 / 8.20 | 0 / 0 (1) | - |
| g_residual_k2_tempered | 180 | 60 (26.9-40.5%) | 0 | 15 | 5.69 / 8.05 | 0 / 0 (1) | 0 / 0 (1) |
| g_residual_k2 | 180 | 60 (26.9-40.5%) | 0 | 13 | 5.69 / 8.05 | 0 / 0 (1) | 0 / 0 (1) |
| g_residual_k3 | 180 | 60 (26.9-40.5%) | 0 | 13 | 5.69 / 8.05 | 0 / 0 (1) | 0 / 0 (1) |

Per condition, successes (bad units, stops):

| Condition | adaptive | g_v1 | g_residual_k2_tempered | g_residual_k2 | g_residual_k3 |
|---|---|---|---|---|---|
| mf_nominal | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_moderate | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) | 30/30 (0, 0) |
| mf_half_latched | 0/30 (0, 13) | 0/30 (0, 10) | 0/30 (0, 11) | 0/30 (0, 12) | 0/30 (0, 11) |
| mf_broken_latch | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_stubbed_terminal | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) | 0/30 (0, 0) |
| mf_wrong_polarization | 0/30 (0, 0) | 0/30 (0, 7) | 0/30 (0, 4) | 0/30 (0, 1) | 0/30 (0, 2) |

