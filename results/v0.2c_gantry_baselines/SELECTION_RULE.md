# v0.2c gantry re-tuning of D, E and F on the latching connector: selection rule

Committed before any run of this protocol. Development seed 2026 only (the W1
tuning seed). Backend: gantry. Script: `experiments/tune_baselines.py --backend
gantry --protocol v02c`.

## Why

W1 tuned D, E and F on the gantry before the Micro-Fit latching connector existed
(W3). benchmark_v0.2b then ran them on latching parts at those settings, and C's
gantry latching lead (95.7% against F's 89.0%, D 56.7%) may partly reflect that.
The arm got a latching-aware tuning pass in v0.2c
(`results/v0.2c_arm_baselines/SELECTION_RULE.md`); this applies the same protocol
to the gantry so both machines are treated alike.

## Protocol

Identical to the v0.2c arm protocol (same grids, conditions, stages, carry-forward
and ranking rule), applied to each controller's gantry config (`ctrl.cfg`, what
every gantry runs), with W1's trial counts instead of the arm's reduced ones,
because gantry trials are cheap:

- Conditions. Coarse and fine: `lateral_3mm, yaw_5deg, tilt_5deg, noise_1mm,
  noise_2mm, friction_1, mf_nominal, mf_noise_1mm`. Speed, speed2 and confirm: W1's
  18 development families plus `mf_nominal, mf_moderate, mf_noise_1mm` (21). Bad
  parts and the two generalization conditions are never tuned on.
- D and F: coarse (81 settings, `ARM_SPIRAL_GRID`) -> top 3 x fine (36,
  `ARM_SPIRAL_FINE`) -> top 1 x speed (12, `ARM_SPIRAL_SPEED`) -> top 1 x speed2
  (4, `ARM_SPIRAL_SPEED2`) -> confirm top 3 of speed and speed2 together.
- E: coarse (18, `CORRECTION_GRID`) -> confirm top 3.
- Trials per condition: 10 in coarse, fine, speed and speed2 (W1: 10); 20 in
  confirm (W1: 20).
- Ranking within each stage: success rate, then median cycle time, then p95 cycle
  time, over all trials of the setting (`tune_baselines.evaluate`). Escapes,
  protective stops and time limits are recorded, not ranked on.

The setting ranked first in confirm is installed as the controller's gantry config,
unless it is the setting already installed, in which case nothing changes.

## Afterwards (not selection)

Before/after on dev seed 2027: gantry standard suite (20 conditions x 10 trials)
and latching suite (20 trials), A-G. Arm field identity for A, B, C, G and for D, E,
F's stiff-fixture configs (arm, seed 2026, standard 5-condition set and latching
suite). No other seed is run.
