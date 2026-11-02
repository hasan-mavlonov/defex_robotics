# v0.2d J re-pick: report

Development work on `v0.2d/integration`, simulation only. J's response to a failed check
(`results/v0.2d_j_verify`) was picked on the 30 N code. This re-runs the same rule on the
integrated code (35.2 N insert target, tilt check in C's latching VERIFY, H/I pull retry).
Rule, committed before the runs: [`SELECTION_RULE.md`](SELECTION_RULE.md) (2105abb).
Commands: [`run.sh`](run.sh). Tables: [`TABLES.md`](TABLES.md)
(`python -m experiments.v02d_j_tables results/v0.2d_j_repick --pick spiral_rcc_verify_research`).
Dev runs at 2105abb, validation at 3ea570b (pick registered); every `config.json` shows
`git_dirty: false`.

## Pick: (b) re-search, unchanged

| Seed | Candidate | Bad units passed | Good parts seated | Median good cycle (s) | Good units/h |
|---|---|---|---|---|---|
| dev 2026 (ranks) | J(a) reject | 0 | 1282/1360 | 7.530 | 430 |
| dev 2026 (ranks) | J(b) re-search | 0 | 1295/1360 | 7.552 | 427 |
| validation 4005 (once) | J(a) reject | 0 | 1288/1360 | 7.579 | 432 |
| validation 4005 (once) | J(b) re-search | 0 | 1302/1360 | 7.603 | 431 |

The rule ranks (b) first on both seeds (step 2, more good parts seated). `spiral_rcc_verify`
keeps `on_verify_fail = "research"`; only its comment changed (3ea570b).

## What changed against the 30 N pick

- (b)'s gain is still on `latch_spread`: gantry 111 -> 120 of 120, arm 116 -> 120 of 120
  (dev 2026). At 35.2 N, F's own insertion reaches the floor more often, so the gain is
  smaller than at 30 N (gantry 38, arm 13 trials on two seeds then).
- On dev 2026, J(b) against C: 1295 against 1290 seated of 1360 (36 / 31 discordant,
  p = 0.63); 0 bad units each. J(b) against I: 1295 against 1276 (38 / 19, p = 0.016);
  bad units 0 against 38 (p < 1e-6). Bad parts passed: 0 of 280 for C, I and J.
- Below C on gantry `standard`: 390 against 400 of 400 (p = 0.002). Equal to I on both
  machines' `latching` and `latch_spread`.
- Cycle: J 7.55 s median against C 7.87 s and I 4.77 s; good units per hour 427 against
  400 and 571.
- Cost of (b): on gantry bad parts it ends in more protective stops than (a), 27 against
  20 of 140 (a second descent into a hard obstruction). Each costs the assumed 60 s reset.

## Checks

- Up to F's "seated", J's events equal F's on all 3,033 trials per candidate where F declared seated
  (both seeds); on the 247 where F did not, J's row equals F's.
- Tilt check: 1 FAIL among the 3,425 tilt verdicts logged in these runs (C and J), on a
  bad part (`mf_terminal_max_broken_latch`). As disclosed in the rule: C's sample window
  is empty at J's hand-over, so the check cannot fail at J's first latch check.

## Uncertain

- 20 trials per condition; differences of a few trials per cell.
- Seed 2026 has now ranked this choice twice (30 N and 35.2 N code).
- J's RCC terms, the missing depth gate and the other skeptic points in
  `results/v0.2d_j_verify/REPORT.md` still apply.
