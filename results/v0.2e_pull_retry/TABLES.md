# v0.2e pull retry: H and I, rule version 4 (before) against version 5 (after)

Before: `results/v0.2d_pull_retry/dev4` (run at 1f1ca4a; H and I code as at 966a5f5). After: `results/v0.2e_pull_retry/after`. Dev seeds 2026 and 2027, latching and latch_spread suites, 20 trials per condition and seed. Good parts: every condition outside the `bad_part` group. Bad units on good parts and bad parts passed are escapes (not seated as required, no stop, not declared failed).

## Outcomes

| Machine | Suite | Ctrl | Rows differ | Good seated before -> after | Lost / gained (p) | Bad units on good parts | Bad parts passed | Stops good+bad | Trials with a retry (retries) | Median good cycle (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| gantry | latching | H | 182 | 106 -> 106 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 2+7 -> 2+7 | 90 (90) -> 147 (166) | 6.16 -> 6.16 |
| gantry | latching | I | 219 | 118 -> 118 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 0+14 -> 0+14 | 30 (30) -> 125 (131) | 5.48 -> 5.48 |
| gantry | latch_spread | H | 334 | 239 -> 239 of 240 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 120 | 0+15 -> 0+15 | 31 (31) -> 121 (131) | 6.06 -> 6.05 |
| gantry | latch_spread | I | 331 | 240 -> 240 of 240 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 120 | 0+24 -> 0+24 | 26 (26) -> 133 (133) | 5.46 -> 5.46 |
| gantry | **both** | H | 516 | 345 -> 345 of 360 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 280 | 2+22 -> 2+22 | 121 (121) -> 268 (297) | 6.08 -> 6.07 |
| gantry | **both** | I | 550 | 358 -> 358 of 360 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 280 | 0+38 -> 0+38 | 56 (56) -> 258 (264) | 5.46 -> 5.46 |
| arm | latching | H | 179 | 98 -> 101 of 120 | 0 / 3 (0.25) | 0 -> 0 | 0 -> 0 of 160 | 5+0 -> 1+0 | 87 (87) -> 164 (165) | 8.44 -> 8.48 |
| arm | latching | I | 204 | 114 -> 114 of 120 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 160 | 0+0 -> 0+0 | 58 (58) -> 134 (148) | 8.53 -> 8.62 |
| arm | latch_spread | H | 350 | 238 -> 238 of 240 | 0 / 0 (1) | 1 -> 1 | 0 -> 0 of 120 | 0+0 -> 0+0 | 11 (11) -> 136 (137) | 8.42 -> 8.44 |
| arm | latch_spread | I | 358 | 240 -> 240 of 240 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 120 | 0+0 -> 0+0 | 15 (15) -> 130 (143) | 8.51 -> 8.60 |
| arm | **both** | H | 529 | 336 -> 339 of 360 | 0 / 3 (0.25) | 1 -> 1 | 0 -> 0 of 280 | 5+0 -> 1+0 | 98 (98) -> 300 (302) | 8.43 -> 8.46 |
| arm | **both** | I | 562 | 354 -> 354 of 360 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 of 280 | 0+0 -> 0+0 | 73 (73) -> 264 (291) | 8.52 -> 8.60 |

## Re-pushes (H and I, both suites, both seeds)

A re-push follows every failed first pull. It ends one of three ways: pull again (v4: always, unless a force limit trips), rejected by the v5 gate (re-push did not hold 0.8 x 35.2 N, or held short of INSERT's seat depth), or aborted on a force limit during the re-push.

| Machine | Ctrl | Re-pushes before -> after | Pulled again | Gate: short of seat depth | Gate: not held | Aborted on lateral force (within 50 ms) | Aborted on other limits | Protective stops in the latch check (after INSERT's seat) |
|---|---|---|---|---|---|---|---|---|
| gantry | H | 176 -> 176 | 175 -> 174 | 0 -> 0 | 0 -> 0 | 0 (0) -> 1 (0) | 1 -> 1 | 0 -> 0 |
| gantry | I | 208 -> 208 | 208 -> 208 | 0 -> 0 | 0 -> 0 | 0 (0) -> 0 (0) | 0 -> 0 | 0 -> 0 |
| arm | H | 203 -> 204 | 194 -> 202 | 0 -> 0 | 0 -> 0 | 8 (8) -> 0 (0) | 1 -> 2 | 4 -> 0 |
| arm | I | 218 -> 218 | 218 -> 218 | 0 -> 0 | 0 -> 0 | 0 (0) -> 0 (0) | 0 -> 0 | 0 -> 0 |

## C against H and I on good parts (both suites, both seeds, paired by trial)

C's rows are from the after run (C's code is unchanged; see the identity check).

| Machine | Ctrl | C good seated | C-only / other-only, before (p) | C-only / other-only, after (p) | C bad parts passed | C stops |
|---|---|---|---|---|---|---|
| gantry | H | 357 of 360 | 14 / 2 (0.0042) | 14 / 2 (0.0042) | 0 | 16 |
| gantry | I | 357 of 360 | 2 / 3 (1) | 2 / 3 (1) | 0 | 16 |
| arm | H | 348 of 360 | 14 / 2 (0.0042) | 11 / 2 (0.022) | 0 | 4 |
| arm | I | 348 of 360 | 3 / 9 (0.15) | 3 / 9 (0.15) | 0 | 4 |

## H and I good-part failures after (v5)

| Machine | Ctrl | Condition | Reason | Trials |
|---|---|---|---|---|
| arm | H | mf_latch_early | false_accept | 1 |
| arm | H | mf_noise_1mm | aborted:excess_lateral_force | 8 |
| arm | H | mf_noise_1mm | aborted:excess_torque | 3 |
| arm | H | mf_noise_1mm | aborted:jam | 2 |
| arm | H | mf_noise_1mm | aborted:retention_failed | 2 |
| arm | H | mf_noise_1mm | aborted:time_limit | 3 |
| arm | H | mf_noise_1mm | protective_stop | 1 |
| arm | H | mf_terminal_min | aborted:excess_torque | 1 |
| arm | I | mf_noise_1mm | aborted:time_limit | 6 |
| gantry | H | mf_noise_1mm | aborted:jam | 1 |
| gantry | H | mf_noise_1mm | aborted:retention_failed | 1 |
| gantry | H | mf_noise_1mm | aborted:time_limit | 10 |
| gantry | H | mf_noise_1mm | protective_stop | 2 |
| gantry | H | mf_terminal_min | aborted:time_limit | 1 |
| gantry | I | mf_noise_1mm | aborted:time_limit | 2 |

## Identity check (seed 2027, 2 trials per condition, all ten controllers)

`identity/before` at 966a5f5, `identity/after` at the v5 code. Rows compared on every field but wall time; events compared as logged. H and I before are also compared with `dev4` (same seed, conditions, trial indices 0-1).

| Machine | Suite | Ctrl | Trials | Rows differ | Event logs differ | H/I before vs dev4: rows differ |
|---|---|---|---|---|---|---|
| gantry | latching | A | 14 | 0 | 0 |  |
| gantry | latching | B | 14 | 0 | 0 |  |
| gantry | latching | C | 14 | 0 | 0 |  |
| gantry | latching | D | 14 | 0 | 0 |  |
| gantry | latching | E | 14 | 0 | 0 |  |
| gantry | latching | F | 14 | 0 | 0 |  |
| gantry | latching | G | 14 | 0 | 0 |  |
| gantry | latching | H | 14 | 8 | 1 | 0 |
| gantry | latching | I | 14 | 12 | 6 | 0 |
| gantry | latching | J | 14 | 0 | 0 |  |
| gantry | latch_spread | A | 18 | 0 | 0 |  |
| gantry | latch_spread | B | 18 | 0 | 0 |  |
| gantry | latch_spread | C | 18 | 0 | 0 |  |
| gantry | latch_spread | D | 18 | 0 | 0 |  |
| gantry | latch_spread | E | 18 | 0 | 0 |  |
| gantry | latch_spread | F | 18 | 0 | 0 |  |
| gantry | latch_spread | G | 18 | 0 | 0 |  |
| gantry | latch_spread | H | 18 | 16 | 7 | 0 |
| gantry | latch_spread | I | 18 | 16 | 6 | 0 |
| gantry | latch_spread | J | 18 | 0 | 0 |  |
| arm | latching | A | 14 | 0 | 0 |  |
| arm | latching | B | 14 | 0 | 0 |  |
| arm | latching | C | 14 | 0 | 0 |  |
| arm | latching | D | 14 | 0 | 0 |  |
| arm | latching | E | 14 | 0 | 0 |  |
| arm | latching | F | 14 | 0 | 0 |  |
| arm | latching | G | 14 | 0 | 0 |  |
| arm | latching | H | 14 | 10 | 10 | 0 |
| arm | latching | I | 14 | 10 | 10 | 0 |
| arm | latching | J | 14 | 0 | 0 |  |
| arm | latch_spread | A | 18 | 0 | 0 |  |
| arm | latch_spread | B | 18 | 0 | 0 |  |
| arm | latch_spread | C | 18 | 0 | 0 |  |
| arm | latch_spread | D | 18 | 0 | 0 |  |
| arm | latch_spread | E | 18 | 0 | 0 |  |
| arm | latch_spread | F | 18 | 0 | 0 |  |
| arm | latch_spread | G | 18 | 0 | 0 |  |
| arm | latch_spread | H | 18 | 17 | 17 | 0 |
| arm | latch_spread | I | 18 | 18 | 17 | 0 |
| arm | latch_spread | J | 18 | 0 | 0 |  |
