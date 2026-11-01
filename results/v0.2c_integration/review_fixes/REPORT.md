# v0.2c integration (branch `v0.2c/integration`): report

Development and validation results on the allowed seeds. This is not a benchmark. Every number comes from a committed file under `results/v0.2c_integration/`; the path, run commit and seed are given. Nothing was pushed. Main, the cp2 worktree, `v0.2/checkpoint2` and `results/benchmark_v0.2b` were not touched. I did not read any `benchmark_v0.2b` trials.csv.

## 1. What the branch is

`v0.2c/integration` starts from Checkpoint 2 (54f3097 code, tip 883db25). It merges the four v0.2c workstreams with `--no-ff`:
- arm-baselines (668823c)
- defect-verdict (a31600c)
- arm-robustness (625b1af)
- learned-prior (3333496)

The only conflicts were in the per-workstream table scripts (now `experiments/v02c_robustness_tables.py` and `v02c_prior_tables.py`). Every command is in `commands.sh`, including section 5 for the review fixes.

Two independent reviews followed (12 findings). The fixes are the eight commits after 5131f29 (66bc8d0 to 36ca4b1). Section 6 goes through them one by one.

## 2. Workstream claims on the merged code (`claims_merged/comparison.md`, seeds 2026 and 2027, code 8d343f8)

