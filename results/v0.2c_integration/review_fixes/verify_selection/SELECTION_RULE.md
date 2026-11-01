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
