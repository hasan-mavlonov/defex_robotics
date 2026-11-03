# Rig-protocol conditions and controllers in ext100

From `trials.csv` under `results/v0.2f_rig_predictions/ext100` (base seed 20261201), the TEST_PROTOCOL conditions and controllers A, C, F, H, I, J only. Rates are k/n with Wilson 95% intervals. Cycle times are of successful trials (good parts) or of all trials (bad parts: time to reject).

## housing-only: pooled over the protocol conditions

| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|
| gantry | A | 126/400 (27.1-36.2%) | 9/400 (1.2-4.2%) | 265/400 (61.5-70.7%) | 4.32 / 4.32 |
| gantry | C | 387/400 (94.5-98.1%) | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 5.49 / 12.99 |
| gantry | F | 336/400 (80.1-87.3%) | 33/400 (5.9-11.4%) | 0/400 (0.0-1.0%) | 2.44 / 9.11 |
| gantry | H | 336/400 (80.1-87.3%) | 30/400 (5.3-10.5%) | 0/400 (0.0-1.0%) | 2.91 / 7.71 |
| gantry | I | 336/400 (80.1-87.3%) | 33/400 (5.9-11.4%) | 0/400 (0.0-1.0%) | 2.44 / 9.11 |
| gantry | J | 360/400 (86.7-92.6%) | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 4.85 / 14.59 |
| arm | A | 115/400 (24.5-33.4%) | 2/400 (0.1-1.8%) | 283/400 (66.1-75.0%) | 4.32 / 4.32 |
| arm | C | 370/400 (89.5-94.7%) | 0/400 (0.0-1.0%) | 5/400 (0.5-2.9%) | 8.50 / 19.22 |
| arm | F | 329/400 (78.2-85.7%) | 39/400 (7.2-13.1%) | 0/400 (0.0-1.0%) | 4.80 / 12.35 |
| arm | H | 315/400 (74.5-82.5%) | 23/400 (3.9-8.5%) | 10/400 (1.4-4.5%) | 4.80 / 10.05 |
| arm | I | 329/400 (78.2-85.7%) | 39/400 (7.2-13.1%) | 0/400 (0.0-1.0%) | 4.80 / 12.35 |
| arm | J | 349/400 (83.6-90.2%) | 0/400 (0.0-1.0%) | 1/400 (0.0-1.4%) | 8.26 / 18.05 |

## Micro-Fit good parts: pooled over the protocol conditions

| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|
| gantry | A | 100/300 (28.2-38.8%) | 0/300 (0.0-1.3%) | 200/300 (61.2-71.8%) | 3.82 / 3.82 |
| gantry | C | 284/300 (91.5-96.7%) | 0/300 (0.0-1.3%) | 0/300 (0.0-1.3%) | 6.16 / 11.64 |
| gantry | F | 297/300 (97.1-99.7%) | 0/300 (0.0-1.3%) | 0/300 (0.0-1.3%) | 2.41 / 11.30 |
| gantry | H | 252/300 (79.4-87.7%) | 0/300 (0.0-1.3%) | 4/300 (0.5-3.4%) | 6.14 / 10.89 |
| gantry | I | 296/300 (96.6-99.5%) | 0/300 (0.0-1.3%) | 1/300 (0.1-1.9%) | 5.47 / 14.15 |
| gantry | J | 296/300 (96.6-99.5%) | 0/300 (0.0-1.3%) | 0/300 (0.0-1.3%) | 5.46 / 14.15 |
| arm | A | 100/300 (28.2-38.8%) | 0/300 (0.0-1.3%) | 200/300 (61.2-71.8%) | 3.79 / 3.79 |
| arm | C | 272/300 (86.8-93.5%) | 0/300 (0.0-1.3%) | 5/300 (0.7-3.8%) | 9.02 / 18.73 |
| arm | F | 279/300 (89.5-95.4%) | 2/300 (0.2-2.4%) | 0/300 (0.0-1.3%) | 4.68 / 13.12 |
| arm | H | 238/300 (74.4-83.5%) | 0/300 (0.0-1.3%) | 9/300 (1.6-5.6%) | 8.50 / 12.68 |
| arm | I | 278/300 (89.1-95.1%) | 2/300 (0.2-2.4%) | 1/300 (0.1-1.9%) | 8.65 / 16.29 |
| arm | J | 280/300 (89.9-95.6%) | 0/300 (0.0-1.3%) | 0/300 (0.0-1.3%) | 8.64 / 16.21 |

## Micro-Fit deliberately bad parts, pooled over the four defects

