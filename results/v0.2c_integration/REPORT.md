# v0.2c integration: four workstreams merged, G retrained, development snapshots

Development measurements in simulation on branch `v0.2c/integration`, branched from the tip of `v0.2/checkpoint2` (883db25). Its code equals the frozen Checkpoint 2 commit 54f3097 except for `experiments/cp2_audit.py`. This is not a benchmark.

- **Seeds run:**
  - 2026 and 2027 (dev);
  - 3001-3030 and 3033-3040 (training data, plus one diagnosis on 3001-3030);
  - 4002 (one selection, under a rule committed first);
  - 3032 (one out-of-sample snapshot, now spent).
  - No reserved or spent seed was run.
- **Benchmark files:** nothing under `results/benchmark_v0.2b/` was read or changed.
- **Provenance:** every `config.json` and model file has `git_dirty: false`. Every command is in `commands.sh`, in the order it was run.
- **Workers:** at most 3 simulation or training processes at a time. The Checkpoint 2 benchmark had already finished.

## Summary

1. **The four branches merge cleanly.** The only textual conflict was a table script added under the same name on three branches; the copies were renamed. The full test suite passes after each merge, and 147 tests pass at the end.
2. **The workstreams do not get in each other's way.** On every set where a workstream's claim should survive the merge, the integrated code reproduces that workstream's committed after-runs field for field. Where the two C workstreams touch the same trials (C on the arm with latching parts), their effects add up:
   - arm false rejects fall from 5 of 180 (defect-verdict alone) to 0 of 180;
   - time per bad part falls from 26.4 s (arm-robustness alone) to about 12.3 s.
3. **G retrained on the integrated C,** using the learned-prior recipe and its rules unchanged:
   - **Gantry:** the rule installed a new model (posterior K=3). It is not significantly better than v1: 392 against 387 of 400 on seed 4002 (p 0.12), and 357 against 355 of 600 on dev 2026 (p 0.62).
   - **Arm:** no retrained candidate ranked above v1, so the rule put the v1 arm model back (the Checkpoint 2 file, sha256 c17fdb80). This replaces the learned-prior workstream's residual K=3 model.
4. **Out-of-sample seed 3032:**
   - C stays ahead of the best fair baseline (F) only on the gantry standard suite: 100% against 97%, p 0.0005.
   - Everywhere else F matches C, within 3 points and p >= 0.08. That includes the arm standard suite: 98.0% against 96.0%, p 0.077.
   - C and G pass 0 of 80 bad parts on each backend (Wilson upper bound 4.6%). D, E and F pass 21-46 of 80.
   - G is not significantly better than C on any suite of seed 3032 (p 0.065 to 1).
5. **What got worse:**
   - **Tilted parts passed on the arm.** In the 2,400 arm training trials (noise_2mm and mf_noise_1mm), the integrated C passed 4 failed units as good, against 0 for Checkpoint 2's C. All 4 were seated 3.09-3.26 deg tilted, just past the 3 deg criterion. The diagnosis traces all 4 to the arm-robustness rules; the merge neither adds nor removes any.
   - **Cost of the defect verdict on arm good parts.** Adding it to the arm rules costs 13 lost and 5 gained seats on those trials (p 0.096), and 4 new false rejects.

## 1. Merges

| Merge | Conflicts | Tests after |
|---|---|---|
| v0.2c/arm-baselines (ffdc670) | none | 110 passed |
| v0.2c/defect-verdict (5054518) | none | 122 passed |
| v0.2c/arm-robustness (d7ff9aa) | `experiments/v02c_tables.py` (add/add). Arm-robustness's copy is now `experiments/v02c_robustness_tables.py`; `make_tables.sh` updated. | 130 passed |
| v0.2c/learned-prior (cc54d52) | The same file again. Learned-prior's copy is now `experiments/v02c_prior_tables.py`; its `commands.sh` and `dev_check.sh` updated. | 140 passed |

`adaptive_fsm.py` and `config.py` merged without textual conflicts. I read the merged C where the two C workstreams meet:
- `_to_detect`: the in-place un-jam and the floor-impact hold come before the excess-force hard-stop evidence;
- the latch-check retract path;
- VERIFY.

