# Rig-protocol conditions and controllers in v0.2f_rig_predictions

From `trials.csv` under `results/v0.2f_rig_predictions` (base seed 20261201), the TEST_PROTOCOL conditions and controllers A, C, F, H, I, J only. Rates are k/n with Wilson 95% intervals. Cycle times are of successful trials (good parts) or of all trials (bad parts: time to reject).

## housing-only: pooled over the protocol conditions

| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|
| gantry | A | 61/200 (24.5-37.2%) | 2/200 (0.3-3.6%) | 137/200 (61.8-74.5%) | 4.32 / 4.32 |
| gantry | C | 194/200 (93.6-98.6%) | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 5.51 / 12.26 |
| gantry | F | 175/200 (82.2-91.4%) | 13/200 (3.8-10.8%) | 0/200 (0.0-1.9%) | 2.44 / 10.46 |
| gantry | H | 172/200 (80.5-90.1%) | 12/200 (3.5-10.2%) | 0/200 (0.0-1.9%) | 2.96 / 7.82 |
| gantry | I | 175/200 (82.2-91.4%) | 13/200 (3.8-10.8%) | 0/200 (0.0-1.9%) | 2.44 / 10.46 |
| gantry | J | 182/200 (86.2-94.2%) | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 4.85 / 16.61 |
| arm | A | 56/200 (22.2-34.6%) | 0/200 (0.0-1.9%) | 144/200 (65.4-77.8%) | 4.32 / 4.32 |
| arm | C | 190/200 (91.0-97.3%) | 0/200 (0.0-1.9%) | 2/200 (0.3-3.6%) | 8.51 / 20.20 |
| arm | F | 168/200 (78.3-88.4%) | 18/200 (5.8-13.8%) | 0/200 (0.0-1.9%) | 4.82 / 13.22 |
| arm | H | 162/200 (75.0-85.8%) | 11/200 (3.1-9.6%) | 4/200 (0.8-5.0%) | 4.82 / 10.50 |
| arm | I | 168/200 (78.3-88.4%) | 18/200 (5.8-13.8%) | 0/200 (0.0-1.9%) | 4.82 / 13.22 |
| arm | J | 177/200 (83.3-92.2%) | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 8.33 / 17.77 |

## Micro-Fit good parts: pooled over the protocol conditions

| Machine | Ctrl | Success | Bad units passed | Protective stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|
| gantry | A | 50/150 (26.3-41.2%) | 0/150 (0.0-2.5%) | 100/150 (58.8-73.7%) | 3.82 / 3.82 |
| gantry | C | 143/150 (90.7-97.7%) | 0/150 (0.0-2.5%) | 0/150 (0.0-2.5%) | 6.18 / 11.65 |
| gantry | F | 148/150 (95.3-99.6%) | 0/150 (0.0-2.5%) | 0/150 (0.0-2.5%) | 2.41 / 13.39 |
| gantry | H | 130/150 (80.3-91.2%) | 0/150 (0.0-2.5%) | 3/150 (0.7-5.7%) | 6.16 / 10.75 |
| gantry | I | 148/150 (95.3-99.6%) | 0/150 (0.0-2.5%) | 0/150 (0.0-2.5%) | 5.47 / 16.38 |
| gantry | J | 148/150 (95.3-99.6%) | 0/150 (0.0-2.5%) | 0/150 (0.0-2.5%) | 5.47 / 16.38 |
| arm | A | 50/150 (26.3-41.2%) | 0/150 (0.0-2.5%) | 100/150 (58.8-73.7%) | 3.79 / 3.79 |
| arm | C | 137/150 (85.7-94.9%) | 0/150 (0.0-2.5%) | 3/150 (0.7-5.7%) | 9.02 / 18.95 |
| arm | F | 141/150 (89.0-96.8%) | 1/150 (0.1-3.7%) | 0/150 (0.0-2.5%) | 4.69 / 15.67 |
| arm | H | 118/150 (71.4-84.5%) | 0/150 (0.0-2.5%) | 6/150 (1.8-8.5%) | 8.50 / 12.18 |
| arm | I | 140/150 (88.2-96.3%) | 1/150 (0.1-3.7%) | 1/150 (0.1-3.7%) | 8.63 / 17.98 |
| arm | J | 141/150 (89.0-96.8%) | 0/150 (0.0-2.5%) | 0/150 (0.0-2.5%) | 8.63 / 17.84 |

