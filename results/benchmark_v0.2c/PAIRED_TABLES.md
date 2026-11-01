# Paired comparisons for benchmark_v0.2c

| Run | C vs | Trials | Successes C / other | C-only / other-only | p | Escapes C / other | p |
|---|---|---|---|---|---|---|---|
| arm_heldout, good parts | I | 500 | 390 / 394 | 56 / 60 | 0.78 | 0 / 31 | 9.3e-10 |
| arm_heldout, good parts | H | 500 | 390 / 336 | 74 / 20 | 1.8e-08 | 0 / 21 | 9.5e-07 |
| arm_latch_spread, good parts | I | 600 | 597 / 474 | 125 / 2 | 9.6e-35 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | I | 500 | 497 / 474 | 25 / 2 | 5.6e-06 | 0 / 0 | 1 |
| arm_latch_spread, good parts | H | 600 | 597 / 475 | 124 / 2 | 1.9e-34 | 0 / 0 | 1 |
| arm_latch_spread, good parts without mf_terminal_max | H | 500 | 497 / 475 | 24 / 2 | 1e-05 | 0 / 0 | 1 |
| arm_latching, good parts | I | 600 | 562 / 577 | 13 / 28 | 0.028 | 0 / 3 | 0.25 |
| arm_latching, good parts | H | 600 | 562 / 484 | 84 / 6 | 1.1e-18 | 0 / 0 | 1 |
| arm_standard, good parts | I | 2000 | 1952 / 1928 | 42 / 18 | 0.0027 | 0 / 34 | 1.2e-10 |
| arm_standard, good parts | H | 2000 | 1952 / 1895 | 70 / 13 | 1.3e-10 | 0 / 22 | 4.8e-07 |
| gantry_heldout, good parts | I | 500 | 429 / 420 | 50 / 41 | 0.4 | 0 / 34 | 1.2e-10 |
| gantry_heldout, good parts | H | 500 | 429 / 354 | 95 / 20 | 7.1e-13 | 0 / 29 | 3.7e-09 |
| gantry_latch_spread, good parts | I | 600 | 600 / 473 | 127 / 0 | 1.2e-38 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | I | 500 | 500 / 473 | 27 / 0 | 1.5e-08 | 0 / 0 | 1 |
| gantry_latch_spread, good parts | H | 600 | 600 / 481 | 119 / 0 | 3e-36 | 0 / 0 | 1 |
| gantry_latch_spread, good parts without mf_terminal_max | H | 500 | 500 / 481 | 19 / 0 | 3.8e-06 | 0 / 0 | 1 |
| gantry_latching, good parts | I | 600 | 574 / 595 | 3 / 24 | 4.9e-05 | 0 / 0 | 1 |
| gantry_latching, good parts | H | 600 | 574 / 523 | 63 / 12 | 1.7e-09 | 0 / 0 | 1 |
| gantry_standard, good parts | I | 2000 | 1980 / 1932 | 52 / 4 | 1.1e-11 | 0 / 33 | 2.3e-10 |
| gantry_standard, good parts | H | 2000 | 1980 / 1925 | 59 / 4 | 1.4e-13 | 0 / 30 | 1.9e-09 |

## Bad units passed on good-part trials, per machine

| Machine | C | G | D | F | H | I |
|---|---|---|---|---|---|---|
| gantry | 0 | 0 | 117 | 183 | 59 | 67 |
| arm | 0 | 1 | 103 | 124 | 43 | 68 |

## I's escapes on good-part trials

| Run | Escapes | Depth min-max (mm) | Tilt max (deg) | Lateral max (mm) | Reasons | Conditions |
|---|---|---|---|---|---|---|
| arm_heldout | 31 | 12.74-14.99 | 4.20 | 0.70 | {'false_accept': 31} | {'heldout_mischar_2mm': 25, 'heldout_mischar_1mm': 5, 'heldout_worst_case': 1} |
| arm_latching | 3 | 7.80-7.80 | 3.07 | 0.22 | {'false_accept': 3} | {'mf_noise_1mm': 3} |
| arm_standard | 34 | 11.03-15.00 | 4.96 | 0.73 | {'false_accept': 34} | {'noise_2mm': 24, 'noise_1mm': 6, 'generalization_combined': 3, 'generalization_tight': 1} |
| gantry_heldout | 34 | 13.47-15.00 | 4.08 | 0.65 | {'false_accept': 34} | {'heldout_mischar_2mm': 27, 'heldout_mischar_1mm': 4, 'heldout_worst_case': 3} |
| gantry_standard | 33 | 11.48-15.01 | 4.46 | 0.66 | {'false_accept': 33} | {'noise_2mm': 26, 'noise_1mm': 4, 'generalization_combined': 3} |
