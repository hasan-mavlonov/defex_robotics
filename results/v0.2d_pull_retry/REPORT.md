# v0.2d: one pull retry for H and I

Development work, not a benchmark. After the force-budget fix, what was left of C's
latch_spread lead over H and I was mostly one behaviour: when the pull fails on a plug
that stopped in the terminal zone (`mf_terminal_max`), C pushes again and pulls again,
while H and I rejected at the first failed pull
([`../v0.2d_force_budget/REPORT.md`](../v0.2d_force_budget/REPORT.md), (b)). A
conventional cell can do the same, so H and I were given one retry.

**Result:** with the retry (version 4, picked by a rule committed before its dev runs
and confirmed once on seed 4004), H and I seat as many latch_spread good parts as C on
dev seeds on both machines, and pass no more bad parts.

## The retry (version 4, installed)

`SpiralSearchConfig.pull_retries` (H and I: 1; D and F: 0). After a failed pull, a
re-push copied from C's bottom proof push: the force loop at the insert target
(35.2 N) capped at 2 mm/s, INSERT's force and torque limits (fail on a limit); pull
again once 0.8 x the target has been held 0.4 s without the plug advancing more than
0.1 mm (an advance restarts the hold), or after 6 s. Hold, cap and advance are C's
`proof_push_s`, `proof_push_speed_mm_s` and `proof_advance_mm`. One retry, then
reject. Test:
`tests/test_fair_baselines.py::test_pull_retry_re_push_reaches_the_target_before_the_second_pull`.

## How it got there (all on dev seeds 2026 and 2027)

| Version | Re-push ended on | What the dev runs showed | Status |
|---|---|---|---|
| v1 ([`v1/`](v1/TABLES.md), 02ece67) | hold, or 3 s after contact | gantry gains; arm none, H passed 2 broken-latch parts | dropped |
| v2 ([`dev/`](dev/TABLES.md), 5a02674) | hold, a stall, or 6 s | pick "I on the gantry only", confirmed on seed 4003 | **withdrawn**: the fairness review found the stall exit had no force gate; H's re-pushes and I's on the arm ended at 9-16 N, and the arm H bad-part passes (16) came from second pulls after those weak re-pushes |
| v3 ([`dev3/`](dev3/TABLES.md), 0ba51c0) | hold or 6 s, capped, force limits | gantry gains, no new stops; arm none: the hold ran out while the plug was still moving through the terminal peak | not used |
| v4 ([`dev4/`](dev4/TABLES.md), 1f1ca4a) | as v3, an advance restarts the hold | gains on all four cells, no new bad parts or stops | **installed** |

Each version's rule was committed before that version's dev runs
([`SELECTION_RULE.md`](SELECTION_RULE.md)); each was written after seeing the previous
version's results on the same dev seeds, and v4 after seed-2026 smoke trials. Seed
4004 was kept fresh for the final check.

## Dev runs, version 4 ([`dev4/TABLES.md`](dev4/TABLES.md))

Seeds 2026 and 2027, latching and latch_spread, 20 trials per condition; retry off is
`results/v0.2d_force_budget/after`. C and D are field-identical (controls).

| Machine | Ctrl | Good seated off -> on (of 360) | Bad parts + bad units off -> on | Protective stops |
|---|---|---|---|---|
| gantry | H | 340 -> 345 | 0 -> 0 | unchanged |
| gantry | I | 342 -> 358 | 0 -> 0 | unchanged |
| arm | H | 321 -> 336 | 1 -> 1 | unchanged |
| arm | I | 344 -> 354 | 0 -> 0 | unchanged |

C against H and I on latch_spread good parts after the retry (C-only / other-only):
gantry H 1 / 0, I 0 / 0; arm H 2 / 2, I 0 / 2. Before it: gantry 6 / 0 and 16 / 0,
arm 17 / 2 and 10 / 2. On latching good parts nothing changed (gantry C vs H 13 / 2,
C vs I 2 / 3; arm 12 / 0 and 3 / 7).

Cost: the retry adds cell time on bad parts (each rejected bad part now pulls twice).
Good units per hour counting bad-part cycles, latch_spread dev: gantry H 281 -> 248,
I 247 -> 227; arm H 280 -> 244, I 280 -> 237.

## Validation, seed 4004, run once

Pick registered at 5d2c3dc; retry off at 34520aa ([`val4004_off/`](val4004_off/)).
Latching and latch_spread pooled, 180 good-part trials per controller and machine:

| Machine | Ctrl | Good seated off -> on | Lost / gained (p) | Bad parts + bad units | Stops |
|---|---|---|---|---|---|
| gantry | H | 163 -> 169 | 0 / 6 (0.031) | 0 -> 0 | 14 -> 14 |
| gantry | I | 165 -> 177 | 0 / 12 (0.00049) | 0 -> 0 | 24 -> 24 |
| arm | H | 159 -> 163 | 0 / 4 (0.12) | 0 -> 0 | 4 -> 4 |
| arm | I | 166 -> 172 | 0 / 6 (0.031) | 0 -> 0 | 1 -> 1 |

The pick stands in all four cells. Every `config.json` shows `git_dirty: false`.

## Limits

- The seat rule of D, F, H and I (declare seated at 0.8 x the target, 28.2 N, for
  0.08 s) is below the 32-33 N terminal peak at the datasheet maximum; the retry
  repairs the consequence rather than the rule. Not re-selected.
- The retry is C's proof-push logic moved into the conventional cell. It is a
  plausible conventional program step (push again, pull again), but it was designed
  with knowledge of C.
- Seeds 2026 and 2027 were used for four versions; 4004 is the only clean check, at
  20 trials per condition.
