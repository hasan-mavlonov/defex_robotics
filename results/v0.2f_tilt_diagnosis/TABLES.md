# v0.2f tilt diagnosis: tables (frozen code, flags off; seeds [2026, 2027]; 11680 trials)

Made by `experiments/v02f_tilt_tables.py` from `runs/*.jsonl.gz`. Development seeds only.

## Item 1: tilt evidence against true tilt, C and G, latching and latch_spread

Latch checks with a tilt verdict (PASS or FAIL). 'Under by > 1 deg': true tilt minus measured tilt over 1 deg. Cause: the largest of the three projections on the true tilt direction (camera axis error, R_corr folds, in-hand estimate error).

| Machine | Ctrl | Trials | Verdicts | Under by > 1 deg | of which true tilt > 2 deg | Cause camera / folds / in-hand (all under > 1) | max underestimate (deg) |
|---|---|---|---|---|---|---|---|
| arm | C | 1600 | 2174 | 82 | 1 | 48 / 1 / 33 | 2.68 |
| arm | G | 1600 | 2186 | 86 | 5 | 51 / 2 / 33 | 2.68 |
| gantry | C | 1600 | 1974 | 33 | 2 | 25 / 0 / 8 | 2.18 |
| gantry | G | 1600 | 1986 | 33 | 2 | 25 / 0 / 8 | 2.18 |

Verdicts under by > 1 deg at a true tilt over 2 deg (each listed):

| Machine | Ctrl | Seed | Condition | Trial | Path | F (N) | Measured | True | CoP edge | Camera err | Folds (R_corr tilt) | In-hand err | Cause | Verdict | Outcome | Final tilt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm | C | 2026 | mf_noise_1mm | 43 | detect:bottomed | 33.6 | 0.39 | 3.07 | 0.64 | 3.37 | 0.00 | 0.22 | camera | PASS | seated | 2.81 |
| arm | G | 2026 | mf_noise_1mm | 8 | detect:floor_impact | 16.7 | 1.77 | 3.14 | 0.29 | 2.73 | 4.37 | 0.37 | folds | PASS | seated | 2.98 |
| arm | G | 2026 | mf_noise_1mm | 17 | detect:floor_impact | 12.9 | 1.43 | 2.56 | 0.15 | 0.64 | 4.60 | 0.48 | folds | PASS | seated | 2.46 |
| arm | G | 2026 | mf_noise_1mm | 34 | detect:bottomed | 32.0 | 0.12 | 2.10 | 0.64 | 1.56 | 1.06 | 0.85 | camera | PASS | seated | 1.88 |
| arm | G | 2026 | mf_noise_1mm | 43 | detect:bottomed | 33.6 | 0.39 | 3.07 | 0.64 | 3.37 | 0.00 | 0.22 | camera | PASS | seated | 2.81 |
| arm | G | 2027 | mf_noise_1mm | 21 | detect:bottomed | 31.9 | 0.10 | 2.05 | 0.65 | 2.17 | 0.00 | 0.23 | camera | PASS | seated | 1.83 |
| gantry | C | 2026 | mf_noise_1mm | 43 | held_reseat | 32.2 | 0.59 | 2.77 | 0.60 | 3.37 | 0.00 | 0.22 | camera | PASS | seated | 2.82 |
| gantry | C | 2027 | mf_noise_1mm | 38 | held_reseat | 32.1 | 0.91 | 2.07 | 0.57 | 2.69 | 0.00 | 0.36 | camera | PASS | seated | 2.13 |
| gantry | G | 2026 | mf_noise_1mm | 43 | held_reseat | 32.2 | 0.59 | 2.77 | 0.60 | 3.37 | 0.00 | 0.22 | camera | PASS | seated | 2.82 |
| gantry | G | 2027 | mf_noise_1mm | 38 | held_reseat | 32.1 | 0.91 | 2.07 | 0.57 | 2.69 | 0.00 | 0.36 | camera | PASS | seated | 2.13 |

Final true tilt of trials C or G declared seated (latching, latch_spread; good and bad parts):

| Machine | Ctrl | Declared | tilt < 2 | 2-2.5 | 2.5-3 | > 3 (bad units) | max |
|---|---|---|---|---|---|---|---|
| arm | C | 874 | 871 | 2 | 1 | 0 | 2.81 |
| arm | G | 890 | 885 | 3 | 2 | 0 | 2.98 |
| arm | J | 354 | 353 | 1 | 0 | 0 | 2.00 |
| gantry | C | 892 | 890 | 1 | 1 | 0 | 2.82 |
| gantry | G | 898 | 895 | 2 | 1 | 0 | 2.82 |
| gantry | J | 358 | 358 | 0 | 0 | 0 | 1.87 |

Each declared trial at 2 deg or more (C, G):

