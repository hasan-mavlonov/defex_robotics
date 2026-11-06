# v0.2e: H and I pull retry, rule version 5

Development work, not a benchmark. benchmark_v0.2d is frozen at 966a5f5 and does not
include this change.

The v0.2d pre-registration ("Disclosed before the run") lists three problems a review
found in H and I's pull retry (rule version 4). They were disclosed there, not fixed.
Version 5 fixes all three. The code was committed (78f3963) before any run here, and
nothing was changed after seeing the results.

**Result, dev seeds 2026 and 2027:** the fixes change outcomes only for H on the arm.
There, re-pushes that tripped the lateral limit fell from 8 to 0, and protective stops
during the latch check fell from 4 to 0. Arm H seats 3 more good parts (336 -> 339 of
360, 0 lost, p = 0.25). Bad parts passed and bad units are the same everywhere. The
depth gate (a) did not fire on any of the 806 re-pushes. I is unchanged on both
machines, and so is H on the gantry.

All numbers come from [`TABLES.md`](TABLES.md), made by
`python -m experiments.v02e_pull_retry_tables`.

## What changed (defex/control/spiral_search.py, defex/config.py)

Two switches, `repush_seat_gate` and `verify_lateral_compliance`, are on for H and I on
both machines and off for D and F. Nothing under `defex/control` imports MuJoCo, the
backend or GroundTruth.

