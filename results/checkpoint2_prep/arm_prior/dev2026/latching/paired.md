### adaptive_learned vs adaptive (paired)

| Condition | Pairs | Differ | Success C / G | C-only / G-only (McNemar p) | Bad units C / G | Stops C / G | Mean retries C / G (diff, 95% CI) | Median cycle C / G (s) | p95 cycle C / G (s) | Cycle diff, both succeeded (s, 95% CI) |
|---|---|---|---|---|---|---|---|---|---|---|
| mf_nominal | 60 | 1 | 60 / 60 | 0 / 0 (1) | 0 / 0 | 0 / 0 | 0.18 / 0.18 (+0.00, +0.00 to +0.00) | 8.29 / 8.29 | 11.86 / 11.86 | +0.00 (+0.00 to +0.00) |
| mf_moderate | 60 | 3 | 60 / 60 | 0 / 0 (1) | 0 / 0 | 0 / 0 | 0.25 / 0.22 (-0.03, -0.10 to +0.00) | 8.30 / 8.30 | 11.89 / 11.80 | -0.11 (-0.35 to +0.01) |
| mf_noise_1mm | 60 | 35 | 39 / 45 | 0 / 6 (0.031) | 0 / 0 | 4 / 4 | 2.88 / 2.05 (-0.83, -1.28 to -0.42) | 12.39 / 12.30 | 23.93 / 19.84 | -1.72 (-2.82 to -0.79) |
| mf_half_latched | 60 | 5 | 0 / 0 | 0 / 0 (1) | 0 / 0 | 0 / 0 | 4.15 / 4.15 (+0.00, +0.00 to +0.00) | n/a / n/a | n/a / n/a | n/a (n/a to n/a) |
| mf_broken_latch | 60 | 6 | 0 / 0 | 0 / 0 (1) | 0 / 0 | 0 / 0 | 4.05 / 4.07 (+0.02, +0.00 to +0.05) | n/a / n/a | n/a / n/a | n/a (n/a to n/a) |
| mf_stubbed_terminal | 60 | 4 | 0 / 0 | 0 / 0 (1) | 0 / 0 | 0 / 0 | 5.25 / 5.25 (+0.00, +0.00 to +0.00) | n/a / n/a | n/a / n/a | n/a (n/a to n/a) |
| mf_wrong_polarization | 60 | 60 | 0 / 0 | 0 / 0 (1) | 0 / 0 | 0 / 3 | 6.73 / 6.55 (-0.18, -0.38 to +0.02) | n/a / n/a | n/a / n/a | n/a (n/a to n/a) |
| all | 420 | 114 | 159 / 165 | 0 / 6 (0.031) | 0 / 0 | 4 / 7 | 3.36 / 3.21 (-0.15, -0.22 to -0.08) | 8.35 / 8.35 | 16.83 / 15.22 | -0.47 (-0.78 to -0.21) |