## Micro-Fit deliberately bad parts, pooled over the four defects

| Machine | Ctrl | Bad parts passed | Protective stops | Time to reject p50 / p95 (s) |
|---|---|---|---|---|
| gantry | A | 2/200 (0.3-3.6%) | 198/200 (96.4-99.7%) | 2.67 / 2.69 |
| gantry | C | 0/200 (0.0-1.9%) | 10/200 (2.7-9.0%) | 8.56 / 11.64 |
| gantry | F | 130/200 (58.2-71.3%) | 15/200 (4.6-12.0%) | 19.13 / 22.38 |
| gantry | H | 0/200 (0.0-1.9%) | 11/200 (3.1-9.6%) | 9.32 / 12.87 |
| gantry | I | 0/200 (0.0-1.9%) | 15/200 (4.6-12.0%) | 8.92 / 21.30 |
| gantry | J | 0/200 (0.0-1.9%) | 25/200 (8.6-17.8%) | 7.86 / 21.30 |
| arm | A | 2/200 (0.3-3.6%) | 198/200 (96.4-99.7%) | 2.63 / 2.64 |
| arm | C | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 13.00 / 16.32 |
| arm | F | 116/200 (51.1-64.6%) | 0/200 (0.0-1.9%) | 8.90 / 26.38 |
| arm | H | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 10.24 / 12.50 |
| arm | I | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 11.55 / 26.37 |
| arm | J | 0/200 (0.0-1.9%) | 0/200 (0.0-1.9%) | 12.11 / 26.37 |

## Per condition

