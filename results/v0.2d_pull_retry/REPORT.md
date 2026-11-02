# v0.2d: one pull retry for H and I

Development work, not a benchmark. After the force-budget fix, what was left of C's
latch_spread lead over H and I was mostly one behaviour: when the pull fails on a plug
that stopped in the terminal zone (`mf_terminal_max`), C pushes again and pulls again,
while H and I reject at the first failed pull
([`../v0.2d_force_budget/REPORT.md`](../v0.2d_force_budget/REPORT.md), (b)). A
conventional cell can do the same, so it was tried.

## The retry

`SpiralSearchConfig.pull_retries` (0 by default). After a failed pull: INSERT's contact
speed until the plug pushes back, then the force loop at the insert target (35.2 N)
capped at 2 mm/s; pull again once held for 0.4 s at 0.8 x the target, or when stalled
(INSERT's stall rule), or after 6 s. Hold and cap are C's proof-push values
(`AdaptiveConfig.proof_push_s`, `proof_push_speed_mm_s`). One retry, then reject.

## Versions and what they showed

* v1 (02ece67, runs in [`v1/`](v1/TABLES.md)): the re-push ended on hold or 3 s after
  contact. Gantry: H 234 -> 239, I 224 -> 240 of 240 latch_spread good parts, no bad
  parts passed. Arm: no seats gained (the re-push timed out while the plug was still
  moving, at 19-24 N), and H passed 2 broken-latch bad parts.
* Current (5a02674): the re-push also ends on a stall. The
  [selection rule](SELECTION_RULE.md) was committed with it, before its dev runs.

Arm smoke trials and the H failures show why the retry is unsafe as a plain
re-push: on `mf_terminal_max_broken_latch` (terminal friction at the datasheet maximum,
latch broken), a second pull that starts from the terminal zone is held at 35.2 N by
terminal friction alone, and passes. C does not have this hole because its latch check
needs the plug at the floor first.

## Dev runs and the pick ([`dev/TABLES.md`](dev/TABLES.md))

Seeds 2026 and 2027, latching and latch_spread, 20 trials per condition; retry off is
`results/v0.2d_force_budget/after`. C and D are field-identical (controls).

| Machine | Ctrl | Good seated off -> on | Bad parts + bad units off -> on | Rule |
|---|---|---|---|---|
| gantry | H | 340 -> 340 of 360 | 0 -> 0 | off (no gain) |
| gantry | I | 342 -> 358 of 360 | 0 -> 0 | **on** |
| arm | H | 321 -> 321 of 360 | 1 -> 17 | off (16 broken-latch parts passed) |
| arm | I | 344 -> 344 of 360 | 0 -> 0 | off (no gain) |

## Validation, seed 4003, run once

Pick registered at 305f4bf; retry off at 34520aa
([`val4003_off/`](val4003_off/)). Gantry I, good parts seated off -> on: latching
60 -> 60 of 60, latch_spread 111 -> 120 of 120 (0 lost / 9 gained, p = 0.0039); bad
parts passed plus bad units 0 -> 0 on both suites. The pick stands. Every
`config.json` shows `git_dirty: false`.

## What this means for the comparison

On the gantry, C's latch_spread lead over I is gone on dev seeds (240 against 240). On
the arm the retry did not help either H or I and is off there, so C's arm lead over H
and I on `mf_terminal_max` stays (dev: 17/2 and 10/2 trials). Doing the retry safely on
the arm would need a depth gate before the second pull, which is C's design rather
than a conventional cell's; that was not tried. Throughput: the retry costs I's gantry
cell time on bad parts (good units per hour on dev latch_spread 247 -> 236, counting
bad-part cycles).
