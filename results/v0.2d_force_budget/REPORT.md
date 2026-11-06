# v0.2d force budget: insert target from the datasheet

Development work on seeds 2026 and 2027 only, gantry and UR5e arm, all nine
controllers (A-I). Most numbers below are in [`TABLES.md`](TABLES.md)
(`python -m experiments.v02d_force_budget_tables results/v0.2d_force_budget`) or
[`EQUIVALENCE.txt`](EQUIVALENCE.txt), both built from the per-trial files in
`before/` and `after/` by [`run.sh`](run.sh) `tables`; the rest (abort and stop counts, single-trial
forces and times) come from the same `trials.csv` and `events.json.gz` files. Before: commit b94b971
(the benchmark_v0.2c code). After: commit 34520aa (the fix). Every `config.json`
shows `git_dirty: false`.

## What changed

benchmark_v0.2c found that the Micro-Fit connector file's insert target (30 N) is
below the datasheet's maximum mating force (8 N per circuit x 4 = 32 N). Every
controller pushes at that target, so D, F, H and I seated none of the
`mf_terminal_max` good parts.

* `assets/connectors/microfit3_4ckt.json`: `insert_target_n` 30.0 -> 35.2 N, that is
  1.1 x the 32 N datasheet maximum, the factor C already uses for its stall push
  (`AdaptiveConfig.proof_push_factor`) and pull test. The derivation is in the file's
  `basis`. Abort 40 N (1.25 x 32 N), protective stop 48 N (1.5 x 32 N) and damage
  58 N (the minimum latch strength) are unchanged.
* The value stays in the JSON rather than being derived in code: `ForceBudget` stays a
  plain per-connector record, and a test ties the number to the datasheet
  (`tests/test_mating_physics.py::test_insert_target_reaches_the_datasheet_maximum_mating_force`:
  for every connector with a force budget, target >= the datasheet maximum, equal to
  `proof_push_factor` x that maximum, and target < abort < stop < damage).
* Who reads the target: C and G, D, F, H and I (`insert_force_n` via `budgeted`);
  A, B and E through `taught_overtravel` (overtravel = target / the fixture's weakest
  translational stiffness; gantry 10 N/mm, 3.0 -> 3.52 mm; arm 8.0 N/mm, 3.75 ->
  4.40 mm). C's own logic is untouched.
* `tests/test_v02c_all_off.py` reproduces committed Checkpoint 2 rows recorded with the
  30 N target; it now runs those trials with the old budget (without that, all four of
  its trials differ). No other test asserted 30 N. Full suite passes.

## The safety thresholds and a 35.2 N push

* `InsertionTask.run` (`defex/tasks/insertion.py`, lines 176-179) uses the
  connector's budget when it has one. On the Micro-Fit the protective stop is 48 N on
  the measured F/T and damage is a 10 ms average of the ground-truth contact force
  above 58 N. `SafetyConfig.protective_stop_force_n` (30 N) and
  `damage_contact_force_n` (45 N) apply only to the housing-only connector, which has
  no budget. A 35.2 N push therefore never meets the 30 N stop; if that stop applied
  to the Micro-Fit, C's proof push before the fix, and every controller's insertion
  after it, would trip it.
* The ground-truth contact force covers MuJoCo housing contacts only. The terminal,
  latch and obstruction forces are applied to the plug by `defex/sim/mating.py` and
  are not part of it, so a push through the terminals shows in the measured F/T, not
  in the damage measure.
* Damage events: 0 for every controller, before and after. The largest 10 ms contact
  peaks of C, D, F, G, H and I after the fix are 23-35 N on the gantry and 22-46 N on
  the arm (D and H, arm latching: 38.5 -> 45.8 N, one trial above 45 N). A, B and E
  exceed 45 N in the same number of trials as before (up to 54 N), never 58 N.
  Measured F/T above 58 N stays rare: at most 2 trials per controller and cell, after
  as before.
* The 40 N abort never ends a good part's trial for C, D, F, G, H or I, before or
  after. On gantry bad parts with a hard obstruction the force now overshoots through
  the abort to the 48 N stop more often: for F and I, excess-force aborts fall from 32
  to 5 and protective stops rise from 2 to 38 of 280 bad-part trials; D and H 25 -> 17
  and 15 -> 22; C 11 -> 16. These parts are still rejected; each stop costs the
  assumed 60 s reset. The abort and the stop are unchanged: lowering the abort cuts
  into the 35.2 N working force, raising the stop cuts into the margin to the 58 N
  damage bound, and neither costs a good part here.

