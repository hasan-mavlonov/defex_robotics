# Selection rule: C's latch check (v0.2c review fix)

Written and committed before any validation run of these candidates. Development runs on dev seeds
2026 and 2027 may happen before or after this commit; they do not choose.

## Why

Review findings (v0.2c integration review, fairness):

1. The pull limit (the model's 0.5 mm post-snap stroke + 0.3 mm margin = 0.8 mm) is the simulator's own
   assumed latch geometry. A latch that engages 0.15 mm earlier fails the pull on a good part.
2. The "click" detector fires on the terminal friction falling from its entry peak to sliding, not on
   the latch (all 40 broken-latch checks per backend on dev seed 2026 showed a "click").

## Candidates (AdaptiveConfig overrides; variants file `../variants.json`)

| Name | click_required | pull_limit_wipe_fraction | Pull limit on Micro-Fit |
|---|---|---|---|
| w3 | True | 0.0 | 0.8 mm (model stroke + margin), the current code |
| noclick | False | 0.0 | 0.8 mm |
| w60 | False | 0.6 | 1.05 mm (0.6 x the datasheet 1.75 mm terminal wipe) |
| w80 | False | 0.8 | 1.40 mm |
| w60click | True | 0.6 | 1.05 mm |

Basis of the wipe fractions: the latch must hold before the terminals have backed out by that share of
their datasheet wipe (they stay mated by the rest). Neither fraction is fitted to the simulator.

## Validation run

- Seed 4002 (validation seed), 30 trials per condition.
- Controller C only (`adaptive@<name>`); G runs the same latch check and inherits the choice.
- Suites `latching` (3 good, 4 bad-part conditions) and `latch_spread` (6 good, 3 bad-part conditions),
  both backends (gantry, arm), at the commit that adds this file. Workers 3.
- Folder: `validation4002/<backend>_<suite>/`.

## Rule

1. Gate: a candidate is eligible only with 0 bad units passed (failed, not stopped, declared success)
   summed over both backends and both suites, good-part and bad-part conditions alike. The gate
   applies to the current code (w3) as well.
2. Rank the eligible candidates by good-part successes summed over both backends and both suites,
   then by median cycle time of those successes (pooled), then by p95, then by the order of the table.
3. Install the first. If none is eligible, keep w3 and report it.
4. Applied mechanically by `python -m experiments.v02c_verify_select <folder>`; output committed as
   `validation4002/selection.md`. Paired McNemar p against w3 and Wilson intervals are reported, not used.

The installed setting is then checked once on dev seed 2026 (snapshot) and is never re-selected on 4002.

## Amendment 1 (before any validation run of any candidate)

Made after the development run `../spread_dev2026_before` (dev seed 2026, code 66bc8d0, the current C):
on the arm, C passed 2 of 60 latch-spread bad parts (`mf_spread_half_latched` #3,
`mf_terminal_max_broken_latch` #2). Both had terminal forces 1.5-1.6 x the model's (inside the
datasheet range) and held the 29 N pull on friction alone, 0.77-0.79 mm out, with no latch. Neither
the pull limit nor the click changes this. A third knob, `pull_test_mating_factor`, pulls at least
that factor x the datasheet maximum mating force (1.1 x 32 N = 35.2 N, the proof-push basis).

Candidates now (replacing the table above; `w60click` is dropped, the rest unchanged):

| Name | click_required | pull_limit_wipe_fraction | pull_test_mating_factor | Pull |
|---|---|---|---|---|
| w3 | True | 0.0 | 0.0 | 29 N, 0.8 mm (current code) |
| noclick | False | 0.0 | 0.0 | 29 N, 0.8 mm |
| w60 | False | 0.6 | 0.0 | 29 N, 1.05 mm |
| w80 | False | 0.8 | 0.0 | 29 N, 1.40 mm |
| w60f | False | 0.6 | 1.1 | 35.2 N, 1.05 mm |
| w80f | False | 0.8 | 1.1 | 35.2 N, 1.40 mm |

The run, gate, ranking and tie order are as above (tie order = this table's order). A dev-seed-2026 run
of these six (`dev2026`) is development only.