The arm-robustness rules are gated on the stiff wrist. The defect verdict is gated on a connector with a mating spec. So the two sets meet only on the arm with the Micro-Fit connector.

One way they can interact:
- The floor-impact hold renames the trigger to `floor_impact`, and `_stop_candidate` does not accept that trigger.
- So on the arm, a hard stop past the seat threshold can be diagnosed without counting as hard-stop evidence.
- In the measured runs, every arm bad part still ended with a defect verdict, except about 1 wrong-polarization part per 20-30 that hit the time limit (as in defect-verdict's own runs).
- I made no code change for it.

`tests/test_v02c_integration.py` (7 tests) checks:
- on the arm with a latching part, both rule sets are on;
- on the gantry, only the verdict is on;
- on the arm with the housing-only part, only the arm rules are on;
- each set switches off on its own;
- the comparison script and the `DEFEX_PRIOR_OUT` output root work;
- the installed models state every fixture field.

## 2. Each workstream's claims on the integrated code

- **Before:** each workstream's committed after-runs, at its own branch tip. These are the untouched results for each workstream, so no separate before run was needed.
- **After:** the same commands on the merged code at 8d343f8 (`claims.sh`).
- **Comparison:** `claims_merged/comparison.md` (`experiments/v02c_integration_compare.py`). Trials are matched on condition, trial index and seed; `wall_time_s` is ignored.
- During these runs the installed G models were still the learned-prior workstream's, so G's rows here are informational.

| Workstream claim | Set | Result on the integrated code |
|---|---|---|
| arm-baselines: A, B, D, E, F tuned and field-identical | gantry rule-3 standard and latching; arm seeds 2026/2027 standard-5 and latching; arm seed 2027 all 20 conditions | 3,550 trials, **0 differ**. D, E and F keep their arm-tuned numbers exactly. For example, seed 2027 latching: D 50 and F 56 of 60 good parts; D 39 and F 45 of 80 bad parts passed. |
| arm-robustness: C on the arm, housing-only connector | arm standard-5 seeds 2026 and 2027; all 20 conditions, seed 2027 | 300 trials, **0 differ**: 92, 90 and 98 of 100, as reported. |
| arm-robustness: no-op on the gantry | gantry rule-3 standard | 60 trials, 0 differ. Latching C changes by design (defect verdict). |
| defect-verdict: gantry C | gantry latching seeds 2026 and 2027 (30 trials); gantry standard (10 trials) | 620 trials, **0 differ**. |
| defect-verdict: arm C on latching parts | arm latching seeds 2026 and 2027, 30 trials | Changes, because the arm-robustness rules act here too. See below. |

C on the arm with latching parts, where both C workstreams act. 30 trials per condition, seeds 2026 and 2027 pooled; good parts out of 180, bad parts out of 240.

| | defect-verdict alone (afa08a4) | integrated | Paired: lost / gained (p) |
|---|---|---|---|
| Good parts seated | 161 | 168 | 0 / 7 (seed 2026: 0 / 3, p 0.25; seed 2027: 0 / 4, p 0.12) |
| False rejects | 5 | 0 | - |
| Protective stops | 5 | 5 | - |
| Bad parts passed | 0 | 0 | - |
| Mean time per bad part (s), seeds 2026 and 2027 | 12.4, 12.3 | 12.4, 12.2 | - |

Against arm-robustness alone (a5bd452), on its 20-trial arm latching sets:
- good parts seated: 56 against 56 (seed 2026) and 55 against 55 (seed 2027) of 60;
- mean time per bad part: 26.4 s against 12.5 s (seed 2026) and 26.4 s against 12.1 s (seed 2027);
- 0 bad parts passed on either side.

On the arm standard set at 5 trials (`arm_standard_cg`), C goes from 95 to 97 of 100 against defect-verdict's run (0 / 2, p 0.5). That is the arm-robustness gain, as expected.

No number a workstream reported for its own claim moved on the integrated code, except where the other C workstream acts on the same trials.

## 3. G retrained on the integrated C

The rule (`prior/SELECTION_RULE.md`) was committed at 0ace479, before any data collection with the integrated C. It is the learned-prior workstream's recipe, `OFFLINE_RULE.md` and `SELECTION_RULE.md`, unchanged. Where those files left something open, it states the choice in advance:
- **Candidate pool, both backends:** residual K=2, residual K=3, residual K=2 tempered, posterior K=3 and ratio K=3. Residual K=1 and the C-only ablation were never carried forward, so they are not trained.
- **Reference:** `g_v1` (the v1 models), as the rule names it.
- **Reported only:** `g_lp`, the learned-prior workstream's models (trained on Checkpoint 2's C). It is run and reported but not ranked.

