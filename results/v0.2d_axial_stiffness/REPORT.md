# v0.2d: taught overtravel along the insertion axis (arm)

Development work, dev seeds 2026 and 2027, UR5e arm, latching and latch_spread suites,
20 trials per condition and seed. Compared, trial by trial, with
`results/v0.2d_force_budget/after` (34520aa, insert target 35.2 N). This run: commit
331885a (fix at 4748791), `git_dirty: false`. Commands: [`run.sh`](run.sh).

## Why

After the insert target went to 35.2 N, E lost 25 of 120 latching and 53 of 240
latch_spread good parts on the arm to protective stops
([`../v0.2d_force_budget/REPORT.md`](../v0.2d_force_budget/REPORT.md)). A, B and E
teach their overtravel as target / stiffness, and the stiffness used was the arm's
weakest translational direction (8.0 N/mm, y). They push along z (10.8 N/mm), so the
static push was about 1.34 x the target, 47 N against the 48 N stop.

## Change

`ControllerContext.insertion_stiffness_n_per_mm`: the stiffness along the insertion
axis at the home pose, set by the arm backend (1 / C[2,2] of the same Cartesian
compliance, 10.76 N/mm on the Micro-Fit scene). `taught_overtravel` uses it when it is
set. The gantry backend does not set it (10 N/mm on every axis), so nothing changes on
the gantry. `FixtureDynamics` is unchanged, so G's model lookup is unaffected. Only A,
B and E read the overtravel, and only on a connector with a force budget. Test:
`tests/test_arm_baselines.py::test_taught_overtravel_uses_the_stiffness_along_the_push`.

## Result (good parts seated, before -> after; lost / gained, exact McNemar)

| Suite | A fixed | B correction | E correction_rcc | C | I |
|---|---|---|---|---|---|
| latching, good 120 | 41 -> 41 | 29 -> 68 (0 / 39, p = 3.6e-12) | 49 -> 74 (0 / 25, p = 6e-8) | 110 -> 110, identical | 114 -> 114, identical |
| latch_spread, good 240 | 0 -> 1 | 88 -> 193 (0 / 105, p = 4.9e-32) | 153 -> 206 (0 / 53, p = 2.2e-16) | 238 -> 238, identical | 230 -> 230, identical |

Protective stops on good parts, E: latching 71 -> 46, latch_spread 87 -> 34; B: 91 -> 52
and 152 -> 47. E is back to its v0.2c count on both suites (74 and 206). C and I
(which do not read the overtravel) are field-identical on all 640 trials each (280 latching, 360 latch_spread).

Deliberately bad parts passed (no pull test in A, B, E): E latching 28 -> 83 of 160,
latch_spread 51 -> 104 of 120; B 23 -> 72 and 30 -> 94. With the push no longer cut
short by the stop, broken-latch parts are pushed deep enough for the depth check, as
with D and F after the force fix.
