# Rig-protocol conditions and controllers in benchmark_v0.2e

From `trials.csv` under `results/benchmark_v0.2e` (base seed 20261130), the TEST_PROTOCOL conditions and controllers A, C, F, H, I, J only. Rates are k/n with Wilson 95% intervals. Cycle times are of successful trials (good parts) or of all trials (bad parts: time to reject).

## housing-only: pooled over the protocol conditions

| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|
| gantry | A | 124/400 (26.7-35.7%) | 8/400 (1.0-3.9%) | 268/400 (62.2-71.4%) | 4.32 / 4.32 |
| gantry | C | 382/400 (93.0-97.1%) | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 5.45 / 12.45 |
| gantry | F | 340/400 (81.2-88.2%) | 29/400 (5.1-10.2%) | 0/400 (0.0-1.0%) | 2.44 / 11.95 |
| gantry | H | 341/400 (81.4-88.4%) | 25/400 (4.3-9.1%) | 0/400 (0.0-1.0%) | 2.91 / 10.98 |
| gantry | I | 340/400 (81.2-88.2%) | 29/400 (5.1-10.2%) | 0/400 (0.0-1.0%) | 2.44 / 11.95 |
| gantry | J | 365/400 (88.1-93.6%) | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 4.86 / 14.72 |
| arm | A | 117/400 (25.0-33.9%) | 2/400 (0.1-1.8%) | 281/400 (65.6-74.5%) | 4.32 / 4.32 |
| arm | C | 371/400 (89.8-94.9%) | 0/400 (0.0-1.0%) | 3/400 (0.3-2.2%) | 8.54 / 18.39 |
| arm | F | 331/400 (78.7-86.1%) | 28/400 (4.9-9.9%) | 0/400 (0.0-1.0%) | 4.82 / 14.54 |
| arm | H | 323/400 (76.6-84.3%) | 18/400 (2.9-7.0%) | 10/400 (1.4-4.5%) | 4.83 / 10.47 |
| arm | I | 331/400 (78.7-86.1%) | 28/400 (4.9-9.9%) | 0/400 (0.0-1.0%) | 4.82 / 14.54 |
| arm | J | 342/400 (81.7-88.6%) | 0/400 (0.0-1.0%) | 0/400 (0.0-1.0%) | 8.29 / 18.40 |

## Micro-Fit good parts: pooled over the protocol conditions

| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|
| gantry | A | 209/600 (31.1-38.7%) | 0/600 (0.0-0.6%) | 391/600 (61.3-68.9%) | 3.82 / 3.82 |
| gantry | C | 585/600 (95.9-98.5%) | 0/600 (0.0-0.6%) | 0/600 (0.0-0.6%) | 6.16 / 13.71 |
| gantry | F | 593/600 (97.6-99.4%) | 0/600 (0.0-0.6%) | 1/600 (0.0-0.9%) | 2.40 / 11.10 |
| gantry | H | 520/600 (83.7-89.2%) | 0/600 (0.0-0.6%) | 11/600 (1.0-3.3%) | 6.10 / 10.54 |
| gantry | I | 592/600 (97.4-99.3%) | 0/600 (0.0-0.6%) | 2/600 (0.1-1.2%) | 5.46 / 13.97 |
| gantry | J | 592/600 (97.4-99.3%) | 0/600 (0.0-0.6%) | 1/600 (0.0-0.9%) | 5.46 / 13.97 |
| arm | A | 205/600 (30.5-38.1%) | 0/600 (0.0-0.6%) | 395/600 (61.9-69.5%) | 3.79 / 3.79 |
| arm | C | 552/600 (89.6-93.9%) | 0/600 (0.0-0.6%) | 6/600 (0.5-2.2%) | 8.99 / 17.67 |
| arm | F | 571/600 (93.1-96.6%) | 3/600 (0.2-1.5%) | 3/600 (0.2-1.5%) | 4.66 / 12.30 |
| arm | H | 474/600 (75.6-82.1%) | 0/600 (0.0-0.6%) | 19/600 (2.0-4.9%) | 8.43 / 12.12 |
| arm | I | 570/600 (93.0-96.5%) | 3/600 (0.2-1.5%) | 4/600 (0.3-1.7%) | 8.63 / 16.11 |
| arm | J | 572/600 (93.3-96.8%) | 1/600 (0.0-0.9%) | 3/600 (0.2-1.5%) | 8.62 / 16.18 |

