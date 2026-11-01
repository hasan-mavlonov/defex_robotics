Rule applied to `results/v0.2c_integration/prior/validation/gantry` (ranking + safety runs, seed 4002).

| Variant | Role | Successes | Bad units (both runs) | Median / p95 cycle (s) | Eligible |
|---|---|---|---|---|---|
| adaptive | C (reported) | 378/400 | 0 | 7.08 / 15.24 | no |
| g_v1 | reference | 387/400 | 0 | 7.47 / 12.44 | yes |
| g_lp | reported only | 391/400 | 0 | 7.51 / 13.73 | no |
| g_residual_k2_tempered | candidate | 386/400 | 0 | 7.33 / 11.60 | yes |
| g_residual_k2 | candidate | 388/400 | 1 | 7.44 / 12.92 | no |
| g_posterior_k3 | candidate | 392/400 | 0 | 7.51 / 12.26 | yes |

Ranking (successes, then median, then p95): g_posterior_k3 > g_v1 > g_residual_k2_tempered

Decision: install `g_posterior_k3` (ranks above g_v1).