**(a) Depth gate before the second pull.** C's rule: after a held re-seat, C checks the
latch only if the plug was held at the push force and is at C's seat depth (the gate a
`seated_candidate` passes). If not, the part fails without a pull
(`adaptive_fsm.py`, `held_reseat`). C's other proof pushes reach a latch check only
through INSERT's bottoming rule, which uses the same seat threshold. H and I now do the
same. At the end of the re-push they pull again only if the re-push held (0.8 x 35.2 N
for 0.4 s, as before). The depth must also be inside the window INSERT used to declare
the seat. Otherwise the part is rejected: `repush_not_held`, or
`repush_short_of_seat` if the plug held short of the seat depth.
- The thresholds that carry over from C are the same in both controllers. The force
  fraction is 0.8 (C's `bottom_force_fraction`). The re-push hold is C's
  `proof_push_s`.
- C's depth numbers do not carry over. C's threshold is 8 mm - 1.0 mm - 2.5 sigma,
  with sigma from C's own touch calibration (0.1 mm), which H and I do not have. H and
  I instead use their own INSERT window: depth below the face contact >= 8 mm - seat
  margin, so 7.5 mm for H gantry and I arm, 7.0 mm for H arm and I gantry. If they went
  straight in, the window is the vision depth, 3 sigma wider. Where H and I touched the
  face, this window is at least as strict as C's 6.75 mm. Depth is what H and I already
  sense: encoder depth, and on the RCC stage the same depth estimate they use in
  INSERT. They get no new sensing.
- The window is the same arithmetic INSERT used, now in a helper (`_seat_window`).

**(b) Lateral compliance through the latch check.** INSERT runs a zero-stiffness lateral
admittance, which lets the plug move sideways under side force. In version 4 it was
frozen at its INSERT value during the pull, the re-push and the re-seat. Side load built
during the pull, and the re-push then tripped the 10 N lateral limit on its first tick.
Version 5 runs the same admittance (`self.adm.update`) in all three phases. The pull is
the same gap: it is where the side load builds. The pull does not check limits, so
fixing only the re-push would still trip on the re-push's first tick. The re-seat is the
same kind of push as INSERT.

**(c) Retries.** A pull retry now adds 1 to `retries`, as C's slide-out retry does. The
`recovered` column (success with retries > 0) follows.

## Evidence

[`run.sh`](run.sh) holds every command. Workers: 1. The main run took 1 h 34 min.
Every `config.json` shows `git_dirty: false`.

| Folder | What | Code |
|---|---|---|
| `after/` | C, H, I; seeds 2026 and 2027; latching and latch_spread; both machines; 20 trials per condition | 78f3963 |
| `../v0.2d_pull_retry/dev4/` | before: H and I, same seeds, suites and trials | run at 1f1ca4a |
| `identity/before/` | all ten controllers, seed 2027, both suites, both machines, 2 trials per condition | 966a5f5 |
| `identity/after/` | the same | 78f3963 |

H and I code did not change from 1f1ca4a to 966a5f5 (one docstring line). The identity
check confirms this: H and I at 966a5f5 give rows identical to dev4 on all 128
overlapping trials. C changed in that window (tilt check), so C's dev4 rows are not
used. C's comparator rows come from `after/`, and the identity check shows C is
unchanged by this commit.

**Identity:** A, B, C, D, E, F, G and J give identical rows (every field but wall time)
and identical event logs before and after, on all 64 trials per controller. Only H and
I differ.

## Results (TABLES.md, both suites and seeds pooled)

| Machine | Ctrl | Good seated before -> after (of 360) | Lost / gained (p) | Bad units on good parts | Bad parts passed (of 280) | Protective stops | Retries (sum) |
|---|---|---|---|---|---|---|---|
| gantry | H | 345 -> 345 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 | 24 -> 24 | 121 -> 297 |
| gantry | I | 358 -> 358 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 | 38 -> 38 | 56 -> 264 |
| arm | H | 336 -> 339 | 0 / 3 (0.25) | 1 -> 1 | 0 -> 0 | 5 -> 1 | 98 -> 302 |
| arm | I | 354 -> 354 | 0 / 0 (1) | 0 -> 0 | 0 -> 0 | 0 -> 0 | 73 -> 291 |

The retry increase is exactly the number of re-pushes, as (c) intends. For example,
gantry H: 121 INSERT retries + 176 pull retries = 297.

Re-pushes, by how they ended:

| Machine | Ctrl | Re-pushes | Failed depth gate | Not held | Lateral-limit aborts (within 50 ms) before -> after | Other limit aborts | Stops in the latch check |
|---|---|---|---|---|---|---|---|
| gantry | H | 176 | 0 | 0 | 0 (0) -> 1 (0) | 1 -> 1 | 0 -> 0 |
| gantry | I | 208 | 0 | 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| arm | H | 203 -> 204 | 0 | 0 | 8 (8) -> 0 (0) | 1 -> 2 | 4 -> 0 |
| arm | I | 218 | 0 | 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 |

(The pre-registration's "12 arm H re-pushes" counts dev4 and val4004 together. These
dev seeds hold 8 of them. Seed 4004 was not rerun here.)

C against H and I on good parts, paired (C-only / other-only): arm H 14 / 2 (p = 0.0042)
before, 11 / 2 (p = 0.022) after. The other three cells did not change: gantry H 14 / 2,
gantry I 2 / 3, arm I 3 / 9.

Cycle time: median good-part cycle changed by at most 0.09 s. Arm I went 8.52 -> 8.60 s
and arm H 8.43 -> 8.46 s.

## What to watch

- **(a) never fired on dev data.** No re-push ended short of the seat window or without
  holding. It guards a case the review identified but these seeds did not produce. All
  re-pushes in dev4 already ended deep enough (`TABLES.md`, re-push table). It neither
  helps nor hurts here.
- **(b) makes arm H better on good parts.** The gain is not in the re-push. It is in the
  first pull: on 4 arm H good parts (`mf_noise_1mm`) the v4 pull loaded the plug
  sideways until the cell's protective stop (0.60 N m). With compliance in the pull, 3
  of them pass and seat. The fourth now fails the pull and aborts on excess torque 2 ms
  into the re-push. The lateral compliance is lateral only, not rotational. This
  narrows C's arm lead over H (14 / 2 -> 11 / 2). It is a fix to the baseline, made
  after the review, on dev seeds only. Seed 4006 is reserved, so it has not been
  validated on a fresh seed.
- **One new lateral abort on the gantry.** On H, `mf_spread_half_latched` trial 16
  (seed 2026), a bad part that went straight in: 2.3 s into the re-push it aborted on
  the lateral limit. In v4 it re-pushed and failed the second pull. It is rejected
  either way and is not a protective stop. A zero-stiffness admittance can drift while
  the plug is held. On these seeds that happened once.
- **The `retries` and `recovered` columns now mean something different for H and I.**
  Any table comparing them across v0.2d and v0.2e must account for this. H/I retries
  roughly triple, and `recovered` changed on 47 rows.
- **Most H and I rows differ at float level.** Compliance in the pull moves every plug
  that reaches the pull slightly, so final pose and peak-force fields change on 2,157
  of 2,560 H and I rows. Outcome fields changed on few rows: `failure_reason` 15,
  `success` 3, `protective_stop` 4, `declared_success` 4.
- Seeds 2026 and 2027 have now been used for five versions of this retry.

## Tests

`tests/test_pull_retry_v5.py`:
- switches on for H and I only;
- a failed pull counts as a retry, and the last failed pull rejects without counting;
- the second pull starts only inside the seat window (`repush_short_of_seat` otherwise);
- a re-push that never holds is rejected (`repush_not_held`);
- with the gate off, version 4 behaviour returns;
- the admittance moves under side load in the pull, re-push and re-seat, and only with
  the switch on;
- the seat-window helper does INSERT's arithmetic;
- slow, arm: the dev4 lateral-abort trial now re-pushes, pulls again and rejects on the
  pull, with retries = 1.

`tests/test_fair_baselines.py`: the H/I-vs-D/F config diff allows the two new switches.

Full suite: 209 passed, slow tests included.