## Equivalence on the housing-only connector

`standard` (nominal, lateral_3mm, tilt_5deg, friction_1, generalization_combined)
and `heldout` (all 5), seed 2026, 10 trials, A-I, both machines: 1,800 trials,
64,800 fields compared, **0 differences** except wall time
([`EQUIVALENCE.txt`](EQUIVALENCE.txt)).

## Before and after: latching and latch_spread suites

Seeds 2026 and 2027 pooled, 20 trials per condition and seed. Good parts: latching
120, latch_spread 240; bad parts: latching 160, latch_spread 120. "Lost / gained":
good-part trials that succeeded only before / only after (exact McNemar). False
rejects are 0 for every controller in every cell; damage events 0 in every cell.

### latch_spread, good parts seated (before -> after)

| Machine | C | H | I | D | F | E | G |
|---|---|---|---|---|---|---|---|
| gantry | 240 -> 240 | 189 -> 234 (0 / 45, p < 1e-6) | 189 -> 224 (0 / 35, p < 1e-6) | 189 -> 234 | 189 -> 237 | 200 -> 200 | 240 -> 240 |
| arm | 240 -> 238 (2 / 0, p = 0.5) | 187 -> 223 (0 / 36, p < 1e-6) | 187 -> 230 (0 / 43, p < 1e-6) | 187 -> 223 | 187 -> 230 | 206 -> 153 (53 / 0) | 240 -> 240 |

### latching, good parts seated (before -> after)

| Machine | C | H | I | D | F | E | G |
|---|---|---|---|---|---|---|---|
| gantry | 115 -> 117 (0 / 2, p = 0.5) | 105 -> 106 (2 / 3) | 118 -> 118 | 105 -> 106 | 118 -> 118 | 74 -> 74 | 120 -> 120 |
| arm | 111 -> 110 (1 / 0, p = 1) | 98 -> 98 | 114 -> 114 | 101 -> 101 | 114 -> 114 | 74 -> 49 (25 / 0, p < 1e-6) | 114 -> 115 |

### C, H and I in detail (before -> after)

| Machine, suite | Ctrl | Bad parts passed | Bad units on good parts | Stops (good + bad) | Max 10 ms contact (N) | Median good cycle (s) | Good units/h (60 s/stop) |
|---|---|---|---|---|---|---|---|
| gantry, latching | C | 0 / 160 | 0 | 0+8 -> 0+6 | 29.1 -> 33.9 | 5.95 -> 6.16 | 436 -> 450 |
| | H | 0 / 160 | 0 | 0+12 -> 2+7 | 29.8 -> 35.0 | 5.93 -> 6.16 | 379 -> 336 |
| | I | 0 / 160 | 0 | 0+0 -> 0+14 | 17.2 -> 23.3 | 5.33 -> 5.48 | 515 -> 504 |
| gantry, latch_spread | C | 0 / 120 | 0 | 0+3 -> 0+10 | 29.0 -> 33.5 | 5.95 -> 6.15 | 530 -> 525 |
| | H | 0 / 120 | 0 | 0+3 -> 0+15 | 21.6 -> 26.5 | 5.89 -> 6.05 | 467 -> 575 |
| | I | 0 / 120 | 0 | 0+2 -> 0+24 | 19.6 -> 24.6 | 5.30 -> 5.45 | 535 -> 613 |
| arm, latching | C | 0 / 160 | 0 | 4+0 -> 3+0 | 26.8 -> 27.1 | 8.67 -> 8.98 | 252 -> 248 |
| | H | 0 / 160 | 0 | 5+0 -> 5+0 | 38.5 -> 45.8 | 8.14 -> 8.44 | 246 -> 241 |
| | I | 0 / 160 | 0 | 0 -> 0 | 21.8 -> 22.4 | 8.23 -> 8.53 | 326 -> 317 |
| arm, latch_spread | C | 0 / 120 | 0 | 0 -> 0 | 25.2 -> 31.2 | 8.70 -> 9.02 | 355 -> 344 |
| | H | 0 / 120 | 0 -> 1 | 0 -> 0 | 22.0 -> 23.6 | 8.07 -> 8.40 | 344 -> 398 |
| | I | 0 / 120 | 0 | 0 -> 0 | 18.3 -> 22.7 | 8.17 -> 8.51 | 335 -> 400 |

