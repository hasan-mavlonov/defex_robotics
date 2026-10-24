| Condition | A: Fixed trajectory success | B: Vision correction success | C: Defex adaptive success | C median cycle (s) | C median peak force (N) | C recovery success |
|---|---|---|---|---|---|---|
| nominal | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.37 | 5.8 | n/a |
| lateral_1mm | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.40 | 5.8 | n/a |
| lateral_3mm | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.37 | 5.8 | n/a |
| lateral_5mm | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.39 | 5.8 | n/a |
| yaw_2deg | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.38 | 5.8 | n/a |
| yaw_5deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.41 | 5.8 | n/a |
| yaw_10deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.37 | 5.8 | n/a |
| tilt_2deg | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.39 | 5.8 | n/a |
| tilt_5deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.39 | 5.8 | n/a |
| tilt_10deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.37 | 5.8 | n/a |
| noise_0mm | 13% (8-21) | 100% (96-100) | 100% (96-100) | 5.01 | 5.8 | n/a |
| noise_0.5mm | 8% (4-15) | 90% (83-94) | 100% (96-100) | 5.71 | 5.8 | 100% of 3 |
| noise_1mm | 11% (6-19) | 36% (27-46) | 100% (96-100) | 8.33 | 7.8 | 100% of 43 |
| noise_2mm | 16% (10-24) | 5% (2-11) | 85% (77-91) | 11.05 | 8.0 | 81% of 77 |
| friction_0.1 | 8% (4-15) | 100% (96-100) | 100% (96-100) | 5.38 | 5.8 | n/a |
| friction_0.3 | 8% (4-15) | 100% (96-100) | 100% (96-100) | 5.39 | 5.8 | n/a |
| friction_0.6 | 3% (1-8) | 99% (95-100) | 100% (96-100) | 5.38 | 5.9 | n/a |
| friction_1 | 2% (1-7) | 89% (81-94) | 100% (96-100) | 5.37 | 5.8 | 100% of 8 |
| generalization_combined | 0% (0-4) | 40% (31-50) | 100% (96-100) | 8.42 | 7.9 | 100% of 49 |
| generalization_tight | 1% (0-5) | 59% (49-68) | 100% (96-100) | 5.48 | 6.3 | 100% of 32 |

| Overall | A: Fixed trajectory | B: Vision correction | C: Defex adaptive |
|---|---|---|---|
| success rate | 23.5% | 85.9% | 99.2% |
| median cycle time, successes (s) | 4.32 | 4.31 | 5.41 |
| median peak contact force (N) | 30.3 | 7.5 | 5.8 |
| 95th pct peak contact force (N) | 30.5 | 30.4 | 8.1 |
| protective stops | 1302 | 234 | 1 |
| mean retries | 0.00 | 0.00 | 0.22 |
| max penetration (mm) | 0.0897 | 0.1480 | 0.0612 |
| false accepts (declared success, not seated) | n/a (no self-verification) | n/a (no self-verification) | 0 |
