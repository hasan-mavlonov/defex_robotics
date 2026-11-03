# Simulator randomization v0.2f: tables for results/sim_randomization_v0.2f

Reference classes from /Users/husanmavlonov/projects/defex_robotics-f-simrand/results/benchmark_v0.2e on the same conditions. 'holds' = same sign (directional reference) or no significant difference ('n.s.' reference) in at least 10 of the randomized variants AND the pooled scenario sign test over the randomized variants is not the opposite class (directional reference) or is 'n.s.' ('n.s.' reference). * = 0.01 <= p < 0.05.

## Verdicts

| Tier | Machine | Group | Metric | X vs Y | Reference | Variant 0: X / Y, X-better / Y-better, p | Variants holding (of which p < 0.05) | Departing variants | Pooled X / Y scenarios, p | P(noise alone fails) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | gantry | c_favourable | success | C vs F | better | 44 / 36 of 45, 8 / 0, 0.0078 | 12 / 12 (11) | none | 10 / 1, 0.012 * (better) | 0.00 | holds |
| primary | gantry | c_favourable | success | C vs H | better | 44 / 35 of 45, 9 / 0, 0.0039 | 12 / 12 (11) | none | 11 / 1, 0.0063 (better) | 0.00 | holds |
| primary | gantry | c_favourable | success | C vs I | better | 44 / 36 of 45, 8 / 0, 0.0078 | 12 / 12 (11) | none | 10 / 1, 0.012 * (better) | 0.00 | holds |
| primary | gantry | c_favourable | bad_units | C vs F | better | 0 / 5 of 45, 5 / 0, 0.062 | 12 / 12 (1) | none | 6 / 1, 0.12 (n.s.) | 0.00 | holds |
| primary | gantry | c_favourable | bad_units | C vs H | better | 0 / 5 of 45, 5 / 0, 0.062 | 12 / 12 (0) | none | 5 / 1, 0.22 (n.s.) | 0.00 | holds |
| primary | gantry | c_favourable | bad_units | C vs I | better | 0 / 5 of 45, 5 / 0, 0.062 | 12 / 12 (1) | none | 6 / 1, 0.12 (n.s.) | 0.00 | holds |
| primary | gantry | neutral | success | C vs F | n.s. | 45 / 45 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 2, 0.5 (n.s.) | - | holds |
| primary | gantry | neutral | success | C vs H | n.s. | 45 / 45 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 1, 1 (n.s.) | - | holds |
| primary | gantry | neutral | success | C vs I | n.s. | 45 / 45 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 2, 0.5 (n.s.) | - | holds |
| primary | gantry | neutral | bad_units | C vs F | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | neutral | bad_units | C vs H | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | neutral | bad_units | C vs I | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | c_unfavourable | success | C vs F | worse | 22 / 30 of 30, 0 / 8, 0.0078 | 12 / 12 (8) | none | 2 / 9, 0.065 (n.s.) | 0.00 | holds |
| primary | gantry | c_unfavourable | success | C vs H | better | 22 / 19 of 30, 5 / 2, 0.45 | 12 / 12 (0) | none | 7 / 5, 0.77 (n.s.) | 0.48 | holds |
| primary | gantry | c_unfavourable | success | C vs I | worse | 22 / 30 of 30, 0 / 8, 0.0078 | 12 / 12 (8) | none | 2 / 9, 0.065 (n.s.) | 0.00 | holds |
| primary | gantry | c_unfavourable | bad_units | C vs F | n.s. | 0 / 0 of 30, 0 / 0, 1 | 12 / 12 (-) | none | 4 / 0, 0.12 (n.s.) | - | holds |
| primary | gantry | c_unfavourable | bad_units | C vs H | n.s. | 0 / 1 of 30, 1 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| primary | gantry | c_unfavourable | bad_units | C vs I | n.s. | 0 / 0 of 30, 0 / 0, 1 | 12 / 12 (-) | none | 4 / 0, 0.12 (n.s.) | - | holds |
| primary | gantry | latching_good | success | C vs F | n.s. | 18 / 19 of 20, 1 / 2, 1 | 12 / 12 (-) | none | 1 / 4, 0.38 (n.s.) | - | holds |
| primary | gantry | latching_good | success | C vs H | better | 18 / 11 of 20, 7 / 0, 0.016 * | 12 / 12 (8) | none | 18 / 0, 7.6e-06 (better) | 0.00 | holds |
| primary | gantry | latching_good | success | C vs I | n.s. | 18 / 19 of 20, 1 / 2, 1 | 10 / 12 (-) | 3,10 | 8 / 4, 0.39 (n.s.) | - | holds |
| primary | gantry | latching_good | bad_units | C vs F | n.s. | 0 / 0 of 20, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | latching_good | bad_units | C vs H | n.s. | 0 / 0 of 20, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | latching_good | bad_units | C vs I | n.s. | 0 / 0 of 20, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | all_good_parts | bad_units | C vs F | better | 0 / 5 of 140, 5 / 0, 0.062 | 12 / 12 (7) | none | 10 / 1, 0.012 * (better) | 0.00 | holds |
| primary | gantry | all_good_parts | bad_units | C vs H | better | 0 / 6 of 140, 6 / 0, 0.031 * | 12 / 12 (7) | none | 6 / 1, 0.12 (n.s.) | 0.00 | holds |
| primary | gantry | all_good_parts | bad_units | C vs I | better | 0 / 5 of 140, 5 / 0, 0.062 | 12 / 12 (7) | none | 10 / 1, 0.012 * (better) | 0.00 | holds |
| primary | gantry | bad_parts | bad_units | C vs H | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | gantry | bad_parts | bad_units | C vs I | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | arm | c_favourable | success | C vs F | better | 40 / 36 of 45, 5 / 1, 0.22 | 10 / 12 (0) | none | 8 / 7, 1 (n.s.) | 0.00 | holds |
| primary | arm | c_favourable | success | C vs H | better | 40 / 33 of 45, 8 / 1, 0.039 * | 12 / 12 (3) | none | 15 / 6, 0.078 (n.s.) | 0.00 | holds |
| primary | arm | c_favourable | success | C vs I | better | 40 / 36 of 45, 5 / 1, 0.22 | 10 / 12 (0) | none | 8 / 7, 1 (n.s.) | 0.00 | holds |
| primary | arm | c_favourable | bad_units | C vs F | better | 0 / 4 of 45, 4 / 0, 0.12 | 12 / 12 (0) | none | 6 / 0, 0.031 * (better) | 0.00 | holds |
| primary | arm | c_favourable | bad_units | C vs H | better | 0 / 2 of 45, 2 / 0, 0.5 | 12 / 12 (0) | none | 3 / 0, 0.25 (n.s.) | 0.01 | holds |
| primary | arm | c_favourable | bad_units | C vs I | better | 0 / 4 of 45, 4 / 0, 0.12 | 12 / 12 (0) | none | 6 / 0, 0.031 * (better) | 0.00 | holds |
| primary | arm | neutral | success | C vs F | n.s. | 43 / 45 of 45, 0 / 2, 0.5 | 6 / 12 (-) | 4,6,7,8,11,12 | 0 / 15, 6.1e-05 (worse) | - | does not hold |
| primary | arm | neutral | success | C vs H | n.s. | 43 / 45 of 45, 0 / 2, 0.5 | 6 / 12 (-) | 4,6,7,8,11,12 | 0 / 15, 6.1e-05 (worse) | - | does not hold |
| primary | arm | neutral | success | C vs I | n.s. | 43 / 45 of 45, 0 / 2, 0.5 | 6 / 12 (-) | 4,6,7,8,11,12 | 0 / 15, 6.1e-05 (worse) | - | does not hold |
| primary | arm | neutral | bad_units | C vs F | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | arm | neutral | bad_units | C vs H | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | arm | neutral | bad_units | C vs I | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | arm | c_unfavourable | success | C vs F | worse | 21 / 28 of 30, 1 / 8, 0.039 * | 12 / 12 (11) | none | 1 / 13, 0.0018 (worse) | 0.03 | holds |
| primary | arm | c_unfavourable | success | C vs H | n.s. | 21 / 18 of 30, 3 / 0, 0.25 | 11 / 12 (-) | 12 | 7 / 2, 0.18 (n.s.) | - | holds |
| primary | arm | c_unfavourable | success | C vs I | worse | 21 / 28 of 30, 1 / 8, 0.039 * | 12 / 12 (11) | none | 1 / 13, 0.0018 (worse) | 0.03 | holds |
| primary | arm | c_unfavourable | bad_units | C vs F | n.s. | 0 / 1 of 30, 1 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| primary | arm | c_unfavourable | bad_units | C vs H | n.s. | 0 / 0 of 30, 0 / 0, 1 | 12 / 12 (-) | none | 2 / 0, 0.5 (n.s.) | - | holds |
| primary | arm | c_unfavourable | bad_units | C vs I | n.s. | 0 / 1 of 30, 1 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| primary | arm | latching_good | success | C vs F | worse | 39 / 47 of 50, 1 / 9, 0.021 * | 9 / 12 (6) | none | 13 / 27, 0.038 * (worse) | 0.17 | does not hold |
| primary | arm | latching_good | success | C vs H | better | 39 / 20 of 50, 21 / 2, 6.6e-05 | 12 / 12 (11) | none | 33 / 7, 4.2e-05 (better) | 0.00 | holds |
| primary | arm | latching_good | success | C vs I | worse | 39 / 47 of 50, 1 / 9, 0.021 * | 9 / 12 (4) | 1 | 17 / 22, 0.52 (n.s.) | 0.22 | not resolved (low power) |
| primary | arm | latching_good | bad_units | C vs F | n.s. | 0 / 0 of 50, 0 / 0, 1 | 12 / 12 (-) | none | 4 / 1, 0.38 (n.s.) | - | holds |
| primary | arm | latching_good | bad_units | C vs H | n.s. | 0 / 0 of 50, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 1, 1 (n.s.) | - | holds |
| primary | arm | latching_good | bad_units | C vs I | n.s. | 0 / 0 of 50, 0 / 0, 1 | 12 / 12 (-) | none | 2 / 1, 1 (n.s.) | - | holds |
| primary | arm | all_good_parts | bad_units | C vs F | better | 0 / 5 of 170, 5 / 0, 0.062 | 12 / 12 (1) | none | 11 / 1, 0.0063 (better) | 0.00 | holds |
| primary | arm | all_good_parts | bad_units | C vs H | better | 0 / 2 of 170, 2 / 0, 0.5 | 12 / 12 (0) | none | 5 / 1, 0.22 (n.s.) | 0.00 | holds |
| primary | arm | all_good_parts | bad_units | C vs I | better | 0 / 5 of 170, 5 / 0, 0.062 | 12 / 12 (0) | none | 9 / 1, 0.021 * (better) | 0.00 | holds |
| primary | arm | bad_parts | bad_units | C vs H | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| primary | arm | bad_parts | bad_units | C vs I | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | c_favourable | success | J vs C | worse | 41 / 44 of 45, 0 / 3, 0.25 | 12 / 12 (2) | none | 1 / 15, 0.00052 (worse) | 0.45 | holds |
| secondary | gantry | c_favourable | success | G vs C | better | 44 / 44 of 45, 1 / 1, 1 (not reproduced) | 2 / 12 (0) | none | 2 / 2, 1 (n.s.) | 0.05 | does not hold |
| secondary | gantry | c_favourable | bad_units | J vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | c_favourable | bad_units | G vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | neutral | success | J vs C | n.s. | 45 / 45 of 45, 0 / 0, 1 | 11 / 12 (-) | 10 | 0 / 12, 0.00049 (worse) | - | does not hold |
| secondary | gantry | neutral | success | G vs C | n.s. | 45 / 45 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 1, 1 (n.s.) | - | holds |
| secondary | gantry | neutral | bad_units | J vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 2, 0.5 (n.s.) | - | holds |
| secondary | gantry | neutral | bad_units | G vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | c_unfavourable | success | J vs C | better | 28 / 22 of 30, 7 / 1, 0.07 | 11 / 12 (7) | none | 9 / 9, 1 (n.s.) | 0.00 | holds |
| secondary | gantry | c_unfavourable | success | G vs C | better | 25 / 22 of 30, 4 / 1, 0.38 | 12 / 12 (0) | none | 8 / 0, 0.0078 (better) | 0.00 | holds |
| secondary | gantry | c_unfavourable | bad_units | J vs C | n.s. | 1 / 0 of 30, 0 / 1, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | c_unfavourable | bad_units | G vs C | n.s. | 0 / 0 of 30, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | latching_good | success | J vs C | n.s. | 19 / 18 of 20, 2 / 1, 1 | 11 / 12 (-) | 3 | 4 / 7, 0.55 (n.s.) | - | holds |
| secondary | gantry | latching_good | success | G vs C | better | 19 / 18 of 20, 1 / 0, 1 | 10 / 12 (0) | none | 5 / 2, 0.45 (n.s.) | 0.87 | holds |
| secondary | gantry | latching_good | bad_units | J vs C | n.s. | 0 / 0 of 20, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | latching_good | bad_units | G vs C | n.s. | 0 / 0 of 20, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | all_good_parts | bad_units | J vs C | n.s. | 1 / 0 of 140, 0 / 1, 1 | 12 / 12 (-) | none | 1 / 2, 1 (n.s.) | - | holds |
| secondary | gantry | all_good_parts | bad_units | G vs C | n.s. | 0 / 0 of 140, 0 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | bad_parts | bad_units | J vs C | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | gantry | bad_parts | bad_units | G vs C | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | arm | c_favourable | success | J vs C | worse | 38 / 40 of 45, 2 / 4, 0.69 | 11 / 12 (1) | none | 5 / 15, 0.041 * (worse) | 0.06 | holds |
| secondary | arm | c_favourable | success | G vs C | better | 43 / 40 of 45, 3 / 0, 0.25 | 12 / 12 (1) | none | 9 / 5, 0.42 (n.s.) | 0.08 | holds |
| secondary | arm | c_favourable | bad_units | J vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 11 / 12 (-) | 4 | 0 / 13, 0.00024 (worse) | - | does not hold |
| secondary | arm | c_favourable | bad_units | G vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | arm | neutral | success | J vs C | n.s. | 45 / 43 of 45, 2 / 0, 0.5 | 6 / 12 (-) | 4,6,7,8,11,12 | 15 / 7, 0.13 (n.s.) | - | does not hold |
| secondary | arm | neutral | success | G vs C | n.s. | 44 / 43 of 45, 1 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| secondary | arm | neutral | bad_units | J vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 7, 0.016 * (worse) | - | does not hold |
| secondary | arm | neutral | bad_units | G vs C | n.s. | 0 / 0 of 45, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | arm | c_unfavourable | success | J vs C | n.s. | 25 / 21 of 30, 5 / 1, 0.22 | 12 / 12 (-) | none | 8 / 9, 1 (n.s.) | - | holds |
| secondary | arm | c_unfavourable | success | G vs C | better | 23 / 21 of 30, 2 / 0, 0.5 | 8 / 12 (0) | none | 8 / 2, 0.11 (n.s.) | 0.19 | does not hold |
| secondary | arm | c_unfavourable | bad_units | J vs C | n.s. | 0 / 0 of 30, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 5, 0.062 (n.s.) | - | holds |
| secondary | arm | c_unfavourable | bad_units | G vs C | n.s. | 0 / 0 of 30, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | arm | latching_good | success | J vs C | better | 47 / 39 of 50, 9 / 1, 0.021 * | 10 / 12 (5) | none | 24 / 14, 0.14 (n.s.) | 0.14 | holds |
| secondary | arm | latching_good | success | G vs C | better | 46 / 39 of 50, 7 / 0, 0.016 * | 8 / 12 (1) | none | 18 / 7, 0.043 * (better) | 0.00 | does not hold |
| secondary | arm | latching_good | bad_units | J vs C | n.s. | 0 / 0 of 50, 0 / 0, 1 | 12 / 12 (-) | none | 1 / 1, 1 (n.s.) | - | holds |
| secondary | arm | latching_good | bad_units | G vs C | n.s. | 0 / 0 of 50, 0 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| secondary | arm | all_good_parts | bad_units | J vs C | n.s. | 0 / 0 of 170, 0 / 0, 1 | 11 / 12 (-) | 4 | 1 / 26, 4.2e-07 (worse) | - | does not hold |
| secondary | arm | all_good_parts | bad_units | G vs C | n.s. | 0 / 0 of 170, 0 / 0, 1 | 12 / 12 (-) | none | 1 / 0, 1 (n.s.) | - | holds |
| secondary | arm | bad_parts | bad_units | J vs C | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |
| secondary | arm | bad_parts | bad_units | G vs C | n.s. | 0 / 0 of 12, 0 / 0, 1 | 12 / 12 (-) | none | 0 / 0, 1 (n.s.) | - | holds |

