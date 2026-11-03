# v0.2f tilt diagnosis: report


Branch `v0.2f/tilt` from 4df8cae. Simulation only. Development seeds 2026 and 2027; seed 4007 once
for validation; seed 20261130 only to replay the three trials the v0.2e report names. Commands:
`run.sh`. Collector (ground truth read between ticks, never by the controller):
`experiments/v02f_tilt_diag.py`. Tables: `TABLES.md` (`experiments/v02f_tilt_tables.py`), candidates
`CAND_P.md`, `CAND_JW.md`, `CAND_JP.md`, validation `VAL_P.md`, `VAL_JW.md`, rule `RULE.md`
(2f95377, committed before any candidate run), decision `DECISION.md` (378e2fb, before seed 4007),
flags-off identity `identity/IDENTITY.md`, traces `traces/`.

## Result

How solid is "C passed 0 mis-seated parts"? The count holds on the dev seeds too. C and G passed 0
bad units in 6,400 latching and latch_spread trials and 3,953 accepted standard units (`TABLES.md`).
But the latching tilt check cannot see the usual way a latched plug ends up tilted. C aims the plug
along its own socket-axis estimate: the camera axis, plus any flat-face folds (`R_corr`). The check then
measures the plug against that same estimate. When the estimate is off, the plug follows it in, and
the check reads a small angle.

Two things keep tilted bad units rare, and neither is the check:

- the Micro-Fit cavity stops a latched plug at about 3.2 deg on the diagonal, only just over the
  3.0 deg limit, and the walls usually turn it back under 3.0 deg;
- the camera's tilt error is rarely over 3 deg. At `mf_noise_1mm` (sigma 1 deg) it was over 3 deg at
  6 of 165 arm tilt verdicts, and none of those became a bad unit.

The margin is thin. On the dev seeds, 5 declared C/G latching trials ended at 2.5-3.0 deg (near
misses), all at `mf_noise_1mm`, out of about 1,770 declared per machine. One trial, 2026/43,
accounts for 4 of them: camera axis 3.37 deg off, final tilt 2.81 deg.

Two default-off options were built and kept by the rule:

- **P**, a push before the tilt check when the window is under the force floor;
- **JW**, J's hand-over window.

Both passed seed 4007, but neither removed a bad unit or caught a tilted part on any seed. With the
flags off, the branch gives the v0.2e rows: 480 trials, 17,280 fields, 0 differences.

## Item 1: G's bad unit (benchmark_v0.2e arm `mf_noise_1mm` trial 130)

**Cause: the socket-axis estimate.** The walls did not hold the plug off-axis (`traces/g_mf_noise_1mm_130.txt`; the per-tick
decomposition was printed from `traces/g_mf_noise_1mm_130.json.gz`, which is not committed).

The replay reproduces the row: `false_accept`, 7.75 mm, 3.01 deg. At the latch check (floor-impact
path, window 12.6 N, just over the 11.75 N floor), the evidence breaks down as follows:

| | deg |
|---|---|
| True plug tilt | 3.09 |
| Measured (plug axis against C's estimate) | 0.47 |
| C's socket-axis estimate against the true socket axis | 2.87 |
| of which the camera | 0.57 |
| In-hand estimate error | 0.76 |
| CoP | 0.09 of the half-width |

How it happened:

1. On attempt 5 (15.05-16.71 s) the rate-mode top-face conform turned the plug by (-2.24, -2.63)
   deg, 3.45 deg in all.
2. During the conform the plug slid 0.11 mm into the lead-in, under the 0.8 mm slide-in threshold.
   The conform was logged "flat", and the rotation was folded into `R_corr`. That fold took the
   socket estimate from 0.81 to 2.79 deg off.
3. Attempts 6 and 7 aimed along the folded axis. The plug entered at 3.5 deg true tilt and the walls
   turned it back to 3.09 deg.
4. The check compared the plug with the axis it had been aimed along, so it read 0.47 deg. The low
   CoP shows that the walls were not holding the plug; it was simply aimed that way.

This is the "wrong flat-face fold" mode disclosed in `results/v0.2d_tilt_check` (3035/81 G). C on the
same trial ended on the time limit (`traces/c_mf_noise_1mm_130.txt`).

**A class, not a one-off: but mostly through the camera, not folds.** Counts are from the dev seeds,
C and G, latching and latch_spread, 50 trials per condition (`TABLES.md`, item 1):

| Machine | Ctrl | Tilt verdicts | Measured under true by > 1 deg | at true tilt > 2 deg | Main cause: camera / folds / in-hand |
|---|---|---|---|---|---|
| arm | C | 2,174 | 82 | 1 | 48 / 1 / 33 |
| arm | G | 2,186 | 86 | 5 | 51 / 2 / 33 |
| gantry | C | 1,974 | 33 | 2 | 25 / 0 / 8 |
| gantry | G | 1,986 | 33 | 2 | 25 / 0 / 8 |

So 234 of 8,320 verdicts read more than 1 deg under the true tilt. The cause is the largest of three
error projections on the true tilt direction: camera 149, in-hand 82, folds 3. The worst was 2.68 deg
under. All 10 verdicts at a true tilt over 2 deg passed. Every one of those trials was seated in the
end, with final tilt 1.83-2.98 deg. Two were wrong folds, G 2026/8 and 2026/17, with `R_corr` at 4.37
and 4.60 deg. The other eight were camera errors of 1.56-3.37 deg.

Declared C/G trials with final tilt 2.5-3.0 deg (near misses):

- arm: C 1 and G 2 of 874 and 890 declared;
- gantry: C 1 and G 1 of 892 and 898 declared;
- over 3 deg (bad units): 0.

**No plain fix.** The camera-type error, which is most of the class, needs a socket-axis reference
that does not come from the aim. C has none at the bottom of a latching cavity. A floor conform at
the bottom before the latch check might give one, but that is a behaviour change, and it was not
built or tested.

Folds are the other cause. *Post-hoc* (decided after seeing the data): a cap that refuses any fold
larger than 3 sigma of the characterized camera tilt would have acted on 14 dev verdicts. In 7 of them
the fold had made the socket estimate better, and in the other 7 worse (arm 4 better and 3 worse;
gantry 3 better and 4 worse). It does not separate good folds from bad ones, so it was not a
candidate.

## Item 2: J's empty first window

**Cause: J's hand-over code.** In `CompliantSpiralSearchVerifyController._succeed`
(`defex/control/spiral_verify.py`), J clears the verifier's sample window (`v._recent.clear()`) and
calls `v._begin_verify` on the same tick. C's code has not stepped yet, so the window is empty by
construction.

On the dev seeds, every hand-over gave no verdict: 562 of 640 arm J trials and 550 of 640 gantry J
trials. Every later J latch check (191 arm, 190 gantry) passed. These are the v0.2e tilt-guard counts.

**It cannot happen to C.** `AdaptiveInsertionController.step` appends the observation to `_recent`
before any state handler runs, so C's window always has at least one sample. C's low-force windows
are a different case (item 4).

**The window is not why J passed its arm bad unit** (`traces/j_mf_noise_1mm_46.txt`):

- F aims along the camera axis and J's `R_corr` is the identity, so J's plug axis is its reference
  axis;
- on the dev seeds the measured tilt at J's hand-over was 0.06 / 0.07 / 0.09 deg on the arm and
  0.17 / 0.31 / 0.69 deg on the gantry (p50 / p95 / max);
- on trial 46 the camera was 3.13 deg off: measured 0.06 deg against a true 3.21 deg. With any window
  the check would have passed.

J's tilt check can fail only when C's own compliance has turned the plug away from the aim.

**Fix (JW, default off):** `handover_window = True` hands C's VERIFY the last 25 samples of F's seat
push.

- Dev: kept by the rule. No row changed; tilt verdicts went 191 -> 753 (arm) and 190 -> 740
  (gantry), all PASS (`CAND_JW.md`).
- Seed 4007: no row changed; verdicts 99 -> 384 and 97 -> 378; GO (`VAL_JW.md`).
- The alternative, JP (P on J's verifier), was also kept: 0 good-part rejections added, 1 protective
  stop added at the bound of 1, and +0.30 s mean cycle on 712 trials (`CAND_JP.md`). The tie-break
  picked JW.

JW gives the check a window, but it does not make the check meaningful for J.

## Item 3: housing-only VERIFY (standard suite)

Accepted units, C and G, dev seeds, 25 trials per condition (`TABLES.md`, item 3):

| Machine | Ctrl | Declared | tilt p95 / max (deg) | tilt 2.5-3 | \|yaw\| p95 / max (deg) | \|yaw\| 2.5-3 | Bad units |
|---|---|---|---|---|---|---|---|
| arm | C | 973 | 0.02 / 0.60 | 0 | 1.33 / 1.94 | 0 | 0 |
| arm | G | 987 | 0.02 / 0.60 | 0 | 1.35 / 1.98 | 0 | 0 |
| gantry | C | 994 | 0.00 / 2.24 | 0 | 0.46 / 1.77 | 0 | 0 |
| gantry | G | 999 | 0.00 / 2.29 | 0 | 0.48 / 1.71 | 0 | 0 |

Tilt and yaw separately:

- **Tilt.** The five units at 2-2.5 deg are all gantry `noise_2mm`. The seat conform leaves the true
  tilt near 0. The plug axis against `R_corr` at the seat (p50 0.55 deg) is the camera's error, not
  the plug's tilt, so it gives no signal for a housing-only tilt check, as `results/v0.2d_tilt_check`
  found.
- **Yaw, arm.** The arm's wall-yaw check covers yaw. A PASS needs half the free y travel to be at
  least 0.293 mm. That is the travel of the rect_12x8 plug (half 6 x 4 mm, cavity half 6.5 x 4.5 mm)
  yawed 2.0 deg. Tilt only narrows the travel, so a PASS proves |yaw| <= 2.0 deg. The cavity alone
  would allow 4.9 deg. All 1,960 accepted arm units went through it, the largest |yaw| was 1.98 deg,
  and none was over 2.0 deg.
- **Yaw, gantry.** The gantry has no yaw check. Its yaw sweep centres the plug between two torque
  limits and always ends in SUCCESS. In 240 of 1,993 accepted C/G gantry units one sweep limit was the
  7.0 deg sweep end, meaning no wall was found on that side. Those units still ended at |yaw| <= 1.77
  deg. J's gantry bad unit in v0.2e (`heldout_mischar_2mm` trial 35, -3.61 deg) is that case:
  "limits (+0.0,+7.0) deg -> corrected +3.50 deg" (`../benchmark_v0.2e/gantry_heldout/events.json.gz`).
- **No plain yaw fix.** Failing a sweep that hits its end would act on 12% of accepted C/G gantry
  units, all with good yaw. It was not built.

Not covered: the heldout suite (mis-characterized vision), where H and I pass housing-only bad units.

## Item 4: tilt catches the force guard drops

Dev seeds, latching and latch_spread, C and G (`TABLES.md`, item 4):

- **Checks under the 11.75 N floor:** arm C 7 and G 8, all floor-impact settles at 8.2-11.0 N.
  Gantry: none.
- **Unguarded, the evidence would have failed one trial per controller.** That trial is 2027
  `mf_noise_1mm` 44: measured 3.07 deg, true 3.90 deg, CoP 1.95 at 10.9 N. It was a correct catch at
  that moment, but the plug was not fully home. With the guard, the pull failed, attempt 2 passed the
  check at 2.32 deg true, and the plug was seated (final 2.06 deg). The dropped catch cost nothing.
- The other 13 checks under the floor had true tilt <= 2.02 deg and would have passed.

**Fix (P, default off):** `AdaptiveConfig.tilt_check_push_below_floor = True`. Where the guard would
give no verdict, P first runs C's bottom-proof push, then takes the verdict on that push's window.
A push that advances the plug more than 0.1 mm goes back to INSERT.

- **Dev:** kept by the rule (`CAND_P.md`). 15 trials changed, all with the same outcome. Bad units,
  bad parts passed, rejections and stops all unchanged. The 80 control trials were identical. Cycle
  change on the 13 trials seated both ways: mean +0.99 s, max +2.33 s. On trial 2027/44 the push
  re-inserted the plug and gave a PASS on attempt 1 (17.63 -> 11.71 s).
- **On the arm the push usually times out**, at 30-31.6 N against the 35.2 N proof force. Its window
  is still over the floor, so the check gives a verdict.
- **Seed 4007:** 2 trials changed, same outcome, +2.26 s; GO (`VAL_P.md`).

## Flags-off identity

`identity/IDENTITY.md`: the v0.2e code (4df8cae, exported) against this branch (2702250,
`git_dirty: false`) with the flags off.

- Coverage: `experiments.robustness`, seed 2026, 10 trials; controllers C, G, J and F; latching
  (`mf_noise_1mm`, `mf_nominal`, `mf_half_latched`) and standard (`noise_1mm`, `tilt_5deg`,
  `yaw_5deg`), both machines.
- Result: 480 trials, 17,280 `trials.csv` fields (wall time ignored), 0 differences.
- The second gantry standard collection (yaw events kept) gave the same rows as the first.

## Tests

`tests/test_v02f_tilt_flags.py` adds 8 tests (9 cases): defaults off, the push path, no second push, an
unchanged verdict over the floor, and the J hand-over window. The full fast suite passes.

## What did not work, or is uncertain

- Neither option removed a bad unit or caught a tilted part on any seed. They are kept by a
  no-harm rule, not for an observed benefit.
- Near misses are few (5 declared at 2.5-3.0 deg on the dev seeds), so the rate of tilted bad units
  is not measured beyond "rare". G's v0.2e unit is about 1 in 600 arm `mf_noise_1mm` G trials on one
  seed.
- The cause attribution uses small-angle projections. It is a label, not a proof, for errors that
  partly cancel.
- The standard suite was cut to 25 trials per condition because the machine was shared (load average
  over 50). The gantry standard collection was run twice; the first file is not committed.
- Binaries: the collector rows (`runs/*.jsonl.gz`, 8.9 MB) are committed because every number above
  comes from them. Per-tick traces are not committed.
- Fairness: P and JW change only C's VERIFY code (C, G, J). No fair baseline has a tilt check, so
  there is nothing equal to give them.

## Ready to merge?

As default-off code, yes: with the flags off the rows are identical, and the tests pass. Switched on,
no: neither option changed an outcome on 3 seeds, and P costs about 1-2 s on the trials it acts on.
Whether to offer either option is Hasan's call.
