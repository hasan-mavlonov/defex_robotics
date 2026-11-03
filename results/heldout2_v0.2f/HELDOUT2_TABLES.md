# heldout2 tables: heldout2_v0.2f

From the per-trial rows. Cells: per machine, the whole suite and each family (two levels pooled). Every heldout2 trial is a good part.

## (a) C against the best fair baseline (D, E, F, H, I), and G against C

| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |
|---|---|---|---|---|---|
| gantry, all families | C vs best of D/E/F/H/I (F) | 94.0% vs 83.2% (+10.7 pts) | 63 / 20 | 2.4e-06 | C ahead of every fair baseline |
| gantry, all families | G vs C | 93.5% vs 94.0% (-0.5 pts) | 3 / 1 (C-only / G-only) | 0.62 | no measurable gain from G |
| gantry, h2_tilt_unseen | C vs best of D/E/F/H/I (E) | 100.0% vs 92.5% (+7.5 pts) | 6 / 0 | 0.031 | C ahead of every fair baseline |
| gantry, h2_tilt_unseen | G vs C | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| gantry, h2_yaw_unseen | C vs best of D/E/F/H/I (D) | 100.0% vs 37.5% (+62.5 pts) | 50 / 0 | <1e-6 | C ahead of every fair baseline |
| gantry, h2_yaw_unseen | G vs C | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| gantry, h2_ft_drift | C vs best of D/E/F/H/I (D) | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 | 1 | a fair baseline matches C: goes in the README headline; Hasan decides the pitch |
| gantry, h2_ft_drift | G vs C | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| gantry, h2_mf_tolerance | C vs best of D/E/F/H/I (F) | 95.0% vs 88.8% (+6.2 pts) | 6 / 1 | 0.12 | a fair baseline matches C: goes in the README headline; Hasan decides the pitch |
| gantry, h2_mf_tolerance | G vs C | 95.0% vs 95.0% (+0.0 pts) | 1 / 1 (C-only / G-only) | 1 | no measurable gain from G |
| gantry, h2_mf_grasp_unseen | C vs best of D/E/F/H/I (F) | 75.0% vs 98.8% (-23.8 pts) | 0 / 19 | 3.8e-06 | C below the best fair baseline, p < 0.05: goes in the README headline |
| gantry, h2_mf_grasp_unseen | G vs C | 72.5% vs 75.0% (-2.5 pts) | 2 / 0 (C-only / G-only) | 0.5 | no measurable gain from G |
| arm, all families | C vs best of D/E/F/H/I (F) | 88.8% vs 79.2% (+9.5 pts) | 74 / 36 | 0.00037 | C ahead of every fair baseline |
| arm, all families | G vs C | 89.2% vs 88.8% (+0.5 pts) | 2 / 4 (C-only / G-only) | 0.69 | no measurable gain from G |
| arm, h2_tilt_unseen | C vs best of D/E/F/H/I (E) | 100.0% vs 85.0% (+15.0 pts) | 12 / 0 | 0.00049 | C ahead of every fair baseline |
| arm, h2_tilt_unseen | G vs C | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| arm, h2_yaw_unseen | C vs best of D/E/F/H/I (F) | 97.5% vs 37.5% (+60.0 pts) | 48 / 0 | <1e-6 | C ahead of every fair baseline |
| arm, h2_yaw_unseen | G vs C | 100.0% vs 97.5% (+2.5 pts) | 0 / 2 (C-only / G-only) | 0.5 | no measurable gain from G |
| arm, h2_ft_drift | C vs best of D/E/F/H/I (D) | 76.2% vs 100.0% (-23.8 pts) | 0 / 19 | 3.8e-06 | C below the best fair baseline, p < 0.05: goes in the README headline |
| arm, h2_ft_drift | G vs C | 76.2% vs 76.2% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| arm, h2_mf_tolerance | C vs best of D/E/F/H/I (F) | 93.8% vs 80.0% (+13.7 pts) | 12 / 1 | 0.0034 | C ahead of every fair baseline |
| arm, h2_mf_tolerance | G vs C | 93.8% vs 93.8% (+0.0 pts) | 2 / 2 (C-only / G-only) | 1 | no measurable gain from G |
| arm, h2_mf_grasp_unseen | C vs best of D/E/F/H/I (F) | 76.2% vs 95.0% (-18.8 pts) | 2 / 17 | 0.00073 | C below the best fair baseline, p < 0.05: goes in the README headline |
| arm, h2_mf_grasp_unseen | G vs C | 76.2% vs 76.2% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |

## (b) Bad units passed on good-part trials, C against H and I

| Machine, cell | Comparison | Bad units, C vs other | C-only / other-only | McNemar p | Outcome |
|---|---|---|---|---|---|
| gantry, all families | C vs H | 0/400 (<= 1.0%) vs 59/400 | 0 / 59 | <1e-6 | C passes fewer than H |
| gantry, all families | C vs I | 0/400 (<= 1.0%) vs 57/400 | 0 / 57 | <1e-6 | C passes fewer than I |
| gantry, h2_tilt_unseen | C vs H | 0/80 (<= 4.6%) vs 12/80 | 0 / 12 | 0.00049 | C passes fewer than H |
| gantry, h2_tilt_unseen | C vs I | 0/80 (<= 4.6%) vs 7/80 | 0 / 7 | 0.016 | C passes fewer than I |
| gantry, h2_yaw_unseen | C vs H | 0/80 (<= 4.6%) vs 47/80 | 0 / 47 | <1e-6 | C passes fewer than H |
| gantry, h2_yaw_unseen | C vs I | 0/80 (<= 4.6%) vs 50/80 | 0 / 50 | <1e-6 | C passes fewer than I |
| gantry, h2_ft_drift | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_ft_drift | C vs I | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_tolerance | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_tolerance | C vs I | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_grasp_unseen | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_grasp_unseen | C vs I | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, all families | C vs H | 8/400 (<= 3.9%) vs 52/400 | 8 / 52 | <1e-6 | C passes fewer than H |
| arm, all families | C vs I | 8/400 (<= 3.9%) vs 63/400 | 7 / 62 | <1e-6 | C passes fewer than I |
| arm, h2_tilt_unseen | C vs H | 0/80 (<= 4.6%) vs 11/80 | 0 / 11 | 0.00098 | C passes fewer than H |
| arm, h2_tilt_unseen | C vs I | 0/80 (<= 4.6%) vs 12/80 | 0 / 12 | 0.00049 | C passes fewer than I |
| arm, h2_yaw_unseen | C vs H | 0/80 (<= 4.6%) vs 41/80 | 0 / 41 | <1e-6 | C passes fewer than H |
| arm, h2_yaw_unseen | C vs I | 0/80 (<= 4.6%) vs 49/80 | 0 / 49 | <1e-6 | C passes fewer than I |
| arm, h2_ft_drift | C vs H | 8/80 (<= 18.5%) vs 0/80 | 8 / 0 | 0.0078 | C passes more than H |
| arm, h2_ft_drift | C vs I | 8/80 (<= 18.5%) vs 1/80 | 7 / 0 | 0.016 | C passes more than I |
| arm, h2_mf_tolerance | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_mf_tolerance | C vs I | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_mf_grasp_unseen | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_mf_grasp_unseen | C vs I | 0/80 (<= 4.6%) vs 1/80 | 0 / 1 | 1 | no significant difference |

## (c) J against C and against I

| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |
|---|---|---|---|---|---|
| gantry, all families | J vs C, seated | 97.2% vs 94.0% (+3.3 pts) | 20 / 7 (J-only / C-only) | 0.019 | J ahead of C |
| gantry, all families | J vs C, bad units passed | 0/400 (<= 1.0%) vs 0/400 | 0 / 0 | 1 | no significant difference |
| gantry, all families | J vs I, seated | 97.2% vs 83.2% (+14.0 pts) | 57 / 1 (J-only / I-only) | <1e-6 | J ahead of I |
| gantry, all families | J vs I, bad units passed | 0/400 (<= 1.0%) vs 57/400 | 0 / 57 | <1e-6 | J passes fewer than I |
| gantry, h2_tilt_unseen | J vs C, seated | 98.8% vs 100.0% (-1.2 pts) | 0 / 1 (J-only / C-only) | 1 | J matches C |
| gantry, h2_tilt_unseen | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_tilt_unseen | J vs I, seated | 98.8% vs 91.2% (+7.5 pts) | 7 / 1 (J-only / I-only) | 0.07 | J matches I |
| gantry, h2_tilt_unseen | J vs I, bad units passed | 0/80 (<= 4.6%) vs 7/80 | 0 / 7 | 0.016 | J passes fewer than I |
| gantry, h2_yaw_unseen | J vs C, seated | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (J-only / C-only) | 1 | J matches C |
| gantry, h2_yaw_unseen | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_yaw_unseen | J vs I, seated | 100.0% vs 37.5% (+62.5 pts) | 50 / 0 (J-only / I-only) | <1e-6 | J ahead of I |
| gantry, h2_yaw_unseen | J vs I, bad units passed | 0/80 (<= 4.6%) vs 50/80 | 0 / 50 | <1e-6 | J passes fewer than I |
| gantry, h2_ft_drift | J vs C, seated | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (J-only / C-only) | 1 | J matches C |
| gantry, h2_ft_drift | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_ft_drift | J vs I, seated | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (J-only / I-only) | 1 | J matches I |
| gantry, h2_ft_drift | J vs I, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_tolerance | J vs C, seated | 88.8% vs 95.0% (-6.2 pts) | 1 / 6 (J-only / C-only) | 0.12 | J matches C |
| gantry, h2_mf_tolerance | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_tolerance | J vs I, seated | 88.8% vs 88.8% (+0.0 pts) | 0 / 0 (J-only / I-only) | 1 | J matches I |
| gantry, h2_mf_tolerance | J vs I, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_grasp_unseen | J vs C, seated | 98.8% vs 75.0% (+23.8 pts) | 19 / 0 (J-only / C-only) | 3.8e-06 | J ahead of C |
| gantry, h2_mf_grasp_unseen | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_mf_grasp_unseen | J vs I, seated | 98.8% vs 98.8% (+0.0 pts) | 0 / 0 (J-only / I-only) | 1 | J matches I |
| gantry, h2_mf_grasp_unseen | J vs I, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, all families | J vs C, seated | 91.0% vs 88.8% (+2.3 pts) | 27 / 18 (J-only / C-only) | 0.23 | J matches C |
| arm, all families | J vs C, bad units passed | 5/400 (<= 2.9%) vs 8/400 | 1 / 4 | 0.38 | no significant difference |
| arm, all families | J vs I, seated | 91.0% vs 79.2% (+11.8 pts) | 60 / 13 (J-only / I-only) | <1e-6 | J ahead of I |
| arm, all families | J vs I, bad units passed | 5/400 (<= 2.9%) vs 63/400 | 4 / 62 | <1e-6 | J passes fewer than I |
| arm, h2_tilt_unseen | J vs C, seated | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (J-only / C-only) | 1 | J matches C |
| arm, h2_tilt_unseen | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_tilt_unseen | J vs I, seated | 100.0% vs 85.0% (+15.0 pts) | 12 / 0 (J-only / I-only) | 0.00049 | J ahead of I |
| arm, h2_tilt_unseen | J vs I, bad units passed | 0/80 (<= 4.6%) vs 12/80 | 0 / 12 | 0.00049 | J passes fewer than I |
| arm, h2_yaw_unseen | J vs C, seated | 96.2% vs 97.5% (-1.2 pts) | 0 / 1 (J-only / C-only) | 1 | J matches C |
| arm, h2_yaw_unseen | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_yaw_unseen | J vs I, seated | 96.2% vs 37.5% (+58.8 pts) | 47 / 0 (J-only / I-only) | <1e-6 | J ahead of I |
| arm, h2_yaw_unseen | J vs I, bad units passed | 0/80 (<= 4.6%) vs 49/80 | 0 / 49 | <1e-6 | J passes fewer than I |
| arm, h2_ft_drift | J vs C, seated | 82.5% vs 76.2% (+6.2 pts) | 8 / 3 (J-only / C-only) | 0.23 | J matches C |
| arm, h2_ft_drift | J vs C, bad units passed | 5/80 (<= 13.8%) vs 8/80 | 1 / 4 | 0.38 | no significant difference |
| arm, h2_ft_drift | J vs I, seated | 82.5% vs 98.8% (-16.3 pts) | 0 / 13 (J-only / I-only) | 0.00024 | J below I |
| arm, h2_ft_drift | J vs I, bad units passed | 5/80 (<= 13.8%) vs 1/80 | 4 / 0 | 0.12 | no significant difference |
| arm, h2_mf_tolerance | J vs C, seated | 80.0% vs 93.8% (-13.7 pts) | 1 / 12 (J-only / C-only) | 0.0034 | J below C |
| arm, h2_mf_tolerance | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_mf_tolerance | J vs I, seated | 80.0% vs 80.0% (+0.0 pts) | 0 / 0 (J-only / I-only) | 1 | J matches I |
| arm, h2_mf_tolerance | J vs I, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_mf_grasp_unseen | J vs C, seated | 96.2% vs 76.2% (+20.0 pts) | 18 / 2 (J-only / C-only) | 0.0004 | J ahead of C |
| arm, h2_mf_grasp_unseen | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_mf_grasp_unseen | J vs I, seated | 96.2% vs 95.0% (+1.3 pts) | 1 / 0 (J-only / I-only) | 1 | J matches I |
| arm, h2_mf_grasp_unseen | J vs I, bad units passed | 0/80 (<= 4.6%) vs 1/80 | 0 / 1 | 1 | no significant difference |

## (d) Throughput: success, cycle p50 / p95 of successes (s), protective stops, bad units, good units per hour (0 s / 60 s per stop)