| Machine | Ctrl | Bad parts passed | Protective stops | Time to reject p50 / p95 (s) |
|---|---|---|---|---|
| gantry | A | 7/400 (0.9-3.6%) | 393/400 (96.4-99.1%) | 2.67 / 2.69 |
| gantry | C | 0/400 (0.0-1.0%) | 23/400 (3.9-8.5%) | 8.52 / 11.54 |
| gantry | F | 252/400 (58.2-67.6%) | 36/400 (6.6-12.2%) | 17.87 / 23.05 |
| gantry | H | 0/400 (0.0-1.0%) | 23/400 (3.9-8.5%) | 9.42 / 13.72 |
| gantry | I | 0/400 (0.0-1.0%) | 36/400 (6.6-12.2%) | 8.91 / 22.21 |
| gantry | J | 0/400 (0.0-1.0%) | 59/400 (11.6-18.6%) | 7.83 / 22.21 |
| arm | A | 5/400 (0.5-2.9%) | 395/400 (97.1-99.5%) | 2.63 / 2.64 |
| arm | C | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 13.01 / 16.19 |
| arm | F | 227/400 (51.9-61.5%) | 0/400 (0.0-1.0%) | 8.93 / 26.38 |
| arm | H | 0/400 (0.0-1.0%) | 1/400 (0.0-1.4%) | 10.18 / 12.29 |
| arm | I | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 11.54 / 26.35 |
| arm | J | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 12.14 / 26.35 |

## Per condition

