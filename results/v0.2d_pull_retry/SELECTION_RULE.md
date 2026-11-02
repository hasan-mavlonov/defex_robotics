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

---

# Selection rule, version 3 (after the fairness review)

The independent review of v0.2d/integration found that the version-2 re-push ended
on a stall with no force gate: H's re-pushes on both machines and I's on the arm
ended at 9-16 N instead of 0.8 x 35.2 N, and the arm H bad-part passes came from
second pulls after such weak re-pushes. That bug decided the version-2 pick, so the
pick above is withdrawn.

Version 3 (this commit): the re-push copies C's bottom proof push: the force loop at
the insert target capped at 2 mm/s from the start, INSERT's force and torque limits
(fail on a limit), pull again once 0.8 x the target has been held for 0.4 s or after
6 s. No stall exit. Test:
`tests/test_fair_baselines.py::test_pull_retry_re_push_reaches_the_target_before_the_second_pull`.

Written and committed before its dev runs. Same candidates, criteria and comparator
as above: retry on for a controller and machine if, on dev seeds 2026 and 2027
(latching and latch_spread, 20 trials per condition), (1) bad parts passed plus bad
units on good-part trials, on <= off, and (2) good parts seated, on > off. Off =
`results/v0.2d_force_budget/after`; on = `results/v0.2d_pull_retry/dev3` (this
commit, retry on in all four cells).

Validation, run once, on a fresh seed, **4004** (no run under `results/` has used
it): latching and latch_spread, 20 trials, both machines, the pick registered, and
retry off at 34520aa for every cell where the retry is on. The pick stands per cell
if (1) holds and seated on >= off; otherwise the retry is turned off there.