## (a) Does C lose anything?

* Successes: no measurable change. Over the four cells C lost 3 good parts and
  gained 2 of 720 (exact McNemar p = 1). In all five the hole search on the face ran
  long (4-8 attempts) and took a different path, ending on the time or retry limit or
  seating where it had not; none is a plug that failed to seat under force
  (`TABLES.md`, "C's trials whose outcome changed").
* Bad parts passed: 0 before and after (0 of 560 bad-part trials; 0 bad units on 720
  good-part trials).
* Protective stops: 15 -> 19. Gantry latch_spread 3 -> 10, all on half-latched bad
  parts: C meets the obstruction while pushing at 35.2 N, detects excess force at
  40 N, and the force reaches the 48 N stop before it backs off (before, the same
  parts got a defect verdict). Gantry latching 8 -> 6; arm 4 -> 3 and 0 -> 0. Mean
  cell time per bad part on gantry latch_spread 12.2 -> 14.8 s with 60 s per stop.
* Damage: none. Largest 10 ms contact peak 33.9 N (was 29.1 N).
* Cycle: 0.2-0.3 s slower (median good cycle gantry 5.95 -> 6.15/6.16 s, arm
  8.67/8.70 -> 8.98/9.02 s). On a nominal trial the extra time is in the latch check:
  the pull starts from a higher push (32.7 N instead of 27.9 N at bottom detection)
  and takes 0.23 s longer to reach 35.2 N. Good units per hour -1% to -3%, except
  gantry latching +3% from the two gained parts.

## (b) What is left of C's latch_spread lead over H and I

After the fix, latch_spread good parts, 40 trials per condition (C / H / I seated;
C-only / other-only, exact McNemar p):

| Condition | gantry C / H / I | gantry vs H | gantry vs I | arm C / H / I | arm vs H | arm vs I |
|---|---|---|---|---|---|---|
| mf_spread | 40 / 40 / 40 | 0 / 0 | 0 / 0 | 40 / 38 / 40 | 2 / 0 (0.5) | 0 / 0 |
| mf_latch_early | 40 / 40 / 40 | 0 / 0 | 0 / 0 | 40 / 39 / 40 | 1 / 0 (1) | 0 / 0 |
| mf_latch_late | 40 / 40 / 40 | 0 / 0 | 0 / 0 | 40 / 40 / 40 | 0 / 0 | 0 / 0 |
| mf_latch_weak | 40 / 40 / 40 | 0 / 0 | 0 / 0 | 39 / 40 / 40 | 0 / 1 (1) | 0 / 1 (1) |
| mf_terminal_max | 40 / 35 / 24 | 5 / 0 (0.062) | 16 / 0 (3.1e-5) | 39 / 27 / 30 | 13 / 1 (0.0018) | 10 / 1 (0.012) |
| mf_terminal_min | 40 / 39 / 40 | 1 / 0 (1) | 0 / 0 | 40 / 39 / 40 | 1 / 0 (1) | 0 / 0 |
| all | 240 / 234 / 224 | 6 / 0 (0.031) | 16 / 0 (3.1e-5) | 238 / 223 / 230 | 17 / 2 (0.00073) | 10 / 2 (0.039) |

Before the fix C was ahead of each of H and I by 51 trials (gantry) and 53 (arm),
with none the other way. After it: H 6 and 15 net, I 16 and 8 net. `mf_spread` is
closed on both machines except 2 of 40 for H on the arm (I's 11 and 13 misses there
before the fix are gone).

Failure reasons of H and I on latch_spread good parts after the fix (49 trials, C
seated all of them; each is listed in `TABLES.md`):

* `aborted:retention_failed`: 47 (gantry H 5, I 16; arm H 16, I 10); 44 of them on
  `mf_terminal_max`.