| Machine, cell | Controller | Success | p50 | p95 | Stops | Bad units | Good units/h |
|---|---|---|---|---|---|---|---|
| gantry, all families | A | 6.0% | 4.32 | 4.32 | 366 | 10 | 80 / 4 |
| gantry, all families | B | 62.8% | 4.31 | 4.33 | 89 | 60 | 585 / 131 |
| gantry, all families | E | 64.8% | 10.81 | 10.83 | 85 | 56 | 255 / 106 |
| gantry, all families | D | 79.8% | 2.96 | 5.40 | 8 | 59 | 681 / 530 |
| gantry, all families | F | 83.2% | 2.43 | 4.25 | 0 | 57 | 907 / 907 |
| gantry, all families | H | 79.8% | 5.34 | 7.23 | 8 | 59 | 544 / 443 |
| gantry, all families | I | 83.2% | 2.44 | 7.26 | 0 | 57 | 675 / 675 |
| gantry, all families | J | 97.2% | 5.24 | 7.34 | 0 | 0 | 596 / 596 |
| gantry, all families | C | 94.0% | 5.76 | 8.66 | 0 | 0 | 503 / 503 |
| gantry, all families | G | 93.5% | 5.76 | 8.67 | 0 | 0 | 497 / 497 |
| gantry, h2_tilt_unseen | A | 2.5% | 4.32 | 4.32 | 75 | 3 | 35 / 2 |
| gantry, h2_tilt_unseen | B | 87.5% | 4.32 | 4.33 | 0 | 10 | 730 / 730 |
| gantry, h2_tilt_unseen | E | 92.5% | 10.82 | 10.83 | 0 | 6 | 308 / 308 |
| gantry, h2_tilt_unseen | D | 83.8% | 2.85 | 6.71 | 0 | 12 | 770 / 770 |
| gantry, h2_tilt_unseen | F | 91.2% | 2.42 | 2.44 | 0 | 7 | 1280 / 1280 |
| gantry, h2_tilt_unseen | H | 83.8% | 2.85 | 6.71 | 0 | 12 | 770 / 770 |
| gantry, h2_tilt_unseen | I | 91.2% | 2.42 | 2.44 | 0 | 7 | 1280 / 1280 |
| gantry, h2_tilt_unseen | J | 98.8% | 5.25 | 5.40 | 0 | 0 | 654 / 654 |
| gantry, h2_tilt_unseen | C | 100.0% | 5.85 | 6.23 | 0 | 0 | 615 / 615 |
| gantry, h2_tilt_unseen | G | 100.0% | 5.85 | 6.23 | 0 | 0 | 615 / 615 |
| gantry, h2_yaw_unseen | A | 6.2% | 4.32 | 4.32 | 71 | 4 | 85 / 4 |
| gantry, h2_yaw_unseen | B | 37.5% | 4.31 | 4.33 | 0 | 50 | 313 / 313 |
| gantry, h2_yaw_unseen | E | 37.5% | 10.82 | 10.83 | 0 | 50 | 125 / 125 |
| gantry, h2_yaw_unseen | D | 37.5% | 2.88 | 5.48 | 0 | 47 | 296 / 296 |
| gantry, h2_yaw_unseen | F | 37.5% | 2.44 | 2.47 | 0 | 50 | 490 / 490 |
| gantry, h2_yaw_unseen | H | 37.5% | 2.88 | 5.48 | 0 | 47 | 296 / 296 |
| gantry, h2_yaw_unseen | I | 37.5% | 2.44 | 2.47 | 0 | 50 | 490 / 490 |
| gantry, h2_yaw_unseen | J | 100.0% | 4.45 | 4.77 | 0 | 0 | 759 / 759 |
| gantry, h2_yaw_unseen | C | 100.0% | 5.03 | 5.27 | 0 | 0 | 714 / 714 |
| gantry, h2_yaw_unseen | G | 100.0% | 5.03 | 5.27 | 0 | 0 | 714 / 714 |
| gantry, h2_ft_drift | A | 17.5% | 4.32 | 4.32 | 63 | 3 | 221 / 13 |
| gantry, h2_ft_drift | B | 100.0% | 4.31 | 4.33 | 0 | 0 | 835 / 835 |
| gantry, h2_ft_drift | E | 100.0% | 10.82 | 10.83 | 0 | 0 | 333 / 333 |
| gantry, h2_ft_drift | D | 100.0% | 2.87 | 5.33 | 0 | 0 | 1187 / 1187 |
| gantry, h2_ft_drift | F | 100.0% | 2.43 | 2.44 | 0 | 0 | 1479 / 1479 |
| gantry, h2_ft_drift | H | 100.0% | 2.87 | 5.33 | 0 | 0 | 1187 / 1187 |
| gantry, h2_ft_drift | I | 100.0% | 2.43 | 2.44 | 0 | 0 | 1479 / 1479 |
| gantry, h2_ft_drift | J | 100.0% | 4.75 | 4.91 | 0 | 0 | 756 / 756 |
| gantry, h2_ft_drift | C | 100.0% | 5.27 | 5.49 | 0 | 0 | 679 / 679 |
| gantry, h2_ft_drift | G | 100.0% | 5.27 | 5.49 | 0 | 0 | 679 / 679 |
| gantry, h2_mf_tolerance | A | 1.2% | 3.82 | 3.82 | 79 | 0 | 17 / 1 |
| gantry, h2_mf_tolerance | B | 38.8% | 3.81 | 3.83 | 49 | 0 | 448 / 35 |
| gantry, h2_mf_tolerance | E | 41.2% | 8.58 | 8.59 | 47 | 0 | 230 / 36 |
| gantry, h2_mf_tolerance | D | 83.8% | 3.23 | 4.19 | 4 | 0 | 495 / 332 |
| gantry, h2_mf_tolerance | F | 88.8% | 2.80 | 4.66 | 0 | 0 | 570 / 570 |
| gantry, h2_mf_tolerance | H | 83.8% | 6.27 | 7.36 | 4 | 0 | 350 / 259 |
| gantry, h2_mf_tolerance | I | 88.8% | 5.84 | 7.72 | 0 | 0 | 385 / 385 |
| gantry, h2_mf_tolerance | J | 88.8% | 5.84 | 7.69 | 0 | 0 | 385 / 385 |
| gantry, h2_mf_tolerance | C | 95.0% | 7.88 | 12.40 | 0 | 0 | 416 / 416 |
| gantry, h2_mf_tolerance | G | 95.0% | 7.89 | 11.04 | 0 | 0 | 419 / 419 |
| gantry, h2_mf_grasp_unseen | A | 2.5% | 3.82 | 3.82 | 78 | 0 | 33 / 1 |
| gantry, h2_mf_grasp_unseen | B | 50.0% | 3.81 | 3.82 | 40 | 0 | 554 / 54 |
| gantry, h2_mf_grasp_unseen | E | 52.5% | 8.58 | 8.59 | 38 | 0 | 275 / 53 |
| gantry, h2_mf_grasp_unseen | D | 93.8% | 3.21 | 4.47 | 4 | 0 | 968 / 520 |
| gantry, h2_mf_grasp_unseen | F | 98.8% | 2.40 | 5.39 | 0 | 0 | 1128 / 1128 |
| gantry, h2_mf_grasp_unseen | H | 93.8% | 6.20 | 7.48 | 4 | 0 | 540 / 365 |
| gantry, h2_mf_grasp_unseen | I | 98.8% | 5.49 | 8.42 | 0 | 0 | 579 / 579 |
| gantry, h2_mf_grasp_unseen | J | 98.8% | 5.49 | 8.42 | 0 | 0 | 579 / 579 |
| gantry, h2_mf_grasp_unseen | C | 75.0% | 6.14 | 8.31 | 0 | 0 | 292 / 292 |
| gantry, h2_mf_grasp_unseen | G | 72.5% | 6.13 | 8.89 | 0 | 0 | 275 / 275 |
| arm, all families | A | 4.0% | 4.32 | 4.32 | 382 | 2 | 56 / 2 |
| arm, all families | B | 58.2% | 4.31 | 4.33 | 109 | 58 | 551 / 104 |
| arm, all families | E | 66.5% | 4.07 | 4.09 | 71 | 63 | 657 / 168 |
| arm, all families | D | 71.5% | 4.75 | 6.58 | 5 | 59 | 442 / 392 |
| arm, all families | F | 79.2% | 4.73 | 7.72 | 2 | 63 | 463 / 442 |
| arm, all families | H | 71.5% | 4.85 | 9.85 | 6 | 52 | 368 / 326 |
| arm, all families | I | 79.2% | 4.84 | 11.55 | 2 | 63 | 378 / 364 |
| arm, all families | J | 91.0% | 9.01 | 12.26 | 2 | 5 | 311 / 303 |
| arm, all families | C | 88.8% | 9.52 | 14.75 | 3 | 8 | 280 / 269 |
| arm, all families | G | 89.2% | 9.53 | 14.03 | 4 | 8 | 284 / 269 |
| arm, h2_tilt_unseen | A | 1.2% | 4.32 | 4.32 | 77 | 2 | 18 / 1 |
| arm, h2_tilt_unseen | B | 85.0% | 4.32 | 4.33 | 0 | 12 | 709 / 709 |
| arm, h2_tilt_unseen | E | 85.0% | 4.08 | 4.09 | 0 | 12 | 750 / 750 |
| arm, h2_tilt_unseen | D | 83.8% | 4.73 | 6.81 | 0 | 11 | 584 / 584 |
| arm, h2_tilt_unseen | F | 85.0% | 4.70 | 4.83 | 0 | 12 | 617 / 617 |
| arm, h2_tilt_unseen | H | 83.8% | 4.73 | 6.81 | 0 | 11 | 584 / 584 |
| arm, h2_tilt_unseen | I | 85.0% | 4.70 | 4.83 | 0 | 12 | 617 / 617 |
| arm, h2_tilt_unseen | J | 100.0% | 9.54 | 13.71 | 0 | 0 | 364 / 364 |
| arm, h2_tilt_unseen | C | 100.0% | 9.85 | 11.06 | 0 | 0 | 360 / 360 |
| arm, h2_tilt_unseen | G | 100.0% | 9.85 | 11.06 | 0 | 0 | 360 / 360 |
| arm, h2_yaw_unseen | A | 5.0% | 4.32 | 4.32 | 76 | 0 | 72 / 3 |
| arm, h2_yaw_unseen | B | 33.8% | 4.31 | 4.33 | 12 | 41 | 295 / 93 |
| arm, h2_yaw_unseen | E | 36.2% | 4.08 | 4.09 | 0 | 51 | 320 / 320 |
| arm, h2_yaw_unseen | D | 36.2% | 4.78 | 4.93 | 0 | 41 | 240 / 240 |
| arm, h2_yaw_unseen | F | 37.5% | 4.78 | 9.26 | 0 | 49 | 227 / 227 |
| arm, h2_yaw_unseen | H | 36.2% | 4.78 | 4.93 | 0 | 41 | 240 / 240 |
| arm, h2_yaw_unseen | I | 37.5% | 4.78 | 9.26 | 0 | 49 | 227 / 227 |
| arm, h2_yaw_unseen | J | 96.2% | 10.28 | 14.78 | 0 | 0 | 312 / 312 |
| arm, h2_yaw_unseen | C | 97.5% | 9.73 | 10.21 | 0 | 0 | 356 / 356 |
| arm, h2_yaw_unseen | G | 100.0% | 9.73 | 10.31 | 0 | 0 | 368 / 368 |
| arm, h2_ft_drift | A | 11.2% | 4.32 | 4.32 | 71 | 0 | 154 / 7 |
| arm, h2_ft_drift | B | 98.8% | 4.31 | 4.33 | 0 | 1 | 824 / 824 |
| arm, h2_ft_drift | E | 100.0% | 4.08 | 4.09 | 0 | 0 | 883 / 883 |
| arm, h2_ft_drift | D | 100.0% | 4.76 | 4.92 | 0 | 0 | 748 / 748 |
| arm, h2_ft_drift | F | 98.8% | 4.75 | 4.87 | 0 | 1 | 741 / 741 |
| arm, h2_ft_drift | H | 100.0% | 4.76 | 4.92 | 0 | 0 | 748 / 748 |
| arm, h2_ft_drift | I | 98.8% | 4.75 | 4.87 | 0 | 1 | 741 / 741 |
| arm, h2_ft_drift | J | 82.5% | 7.83 | 8.25 | 0 | 5 | 307 / 307 |
| arm, h2_ft_drift | C | 76.2% | 8.09 | 17.87 | 2 | 8 | 244 / 216 |
| arm, h2_ft_drift | G | 76.2% | 8.09 | 17.87 | 2 | 8 | 244 / 216 |
| arm, h2_mf_tolerance | A | 0.0% | nan | nan | 80 | 0 | 0 / 0 |
| arm, h2_mf_tolerance | B | 33.8% | 3.78 | 3.80 | 52 | 1 | 396 / 29 |
| arm, h2_mf_tolerance | E | 52.5% | 3.48 | 3.50 | 38 | 0 | 641 / 60 |
| arm, h2_mf_tolerance | D | 68.8% | 4.82 | 6.56 | 5 | 2 | 321 / 216 |
| arm, h2_mf_tolerance | F | 80.0% | 4.80 | 8.07 | 0 | 0 | 301 / 301 |
| arm, h2_mf_tolerance | H | 68.8% | 8.73 | 10.44 | 6 | 0 | 236 / 165 |
| arm, h2_mf_tolerance | I | 80.0% | 8.73 | 11.96 | 0 | 0 | 226 / 226 |
| arm, h2_mf_tolerance | J | 80.0% | 8.73 | 11.96 | 0 | 0 | 226 / 226 |
| arm, h2_mf_tolerance | C | 93.8% | 10.11 | 16.36 | 1 | 0 | 279 / 263 |
| arm, h2_mf_tolerance | G | 93.8% | 10.11 | 15.97 | 2 | 0 | 287 / 254 |
| arm, h2_mf_grasp_unseen | A | 2.5% | 3.79 | 3.79 | 78 | 0 | 34 / 1 |
| arm, h2_mf_grasp_unseen | B | 40.0% | 3.78 | 3.79 | 45 | 3 | 450 / 39 |
| arm, h2_mf_grasp_unseen | E | 58.8% | 3.48 | 3.50 | 33 | 0 | 698 / 76 |
| arm, h2_mf_grasp_unseen | D | 68.8% | 4.60 | 7.51 | 0 | 5 | 415 / 415 |
| arm, h2_mf_grasp_unseen | F | 95.0% | 4.68 | 7.78 | 2 | 1 | 624 / 490 |
| arm, h2_mf_grasp_unseen | H | 68.8% | 8.46 | 11.24 | 0 | 0 | 274 / 274 |
| arm, h2_mf_grasp_unseen | I | 95.0% | 8.61 | 11.67 | 2 | 1 | 370 / 318 |
| arm, h2_mf_grasp_unseen | J | 96.2% | 8.59 | 11.71 | 2 | 0 | 375 / 323 |
| arm, h2_mf_grasp_unseen | C | 76.2% | 8.94 | 12.60 | 0 | 0 | 197 / 197 |
| arm, h2_mf_grasp_unseen | G | 76.2% | 8.94 | 12.60 | 0 | 0 | 198 / 198 |

