# W3: latch physics and push-click-pull verification (development measurements)

Development seed 2026, 20 trials per cell. Not a reported benchmark: these runs
used an uncommitted working tree at the W3 branch; the next pre-registered run
(Checkpoint 2) will measure the committed code on a fresh seed.

## Physics (pinned by tests/test_mating_physics.py)

Molex Micro-Fit 3.0, 4 circuits (`assets/connectors/microfit3_4ckt.json`):
terminal friction from the 1.75 mm wipe (entry peak 20 N, sliding 12 N against
the datasheet's 32 N maximum mating and 9.6 N minimum unmating), a latch ramp
with a snap (6 N peak: assumed, no datasheet value), engaged latch holding the
rated 58 N then breaking. No manufacturer publishes a force-depth curve, so the
model is checked against the published force values, not a curve:

- wrist-F/T-measured mating peak within 15% of the model and under 32 N;
- latch holds to 58 N (within 15%) then breaks;
- a good part holds a 29 N pull (half the rated retention); broken-latch,
  half-latched and stubbed-terminal parts pull out; wrong polarization stops at
  the key, 1 mm in.

Force thresholds come from the connector's force budget (insert 30 N, abort
40 N, cell stop 48 N, damage 58 N) for every controller. Position programs
(A, B, E) are taught the overtravel that produces the insertion force.

## Push-click-pull VERIFY (controller C, latching parts)

1. Click: in the force-depth trace of the insertion, a force drop of at least
   40% of the latch peak where the snap should be. The window is placed relative
   to the depth the plug bottomed at (encoder-precise), not to the camera.
2. Guarded pull at 50% of the rated retention (29 N): pass if the plug moves
   less than the post-snap stroke plus 0.3 mm.
3. Re-seat to the floor, then declare success.
Wall probes and yaw centring are skipped on latching parts.

## Results

gantry latching (20 trials per cell; success / bad units passed):

| Condition | A | B | E | D | F | C |
|---|---|---|---|---|---|---|
| mf_nominal | 20 / 0 | 17 / 0 | 18 / 0 | 11 / 0 | 20 / 0 | 20 / 0 |
| mf_moderate | 2 / 0 | 16 / 0 | 16 / 0 | 12 / 0 | 19 / 0 | 20 / 0 |
| mf_noise_1mm | 0 / 0 | 1 / 0 | 1 / 0 | 3 / 0 | 15 / 0 | 18 / 0 |
| mf_half_latched | 0 / 0 | 0 / 17 | 0 / 17 | 0 / 12 | 0 / 10 | 0 / 0 |
| mf_broken_latch | 0 / 0 | 0 / 16 | 0 / 17 | 0 / 16 | 0 / 19 | 0 / 0 |
| mf_stubbed_terminal | 0 / 0 | 0 / 12 | 0 / 13 | 0 / 11 | 0 / 16 | 0 / 0 |
| mf_wrong_polarization | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Bad parts passed as good, all four defects (of 80): A 0, B 45, E 47, D 39, F 45, C 0

arm latching (20 trials per cell; success / bad units passed):

| Condition | A | B | E | D | F | C |
|---|---|---|---|---|---|---|
| mf_nominal | 20 / 0 | 17 / 0 | 17 / 0 | 12 / 0 | 20 / 0 | 19 / 0 |
| mf_moderate | 1 / 0 | 16 / 0 | 16 / 0 | 14 / 0 | 20 / 0 | 18 / 0 |
| mf_noise_1mm | 0 / 0 | 1 / 0 | 1 / 0 | 5 / 0 | 17 / 0 | 3 / 0 |
| mf_half_latched | 0 / 0 | 0 / 8 | 0 / 13 | 0 / 13 | 0 / 20 | 0 / 0 |
| mf_broken_latch | 0 / 0 | 0 / 16 | 0 / 17 | 0 / 16 | 0 / 20 | 0 / 0 |
| mf_stubbed_terminal | 0 / 0 | 0 / 1 | 0 / 1 | 0 / 4 | 0 / 16 | 0 / 0 |
| mf_wrong_polarization | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Bad parts passed as good, all four defects (of 80): A 0, B 25, E 31, D 33, F 56, C 0

Data: `data/gantry_latching`, `data/arm_latching`.

What this shows, with its limits:

- **C passed none of the 160 deliberately bad parts** (two backends x 80); the
  conventional cells passed many (gantry: B 45, E 47, D 39, F 45 of 80; arm:
  B 25, E 31, D 33, F 56 of 80). A depth check cannot tell a broken or
  half-engaged latch from a good one. 0 of 80 bounds C's false-accept rate below
  4.6% (95% Wilson upper limit) per backend at this sample size.
- On good parts C seated 58 of 60 on the gantry (F 54 of 60). On the arm it
  seats well with good vision (19 and 18 of 20) but fails under 1 mm vision noise
  (3 of 20, against F's 17): C's contact-based recovery still does not transfer to
  the serial arm (W5 report).
- C rejects some bad parts by tripping the cell's protective stop (pushing at
  its 30 N insertion target against an obstruction during retries): 7 of 80 on
  the gantry. Clean, but harsh; a gentler retry policy for "stalled short of the
  snap" is open.
- The terminal and latch model and its numbers (latch peak, post-snap stroke,
  latch stiffness) are assumptions where the datasheet is silent; a bench curve
  (hardware/TEST_PROTOCOL.md, calibration moves) is needed before any real claim.
