- `results/v0.2c_defect_verdict/validation/gantry`: backend gantry, seed 4002, 20 trials per cell, commit `afa08a4`, dirty False
- `results/v0.2c_defect_verdict/validation/arm`: backend arm, seed 4002, 20 trials per cell, commit `f2ca43d`, dirty False

| Candidate | Trials | Bad parts passed | Good parts seated (95% CI) | vs off: off-only / cand-only (p) | False rejects | Stops good / bad | Time per bad part (s) | Good units per hour, no reset / 60 s per stop | Cycle p50 / p95, good successes (s) |
|---|---|---|---|---|---|---|---|---|---|
| off | 560 | 0 | 221/240 (88.0-94.9%) | reference | 0 | 3 / 20 | 23.85 | 80 / 70 | 8.28 / 14.06 |
| r2 | 560 | 0 | 223/240 (89.0-95.5%) | 0 / 2 (0.5) | 4 | 1 / 7 | 10.37 | 144 / 132 | 8.28 / 14.07 |
| r3 | 560 | 0 | 223/240 (89.0-95.5%) | 0 / 2 (0.5) | 4 | 1 / 12 | 14.67 | 115 / 104 | 8.28 / 14.01 |

Step 1 (no bad part passed): off, r2, r3.
Step 2 (good-part success; most: r2, 223): tied with it (McNemar p >= 0.05): off, r2, r3.
Steps 3-4 (good units per hour with 60 s per stop, then p50, p95): r2 (132.2), r3 (103.7), off (70.4).

**Chosen: r2.**