## (e) Per-condition success table per machine

### gantry, h2_tilt_unseen_2deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 1 | 0 | 37 | 4.32/4.32/4.32 | 69 / 3 | 30.5 | 0.22 | 38 / 0 (<1e-6) |
| B correction | 95.0% (83.5-98.6) | 2 | 0 | 0 | 4.32/4.33/4.33 | 792 / 792 | 12.6 | 0.09 | 2 / 0 (0.5) |
| E correction_rcc | 97.5% (87.1-99.6) | 1 | 0 | 0 | 10.82/10.83/10.83 | 324 / 324 | 16.7 | 0.12 | 1 / 0 (1) |
| D spiral | 95.0% (83.5-98.6) | 2 | 0 | 0 | 2.85/5.66/7.84 | 967 / 967 | 13.7 | 0.06 | 2 / 0 (0.5) |
| F spiral_rcc | 97.5% (87.1-99.6) | 1 | 0 | 0 | 2.43/2.43/2.44 | 1447 / 1447 | 12.6 | 0.07 | 1 / 0 (1) |
| H spiral_pull | 95.0% (83.5-98.6) | 2 | 0 | 0 | 2.85/5.66/7.84 | 967 / 967 | 13.7 | 0.06 | 2 / 0 (0.5) |
| I spiral_rcc_pull | 97.5% (87.1-99.6) | 1 | 0 | 0 | 2.43/2.43/2.44 | 1447 / 1447 | 12.6 | 0.07 | 1 / 0 (1) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.17/5.37/5.40 | 695 / 695 | 12.6 | 0.08 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.71/5.99/6.13 | 627 / 627 | 13.3 | 0.29 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.71/5.99/6.13 | 627 / 627 | 13.3 | 0.29 | 0 / 0 (1) |

### gantry, h2_tilt_unseen_3deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 2 | 0 | 38 | n/a | 0 / 0 | 31.0 | 0.22 | 40 / 0 (<1e-6) |
| B correction | 80.0% (65.2-89.5) | 8 | 0 | 0 | 4.32/4.33/4.33 | 667 / 667 | 15.0 | 0.10 | 8 / 0 (0.0078) |
| E correction_rcc | 87.5% (73.9-94.5) | 5 | 0 | 0 | 10.82/10.83/10.84 | 291 / 291 | 18.0 | 0.13 | 5 / 0 (0.062) |
| D spiral | 72.5% (57.2-83.9) | 10 | 0 | 0 | 2.91/6.86/7.62 | 608 / 608 | 13.6 | 0.06 | 11 / 0 (0.00098) |
| F spiral_rcc | 85.0% (70.9-92.9) | 6 | 0 | 0 | 2.42/2.45/3.08 | 1130 / 1130 | 12.4 | 0.07 | 6 / 0 (0.031) |
| H spiral_pull | 72.5% (57.2-83.9) | 10 | 0 | 0 | 2.91/6.86/7.62 | 608 / 608 | 13.6 | 0.06 | 11 / 0 (0.00098) |
| I spiral_rcc_pull | 85.0% (70.9-92.9) | 6 | 0 | 0 | 2.42/2.45/3.08 | 1130 / 1130 | 12.4 | 0.07 | 6 / 0 (0.031) |
| J spiral_rcc_verify | 97.5% (87.1-99.6) | 0 | 0 | 0 | 5.30/6.61/10.85 | 617 / 617 | 12.4 | 0.09 | 1 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.93/6.31/6.34 | 603 / 603 | 12.7 | 0.29 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.93/6.31/6.34 | 603 / 603 | 12.7 | 0.29 | 0 / 0 (1) |

