| Condition | A: Fixed trajectory success | B: Vision correction success | E: Vision + RCC success | D: Spiral search success | F: Spiral + RCC success | C: Defex adaptive success | G: Defex + learned prior success | C median cycle (s) | C median peak force (N) | C recovery success |
|---|---|---|---|---|---|---|---|---|---|---|
| mf_nominal | 100% (98-100) | 84% (78-88) | 88% (83-92) | 68% (61-74) | 100% (98-100) | 100% (98-100) | 100% (98-100) | 8.30 | 30.5 | 100% of 26 |
| mf_moderate | 0% (0-3) | 80% (73-85) | 86% (81-91) | 66% (59-72) | 100% (97-100) | 100% (97-100) | 100% (98-100) | 8.32 | 31.3 | 97% of 36 |
| mf_noise_1mm | 0% (0-3) | 9% (6-14) | 16% (11-21) | 33% (27-40) | 86% (81-90) | 73% (66-79) | 78% (72-84) | 12.62 | 30.7 | 70% of 174 |
| mf_half_latched | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 17.2 | 0% of 200 |
| mf_broken_latch | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 32.8 | 0% of 200 |
| mf_stubbed_terminal | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 15.5 | 0% of 200 |
| mf_wrong_polarization | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | 0% (0-2) | nan | 25.9 | 0% of 200 |

| Overall | A: Fixed trajectory | B: Vision correction | E: Vision + RCC | D: Spiral search | F: Spiral + RCC | C: Defex adaptive | G: Defex + learned prior |
|---|---|---|---|---|---|---|---|
| success rate | 14.4% | 24.6% | 27.2% | 23.7% | 40.8% | 38.9% | 39.8% |
| median cycle time, successes (s) | 3.85 | 3.84 | 5.26 | 6.09 | 5.35 | 8.36 | 8.37 |
| median peak contact force (N) | 48.5 | 45.1 | 25.6 | 19.8 | 15.6 | 25.9 | 26.0 |
| 95th pct peak contact force (N) | 67.6 | 68.6 | 48.3 | 40.2 | 18.4 | 41.3 | 41.5 |
| protective stops | 1192 | 812 | 734 | 5 | 0 | 21 | 22 |
| max measured wrist torque (N m; stop at 0.6) | 0.744 | 0.638 | 0.313 | 0.605 | 0.234 | 0.648 | 0.811 |
| mean retries | 0.00 | 0.00 | 0.00 | 0.24 | 0.15 | 3.28 | 3.21 |
| max penetration (mm) | 0.0385 | 0.0496 | 0.1024 | 0.0121 | 0.1116 | 0.0263 | 0.0263 |
| false accepts (declared success, not seated) | n/a (no self-verification) | n/a (no self-verification) | n/a (no self-verification) | 194 | 579 | 0 | 0 |
