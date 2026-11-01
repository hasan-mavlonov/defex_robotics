# Validation sweep, seed 4002: result

Rule: `SELECTION_RULE.md` (committed before the sweep). Files: `standard_a5bd452/trials.csv`, `latching_a5bd452/trials.csv` (commit a5bd452).

| Candidate | Successes (of 120) | 95% CI | Base-only / candidate-only (McNemar p) | Escapes | Stops | Cycle p50 / p95 of successes (s) |
|---|---|---|---|---|---|---|
| base | 102 | 78-90% | 0 / 0 (1) | 0 | 4 | 11.89 / 21.38 |
| settle01 | 97 | 73-87% | 6 / 1 (0.12) | 0 | 3 | 11.51 / 19.97 |
| limit6 | 98 | 74-88% | 8 / 4 (0.39) | 0 | 4 | 12.02 / 19.63 |
| settle01_limit6 | 100 | 76-89% | 6 / 4 (0.75) | 0 | 3 | 11.91 / 19.16 |

Ranked by the rule (escapes excluded; successes, then median, then p95 cycle): base (102, 11.89 s, 21.38 s), settle01_limit6 (100, 11.91 s, 19.16 s), limit6 (98, 12.02 s, 19.63 s), settle01 (97, 11.51 s, 19.97 s). Selected: base.