### gantry, h2_yaw_unseen_2.5deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 7.5% (2.6-19.9) | 3 | 0 | 34 | 4.32/4.32/4.32 | 99 / 5 | 30.5 | 0.21 | 37 / 0 (<1e-6) |
| B correction | 72.5% (57.2-83.9) | 11 | 0 | 0 | 4.31/4.33/4.33 | 605 / 605 | 13.8 | 0.09 | 11 / 0 (0.00098) |
| E correction_rcc | 72.5% (57.2-83.9) | 11 | 0 | 0 | 10.82/10.83/10.83 | 241 / 241 | 13.4 | 0.08 | 11 / 0 (0.00098) |
| D spiral | 72.5% (57.2-83.9) | 11 | 0 | 0 | 2.88/5.48/5.60 | 695 / 695 | 13.5 | 0.06 | 11 / 0 (0.00098) |
| F spiral_rcc | 72.5% (57.2-83.9) | 11 | 0 | 0 | 2.44/2.47/2.49 | 1069 / 1069 | 13.4 | 0.06 | 11 / 0 (0.00098) |
| H spiral_pull | 72.5% (57.2-83.9) | 11 | 0 | 0 | 2.88/5.48/5.60 | 695 / 695 | 13.5 | 0.06 | 11 / 0 (0.00098) |
| I spiral_rcc_pull | 72.5% (57.2-83.9) | 11 | 0 | 0 | 2.44/2.47/2.49 | 1069 / 1069 | 13.4 | 0.06 | 11 / 0 (0.00098) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.52/4.72/4.83 | 795 / 795 | 13.4 | 0.08 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.13/5.31/5.38 | 702 / 702 | 12.3 | 0.29 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.13/5.31/5.38 | 702 / 702 | 12.3 | 0.29 | 0 / 0 (1) |

### gantry, h2_yaw_unseen_4deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 1 | 0 | 37 | 4.32/4.32/4.32 | 69 / 3 | 30.5 | 0.22 | 38 / 0 (<1e-6) |
| B correction | 2.5% (0.4-12.9) | 39 | 0 | 0 | 4.32/4.32/4.32 | 21 / 21 | 18.4 | 0.15 | 39 / 0 (<1e-6) |
| E correction_rcc | 2.5% (0.4-12.9) | 39 | 0 | 0 | 10.82/10.82/10.82 | 8 / 8 | 15.7 | 0.09 | 39 / 0 (<1e-6) |
| D spiral | 2.5% (0.4-12.9) | 36 | 0 | 0 | 2.83/2.83/2.83 | 17 / 17 | 13.7 | 0.07 | 39 / 0 (<1e-6) |
| F spiral_rcc | 2.5% (0.4-12.9) | 39 | 0 | 0 | 2.43/2.43/2.43 | 29 / 29 | 12.7 | 0.07 | 39 / 0 (<1e-6) |
| H spiral_pull | 2.5% (0.4-12.9) | 36 | 0 | 0 | 2.83/2.83/2.83 | 17 / 17 | 13.7 | 0.07 | 39 / 0 (<1e-6) |
| I spiral_rcc_pull | 2.5% (0.4-12.9) | 39 | 0 | 0 | 2.43/2.43/2.43 | 29 / 29 | 12.7 | 0.07 | 39 / 0 (<1e-6) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.35/5.53/17.36 | 725 / 725 | 12.7 | 0.08 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.94/5.14/5.16 | 727 / 727 | 13.2 | 0.29 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.94/5.14/5.16 | 727 / 727 | 13.2 | 0.29 | 0 / 0 (1) |

### gantry, h2_ft_drift_0.1

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 20.0% (10.5-34.8) | 0 | 0 | 32 | 4.32/4.32/4.32 | 255 / 14 | 30.6 | 0.22 | 32 / 0 (<1e-6) |
| B correction | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.32/4.33/4.33 | 834 / 834 | 10.8 | 0.08 | 0 / 0 (1) |
| E correction_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 10.82/10.83/10.83 | 333 / 333 | 15.1 | 0.10 | 0 / 0 (1) |
| D spiral | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.86/3.09/5.41 | 1204 / 1204 | 9.7 | 0.05 | 0 / 0 (1) |
| F spiral_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.43/2.44/2.44 | 1480 / 1480 | 13.5 | 0.07 | 0 / 0 (1) |
| H spiral_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.86/3.09/5.41 | 1204 / 1204 | 9.7 | 0.05 | 0 / 0 (1) |
| I spiral_rcc_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.43/2.44/2.44 | 1480 / 1480 | 13.5 | 0.07 | 0 / 0 (1) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.75/4.90/4.99 | 756 / 756 | 13.5 | 0.08 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.27/5.41/5.51 | 681 / 681 | 11.0 | 0.29 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.27/5.41/5.51 | 681 / 681 | 11.0 | 0.29 | 0 / 0 (1) |

### gantry, h2_ft_drift_0.3

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 15.0% (7.1-29.1) | 3 | 0 | 31 | 4.32/4.32/4.32 | 188 / 11 | 30.9 | 0.24 | 34 / 0 (<1e-6) |
| B correction | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.31/4.32/4.33 | 835 / 835 | 10.9 | 0.09 | 0 / 0 (1) |
| E correction_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 10.82/10.83/10.83 | 333 / 333 | 15.1 | 0.15 | 0 / 0 (1) |
| D spiral | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.87/5.38/5.40 | 1171 / 1171 | 9.4 | 0.05 | 0 / 0 (1) |
| F spiral_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.43/2.44/2.45 | 1479 / 1479 | 12.7 | 0.08 | 0 / 0 (1) |
| H spiral_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.87/5.38/5.40 | 1171 / 1171 | 9.4 | 0.05 | 0 / 0 (1) |
| I spiral_rcc_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.43/2.44/2.45 | 1479 / 1479 | 12.7 | 0.08 | 0 / 0 (1) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.75/4.93/4.95 | 756 / 756 | 12.7 | 0.09 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.28/5.63/5.70 | 678 / 678 | 10.9 | 0.30 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.28/5.63/5.70 | 678 / 678 | 10.9 | 0.30 | 0 / 0 (1) |

### gantry, h2_mf_tol_0.10mm

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 2.5% (0.4-12.9) | 0 | 0 | 39 | 3.82/3.82/3.82 | 33 / 1 | 48.5 | 0.23 | 39 / 0 (<1e-6) |
| B correction | 55.0% (39.8-69.3) | 0 | 0 | 18 | 3.82/3.83/3.83 | 599 / 65 | 48.4 | 0.20 | 18 / 0 (7.6e-06) |
| E correction_rcc | 57.5% (42.2-71.5) | 0 | 0 | 17 | 8.58/8.59/8.59 | 294 / 64 | 48.1 | 0.17 | 17 / 0 (1.5e-05) |
| D spiral | 95.0% (83.5-98.6) | 0 | 0 | 1 | 3.12/3.81/4.27 | 895 / 643 | 22.5 | 0.11 | 2 / 0 (0.5) |
| F spiral_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.40/4.04/4.67 | 1254 / 1254 | 21.8 | 0.07 | 0 / 0 (1) |
| H spiral_pull | 95.0% (83.5-98.6) | 0 | 0 | 1 | 6.13/6.83/7.33 | 510 / 417 | 22.5 | 0.11 | 2 / 0 (0.5) |
| I spiral_rcc_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.46/7.09/7.75 | 609 / 609 | 21.8 | 0.07 | 0 / 0 (1) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.46/7.09/7.75 | 609 / 609 | 21.8 | 0.07 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 6.16/8.65/9.91 | 507 / 507 | 33.5 | 0.16 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 6.16/8.72/11.71 | 499 / 499 | 33.5 | 0.16 | 0 / 0 (1) |