**Data** (`prior/data/`, collected at 0ace479):

| Backend | C, seeds 3001-3030 | DAgger: G with the merge-time models, seeds 3033-3040 | Dev 2026 (reported only) |
|---|---|---|---|
| gantry | 3,900 trials, 9,827 records | 1,040 trials, 2,205 records | 240 trials, 514 records |
| arm | 5,100 trials, 11,668 records | 1,360 trials, 2,722 records | 300 trials, 630 records |

- **Gantry data against W9's:** every housing-only trial is identical. 149 of 1,200 mf_noise_1mm trials differ, from the defect verdict: protective stops 51 to 0, seats up 46, and 2 new false rejects.
- **Arm data against Checkpoint 2's:** 4,542 of 4,800 trials differ: seated 3,636 to 4,058, stops 224 to 142.
- **Replay check:** the analytic posterior replay still reproduces C's recorded posterior mean to 2e-15 mm on both backends.

**Training** (`prior/train.sh`, at 0692c04) uses the recipe's hyperparameters unchanged.

**Offline rule** (`prior/OFFLINE_RESULT.md`): stopping-split grid NLL in nats; lower is better.

| Backend | res K=2 tempered | res K=2 | res K=3 | post K=3 | ratio K=3 | Carried |
|---|---|---|---|---|---|---|
| gantry | 2.089 | 2.756 | 2.979 | 2.942 | 3.181 | tempered, res K=2, post K=3 |
| arm | 1.962 | 3.472 | 3.231 | 3.258 | 3.839 | tempered, res K=3, post K=3 |

**Seed 4002** (`prior/validation/<backend>/tables.md` and `selection.md`, at dfbbdb9). Ranking families at 100 trials each. Bad units are counted over the ranking and safety runs.

Gantry, 400 ranking trials per variant:

| Variant | Seated (Wilson 95%) | Bad units | vs C: C-only / new-only (p) | vs g_v1 (p) | Median / p95 cycle (s) |
|---|---|---|---|---|---|
| C | 378 (91.8-96.3%) | 0 | - | - | 7.08 / 15.24 |
| g_v1 | 387 (94.5-98.1%) | 0 | 6 / 15 (0.078) | - | 7.47 / 12.44 |
| g_lp (reported only) | 391 | 0 | 6 / 19 (0.015) | 3 / 7 (0.34) | 7.51 / 13.73 |
| res K=2 tempered | 386 | 0 | 11 / 19 (0.2) | 8 / 7 (1) | 7.33 / 11.60 |
| res K=2 | 388 | 1 (excluded) | 7 / 17 (0.064) | 4 / 5 (1) | 7.44 / 12.92 |
| **post K=3 (installed)** | **392 (96.1-99.0%)** | 0 | 5 / 19 (0.0066) | 1 / 6 (0.12) | 7.51 / 12.26 |

Arm, 500 ranking trials per variant:

| Variant | Seated (Wilson 95%) | Bad units | vs C (p) | vs g_v1 (p) | Median / p95 cycle (s) |
|---|---|---|---|---|---|
| C | 435 (83.8-89.7%) | 0 | - | - | 9.69 / 19.20 |
| **g_v1 (installed)** | **461 (89.5-94.2%)** | **1** | 5 / 31 (1.3e-05) | - | 9.98 / 18.29 |
| g_lp (reported only) | 461 | 0 | 8 / 34 (6.9e-05) | 12 / 12 (1) | 9.98 / 18.93 |
| res K=2 tempered | 455 | 1 (excluded) | 12 / 32 (0.0037) | 19 / 13 (0.38) | 9.80 / 18.23 |
| res K=3 | 460 | 0 | 9 / 34 (0.00017) | 8 / 7 (1) | 9.93 / 19.57 |
| post K=3 | 465 | 1 (excluded) | 6 / 36 (2.8e-06) | 10 / 14 (0.54) | 10.07 / 18.59 |

