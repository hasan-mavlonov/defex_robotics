# v0.2d dev check: A-J on the integrated code

Development check, not a selection: nothing was ranked or tuned on these runs. Dev seed 2027,
20 trials per condition, gantry and arm, all four suites, all ten controllers, at 43c8b6b
(every `config.json`: `git_dirty: false`). Commands: [`run.sh`](run.sh). Tables:
[`TABLES.md`](TABLES.md) (`python -m experiments.checkpoint_report results/v0.2d_dev_check`),
whose last section applies the v0.2c decision rules plus the J rules.

Good parts seated (good-part escapes), per machine and suite:

| Cell | C | best fair | G | J | I |
|---|---|---|---|---|---|
| gantry standard (400) | 397 (0) | F 384 (9) | 400 (0) | 387 (1) | 384 (9) |
| gantry latching (60) | 58 (0) | F 60 (0) | 60 (0) | 60 (0) | 60 (0) |
| gantry heldout (100) | 86 (0) | F 81 (11) | 94 (0) | 89 (0) | 81 (11) |
| gantry latch_spread (120) | 120 (0) | I 120 (0) | 120 (0) | 120 (0) | 120 (0) |
| arm standard (400) | 389 (0) | F 381 (12) | 394 (0) | 384 (0) | 381 (12) |
| arm latching (60) | 54 (0) | F 56 (0) | 56 (0) | 56 (0) | 56 (0) |
| arm heldout (100) | 83 (0) | F 77 (10) | 88 (0) | 78 (0) | 77 (10) |
| arm latch_spread (120) | 119 (0) | I 120 (0) | 120 (0) | 120 (0) | 120 (0) |

- Rules (TABLES.md): C ahead of every fair baseline only on `standard` (gantry p = 0.00024,
  arm p = 0.039); a fair baseline matches C in the other six cells. G helps only on gantry
  heldout (p = 0.021). J below C on gantry standard (p = 0.002), matches C elsewhere; J
  passes fewer bad units than I on standard and heldout on both machines.
- Deliberately bad parts passed: C, G, H, I, J 0 of 280 per machine. Without a pull: D, F
  (and A, B, E) pass most of them.
- J's one bad unit: gantry `noise_2mm` trial 11, the same unit as in `v0.2d_j_verify`
  (F's seat reading 11.0 mm, tilted; the housing-only VERIFY has no depth gate or tilt check).
- A is mostly protective stops on the latching suites, as in benchmark_v0.2c.