### gantry, h2_mf_tol_0.05mm

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 0 | 0 | 40 | n/a | 0 / 0 | 48.5 | 0.23 | 36 / 0 (<1e-6) |
| B correction | 22.5% (12.3-37.5) | 0 | 0 | 31 | 3.81/3.82/3.83 | 276 / 16 | 48.5 | 0.24 | 27 / 0 (<1e-6) |
| E correction_rcc | 25.0% (14.2-40.2) | 0 | 0 | 30 | 8.58/8.59/8.59 | 154 / 18 | 48.1 | 0.18 | 26 / 0 (<1e-6) |
| D spiral | 72.5% (57.2-83.9) | 0 | 0 | 3 | 3.31/4.49/8.95 | 312 / 203 | 24.8 | 0.24 | 8 / 1 (0.039) |
| F spiral_rcc | 77.5% (62.5-87.7) | 0 | 0 | 0 | 3.01/4.80/5.72 | 334 / 334 | 22.0 | 0.09 | 6 / 1 (0.12) |
| H spiral_pull | 72.5% (57.2-83.9) | 0 | 0 | 3 | 6.33/7.59/12.11 | 247 / 173 | 24.9 | 0.31 | 8 / 1 (0.039) |
| I spiral_rcc_pull | 77.5% (62.5-87.7) | 0 | 0 | 0 | 6.03/7.84/8.80 | 261 / 261 | 22.0 | 0.09 | 6 / 1 (0.12) |
| J spiral_rcc_verify | 77.5% (62.5-87.7) | 0 | 0 | 0 | 6.04/7.81/8.80 | 261 / 261 | 22.0 | 0.09 | 6 / 1 (0.12) |
| C adaptive | 90.0% (76.9-96.0) | 0 | 0 | 0 | 8.02/12.61/13.29 | 348 / 348 | 33.6 | 0.20 | reference |
| G adaptive_learned | 90.0% (76.9-96.0) | 0 | 0 | 0 | 8.08/11.92/15.34 | 355 / 355 | 33.6 | 0.16 | 1 / 1 (1) |

### gantry, h2_mf_grasp_unseen_1deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 0 | 0 | 38 | 3.82/3.82/3.82 | 66 / 3 | 48.5 | 0.23 | 36 / 0 (<1e-6) |
| B correction | 62.5% (47.0-75.8) | 0 | 0 | 15 | 3.82/3.83/3.83 | 664 / 87 | 48.4 | 0.24 | 13 / 0 (0.00024) |
| E correction_rcc | 65.0% (49.5-77.9) | 0 | 0 | 14 | 8.58/8.59/8.59 | 319 / 83 | 48.1 | 0.20 | 12 / 0 (0.00049) |
| D spiral | 95.0% (83.5-98.6) | 0 | 0 | 2 | 3.16/3.78/4.04 | 1058 / 549 | 27.2 | 0.31 | 2 / 2 (1) |
| F spiral_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 2.39/4.28/4.99 | 1271 / 1271 | 21.0 | 0.09 | 0 / 2 (0.5) |
| H spiral_pull | 95.0% (83.5-98.6) | 0 | 0 | 2 | 6.13/6.73/7.03 | 565 / 378 | 27.2 | 0.31 | 2 / 2 (1) |
| I spiral_rcc_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.44/7.30/8.01 | 614 / 614 | 21.1 | 0.09 | 0 / 2 (0.5) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 5.43/7.30/8.01 | 614 / 614 | 21.0 | 0.09 | 0 / 2 (0.5) |
| C adaptive | 95.0% (83.5-98.6) | 0 | 0 | 0 | 6.15/8.35/8.73 | 471 / 471 | 33.5 | 0.16 | reference |
| G adaptive_learned | 90.0% (76.9-96.0) | 0 | 0 | 0 | 6.15/8.97/9.70 | 416 / 416 | 33.5 | 0.17 | 2 / 0 (0.5) |

### gantry, h2_mf_grasp_unseen_2deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 0 | 0 | 40 | n/a | 0 / 0 | 48.5 | 0.24 | 22 / 0 (<1e-6) |
| B correction | 37.5% (24.2-53.0) | 0 | 0 | 25 | 3.81/3.82/3.82 | 434 / 33 | 48.5 | 0.25 | 7 / 0 (0.016) |
| E correction_rcc | 40.0% (26.3-55.4) | 0 | 0 | 24 | 8.57/8.58/8.58 | 224 / 34 | 48.1 | 0.21 | 6 / 0 (0.031) |
| D spiral | 92.5% (80.1-97.4) | 0 | 0 | 2 | 3.51/4.76/6.19 | 890 / 494 | 26.7 | 0.35 | 1 / 16 (0.00027) |
| F spiral_rcc | 97.5% (87.1-99.6) | 0 | 0 | 0 | 3.33/5.69/6.78 | 1011 / 1011 | 21.6 | 0.12 | 0 / 17 (1.5e-05) |
| H spiral_pull | 92.5% (80.1-97.4) | 0 | 0 | 2 | 6.33/7.72/8.76 | 516 / 352 | 28.6 | 0.35 | 1 / 16 (0.00027) |
| I spiral_rcc_pull | 97.5% (87.1-99.6) | 0 | 0 | 0 | 6.38/8.72/9.80 | 547 / 547 | 21.6 | 0.12 | 0 / 17 (1.5e-05) |
| J spiral_rcc_verify | 97.5% (87.1-99.6) | 0 | 0 | 0 | 6.38/8.73/9.74 | 548 / 548 | 21.6 | 0.12 | 0 / 17 (1.5e-05) |
| C adaptive | 55.0% (39.8-69.3) | 0 | 0 | 0 | 6.12/7.94/12.23 | 176 / 176 | 33.5 | 0.27 | reference |
| G adaptive_learned | 55.0% (39.8-69.3) | 0 | 0 | 0 | 6.12/7.96/12.24 | 177 / 177 | 33.5 | 0.27 | 0 / 0 (1) |

### arm, h2_tilt_unseen_2deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 2.5% (0.4-12.9) | 1 | 0 | 38 | 4.32/4.32/4.32 | 36 / 2 | 67.0 | 0.22 | 39 / 0 (<1e-6) |
| B correction | 95.0% (83.5-98.6) | 2 | 0 | 0 | 4.32/4.33/4.33 | 792 / 792 | 43.0 | 0.16 | 2 / 0 (0.5) |
| E correction_rcc | 95.0% (83.5-98.6) | 2 | 0 | 0 | 4.08/4.09/4.09 | 838 / 838 | 18.0 | 0.13 | 2 / 0 (0.5) |
| D spiral | 92.5% (80.1-97.4) | 2 | 0 | 0 | 4.71/8.47/8.85 | 645 / 645 | 44.9 | 0.15 | 3 / 0 (0.25) |
| F spiral_rcc | 95.0% (83.5-98.6) | 2 | 0 | 0 | 4.70/4.79/4.83 | 729 / 729 | 11.4 | 0.09 | 2 / 0 (0.5) |
| H spiral_pull | 92.5% (80.1-97.4) | 2 | 0 | 0 | 4.71/8.47/8.85 | 645 / 645 | 44.9 | 0.15 | 3 / 0 (0.25) |
| I spiral_rcc_pull | 95.0% (83.5-98.6) | 2 | 0 | 0 | 4.70/4.79/4.83 | 729 / 729 | 11.4 | 0.09 | 2 / 0 (0.5) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.07/9.83/10.10 | 391 / 391 | 11.4 | 0.09 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.43/10.27/10.40 | 382 / 382 | 36.9 | 0.13 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.43/10.27/10.40 | 382 / 382 | 36.9 | 0.13 | 0 / 0 (1) |

### arm, h2_tilt_unseen_3deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 1 | 0 | 39 | n/a | 0 / 0 | 71.2 | 0.22 | 40 / 0 (<1e-6) |
| B correction | 75.0% (59.8-85.8) | 10 | 0 | 0 | 4.32/4.33/4.33 | 626 / 626 | 48.8 | 0.33 | 10 / 0 (0.002) |
| E correction_rcc | 75.0% (59.8-85.8) | 10 | 0 | 0 | 4.08/4.09/4.10 | 662 / 662 | 19.2 | 0.14 | 10 / 0 (0.002) |
| D spiral | 75.0% (59.8-85.8) | 9 | 0 | 0 | 4.74/6.32/6.81 | 523 / 523 | 43.5 | 0.19 | 10 / 0 (0.002) |
| F spiral_rcc | 75.0% (59.8-85.8) | 10 | 0 | 0 | 4.70/7.03/9.12 | 516 / 516 | 14.4 | 0.10 | 10 / 0 (0.002) |
| H spiral_pull | 75.0% (59.8-85.8) | 9 | 0 | 0 | 4.74/6.32/6.81 | 523 / 523 | 43.5 | 0.19 | 10 / 0 (0.002) |
| I spiral_rcc_pull | 75.0% (59.8-85.8) | 10 | 0 | 0 | 4.70/7.03/9.12 | 516 / 516 | 14.4 | 0.10 | 10 / 0 (0.002) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 10.08/14.96/15.03 | 340 / 340 | 14.4 | 0.10 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 10.37/11.82/15.34 | 341 / 341 | 33.2 | 0.13 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 10.37/11.82/15.34 | 341 / 341 | 33.2 | 0.13 | 0 / 0 (1) |