## Micro-Fit deliberately bad parts, pooled over the four defects

| Machine | Ctrl | Bad parts passed | Protective stops | Time to reject p50 / p95 (s) |
|---|---|---|---|---|
| gantry | A | 7/800 (0.4-1.8%) | 793/800 (98.2-99.6%) | 2.67 / 2.69 |
| gantry | C | 0/800 (0.0-0.5%) | 32/800 (2.8-5.6%) | 8.93 / 11.50 |
| gantry | F | 518/800 (61.4-68.0%) | 69/800 (6.9-10.8%) | 18.20 / 23.88 |
| gantry | H | 0/800 (0.0-0.5%) | 51/800 (4.9-8.3%) | 9.41 / 13.71 |
| gantry | I | 0/800 (0.0-0.5%) | 69/800 (6.9-10.8%) | 8.91 / 22.68 |
| gantry | J | 0/800 (0.0-0.5%) | 122/800 (12.9-17.9%) | 7.82 / 22.68 |
| arm | A | 3/800 (0.1-1.1%) | 797/800 (98.9-99.9%) | 2.63 / 2.65 |
| arm | C | 0/800 (0.0-0.5%) | 0/800 (0.0-0.5%) | 13.02 / 16.33 |
| arm | F | 468/800 (55.1-61.9%) | 0/800 (0.0-0.5%) | 9.04 / 26.38 |
| arm | H | 0/800 (0.0-0.5%) | 0/800 (0.0-0.5%) | 10.13 / 12.38 |
| arm | I | 0/800 (0.0-0.5%) | 0/800 (0.0-0.5%) | 11.53 / 26.35 |
| arm | J | 0/800 (0.0-0.5%) | 0/800 (0.0-0.5%) | 12.17 / 26.35 |

## Per condition

