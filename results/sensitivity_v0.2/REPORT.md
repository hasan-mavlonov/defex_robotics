# Sensitivity of controller C to its constants (development measurement)

Every one of the 113 numeric fields of `AdaptiveConfig` scaled by 0.5, 0.8,
1.2 and 1.5, one at a time, on `noise_1mm`, `noise_2mm` and `friction_1` x 20
trials of development seed 2026 (27,180 trials, 47 min on an Apple M5). Code:
commit 29660b4 plus `experiments/sensitivity.py` (committed in fe48eca).
Command: `python -m experiments.sensitivity`.

- Baseline: 60 of 60 (100%), median cycle 8.10 s.
- **No cliffs**: no +/-20% change costs more than 10 points of success. No
  setting crashed.
- Largest losses, all at +/-50%: `stall_force_fraction` x1.5 and
  `time_limit_s` x0.5 (-8.3 points each); `max_insert_speed_mm_s` x0.5 and
  `conform_damping_nm_s_per_rad` x0.5 (-5.0). At +/-50% another 26 settings lost
  points (4 at -3.3, 22 at -1.7); over all four scales 44 settings lost something,
  most of them one trial in 60. Full table in `sensitivity.csv`, the 30 most
  sensitive in `sensitivity.png`. (Corrected in review: the first version said
  "seven more".)
- Two settings are distorted: `time_limit_s` x1.2 and x1.5 exceed the harness's
  30 s trial cap, so those runs end on the harness timeout, not C's own limit.
- Not swept: two thresholds still hard-coded after the W2 refactor, the yaw-search
  trigger (`blocks_at_best >= 2` in adaptive_fsm.py) and the contact-release factor
  in failure_detector.py (`0.5 * contact_force_n`).
- No setting improved success by more than 3 points.

Limit of this measurement: the baseline is at the ceiling (60 of 60), so the
sweep can show losses but not gains, and 60 trials resolve about 2 points.
It says C is not balanced on a knife edge of its own constants in MuJoCo; it
says nothing about transfer to hardware.
