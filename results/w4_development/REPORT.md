# W4: joint (x, y, yaw) localizer and yaw verification (development measurements)

All numbers here are development measurements on seed 2026, not a reported
benchmark. The mis-characterized-vision families were pre-registered and run as
held-out in `results/heldout_v0.2`; using them here for development means a
future held-out evaluation needs new families.

## Joint localizer: built, validated, no measured gain

`defex/recovery/yaw_localizer.py` models the plug at a relative yaw: support
region = (rotated plug ∩ housing) minus the lead-in opening, CoP = projection of
the plug centre onto its hull; entry = closed-form fit of a rotated rectangle.

- Against the 2D model at zero yaw: identical on 12,769 offsets (blocked, missed,
  CoP to 1e-15 m).
- Against MuJoCo at 3-12 degrees of yaw: worst CoP error 0.10 mm (test bound 0.3 mm,
  `test_yaw_contact_model_matches_mujoco_at_nonzero_yaw`).
- In closed loop on `noise_2mm` (100 development trials): 94/100 with the joint
  localizer, 94/100 with V0.1's 2D localizer and yaw sequence, same median and
  p95 cycle, about 3x the compute. The contact readings carry little yaw
  information until the plug is nearly in, so the joint posterior mostly tracks
  the 2D one.

Decision: kept as `localizer_mode="xyyaw"`; C's default stays `"xy"`.

## Yaw verification: the fix that matters

Every bad unit C passed so far (replication seed: 1; held-out families: 29) was a
plug seated more than 3 degrees off in yaw. VERIFY re-centred yaw only when the
characterized vision yaw sigma exceeded 1 degree, and the wall probes cannot see
yaw. Policies compared (`yaw_center_policy`), 40 development trials per cell:

| Condition | sigma_gate (V0.1) | gate_or_corrected | always |
|---|---|---|---|
| nominal | 40, median 5.36 s | 40, 5.36 s | 40, 6.80 s |
| friction_1 | 38 | 38 | 38 |
| told 0.5 mm, true 1.0 mm | 37 (2 bad units, 1 stop) | 37 (2 bad, 1 stop) | 39 (0 bad, 1 stop) |
| told 0.5 mm, true 2.0 mm | 24 (6 bad units) | 24 (6 bad) | 30 (0 bad) |

"always" removes this class of escape and raises success where vision is worse
than claimed, at about 1.4 s more per cycle. It is the W4 default. This widens
the cycle-time gap to the spiral-search cell (3.5 s median), so it is flagged for
Hasan: zero bad units against throughput is a product decision.

Also seen: one protective stop by C (told 0.5 mm, true 1.0 mm), the first in any
run. Not yet analysed.
