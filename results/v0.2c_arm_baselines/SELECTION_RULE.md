# v0.2c arm tuning of D, E and F: selection rule

Committed before any arm tuning run. Development seed 2026 only (the W1 tuning seed).
Backend: UR5e arm. Script: `experiments/tune_baselines.py --backend arm` (grids and
condition lists are the `ARM_*` constants there). Settings are applied to each
controller's stiff-fixture config, which only fixtures outside the gantry family
select (`defex.control.base.outside_reference_family`, thresholds 4x wrist stiffness
or 2x servo lag, the same as C's W5b rules). Every gantry keeps the gantry config.

## Why the protocol differs from W1

- **Conditions.** W1 tuned on housing-only conditions; it predates the Micro-Fit
  latching connector (W3), which the reported benchmark includes and where D loses
  most on the arm (dev seed 2026: mf_nominal 12/20 against F 20/20). Coarse and fine:
  W1's six (`lateral_3mm, yaw_5deg, tilt_5deg, noise_1mm, noise_2mm, friction_1`) plus
  `mf_nominal, mf_noise_1mm`. Speed stage and confirm: W1's 18 development families
  plus `mf_nominal, mf_moderate, mf_noise_1mm` (21). The four bad-part conditions and
  the two generalization conditions are never tuned on.
- **Compute.** The machine is shared (another benchmark plus other agents); arm trials
  run at about 0.4 to 0.7 per second on the 2-3 workers allowed. W1 used about 34,000
  trials for D and F each; this protocol uses about 4,200 each. Cuts, stated exactly:
  - coarse grid: 81 settings, not 324. Search force {2, 3, 5} N (W1 coarse 3, 5, 8
    plus the edge value 2; 8 N never made the gantry top five), pitch {0.5, 1.0, 1.5} mm
    (W1 1.0-2.5 plus edge 0.5; 2.0 and 2.5 dropped), spiral speed {2.5, 5, 10} mm/s
    (W1 5-20 plus edge 2.5; 20 dropped), lateral stiffness {stiff, 2, 0.5} N/mm (all of
    W1's), push distance fixed at 0.5 mm in coarse (both gantry winners) and varied in
    the speed stage.
  - 3 trials per condition in coarse, fine and speed (W1: 10, 10, 20); 10 in confirm (W1: 20).
  - fine: top 3 coarse settings (W1: 5) x insert force {3, 5, 8} x attempts {2, 3}
    (W1 also had 1, never in the gantry top five) x seat margin {0.5, 1.0}: 36 settings.
  - no separate edge stage: its values are inside the coarse grid.
  - confirm: top 3 (W1: 5).
- **Arm-specific stage ("speed"), added.** The fine winner x push distance {0.3, 0.5,
  1.0} mm x guarded speed {10, 25} mm/s nominal (Flexiv insertVel, applied to both the
  descent and the insertion; the W5 rule scales these to 4 and 10 mm/s on the arm) x
  `hole_at_measured_position` {off, on}: 12 settings on all 21 conditions. The last is
  the one mechanical change offered: on hole found, continue from the measured tip
  position instead of the commanded spiral point, which leads the plug by speed x
  0.2 s on the UR5e. It is selected or not by the same rule as every other parameter.
- **E.** W1's grid unchanged (18 settings: insert speed {2, 4, 8} mm/s, overtravel {0.25,
  0.5, 1.0} mm, approach height {2, 5} mm) on the 8 coarse conditions, 3 trials; confirm
  top 3 on the 21 conditions, 10 trials.

## Ranking rule

Within every stage: success rate, then median cycle time, then 95th-percentile cycle
time. Cycle times are over all trials of the setting, failures included, as W1
computed them (`tune_baselines.evaluate`). The setting ranked first in the confirm stage is installed
as the controller's stiff-fixture config. Carried forward between stages: coarse top 3
-> fine; fine top 1 -> speed; speed top 3 -> confirm (D, F); coarse top 3 -> confirm (E).

No other criterion enters the choice. Escapes (failed parts passed as good),
protective stops and time limits are recorded per setting and reported, not ranked on.

## Afterwards (not selection)

Before/after on dev seed 2027 (arm, standard 5-condition set and latching suite, A-G,
20 trials; full 20 standard conditions, 5 trials) and on dev seed 2026 (arm, the same
5-condition set and latching suite). Gantry rule-3 set, A-G, for field identity.
Validation seed 4002 is not used by this rule; seeds 3032, 3031, 4001 and all
reserved benchmark seeds are not run.

## Amendment 1 (committed before any run that uses it)

Written after D's coarse, fine and speed stages and before D's confirm stage
finished (it was stopped with no output) or any F or E run.

**What was seen.** In D's speed stage, the faster guarded speed (25 mm/s nominal,
10 mm/s on the arm) seated 3 or 4 of 63 against 59 or 60 of 63 at 10 mm/s nominal.
A diagnostic trace (nominal, trials 0-2) shows why: the floor contact at 10 mm/s with
the arm's 0.2 s lag trips D's 20 N force abort (21.7-23.4 N). So the W5 speed scaling
is what keeps D inside its force budget, and a single faster speed cannot be used.
The `hole_at_measured_position` option made no difference to success (60 against
60) and is left to the rule.

**What is added.** The fix an integrator would make, and the one C already has
(`free_insert_speed_mm_s`, `near_bottom_*`): two speeds. Inside the cavity, outside
the mouth band (3 sigma of vision z plus the chamfer) and more than a margin above
the floor (plus 3 sigma when the face was not touched), move at a free speed, then at
the tuned guarded speed. New config fields `free_speed_mm_s` (0 = off, the default and
every gantry value) and `near_floor_margin_mm`; the W5 contact-speed rule scales the
free speed like the others.

**New stage "speed2"** (D and F, after "speed"): the speed winner x free speed {15, 25}
mm/s nominal (C's free-insert speed, and the faster value above) x near-floor margin
{2, 4} mm (C's 2 mm, and double): 4 settings on the 21 confirm conditions, 3 trials.

**Confirm** then takes the top 3 of the speed and speed2 settings ranked together
(same 21 conditions and trials; a speed-stage setting has the two-speed option off),
by the same rule. Nothing else changes. D resumes at speed2 with its coarse, fine and
speed results kept.