| Machine | Ctrl | Seed | Condition | Trial | Final tilt | Outcome | Last verdict: measured / true / edge / F |
|---|---|---|---|---|---|---|---|
| arm | G | 2026 | mf_noise_1mm | 8 | 2.98 | seated | PASS: 1.77 / 3.14 / 0.29 / 16.7 |
| gantry | C | 2026 | mf_noise_1mm | 43 | 2.82 | seated | PASS: 0.59 / 2.77 / 0.60 / 32.2 |
| gantry | G | 2026 | mf_noise_1mm | 43 | 2.82 | seated | PASS: 0.59 / 2.77 / 0.60 / 32.2 |
| arm | C | 2026 | mf_noise_1mm | 43 | 2.81 | seated | PASS: 0.39 / 3.07 / 0.64 / 33.6 |
| arm | G | 2026 | mf_noise_1mm | 43 | 2.81 | seated | PASS: 0.39 / 3.07 / 0.64 / 33.6 |
| arm | G | 2026 | mf_noise_1mm | 17 | 2.46 | seated | PASS: 1.43 / 2.56 / 0.15 / 12.9 |
| gantry | G | 2027 | mf_noise_1mm | 40 | 2.20 | seated | PASS: 2.14 / 2.15 / 0.59 / 32.1 |
| arm | C | 2027 | mf_latch_weak | 10 | 2.19 | seated | PASS: 2.67 / 2.42 / 0.64 / 31.9 |
| arm | G | 2027 | mf_latch_weak | 10 | 2.19 | seated | PASS: 2.67 / 2.42 / 0.64 / 31.9 |
| gantry | C | 2027 | mf_noise_1mm | 38 | 2.13 | seated | PASS: 0.91 / 2.07 / 0.57 / 32.1 |
| gantry | G | 2027 | mf_noise_1mm | 38 | 2.13 | seated | PASS: 0.91 / 2.07 / 0.57 / 32.1 |
| arm | C | 2027 | mf_noise_1mm | 44 | 2.06 | seated | PASS: 1.60 / 2.32 / 0.69 / 33.4 |
| arm | G | 2027 | mf_noise_1mm | 44 | 2.06 | seated | PASS: 1.60 / 2.32 / 0.69 / 33.4 |

## Item 2: J's first latch check

| Machine | J trials (latching, latch_spread) | Latch checks | of which hand-over | hand-over with samples | no verdict (all) | Verdicts | Hand-over: measured tilt p50 / p95 / max | Hand-over: true tilt p50 / max |
|---|---|---|---|---|---|---|---|---|
| arm | 640 | 753 | 562 | 0 | 562 | 191 | 0.06 / 0.07 / 0.09 | 0.51 / 2.38 |
| gantry | 640 | 740 | 550 | 0 | 550 | 190 | 0.17 / 0.31 / 0.69 | 0.34 / 1.82 |

## Item 3: housing-only VERIFY (standard suite), C and G, accepted units

Final true tilt and |yaw| of every trial declared seated (trials.csv fields final_tilt_deg, final_yaw_deg). Limits 3.0 deg each.

| Machine | Ctrl | Declared | tilt p50 / p95 / p99 / max | tilt 2-2.5 / 2.5-3 / > 3 | |yaw| p50 / p95 / p99 / max | |yaw| 2-2.5 / 2.5-3 / > 3 | bad units |
|---|---|---|---|---|---|---|---|
| arm | C | 973 | 0.01 / 0.02 / 0.06 / 0.60 | 0 / 0 / 0 | 0.41 / 1.33 / 1.78 / 1.94 | 0 / 0 / 0 | 0 |
| arm | G | 987 | 0.01 / 0.02 / 0.09 / 0.60 | 0 / 0 / 0 | 0.41 / 1.35 / 1.80 / 1.98 | 0 / 0 / 0 | 0 |
| gantry | C | 994 | 0.00 / 0.00 / 0.63 / 2.24 | 2 / 0 / 0 | 0.03 / 0.46 / 1.13 / 1.77 | 0 / 0 / 0 | 0 |
| gantry | G | 999 | 0.00 / 0.00 / 0.63 / 2.29 | 3 / 0 / 0 | 0.02 / 0.48 / 1.19 / 1.71 | 0 / 0 / 0 | 0 |

By condition, declared trials with tilt or |yaw| at 2 deg or more (C and G pooled):

| Machine | Condition | Declared | tilt >= 2 | tilt >= 2.5 | |yaw| >= 2 | |yaw| >= 2.5 |
|---|---|---|---|---|---|---|
| gantry | noise_2mm | 93 | 5 | 0 | 0 | 0 |

Yaw verdict path of each declared trial, and its true |yaw| (deg):

| Machine | Path | Declared | |yaw| p50 / p95 / max | |yaw| > 2 (the wall-yaw tolerance) |
|---|---|---|---|---|
| arm | wall_yaw PASS | 1910 | 0.41 / 1.35 / 1.98 | 0 |
| arm | wall_yaw PASS after a turn | 50 | 0.02 / 0.13 / 0.68 | 0 |
| gantry | yaw sweep | 1993 | 0.02 / 0.47 / 1.77 | 0 |

