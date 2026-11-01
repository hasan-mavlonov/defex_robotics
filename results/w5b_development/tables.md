## Arm, standard set, seed 2026 (20 trials per cell)

| Controller | Success before | Success after | Escapes: failed units passed as good (before / after) | Protective stops (before / after) | Median cycle of successes, s (before / after) |
|---|---|---|---|---|---|
| A fixed | 24% | 24% | 0 / 0 | 76 / 76 | 4.32 / 4.32 |
| B correction | 62% | 62% | 5 / 5 | 33 / 33 | 4.31 / 4.31 |
| E correction_rcc | 76% | 76% | 2 / 2 | 22 / 22 | 6.32 / 6.32 |
| D spiral | 83% | 83% | 6 / 6 | 2 / 2 | 6.52 / 6.52 |
| F spiral_rcc | 84% | 84% | 10 / 10 | 0 / 0 | 6.51 / 6.51 |
| C adaptive | 39% | 86% | 0 / 0 | 44 / 3 | 11.39 / 8.41 |

Per condition, successes/escapes, before -> after:

| Condition | A | B | E | D | F | C |
|---|---|---|---|---|---|---|
| nominal | 20/0 -> 20/0 | 19/0 -> 19/0 | 20/0 -> 20/0 | 20/0 -> 20/0 | 20/0 -> 20/0 | 4/0 -> 20/0 |
| lateral_3mm | 0/0 -> 0/0 | 20/0 -> 20/0 | 20/0 -> 20/0 | 20/0 -> 20/0 | 20/0 -> 20/0 | 6/0 -> 20/0 |
| noise_1mm | 2/0 -> 2/0 | 4/4 -> 4/4 | 13/2 -> 13/2 | 15/4 -> 15/4 | 15/4 -> 15/4 | 8/0 -> 18/0 |
| noise_2mm | 1/0 -> 1/0 | 1/1 -> 1/1 | 3/0 -> 3/0 | 9/2 -> 9/2 | 9/6 -> 9/6 | 5/0 -> 10/0 |
| friction_1 | 1/0 -> 1/0 | 18/0 -> 18/0 | 20/0 -> 20/0 | 19/0 -> 19/0 | 20/0 -> 20/0 | 16/0 -> 18/0 |

C's failures after the change:

| Condition | aborted:time_limit | protective_stop |
|---|---|---|
| noise_1mm | 2 | 0 |
| noise_2mm | 7 | 3 |
| friction_1 | 2 | 0 |

## Arm, latching suite, seed 2026 (20 trials per cell)

| Controller | Success before | Success after | Escapes: failed units passed as good (before / after) | Protective stops (before / after) | Median cycle of successes, s (before / after) |
|---|---|---|---|---|---|
| A fixed | 15% | 15% | 0 / 0 | 119 / 119 | 3.85 / 3.85 |
| B correction | 24% | 24% | 25 / 25 | 81 / 81 | 3.84 / 3.84 |
| E correction_rcc | 24% | 24% | 31 / 31 | 75 / 75 | 5.26 / 5.26 |
| D spiral | 22% | 22% | 33 / 33 | 1 / 1 | 5.65 / 5.65 |
| F spiral_rcc | 41% | 41% | 56 / 56 | 0 / 0 | 5.44 / 5.44 |
| C adaptive | 29% | 38% | 0 / 0 | 1 / 1 | 8.26 / 8.29 |

Per condition, successes/escapes, before -> after:

| Condition | A | B | E | D | F | C |
|---|---|---|---|---|---|---|
| mf_nominal | 20/0 -> 20/0 | 17/0 -> 17/0 | 17/0 -> 17/0 | 12/0 -> 12/0 | 20/0 -> 20/0 | 19/0 -> 20/0 |
| mf_moderate | 1/0 -> 1/0 | 16/0 -> 16/0 | 16/0 -> 16/0 | 14/0 -> 14/0 | 20/0 -> 20/0 | 18/0 -> 20/0 |
| mf_noise_1mm | 0/0 -> 0/0 | 1/0 -> 1/0 | 1/0 -> 1/0 | 5/0 -> 5/0 | 17/0 -> 17/0 | 3/0 -> 13/0 |
| mf_half_latched | 0/0 -> 0/0 | 0/8 -> 0/8 | 0/13 -> 0/13 | 0/13 -> 0/13 | 0/20 -> 0/20 | 0/0 -> 0/0 |
| mf_broken_latch | 0/0 -> 0/0 | 0/16 -> 0/16 | 0/17 -> 0/17 | 0/16 -> 0/16 | 0/20 -> 0/20 | 0/0 -> 0/0 |
| mf_stubbed_terminal | 0/0 -> 0/0 | 0/1 -> 0/1 | 0/1 -> 0/1 | 0/4 -> 0/4 | 0/16 -> 0/16 | 0/0 -> 0/0 |
| mf_wrong_polarization | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 |

C's failures after the change:

| Condition | aborted:retry_limit | aborted:time_limit | protective_stop |
|---|---|---|---|
| mf_noise_1mm | 4 | 2 | 1 |
| mf_half_latched | 0 | 20 | 0 |
| mf_broken_latch | 0 | 20 | 0 |
| mf_stubbed_terminal | 0 | 20 | 0 |
| mf_wrong_polarization | 1 | 19 | 0 |

## Arm, standard set, seed 2027 (10 trials per cell)

| Controller | Success before | Success after | Escapes: failed units passed as good (before / after) | Protective stops (before / after) | Median cycle of successes, s (before / after) |
|---|---|---|---|---|---|
| A fixed | 26% | 26% | 0 / 0 | 37 / 37 | 4.32 / 4.32 |
| B correction | 64% | 64% | 1 / 1 | 17 / 17 | 4.31 / 4.31 |
| E correction_rcc | 72% | 72% | 1 / 1 | 13 / 13 | 6.32 / 6.32 |
| D spiral | 82% | 82% | 3 / 3 | 0 / 0 | 6.55 / 6.55 |
| F spiral_rcc | 82% | 82% | 6 / 6 | 0 / 0 | 6.52 / 6.52 |
| C adaptive | 38% | 88% | 0 / 0 | 20 / 0 | 11.19 / 8.50 |

Per condition, successes/escapes, before -> after:

| Condition | A | B | E | D | F | C |
|---|---|---|---|---|---|---|
| nominal | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 5/0 -> 10/0 |
| lateral_3mm | 0/0 -> 0/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 2/0 -> 10/0 |
| noise_1mm | 1/0 -> 1/0 | 4/1 -> 4/1 | 5/1 -> 5/1 | 9/1 -> 9/1 | 9/1 -> 9/1 | 0/0 -> 10/0 |
| noise_2mm | 2/0 -> 2/0 | 0/0 -> 0/0 | 1/0 -> 1/0 | 2/2 -> 2/2 | 2/5 -> 2/5 | 2/0 -> 4/0 |
| friction_1 | 0/0 -> 0/0 | 8/0 -> 8/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 | 10/0 -> 10/0 |

C's failures after the change:

| Condition | aborted:retry_limit | aborted:time_limit |
|---|---|---|
| noise_2mm | 1 | 5 |

## Arm, latching suite, seed 2027 (10 trials per cell)

| Controller | Success before | Success after | Escapes: failed units passed as good (before / after) | Protective stops (before / after) | Median cycle of successes, s (before / after) |
|---|---|---|---|---|---|
| A fixed | 14% | 14% | 0 / 0 | 60 / 60 | 3.85 / 3.85 |
| B correction | 24% | 24% | 13 / 13 | 40 / 40 | 3.84 / 3.84 |
| E correction_rcc | 29% | 29% | 17 / 17 | 33 / 33 | 5.26 / 5.26 |
| D spiral | 23% | 23% | 18 / 18 | 0 / 0 | 5.30 / 5.30 |
| F spiral_rcc | 40% | 40% | 29 / 29 | 0 / 0 | 5.34 / 5.34 |
| C adaptive | 33% | 36% | 0 / 0 | 0 / 3 | 8.29 / 8.35 |

Per condition, successes/escapes, before -> after:

| Condition | A | B | E | D | F | C |
|---|---|---|---|---|---|---|
| mf_nominal | 10/0 -> 10/0 | 9/0 -> 9/0 | 9/0 -> 9/0 | 7/0 -> 7/0 | 10/0 -> 10/0 | 9/0 -> 10/0 |
| mf_moderate | 0/0 -> 0/0 | 8/0 -> 8/0 | 9/0 -> 9/0 | 8/0 -> 8/0 | 10/0 -> 10/0 | 10/0 -> 10/0 |
| mf_noise_1mm | 0/0 -> 0/0 | 0/0 -> 0/0 | 2/0 -> 2/0 | 1/0 -> 1/0 | 8/0 -> 8/0 | 4/0 -> 5/0 |
| mf_half_latched | 0/0 -> 0/0 | 0/6 -> 0/6 | 0/8 -> 0/8 | 0/8 -> 0/8 | 0/10 -> 0/10 | 0/0 -> 0/0 |
| mf_broken_latch | 0/0 -> 0/0 | 0/7 -> 0/7 | 0/9 -> 0/9 | 0/9 -> 0/9 | 0/10 -> 0/10 | 0/0 -> 0/0 |
| mf_stubbed_terminal | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/1 -> 0/1 | 0/9 -> 0/9 | 0/0 -> 0/0 |
| mf_wrong_polarization | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 | 0/0 -> 0/0 |

C's failures after the change:

| Condition | aborted:retry_limit | aborted:time_limit | protective_stop |
|---|---|---|---|
| mf_noise_1mm | 1 | 1 | 3 |
| mf_half_latched | 0 | 10 | 0 |
| mf_broken_latch | 0 | 10 | 0 |
| mf_stubbed_terminal | 0 | 10 | 0 |
| mf_wrong_polarization | 1 | 9 | 0 |