| Machine | Condition | Ctrl | Success | Bad units or bad parts passed | Stops | Cycle p50 / p95 (s) |
|---|---|---|---|---|---|---|
| gantry | lateral_3mm | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| gantry | lateral_3mm | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 5.29 / 5.51 |
| gantry | lateral_3mm | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.43 / 2.45 |
| gantry | lateral_3mm | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.86 / 5.34 |
| gantry | lateral_3mm | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.43 / 2.45 |
| gantry | lateral_3mm | J | 48/50 (86.5-98.9%) | 0/50 (0.0-7.1%) | 0 | 4.77 / 4.94 |
| gantry | noise_1mm | A | 5/50 (4.3-21.4%) | 1/50 (0.4-10.5%) | 44 | 4.32 / 4.32 |
| gantry | noise_1mm | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 6.15 / 8.64 |
| gantry | noise_1mm | F | 49/50 (89.5-99.6%) | 1/50 (0.4-10.5%) | 0 | 2.52 / 7.98 |
| gantry | noise_1mm | H | 49/50 (89.5-99.6%) | 1/50 (0.4-10.5%) | 0 | 4.65 / 7.16 |
| gantry | noise_1mm | I | 49/50 (89.5-99.6%) | 1/50 (0.4-10.5%) | 0 | 2.52 / 7.98 |
| gantry | noise_1mm | J | 48/50 (86.5-98.9%) | 0/50 (0.0-7.1%) | 0 | 5.27 / 10.39 |
| gantry | noise_2mm | A | 6/50 (5.6-23.8%) | 1/50 (0.4-10.5%) | 43 | 4.32 / 4.32 |
| gantry | noise_2mm | C | 44/50 (76.2-94.4%) | 0/50 (0.0-7.1%) | 0 | 9.18 / 18.22 |
| gantry | noise_2mm | F | 26/50 (38.5-65.2%) | 12/50 (14.3-37.4%) | 0 | 6.82 / 19.71 |
| gantry | noise_2mm | H | 23/50 (33.0-59.6%) | 11/50 (12.8-35.2%) | 0 | 6.75 / 20.75 |
| gantry | noise_2mm | I | 26/50 (38.5-65.2%) | 12/50 (14.3-37.4%) | 0 | 6.82 / 19.71 |
| gantry | noise_2mm | J | 38/50 (62.6-85.7%) | 0/50 (0.0-7.1%) | 0 | 9.55 / 22.79 |
| gantry | nominal | A | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.32 / 4.32 |
| gantry | nominal | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 5.29 / 5.49 |
| gantry | nominal | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.43 / 2.45 |
| gantry | nominal | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.87 / 5.41 |
| gantry | nominal | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.43 / 2.45 |
| gantry | nominal | J | 48/50 (86.5-98.9%) | 0/50 (0.0-7.1%) | 0 | 4.77 / 4.92 |
| gantry | mf_moderate | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| gantry | mf_moderate | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 6.13 / 8.15 |
| gantry | mf_moderate | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.39 / 3.15 |
| gantry | mf_moderate | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 6.05 / 6.51 |
| gantry | mf_moderate | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 5.44 / 6.20 |
| gantry | mf_moderate | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 5.44 / 6.20 |
| gantry | mf_noise_1mm | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| gantry | mf_noise_1mm | C | 43/50 (73.8-93.0%) | 0/50 (0.0-7.1%) | 0 | 8.81 / 15.94 |
| gantry | mf_noise_1mm | F | 48/50 (86.5-98.9%) | 0/50 (0.0-7.1%) | 0 | 5.49 / 17.17 |
| gantry | mf_noise_1mm | H | 30/50 (46.2-72.4%) | 0/50 (0.0-7.1%) | 3 | 8.67 / 16.09 |
| gantry | mf_noise_1mm | I | 48/50 (86.5-98.9%) | 0/50 (0.0-7.1%) | 0 | 8.58 / 20.17 |
| gantry | mf_noise_1mm | J | 48/50 (86.5-98.9%) | 0/50 (0.0-7.1%) | 0 | 8.58 / 20.17 |
| gantry | mf_nominal | A | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 3.82 / 3.82 |
| gantry | mf_nominal | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 6.12 / 8.69 |
| gantry | mf_nominal | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 2.39 / 3.94 |
| gantry | mf_nominal | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 6.11 / 6.59 |
| gantry | mf_nominal | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 5.45 / 7.00 |
| gantry | mf_nominal | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 5.45 / 7.00 |
| gantry | mf_broken_latch | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| gantry | mf_broken_latch | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_broken_latch | F | 0/50 (0.0-7.1%) | 50/50 (92.9-100.0%) | 0 | nan / nan |
| gantry | mf_broken_latch | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_broken_latch | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_broken_latch | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_half_latched | A | 0/50 (0.0-7.1%) | 2/50 (1.1-13.5%) | 48 | nan / nan |
| gantry | mf_half_latched | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 8 | nan / nan |
| gantry | mf_half_latched | F | 0/50 (0.0-7.1%) | 35/50 (56.2-80.9%) | 15 | nan / nan |
| gantry | mf_half_latched | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 11 | nan / nan |
| gantry | mf_half_latched | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 15 | nan / nan |
| gantry | mf_half_latched | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 25 | nan / nan |
| gantry | mf_stubbed_terminal | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| gantry | mf_stubbed_terminal | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | F | 0/50 (0.0-7.1%) | 45/50 (78.6-95.7%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_stubbed_terminal | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| gantry | mf_wrong_polarization | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 2 | nan / nan |
| gantry | mf_wrong_polarization | F | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| gantry | mf_wrong_polarization | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | lateral_3mm | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| arm | lateral_3mm | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.09 / 8.52 |
| arm | lateral_3mm | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.75 / 7.08 |
| arm | lateral_3mm | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.75 / 6.93 |
| arm | lateral_3mm | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.75 / 7.08 |
| arm | lateral_3mm | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 7.96 / 10.29 |
| arm | noise_1mm | A | 2/50 (1.1-13.5%) | 0/50 (0.0-7.1%) | 48 | 4.32 / 4.32 |
| arm | noise_1mm | C | 49/50 (89.5-99.6%) | 0/50 (0.0-7.1%) | 0 | 10.47 / 14.20 |
| arm | noise_1mm | F | 49/50 (89.5-99.6%) | 1/50 (0.4-10.5%) | 0 | 6.40 / 11.83 |
| arm | noise_1mm | H | 48/50 (86.5-98.9%) | 2/50 (1.1-13.5%) | 0 | 5.83 / 10.47 |
| arm | noise_1mm | I | 49/50 (89.5-99.6%) | 1/50 (0.4-10.5%) | 0 | 6.40 / 11.83 |
| arm | noise_1mm | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 10.82 / 16.13 |
| arm | noise_2mm | A | 4/50 (3.2-18.8%) | 0/50 (0.0-7.1%) | 46 | 4.32 / 4.32 |
| arm | noise_2mm | C | 41/50 (69.2-90.2%) | 0/50 (0.0-7.1%) | 2 | 16.19 / 23.07 |
| arm | noise_2mm | F | 19/50 (25.9-51.8%) | 17/50 (22.4-47.8%) | 0 | 10.41 / 23.44 |
| arm | noise_2mm | H | 14/50 (17.5-41.7%) | 9/50 (9.8-30.8%) | 4 | 9.06 / 18.62 |
| arm | noise_2mm | I | 19/50 (25.9-51.8%) | 17/50 (22.4-47.8%) | 0 | 10.41 / 23.44 |
| arm | noise_2mm | J | 27/50 (40.4-67.0%) | 0/50 (0.0-7.1%) | 0 | 15.49 / 21.09 |
| arm | nominal | A | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.32 / 4.32 |
| arm | nominal | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.19 / 8.51 |
| arm | nominal | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.76 / 7.20 |
| arm | nominal | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.76 / 4.95 |
| arm | nominal | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.76 / 7.20 |
| arm | nominal | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.00 / 10.44 |
| arm | mf_moderate | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| arm | mf_moderate | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.97 / 12.49 |
| arm | mf_moderate | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.62 / 6.38 |
| arm | mf_moderate | H | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.38 / 8.99 |
| arm | mf_moderate | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.56 / 10.39 |
| arm | mf_moderate | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.56 / 10.39 |
| arm | mf_noise_1mm | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| arm | mf_noise_1mm | C | 37/50 (60.4-84.1%) | 0/50 (0.0-7.1%) | 3 | 13.19 / 23.31 |
| arm | mf_noise_1mm | F | 41/50 (69.2-90.2%) | 1/50 (0.4-10.5%) | 0 | 8.12 / 19.58 |
| arm | mf_noise_1mm | H | 19/50 (25.9-51.8%) | 0/50 (0.0-7.1%) | 5 | 10.87 / 17.46 |
| arm | mf_noise_1mm | I | 40/50 (67.0-88.8%) | 1/50 (0.4-10.5%) | 1 | 12.03 / 23.42 |
| arm | mf_noise_1mm | J | 41/50 (69.2-90.2%) | 0/50 (0.0-7.1%) | 0 | 12.07 / 23.42 |
| arm | mf_nominal | A | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 3.79 / 3.79 |
| arm | mf_nominal | C | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.98 / 12.54 |
| arm | mf_nominal | F | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 4.63 / 6.85 |
| arm | mf_nominal | H | 49/50 (89.5-99.6%) | 0/50 (0.0-7.1%) | 1 | 8.49 / 9.52 |
| arm | mf_nominal | I | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.59 / 10.82 |
| arm | mf_nominal | J | 50/50 (92.9-100.0%) | 0/50 (0.0-7.1%) | 0 | 8.59 / 10.82 |
| arm | mf_broken_latch | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| arm | mf_broken_latch | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_broken_latch | F | 0/50 (0.0-7.1%) | 50/50 (92.9-100.0%) | 0 | nan / nan |
| arm | mf_broken_latch | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_broken_latch | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_broken_latch | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_half_latched | A | 0/50 (0.0-7.1%) | 2/50 (1.1-13.5%) | 48 | nan / nan |
| arm | mf_half_latched | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_half_latched | F | 0/50 (0.0-7.1%) | 48/50 (86.5-98.9%) | 0 | nan / nan |
| arm | mf_half_latched | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_half_latched | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_half_latched | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| arm | mf_stubbed_terminal | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | F | 0/50 (0.0-7.1%) | 18/50 (24.1-49.9%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_stubbed_terminal | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_wrong_polarization | A | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 50 | nan / nan |
| arm | mf_wrong_polarization | C | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_wrong_polarization | F | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_wrong_polarization | H | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_wrong_polarization | I | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |
| arm | mf_wrong_polarization | J | 0/50 (0.0-7.1%) | 0/50 (0.0-7.1%) | 0 | nan / nan |

## Predicted differences between controllers (paired, same trials)

C-only / other-only: trials where only C (only the other) succeeded, or only C (only the other) passed a bad unit or bad part. Exact McNemar p. The difference is C minus the other, with its Newcombe paired 95% interval.

| Machine | Part | C vs | Metric | C / other | C-only / other-only | p | C - other (95% CI) |
|---|---|---|---|---|---|---|---|
| gantry | housing-only | I | success | 194 / 175 of 200 | 21 / 2 | 6.6e-05 | +9.5 (+5.1 to +14.6) points |
| gantry | housing-only | I | bad units | 0 / 13 of 200 | 0 / 13 | 0.00024 | -6.5 (-10.8 to -3.2) points |
| gantry | housing-only | J | success | 194 / 182 of 200 | 14 / 2 | 0.0042 | +6.0 (+2.2 to +10.5) points |
| gantry | housing-only | J | bad units | 0 / 0 of 200 | 0 / 0 | 1 | +0.0 (-1.9 to +1.9) points |
| gantry | housing-only | F | success | 194 / 175 of 200 | 21 / 2 | 6.6e-05 | +9.5 (+5.1 to +14.6) points |
| gantry | housing-only | F | bad units | 0 / 13 of 200 | 0 / 13 | 0.00024 | -6.5 (-10.8 to -3.2) points |
| gantry | Micro-Fit good parts | I | success | 143 / 148 of 150 | 0 / 5 | 0.062 | -3.3 (-7.6 to -0.4) points |
| gantry | Micro-Fit good parts | I | bad units | 0 / 0 of 150 | 0 / 0 | 1 | +0.0 (-2.5 to +2.5) points |
| gantry | Micro-Fit good parts | J | success | 143 / 148 of 150 | 0 / 5 | 0.062 | -3.3 (-7.6 to -0.4) points |
| gantry | Micro-Fit good parts | J | bad units | 0 / 0 of 150 | 0 / 0 | 1 | +0.0 (-2.5 to +2.5) points |
| gantry | Micro-Fit good parts | F | success | 143 / 148 of 150 | 0 / 5 | 0.062 | -3.3 (-7.6 to -0.4) points |
| gantry | Micro-Fit good parts | F | bad units | 0 / 0 of 150 | 0 / 0 | 1 | +0.0 (-2.5 to +2.5) points |
| gantry | Micro-Fit bad parts | I | bad parts passed | 0 / 0 of 200 | 0 / 0 | 1 | +0.0 (-1.9 to +1.9) points |
| gantry | Micro-Fit bad parts | J | bad parts passed | 0 / 0 of 200 | 0 / 0 | 1 | +0.0 (-1.9 to +1.9) points |
| gantry | Micro-Fit bad parts | F | bad parts passed | 0 / 130 of 200 | 0 / 130 | 1.5e-39 | -65.0 (-71.3 to -57.9) points |
| arm | housing-only | I | success | 190 / 168 of 200 | 25 / 3 | 2.7e-05 | +11.0 (+6.2 to +16.4) points |
| arm | housing-only | I | bad units | 0 / 18 of 200 | 0 / 18 | 7.6e-06 | -9.0 (-13.8 to -5.3) points |
| arm | housing-only | J | success | 190 / 177 of 200 | 16 / 3 | 0.0044 | +6.5 (+2.4 to +11.2) points |
| arm | housing-only | J | bad units | 0 / 0 of 200 | 0 / 0 | 1 | +0.0 (-1.9 to +1.9) points |
| arm | housing-only | F | success | 190 / 168 of 200 | 25 / 3 | 2.7e-05 | +11.0 (+6.2 to +16.4) points |
| arm | housing-only | F | bad units | 0 / 18 of 200 | 0 / 18 | 7.6e-06 | -9.0 (-13.8 to -5.3) points |
| arm | Micro-Fit good parts | I | success | 137 / 140 of 150 | 6 / 9 | 0.61 | -2.0 (-7.5 to +3.3) points |
| arm | Micro-Fit good parts | I | bad units | 0 / 1 of 150 | 0 / 1 | 1 | -0.7 (-3.7 to +1.9) points |
| arm | Micro-Fit good parts | J | success | 137 / 141 of 150 | 6 / 10 | 0.45 | -2.7 (-8.3 to +2.8) points |
| arm | Micro-Fit good parts | J | bad units | 0 / 0 of 150 | 0 / 0 | 1 | +0.0 (-2.5 to +2.5) points |
| arm | Micro-Fit good parts | F | success | 137 / 141 of 150 | 5 / 9 | 0.42 | -2.7 (-8.1 to +2.5) points |
| arm | Micro-Fit good parts | F | bad units | 0 / 1 of 150 | 0 / 1 | 1 | -0.7 (-3.7 to +1.9) points |
| arm | Micro-Fit bad parts | I | bad parts passed | 0 / 0 of 200 | 0 / 0 | 1 | +0.0 (-1.9 to +1.9) points |
| arm | Micro-Fit bad parts | J | bad parts passed | 0 / 0 of 200 | 0 / 0 | 1 | +0.0 (-1.9 to +1.9) points |
| arm | Micro-Fit bad parts | F | bad parts passed | 0 / 116 of 200 | 0 / 116 | 2.4e-35 | -58.0 (-64.6 to -50.8) points |

## Final pose of the bad units passed on good parts

What the rig's pose measurement has to resolve. Depth is from the socket mouth (housing-only full depth 15 mm, Micro-Fit 8 mm); the pass limits are depth >= full - 0.5 mm and abs(tilt), abs(yaw) <= 3 deg.

| Machine | Part | Ctrl | Bad units | At full depth | Of those, tilt > 3 deg / yaw > 3 deg | max of abs(tilt), abs(yaw), range (deg) |
|---|---|---|---|---|---|---|
| gantry | housing-only | A | 2 | 2 | 0 / 2 | 4.10-4.28 |
| gantry | housing-only | F | 13 | 11 | 4 / 7 | 3.00-4.65 |
| gantry | housing-only | H | 12 | 9 | 2 / 7 | 3.01-4.74 |
| gantry | housing-only | I | 13 | 11 | 4 / 7 | 3.00-4.65 |
| arm | housing-only | F | 18 | 16 | 9 / 7 | 3.00-4.52 |
| arm | housing-only | H | 11 | 7 | 4 / 3 | 3.01-3.87 |
| arm | housing-only | I | 18 | 16 | 9 / 7 | 3.00-4.52 |
| arm | Micro-Fit good parts | F | 1 | 1 | 1 / 0 | 3.22-3.22 |
| arm | Micro-Fit good parts | I | 1 | 1 | 1 / 0 | 3.22-3.22 |
