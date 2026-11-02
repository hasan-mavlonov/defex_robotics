# Paired comparisons for benchmark_v0.2d_rep

| Run | C vs | Trials | Successes C / other | C-only / other-only | p | Escapes C / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | I | 500 | 395 / 410 | 43 / 58 | 0.16 | 0 / 28 | 7.5e-09 |
| arm_heldout, good parts | H | 500 | 395 / 352 | 64 / 21 | 3.3e-06 | 0 / 19 | 3.8e-06 |
| arm_latch_spread, good parts | I | 600 | 599 / 600 | 0 / 1 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts | H | 600 | 599 / 596 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | H | 500 | 500 / 497 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| arm_latching, good parts | I | 600 | 562 / 562 | 20 / 20 | 1 | 0 / 1 | 1 |
| arm_latching, good parts | H | 600 | 562 / 481 | 88 / 7 | 6e-19 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1963 / 1923 | 51 / 11 | 2.8e-07 | 0 / 39 | 3.6e-12 |
| arm_standard, good parts | H | 2000 | 1963 / 1889 | 81 / 7 | 4.5e-17 | 0 / 32 | 4.7e-10 |
| gantry_heldout, good parts | I | 500 | 436 / 431 | 46 / 41 | 0.67 | 0 / 31 | 9.3e-10 |
| gantry_heldout, good parts | H | 500 | 436 / 372 | 81 / 17 | 3.6e-11 | 0 / 27 | 1.5e-08 |
| gantry_latch_spread, good parts | I | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | H | 600 | 600 / 597 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | H | 500 | 500 / 497 | 3 / 0 | 0.25 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 579 / 592 | 5 / 18 | 0.011 | 0 / 0 | 1 |
| gantry_latching, good parts | H | 600 | 579 / 533 | 56 / 10 | 6.9e-09 | 0 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1988 / 1929 | 62 / 3 | 2.5e-15 | 0 / 39 | 3.6e-12 |
| gantry_standard, good parts | H | 2000 | 1988 / 1927 | 63 / 2 | 1.2e-16 | 0 / 34 | 1.2e-10 |

## J against C and against I

| Run | J vs | Trials | Successes J / other | J-only / other-only | p | Escapes J / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | C | 500 | 400 / 395 | 41 / 36 | 0.65 | 0 / 0 | 1 |
| arm_heldout, good parts | I | 500 | 400 / 410 | 18 / 28 | 0.18 | 0 / 28 | 7.5e-09 |
| arm_latch_spread, good parts | C | 600 | 600 / 599 | 1 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | C | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts | I | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| arm_latching, good parts | C | 600 | 563 / 562 | 20 / 19 | 1 | 0 / 0 | 1 |
| arm_latching, good parts | I | 600 | 563 / 562 | 1 / 0 | 1 | 0 / 1 | 1 |
| arm_standard, good parts | C | 2000 | 1935 / 1963 | 11 / 39 | 9e-05 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1935 / 1923 | 21 / 9 | 0.043 | 0 / 39 | 3.6e-12 |
| gantry_heldout, good parts | C | 500 | 452 / 436 | 47 / 31 | 0.089 | 1 / 0 | 1 |
| gantry_heldout, good parts | I | 500 | 452 / 431 | 30 / 9 | 0.0011 | 1 / 31 | 1.5e-08 |
| gantry_latch_spread, good parts | C | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | C | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | I | 600 | 600 / 600 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 500 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_latching, good parts | C | 600 | 592 / 579 | 18 / 5 | 0.011 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 592 / 592 | 0 / 0 | 1 | 0 / 0 | 1 |
| gantry_standard, good parts | C | 2000 | 1959 / 1988 | 4 / 33 | 1.1e-06 | 1 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1959 / 1929 | 37 / 7 | 5.3e-06 | 1 / 39 | 7.3e-12 |

## Bad units passed on good-part trials, per machine

| Machine | C | G | D | F | H | I | J |
|---|---|---|---|---|---|---|---|
| gantry | 0 | 0 | 74 | 77 | 61 | 70 | 2 |
| arm | 0 | 0 | 80 | 99 | 51 | 68 | 0 |

## I's escapes on good-part trials

| Run | Escapes | Depth min-max (mm) | Tilt max (deg) | Lateral max (mm) | Reasons | Conditions |
|---|---|---|---|---|---|---|
| arm_heldout | 28 | 12.85-14.95 | 5.01 | 0.65 | {'false_accept': 28} | {'heldout_mischar_2mm': 20, 'heldout_mischar_1mm': 7, 'heldout_worst_case': 1} |
| arm_latching | 1 | 7.81-7.81 | 3.06 | 0.20 | {'false_accept': 1} | {'mf_noise_1mm': 1} |
| arm_standard | 39 | 9.38-15.00 | 6.02 | 0.70 | {'false_accept': 39} | {'noise_2mm': 25, 'noise_1mm': 11, 'generalization_combined': 3} |
| gantry_heldout | 31 | 14.31-14.98 | 4.63 | 0.71 | {'false_accept': 31} | {'heldout_mischar_2mm': 25, 'heldout_mischar_1mm': 5, 'heldout_worst_case': 1} |
| gantry_standard | 39 | 9.78-15.01 | 5.94 | 0.70 | {'false_accept': 39} | {'noise_2mm': 25, 'noise_1mm': 11, 'generalization_combined': 3} |
