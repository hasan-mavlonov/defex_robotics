# benchmark_v0.2a: pre-registered metrics missing from the first report

Found in review: the pre-registration listed p95 peak wrist torque and false
rejects, which the first report did not give. Computed from `trials.csv`:

| Controller | p95 peak measured wrist torque (N m) | max (N m) | false rejects |
|---|---|---|---|
| fixed | 0.223 | 0.470 | 0 |
| correction | 0.200 | 0.597 | 0 |
| correction_rcc | 0.187 | 0.353 | 0 |
| spiral | 0.063 | 0.249 | 0 |
| spiral_rcc | 0.038 | 0.289 | 0 |
| adaptive | 0.090 | 0.213 | 0 |