### arm, h2_yaw_unseen_2.5deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 0 | 0 | 38 | 4.32/4.32/4.32 | 72 / 3 | 67.6 | 0.22 | 38 / 0 (<1e-6) |
| B correction | 65.0% (49.5-77.9) | 12 | 0 | 2 | 4.31/4.33/4.33 | 554 / 324 | 39.7 | 0.18 | 14 / 0 (0.00012) |
| E correction_rcc | 70.0% (54.6-81.9) | 12 | 0 | 0 | 4.08/4.09/4.09 | 619 / 619 | 14.1 | 0.10 | 12 / 0 (0.00049) |
| D spiral | 70.0% (54.6-81.9) | 12 | 0 | 0 | 4.78/4.93/4.95 | 522 / 522 | 49.9 | 0.17 | 12 / 0 (0.00049) |
| F spiral_rcc | 72.5% (57.2-83.9) | 11 | 0 | 0 | 4.78/9.26/9.37 | 479 / 479 | 15.1 | 0.09 | 11 / 0 (0.00098) |
| H spiral_pull | 70.0% (54.6-81.9) | 12 | 0 | 0 | 4.78/4.93/4.95 | 522 / 522 | 49.9 | 0.17 | 12 / 0 (0.00049) |
| I spiral_rcc_pull | 72.5% (57.2-83.9) | 11 | 0 | 0 | 4.78/9.26/9.37 | 479 / 479 | 15.1 | 0.09 | 11 / 0 (0.00098) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 10.25/14.52/14.88 | 360 / 360 | 15.1 | 0.09 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.73/10.17/10.32 | 382 / 382 | 31.6 | 0.09 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.73/10.17/10.32 | 382 / 382 | 31.6 | 0.09 | 0 / 0 (1) |

### arm, h2_yaw_unseen_4deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 0 | 0 | 38 | 4.32/4.32/4.32 | 72 / 3 | 66.3 | 0.22 | 37 / 1 (<1e-6) |
| B correction | 2.5% (0.4-12.9) | 29 | 0 | 10 | 4.32/4.32/4.32 | 22 / 5 | 43.9 | 0.60 | 37 / 0 (<1e-6) |
| E correction_rcc | 2.5% (0.4-12.9) | 39 | 0 | 0 | 4.08/4.08/4.08 | 22 / 22 | 17.3 | 0.12 | 37 / 0 (<1e-6) |
| D spiral | 2.5% (0.4-12.9) | 29 | 0 | 0 | 4.69/4.69/4.69 | 15 / 15 | 54.7 | 0.37 | 37 / 0 (<1e-6) |
| F spiral_rcc | 2.5% (0.4-12.9) | 38 | 0 | 0 | 4.69/4.69/4.69 | 14 / 14 | 15.1 | 0.10 | 37 / 0 (<1e-6) |
| H spiral_pull | 2.5% (0.4-12.9) | 29 | 0 | 0 | 4.69/4.69/4.69 | 15 / 15 | 54.7 | 0.37 | 37 / 0 (<1e-6) |
| I spiral_rcc_pull | 2.5% (0.4-12.9) | 38 | 0 | 0 | 4.69/4.69/4.69 | 14 / 14 | 15.1 | 0.10 | 37 / 0 (<1e-6) |
| J spiral_rcc_verify | 92.5% (80.1-97.4) | 0 | 0 | 0 | 10.35/14.82/15.06 | 273 / 273 | 15.1 | 0.10 | 1 / 0 (1) |
| C adaptive | 95.0% (83.5-98.6) | 0 | 0 | 0 | 9.73/10.21/10.40 | 331 / 331 | 31.9 | 0.21 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.75/10.65/17.99 | 355 / 355 | 31.9 | 0.21 | 0 / 2 (0.5) |

### arm, h2_ft_drift_0.1

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 17.5% (8.7-32.0) | 0 | 0 | 33 | 4.32/4.32/4.32 | 230 / 12 | 66.8 | 0.22 | 33 / 0 (<1e-6) |
| B correction | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.32/4.33/4.33 | 834 / 834 | 40.6 | 0.11 | 0 / 0 (1) |
| E correction_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.08/4.09/4.09 | 883 / 883 | 16.3 | 0.11 | 0 / 0 (1) |
| D spiral | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.74/4.85/7.21 | 743 / 743 | 45.4 | 0.16 | 0 / 0 (1) |
| F spiral_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.74/4.83/4.86 | 758 / 758 | 10.6 | 0.09 | 0 / 0 (1) |
| H spiral_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.74/4.85/7.21 | 743 / 743 | 45.4 | 0.16 | 0 / 0 (1) |
| I spiral_rcc_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.74/4.83/4.86 | 758 / 758 | 10.6 | 0.09 | 0 / 0 (1) |
| J spiral_rcc_verify | 100.0% (91.2-100.0) | 0 | 0 | 0 | 7.83/8.23/8.45 | 457 / 457 | 10.6 | 0.09 | 0 / 0 (1) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 8.08/10.33/19.06 | 417 / 417 | 32.6 | 0.12 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 8.08/10.33/19.06 | 417 / 417 | 32.6 | 0.12 | 0 / 0 (1) |

### arm, h2_ft_drift_0.3

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 0 | 0 | 38 | 4.32/4.32/4.32 | 71 / 3 | 69.3 | 0.24 | 19 / 0 (3.8e-06) |
| B correction | 97.5% (87.1-99.6) | 1 | 0 | 0 | 4.31/4.32/4.33 | 814 / 814 | 39.0 | 0.13 | 1 / 19 (4e-05) |
| E correction_rcc | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.08/4.09/4.09 | 883 / 883 | 16.0 | 0.12 | 0 / 19 (3.8e-06) |
| D spiral | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.76/4.96/5.05 | 753 / 753 | 40.9 | 0.15 | 0 / 19 (3.8e-06) |
| F spiral_rcc | 97.5% (87.1-99.6) | 1 | 0 | 0 | 4.76/4.95/5.70 | 725 / 725 | 10.7 | 0.11 | 0 / 18 (7.6e-06) |
| H spiral_pull | 100.0% (91.2-100.0) | 0 | 0 | 0 | 4.76/4.96/5.05 | 753 / 753 | 40.9 | 0.15 | 0 / 19 (3.8e-06) |
| I spiral_rcc_pull | 97.5% (87.1-99.6) | 1 | 0 | 0 | 4.76/4.95/5.70 | 725 / 725 | 10.7 | 0.11 | 0 / 18 (7.6e-06) |
| J spiral_rcc_verify | 65.0% (49.5-77.9) | 5 | 0 | 0 | 7.80/8.64/8.92 | 204 / 204 | 10.7 | 0.29 | 3 / 8 (0.23) |
| C adaptive | 52.5% (37.5-67.1) | 8 | 0 | 2 | 8.09/19.59/21.54 | 137 / 112 | 32.2 | 0.37 | reference |
| G adaptive_learned | 52.5% (37.5-67.1) | 8 | 0 | 2 | 8.09/19.59/21.54 | 137 / 112 | 32.2 | 0.37 | 0 / 0 (1) |

