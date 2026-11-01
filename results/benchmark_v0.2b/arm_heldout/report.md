| Condition | A: Fixed trajectory success | B: Vision correction success | E: Vision + RCC success | D: Spiral search success | F: Spiral + RCC success | C: Defex adaptive success | G: Defex + learned prior success | C median cycle (s) | C median peak force (N) | C recovery success |
|---|---|---|---|---|---|---|---|---|---|---|
| heldout_mischar_1mm | 6% (3-12) | 26% (18-35) | 52% (42-62) | 88% (80-93) | 91% (84-95) | 95% (89-98) | 96% (90-98) | 10.42 | 24.8 | 88% of 41 |
| heldout_mischar_2mm | 4% (2-10) | 3% (1-8) | 5% (2-11) | 27% (19-36) | 41% (32-51) | 49% (39-59) | 58% (48-67) | 13.79 | 27.3 | 41% of 83 |
| heldout_handeye_bias_1.5mm | 5% (2-11) | 14% (9-22) | 39% (30-49) | 100% (96-100) | 100% (96-100) | 99% (95-100) | 99% (95-100) | 11.40 | 25.8 | 98% of 58 |
| heldout_vision_outliers | 7% (3-14) | 91% (84-95) | 93% (86-97) | 94% (88-97) | 97% (92-99) | 100% (96-100) | 99% (95-100) | 8.17 | 24.2 | 100% of 7 |
| heldout_worst_case | 0% (0-4) | 3% (1-8) | 43% (34-53) | 14% (9-22) | 78% (69-85) | 34% (25-44) | 42% (33-52) | 14.03 | 28.2 | 30% of 88 |

| Overall | A: Fixed trajectory | B: Vision correction | E: Vision + RCC | D: Spiral search | F: Spiral + RCC | C: Defex adaptive | G: Defex + learned prior |
|---|---|---|---|---|---|---|---|
| success rate | 4.4% | 27.4% | 46.4% | 64.6% | 81.4% | 75.4% | 78.8% |
| median cycle time, successes (s) | 4.32 | 4.32 | 6.32 | 10.00 | 8.01 | 9.81 | 10.38 |
| median peak contact force (N) | 43.1 | 36.5 | 24.8 | 24.1 | 8.5 | 25.3 | 25.0 |
| 95th pct peak contact force (N) | 68.4 | 66.8 | 30.4 | 32.4 | 15.1 | 33.9 | 33.9 |
| protective stops | 473 | 348 | 244 | 13 | 4 | 21 | 31 |
| max measured wrist torque (N m; stop at 0.6) | 0.601 | 0.617 | 0.600 | 0.633 | 0.357 | 0.781 | 0.864 |
| mean retries | 0.00 | 0.00 | 0.00 | 0.28 | 0.13 | 1.80 | 1.48 |
| max penetration (mm) | 0.0341 | 0.0300 | 0.0921 | 0.0151 | 0.0782 | 0.0265 | 0.0265 |
| false accepts (declared success, not seated) | n/a (no self-verification) | n/a (no self-verification) | n/a (no self-verification) | 19 | 52 | 5 | 7 |
