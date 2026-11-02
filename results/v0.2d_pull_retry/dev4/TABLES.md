# v0.2d pull retry: H and I before (no retry) and after (one retry)

Before: `results/v0.2d_force_budget/after` (34520aa). After: `results/v0.2d_pull_retry/dev4`. Seeds 2026 and 2027 pooled, 20 trials per condition and seed.

| Machine, suite | Ctrl | Rows differ | Good seated before -> after | Lost / gained (p) | Bad units on good parts | Bad parts passed | Stops good + bad | Median good cycle (s) | Good units/h (60 s/stop) |
|---|---|---|---|---|---|---|---|---|---|
| gantry, latching | D | 0 | 106 -> 106 of 120 | 0 / 0 (1) | 1 -> 1 | 75 -> 75 of 160 | 2+7 -> 2+7 | 3.12 -> 3.12 | 185 -> 185 |
| gantry, latching | C | 0 | 117 -> 117 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 0+6 -> 0+6 | 6.16 -> 6.16 | 161 -> 161 |
| gantry, latching | H | 76 | 106 -> 106 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 2+7 -> 2+7 | 6.16 -> 6.16 | 150 -> 133 |
| gantry, latching | I | 101 | 118 -> 118 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 0+14 -> 0+14 | 5.48 -> 5.48 | 146 -> 127 |
| gantry, latching | C vs H after | | C-only / H-only | 13 / 2 (0.0074) | | | | | |
| gantry, latching | C vs I after | | C-only / I-only | 2 / 3 (1) | | | | | |
| gantry, latch_spread | D | 0 | 234 -> 234 of 240 | 0 / 0 (1) | 5 -> 5 | 95 -> 95 of 120 | 0+15 -> 0+15 | 3.06 -> 3.06 | 400 -> 400 |
| gantry, latch_spread | C | 0 | 240 -> 240 of 240 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 120 | 0+10 -> 0+10 | 6.15 -> 6.15 | 253 -> 253 |
| gantry, latch_spread | H | 100 | 234 -> 239 of 240 | 0 / 5 (0.062) | 0 -> 0 | 0 -> 0 of 120 | 0+15 -> 0+15 | 6.05 -> 6.06 | 281 -> 248 |
| gantry, latch_spread | I | 107 | 224 -> 240 of 240 | 0 / 16 (3.1e-05) | 0 -> 0 | 0 -> 0 of 120 | 0+24 -> 0+24 | 5.45 -> 5.46 | 247 -> 227 |
| gantry, latch_spread | C vs H after | | C-only / H-only | 1 / 0 (1) | | | | | |
| gantry, latch_spread | C vs I after | | C-only / I-only | 0 / 0 (1) | | | | | |
| arm, latching | D | 0 | 101 -> 101 of 120 | 0 / 0 (1) | 3 -> 3 | 75 -> 75 of 160 | 1+0 -> 1+0 | 4.61 -> 4.61 | 193 -> 193 |
| arm, latching | C | 0 | 110 -> 110 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 3+0 -> 3+0 | 8.98 -> 8.98 | 110 -> 110 |
| arm, latching | H | 77 | 98 -> 98 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 5+0 -> 5+0 | 8.44 -> 8.44 | 132 -> 116 |
| arm, latching | I | 90 | 114 -> 114 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 0+0 -> 0+0 | 8.53 -> 8.53 | 137 -> 120 |
| arm, latching | C vs H after | | C-only / H-only | 12 / 0 (0.00049) | | | | | |
| arm, latching | C vs I after | | C-only / I-only | 3 / 7 (0.34) | | | | | |
| arm, latch_spread | D | 0 | 223 -> 223 of 240 | 0 / 0 (1) | 17 -> 17 | 110 -> 110 of 120 | 0+0 -> 0+0 | 4.53 -> 4.53 | 465 -> 465 |
| arm, latch_spread | C | 0 | 238 -> 238 of 240 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 120 | 0+0 -> 0+0 | 9.02 -> 9.02 | 195 -> 195 |
| arm, latch_spread | H | 126 | 223 -> 238 of 240 | 0 / 15 (6.1e-05) | 1 -> 1 | 0 -> 0 of 120 | 0+0 -> 0+0 | 8.40 -> 8.42 | 280 -> 244 |
| arm, latch_spread | I | 128 | 230 -> 240 of 240 | 0 / 10 (0.002) | 0 -> 0 | 0 -> 0 of 120 | 0+0 -> 0+0 | 8.51 -> 8.51 | 280 -> 237 |
| arm, latch_spread | C vs H after | | C-only / H-only | 2 / 2 (1) | | | | | |
| arm, latch_spread | C vs I after | | C-only / I-only | 0 / 2 (0.5) | | | | | |

## H and I good-part failures after the retry

| Machine | Suite | Ctrl | Condition | Reason | Trials |
|---|---|---|---|---|---|
| arm | latch_spread | H | mf_latch_early | false_accept | 1 |
| arm | latch_spread | H | mf_terminal_min | aborted:retention_failed | 1 |
| arm | latching | H | mf_noise_1mm | aborted:excess_lateral_force | 8 |
| arm | latching | H | mf_noise_1mm | aborted:excess_torque | 3 |
| arm | latching | H | mf_noise_1mm | aborted:jam | 2 |
| arm | latching | H | mf_noise_1mm | aborted:retention_failed | 1 |
| arm | latching | H | mf_noise_1mm | aborted:time_limit | 3 |
| arm | latching | H | mf_noise_1mm | protective_stop | 5 |
| arm | latching | I | mf_noise_1mm | aborted:time_limit | 6 |
| gantry | latch_spread | H | mf_terminal_min | aborted:time_limit | 1 |
| gantry | latching | H | mf_noise_1mm | aborted:jam | 1 |
| gantry | latching | H | mf_noise_1mm | aborted:retention_failed | 1 |
| gantry | latching | H | mf_noise_1mm | aborted:time_limit | 10 |
| gantry | latching | H | mf_noise_1mm | protective_stop | 2 |
| gantry | latching | I | mf_noise_1mm | aborted:time_limit | 2 |
