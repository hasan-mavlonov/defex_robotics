# v0.2e validation on seed 4006

Rule: `VALIDATION_RULE.md`, committed at 9113842 before any run on seed 4006. Tables:
`TABLES.md`, made by `python -m experiments.v02e_validation results/v0.2e_validation`.
Simulation only.

## Runs

All ten controllers, both machines, the four suites, 20 trials per condition, seed
4006, `--workers 9`; 8,200 trials per version, 16,400 paired.

- `before/`: benchmark_v0.2d code, run 03:55-04:15 PST on 2026-11-02 from
  v0.2d/integration. Its `config.json` files record cca2d1b (gantry standard) and
  ea812c0 (the other seven): a merge of results files landed between the first and
  second run. Neither commit changes code since 42df5c8; all `git_dirty: false`.
- `after/`: v0.2e integration code at 6edaa49, run 04:25-04:44, all `git_dirty: false`.

## Result: all three fixes kept

| Fix | Controllers | Outcome on seed 4006 |
|---|---|---|
| 1 simulator reset | all | no outcome change on A, B, D, E, F (the controllers no other fix touches); G and J changed 5 rows each on the arm, in the last digits, with no outcome change |
| 2 H/I pull retry v5 | H, I | arm H seated 1 more good part (611 -> 612 of 680, 0 lost, p = 1); no other outcome change; bad parts 0 -> 0, bad units on good parts unchanged (gantry 13 and 13, arm 8 and 13) |
| 3 tilt-check force guard | C, G, J | no outcome change |

No controller seated fewer good parts, passed more bad parts or passed more bad units.
H and I rows differ at float level on 262-297 of 820 trials per machine, as in
development. The rule's fix 1 clause ("any outcome changes") is judged on A, B, D, E and
F, because outcome changes on C, G, H, I and J can also come from fixes 2 and 3; on G
and J no outcome changed at all, and on H the one change is the gained part above.
