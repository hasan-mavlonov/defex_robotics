# Baseline fairness run: draft pre-registration

**DRAFT, not frozen. Hasan decides whether to run this. Nothing has been run.**

This is the benchmark entry for the two baseline fairness items being built today on
other branches. Their designs are not final. Every value that depends on them is a
placeholder in angle brackets (`<...>`). No validation or benchmark seed has been spent
for them. Power numbers come from `POWER.md` in this folder (made by `power_v02g.py`
from committed trials.csv only). Seeds read "seed to be assigned when frozen".

## 1. Question

`results/v0.2f_checkpoint/CHECKPOINT_REPORT.md` item 8 lists two fairness items, one
each way:

- **Against C**: no fair baseline squares the part after seating. A conventional
  seat-and-align step might close much of C's tilt, yaw and bad-unit edge.
- **Against the baselines**: C caps its retract pull on a latching part at 36 N and
  retracts at 15 mm/s; D, F, H and I retry-retract at 40 mm/s with no working cap. On
  development seed 2027 the uncapped D and H tore two good gantry latches. The v0.2f port
  of C's cap was dropped by its own rule (`results/v0.2f_baseline_retract_cap/REPORT.md`).

The questions:

1. Does a conventional seat-and-align step cut I's and F's bad units on good parts?
2. With it, does C still seat more good parts than the best fair baseline, per machine
   and suite?
3. Does a gentle retract stop D, F, H and I tearing good latches, without losing parts?
4. Does either change move any headline verdict?

The pitch is Hasan's decision. This run does not pick it.

## 2. The two items (designs not final)

### 2.1 Seat-and-align (branch `v0.2g/seat-align`)

Design: `results/v0.2g_seat_align/DESIGN.md` on that branch (commit c1cb247). Summary:

- New controllers **K** = I plus seat-and-align, **K2** = F plus seat-and-align. Names in
  the registry: `<K name>`, `<K2 name>`.
- A post-seat phase entered where F's seat rule would declare the seat (on K, before I's
  retention pull): press with zero-torque rotational compliance (a force-mode face match),
  one decaying yaw dither under compliance, then a final press and F's own depth window.
  A short or unpressed plug goes to F's own jam path.
- It reads only F's own state, the observation and the context. It does not use, call or
  copy C's VERIFY. No F/T re-zero in contact.
- Parameters are set from the drawing, the datasheets and the fixture characterization
  (deadband, speed limits, dither amplitude, offset bounds). The design table lists their
  bases. Final values: `<T_db>`, `<T_band>`, `<w_tilt per machine>`,
  `<w_yaw per machine>`, `<free_yaw per part>`, `<free_tilt per part>`, `<bounds>`.
- Commissioning: seed 2026 only, trial indices 0-9, six named conditions, at most 3
  revisions, each logged with its reason before RULE.md. Seed 2027 not looked at before
  RULE.md. Commissioning log: `<to be filled on that branch>`.
- Acts on housing-only and latching parts: `<confirm>`.

### 2.2 Gentle retract (branch `v0.2g/gentle-retract`)

Rule: `results/v0.2g_gentle_retract/RULE.md` on that branch (commit 97343c6), committed
before its development runs. Summary:

- Four default-off candidates for D, F, H and I, latching parts only:
  V1 `@slow` (retry retract at 15 mm/s, C's speed), V2 `@slowcap` (V1 plus the v0.2f
  cap), V3 `@slowhold` (V1, cap, hold and fail in place), V4 `@slowarm` (V1, cap, a
  re-seat whose aborts arm only once the axial force is back at or above zero).
- Every value is C's or the baseline's own (15 mm/s, 36 N). Nothing is searched.
- The rule picks at most one candidate to propose, on development seeds 2026 and 2027
  only. That rule says the pick "does not enter any benchmark", so this entry needs a
  validation step first (section 4).
- The flags reach J's F phase. J's VERIFY is C's code, unchanged.
- Chosen candidate: `<pick, or none>`. Variant name in this run: `X@<pick>`.

