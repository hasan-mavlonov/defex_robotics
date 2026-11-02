# Selection rule: H and I pull retry, per machine

Written and committed before the dev runs it decides (this commit), after the first
retry version's dev runs (`TABLES.md`, commit fd77f86) and seed-2026 smoke trials
of the current version on three latch_spread conditions. Those showed the retry adds
seats on the gantry and, on the arm, adds few seats and lets H pass broken-latch
parts with terminal friction at the datasheet maximum (a second pull from the
terminal zone is held by terminal friction).

Candidates: retry off (v0.2c H and I, insert target 35.2 N) and retry on (one
re-push and second pull, as in this commit). Decided separately for each of H and I
and for each machine (`cfg` gantry, `stiff_fixture_cfg` arm).

Development data: seeds 2026 and 2027, latching and latch_spread suites, 20 trials per
condition. Off = `results/v0.2d_force_budget/after`; on = `results/v0.2d_pull_retry/dev`.

Retry on for a controller and machine if both hold:
1. bad parts passed plus bad units on good-part trials, on <= off;
2. good parts seated, on > off.
Otherwise off.

Validation, run once: seed 4003, latching and latch_spread, 20 trials, both machines,
the pick registered. For each controller and machine with the retry on, the pick
stands if (1) holds against retry off on the same seed and seated on >= off;
otherwise the retry is turned off there. No other change follows from seed 4003.