- **A, B, D, E, F:** field-identical to each workstream's after-runs on every set (0 differences).
- **C on the gantry:** identical on the standard suite. On latching, the defect-verdict rules change 38 of 70 trials; seated 29 to 29, stops 3 to 2.
- **C on the arm:** standard-5 on seed 2026 seated 92 of 100 (Checkpoint 2's C: 86). Latching on seed 2026 seated 56 of 60 good parts (53), with 0 of 80 bad parts passed.
- **G:** changes wherever C changes.

## 3. G retrained on the integrated C (`prior/`)

**Process:**
- The rule `prior/SELECTION_RULE.md` was committed at 0ace479, before any data.
- Contact data with C (seeds 3001-3030) and DAgger data with G (seeds 3033-3040) were collected at 0ace479.
- Candidates were trained at 0692c04.
- The offline rule (`prior/OFFLINE_RESULT.md`) carried three candidates per backend to seed 4002 (run at dfbbdb9).

Results are in `prior/validation/<backend>/selection.md` and `tables.md`. **These are selection-seed figures.** Seed 4002 chose the installed models, so the p-values are not independent tests.

| Backend | C | Reference g_v1 | Installed | Installed vs C (C-only / G-only, p) |
|---|---|---|---|---|
| gantry | 378/400 | 387/400, 0 bad units | posterior K=3: 392/400, 0 bad units | 5 / 19 (0.0066) |
| arm | 435/500 | 461/500, 1 bad unit | g_v1 kept (no candidate ranked above it) | 5 / 31 (1.3e-05) |

**Safety suite (180 trials per variant):** every variant seated all 60 good parts on both backends, except arm residual K=2 tempered at 59 of 60 (`mf_moderate` #3, aborted:retry_limit). That variant was already excluded for a bad unit. No variant passed a safety-suite bad part.

**The gate was asymmetric.** It excluded candidates for one bad unit but did not gate the reference: g_v1 was installed on the arm with 1 bad unit (461/500). Posterior K=3 had 465/500 and also 1 bad unit. `g_lp` seated 461 with 0 bad units. The rule was followed as written. I did not re-select on 4002. For the v0.2c pre-registration the gate should apply to the reference too.

**Installed models:**
- gantry: `prior/models/gantry_posterior_k3.json`
- arm: the v1 model (c17fdb80, byte-identical to 54f3097's)

## 4. A-G snapshots on the code before the review fixes (`snapshot_seed2026`, `snapshot_seed3032`; code 96a4be3)

**Run details:**
- Seed 2026 (dev) was run at 96a4be3. Seed 3032 (the one out-of-sample check) was run at 586caed.
- 20 trials per cell.
- The seed-3032 snapshot measures the code before the review fixes. It cannot be re-run (single use).

The pre-registered rules applied per suite are in each `TABLES.md`. Recomputed views are in `review_fixes/REVIEW_TABLES.md`.

**C against the best fair baseline (D/E/F):**
- C was ahead with p < 0.05 only on gantry standard (both seeds) and arm standard on seed 2026 (p 0.021).
- Everywhere else a fair baseline matched C.

**G against C, paired, good parts:**
- On seed 3032, no single suite reaches p < 0.05.
- G is ahead of or tied with C on all six suites.
- Pooled over the six suites (**not pre-registered**): G-only / C-only = 27 / 8, p 0.0019. Arm alone: 16 / 5, p 0.027. Gantry alone: 11 / 3, p 0.057.
- Seed 2026 pooled: 28 / 3, p 4.6e-06.

**Throughput and stops.** Good units per hour on good parts, counting 60 s per protective stop (`REVIEW_TABLES.md`):
- F has more good units per hour than C on every suite and seed. Seed 3032: gantry standard 882 vs 617; gantry latching 603 vs 459; gantry heldout 424 vs 341; arm standard 589 vs 370; arm latching 480 vs 305; arm heldout 308 vs 179.
- G's arm-heldout gain on seed 2026 (86 vs 79 seated, p 0.016) comes with more protective stops: 7 vs 3 (seed 3032: 6 vs 4). Throughput is unchanged (185 vs 186).

**Bad parts.** Before the fixes: C and G passed 0 of 80 per backend; D, E and F passed 21-46. That gap mostly measured whether a retention pull test exists (section 6, R2-4). D on gantry Micro-Fit seats few good parts: 24 of 60 on seed 2026. Gantry D and F were never tuned on the latching connector.

## 5. Diagnosis of arm escapes and false rejects (`diagnosis_arm_escapes/comparison.md`)

- The 4 arm escapes in the integrated C's training data (tilt 3.087-3.258 deg) also appear at arm-robustness a5bd452.
- The 148 false rejects at defect-verdict afa08a4 alone fall to 4 when the workstreams are integrated.
- The tilt blind spot is not arm-only. The push-click-pull and wall-probe checks cannot see a seat just past 3 deg on either backend: 1 of 3,600 gantry training trials (noise_2mm #21, 3.049 deg, also present in W9's data) and 4 of 4,800 arm training trials.

## 6. Review findings: reproduction and fixes

New tools used below:
- **`latch_spread` suite** (`experiments.robustness --suite latch_spread`). It varies the simulator's mating values per part: latch position ±0.2 mm, latch peak ±50%, terminal force 0.8-1.6× (the datasheet range). It has six good-part and three bad-part conditions. This is simulator-side only (`PartVariation`, `PartSpread`); the controller still gets the nominal `ConnectorSpec`, and a test checks that.
- **`review_fixes/equiv_before`** (run at 5131f29). It reproduces `snapshot_seed2026` field for field: 9,160 trials, 0 differences.

### R2-1 (high): the pull limit is the model's own latch geometry. Confirmed and fixed.

**Before** (`spread_dev2026_before`, run at 66bc8d0, seed 2026):
- With the latch 0.2 mm shallower (`mf_latch_early`), C seated 0 of 20 on the gantry and 1 of 20 on the arm.
- Every failure was `stuck_during_retract` with gt_seated False, so the false-reject metric did not count them.
- F seated 19 and 20 of 20.

**Fix:** a pre-registered selection on seed 4002.
- Rule: `verify_selection/SELECTION_RULE.md` (a59919b), plus amendment 1 (97d4121), both committed before any validation run.
- The gate applies to the current code too.

Results (`validation4002/selection.md`, code 97d4121, 30 trials, C only, latching + latch_spread, both backends):

| Candidate | Good parts seated | Bad parts passed (of 420) | Median / p95 cycle (s) |
|---|---|---|---|
| w3 (current) | 465/540 | 5 | 8.25 / 14.16 |
| noclick | 466/540 | 7 | 8.25 / 14.16 |
| w60 (29 N, 1.05 mm) | 531/540 | 6 | 8.25 / 14.13 |
| w80 (29 N, 1.40 mm) | 531/540 | 79 | 8.25 / 14.19 |
| w60f (35.2 N, 1.05 mm) | 532/540 | 0 | 8.56 / 14.46 |
| w80f (35.2 N, 1.40 mm) | 532/540 | 0 | 8.56 / 14.50 |

**Installed (b57e0db): w60f.** w3-only / w60f-only = 0 / 67, p < 1e-6.
- On the latching suite alone, w60f and w3 have the same counts: gantry 87/90, arm 85/90, 0 bad.
- The whole gain is on the spread suite. The w3 escapes were 5 `mf_spread_half_latched` parts (1 gantry, 4 arm).

Installed values (`AdaptiveConfig`):
- `click_required` = False
- `pull_limit_wipe_fraction` = 0.6: the plug must hold within 0.6 × the datasheet 1.75 mm terminal wipe
- `pull_test_mating_factor` = 1.1: pull at max(0.5 × 58 N, 1.1 × 32 N datasheet maximum mating force) = 35.2 N

### R2-2 (high): the click detector does not see the latch. Confirmed and fixed.

- In the seed-2026 snapshot event logs, the click was seen on 40 of 40 broken-latch checks per backend (median drop 7.8 N gantry, 8.0 N arm). That drop is the terminal friction falling from its entry peak to sliding.
- With w60f the click is logged but not required. The verdict is a retention pull test.
- The `unverified:latched_no_click` outcome can no longer occur with the defaults.

### Amendment 1: a defect found while reproducing R2-1, fixed by the same selection

- With the 29 N pull, two bad parts on the arm passed on dev seed 2026 (`mf_spread_half_latched` #3 and `mf_terminal_max_broken_latch` #2, terminal force 1.5-1.6×).
- Both held 29 N on friction alone, 0.77-0.79 mm out, with no latch.
- A wider limit makes this worse: w80 passed 79 bad parts on 4002. Hence the 35.2 N pull, added before validation.

### R2-3 (medium): the latching conclusions depend on the assumed terminal force. Confirmed and measured.

At the datasheet maximum terminal force (`mf_terminal_max`, seed 2026):

| Controller | Gantry seated | Gantry bad units passed | Arm seated | Arm bad units passed |
|---|---|---|---|---|
| F | 0/20 | 19 | 0/20 | 4 |
| D | 0/20 | 4 | 0/20 | 12 |
| C | 20/20 | 0 | 20/20 | 0 |

After the fix, on the whole latch_spread suite (seed 2026, b57e0db):
- C seats 120 of 120 per backend. The best fair baseline is E at 98 of 120 (gantry) and 101 of 120 (arm); C-only / E-only = 22 / 0 and 19 / 0.
- **Caveat:** C's latch check was chosen on this suite (on seed 4002), and the baselines were not tuned on it. The comparison favours C by construction.

### R2-4 (medium): only C and G run a pull test. Confirmed and measured.

D and F with C's installed check (variant `pull`, `SpiralSearchConfig.retention_pull`, off by default; `baseline_pull_dev2026`, seed 2026, b57e0db):
- They pass 0 of 80 latching bad parts and 0 of 60 spread bad parts on both backends.
- Before: F 45 and 44 of 80, D 24 and 42 of 80.
- Good-part success is unchanged (arm D latching: 51 to 50).
- The pull costs time. F good units/h: gantry latching 538 to 377, arm latching 519 to 340.

So the bad-part gap was the pull test, not the adaptive method.

### R2-5 (low): D's gantry bad-part count read as a merit. Fixed in the tables.

- The bad-part table (`experiments/checkpoint_report.py`) now shows each controller's good parts seated underneath. Gantry latching D seats 24 of 60.
- Gantry D and F are untuned on the Micro-Fit connector.

### R2-6 (low): throughput was reported only for arm standard. Fixed.

Throughput and stops per suite are now in `REVIEW_TABLES.md` (see section 4).

### R2-7 (low): the safety-suite sentence was wrong. Fixed.

Arm residual K=2 tempered seated 59 of 60 (section 3).

### R2-8 (low): seed 4002 was reused and the reference was not gated. Labelled; no re-selection.

- 4002 figures are labelled as selection-seed numbers (section 3).
- The new latch-check rule gates the reference.

### R1-1 (medium): the pooled G vs C comparison on seed 3032 was missing. Added.

See section 4, labelled not pre-registered.

### R1-2 (low): held_reseat skipped the depth gate. Confirmed and fixed (66bc8d0).

- A plug held while backing out is now checked only at the seat depth. Otherwise it is failed in place (`stuck_during_retract`).
- A unit test fails on the old code and passes on the new.
- It is field-identical on every run: `equiv_after1` equals `equiv_before` on 9,160 trials.
- The path ran 91 times in latch_spread, always at seat depth.

### R1-3 (low): the tilt blind spot is not arm-specific. Confirmed.

See section 5.

### R1-4 (low): the click detector uses assumed latch values. Confirmed; resolved by w60f.

With the defaults, the model's latch geometry and 6 N latch peak only feed the logged click. They no longer feed the verdict.

### R1-5 (low): test and tooling gaps. Fixed.

- `make_controller('d@v')` now also applies the overrides to `stiff_fixture_cfg` (what D, E and F run on the arm) and `dwell_s` (A, B). A test covers it.
- `tests/test_v02c_all_off.py` runs C with every v0.2c switch off on the first seed-2026 latching trials the rules change, and matches the committed 54f3097 rows.
- Committed set `alloff_final` (b57e0db) against `cp2_54f3097` (run at 54f3097): 1,280 trials (standard, latching and heldout, both backends), 0 differences.

## 7. What changed in the numbers (seed 2026, `review_fixes/before_after.md`, before = 5131f29, after = b57e0db)

**Field-identical:**
- A, B, D, E, F on every suite and both backends.
- C and G on standard (400 trials per backend) and heldout (100).

**Latching suite:**

| | Gantry | Arm |
|---|---|---|
| C seated | 58 to 58 of 60 | 56 to 56 of 60 |
| C stops | 3 to 4 | 0 to 0 |
| C median cycle (s) | 5.74 to 5.97 | 8.32 to 8.65 |
| G seated | 60 to 60 | 59 to 58 |
| Bad parts passed (C and G) | 0 of 80 | 0 of 80 |

**latch_spread suite (before at 66bc8d0):**

| | Gantry | Arm |
|---|---|---|
| C seated | 95 to 120 of 120 (0 / 25, p 6e-08) | 98 to 120 (0 / 22, p 4.8e-07) |
| G seated | 95 to 120 | 99 to 120 |
| Bad parts passed (C and G) | 0 to 0 of 60 | 2 to 0 of 60 |

**Not re-run:** the seed-3032 snapshot and the seed-4002 G selection.

## 8. What got worse

- **Slower cycles:** median cycle rises 0.2-0.3 s on latching parts (the 35.2 N pull and the longer allowed travel).
- **One more stop on gantry half-latched parts** (seed 2026: 3 to 4). After a failed pull the plug now slides 1.1 mm out instead of 0.8 mm, and the next insert met the obstruction at 51-52 N on two parts (one earlier stop went away).
- **One G unit lost on the arm** (`mf_noise_1mm` #4): the pull passed, but the re-seat ran into the 26 s time limit.
- **F's throughput falls about 30%** with the pull test. Numbers are in R2-4.
- **D on the arm stops more with the pull:** 3 stops on good parts vs 1 without it.

## 9. Open issues

- **The pull test can be fooled by friction at the edges of the datasheet range.** At 35.2 N the margin over the 32 N maximum mating force is 10%. A part whose withdrawal friction exceeds that would pass. Nothing in the datasheet bounds the unmating force from above.
- **Tilt is invisible to the latching verify** (about 1 in 1,000 on both backends).
- **The G models were trained on the old latch check's data.** They have not been retrained.
- **The latch_spread suite was used to choose C's check.** A fresh-seed measurement belongs in the v0.2c pre-registered test (seed 20261116), with all controllers.
- **Baselines have no pull test by default.** If the benchmark keeps the bad-part comparison, D and F should run `pull` too, or every bad-part table should say plainly that only C and G test retention.

## 10. Provenance

| Folder | Run commit | Seed | Trials per cell |
|---|---|---|---|
| `equiv_before` | 5131f29 | 2026 | 20 |
| `equiv_after1` | 66bc8d0 | 2026 | 20 |
| `spread_dev2026_before` | 66bc8d0 | 2026 | 20 |
| `cp2_54f3097` | 54f3097 | 2026 | 20 |
| `verify_selection/dev2026` (development only) | 97d4121 | 2026 | 20 |
| `verify_selection/validation4002` | 97d4121 | 4002 | 30 |
| `snapshot2026_after` | b57e0db | 2026 | 20 |
| `baseline_pull_dev2026` | b57e0db | 2026 | 20 |
| `alloff_final` | b57e0db | 2026 | 20 |

- Every `config.json` has git_dirty false.
- Every run used workers 3 (after Checkpoint 2's benchmark had finished), from temporary detached worktrees that were removed afterwards.
- Tests: 162 passed at 36ca4b1.