- **Safety suite** (180 trials per variant): every variant seated all 60 good parts on both backends and passed 0 bad parts.
- **Gantry decision:** posterior K=3 ranks above g_v1, so it is installed with the `install` subcommand.
- **Arm decision:** the only eligible candidate, residual K=3, ranks below g_v1 (460 against 461). The v1 model is installed.
- **The arm reference is not gated:** the rule's gate covers candidates only. g_v1 passed 1 bad unit on the arm ranking families. `g_lp` passed 0 and seated the same 461, but the rule does not rank it.
- **Dev 2026 check, gantry** (`prior/dev2026/gantry/tables.md`, at 96a4be3; 60 trials, 10 conditions): out of 600, C 350, g_v1 355, installed 357 (installed against v1: 1 / 3, p 0.62). No bad units for any of the three. The rule runs no arm check when v1 stays.

What this shows:
- Retraining on the integrated C did not produce a measurable gain over v1 on either backend.
- The learned-prior workstream's arm model (residual K=3 on Checkpoint 2's C) is reverted. That workstream had already called its arm gain "not established".
- The installed gantry model is a posterior-mode model, not a residual one. Under the pre-registered rule, that is a pick within noise.

## 4. Development snapshot, seed 2026, and comparison with Checkpoint 2 prep

Source: `snapshot_seed2026/TABLES.md` (`experiments/checkpoint_report.py`, code 96a4be3). All suites, 20 trials per cell. Seed 2026 is the development seed for C's arm rules and for the arm baseline tuning, so on the arm it favours C and D/E/F.

| Backend, suite | C | Best fair baseline | G | C vs F: C-only / F-only (p) | G vs C: C-only / G-only (p) | Bad parts passed: C / G / fewest of D, E, F |
|---|---|---|---|---|---|---|
| gantry standard | 100.0% | F 97.0% | 100.0% | 12 / 0 (0.00049) | 0 / 0 (1) | - |
| gantry latching (good parts) | 96.7% | F 90.0% | 100.0% | 5 / 1 (0.22) | 0 / 2 (0.5) | 0 / 0 / D 24 of 80 |
| gantry heldout | 83.0% | F 78.0% | 90.0% | 12 / 7 (0.36) | 3 / 10 (0.092) | - |
| arm standard | 97.8% | F 95.8% | 99.2% | 9 / 1 (0.021) | 0 / 6 (0.031) | - |
| arm latching (good parts) | 93.3% | F 96.7% | 98.3% | 1 / 3 (0.62) | 0 / 3 (0.25) | 0 / 0 / E 31 of 80 |
| arm heldout | 79.0% | F 77.0% | 86.0% | 10 / 8 (0.81) | 0 / 7 (0.016) | - |

C's cycle time and throughput, next to its success rate:
- **Gantry standard:** median cycle 5.29 s against F's 3.54 s; 635 against 870 good units per hour.
- **Arm standard:** median 8.15 s against F's 4.77 s; 379 against 585 good units per hour, counting 60 s per protective stop.
- **Time per bad part:** C 7.9 s on the gantry and 12.5 s on the arm, against F's 5.3 s and 9.0 s.

Against the Checkpoint 2 prep snapshot (`snapshot_seed2026/vs_checkpoint2_prep.md`; same seed, common trials only):