* `aborted:time_limit`: 1 (gantry H, `mf_terminal_min`).
* `false_accept`: 1 (arm H, `mf_latch_early`, seed 2027 trial 14): the pull passed at
  35.2 N with the plug at 7.39 mm, short of the 7.5 mm seat tolerance. A bad unit
  passed; H had none before the fix.

What the event logs show for the retention failures: H and I declare the plug seated
at 6.2-7.2 mm of depth (the latch snaps at 7.5 mm), because their seat rule (depth
inside the window and axial force at least 0.8 x the target, 28.2 N, for 0.08 s) is
met while a part at the datasheet's maximum terminal force is still crossing its
32-33 N terminal peak. The pull then finds no latch (the plug comes back 1.05-1.28 mm
at 5.1 N or less) and they fail without a retry. C's first bottom detection fires at
the same point (gantry `mf_terminal_max`, seed 2026, trial 0: bottomed at 6.47 mm,
32.6 N) and its first latch check fails too; C then retries, meets the same bottom,
pushes at 35.2 N (its proof push after a slide-out), advances past the peak and
passes the pull. On 42 of the 49 trials C seated after a failed latch check and a
proof push, on 3 after a proof push only, on 4 with neither.

What remains of C's latch_spread lead after the force fix is therefore mostly one
behaviour: when the latch check fails on a plug that stopped in the terminal zone, C
tries again and holds the full force; H and I stop at the first failed pull. A
conventional cell could do the same (one retry with a hold at the insert target after
a failed pull). That has not been tested.

## Other effects of the fix

* E (a fair baseline) loses good parts on the arm: latching 74 -> 49 (25 / 0,
  p < 1e-6), latch_spread 206 -> 153 (53 / 0, p < 1e-6), from protective stops on good
  parts (latching 46 -> 71, latch_spread 34 -> 87). B behaves the same way. Cause:
  `taught_overtravel` divides the target by the arm's weakest translational stiffness
  (8.0 N/mm, along y) while the push is along z (10.8 N/mm from the same compliance
  matrix), so the static push is about 1.34 x the target. E's median peak measured
  force on `mf_nominal` went from 40-41 N to 47-48 N, at the 48 N stop. On the gantry
  (10 N/mm on every axis) A, B and E are almost unchanged. A fix needs the fixture's
  stiffness along the insertion axis (simulator side, `FixtureDynamics`); not done
  here. E's arm settings were also tuned with the 30 N target.
* D and F (no pull test) pass more deliberately bad parts on latch_spread: they now
  push broken-latch parts deep enough for their depth check (gantry D 73 -> 95, F 98
  -> 91; arm D 79 -> 110, F 93 -> 118 of 120), and pass fewer bad units on good parts
  (gantry D 16 -> 5, F 47 -> 3; arm D 29 -> 17, F 19 -> 10). H and I pass 0 bad parts
  before and after.
* Good units per hour on latch_spread rise for H and I (gantry 467 -> 575 and 535 ->
  613, arm 344 -> 398 and 335 -> 400); on latching they fall 2-11%.

Against the best fair baseline after the fix (dev seeds, not a benchmark result):
latch_spread gantry C 240 against F 237 (3 / 0, p = 0.25); arm C 238 against F and I
230 (10 / 2, p = 0.039).

## Not checked or uncertain

* Development seeds, 40 trials per condition and machine. The remaining gap rests on
  one condition, `mf_terminal_max`.
* The damage measure does not see terminal, latch or obstruction loads (applied
  forces in the simulator). Whether a real terminal tolerates 35.2 N (the datasheet
  maximum plus 10%) is not modelled.
* The 1.1 margin is assumed, as it was for C's proof push.
* `experiments/evaluate.py` plots draw `SafetyConfig`'s 30 N and 45 N lines on every
  run, including Micro-Fit runs where 48 N and 58 N apply (plots only).
* README.md (lines 72, 923), `docs/TECHNICAL_BRIEF.md` and
  `docs/HASAN_DEFENSE_NOTES.md` still describe the 30 N target as current.

## Reproduce

    git checkout b94b971 && results/v0.2d_force_budget/run.sh before
    git checkout 34520aa && results/v0.2d_force_budget/run.sh after
    results/v0.2d_force_budget/run.sh tables    # at 6578506 or later
