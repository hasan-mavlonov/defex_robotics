# W6: cycle time (development measurements, seed 2026)

Where C's time goes on a clean insertion (W4 code, yaw centring always on):
approach 1.5 s (same transit as every controller), insert 2.4 s, verify 2.7 s.

Speed profiles, 6 conditions (nominal, lateral_3mm, noise_1mm, noise_2mm,
friction_1, tilt_10deg) x 30 trials:

| Profile | Changes from V0.1 | Success | Bad units | Median | p95 | p95 peak force |
|---|---|---|---|---|---|---|
| S0 | none | 179/180 | 0 | 6.90 s | 11.83 s | 8.5 N |
| S6 | yaw probe 25 deg/s, near-floor 10 mm/s | 179/180 | 0 | 6.14 s | 11.22 s | 10.8 N |
| S5 | S6 + insert 10 mm/s, wall probe 3.5 mm/s | 179/180 | 0 | 5.50 s | 9.94 s | 12.7 N |
| **S2 (W6 default)** | S6 + insert 10 mm/s, wall probe 5 mm/s | 179/180 | 0 | **5.35 s** | **9.84 s** | 12.7 N |
| S3 | S2 + shorter seat conform and preload | 177/180 | 2 | 5.34 s | 9.29 s | 12.7 N (rejected: bad units) |

Floor impact speed drives the extra force: faster cycles cost contact force.

The brief's tail target, p95 at most 1.5 x median, is not met (S2: 1.84 x).
The tail is recoveries: each costs 3-4 s (retract, re-align, tare, re-insert).
Shorter recoveries need a faster tare and re-approach, or fewer recoveries
(better first probe), which W4's joint localizer did not deliver.

For comparison, benchmark_v0.2a's spiral + RCC cell (F): median 3.54 s,
p95 5.12 s, p95 force 6.2 N. C does not match it on speed or force with any of
these profiles; its case is success under poor vision and verification.