| Run | Controller | Checkpoint 2 prep -> integrated | Paired: lost / gained (p) |
|---|---|---|---|
| gantry standard (400 per controller) | A, B, C, E, F | 0 trials differ | - |
| gantry standard | G | 399 -> 400 | 0 / 1 |
| gantry latching (60 good parts, 80 bad) | C | good 58 -> 58; stops 7 -> 3; time per bad part 21.4 -> 7.9 s | 0 / 0 |
| gantry latching | G | good 60 -> 60; stops 12 -> 3; time per bad part 21.3 -> 8.0 s | 0 / 0 |
| arm standard, 5 conditions (100) | C | 86 -> 92 | 0 / 6 (0.031) |
| arm standard, 5 conditions | G | 91 -> 97 | 1 / 7 (0.07) |
| arm standard, 5 conditions | D / E / F | seated 83 -> 80 / 76 -> 75 / 84 -> 85; median cycle 6.5 -> 4.8 / 6.3 -> 4.1 / 6.5 -> 4.8 s | 4 / 1, 2 / 1, 1 / 2 |
| arm latching | C | good 53 -> 56; time per bad part 26.4 -> 12.5 s; bad parts passed 0 -> 0 | 0 / 3 (0.25) |
| arm latching | G | good 56 -> 59; time per bad part 26.3 -> 12.7 s | 1 / 4 (0.38) |
| arm latching | D | good 31 -> 51; bad parts passed 33 -> 42 of 80 | 0 / 20 (1.9e-06) |
| arm latching | F | good 57 -> 58; bad parts passed 56 -> 44 of 80 | 1 / 2 (1) |

The Checkpoint 2 prep snapshot predates the D setting fixed in benchmark_v0.2b's pre-registration. Its gantry D rows differ for that reason, not because of v0.2c: arm-baselines showed gantry D field-identical to 54f3097. Those rows are left out above.

## 5. Out-of-sample snapshot, seed 3032 (run once)

Source: `snapshot_seed3032/TABLES.md`. Code 96a4be3, run at 586caed, which differs from it only under `results/`. No choice was made on this seed.

| Backend, suite | C | Best fair baseline | G | C vs F: C-only / F-only (p) | G vs C: C-only / G-only (p) | Bad parts passed: C / G / fewest of D, E, F |
|---|---|---|---|---|---|---|
| gantry standard | 100.0% | F 97.0% | 100.0% | 12 / 0 (0.00049) | 0 / 0 (1) | - |
| gantry latching (good parts) | 96.7% | F 91.7% | 98.3% | 4 / 1 (0.38) | 1 / 2 (1) | 0 / 0 / D 21 of 80 |
| gantry heldout | 87.0% | F 86.0% | 94.0% | 11 / 10 (1) | 2 / 9 (0.065) | - |
| arm standard | 98.0% | F 96.0% | 98.8% | 12 / 4 (0.077) | 3 / 6 (0.51) | - |
| arm latching (good parts) | 93.3% | F 95.0% | 98.3% | 0 / 1 (1) | 0 / 3 (0.25) | 0 / 0 / E 30 of 80 |
| arm heldout | 79.0% | F 82.0% | 84.0% | 10 / 13 (0.68) | 2 / 7 (0.18) | - |

benchmark_v0.2b's decision rules, applied mechanically (last section of `TABLES.md`):
- C is ahead of every fair baseline only on the gantry standard suite.
- On the other five suites, a fair baseline matches C.
- On the arm heldout and arm latching suites F is numerically ahead (82.0% against 79.0%, and 95.0% against 93.3%), but not significantly.
- G shows no measurable gain over C on any suite of this seed.

Bad parts passed as good, out of 80:

| Controller | Gantry | Arm |
|---|---|---|
| C | 0 | 0 |
| G | 0 | 0 |
| D | 21 | 41 |
| E | 44 | 30 |
| F | 46 | 46 |

The Wilson 95% upper bound for C's and G's 0 of 80 is 4.6%.

Failed units passed as good on good-part conditions (standard and heldout suites): 0 for C and G on both backends; 8-12 per suite for F and 6-14 for D.

Arm standard:
- C median cycle 8.12 s against F's 4.78 s; 370 against 589 good units per hour (60 s per stop).
- Time per bad part: C 12.4 s on the arm and 8.0 s on the gantry, against F's 10.2 s and 5.7 s.

## 6. Diagnosis: arm escapes and false rejects in the training data

