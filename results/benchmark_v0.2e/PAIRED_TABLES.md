# Paired comparisons for benchmark_v0.2e

| Run | C vs | Trials | Successes C / other | C-only / other-only | p | Escapes C / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | I | 500 | 384 / 392 | 52 / 60 | 0.51 | 0 / 34 | 1.2e-10 |
| arm_heldout, good parts | H | 500 | 384 / 345 | 66 / 27 | 6.5e-05 | 0 / 16 | 3.1e-05 |
| arm_latch_spread, good parts | I | 600 | 597 / 599 | 0 / 2 | 0.5 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 498 / 499 | 0 / 1 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts | H | 600 | 597 / 598 | 1 / 2 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | H | 500 | 498 / 498 | 1 / 1 | 1 | 0 / 0 | 1 |
| arm_latching, good parts | I | 600 | 552 / 570 | 19 / 37 | 0.022 | 0 / 3 | 0.25 |
| arm_latching, good parts | H | 600 | 552 / 474 | 84 / 6 | 1.1e-18 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1962 / 1924 | 54 / 16 | 5.9e-06 | 0 / 32 | 4.7e-10 |
| arm_standard, good parts | H | 2000 | 1962 / 1886 | 92 / 16 | 3.8e-14 | 0 / 27 | 1.5e-08 |
| gantry_heldout, good parts | I | 500 | 407 / 419 | 48 / 60 | 0.29 | 0 / 37 | 1.5e-11 |
| gantry_heldout, good parts | H | 500 | 407 / 364 | 73 / 30 | 2.7e-05 | 0 / 28 | 7.5e-09 |
| gantry_latch_spread, good parts | I | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | H | 600 | 600 / 596 | 4 / 0 | 0.12 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | H | 500 | 500 / 497 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 585 / 592 | 7 / 14 | 0.19 | 0 / 0 | 1 |
| gantry_latching, good parts | H | 600 | 585 / 520 | 71 / 6 | 3.4e-15 | 0 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1981 / 1936 | 53 / 8 | 3e-09 | 0 / 32 | 4.7e-10 |
| gantry_standard, good parts | H | 2000 | 1981 / 1928 | 59 / 6 | 5e-12 | 0 / 30 | 1.9e-09 |

## J against C and against I

| Run | J vs | Trials | Successes J / other | J-only / other-only | p | Escapes J / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | C | 500 | 379 / 384 | 40 / 45 | 0.66 | 0 / 0 | 1 |
| arm_heldout, good parts | I | 500 | 379 / 392 | 20 / 33 | 0.098 | 0 / 34 | 1.2e-10 |
| arm_latch_spread, good parts | C | 600 | 600 / 597 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | C | 500 | 500 / 498 | 2 / 0 | 0.5 | 0 / 0 | 1 |
| arm_latch_spread, good parts | I | 600 | 600 / 599 | 1 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 499 | 1 / 0 | 1 | 0 / 0 | 1 |
| arm_latching, good parts | C | 600 | 572 / 552 | 38 / 18 | 0.01 | 1 / 0 | 1 |
| arm_latching, good parts | I | 600 | 572 / 570 | 2 / 0 | 0.5 | 1 / 3 | 0.5 |
| arm_standard, good parts | C | 2000 | 1935 / 1962 | 16 / 43 | 0.00058 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1935 / 1924 | 21 / 10 | 0.071 | 0 / 32 | 4.7e-10 |
| gantry_heldout, good parts | C | 500 | 444 / 407 | 71 / 34 | 0.00039 | 1 / 0 | 1 |
| gantry_heldout, good parts | I | 500 | 444 / 419 | 34 / 9 | 0.00017 | 1 / 37 | 2.9e-11 |
| gantry_latch_spread, good parts | C | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | C | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | I | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latching, good parts | C | 600 | 592 / 585 | 14 / 7 | 0.19 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 592 / 592 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_standard, good parts | C | 2000 | 1959 / 1981 | 10 / 32 | 0.00094 | 0 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1959 / 1936 | 32 / 9 | 0.00043 | 0 / 32 | 4.7e-10 |

## Bad units passed on good-part trials, per machine

| Machine | C | G | D | F | H | I | J |
|---|---|---|---|---|---|---|---|
| gantry | 0 | 0 | 71 | 75 | 58 | 69 | 1 |
| arm | 0 | 1 | 65 | 103 | 43 | 69 | 1 |

## I's escapes on good-part trials

| Run | Escapes | Depth min-max (mm) | Tilt max (deg) | Lateral max (mm) | Reasons | Conditions |
|---|---|---|---|---|---|---|
| arm_heldout | 34 | 12.69-15.01 | 5.18 | 0.70 | {'false_accept': 34} | {'heldout_mischar_2mm': 26, 'heldout_mischar_1mm': 6, 'heldout_worst_case': 2} |
| arm_latching | 3 | 7.79-7.85 | 3.22 | 0.25 | {'false_accept': 3} | {'mf_noise_1mm': 3} |
| arm_standard | 32 | 10.43-14.96 | 6.52 | 0.63 | {'false_accept': 32} | {'noise_2mm': 17, 'noise_1mm': 11, 'generalization_combined': 4} |
| gantry_heldout | 37 | 14.38-15.01 | 5.20 | 0.67 | {'false_accept': 37} | {'heldout_mischar_2mm': 31, 'heldout_mischar_1mm': 5, 'heldout_worst_case': 1} |
| gantry_standard | 32 | 14.38-14.98 | 5.53 | 0.68 | {'false_accept': 32} | {'noise_2mm': 19, 'noise_1mm': 10, 'generalization_combined': 3} |
