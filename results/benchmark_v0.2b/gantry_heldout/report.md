| Condition | A: Fixed trajectory success | B: Vision correction success | E: Vision + RCC success | D: Spiral search success | F: Spiral + RCC success | C: Defex adaptive success | G: Defex + learned prior success | C median cycle (s) | C median peak force (N) | C recovery success |
|---|---|---|---|---|---|---|---|---|---|---|
| heldout_mischar_1mm | 11% (6-19) | 41% (32-51) | 57% (47-66) | 90% (83-94) | 92% (85-96) | 96% (90-98) | 97% (92-99) | 5.97 | 9.7 | 90% of 39 |
| heldout_mischar_2mm | 7% (3-14) | 6% (3-12) | 10% (6-17) | 39% (30-49) | 46% (37-56) | 85% (77-91) | 84% (76-90) | 10.24 | 9.7 | 80% of 76 |
| heldout_handeye_bias_1.5mm | 9% (5-16) | 31% (23-41) | 37% (28-47) | 100% (96-100) | 100% (96-100) | 100% (96-100) | 100% (96-100) | 7.51 | 9.6 | 100% of 59 |
| heldout_vision_outliers | 15% (9-23) | 93% (86-97) | 93% (86-97) | 98% (93-99) | 100% (96-100) | 100% (96-100) | 98% (93-99) | 5.27 | 9.1 | 100% of 7 |
| heldout_worst_case | 0% (0-4) | 5% (2-11) | 46% (37-56) | 16% (10-24) | 83% (74-89) | 56% (46-65) | 75% (66-82) | 7.84 | 10.0 | 42% of 76 |

| Overall | A: Fixed trajectory | B: Vision correction | E: Vision + RCC | D: Spiral search | F: Spiral + RCC | C: Defex adaptive | G: Defex + learned prior |
|---|---|---|---|---|---|---|---|
| success rate | 8.4% | 35.2% | 48.6% | 68.6% | 84.2% | 87.4% | 90.8% |
| median cycle time, successes (s) | 4.32 | 4.32 | 6.32 | 5.13 | 4.32 | 6.47 | 6.68 |
| median peak contact force (N) | 30.4 | 30.3 | 23.0 | 8.7 | 4.7 | 9.7 | 9.6 |
| 95th pct peak contact force (N) | 30.5 | 30.5 | 30.2 | 14.1 | 12.9 | 16.6 | 16.5 |
| protective stops | 439 | 290 | 240 | 0 | 0 | 0 | 0 |
| max measured wrist torque (N m; stop at 0.6) | 0.471 | 0.453 | 0.415 | 0.231 | 0.259 | 0.408 | 0.356 |
| mean retries | 0.00 | 0.00 | 0.00 | 0.23 | 0.10 | 1.72 | 1.36 |
| max penetration (mm) | 0.1070 | 0.1057 | 0.0883 | 0.0542 | 0.1130 | 0.0516 | 0.0516 |
| false accepts (declared success, not seated) | n/a (no self-verification) | n/a (no self-verification) | n/a (no self-verification) | 28 | 47 | 0 | 1 |