The integrated C's arm training data (seeds 3001-3030, 40 trials each) had escapes and false rejects that Checkpoint 2's C did not have on the same trials.
- **Method:** I ran C at each C workstream's final code on the same trials: noise_2mm and mf_noise_1mm, 1,200 each. The runs used temporary detached worktrees, since removed.
- **Sources:** `diagnosis_arm_escapes/escapes.txt` and `comparison.md`.

| Code | noise_2mm: seated / escapes / stops | mf_noise_1mm: seated / escapes / false rejects / stops |
|---|---|---|
| Checkpoint 2 C | 636 / 0 / 44 | 781 / 0 / 0 / 125 |
| defect-verdict (afa08a4) | 636 / 0 / 44 | 795 / 0 / 148 / 40 |
| arm-robustness (a5bd452) | 830 / 1 / 53 | 982 / 3 / 0 / 41 |
| integrated | 830 / 1 / 53 | 974 / 3 / 4 / 23 |

**Escapes.**
- All 4 come from the arm-robustness rules; the integration neither adds nor removes any.
- Each is a plug seated past the 3 deg tilt criterion that C declared good: 3.09 deg on noise_2mm; 3.16, 3.20 and 3.26 deg on latched mf_noise_1mm parts.
- arm-robustness reported this blind spot of the push-click-pull check (one 3.04 deg case on dev seed 2026) and turned off re-aim for latching parts. Its in-cavity tilt rules still let a few such seats through, about 0.3% of these hard trials.
- The dev and out-of-sample snapshots are too small to see this rate; they show 0 escapes.

**False rejects.**
- The defect verdict alone produced 148 of 1,200 on arm mf_noise_1mm: latched parts with no detected click. On its dev seeds it had shown 5 of 180.
- With the arm-robustness rules in front of it, the integrated C has 4.

**Cost of the defect verdict on arm good parts.** Integrated against arm-robustness alone:
- 13 lost and 5 gained seats (p 0.096), all on mf_noise_1mm;
- protective stops 94 to 76;
- false rejects 0 to 4.

I did not change C for either finding. Both need a decision from whoever owns C's verify: a tilt check before a latched part is passed, and click detection on the arm.

## 7. Equivalence summary

| What | Set | Result |
|---|---|---|
| A, B, D, E, F against arm-baselines (e054ff0) | 7 sets, gantry and arm, seeds 2026/2027 | 3,550 trials, 0 differ |
| C against arm-robustness (a5bd452): housing-only connector and gantry standard | 4 sets | 360 trials, 0 differ |
| C against defect-verdict (afa08a4), gantry | latching seeds 2026/2027, standard | 620 trials, 0 differ |
| A, B, C, E, F against the Checkpoint 2 prep snapshot, gantry standard | seed 2026 | 2,000 trials, 0 differ |
| Gantry C training data against W9's, housing-only rows | noise_1mm and noise_2mm, seeds 3001-3030 | 2,400 trials, 0 differ |

## 8. Open issues

- **Arm tilted-seat escapes** (section 6): 4 of 2,400 hard arm training trials, from the arm-robustness rules. Not fixed.
- **Arm false rejects of latched parts without a click:** 4 of 1,200 on the training data with the integrated C, and 148 with the defect verdict alone. The cause is the click detector on the arm. Not fixed.
- **G: no measurable gain from retraining on either backend.**
  - The gantry install is a pick within noise.
  - The arm reference (v1) passed 1 bad unit on seed 4002, and the rule does not gate the reference. `g_lp`, which seated the same 461, passed 0.
  - Whether to keep the rule's choice is for the main agent.
- **Floor-impact hold and hard-stop evidence** (section 1): the hold renames the trigger, so a hard stop at the floor on the arm does not count as hard-stop evidence. It did not show up as a missed verdict in these runs, but it was not tested on its own.
- **Not merged:** `v0.2c/verify-fixes` (e84bbbf: the wall-yaw check now fails a plug the walls clamp). It was not in the integration list. If it is merged later, C on the arm changes, and G's arm data would need collecting again under the same rule.
- **DAgger round:** it used the learned-prior workstream's models on the integrated C, not the models now installed. One round only, as in the recipe.
- **Seed 3032 is spent.** A v0.2c pre-registered test needs seed 20261116, which was not touched here.