## 3. What must be frozen before the run

- [ ] Each item's development decision by its own committed rule: seat-align
      `<RULE.md commit>` KEEP, gentle retract `<RULE.md commit>` pick `<V?>`. An item
      that is not kept is not in this run, and its fairness item stays open with the
      failing cells named.
- [ ] Each kept item's validation on a fresh seed (section 4) passed.
- [ ] Flags-off identity: with the new flags off, every existing controller gives the
      v0.2e rows (as `results/v0.2f_tilt_diagnosis/identity/IDENTITY.md` did).
- [ ] Frozen commit `<hash>` with both items merged; `git_dirty: false` in every
      `config.json`; the variants file `<path>` and its sha256 `<sha>`.
- [ ] Every parameter value in section 2 filled in.
- [ ] Fast tests and the architecture test pass at the frozen commit.
- [ ] The table scripts (`checkpoint_report`, `cp2_audit`, `v02c_paired`,
      `v02d_headline`, `heldout2_tables`) accept K, K2 and the `@` variants, and treat
      them as fair baselines.
- [ ] Seeds V2 and B2 assigned and checked unused (`grep -rl <seed> results`).
- [ ] The "Expected from development" section written from the dev and validation
      results, before the run.
- [ ] Hasan approves the CPU plan (section 10): the full plan is over the brief's 4-hour
      line.

## 4. Seeds and validation