## Per variant (X / Y count of n, X-better / Y-better, p)

- gantry c_favourable success C vs F (ref better): 1: 44/36 of 45, 8/0; 2: 44/36 of 45, 8/0; 3: 44/36 of 45, 8/0; 4: 44/36 of 45, 8/0; 5: 43/36 of 45, 7/0; 6: 45/36 of 45, 9/0; 7: 45/36 of 45, 9/0; 8: 44/36 of 45, 8/0; 9: 44/36 of 45, 8/0; 10: 42/36 of 45, 8/2; 11: 45/35 of 45, 10/0; 12: 45/36 of 45, 9/0
- gantry c_favourable success C vs H (ref better): 1: 44/35 of 45, 9/0; 2: 44/35 of 45, 9/0; 3: 44/36 of 45, 8/0; 4: 44/35 of 45, 9/0; 5: 43/36 of 45, 7/0; 6: 45/34 of 45, 11/0; 7: 45/35 of 45, 10/0; 8: 44/35 of 45, 9/0; 9: 44/35 of 45, 9/0; 10: 42/36 of 45, 8/2; 11: 45/35 of 45, 10/0; 12: 45/35 of 45, 10/0
- gantry c_favourable success C vs I (ref better): 1: 44/36 of 45, 8/0; 2: 44/36 of 45, 8/0; 3: 44/36 of 45, 8/0; 4: 44/36 of 45, 8/0; 5: 43/36 of 45, 7/0; 6: 45/36 of 45, 9/0; 7: 45/36 of 45, 9/0; 8: 44/36 of 45, 8/0; 9: 44/36 of 45, 8/0; 10: 42/36 of 45, 8/2; 11: 45/35 of 45, 10/0; 12: 45/36 of 45, 9/0
- gantry c_favourable success J vs C (ref worse): 1: 42/44 of 45, 1/3; 2: 41/44 of 45, 0/3; 3: 34/44 of 45, 0/10; 4: 41/44 of 45, 0/3; 5: 41/43 of 45, 0/2; 6: 41/45 of 45, 0/4; 7: 41/45 of 45, 0/4; 8: 41/44 of 45, 0/3; 9: 41/44 of 45, 0/3; 10: 32/42 of 45, 2/12; 11: 40/45 of 45, 0/5; 12: 40/45 of 45, 0/5
- gantry c_favourable success G vs C (ref better): 1: 43/44 of 45, 0/1 x; 2: 44/44 of 45, 1/1 x; 3: 44/44 of 45, 1/1 x; 4: 44/44 of 45, 1/1 x; 5: 45/43 of 45, 2/0; 6: 45/45 of 45, 0/0 x; 7: 44/45 of 45, 0/1 x; 8: 44/44 of 45, 1/1 x; 9: 43/44 of 45, 1/2 x; 10: 43/42 of 45, 2/1; 11: 43/45 of 45, 0/2 x; 12: 44/45 of 45, 0/1 x
- gantry c_favourable bad_units C vs F (ref better): 1: 0/6 of 45, 6/0; 2: 0/5 of 45, 5/0; 3: 0/4 of 45, 4/0; 4: 0/5 of 45, 5/0; 5: 0/5 of 45, 5/0; 6: 0/5 of 45, 5/0; 7: 0/5 of 45, 5/0; 8: 0/5 of 45, 5/0; 9: 0/5 of 45, 5/0; 10: 1/5 of 45, 5/1; 11: 0/5 of 45, 5/0; 12: 0/4 of 45, 4/0
- gantry c_favourable bad_units C vs H (ref better): 1: 0/5 of 45, 5/0; 2: 0/4 of 45, 4/0; 3: 0/4 of 45, 4/0; 4: 0/5 of 45, 5/0; 5: 0/5 of 45, 5/0; 6: 0/5 of 45, 5/0; 7: 0/5 of 45, 5/0; 8: 0/5 of 45, 5/0; 9: 0/4 of 45, 4/0; 10: 1/4 of 45, 4/1; 11: 0/4 of 45, 4/0; 12: 0/5 of 45, 5/0
- gantry c_favourable bad_units C vs I (ref better): 1: 0/6 of 45, 6/0; 2: 0/5 of 45, 5/0; 3: 0/4 of 45, 4/0; 4: 0/5 of 45, 5/0; 5: 0/5 of 45, 5/0; 6: 0/5 of 45, 5/0; 7: 0/5 of 45, 5/0; 8: 0/5 of 45, 5/0; 9: 0/5 of 45, 5/0; 10: 1/5 of 45, 5/1; 11: 0/5 of 45, 5/0; 12: 0/4 of 45, 4/0
- gantry c_favourable bad_units J vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/1 of 45, 1/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry c_favourable bad_units G vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/1 of 45, 1/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry neutral success C vs F (ref n.s.): 1: 45/45 of 45, 0/0; 2: 45/45 of 45, 0/0; 3: 45/45 of 45, 0/0; 4: 45/45 of 45, 0/0; 5: 45/45 of 45, 0/0; 6: 45/45 of 45, 0/0; 7: 45/45 of 45, 0/0; 8: 45/45 of 45, 0/0; 9: 45/45 of 45, 0/0; 10: 43/45 of 45, 0/2; 11: 45/45 of 45, 0/0; 12: 45/45 of 45, 0/0
- gantry neutral success C vs H (ref n.s.): 1: 45/45 of 45, 0/0; 2: 45/45 of 45, 0/0; 3: 45/44 of 45, 1/0; 4: 45/45 of 45, 0/0; 5: 45/45 of 45, 0/0; 6: 45/45 of 45, 0/0; 7: 45/45 of 45, 0/0; 8: 45/45 of 45, 0/0; 9: 45/45 of 45, 0/0; 10: 43/45 of 45, 0/2; 11: 45/45 of 45, 0/0; 12: 45/45 of 45, 0/0
- gantry neutral success C vs I (ref n.s.): 1: 45/45 of 45, 0/0; 2: 45/45 of 45, 0/0; 3: 45/45 of 45, 0/0; 4: 45/45 of 45, 0/0; 5: 45/45 of 45, 0/0; 6: 45/45 of 45, 0/0; 7: 45/45 of 45, 0/0; 8: 45/45 of 45, 0/0; 9: 45/45 of 45, 0/0; 10: 43/45 of 45, 0/2; 11: 45/45 of 45, 0/0; 12: 45/45 of 45, 0/0
- gantry neutral success J vs C (ref n.s.): 1: 45/45 of 45, 0/0; 2: 45/45 of 45, 0/0; 3: 42/45 of 45, 0/3; 4: 45/45 of 45, 0/0; 5: 45/45 of 45, 0/0; 6: 45/45 of 45, 0/0; 7: 45/45 of 45, 0/0; 8: 45/45 of 45, 0/0; 9: 45/45 of 45, 0/0; 10: 33/43 of 45, 0/10 x; 11: 45/45 of 45, 0/0; 12: 45/45 of 45, 0/0
- gantry neutral success G vs C (ref n.s.): 1: 45/45 of 45, 0/0; 2: 45/45 of 45, 0/0; 3: 45/45 of 45, 0/0; 4: 45/45 of 45, 0/0; 5: 44/45 of 45, 0/1; 6: 45/45 of 45, 0/0; 7: 45/45 of 45, 0/0; 8: 45/45 of 45, 0/0; 9: 45/45 of 45, 0/0; 10: 43/43 of 45, 0/0; 11: 45/45 of 45, 0/0; 12: 45/45 of 45, 0/0
- gantry neutral bad_units C vs F (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry neutral bad_units C vs H (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry neutral bad_units C vs I (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry neutral bad_units J vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 2/0 of 45, 0/2; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry neutral bad_units G vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- gantry c_unfavourable success C vs F (ref worse): 1: 22/29 of 30, 0/7; 2: 23/29 of 30, 0/6; 3: 23/29 of 30, 0/6; 4: 22/29 of 30, 0/7; 5: 22/30 of 30, 0/8; 6: 23/29 of 30, 0/6; 7: 23/28 of 30, 1/6; 8: 23/28 of 30, 0/5; 9: 23/30 of 30, 0/7; 10: 24/29 of 30, 0/5; 11: 22/25 of 30, 1/4; 12: 23/29 of 30, 0/6
- gantry c_unfavourable success C vs H (ref better): 1: 22/20 of 30, 4/2; 2: 23/19 of 30, 5/1; 3: 23/20 of 30, 4/1; 4: 22/20 of 30, 3/1; 5: 22/20 of 30, 4/2; 6: 23/20 of 30, 3/0; 7: 23/20 of 30, 3/0; 8: 23/20 of 30, 4/1; 9: 23/19 of 30, 5/1; 10: 24/20 of 30, 5/1; 11: 22/19 of 30, 4/1; 12: 23/21 of 30, 3/1
- gantry c_unfavourable success C vs I (ref worse): 1: 22/29 of 30, 0/7; 2: 23/29 of 30, 0/6; 3: 23/29 of 30, 0/6; 4: 22/29 of 30, 0/7; 5: 22/30 of 30, 0/8; 6: 23/29 of 30, 0/6; 7: 23/28 of 30, 1/6; 8: 23/28 of 30, 0/5; 9: 23/30 of 30, 0/7; 10: 24/29 of 30, 0/5; 11: 22/25 of 30, 1/4; 12: 23/29 of 30, 0/6
- gantry c_unfavourable success J vs C (ref better): 1: 30/22 of 30, 8/0; 2: 30/23 of 30, 7/0; 3: 26/23 of 30, 7/4; 4: 30/22 of 30, 8/0; 5: 30/22 of 30, 8/0; 6: 29/23 of 30, 7/1; 7: 29/23 of 30, 7/1; 8: 29/23 of 30, 6/0; 9: 30/23 of 30, 7/0; 10: 23/24 of 30, 6/7 x; 11: 28/22 of 30, 7/1; 12: 29/23 of 30, 6/0
- gantry c_unfavourable success G vs C (ref better): 1: 27/22 of 30, 5/0; 2: 26/23 of 30, 3/0; 3: 25/23 of 30, 2/0; 4: 27/22 of 30, 5/0; 5: 27/22 of 30, 5/0; 6: 27/23 of 30, 4/0; 7: 26/23 of 30, 3/0; 8: 24/23 of 30, 1/0; 9: 26/23 of 30, 3/0; 10: 25/24 of 30, 1/0; 11: 23/22 of 30, 1/0; 12: 26/23 of 30, 3/0
- gantry c_unfavourable bad_units C vs F (ref n.s.): 1: 0/1 of 30, 1/0; 2: 0/1 of 30, 1/0; 3: 0/1 of 30, 1/0; 4: 0/1 of 30, 1/0; 5: 0/0 of 30, 0/0; 6: 0/1 of 30, 1/0; 7: 0/1 of 30, 1/0; 8: 0/1 of 30, 1/0; 9: 0/0 of 30, 0/0; 10: 0/1 of 30, 1/0; 11: 0/3 of 30, 3/0; 12: 0/0 of 30, 0/0
- gantry c_unfavourable bad_units C vs H (ref n.s.): 1: 0/1 of 30, 1/0; 2: 0/1 of 30, 1/0; 3: 0/1 of 30, 1/0; 4: 0/1 of 30, 1/0; 5: 0/1 of 30, 1/0; 6: 0/1 of 30, 1/0; 7: 0/1 of 30, 1/0; 8: 0/1 of 30, 1/0; 9: 0/1 of 30, 1/0; 10: 0/1 of 30, 1/0; 11: 0/1 of 30, 1/0; 12: 0/1 of 30, 1/0
- gantry c_unfavourable bad_units C vs I (ref n.s.): 1: 0/1 of 30, 1/0; 2: 0/1 of 30, 1/0; 3: 0/1 of 30, 1/0; 4: 0/1 of 30, 1/0; 5: 0/0 of 30, 0/0; 6: 0/1 of 30, 1/0; 7: 0/1 of 30, 1/0; 8: 0/1 of 30, 1/0; 9: 0/0 of 30, 0/0; 10: 0/1 of 30, 1/0; 11: 0/3 of 30, 3/0; 12: 0/0 of 30, 0/0
- gantry c_unfavourable bad_units J vs C (ref n.s.): 1: 0/0 of 30, 0/0; 2: 0/0 of 30, 0/0; 3: 0/0 of 30, 0/0; 4: 0/0 of 30, 0/0; 5: 0/0 of 30, 0/0; 6: 0/0 of 30, 0/0; 7: 0/0 of 30, 0/0; 8: 0/0 of 30, 0/0; 9: 0/0 of 30, 0/0; 10: 0/0 of 30, 0/0; 11: 0/0 of 30, 0/0; 12: 0/0 of 30, 0/0
- gantry c_unfavourable bad_units G vs C (ref n.s.): 1: 0/0 of 30, 0/0; 2: 0/0 of 30, 0/0; 3: 0/0 of 30, 0/0; 4: 0/0 of 30, 0/0; 5: 0/0 of 30, 0/0; 6: 0/0 of 30, 0/0; 7: 0/0 of 30, 0/0; 8: 0/0 of 30, 0/0; 9: 0/0 of 30, 0/0; 10: 0/0 of 30, 0/0; 11: 0/0 of 30, 0/0; 12: 0/0 of 30, 0/0
- gantry latching_good success C vs F (ref n.s.): 1: 16/19 of 20, 1/4; 2: 17/19 of 20, 1/3; 3: 17/19 of 20, 1/3; 4: 19/19 of 20, 1/1; 5: 17/20 of 20, 0/3; 6: 18/19 of 20, 1/2; 7: 18/19 of 20, 1/2; 8: 18/19 of 20, 1/2; 9: 17/20 of 20, 0/3; 10: 17/20 of 20, 0/3; 11: 20/19 of 20, 1/0; 12: 15/19 of 20, 1/5
- gantry latching_good success C vs H (ref better): 1: 16/11 of 20, 6/1; 2: 17/8 of 20, 10/1; 3: 17/11 of 20, 7/1; 4: 19/9 of 20, 10/0; 5: 17/11 of 20, 7/1; 6: 18/2 of 20, 16/0; 7: 18/5 of 20, 13/0; 8: 18/7 of 20, 11/0; 9: 17/12 of 20, 6/1; 10: 17/10 of 20, 8/1; 11: 20/9 of 20, 11/0; 12: 15/8 of 20, 7/0
- gantry latching_good success C vs I (ref n.s.): 1: 16/19 of 20, 1/4; 2: 17/19 of 20, 1/3; 3: 17/10 of 20, 8/1 x; 4: 19/19 of 20, 1/1; 5: 17/20 of 20, 0/3; 6: 18/19 of 20, 1/2; 7: 18/19 of 20, 1/2; 8: 18/19 of 20, 1/2; 9: 17/20 of 20, 0/3; 10: 17/10 of 20, 8/1 x; 11: 20/19 of 20, 1/0; 12: 15/19 of 20, 1/5
- gantry latching_good success J vs C (ref n.s.): 1: 19/16 of 20, 4/1; 2: 19/17 of 20, 3/1; 3: 10/17 of 20, 1/8 x; 4: 19/19 of 20, 1/1; 5: 20/17 of 20, 3/0; 6: 19/18 of 20, 2/1; 7: 19/18 of 20, 2/1; 8: 19/18 of 20, 2/1; 9: 20/17 of 20, 3/0; 10: 11/17 of 20, 1/7; 11: 19/20 of 20, 0/1; 12: 19/15 of 20, 5/1
- gantry latching_good success G vs C (ref better): 1: 20/16 of 20, 4/0; 2: 20/17 of 20, 3/0; 3: 16/17 of 20, 2/3 x; 4: 20/19 of 20, 1/0; 5: 20/17 of 20, 3/0; 6: 19/18 of 20, 1/0; 7: 20/18 of 20, 2/0; 8: 20/18 of 20, 2/0; 9: 20/17 of 20, 3/0; 10: 19/17 of 20, 3/1; 11: 19/20 of 20, 0/1 x; 12: 20/15 of 20, 5/0
- gantry latching_good bad_units C vs F (ref n.s.): 1: 0/0 of 20, 0/0; 2: 0/0 of 20, 0/0; 3: 0/0 of 20, 0/0; 4: 0/0 of 20, 0/0; 5: 0/0 of 20, 0/0; 6: 0/0 of 20, 0/0; 7: 0/0 of 20, 0/0; 8: 0/0 of 20, 0/0; 9: 0/0 of 20, 0/0; 10: 0/0 of 20, 0/0; 11: 0/0 of 20, 0/0; 12: 0/0 of 20, 0/0
- gantry latching_good bad_units C vs H (ref n.s.): 1: 0/0 of 20, 0/0; 2: 0/0 of 20, 0/0; 3: 0/0 of 20, 0/0; 4: 0/0 of 20, 0/0; 5: 0/0 of 20, 0/0; 6: 0/0 of 20, 0/0; 7: 0/0 of 20, 0/0; 8: 0/0 of 20, 0/0; 9: 0/0 of 20, 0/0; 10: 0/0 of 20, 0/0; 11: 0/0 of 20, 0/0; 12: 0/0 of 20, 0/0
- gantry latching_good bad_units C vs I (ref n.s.): 1: 0/0 of 20, 0/0; 2: 0/0 of 20, 0/0; 3: 0/0 of 20, 0/0; 4: 0/0 of 20, 0/0; 5: 0/0 of 20, 0/0; 6: 0/0 of 20, 0/0; 7: 0/0 of 20, 0/0; 8: 0/0 of 20, 0/0; 9: 0/0 of 20, 0/0; 10: 0/0 of 20, 0/0; 11: 0/0 of 20, 0/0; 12: 0/0 of 20, 0/0
- gantry latching_good bad_units J vs C (ref n.s.): 1: 0/0 of 20, 0/0; 2: 0/0 of 20, 0/0; 3: 0/0 of 20, 0/0; 4: 0/0 of 20, 0/0; 5: 0/0 of 20, 0/0; 6: 0/0 of 20, 0/0; 7: 0/0 of 20, 0/0; 8: 0/0 of 20, 0/0; 9: 0/0 of 20, 0/0; 10: 0/0 of 20, 0/0; 11: 0/0 of 20, 0/0; 12: 0/0 of 20, 0/0
- gantry latching_good bad_units G vs C (ref n.s.): 1: 0/0 of 20, 0/0; 2: 0/0 of 20, 0/0; 3: 0/0 of 20, 0/0; 4: 0/0 of 20, 0/0; 5: 0/0 of 20, 0/0; 6: 0/0 of 20, 0/0; 7: 0/0 of 20, 0/0; 8: 0/0 of 20, 0/0; 9: 0/0 of 20, 0/0; 10: 0/0 of 20, 0/0; 11: 0/0 of 20, 0/0; 12: 0/0 of 20, 0/0
- gantry all_good_parts bad_units C vs F (ref better): 1: 0/7 of 140, 7/0; 2: 0/6 of 140, 6/0; 3: 0/5 of 140, 5/0; 4: 0/6 of 140, 6/0; 5: 0/5 of 140, 5/0; 6: 0/6 of 140, 6/0; 7: 0/6 of 140, 6/0; 8: 0/6 of 140, 6/0; 9: 0/5 of 140, 5/0; 10: 1/6 of 140, 6/1; 11: 0/8 of 140, 8/0; 12: 0/4 of 140, 4/0
- gantry all_good_parts bad_units C vs H (ref better): 1: 0/6 of 140, 6/0; 2: 0/5 of 140, 5/0; 3: 0/5 of 140, 5/0; 4: 0/6 of 140, 6/0; 5: 0/6 of 140, 6/0; 6: 0/6 of 140, 6/0; 7: 0/6 of 140, 6/0; 8: 0/6 of 140, 6/0; 9: 0/5 of 140, 5/0; 10: 1/5 of 140, 5/1; 11: 0/5 of 140, 5/0; 12: 0/6 of 140, 6/0
- gantry all_good_parts bad_units C vs I (ref better): 1: 0/7 of 140, 7/0; 2: 0/6 of 140, 6/0; 3: 0/5 of 140, 5/0; 4: 0/6 of 140, 6/0; 5: 0/5 of 140, 5/0; 6: 0/6 of 140, 6/0; 7: 0/6 of 140, 6/0; 8: 0/6 of 140, 6/0; 9: 0/5 of 140, 5/0; 10: 1/6 of 140, 6/1; 11: 0/8 of 140, 8/0; 12: 0/4 of 140, 4/0
- gantry all_good_parts bad_units J vs C (ref n.s.): 1: 0/0 of 140, 0/0; 2: 0/0 of 140, 0/0; 3: 0/0 of 140, 0/0; 4: 0/0 of 140, 0/0; 5: 0/0 of 140, 0/0; 6: 0/0 of 140, 0/0; 7: 0/0 of 140, 0/0; 8: 0/0 of 140, 0/0; 9: 0/0 of 140, 0/0; 10: 2/1 of 140, 1/2; 11: 0/0 of 140, 0/0; 12: 0/0 of 140, 0/0
- gantry all_good_parts bad_units G vs C (ref n.s.): 1: 0/0 of 140, 0/0; 2: 0/0 of 140, 0/0; 3: 0/0 of 140, 0/0; 4: 0/0 of 140, 0/0; 5: 0/0 of 140, 0/0; 6: 0/0 of 140, 0/0; 7: 0/0 of 140, 0/0; 8: 0/0 of 140, 0/0; 9: 0/0 of 140, 0/0; 10: 0/1 of 140, 1/0; 11: 0/0 of 140, 0/0; 12: 0/0 of 140, 0/0
- gantry bad_parts bad_units C vs H (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- gantry bad_parts bad_units C vs I (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- gantry bad_parts bad_units J vs C (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- gantry bad_parts bad_units G vs C (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- arm c_favourable success C vs F (ref better): 1: 40/36 of 45, 6/2; 2: 39/36 of 45, 5/2; 3: 39/36 of 45, 4/1; 4: 39/37 of 45, 3/1; 5: 40/36 of 45, 5/1; 6: 37/35 of 45, 5/3; 7: 39/37 of 45, 4/2; 8: 36/37 of 45, 2/3 x; 9: 40/36 of 45, 5/1; 10: 40/36 of 45, 5/1; 11: 39/37 of 45, 3/1; 12: 36/37 of 45, 2/3 x
- arm c_favourable success C vs H (ref better): 1: 40/34 of 45, 8/2; 2: 39/34 of 45, 7/2; 3: 39/34 of 45, 6/1; 4: 39/36 of 45, 4/1; 5: 40/33 of 45, 8/1; 6: 37/34 of 45, 5/2; 7: 39/35 of 45, 5/1; 8: 36/35 of 45, 4/3; 9: 40/33 of 45, 8/1; 10: 40/33 of 45, 8/1; 11: 39/33 of 45, 7/1; 12: 36/34 of 45, 5/3
- arm c_favourable success C vs I (ref better): 1: 40/36 of 45, 6/2; 2: 39/36 of 45, 5/2; 3: 39/36 of 45, 4/1; 4: 39/37 of 45, 3/1; 5: 40/36 of 45, 5/1; 6: 37/35 of 45, 5/3; 7: 39/37 of 45, 4/2; 8: 36/37 of 45, 2/3 x; 9: 40/36 of 45, 5/1; 10: 40/36 of 45, 5/1; 11: 39/37 of 45, 3/1; 12: 36/37 of 45, 2/3 x
- arm c_favourable success J vs C (ref worse): 1: 38/40 of 45, 3/5; 2: 38/39 of 45, 3/4; 3: 37/39 of 45, 2/4; 4: 31/39 of 45, 2/10; 5: 38/40 of 45, 2/4; 6: 36/37 of 45, 4/5; 7: 37/39 of 45, 2/4; 8: 35/36 of 45, 3/4; 9: 38/40 of 45, 2/4; 10: 37/40 of 45, 2/5; 11: 37/39 of 45, 2/4; 12: 37/36 of 45, 4/3 x
- arm c_favourable success G vs C (ref better): 1: 41/40 of 45, 3/2; 2: 42/39 of 45, 4/1; 3: 41/39 of 45, 3/1; 4: 41/39 of 45, 2/0; 5: 44/40 of 45, 5/1; 6: 41/37 of 45, 5/1; 7: 43/39 of 45, 4/0; 8: 41/36 of 45, 6/1; 9: 44/40 of 45, 4/0; 10: 41/40 of 45, 4/3; 11: 43/39 of 45, 5/1; 12: 42/36 of 45, 6/0
- arm c_favourable bad_units C vs F (ref better): 1: 0/4 of 45, 4/0; 2: 0/4 of 45, 4/0; 3: 0/4 of 45, 4/0; 4: 0/4 of 45, 4/0; 5: 0/4 of 45, 4/0; 6: 0/5 of 45, 5/0; 7: 0/3 of 45, 3/0; 8: 0/4 of 45, 4/0; 9: 0/4 of 45, 4/0; 10: 0/4 of 45, 4/0; 11: 0/3 of 45, 3/0; 12: 0/3 of 45, 3/0
- arm c_favourable bad_units C vs H (ref better): 1: 0/3 of 45, 3/0; 2: 0/3 of 45, 3/0; 3: 0/2 of 45, 2/0; 4: 0/1 of 45, 1/0; 5: 0/2 of 45, 2/0; 6: 0/1 of 45, 1/0; 7: 0/1 of 45, 1/0; 8: 0/1 of 45, 1/0; 9: 0/3 of 45, 3/0; 10: 0/3 of 45, 3/0; 11: 0/1 of 45, 1/0; 12: 0/1 of 45, 1/0
- arm c_favourable bad_units C vs I (ref better): 1: 0/4 of 45, 4/0; 2: 0/4 of 45, 4/0; 3: 0/4 of 45, 4/0; 4: 0/4 of 45, 4/0; 5: 0/4 of 45, 4/0; 6: 0/5 of 45, 5/0; 7: 0/3 of 45, 3/0; 8: 0/4 of 45, 4/0; 9: 0/4 of 45, 4/0; 10: 0/4 of 45, 4/0; 11: 0/3 of 45, 3/0; 12: 0/3 of 45, 3/0
- arm c_favourable bad_units J vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 7/0 of 45, 0/7 x; 5: 0/0 of 45, 0/0; 6: 2/0 of 45, 0/2; 7: 1/0 of 45, 0/1; 8: 3/0 of 45, 0/3; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 1/0 of 45, 0/1; 12: 1/0 of 45, 0/1
- arm c_favourable bad_units G vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- arm neutral success C vs F (ref n.s.): 1: 44/45 of 45, 0/1; 2: 44/45 of 45, 0/1; 3: 43/45 of 45, 0/2; 4: 30/45 of 45, 0/15 x; 5: 43/45 of 45, 0/2; 6: 30/45 of 45, 0/15 x; 7: 30/45 of 45, 0/15 x; 8: 30/45 of 45, 0/15 x; 9: 43/45 of 45, 0/2; 10: 44/45 of 45, 0/1; 11: 31/45 of 45, 0/14 x; 12: 30/44 of 45, 0/14 x
- arm neutral success C vs H (ref n.s.): 1: 44/45 of 45, 0/1; 2: 44/45 of 45, 0/1; 3: 43/45 of 45, 0/2; 4: 30/45 of 45, 0/15 x; 5: 43/45 of 45, 0/2; 6: 30/45 of 45, 0/15 x; 7: 30/45 of 45, 0/15 x; 8: 30/45 of 45, 0/15 x; 9: 43/45 of 45, 0/2; 10: 44/45 of 45, 0/1; 11: 31/45 of 45, 0/14 x; 12: 30/45 of 45, 0/15 x
- arm neutral success C vs I (ref n.s.): 1: 44/45 of 45, 0/1; 2: 44/45 of 45, 0/1; 3: 43/45 of 45, 0/2; 4: 30/45 of 45, 0/15 x; 5: 43/45 of 45, 0/2; 6: 30/45 of 45, 0/15 x; 7: 30/45 of 45, 0/15 x; 8: 30/45 of 45, 0/15 x; 9: 43/45 of 45, 0/2; 10: 44/45 of 45, 0/1; 11: 31/45 of 45, 0/14 x; 12: 30/44 of 45, 0/14 x
- arm neutral success J vs C (ref n.s.): 1: 45/44 of 45, 1/0; 2: 45/44 of 45, 1/0; 3: 45/43 of 45, 2/0; 4: 45/30 of 45, 15/0 x; 5: 45/43 of 45, 2/0; 6: 44/30 of 45, 15/1 x; 7: 43/30 of 45, 15/2 x; 8: 45/30 of 45, 15/0 x; 9: 45/43 of 45, 2/0; 10: 45/44 of 45, 1/0; 11: 43/31 of 45, 14/2 x; 12: 41/30 of 45, 14/3 x
- arm neutral success G vs C (ref n.s.): 1: 44/44 of 45, 0/0; 2: 44/44 of 45, 0/0; 3: 43/43 of 45, 0/0; 4: 30/30 of 45, 0/0; 5: 44/43 of 45, 1/0; 6: 30/30 of 45, 0/0; 7: 30/30 of 45, 0/0; 8: 30/30 of 45, 0/0; 9: 43/43 of 45, 0/0; 10: 45/44 of 45, 1/0; 11: 31/31 of 45, 0/0; 12: 30/30 of 45, 0/0
- arm neutral bad_units C vs F (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- arm neutral bad_units C vs H (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- arm neutral bad_units C vs I (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- arm neutral bad_units J vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 1/0 of 45, 0/1; 7: 2/0 of 45, 0/2; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 2/0 of 45, 0/2; 12: 3/0 of 45, 0/3
- arm neutral bad_units G vs C (ref n.s.): 1: 0/0 of 45, 0/0; 2: 0/0 of 45, 0/0; 3: 0/0 of 45, 0/0; 4: 0/0 of 45, 0/0; 5: 0/0 of 45, 0/0; 6: 0/0 of 45, 0/0; 7: 0/0 of 45, 0/0; 8: 0/0 of 45, 0/0; 9: 0/0 of 45, 0/0; 10: 0/0 of 45, 0/0; 11: 0/0 of 45, 0/0; 12: 0/0 of 45, 0/0
- arm c_unfavourable success C vs F (ref worse): 1: 21/30 of 30, 0/9; 2: 21/29 of 30, 1/9; 3: 21/28 of 30, 1/8; 4: 18/29 of 30, 0/11; 5: 22/29 of 30, 0/7; 6: 22/29 of 30, 0/7; 7: 20/29 of 30, 0/9; 8: 20/29 of 30, 0/9; 9: 22/30 of 30, 0/8; 10: 21/30 of 30, 0/9; 11: 19/27 of 30, 0/8; 12: 23/25 of 30, 3/5
- arm c_unfavourable success C vs H (ref n.s.): 1: 21/18 of 30, 3/0; 2: 21/17 of 30, 5/1; 3: 21/19 of 30, 3/1; 4: 18/17 of 30, 2/1; 5: 22/18 of 30, 4/0; 6: 22/18 of 30, 5/1; 7: 20/17 of 30, 4/1; 8: 20/15 of 30, 5/0; 9: 22/18 of 30, 4/0; 10: 21/18 of 30, 6/3; 11: 19/18 of 30, 2/1; 12: 23/15 of 30, 8/0 x
- arm c_unfavourable success C vs I (ref worse): 1: 21/30 of 30, 0/9; 2: 21/29 of 30, 1/9; 3: 21/28 of 30, 1/8; 4: 18/29 of 30, 0/11; 5: 22/29 of 30, 0/7; 6: 22/29 of 30, 0/7; 7: 20/29 of 30, 0/9; 8: 20/29 of 30, 0/9; 9: 22/30 of 30, 0/8; 10: 21/30 of 30, 0/9; 11: 19/27 of 30, 0/8; 12: 23/25 of 30, 3/5
- arm c_unfavourable success J vs C (ref n.s.): 1: 27/21 of 30, 7/1; 2: 26/21 of 30, 5/0; 3: 24/21 of 30, 4/1; 4: 23/18 of 30, 6/1; 5: 25/22 of 30, 4/1; 6: 22/22 of 30, 4/4; 7: 24/20 of 30, 5/1; 8: 22/20 of 30, 5/3; 9: 26/22 of 30, 5/1; 10: 26/21 of 30, 5/0; 11: 23/19 of 30, 5/1; 12: 21/23 of 30, 4/6
- arm c_unfavourable success G vs C (ref better): 1: 24/21 of 30, 3/0; 2: 21/21 of 30, 1/1 x; 3: 23/21 of 30, 2/0; 4: 19/18 of 30, 1/0; 5: 23/22 of 30, 1/0; 6: 24/22 of 30, 2/0; 7: 21/20 of 30, 2/1; 8: 22/20 of 30, 3/1; 9: 22/22 of 30, 1/1 x; 10: 25/21 of 30, 4/0; 11: 19/19 of 30, 1/1 x; 12: 22/23 of 30, 1/2 x
- arm c_unfavourable bad_units C vs F (ref n.s.): 1: 0/0 of 30, 0/0; 2: 0/1 of 30, 1/0; 3: 0/1 of 30, 1/0; 4: 0/0 of 30, 0/0; 5: 0/0 of 30, 0/0; 6: 0/0 of 30, 0/0; 7: 0/0 of 30, 0/0; 8: 0/0 of 30, 0/0; 9: 0/0 of 30, 0/0; 10: 0/0 of 30, 0/0; 11: 0/1 of 30, 1/0; 12: 0/0 of 30, 0/0
- arm c_unfavourable bad_units C vs H (ref n.s.): 1: 0/1 of 30, 1/0; 2: 0/2 of 30, 2/0; 3: 0/0 of 30, 0/0; 4: 0/0 of 30, 0/0; 5: 0/0 of 30, 0/0; 6: 0/0 of 30, 0/0; 7: 0/1 of 30, 1/0; 8: 0/1 of 30, 1/0; 9: 0/0 of 30, 0/0; 10: 0/1 of 30, 1/0; 11: 0/0 of 30, 0/0; 12: 0/0 of 30, 0/0
- arm c_unfavourable bad_units C vs I (ref n.s.): 1: 0/0 of 30, 0/0; 2: 0/1 of 30, 1/0; 3: 0/1 of 30, 1/0; 4: 0/0 of 30, 0/0; 5: 0/0 of 30, 0/0; 6: 0/0 of 30, 0/0; 7: 0/0 of 30, 0/0; 8: 0/0 of 30, 0/0; 9: 0/0 of 30, 0/0; 10: 0/0 of 30, 0/0; 11: 0/1 of 30, 1/0; 12: 0/0 of 30, 0/0
- arm c_unfavourable bad_units J vs C (ref n.s.): 1: 0/0 of 30, 0/0; 2: 0/0 of 30, 0/0; 3: 0/0 of 30, 0/0; 4: 1/0 of 30, 0/1; 5: 0/0 of 30, 0/0; 6: 2/0 of 30, 0/2; 7: 0/0 of 30, 0/0; 8: 2/0 of 30, 0/2; 9: 0/0 of 30, 0/0; 10: 0/0 of 30, 0/0; 11: 1/0 of 30, 0/1; 12: 1/0 of 30, 0/1
- arm c_unfavourable bad_units G vs C (ref n.s.): 1: 0/0 of 30, 0/0; 2: 0/0 of 30, 0/0; 3: 0/0 of 30, 0/0; 4: 0/0 of 30, 0/0; 5: 0/0 of 30, 0/0; 6: 0/0 of 30, 0/0; 7: 0/0 of 30, 0/0; 8: 0/0 of 30, 0/0; 9: 0/0 of 30, 0/0; 10: 0/0 of 30, 0/0; 11: 0/0 of 30, 0/0; 12: 0/0 of 30, 0/0
- arm latching_good success C vs F (ref worse): 1: 33/46 of 50, 1/14; 2: 38/47 of 50, 1/10; 3: 37/46 of 50, 2/11; 4: 36/39 of 50, 6/9; 5: 41/47 of 50, 1/7; 6: 37/37 of 50, 8/8 x; 7: 34/39 of 50, 4/9; 8: 38/38 of 50, 6/6 x; 9: 36/47 of 50, 0/11; 10: 37/45 of 50, 2/10; 11: 23/38 of 50, 3/18; 12: 34/31 of 50, 8/5 x
- arm latching_good success C vs H (ref better): 1: 33/23 of 50, 15/5; 2: 38/23 of 50, 18/3; 3: 37/19 of 50, 19/1; 4: 36/18 of 50, 20/2; 5: 41/21 of 50, 20/0; 6: 37/19 of 50, 19/1; 7: 34/18 of 50, 18/2; 8: 38/17 of 50, 22/1; 9: 36/20 of 50, 21/5; 10: 37/23 of 50, 16/2; 11: 23/14 of 50, 14/5; 12: 34/21 of 50, 15/2
- arm latching_good success C vs I (ref worse): 1: 33/18 of 50, 19/4 x; 2: 38/47 of 50, 1/10; 3: 37/46 of 50, 2/11; 4: 36/39 of 50, 6/9; 5: 41/47 of 50, 1/7; 6: 37/39 of 50, 6/8; 7: 34/39 of 50, 4/9; 8: 38/38 of 50, 6/6 x; 9: 36/47 of 50, 0/11; 10: 37/45 of 50, 2/10; 11: 23/25 of 50, 8/10; 12: 34/31 of 50, 7/4 x
- arm latching_good success J vs C (ref better): 1: 42/33 of 50, 13/4; 2: 47/38 of 50, 10/1; 3: 46/37 of 50, 11/2; 4: 39/36 of 50, 9/6; 5: 47/41 of 50, 7/1; 6: 39/37 of 50, 8/6; 7: 39/34 of 50, 9/4; 8: 38/38 of 50, 6/6 x; 9: 47/36 of 50, 11/0; 10: 45/37 of 50, 10/2; 11: 32/23 of 50, 14/5; 12: 33/34 of 50, 6/7 x
- arm latching_good success G vs C (ref better): 1: 37/33 of 50, 6/2; 2: 37/38 of 50, 4/5 x; 3: 44/37 of 50, 9/2; 4: 39/36 of 50, 4/1; 5: 46/41 of 50, 5/0; 6: 37/37 of 50, 4/4 x; 7: 37/34 of 50, 4/1; 8: 43/38 of 50, 6/1; 9: 42/36 of 50, 9/3; 10: 37/37 of 50, 7/7 x; 11: 31/23 of 50, 9/1; 12: 30/34 of 50, 4/8 x
- arm latching_good bad_units C vs F (ref n.s.): 1: 0/0 of 50, 0/0; 2: 0/0 of 50, 0/0; 3: 0/0 of 50, 0/0; 4: 0/0 of 50, 0/0; 5: 0/0 of 50, 0/0; 6: 0/2 of 50, 2/0; 7: 0/0 of 50, 0/0; 8: 0/0 of 50, 0/0; 9: 0/0 of 50, 0/0; 10: 1/1 of 50, 1/1; 11: 0/0 of 50, 0/0; 12: 0/2 of 50, 2/0
- arm latching_good bad_units C vs H (ref n.s.): 1: 0/0 of 50, 0/0; 2: 0/0 of 50, 0/0; 3: 0/0 of 50, 0/0; 4: 0/0 of 50, 0/0; 5: 0/0 of 50, 0/0; 6: 0/0 of 50, 0/0; 7: 0/0 of 50, 0/0; 8: 0/0 of 50, 0/0; 9: 0/0 of 50, 0/0; 10: 1/0 of 50, 0/1; 11: 0/0 of 50, 0/0; 12: 0/0 of 50, 0/0
- arm latching_good bad_units C vs I (ref n.s.): 1: 0/0 of 50, 0/0; 2: 0/0 of 50, 0/0; 3: 0/0 of 50, 0/0; 4: 0/0 of 50, 0/0; 5: 0/0 of 50, 0/0; 6: 0/0 of 50, 0/0; 7: 0/0 of 50, 0/0; 8: 0/0 of 50, 0/0; 9: 0/0 of 50, 0/0; 10: 1/1 of 50, 1/1; 11: 0/0 of 50, 0/0; 12: 0/1 of 50, 1/0
- arm latching_good bad_units J vs C (ref n.s.): 1: 0/0 of 50, 0/0; 2: 0/0 of 50, 0/0; 3: 0/0 of 50, 0/0; 4: 0/0 of 50, 0/0; 5: 0/0 of 50, 0/0; 6: 0/0 of 50, 0/0; 7: 0/0 of 50, 0/0; 8: 0/0 of 50, 0/0; 9: 0/0 of 50, 0/0; 10: 1/1 of 50, 1/1; 11: 0/0 of 50, 0/0; 12: 0/0 of 50, 0/0
- arm latching_good bad_units G vs C (ref n.s.): 1: 0/0 of 50, 0/0; 2: 0/0 of 50, 0/0; 3: 0/0 of 50, 0/0; 4: 0/0 of 50, 0/0; 5: 0/0 of 50, 0/0; 6: 0/0 of 50, 0/0; 7: 0/0 of 50, 0/0; 8: 0/0 of 50, 0/0; 9: 0/0 of 50, 0/0; 10: 0/1 of 50, 1/0; 11: 0/0 of 50, 0/0; 12: 0/0 of 50, 0/0
- arm all_good_parts bad_units C vs F (ref better): 1: 0/4 of 170, 4/0; 2: 0/5 of 170, 5/0; 3: 0/5 of 170, 5/0; 4: 0/4 of 170, 4/0; 5: 0/4 of 170, 4/0; 6: 0/7 of 170, 7/0; 7: 0/3 of 170, 3/0; 8: 0/4 of 170, 4/0; 9: 0/4 of 170, 4/0; 10: 1/5 of 170, 5/1; 11: 0/4 of 170, 4/0; 12: 0/5 of 170, 5/0
- arm all_good_parts bad_units C vs H (ref better): 1: 0/4 of 170, 4/0; 2: 0/5 of 170, 5/0; 3: 0/2 of 170, 2/0; 4: 0/1 of 170, 1/0; 5: 0/2 of 170, 2/0; 6: 0/1 of 170, 1/0; 7: 0/2 of 170, 2/0; 8: 0/2 of 170, 2/0; 9: 0/3 of 170, 3/0; 10: 1/4 of 170, 4/1; 11: 0/1 of 170, 1/0; 12: 0/1 of 170, 1/0
- arm all_good_parts bad_units C vs I (ref better): 1: 0/4 of 170, 4/0; 2: 0/5 of 170, 5/0; 3: 0/5 of 170, 5/0; 4: 0/4 of 170, 4/0; 5: 0/4 of 170, 4/0; 6: 0/5 of 170, 5/0; 7: 0/3 of 170, 3/0; 8: 0/4 of 170, 4/0; 9: 0/4 of 170, 4/0; 10: 1/5 of 170, 5/1; 11: 0/4 of 170, 4/0; 12: 0/4 of 170, 4/0
- arm all_good_parts bad_units J vs C (ref n.s.): 1: 0/0 of 170, 0/0; 2: 0/0 of 170, 0/0; 3: 0/0 of 170, 0/0; 4: 8/0 of 170, 0/8 x; 5: 0/0 of 170, 0/0; 6: 5/0 of 170, 0/5; 7: 3/0 of 170, 0/3; 8: 5/0 of 170, 0/5; 9: 0/0 of 170, 0/0; 10: 1/1 of 170, 1/1; 11: 4/0 of 170, 0/4; 12: 5/0 of 170, 0/5
- arm all_good_parts bad_units G vs C (ref n.s.): 1: 0/0 of 170, 0/0; 2: 0/0 of 170, 0/0; 3: 0/0 of 170, 0/0; 4: 0/0 of 170, 0/0; 5: 0/0 of 170, 0/0; 6: 0/0 of 170, 0/0; 7: 0/0 of 170, 0/0; 8: 0/0 of 170, 0/0; 9: 0/0 of 170, 0/0; 10: 0/1 of 170, 1/0; 11: 0/0 of 170, 0/0; 12: 0/0 of 170, 0/0
- arm bad_parts bad_units C vs H (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- arm bad_parts bad_units C vs I (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- arm bad_parts bad_units J vs C (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0
- arm bad_parts bad_units G vs C (ref n.s.): 1: 0/0 of 12, 0/0; 2: 0/0 of 12, 0/0; 3: 0/0 of 12, 0/0; 4: 0/0 of 12, 0/0; 5: 0/0 of 12, 0/0; 6: 0/0 of 12, 0/0; 7: 0/0 of 12, 0/0; 8: 0/0 of 12, 0/0; 9: 0/0 of 12, 0/0; 10: 0/0 of 12, 0/0; 11: 0/0 of 12, 0/0; 12: 0/0 of 12, 0/0

## Bad units and bad parts passed, all variants

| Machine | Controller | Good-part trials | Bad units (all variants) | Wilson 95% upper | Variants with any | Bad parts passed / trials | Wilson 95% upper | Variants with any |
|---|---|---|---|---|---|---|---|---|
| gantry | C | 1820 | 1 | 0.31% | 1 | 0 / 156 | 2.40% | 0 |
| gantry | F | 1820 | 75 | 5.13% | 13 | 146 / 156 | 96.48% | 13 |
| gantry | H | 1820 | 73 | 5.01% | 13 | 0 / 156 | 2.40% | 0 |
| gantry | I | 1820 | 75 | 5.13% | 13 | 0 / 156 | 2.40% | 0 |
| gantry | J | 1820 | 3 | 0.48% | 2 | 0 / 156 | 2.40% | 0 |
| gantry | G | 1820 | 0 | 0.21% | 0 | 0 / 156 | 2.40% | 0 |
| arm | C | 2210 | 1 | 0.26% | 1 | 0 / 156 | 2.40% | 0 |
| arm | F | 2210 | 59 | 3.43% | 13 | 117 / 156 | 81.14% | 13 |
| arm | H | 2210 | 30 | 1.93% | 13 | 0 / 156 | 2.40% | 0 |
| arm | I | 2210 | 56 | 3.28% | 13 | 0 / 156 | 2.40% | 0 |
| arm | J | 2210 | 31 | 1.98% | 7 | 0 / 156 | 2.40% | 0 |
| arm | G | 2210 | 0 | 0.17% | 0 | 0 / 156 | 2.40% | 0 |

## Every bad unit C or G passed, every bad part C, G, H, I or J passed

| Machine | Variant | Controller | Condition | Trial | Depth mm | Lateral mm | Tilt deg | Yaw deg | Failure | gt_seated | declared |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry | 10 | C | noise_2mm | 6 | 14.81 | 0.22 | 1.48 | 0.13 | penetration_violation | True | True |
| arm | 10 | C | mf_noise_1mm | 15 | 7.74 | 0.21 | 3.11 | -0.08 | false_accept | False | True |

## Controls (flag only)

| Machine | Variant | F passed `mf_half_latched` | F passed `mf_broken_latch` | F passed `mf_stubbed_terminal` | lowest `nominal` success over controllers | flag |
|---|---|---|---|---|---|---|
| gantry | 0 | 2 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 1 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 2 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 3 | 0 / 4 | 4 / 4 | 4 / 4 | 100% | F passed no `mf_half_latched` |
| gantry | 4 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 5 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 6 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 7 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 8 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 9 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 10 | 0 / 4 | 4 / 4 | 4 / 4 | 80% | F passed no `mf_half_latched`; a controller under 90% on `nominal` |
| gantry | 11 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| gantry | 12 | 4 / 4 | 4 / 4 | 4 / 4 | 100% | - |
| arm | 0 | 4 / 4 | 4 / 4 | 2 / 4 | 100% | - |
| arm | 1 | 3 / 4 | 4 / 4 | 0 / 4 | 100% | F passed no `mf_stubbed_terminal` |
| arm | 2 | 3 / 4 | 4 / 4 | 0 / 4 | 100% | F passed no `mf_stubbed_terminal` |
| arm | 3 | 4 / 4 | 4 / 4 | 2 / 4 | 100% | - |
| arm | 4 | 4 / 4 | 4 / 4 | 2 / 4 | 100% | - |
| arm | 5 | 4 / 4 | 4 / 4 | 2 / 4 | 100% | - |
| arm | 6 | 3 / 4 | 4 / 4 | 0 / 4 | 100% | F passed no `mf_stubbed_terminal` |
| arm | 7 | 4 / 4 | 4 / 4 | 2 / 4 | 93% | - |
| arm | 8 | 4 / 4 | 4 / 4 | 2 / 4 | 100% | - |
| arm | 9 | 4 / 4 | 4 / 4 | 2 / 4 | 100% | - |
| arm | 10 | 4 / 4 | 4 / 4 | 0 / 4 | 100% | F passed no `mf_stubbed_terminal` |
| arm | 11 | 4 / 4 | 4 / 4 | 2 / 4 | 93% | - |
| arm | 12 | 4 / 4 | 4 / 4 | 0 / 4 | 80% | F passed no `mf_stubbed_terminal`; a controller under 90% on `nominal` |
