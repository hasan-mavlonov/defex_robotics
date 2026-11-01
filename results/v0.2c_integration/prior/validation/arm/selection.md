Rule applied to `results/v0.2c_integration/prior/validation/arm` (ranking + safety runs, seed 4002).

| Variant | Role | Successes | Bad units (both runs) | Median / p95 cycle (s) | Eligible |
|---|---|---|---|---|---|
| adaptive | C (reported) | 435/500 | 0 | 9.69 / 19.20 | no |
| g_v1 | reference | 461/500 | 1 | 9.98 / 18.29 | yes |
| g_lp | reported only | 461/500 | 0 | 9.98 / 18.93 | no |
| g_residual_k2_tempered | candidate | 455/500 | 1 | 9.80 / 18.23 | no |
| g_residual_k3 | candidate | 460/500 | 0 | 9.93 / 19.57 | yes |
| g_posterior_k3 | candidate | 465/500 | 1 | 10.07 / 18.59 | no |

Ranking (successes, then median, then p95): g_v1 > g_residual_k3

Decision: no candidate ranks above g_v1; install the v1 model.