| Use | Seed |
|---|---|
| Development | 2026 and 2027 only (each item's own branch) |
| Validation (once per item) | seed V2, to be assigned when frozen |
| Benchmark | seed B2, to be assigned when frozen |

Spent, do not use: 2026 and 2027 (development only), 3001-3040, 3031, 3032, 4001-4006,
4007, 20261025, 20261031, 20261102, 20261107, 20261108, 20261109, 20261116, 20261123,
20261124, 20261130, 20261201, 20261205, 20261207. Unspent but reserved: 4008 and
20261210; this draft does not assign them. If the C design round also runs, its seeds V
and B must differ from V2 and B2, or the two entries must share one validation and one
benchmark seed by Hasan's choice.

**Validation on seed V2, once.**
- Seat-align: `standard` and `latching`, both machines, 20 trials per condition, K and K2
  against I and F on the same trials. GO if no K-only or K2-only bad part passed, no
  K-only bad unit, net good-part rejections and protective stops within the item's own
  RULE.md bounds (computed from V2's counts), and K's bad units on good parts below I's.
- Gentle retract: `latching` and `latch_spread`, both machines, 20 trials per condition,
  `X@<pick>` against X for D, F, H, I. GO if the item's RULE.md checks 1-5 hold on every
  cell. Check 6 (fewer tears) is reported but not required, because tears are rare (2
  torn in 360 gantry good-part dev trials for D and for H; `POWER.md` table 5).
- A NO-GO drops the item from this run. No second try on seed V2.
- Neither item may run heldout2 on any seed before this benchmark. The seat-align design
  already excludes it (DESIGN.md, "What is deliberately not in the step").

## 5. Benchmark design

Base seed B2. Both machines. The run starts from a commit that changes only `results/`.
`RUN_LOG.md` records the clean tree, environment, times and workers.

**Controllers.**

| Name | Role | Suites |
|---|---|---|
| C, J | references (v0.2e) | all |
| D, E, F, H, I | v0.2e fair baselines | all |
| K, K2 | seat-and-align fair baselines, if kept | all (latching only if the step acts there) |
| D, F, H, I `@<pick>` | gentle-retract fair baselines, if kept | latching, latch_spread |
| K, K2 `@<pick>` | both items together, if both kept and the step acts on latching parts | latching, latch_spread |

The gentle retract acts only on latching parts, so its variants are not run on the
housing-only suites; there they would give the parent's rows.

**Suites and trials.**

| Suite | Trials per condition | Pairs per controller per machine | Why |
|---|---|---|---|
| standard | 100 | 2,000 | where C's lead and I's bad units sit |
| heldout (old) | 100 | 500 | I passes most housing-only bad units here; not a clean test |
| heldout2 | 100 | 1,000 | unseen tilt and yaw, where C leads by VERIFY; clean for these items |
| latching | 400 | 2,800 (1,200 good) | torn latches are rare; see power |
| latch_spread | 100 | 900 (600 good) | as v0.2e |

**Commands** (to be fixed when frozen):

```
for M in gantry arm; do
  for S in standard:100 heldout:100 heldout2:100; do
    DEFEX_CONTROLLER_VARIANTS=<variants file> python -m experiments.robustness \
      --suite ${S%%:*} --backend $M --trials ${S##*:} --seed <seed B2> --workers 9 \
      --no-plots --name <folder>/${M}_${S%%:*} --controllers <housing-only list>
  done
  for S in latching:400 latch_spread:100; do
    DEFEX_CONTROLLER_VARIANTS=<variants file> python -m experiments.robustness \
      --suite ${S%%:*} --backend $M --trials ${S##*:} --seed <seed B2> --workers 9 \
      --no-plots --name <folder>/${M}_${S%%:*} --controllers <latching list>
  done
done
```

## 6. Endpoints

**Primary, seat-and-align family** (Holm over 4 tests):

| Id | Cell | Comparison | Metric |
|---|---|---|---|
| SA1g | gantry standard, 2,000 pairs | K vs I | bad units on good parts |
| SA1a | arm standard, 2,000 pairs | K vs I | bad units on good parts |
| SA2g | gantry standard, 2,000 pairs | C vs K | seated |
| SA2a | arm standard, 2,000 pairs | C vs K | seated |

**Primary, gentle-retract family** (one test):

| Id | Cell | Comparison | Metric |
|---|---|---|---|
| GR1 | gantry latching good parts, 1,200 pairs | H`@<pick>` vs H | torn good latches (`final_latch_intact` False) |

H is chosen because the first tears were seen on H's retry, and H is a comparison in the
bad-unit claims. D tore the same two dev trials as H; D is secondary.

**Secondary.**
1. Every cell (machine x suite, and machine x heldout2 family): C vs the best fair
   baseline by the v0.2e decision rules (`results/benchmark_v0.2e/PREREGISTRATION.md`),
   with the best taken over D, E, F, H, I plus the kept new baselines. The same with the
   v0.2e set only, for continuity.
2. Bad units on good parts: C vs K, C vs K2, K2 vs F, per cell. Bad parts passed: K vs I
   (K must still reject bad parts through I's pull), K2 vs F.
3. Harm checks: K vs I and K2 vs F seated, and each `@<pick>` vs its parent seated, every
   cell. Any loss at p < 0.05 goes in the report headline.
4. heldout2 `h2_tilt_unseen` and `h2_yaw_unseen`: C vs K, J vs K, K vs I (seated and bad
   units). This is where C's lead is mostly VERIFY.
5. J vs K: C's VERIFY on F's insertion against a conventional square-up on I's insertion.
6. Torn good latches for every controller; D`@<pick>` vs D.
7. Cycle p50 and p95, good units per hour (0 s and 60 s per stop), protective stops, for
   every controller, next to its success.
8. Final tilt and yaw of K's and K2's declared units (distribution), against I's and F's.

## 7. Multiplicity

- Seat-and-align family: Holm over SA1g, SA1a, SA2g, SA2a, family-wise 0.05.
- Gentle-retract family: GR1 alone at 0.05.
- Secondary: no correction, as in every earlier run; outcomes at 0.01 <= p < 0.05 are
  marked. Pooled totals are descriptive and get no test.
- "Matches" means no significant difference, not equal. McNemar cannot show two
  controllers equal; where C vs K reads "matches", the report gives the discordant counts
  and the 95% interval of the difference.

## 8. Power

From `POWER.md` tables 4 and 5. Scenario for seat-and-align: K turns a share f of I's bad
units into seated parts and changes nothing else. The design can also turn a bad unit into
a declared failure (F's jam path). That cuts bad units but not C's lead, so f counts only
the seated conversions.

| Test | Observed (three benchmark seeds pooled) | f | Scenario rates | Power at 2,000 | at alpha 0.0125 |
|---|---|---|---|---|---|
| SA1g, K vs I bad units | I 1.98% of gantry standard trials | 0.5 | 0.99% / 0 | 1.00 | 1.00 |
| SA1a, K vs I bad units | I 1.90% of arm standard trials | 0.5 | 0.95% / 0 | 1.00 | 1.00 |
| SA2g, C vs K seated | C-only / I-only 175 / 13 of 6,000; 111 of the C-only are I bad units | 1.0 | 1.07% / 0.35% | 0.73 | 0.52 |
| SA2g | | 0.5 | 1.99% / 0.28% | 1.00 | 1.00 |
| SA2a, C vs K seated | 156 / 44 of 6,000; 95 of the C-only are I bad units | 1.0 | 1.02% / 1.05% | 0.04 | 0.01 |
| SA2a | | 0.5 | 1.81% / 0.89% | 0.67 | 0.45 |

What the scenarios say, before any data:
- If K seats every part where I passed a bad unit, C's arm standard lead goes to about
  zero (1.02% against 1.05% of trials), and C's gantry lead shrinks to about 1.07%
  against 0.35%; at 2,000 pairs the gantry lead would still be found with power 0.73
  (0.52 under Holm).
- If K fixes half, C stays ahead on both machines, and the arm test has power 0.67.
- heldout2 (one seed, 80 pairs per family): every C-only trial against I in `h2_tilt_unseen`
  and `h2_yaw_unseen` is an I bad unit (gantry 7 and 50, arm 12 and 48). So K's effect
  on those families decides whether C's heldout2 lead survives. At 200 pairs per family
  and f = 0.5, C vs K has power 0.87-1.00 (table 4).

Gentle retract, from development seeds only (2 torn trials in 120 gantry latching
good-part trials for D and for H; 0 for F and I; 0 on the arm and on latch_spread):

| Test | Dev tear rate | f | Power at 600 pairs (latching at 200) | at 1,200 pairs (latching at 400) |
|---|---|---|---|---|
| GR1 | 1.67% | 1.0 | 0.93 | 1.00 |
| GR1 | 1.67% | 0.5 | 0.38 | 0.93 |

- The dev rate rests on 2 trials; the true rate could be several times lower or higher.
  If it is near 0.5%, even 1,200 pairs will not show a difference.
- F and I, the best baselines on latching, tore no latch on the dev seeds. So the gentle
  retract is not expected to move any latching headline, where F and I are the best fair
  baselines (`results/benchmark_v0.2e/HEADLINE_TABLES.md`).

## 9. Decision rules

- As benchmark_v0.2e, applied per cell, with the extended set of fair baselines (D, E, F,
  H, I, K, K2 and the kept `@<pick>` variants) for "best fair baseline". Ties go to the
  first of D, E, F, H, I, K2, K, then the `@` variants.
- K and K2 are fair baselines only if they use nothing from C (the design's "No copy of
  C's VERIFY" list, checked in review before freezing).
- SA1: "the step cuts I's bad units" only where K passes fewer than I with Holm-adjusted
  p < 0.05, else "no significant difference".
- SA2: "C ahead of K" only with Holm-adjusted p < 0.05; "C below K" likewise; otherwise
  "K matches C", which goes in the README headline, and Hasan decides how the pitch
  changes.
- GR1: "the gentle retract prevents tears" only with p < 0.05; otherwise "no significant
  difference", with counts.
- Zero counts get Wilson upper bounds. C's and J's cycle time and throughput are reported
  next to their success, including where they are worse.

## 10. Rough time and CPU

Per-trial CPU from `POWER.md` table 6. K and K2 are assumed to cost about what J costs
(F's insertion plus a post-seat step bounded at about 2.2 s on the gantry and 6.4 s on the
arm, `DESIGN.md`). `@` variants cost about their parents.

| Plan | CPU hours | Wall at 9 workers, quiet machine | Wall at 2 workers |
|---|---|---|---|
| Full (section 5): housing-only suites 12.8, latching at 400 plus latch_spread 30.6 | about 43 | about 4.8 h | about 22 h |
| Full plus K and K2 `@<pick>` on latching | about 49 | about 5.5 h | about 25 h |
| Latching at 200 instead of 400 | about 31 | about 3.5 h | about 16 h |
| Split: seat-align entry (housing-only suites, latching 200, latch_spread) | about 26 | about 2.9 h | about 13 h |
| Split: gentle-retract entry (latching 400, latch_spread) | about 25 | about 2.7 h | about 12 h |
| Validation on seed V2, both items | about 2 | about 15 min | about 1 h |

- The full plan crosses the brief's 4-hour line, so it needs Hasan's approval, or a cut.
  The cuts above lower GR1's power (0.38 instead of 0.93 at f = 0.5 with latching at
  200). Splitting into two entries keeps each under 4 hours but is the same total work;
  it should be presented as one decision, not as a way round the line.
- If the C design round also runs, its benchmark can carry these baselines instead
  (`C_DESIGN_ROUND.md` section 12: about 37 CPU hours with K and K2, about 47 with the
  gentle variants too).

## 11. Stop conditions

- An item fails its development rule or its validation: it is not in this run. If both
  fail, there is no run; the fairness items stay open, with the failing cells named.
- Any change would need to break the ground-truth separation: stop and ask Hasan.
- The frozen estimate is over 4 hours: stop and ask Hasan.
- A run that stops early is repeated with the same command, and `RUN_LOG.md` says so. A
  bug found by the run: fix, new pre-registration, fresh seed, superseded report kept in
  `earlier_runs/`. No result is read until every run finishes.

## 12. What each result would mean

| Result | Meaning |
|---|---|
| SA1 significant, K's bad units near 0 | A conventional square-up removes most of I's housing-only bad units in simulation. C's bad-unit edge on housing-only parts then reads as "against a cell without a seat-and-align step". |
| SA1 not significant | This seat-and-align design does not fix I's bad units. The fairness item closes in C's favour for this design only, not for every possible one. |
| SA2 "C ahead" on both machines | C's standard lead survives a fairer baseline. The concentration finding (lead in 1-2 mm camera error, checkpoint item 1) still applies. |
| SA2 "K matches C" on a machine | That machine's standard lead was mostly I's bad units, which a conventional step removes. It goes in the README headline. |
| SA2 "C below K" | Goes in the README headline. |
| heldout2 tilt and yaw: K matches C | C's heldout2 tilt and yaw lead, mostly VERIFY, is matched by a conventional step. |
| J vs K close | A conventional square-up does about what C's VERIFY does on F's insertion. The "C or J" question gains a third option: a conventional cell with seat-and-align. |
| GR1 significant | The gentle retract prevents the baselines' torn latches; the fairness item closes. |
| GR1 not significant, no harm | The baselines carry the gentle retract anyway (equal effort, no cost found); the tear rate was too rare to show a difference. |
| Any harm check fails | Goes in the report; that variant is not used as a fair baseline in later runs without a new rule. |

Whether any result changes the pitch is Hasan's decision.

## 13. Disclosed before the run (to keep in the frozen version)

- Both items were designed after the benchmark results were seen. The seat-align design
  used POST HOC development traces of F's bad units (seed 2026, gantry). Its commissioning
  trials (seed 2026, indices 0-9 of six conditions) are inside its development runs.
- The gentle-retract rule had a smoke run on seed 2026 (`mf_noise_1mm`, trials 0-7) before
  it was written, disclosed in its RULE.md.
- The tear rate behind GR1's power rests on 2 development trials.
- Seeds 2026 and 2027 have been used for every decision since W1.
- C was not changed for this run. If the C design round runs too, its C2 is reported
  separately.
