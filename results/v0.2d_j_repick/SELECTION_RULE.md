# J re-pick on the integrated v0.2d code: selection rule

Written and committed before any run it ranks.

## Why a re-pick

J's response to a failed check was picked in `results/v0.2d_j_verify` (pick: (b) re-search) on the
benchmark_v0.2c code base, insert target 30 N. Most of (b)'s gain was on `latch_spread`
(`mf_terminal_max`), where F stalled at 30 N and C's proof push at 35.2 N carried the plug in on the
second hand-over. The integrated code (`v0.2d/integration`, f2791a5) changes what that pick rested on:

- every controller's insert target is 35.2 N (`v0.2d_force_budget`), so F itself may now seat those parts;
- C's latching VERIFY, which J runs, has the tilt check (`v0.2d_tilt_check`);
- A, B and E use the stiffness along the push on the arm (`v0.2d_axial_stiffness`; does not touch J);
- H and I have one push-and-pull retry (`v0.2d_pull_retry`; does not touch J, whose pull is C's).

## Candidates

Unchanged from `results/v0.2d_j_verify/SELECTION_RULE.md`, both with the RCC terms:

- **(a) reject**, `spiral_rcc_verify_reject`.
- **(b) re-search**, `spiral_rcc_verify_research`.

Known before the runs: at J's hand-over, C's sample window (`_recent`) is empty, so the tilt check's
CoP input is 0 at J's first latch check and the check cannot fail there; on J it can act only within
an attempt it has already failed. J's encoders do not see the RCC stage's tilt. Neither is changed
for this re-pick.

## Runs ranked

Dev seed 2026, gantry and arm, all four suites, 20 trials per condition, at the commit that adds this
file: C, F, I and both candidates in the same run (`run.sh`, PHASE=dev).

## Rule

The same rule as before, over both machines and all four suites pooled, in this order:

1. Fewer bad units passed (escapes on good-part conditions plus deliberately bad parts passed, `is_escape`).
2. More good parts seated.
3. Lower median cycle time of the successful good-part trials.

A step decides only when the two differ; equal at all three: (a).

The pick is written into `spiral_verify.py` (`on_verify_fail`) and committed before validation.

## Validation

Once, on fresh validation seed **4005** (no `config.json` under `results/` uses it), same machines,
suites and trials, both candidates and F (`run.sh`, PHASE=val). The same rule is applied. If it ranks
the other candidate first, the pick does not change and the report says so.

Tables: `python -m experiments.v02d_j_tables results/v0.2d_j_repick --pick <pick>`.