Gantry yaw sweeps of declared trials (events `yaw_centering`; the sweep always ends in SUCCESS):

| Sweep | Declared | final |yaw| p95 / max |
|---|---|---|
| both limits found | 1753 | 0.34 / 1.57 |
| one limit at the 7.0 deg sweep end | 240 | 1.19 / 1.77 |

Tilt evidence at the declared seat (housing only; no check uses it): plug axis against R_corr, against true tilt:

| Machine | Ctrl | Seats | measured p50 / p95 | true p50 / p95 | true >= 2.5 | of which measured >= 2.5 |
|---|---|---|---|---|---|---|
| arm | C | 973 | 0.55 / 1.49 | 0.01 / 0.02 | 0 | 0 |
| arm | G | 987 | 0.55 / 1.63 | 0.01 / 0.02 | 0 | 0 |
| gantry | C | 994 | 0.55 / 1.76 | 0.00 / 0.00 | 0 | 0 |
| gantry | G | 999 | 0.55 / 1.80 | 0.00 / 0.00 | 0 | 0 |

## Item 4: latch checks under the force floor (C and G)

'Would fail': the unguarded evidence fails the bounds (axis > 2.5 deg and CoP > 0.875 or a failed check in the attempt). 'Correct catch': would fail and the true tilt is over 3.0 deg.

| Machine | Ctrl | Path | Checks under the floor | F (N) min / max | Would fail | Correct catches dropped | True tilt > 3 (any) | Outcome of those trials |
|---|---|---|---|---|---|---|---|---|
| arm | C | detect:floor_impact | 7 | 8.2 / 11.0 | 1 | 1 | 1 | seated 6, aborted:defect_suspected:no_retention 1 |
| arm | G | detect:floor_impact | 8 | 8.2 / 10.9 | 1 | 1 | 1 | seated 7, aborted:defect_suspected:no_retention 1 |

Each check under the floor:

| Machine | Ctrl | Seed | Condition | Trial | Path | F (N) | Measured | True | CoP edge | Would fail | Outcome | Final tilt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm | C | 2026 | mf_terminal_min | 8 | detect:floor_impact | 8.8 | 1.40 | 1.92 | 0.03 | False | seated | 1.80 |
| arm | G | 2026 | mf_terminal_min | 8 | detect:floor_impact | 8.8 | 1.40 | 1.92 | 0.03 | False | seated | 1.80 |
| arm | C | 2026 | mf_noise_1mm | 23 | detect:floor_impact | 11.0 | 0.77 | 1.55 | 0.05 | False | seated | 1.46 |
| arm | G | 2026 | mf_noise_1mm | 23 | detect:floor_impact | 10.9 | 0.74 | 1.58 | 0.05 | False | seated | 1.48 |
| arm | C | 2027 | mf_latch_weak | 4 | detect:floor_impact | 9.9 | 1.86 | 1.87 | 0.03 | False | seated | 1.79 |
| arm | G | 2027 | mf_latch_weak | 4 | detect:floor_impact | 9.9 | 1.86 | 1.87 | 0.03 | False | seated | 1.79 |
| arm | C | 2027 | mf_broken_latch | 7 | detect:floor_impact | 8.2 | 2.30 | 2.02 | 0.06 | False | aborted:defect_suspected:no_retention | 1.50 |
| arm | G | 2027 | mf_broken_latch | 7 | detect:floor_impact | 8.2 | 2.30 | 2.02 | 0.06 | False | aborted:defect_suspected:no_retention | 1.50 |
| arm | C | 2027 | mf_noise_1mm | 12 | detect:floor_impact | 10.3 | 0.83 | 1.49 | 0.05 | False | seated | 1.41 |
| arm | C | 2027 | mf_noise_1mm | 24 | detect:floor_impact | 10.7 | 2.06 | 1.86 | 0.08 | False | seated | 1.78 |
| arm | C | 2027 | mf_noise_1mm | 44 | detect:floor_impact | 10.9 | 3.07 | 3.90 | 1.95 | True | seated | 2.06 |
| arm | G | 2027 | mf_noise_1mm | 12 | detect:floor_impact | 10.3 | 0.83 | 1.49 | 0.05 | False | seated | 1.41 |
| arm | G | 2027 | mf_noise_1mm | 36 | detect:floor_impact | 9.4 | 0.68 | 0.66 | 0.02 | False | seated | 0.60 |
| arm | G | 2027 | mf_noise_1mm | 43 | detect:floor_impact | 9.6 | 0.30 | 0.98 | 0.24 | False | seated | 0.86 |
| arm | G | 2027 | mf_noise_1mm | 44 | detect:floor_impact | 10.9 | 3.07 | 3.90 | 1.95 | True | seated | 2.06 |
