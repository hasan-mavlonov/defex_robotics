| Condition | A: Fixed trajectory success | B: Vision correction success | E: Vision + RCC success | D: Spiral search success | F: Spiral + RCC success | C: Defex adaptive success | G: Defex + learned prior success | C median cycle (s) | C median peak force (N) | C recovery success |
|---|---|---|---|---|---|---|---|---|---|---|
| mf_nominal | 100% (98-100) | 86% (81-90) | 87% (82-91) | 66% (60-73) | 99% (96-100) | 100% (98-100) | 100% (98-100) | 5.68 | 15.9 | 100% of 26 |
| mf_moderate | 2% (1-6) | 80% (74-85) | 82% (76-87) | 67% (60-73) | 98% (94-99) | 100% (97-100) | 100% (97-100) | 5.69 | 18.9 | 100% of 36 |
| mf_noise_1mm | 2% (1-4) | 14% (10-20) | 18% (13-23) | 36% (30-43) | 70% (64-76) | 88% (82-91) | 96% (92-98) | 8.30 | 29.0 | 86% of 165 |
| mf_half_latched | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 24.3 | 0% of 190 |
| mf_broken_latch | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 15.9 | 0% of 200 |
| mf_stubbed_terminal | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 9.4 | 0% of 200 |
| mf_wrong_polarization | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 29.0 | 0% of 200 |

| Overall | A: Fixed trajectory | B: Vision correction | E: Vision + RCC | D: Spiral search | F: Spiral + RCC | C: Defex adaptive | G: Defex + learned prior |
|---|---|---|---|---|---|---|---|
| success rate | 14.9% | 25.9% | 26.6% | 24.3% | 38.1% | 41.0% | 42.2% |
| median cycle time, successes (s) | 3.75 | 3.75 | 5.07 | 3.53 | 3.26 | 5.72 | 5.72 |
| median peak contact force (N) | 48.4 | 19.2 | 17.0 | 12.3 | 15.8 | 21.7 | 21.7 |
| 95th pct peak contact force (N) | 48.5 | 48.4 | 48.2 | 22.9 | 15.9 | 34.0 | 44.4 |
| protective stops | 1180 | 570 | 543 | 21 | 68 | 71 | 96 |
| max measured wrist torque (N m; stop at 0.6) | 0.600 | 0.638 | 0.238 | 0.455 | 0.166 | 0.442 | 0.465 |
| mean retries | 0.00 | 0.00 | 0.00 | 0.21 | 0.20 | 4.04 | 3.95 |
| max penetration (mm) | 0.0784 | 0.0712 | 0.1110 | 0.0354 | 0.1184 | 0.1077 | 0.1229 |
| false accepts (declared success, not seated) | n/a (no self-verification) | n/a (no self-verification) | n/a (no self-verification) | 251 | 491 | 0 | 0 |
