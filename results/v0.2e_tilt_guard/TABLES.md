| Machine | Suite | Controller | Trials | Latch checks before / after | Verdicts before | Verdicts under the floor before (PASS / FAIL) | Fails before / after | Blocked after | Trials changed |
|---|---|---|---|---|---|---|---|---|---|
| arm | latch_spread | adaptive | 360 | 545 / 545 | 545 | 2 (2 / 0) | 1 / 1 | 2 | 0 |
| arm | latch_spread | adaptive_learned | 360 | 546 / 546 | 546 | 2 (2 / 0) | 1 / 1 | 2 | 0 |
| arm | latch_spread | spiral_rcc_verify | 360 | 473 / 473 | 473 | 358 (358 / 0) | 0 / 0 | 358 | 0 |
| arm | latching | adaptive | 280 | 316 / 316 | 316 | 2 (2 / 0) | 0 / 0 | 2 | 0 |
| arm | latching | adaptive_learned | 280 | 322 / 322 | 322 | 2 (2 / 0) | 0 / 0 | 2 | 0 |
| arm | latching | spiral_rcc_verify | 280 | 280 / 280 | 280 | 204 (204 / 0) | 0 / 0 | 204 | 0 |
| gantry | latch_spread | adaptive | 360 | 492 / 492 | 492 | 0 (0 / 0) | 0 / 0 | 0 | 0 |
| gantry | latch_spread | adaptive_learned | 360 | 489 / 489 | 489 | 0 (0 / 0) | 0 / 0 | 0 | 0 |
| gantry | latch_spread | spiral_rcc_verify | 360 | 439 / 439 | 439 | 331 (331 / 0) | 0 / 0 | 331 | 0 |
| gantry | latching | adaptive | 280 | 307 / 307 | 307 | 0 (0 / 0) | 0 / 0 | 0 | 0 |
| gantry | latching | adaptive_learned | 280 | 312 / 312 | 312 | 0 (0 / 0) | 0 / 0 | 0 | 0 |
| gantry | latching | spiral_rcc_verify | 280 | 301 / 301 | 301 | 219 (219 / 0) | 0 / 0 | 219 | 0 |
| all | | | 3840 | 4822 / 4822 | 4822 | 1120 (1120 / 0) | 2 / 2 | 1120 | 0 |

Verdicts under the floor before, by path into the latch check:

- arm adaptive: detect:floor_impact 4
- arm adaptive_learned: detect:floor_impact 4
- arm spiral_rcc_verify: handover 562
- gantry spiral_rcc_verify: handover 550

Window axial force at every verdict before (N), by machine and path: n, min, p5, median

- arm detect:bottomed: 1202 (0 with no samples); 28.1, 31.9, 32.1
- arm detect:floor_impact: 10 (0 with no samples); 8.2, 8.2, 9.9
- arm detect:stall: 178 (0 with no samples); 23.0, 25.3, 25.8
- arm handover: 562 (562 with no samples); -
- arm proof: 530 (0 with no samples); 34.7, 34.8, 35.1
- gantry detect:bottomed: 1274 (0 with no samples); 20.1, 32.4, 32.7
- gantry detect:stall: 2 (0 with no samples); 34.1, 34.1, 34.1
- gantry handover: 550 (550 with no samples); -
- gantry held_reseat: 2 (0 with no samples); 32.1, 32.1, 32.1
- gantry proof: 512 (0 with no samples); 35.1, 35.1, 35.2

Trials whose row changed (before -> after outcome; under-floor FAIL before?):

- none

Changed trials without an under-floor FAIL before: 0
