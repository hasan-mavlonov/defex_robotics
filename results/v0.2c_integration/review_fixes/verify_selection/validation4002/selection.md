Rule applied to `results/v0.2c_integration/review_fixes/verify_selection/validation4002` (C only, latching + latch_spread suites, both backends).

| Variant | Good parts seated (95% CI) | Bad units passed (bad-part trials) | False rejects | Protective stops | Median / p95 cycle (s) | vs w3: w3-only / variant-only (McNemar p) | Eligible |
|---|---|---|---|---|---|---|---|
| w3 | 465/540 = 86.1% (82.9-88.8) | 5 (420) | 1 | 15 | 8.25 / 14.16 | reference | no |
| noclick | 466/540 = 86.3% (83.1-88.9) | 7 (420) | 0 | 15 | 8.25 / 14.16 | 0 / 1 (1) | no |
| w60 | 531/540 = 98.3% (96.9-99.1) | 6 (420) | 0 | 15 | 8.25 / 14.13 | 0 / 66 (<1e-6) | no |
| w80 | 531/540 = 98.3% (96.9-99.1) | 79 (420) | 0 | 14 | 8.25 / 14.19 | 0 / 66 (<1e-6) | no |
| w60f | 532/540 = 98.5% (97.1-99.2) | 0 (420) | 0 | 16 | 8.56 / 14.46 | 0 / 67 (<1e-6) | yes |
| w80f | 532/540 = 98.5% (97.1-99.2) | 0 (420) | 0 | 16 | 8.56 / 14.50 | 0 / 67 (<1e-6) | yes |

gantry:

| Variant | Good parts seated | Bad units passed | False rejects | Stops |
|---|---|---|---|---|
| w3 | 232/270 | 1 | 0 | 15 |
| noclick | 232/270 | 2 | 0 | 15 |
| w60 | 266/270 | 1 | 0 | 15 |
| w80 | 266/270 | 35 | 0 | 14 |
| w60f | 267/270 | 0 | 0 | 16 |
| w80f | 267/270 | 0 | 0 | 16 |

arm:

| Variant | Good parts seated | Bad units passed | False rejects | Stops |
|---|---|---|---|---|
| w3 | 233/270 | 4 | 1 | 0 |
| noclick | 234/270 | 5 | 0 | 0 |
| w60 | 265/270 | 5 | 0 | 0 |
| w80 | 265/270 | 44 | 0 | 0 |
| w60f | 265/270 | 0 | 0 | 0 |
| w80f | 265/270 | 0 | 0 | 0 |

Ranking (good parts seated, then median, then p95, then rule order): w60f > w80f

Decision: install w60f.