| Machine | Condition | Ctrl | Success | Bad units or bad parts passed | Stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|---|
| gantry | lateral_3mm | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| gantry | lateral_3mm | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.28 / 5.44 |
| gantry | lateral_3mm | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.44 |
| gantry | lateral_3mm | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.86 / 5.40 |
| gantry | lateral_3mm | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.44 |
| gantry | lateral_3mm | J | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 0 | 4.77 / 4.91 |
| gantry | noise_1mm | A | 12/100 (7.0-19.8%) | 4/100 (1.6-9.8%) | 84 | 4.32 / 4.32 |
| gantry | noise_1mm | C | 99/100 (94.6-99.8%) | 0/100 (0.0-3.7%) | 0 | 6.27 / 11.13 |
| gantry | noise_1mm | F | 88/100 (80.2-93.0%) | 10/100 (5.5-17.4%) | 0 | 3.13 / 8.44 |
| gantry | noise_1mm | H | 88/100 (80.2-93.0%) | 9/100 (4.8-16.2%) | 0 | 5.36 / 8.15 |
| gantry | noise_1mm | I | 88/100 (80.2-93.0%) | 10/100 (5.5-17.4%) | 0 | 3.13 / 8.44 |
| gantry | noise_1mm | J | 97/100 (91.5-99.0%) | 0/100 (0.0-3.7%) | 0 | 5.79 / 10.76 |
| gantry | noise_2mm | A | 12/100 (7.0-19.8%) | 4/100 (1.6-9.8%) | 84 | 4.32 / 4.32 |
| gantry | noise_2mm | C | 83/100 (74.5-89.1%) | 0/100 (0.0-3.7%) | 0 | 9.89 / 16.46 |
| gantry | noise_2mm | F | 52/100 (42.3-61.5%) | 19/100 (12.5-27.8%) | 0 | 6.48 / 22.18 |
| gantry | noise_2mm | H | 53/100 (43.3-62.5%) | 16/100 (10.1-24.4%) | 0 | 7.14 / 21.55 |
| gantry | noise_2mm | I | 52/100 (42.3-61.5%) | 19/100 (12.5-27.8%) | 0 | 6.48 / 22.18 |
| gantry | noise_2mm | J | 69/100 (59.4-77.2%) | 0/100 (0.0-3.7%) | 0 | 8.92 / 22.80 |
| gantry | nominal | A | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.32 / 4.32 |
| gantry | nominal | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 5.30 / 5.45 |
| gantry | nominal | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.44 |
| gantry | nominal | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.86 / 5.48 |
| gantry | nominal | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 2.43 / 2.44 |
| gantry | nominal | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.76 / 4.90 |
| gantry | mf_moderate | A | 5/200 (1.1-5.7%) | 0/200 (0.0-1.9%) | 195 | 3.82 / 3.82 |
| gantry | mf_moderate | C | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 6.11 / 8.60 |
| gantry | mf_moderate | F | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 2.39 / 3.40 |
| gantry | mf_moderate | H | 199/200 (97.2-99.9%) | 0/200 (0.0-1.9%) | 0 | 6.04 / 6.70 |
| gantry | mf_moderate | I | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 5.44 / 6.49 |
| gantry | mf_moderate | J | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 5.44 / 6.44 |
| gantry | mf_noise_1mm | A | 4/200 (0.8-5.0%) | 0/200 (0.0-1.9%) | 196 | 3.82 / 3.82 |
| gantry | mf_noise_1mm | C | 185/200 (88.0-95.4%) | 0/200 (0.0-1.9%) | 0 | 8.82 / 16.45 |
| gantry | mf_noise_1mm | F | 193/200 (93.0-98.3%) | 0/200 (0.0-1.9%) | 1 | 5.66 / 15.12 |
| gantry | mf_noise_1mm | H | 121/200 (53.6-67.0%) | 0/200 (0.0-1.9%) | 11 | 7.96 / 14.50 |
| gantry | mf_noise_1mm | I | 192/200 (92.3-98.0%) | 0/200 (0.0-1.9%) | 2 | 8.66 / 17.30 |
| gantry | mf_noise_1mm | J | 192/200 (92.3-98.0%) | 0/200 (0.0-1.9%) | 1 | 8.66 / 17.30 |
| gantry | mf_nominal | A | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 3.82 / 3.82 |
| gantry | mf_nominal | C | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 6.11 / 8.52 |
| gantry | mf_nominal | F | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 2.39 / 3.42 |
| gantry | mf_nominal | H | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 6.06 / 6.65 |
| gantry | mf_nominal | I | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 5.44 / 6.47 |
| gantry | mf_nominal | J | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 5.44 / 6.47 |
| gantry | mf_broken_latch | A | 0/200 (0.0-1.9%) | 4/200 (0.8-5.0%) | 196 | nan / nan |
| gantry | mf_broken_latch | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_broken_latch | F | 0/200 (0.0-1.9%) | 200/200 (98.1-100.0%) | 0 | nan / nan |
| gantry | mf_broken_latch | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_broken_latch | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_broken_latch | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_half_latched | A | 0/200 (0.0-1.9%) | 3/200 (0.5-4.3%) | 197 | nan / nan |
| gantry | mf_half_latched | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 30 | nan / nan |
| gantry | mf_half_latched | F | 0/200 (0.0-1.9%) | 131/200 (58.7-71.7%) | 69 | nan / nan |
| gantry | mf_half_latched | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 51 | nan / nan |
| gantry | mf_half_latched | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 69 | nan / nan |
| gantry | mf_half_latched | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 122 | nan / nan |
| gantry | mf_stubbed_terminal | A | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 200 | nan / nan |
| gantry | mf_stubbed_terminal | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | F | 0/200 (0.0-1.9%) | 187/200 (89.2-96.2%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | A | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 200 | nan / nan |
| gantry | mf_wrong_polarization | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 2 | nan / nan |
| gantry | mf_wrong_polarization | F | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | lateral_3mm | A | 0/100 (0.0-3.7%) | 0/100 (0.0-3.7%) | 100 | nan / nan |
| arm | lateral_3mm | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.11 / 8.59 |
| arm | lateral_3mm | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.87 |
| arm | lateral_3mm | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.76 / 4.87 |
| arm | lateral_3mm | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.87 |
| arm | lateral_3mm | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 7.94 / 8.42 |
| arm | noise_1mm | A | 8/100 (4.1-15.0%) | 2/100 (0.6-7.0%) | 90 | 4.32 / 4.32 |
| arm | noise_1mm | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 11.07 / 16.41 |
| arm | noise_1mm | F | 86/100 (77.9-91.5%) | 11/100 (6.3-18.6%) | 0 | 6.52 / 11.73 |
| arm | noise_1mm | H | 86/100 (77.9-91.5%) | 8/100 (4.1-15.0%) | 1 | 5.89 / 10.43 |
| arm | noise_1mm | I | 86/100 (77.9-91.5%) | 11/100 (6.3-18.6%) | 0 | 6.52 / 11.73 |
| arm | noise_1mm | J | 94/100 (87.5-97.2%) | 0/100 (0.0-3.7%) | 0 | 11.52 / 17.87 |
| arm | noise_2mm | A | 9/100 (4.8-16.2%) | 0/100 (0.0-3.7%) | 91 | 4.32 / 4.32 |
| arm | noise_2mm | C | 71/100 (61.5-79.0%) | 0/100 (0.0-3.7%) | 3 | 15.99 / 23.51 |
| arm | noise_2mm | F | 45/100 (35.6-54.8%) | 17/100 (10.9-25.5%) | 0 | 10.70 / 23.78 |
| arm | noise_2mm | H | 37/100 (28.2-46.8%) | 10/100 (5.5-17.4%) | 9 | 8.47 / 19.57 |
| arm | noise_2mm | I | 45/100 (35.6-54.8%) | 17/100 (10.9-25.5%) | 0 | 10.70 / 23.78 |
| arm | noise_2mm | J | 48/100 (38.5-57.7%) | 0/100 (0.0-3.7%) | 0 | 15.04 / 24.56 |
| arm | nominal | A | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.32 / 4.32 |
| arm | nominal | C | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 8.09 / 8.68 |
| arm | nominal | F | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.87 |
| arm | nominal | H | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.76 / 5.00 |
| arm | nominal | I | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 4.75 / 4.87 |
| arm | nominal | J | 100/100 (96.3-100.0%) | 0/100 (0.0-3.7%) | 0 | 7.95 / 8.54 |
| arm | mf_moderate | A | 2/200 (0.3-3.6%) | 0/200 (0.0-1.9%) | 198 | 3.79 / 3.79 |
| arm | mf_moderate | C | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.94 / 12.49 |
| arm | mf_moderate | F | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 4.61 / 6.26 |
| arm | mf_moderate | H | 199/200 (97.2-99.9%) | 0/200 (0.0-1.9%) | 0 | 8.38 / 9.53 |
| arm | mf_moderate | I | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.55 / 10.17 |
| arm | mf_moderate | J | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.55 / 10.17 |
| arm | mf_noise_1mm | A | 3/200 (0.5-4.3%) | 0/200 (0.0-1.9%) | 197 | 3.79 / 3.79 |
| arm | mf_noise_1mm | C | 152/200 (69.6-81.4%) | 0/200 (0.0-1.9%) | 6 | 13.05 / 21.20 |
| arm | mf_noise_1mm | F | 171/200 (80.0-89.7%) | 3/200 (0.5-4.3%) | 3 | 8.60 / 15.52 |
| arm | mf_noise_1mm | H | 75/200 (31.1-44.4%) | 0/200 (0.0-1.9%) | 19 | 10.59 / 16.98 |
| arm | mf_noise_1mm | I | 170/200 (79.4-89.3%) | 3/200 (0.5-4.3%) | 4 | 12.51 / 18.87 |
| arm | mf_noise_1mm | J | 172/200 (80.5-90.1%) | 1/200 (0.1-2.8%) | 3 | 12.51 / 18.83 |
| arm | mf_nominal | A | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 3.79 / 3.79 |
| arm | mf_nominal | C | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.93 / 12.46 |
| arm | mf_nominal | F | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 4.59 / 6.27 |
| arm | mf_nominal | H | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.39 / 9.36 |
| arm | mf_nominal | I | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.53 / 10.20 |
| arm | mf_nominal | J | 200/200 (98.1-100.0%) | 0/200 (0.0-1.9%) | 0 | 8.53 / 10.20 |
| arm | mf_broken_latch | A | 0/200 (0.0-1.9%) | 2/200 (0.3-3.6%) | 198 | nan / nan |
| arm | mf_broken_latch | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_broken_latch | F | 0/200 (0.0-1.9%) | 200/200 (98.1-100.0%) | 0 | nan / nan |
| arm | mf_broken_latch | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_broken_latch | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_broken_latch | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_half_latched | A | 0/200 (0.0-1.9%) | 1/200 (0.1-2.8%) | 199 | nan / nan |
| arm | mf_half_latched | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_half_latched | F | 0/200 (0.0-1.9%) | 196/200 (95.0-99.2%) | 0 | nan / nan |
| arm | mf_half_latched | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_half_latched | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_half_latched | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | A | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 200 | nan / nan |
| arm | mf_stubbed_terminal | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | F | 0/200 (0.0-1.9%) | 72/200 (29.7-42.9%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_wrong_polarization | A | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 200 | nan / nan |
| arm | mf_wrong_polarization | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_wrong_polarization | F | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_wrong_polarization | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_wrong_polarization | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |
| arm | mf_wrong_polarization | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 0 | nan / nan |

## Predicted differences between controllers (paired, same trials)

C-only / other-only: trials where only C (only the other) succeeded, or only C (only the other) passed a bad unit or bad part. Exact McNemar p. The difference is C minus the other, with its Newcombe paired 95% interval.

| Machine | Part | C vs | Metric | C / other | C-only / other-only | p | C - other (95% CI) |
|---|---|---|---|---|---|---|---|
| gantry | housing-only | I | success | 382 / 340 of 400 | 49 / 7 | 7.5e-09 | +10.5 (+7.1 to +14.2) points |
| gantry | housing-only | I | bad units | 0 / 29 of 400 | 0 / 29 | 3.7e-09 | -7.2 (-10.2 to -4.9) points |
| gantry | housing-only | J | success | 382 / 365 of 400 | 26 / 9 | 0.006 | +4.2 (+1.4 to +7.3) points |
| gantry | housing-only | J | bad units | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| gantry | housing-only | F | success | 382 / 340 of 400 | 49 / 7 | 7.5e-09 | +10.5 (+7.1 to +14.2) points |
| gantry | housing-only | F | bad units | 0 / 29 of 400 | 0 / 29 | 3.7e-09 | -7.2 (-10.2 to -4.9) points |
| gantry | Micro-Fit good parts | I | success | 585 / 592 of 600 | 7 / 14 | 0.19 | -1.2 (-2.8 to +0.4) points |
| gantry | Micro-Fit good parts | I | bad units | 0 / 0 of 600 | 0 / 0 | 1 | +0.0 (-0.6 to +0.6) points |
| gantry | Micro-Fit good parts | J | success | 585 / 592 of 600 | 7 / 14 | 0.19 | -1.2 (-2.8 to +0.4) points |
| gantry | Micro-Fit good parts | J | bad units | 0 / 0 of 600 | 0 / 0 | 1 | +0.0 (-0.6 to +0.6) points |
| gantry | Micro-Fit good parts | F | success | 585 / 593 of 600 | 6 / 14 | 0.12 | -1.3 (-3.0 to +0.2) points |
| gantry | Micro-Fit good parts | F | bad units | 0 / 0 of 600 | 0 / 0 | 1 | +0.0 (-0.6 to +0.6) points |
| gantry | Micro-Fit bad parts | I | bad parts passed | 0 / 0 of 800 | 0 / 0 | 1 | +0.0 (-0.5 to +0.5) points |
| gantry | Micro-Fit bad parts | J | bad parts passed | 0 / 0 of 800 | 0 / 0 | 1 | +0.0 (-0.5 to +0.5) points |
| gantry | Micro-Fit bad parts | F | bad parts passed | 0 / 518 of 800 | 0 / 518 | 2.3e-156 | -64.8 (-68.0 to -61.3) points |
| arm | housing-only | I | success | 371 / 331 of 400 | 48 / 8 | 4.7e-08 | +10.0 (+6.5 to +13.7) points |
| arm | housing-only | I | bad units | 0 / 28 of 400 | 0 / 28 | 7.5e-09 | -7.0 (-9.9 to -4.7) points |
| arm | housing-only | J | success | 371 / 342 of 400 | 38 / 9 | 2.5e-05 | +7.3 (+4.0 to +10.7) points |
| arm | housing-only | J | bad units | 0 / 0 of 400 | 0 / 0 | 1 | +0.0 (-1.0 to +1.0) points |
| arm | housing-only | F | success | 371 / 331 of 400 | 48 / 8 | 4.7e-08 | +10.0 (+6.5 to +13.7) points |
| arm | housing-only | F | bad units | 0 / 28 of 400 | 0 / 28 | 7.5e-09 | -7.0 (-9.9 to -4.7) points |
| arm | Micro-Fit good parts | I | success | 552 / 570 of 600 | 19 / 37 | 0.022 | -3.0 (-5.5 to -0.6) points |
| arm | Micro-Fit good parts | I | bad units | 0 / 3 of 600 | 0 / 3 | 0.25 | -0.5 (-1.5 to +0.2) points |
| arm | Micro-Fit good parts | J | success | 552 / 572 of 600 | 18 / 38 | 0.01 | -3.3 (-5.9 to -0.9) points |
| arm | Micro-Fit good parts | J | bad units | 0 / 1 of 600 | 0 / 1 | 1 | -0.2 (-0.9 to +0.5) points |
| arm | Micro-Fit good parts | F | success | 552 / 571 of 600 | 18 / 37 | 0.014 | -3.2 (-5.7 to -0.8) points |
| arm | Micro-Fit good parts | F | bad units | 0 / 3 of 600 | 0 / 3 | 0.25 | -0.5 (-1.5 to +0.2) points |
| arm | Micro-Fit bad parts | I | bad parts passed | 0 / 0 of 800 | 0 / 0 | 1 | +0.0 (-0.5 to +0.5) points |
| arm | Micro-Fit bad parts | J | bad parts passed | 0 / 0 of 800 | 0 / 0 | 1 | +0.0 (-0.5 to +0.5) points |
| arm | Micro-Fit bad parts | F | bad parts passed | 0 / 468 of 800 | 0 / 468 | 2.6e-141 | -58.5 (-61.9 to -55.0) points |

## Final pose of the bad units passed on good parts

What the rig's pose measurement has to resolve. Depth is from the socket mouth (housing-only full depth 15 mm, Micro-Fit 8 mm); the pass limits are depth >= full - 0.5 mm and abs(tilt), abs(yaw) <= 3 deg.

| Machine | Part | Ctrl | Bad units | At full depth | Of those, tilt > 3 deg / yaw > 3 deg | max of abs(tilt), abs(yaw), range (deg) |
|---|---|---|---|---|---|---|
| gantry | housing-only | A | 8 | 7 | 0 / 7 | 3.07-4.50 |
| gantry | housing-only | F | 29 | 26 | 13 / 13 | 3.00-4.71 |
| gantry | housing-only | H | 25 | 20 | 10 / 10 | 3.03-4.33 |
| gantry | housing-only | I | 29 | 26 | 13 / 13 | 3.00-4.71 |
| arm | housing-only | A | 2 | 2 | 0 / 2 | 3.24-4.00 |
| arm | housing-only | F | 28 | 25 | 13 / 12 | 3.02-4.18 |
| arm | housing-only | H | 18 | 12 | 4 / 8 | 3.03-3.58 |
| arm | housing-only | I | 28 | 25 | 13 / 12 | 3.02-4.18 |
| arm | Micro-Fit good parts | F | 3 | 3 | 3 / 0 | 3.02-3.23 |
| arm | Micro-Fit good parts | I | 3 | 3 | 3 / 0 | 3.02-3.22 |
| arm | Micro-Fit good parts | J | 1 | 1 | 1 / 0 | 3.10-3.10 |
