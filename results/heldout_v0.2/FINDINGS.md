# Held-out vision families: result (pre-registered)

Seed 20261109, commit 8408cdb (code frozen at fe48eca), 3,000 paired trials,
[`PREREGISTRATION.md`](PREREGISTRATION.md). Success out of 100 per family:

| Family | A | B | E | D | F | C | Bad units passed, F / C |
|---|---|---|---|---|---|---|---|
| told 0.5 mm, true 1.0 mm | 11 | 42 | 50 | 89 | 92 | 92 | 7 / 7 |
| told 0.5 mm, true 2.0 mm | 10 | 8 | 11 | 33 | 36 | 54 | 43 / 22 |
| hidden 1.5 mm hand-eye bias | 7 | 40 | 44 | 100 | 100 | 97 | 0 / 0 |
| 5% vision outliers | 9 | 93 | 93 | 100 | 100 | 100 | 0 / 0 |
| worst case (mu 0.8, 0.2 mm clearance, told 0.5 true 1.0) | 0 | 4 | 40 | 23 | 85 | 56 | 0 / 0 |
| **all five** | 7.4% | 37.4% | 47.6% | 69.0% | **82.6%** | **79.8%** | 50 / 29 |

Paired, C vs F over all five: C-only 27, F-only 41 (exact McNemar p = 0.1).
Per family (pre-registered; added in review):

| Family | C-only | F-only | exact McNemar p |
|---|---|---|---|
| told 0.5 mm, true 1.0 mm | 1 | 1 | 1.0 |
| told 0.5 mm, true 2.0 mm | 22 | 4 | 0.0005 (C ahead) |
| hidden 1.5 mm hand-eye bias | 0 | 3 | 0.25 (not significant) |
| 5% vision outliers | 0 | 0 | 1.0 |
| worst case | 4 | 33 | 1e-6 (F ahead) |

C against the matching correctly-characterized conditions of benchmark_v0.2a
(pre-registered; added in review): `noise_1mm` 100 -> 92 when told 0.5 mm with a
true 1.0 mm; `noise_2mm` 95 -> 54 when told 0.5 mm with a true 2.0 mm.

**Pre-registered rule triggered.** C's lead over the best fair baseline reverses
in the worst case (F 85, C 56, p = 1e-6). With the hand-eye bias F is ahead too
(100 against 97) but not significantly (p = 0.25). Overall F is ahead, not
significantly.

Why, from the trial records:

- **All 29 of C's bad units (7 and 22 in the two mis-characterized families) are yaw.** The plug seated at full depth more than
  3 degrees off in yaw. C re-centres yaw in VERIFY only when the characterized
  vision yaw sigma exceeds 1 degree; here it was told 0.83 degrees while the true
  error was larger, and the wall probes cannot see yaw. The same flaw caused the
  replication-seed escape. Fix (W4 branch): re-centre yaw whenever C changed it;
  the general fix is to check every tolerance in VERIFY regardless of what the
  camera claims.
- **Worst case: 44 retry-limit aborts.** C sizes its search prior from the
  characterized accuracy. Told 0.5 mm with a true 1.0 mm error and a 0.2 mm
  clearance, the localizer runs out of attempts. The spiral search does not
  depend on a prior and keeps going.
- **Hand-eye bias: 3 retry-limit aborts.** Same mechanism, milder.

What holds: with outliers C is perfect (as are D and F); with the worst
mis-characterization (true 2.0 mm) C is still clearly ahead (54 against 36).
