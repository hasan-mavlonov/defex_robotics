| Condition | A: Fixed trajectory success | B: Vision correction success | C: Defex adaptive success | C median cycle (s) | C median peak force (N) | C recovery success |
|---|---|---|---|---|---|---|
| nominal | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.12 | 5.9 | n/a |
| lateral_1mm | 100% (96-100) | 99% (95-100) | 100% (96-100) | 5.13 | 5.9 | n/a |
| lateral_3mm | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.12 | 5.9 | n/a |
| lateral_5mm | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.09 | 6.0 | n/a |
| yaw_2deg | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.11 | 5.9 | n/a |
| yaw_5deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.11 | 5.9 | n/a |
| yaw_10deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.11 | 5.9 | n/a |
| tilt_2deg | 100% (96-100) | 100% (96-100) | 100% (96-100) | 5.11 | 5.9 | n/a |
| tilt_5deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.11 | 5.9 | n/a |
| tilt_10deg | 0% (0-4) | 100% (96-100) | 100% (96-100) | 5.11 | 5.9 | n/a |
| noise_0mm | 14% (9-22) | 100% (96-100) | 100% (96-100) | 4.74 | 5.8 | n/a |
| noise_0.5mm | 9% (5-16) | 92% (85-96) | 100% (96-100) | 5.42 | 6.3 | 100% of 4 |
| noise_1mm | 12% (7-20) | 49% (39-59) | 100% (96-100) | 7.74 | 7.7 | 100% of 40 |
| noise_2mm | 9% (5-16) | 7% (3-14) | 89% (81-94) | 10.23 | 8.0 | 87% of 86 |
| friction_0.1 | 16% (10-24) | 100% (96-100) | 100% (96-100) | 5.13 | 5.8 | n/a |
| friction_0.3 | 14% (9-22) | 100% (96-100) | 100% (96-100) | 5.11 | 5.8 | n/a |
| friction_0.6 | 6% (3-12) | 99% (95-100) | 100% (96-100) | 5.15 | 7.4 | n/a |
| friction_1 | 4% (2-10) | 93% (86-97) | 99% (95-100) | 4.52 | 5.8 | 80% of 5 |
| generalization_combined | 0% (0-4) | 45% (36-55) | 99% (95-100) | 7.62 | 7.9 | 97% of 35 |
| generalization_tight | 0% (0-4) | 64% (54-73) | 100% (96-100) | 5.21 | 7.7 | 100% of 27 |

| Overall | A: Fixed trajectory | B: Vision correction | C: Defex adaptive |
|---|---|---|---|
| success rate | 24.2% | 87.4% | 99.4% |
| median cycle time, successes (s) | 4.32 | 4.31 | 5.14 |
| median peak contact force (N) | 30.3 | 7.4 | 6.1 |
| 95th pct peak contact force (N) | 30.5 | 30.4 | 8.8 |
| protective stops | 1281 | 226 | 0 |
| mean retries | 0.00 | 0.00 | 0.19 |
| max penetration (mm) | 0.0896 | 0.1408 | 0.0582 |
| false accepts (declared success, not seated) | n/a (no self-verification) | n/a (no self-verification) | 0 |