| Machine | Condition | Ctrl | Success | Bad units or bad parts passed | Stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|---|
| gantry | lateral_3mm | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| gantry | lateral_3mm | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.29 / 5.51 |
| gantry | lateral_3mm | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.45 |
| gantry | lateral_3mm | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.86 / 5.38 |
| gantry | lateral_3mm | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.45 |
| gantry | lateral_3mm | J | 98/100 (93.0-99.4%) | 0/100 (0.0-3.7%) | 0 | 4.77 / 4.94 |
| gantry | noise_1mm | A | 12/100 (7.0-19.8%) | 4/100 (1.6-9.8%) | 84 | 4.32 / 4.32 |
| gantry | noise_1mm | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 6.15 / 8.62 |
| gantry | noise_1mm | F | 94/100 (87.5-97.2%) | 6/100 (2.8-12.5%) | 0 | 2.52 / 8.46 |
| gantry | noise_1mm | H | 95/100 (88.8-97.8%) | 4/100 (1.6-9.8%) | 0 | 5.11 / 7.40 |
| gantry | noise_1mm | I | 94/100 (87.5-97.2%) | 6/100 (2.8-12.5%) | 0 | 2.52 / 8.46 |
| gantry | noise_1mm | J | 97/100 (91.5-99.0%) | 0/100 (0.0-3.7%) | 0 | 5.37 / 10.71 |
| gantry | noise_2mm | A | 14/100 (8.5-22.1%) | 5/100 (2.2-11.2%) | 81 | 4.32 / 4.32 |
| gantry | noise_2mm | C | 87/100 (79.0-92.2%) | 0/100 (0.0-3.7%) | 0 | 9.08 / 19.08 |
| gantry | noise_2mm | F | 42/100 (32.8-51.8%) | 27/100 (19.3-36.4%) | 0 | 6.46 / 21.48 |
| gantry | noise_2mm | H | 41/100 (31.9-50.8%) | 26/100 (18.4-35.4%) | 0 | 6.65 / 20.85 |
| gantry | noise_2mm | I | 42/100 (32.8-51.8%) | 27/100 (19.3-36.4%) | 0 | 6.46 / 21.48 |
| gantry | noise_2mm | J | 67/100 (57.3-75.4%) | 0/100 (0.0-3.7%) | 0 | 9.91 / 23.77 |
| gantry | nominal | A | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.32 / 4.32 |
| gantry | nominal | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.29 / 5.43 |
| gantry | nominal | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.44 |
| gantry | nominal | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.86 / 5.43 |
| gantry | nominal | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.44 |
| gantry | nominal | J | 98/100 (93.0-99.4%) | 0/100 (0.0-3.7%) | 0 | 4.77 / 4.90 |
| gantry | mf_moderate | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| gantry | mf_moderate | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 6.12 / 8.37 |
| gantry | mf_moderate | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.39 / 3.56 |
| gantry | mf_moderate | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 6.06 / 6.82 |
| gantry | mf_moderate | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.44 / 6.59 |
| gantry | mf_moderate | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.44 / 6.59 |
| gantry | mf_noise_1mm | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| gantry | mf_noise_1mm | C | 84/100 (75.6-89.9%) | 0/100 (0.0-3.7%) | 0 | 8.68 / 15.48 |
| gantry | mf_noise_1mm | F | 97/100 (91.5-99.0%) | 0/100 (0.0-3.7%) | 0 | 5.38 / 17.97 |
| gantry | mf_noise_1mm | H | 54/100 (44.3-63.4%) | 0/100 (0.0-3.7%) | 4 | 7.91 / 15.39 |
| gantry | mf_noise_1mm | I | 96/100 (90.2-98.4%) | 0/100 (0.0-3.7%) | 1 | 8.32 / 19.53 |
| gantry | mf_noise_1mm | J | 96/100 (90.2-98.4%) | 0/100 (0.0-3.7%) | 0 | 8.31 / 19.53 |
| gantry | mf_nominal | A | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 3.82 / 3.82 |
| gantry | mf_nominal | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 6.12 / 8.70 |
| gantry | mf_nominal | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.39 / 4.15 |
| gantry | mf_nominal | H | 98/100 (93.0-99.4%) | 0/100 (0.0-3.7%) | 0 | 6.11 / 6.64 |
| gantry | mf_nominal | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.45 / 7.22 |
| gantry | mf_nominal | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.45 / 7.20 |
| gantry | mf_broken_latch | A | 0/100 (0.0-3.7%) | 1/100 (0.2-5.4%) | 99 | nan / nan |
| gantry | mf_broken_latch | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_broken_latch | F | 0/100 (0.0-3.7%) | 100/100 (96.3-100.0%) | 0 | nan / nan |
| gantry | mf_broken_latch | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_broken_latch | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_broken_latch | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_half_latched | A | 0/100 (0.0-3.7%) | 6/100 (2.8-12.5%) | 94 | nan / nan |
| gantry | mf_half_latched | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 18 | nan / nan |
| gantry | mf_half_latched | F | 0/100 (0.0-3.7%) | 64/100 (54.2-72.7%) | 36 | nan / nan |
| gantry | mf_half_latched | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 23 | nan / nan |
| gantry | mf_half_latched | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 36 | nan / nan |
| gantry | mf_half_latched | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 59 | nan / nan |
| gantry | mf_stubbed_terminal | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| gantry | mf_stubbed_terminal | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | F | 0/100 (0.0-3.7%) | 88/100 (80.2-93.0%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| gantry | mf_wrong_polarization | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 5 | nan / nan |
| gantry | mf_wrong_polarization | F | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | lateral_3mm | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| arm | lateral_3mm | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.13 / 8.56 |
| arm | lateral_3mm | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.74 / 4.88 |
| arm | lateral_3mm | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.92 |
| arm | lateral_3mm | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.74 / 4.88 |
| arm | lateral_3mm | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 7.96 / 8.64 |
| arm | noise_1mm | A | 6/100 (2.8-12.5%) | 0/100 (0.0-3.7%) | 94 | 4.32 / 4.32 |
| arm | noise_1mm | C | 97/100 (91.5-99.0%) | 0/100 (0.0-3.7%) | 1 | 10.58 / 16.02 |
| arm | noise_1mm | F | 94/100 (87.5-97.2%) | 6/100 (2.8-12.5%) | 0 | 7.02 / 12.04 |
| arm | noise_1mm | H | 90/100 (82.6-94.5%) | 6/100 (2.8-12.5%) | 2 | 5.80 / 10.46 |
| arm | noise_1mm | I | 94/100 (87.5-97.2%) | 6/100 (2.8-12.5%) | 0 | 7.02 / 12.04 |
| arm | noise_1mm | J | 98/100 (93.0-99.4%) | 0/100 (0.0-3.7%) | 0 | 11.89 / 16.44 |
| arm | noise_2mm | A | 9/100 (4.8-16.2%) | 2/100 (0.6-7.0%) | 89 | 4.32 / 4.32 |
| arm | noise_2mm | C | 73/100 (63.6-80.7%) | 0/100 (0.0-3.7%) | 4 | 15.82 / 23.04 |
| arm | noise_2mm | F | 35/100 (26.4-44.7%) | 33/100 (24.6-42.7%) | 0 | 10.41 / 23.78 |
| arm | noise_2mm | H | 25/100 (17.5-34.3%) | 17/100 (10.9-25.5%) | 8 | 8.20 / 17.59 |
| arm | noise_2mm | I | 35/100 (26.4-44.7%) | 33/100 (24.6-42.7%) | 0 | 10.41 / 23.78 |
| arm | noise_2mm | J | 51/100 (41.3-60.6%) | 0/100 (0.0-3.7%) | 1 | 15.53 / 22.24 |
| arm | nominal | A | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.32 / 4.32 |
| arm | nominal | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.09 / 8.51 |
| arm | nominal | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.85 |
| arm | nominal | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.91 |
| arm | nominal | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.85 |
| arm | nominal | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 7.94 / 8.45 |
| arm | mf_moderate | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| arm | mf_moderate | C | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 0 | 8.97 / 12.50 |
| arm | mf_moderate | F | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 0 | 4.62 / 6.76 |
| arm | mf_moderate | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.39 / 9.41 |
| arm | mf_moderate | I | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 0 | 8.58 / 10.65 |
| arm | mf_moderate | J | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 0 | 8.57 / 10.65 |
| arm | mf_noise_1mm | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| arm | mf_noise_1mm | C | 73/100 (63.6-80.7%) | 0/100 (0.0-3.7%) | 5 | 13.01 / 23.11 |
| arm | mf_noise_1mm | F | 80/100 (71.1-86.7%) | 2/100 (0.6-7.0%) | 0 | 8.11 / 19.32 |
| arm | mf_noise_1mm | H | 39/100 (30.0-48.8%) | 0/100 (0.0-3.7%) | 8 | 10.87 / 16.74 |
| arm | mf_noise_1mm | I | 79/100 (70.0-85.8%) | 2/100 (0.6-7.0%) | 1 | 12.02 / 22.68 |
| arm | mf_noise_1mm | J | 81/100 (72.2-87.5%) | 0/100 (0.0-3.7%) | 0 | 12.06 / 22.49 |
| arm | mf_nominal | A | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 3.79 / 3.79 |
| arm | mf_nominal | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.98 / 12.57 |
| arm | mf_nominal | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.63 / 6.51 |
| arm | mf_nominal | H | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 1 | 8.45 / 9.53 |
| arm | mf_nominal | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.58 / 10.45 |
| arm | mf_nominal | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.57 / 10.45 |
| arm | mf_broken_latch | A | 0/100 (0.0-3.7%) | 1/100 (0.2-5.4%) | 99 | nan / nan |
| arm | mf_broken_latch | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_broken_latch | F | 0/100 (0.0-3.7%) | 100/100 (96.3-100.0%) | 0 | nan / nan |
| arm | mf_broken_latch | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 1 | nan / nan |
| arm | mf_broken_latch | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_broken_latch | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_half_latched | A | 0/100 (0.0-3.7%) | 4/100 (1.6-9.8%) | 96 | nan / nan |
| arm | mf_half_latched | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_half_latched | F | 0/100 (0.0-3.7%) | 95/100 (88.8-97.8%) | 0 | nan / nan |
| arm | mf_half_latched | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_half_latched | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_half_latched | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| arm | mf_stubbed_terminal | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | F | 0/100 (0.0-3.7%) | 32/100 (23.7-41.7%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_wrong_polarization | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| arm | mf_wrong_polarization | C | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_wrong_polarization | F | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_wrong_polarization | H | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_wrong_polarization | I | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |
| arm | mf_wrong_polarization | J | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 0 | nan / nan |

## Predicted differences between controllers (paired, same trials)

C-only / other-only: trials where only C (only the other) succeeded, or only C (only the other) passed a bad unit or bad part. Exact McNemar p. The difference is C minus the other, with its Newcombe paired 95% interval.

| Machine | Part | C vs | Metric | C / other | C-only / other-only | p | C - other (95% CI) |
|---|---|---|---|---|---|---|---|
| gantry | housing-only | I | success | 387 / 336 of 400 | 53 / 2 | 8.6e-14 | +12.8 (+9.5 to +16.4) points |
| gantry | housing-only | I | bad units | 0 / 33 of 400 | 0 / 33 | 2.3e-10 | -8.2 (-11.4 to -5.7) points |
| gantry | housing-only | J | success | 387 / 360 of 400 | 29 / 2 | 4.6e-07 | +6.8 (+4.2 to +9.7) points |
| gantry | housing-only | J | bad units | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| gantry | housing-only | F | success | 387 / 336 of 400 | 53 / 2 | 8.6e-14 | +12.8 (+9.5 to +16.4) points |
| gantry | housing-only | F | bad units | 0 / 33 of 400 | 0 / 33 | 2.3e-10 | -8.2 (-11.4 to -5.7) points |
| gantry | Micro-Fit good parts | I | success | 284 / 296 of 300 | 1 / 13 | 0.0018 | -4.0 (-7.0 to -1.7) points |
| gantry | Micro-Fit good parts | I | bad units | 0 / 0 of 300 | 0 / 0 | 1 | +0.0 (-1.3 to +1.3) points |
| gantry | Micro-Fit good parts | J | success | 284 / 296 of 300 | 1 / 13 | 0.0018 | -4.0 (-7.0 to -1.7) points |
| gantry | Micro-Fit good parts | J | bad units | 0 / 0 of 300 | 0 / 0 | 1 | +0.0 (-1.3 to +1.3) points |
| gantry | Micro-Fit good parts | F | success | 284 / 297 of 300 | 0 / 13 | 0.00024 | -4.3 (-7.3 to -2.2) points |
| gantry | Micro-Fit good parts | F | bad units | 0 / 0 of 300 | 0 / 0 | 1 | +0.0 (-1.3 to +1.3) points |
| gantry | Micro-Fit bad parts | I | bad parts passed | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| gantry | Micro-Fit bad parts | J | bad parts passed | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| gantry | Micro-Fit bad parts | F | bad parts passed | 0 / 252 of 400 | 0 / 252 | 2.8e-76 | -63.0 (-67.6 to -58.1) points |
| arm | housing-only | I | success | 370 / 329 of 400 | 45 / 4 | 8.2e-10 | +10.3 (+7.1 to +13.7) points |
| arm | housing-only | I | bad units | 0 / 39 of 400 | 0 / 39 | 3.6e-12 | -9.8 (-13.1 to -7.0) points |
| arm | housing-only | J | success | 370 / 349 of 400 | 26 / 5 | 0.00019 | +5.2 (+2.6 to +8.1) points |
| arm | housing-only | J | bad units | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| arm | housing-only | F | success | 370 / 329 of 400 | 45 / 4 | 8.2e-10 | +10.3 (+7.1 to +13.7) points |
| arm | housing-only | F | bad units | 0 / 39 of 400 | 0 / 39 | 3.6e-12 | -9.8 (-13.1 to -7.0) points |
| arm | Micro-Fit good parts | I | success | 272 / 278 of 300 | 12 / 18 | 0.36 | -2.0 (-5.8 to +1.7) points |
| arm | Micro-Fit good parts | I | bad units | 0 / 2 of 300 | 0 / 2 | 0.5 | -0.7 (-2.4 to +0.7) points |
| arm | Micro-Fit good parts | J | success | 272 / 280 of 300 | 11 / 19 | 0.2 | -2.7 (-6.4 to +1.0) points |
| arm | Micro-Fit good parts | J | bad units | 0 / 0 of 300 | 0 / 0 | 1 | +0.0 (-1.3 to +1.3) points |
| arm | Micro-Fit good parts | F | success | 272 / 279 of 300 | 11 / 18 | 0.26 | -2.3 (-6.0 to +1.2) points |
| arm | Micro-Fit good parts | F | bad units | 0 / 2 of 300 | 0 / 2 | 0.5 | -0.7 (-2.4 to +0.7) points |
| arm | Micro-Fit bad parts | I | bad parts passed | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| arm | Micro-Fit bad parts | J | bad parts passed | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| arm | Micro-Fit bad parts | F | bad parts passed | 0 / 227 of 400 | 0 / 227 | 9.3e-69 | -56.8 (-61.5 to -51.8) points |

## Final pose of the bad units passed on good parts

What the rig's pose measurement has to resolve. Depth is from the socket mouth (housing-only full depth 15 mm, Micro-Fit 8 mm); the pass limits are depth >= full - 0.5 mm and abs(tilt), abs(yaw) <= 3 deg.

| Machine | Part | Ctrl | Bad units | At full depth | Of those, tilt > 3 deg / yaw > 3 deg | max of abs(tilt), abs(yaw), range (deg) |
|---|---|---|---|---|---|---|
| gantry | housing-only | A | 9 | 8 | 0 / 8 | 3.34-4.74 |
| gantry | housing-only | F | 33 | 30 | 11 / 19 | 3.00-5.00 |
| gantry | housing-only | H | 30 | 24 | 7 / 17 | 3.01-4.74 |
| gantry | housing-only | I | 33 | 30 | 11 / 19 | 3.00-5.00 |
| arm | housing-only | A | 2 | 2 | 0 / 2 | 3.45-4.01 |
| arm | housing-only | F | 39 | 36 | 18 / 18 | 3.00-5.01 |
| arm | housing-only | H | 23 | 15 | 8 / 7 | 3.01-4.45 |
| arm | housing-only | I | 39 | 36 | 18 / 18 | 3.00-5.01 |
| arm | Micro-Fit good parts | F | 2 | 2 | 2 / 0 | 3.18-3.22 |
| arm | Micro-Fit good parts | I | 2 | 2 | 2 / 0 | 3.18-3.22 |