### arm, h2_mf_tol_0.10mm

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 0 | 0 | 40 | n/a | 0 / 0 | 67.2 | 0.23 | 40 / 0 (<1e-6) |
| B correction | 52.5% (37.5-67.1) | 0 | 0 | 19 | 3.78/3.80/3.80 | 582 / 60 | 77.3 | 0.26 | 19 / 0 (3.8e-06) |
| E correction_rcc | 60.0% (44.6-73.7) | 0 | 0 | 16 | 3.49/3.50/3.50 | 712 / 80 | 48.7 | 0.19 | 16 / 0 (3.1e-05) |
| D spiral | 95.0% (83.5-98.6) | 0 | 0 | 1 | 4.65/6.13/6.64 | 682 / 525 | 43.7 | 0.12 | 2 / 0 (0.5) |
| F spiral_rcc | 90.0% (76.9-96.0) | 0 | 0 | 0 | 4.68/7.53/8.07 | 437 / 437 | 20.1 | 0.09 | 4 / 0 (0.12) |
| H spiral_pull | 95.0% (83.5-98.6) | 0 | 0 | 1 | 8.56/10.02/10.49 | 393 / 335 | 43.7 | 0.12 | 2 / 0 (0.5) |
| I spiral_rcc_pull | 90.0% (76.9-96.0) | 0 | 0 | 0 | 8.65/11.39/12.03 | 296 / 296 | 20.3 | 0.09 | 4 / 0 (0.12) |
| J spiral_rcc_verify | 90.0% (76.9-96.0) | 0 | 0 | 0 | 8.64/11.38/12.01 | 296 / 296 | 20.2 | 0.09 | 4 / 0 (0.12) |
| C adaptive | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.05/12.65/15.72 | 342 / 342 | 43.1 | 0.13 | reference |
| G adaptive_learned | 100.0% (91.2-100.0) | 0 | 0 | 0 | 9.05/12.56/15.56 | 343 / 343 | 43.3 | 0.13 | 0 / 0 (1) |

### arm, h2_mf_tol_0.05mm

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 0 | 0 | 40 | n/a | 0 / 0 | 65.8 | 0.23 | 35 / 0 (<1e-6) |
| B correction | 15.0% (7.1-29.1) | 1 | 0 | 33 | 3.78/3.79/3.79 | 187 / 10 | 67.5 | 0.59 | 29 / 0 (<1e-6) |
| E correction_rcc | 45.0% (30.7-60.2) | 0 | 0 | 22 | 3.48/3.49/3.49 | 566 / 45 | 48.9 | 0.20 | 17 / 0 (1.5e-05) |
| D spiral | 42.5% (28.5-57.8) | 2 | 0 | 4 | 5.08/7.02/7.98 | 147 / 93 | 39.9 | 0.60 | 18 / 0 (7.6e-06) |
| F spiral_rcc | 70.0% (54.6-81.9) | 0 | 0 | 0 | 4.87/8.25/8.87 | 214 / 214 | 20.1 | 0.12 | 8 / 1 (0.039) |
| H spiral_pull | 42.5% (28.5-57.8) | 0 | 0 | 5 | 8.96/10.92/11.91 | 125 / 77 | 39.9 | 0.60 | 18 / 0 (7.6e-06) |
| I spiral_rcc_pull | 70.0% (54.6-81.9) | 0 | 0 | 0 | 8.80/12.18/12.83 | 174 / 174 | 20.2 | 0.12 | 8 / 1 (0.039) |
| J spiral_rcc_verify | 70.0% (54.6-81.9) | 0 | 0 | 0 | 8.83/12.14/12.82 | 174 / 174 | 20.2 | 0.12 | 8 / 1 (0.039) |
| C adaptive | 87.5% (73.9-94.5) | 0 | 0 | 1 | 12.29/18.92/22.88 | 230 / 207 | 42.6 | 0.39 | reference |
| G adaptive_learned | 87.5% (73.9-94.5) | 0 | 0 | 2 | 12.45/17.66/22.42 | 241 / 196 | 40.9 | 0.53 | 2 / 2 (1) |

### arm, h2_mf_grasp_unseen_1deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 5.0% (1.4-16.5) | 0 | 0 | 38 | 3.79/3.79/3.79 | 67 / 3 | 68.6 | 0.23 | 37 / 0 (<1e-6) |
| B correction | 55.0% (39.8-69.3) | 1 | 0 | 17 | 3.78/3.79/3.80 | 593 / 69 | 67.2 | 0.48 | 17 / 0 (1.5e-05) |
| E correction_rcc | 75.0% (59.8-85.8) | 0 | 0 | 10 | 3.49/3.50/3.51 | 841 / 148 | 48.7 | 0.22 | 9 / 0 (0.0039) |
| D spiral | 90.0% (76.9-96.0) | 1 | 0 | 0 | 4.57/5.89/6.43 | 628 / 628 | 41.1 | 0.32 | 4 / 1 (0.38) |
| F spiral_rcc | 97.5% (87.1-99.6) | 0 | 0 | 1 | 4.62/7.65/7.71 | 700 / 539 | 20.1 | 0.09 | 1 / 1 (1) |
| H spiral_pull | 90.0% (76.9-96.0) | 0 | 0 | 0 | 8.40/9.79/10.26 | 367 / 367 | 41.1 | 0.35 | 4 / 1 (0.38) |
| I spiral_rcc_pull | 97.5% (87.1-99.6) | 0 | 0 | 1 | 8.57/11.60/11.69 | 397 / 339 | 20.3 | 0.10 | 1 / 1 (1) |
| J spiral_rcc_verify | 97.5% (87.1-99.6) | 0 | 0 | 1 | 8.56/11.61/11.69 | 397 / 340 | 20.2 | 0.10 | 1 / 1 (1) |
| C adaptive | 97.5% (87.1-99.6) | 0 | 0 | 0 | 8.97/12.59/13.17 | 337 / 337 | 40.7 | 0.32 | reference |
| G adaptive_learned | 97.5% (87.1-99.6) | 0 | 0 | 0 | 8.97/12.59/13.17 | 337 / 337 | 40.8 | 0.32 | 0 / 0 (1) |

### arm, h2_mf_grasp_unseen_2deg

| Controller | Success (95% CI) | Bad units passed | False rejects | Protective stops | Cycle p50 / p95 / p99 (s) | Good units/h (0 s / 60 s per stop) | p95 peak force (N) | p95 wrist torque (N m) | vs C: C-only / other-only (McNemar p) |
|---|---|---|---|---|---|---|---|---|---|
| A fixed | 0.0% (0.0-8.8) | 0 | 0 | 40 | n/a | 0 / 0 | 66.2 | 0.25 | 22 / 0 (<1e-6) |
| B correction | 25.0% (14.2-40.2) | 2 | 0 | 28 | 3.78/3.79/3.79 | 294 / 20 | 63.2 | 0.60 | 12 / 0 (0.00049) |
| E correction_rcc | 42.5% (28.5-57.8) | 0 | 0 | 23 | 3.48/3.49/3.49 | 538 / 41 | 48.9 | 0.24 | 5 / 0 (0.062) |
| D spiral | 47.5% (32.9-62.5) | 4 | 0 | 0 | 4.92/8.15/8.25 | 252 / 252 | 42.8 | 0.45 | 10 / 7 (0.63) |
| F spiral_rcc | 92.5% (80.1-97.4) | 1 | 0 | 1 | 5.53/7.93/9.96 | 559 / 447 | 23.0 | 0.15 | 1 / 16 (0.00027) |
| H spiral_pull | 47.5% (32.9-62.5) | 0 | 0 | 0 | 8.74/11.94/12.15 | 185 / 185 | 42.8 | 0.46 | 10 / 7 (0.63) |
| I spiral_rcc_pull | 92.5% (80.1-97.4) | 1 | 0 | 1 | 9.36/11.85/13.85 | 345 / 299 | 23.0 | 0.16 | 1 / 16 (0.00027) |
| J spiral_rcc_verify | 95.0% (83.5-98.6) | 0 | 0 | 1 | 9.43/11.84/13.82 | 355 / 307 | 23.0 | 0.16 | 1 / 17 (0.00014) |
| C adaptive | 55.0% (39.8-69.3) | 0 | 0 | 0 | 8.91/19.03/24.12 | 113 / 113 | 39.6 | 0.36 | reference |
| G adaptive_learned | 55.0% (39.8-69.3) | 0 | 0 | 0 | 8.91/16.18/23.49 | 114 / 114 | 39.6 | 0.36 | 0 / 0 (1) |
