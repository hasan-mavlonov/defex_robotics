# Paired comparisons for benchmark_v0.2d

| Run | C vs | Trials | Successes C / other | C-only / other-only | p | Escapes C / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | I | 500 | 395 / 397 | 50 / 52 | 0.92 | 0 / 31 | 9.3e-10 |
| arm_heldout, good parts | H | 500 | 395 / 342 | 73 / 20 | 2.9e-08 | 0 / 18 | 7.6e-06 |
| arm_latch_spread, good parts | I | 600 | 599 / 597 | 2 / 0 | 0.5 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 499 / 497 | 2 / 0 | 0.5 | 0 / 0 | 1 |
| arm_latch_spread, good parts | H | 600 | 599 / 598 | 1 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | H | 500 | 499 / 498 | 1 / 0 | 1 | 0 / 0 | 1 |
| arm_latching, good parts | I | 600 | 566 / 560 | 23 / 17 | 0.43 | 0 / 0 | 1 |
| arm_latching, good parts | H | 600 | 566 / 486 | 90 / 10 | 3.1e-17 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1956 / 1922 | 51 / 17 | 4.5e-05 | 0 / 43 | 2.3e-13 |
| arm_standard, good parts | H | 2000 | 1956 / 1889 | 78 / 11 | 1.4e-13 | 0 / 35 | 5.8e-11 |
| gantry_heldout, good parts | I | 500 | 438 / 417 | 60 / 39 | 0.044 | 0 / 39 | 3.6e-12 |
| gantry_heldout, good parts | H | 500 | 438 / 360 | 97 / 19 | 8.6e-14 | 0 / 28 | 7.5e-09 |
| gantry_latch_spread, good parts | I | 600 | 600 / 599 | 1 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 499 | 1 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | H | 600 | 600 / 597 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | H | 500 | 500 / 498 | 2 / 0 | 0.5 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 579 / 588 | 7 / 16 | 0.093 | 0 / 0 | 1 |
| gantry_latching, good parts | H | 600 | 579 / 537 | 51 / 9 | 3.1e-08 | 0 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1984 / 1926 | 60 / 2 | 8.5e-16 | 0 / 48 | 7.1e-15 |
| gantry_standard, good parts | H | 2000 | 1984 / 1921 | 66 / 3 | 1.9e-16 | 0 / 37 | 1.5e-11 |

## J against C and against I

| Run | J vs | Trials | Successes J / other | J-only / other-only | p | Escapes J / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | C | 500 | 389 / 395 | 37 / 43 | 0.58 | 0 / 0 | 1 |
| arm_heldout, good parts | I | 500 | 389 / 397 | 17 / 25 | 0.28 | 0 / 31 | 9.3e-10 |
| arm_latch_spread, good parts | C | 600 | 597 / 599 | 0 / 2 | 0.5 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | C | 500 | 497 / 499 | 0 / 2 | 0.5 | 0 / 0 | 1 |
| arm_latch_spread, good parts | I | 600 | 597 / 597 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 497 / 497 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_latching, good parts | C | 600 | 560 / 566 | 17 / 23 | 0.43 | 0 / 0 | 1 |
| arm_latching, good parts | I | 600 | 560 / 560 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_standard, good parts | C | 2000 | 1939 / 1956 | 19 / 36 | 0.03 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1939 / 1922 | 28 / 11 | 0.0095 | 0 / 43 | 2.3e-13 |
| gantry_heldout, good parts | C | 500 | 447 / 438 | 46 / 37 | 0.38 | 2 / 0 | 0.5 |
| gantry_heldout, good parts | I | 500 | 447 / 417 | 39 / 9 | 1.5e-05 | 2 / 39 | 7.8e-10 |
| gantry_latch_spread, good parts | C | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | C | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | I | 600 | 600 / 599 | 1 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 499 | 1 / 0 | 1 | 0 / 0 | 1 |
| gantry_latching, good parts | C | 600 | 588 / 579 | 16 / 7 | 0.093 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 588 / 588 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_standard, good parts | C | 2000 | 1961 / 1984 | 6 / 29 | 0.00012 | 1 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1961 / 1926 | 48 / 13 | 7.7e-06 | 1 / 48 | 1.8e-13 |

## Bad units passed on good-part trials, per machine

| Machine | C | G | D | F | H | I | J |
|---|---|---|---|---|---|---|---|
| gantry | 0 | 0 | 83 | 92 | 65 | 87 | 3 |
| arm | 0 | 0 | 78 | 105 | 53 | 74 | 0 |

## I's escapes on good-part trials

| Run | Escapes | Depth min-max (mm) | Tilt max (deg) | Lateral max (mm) | Reasons | Conditions |
|---|---|---|---|---|---|---|
| arm_heldout | 31 | 12.20-14.99 | 4.53 | 0.65 | {'false_accept': 31} | {'heldout_mischar_2mm': 26, 'heldout_mischar_1mm': 5} |
| arm_standard | 43 | 11.67-14.99 | 4.80 | 0.73 | {'false_accept': 43} | {'noise_2mm': 31, 'noise_1mm': 6, 'generalization_combined': 6} |
| gantry_heldout | 39 | 13.90-15.01 | 4.49 | 0.73 | {'false_accept': 39} | {'heldout_mischar_2mm': 30, 'heldout_mischar_1mm': 6, 'heldout_worst_case': 3} |
| gantry_standard | 48 | 14.45-15.01 | 4.97 | 0.73 | {'false_accept': 48} | {'noise_2mm': 35, 'noise_1mm': 7, 'generalization_combined': 6} |
