# Simulator randomization: result (pre-registered)

Seed 20261108, commit 294fd2e (code frozen at fe48eca), 12 randomized MuJoCo
variants plus the nominal one, 6 conditions (nominal, lateral_3mm, noise_1mm,
noise_2mm, friction_1, generalization_tight) x 20 paired trials x 6
controllers = 9,360 trials. Bands and per-variant draws in `variants.json`;
pre-registration in [`../heldout_v0.2/PREREGISTRATION.md`](../heldout_v0.2/PREREGISTRATION.md).

| Variant | A | B | E | D | F | C | C minus best of D/E/F | cone | servo (N/mm) |
|---|---|---|---|---|---|---|---|---|---|
| 0 (nominal) | 22.5 | 70.0 | 74.2 | 85.0 | 86.7 | 95.0 | +8.3 | elliptic | 10.0 |
| 1 | 22.5 | 66.7 | 73.3 | 79.2 | 85.8 | 95.8 | +10.0 | elliptic | 16.6 |
| 2 | 22.5 | 71.7 | 73.3 | 80.8 | 85.8 | 97.5 | +11.7 | elliptic | 14.2 |
| 3 | 22.5 | 70.0 | 74.2 | 85.0 | 86.7 | 95.0 | +8.3 | elliptic | 6.8 |
| 4 | 22.5 | 70.0 | 74.2 | 82.5 | 85.8 | 96.7 | +10.8 | elliptic | 10.5 |
| 5 | 22.5 | 70.8 | 75.0 | 82.5 | 86.7 | 96.7 | +10.0 | elliptic | 10.7 |
| 6 | 20.0 | 61.7 | 69.2 | 70.8 | 85.0 | 95.8 | +10.8 | pyramidal | 19.2 |
| 7 | 22.5 | 70.8 | 74.2 | 85.8 | 86.7 | 95.0 | +8.3 | elliptic | 7.9 |
| 8 | 22.5 | 68.3 | 73.3 | 79.2 | 85.8 | 97.5 | +11.7 | elliptic | 16.9 |
| 9 | 20.8 | 62.5 | 69.2 | 66.7 | 85.0 | 97.5 | +12.5 | pyramidal | 18.5 |
| 10 | 22.5 | 67.5 | 71.7 | 75.8 | 85.0 | 95.8 | +10.8 | pyramidal | 14.8 |
| 11 | 22.5 | 70.8 | 71.7 | 79.2 | 85.8 | 96.7 | +10.8 | elliptic | 13.6 |
| 12 | 22.5 | 70.0 | 73.3 | 67.5 | 85.8 | 96.7 | +10.8 | pyramidal | 9.3 |

Success in percent of 120 trials per cell. C leads the best conventional
controller in all 13 simulators, by 8.3 to 12.5 points; no variant reverses
the ranking (the pre-registered threshold was more than 2 of 12). C ranges
95.0-97.5%, F 85.0-86.7%; D is the most simulator-sensitive (66.7-85.8%),
mostly with the pyramidal friction cone. The comparison does not hinge on one
tuning of MuJoCo's contact model. It says nothing about real parts: that is W7.
