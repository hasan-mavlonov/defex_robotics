# v0.2g draft pre-registrations: discordance rates and power

Made by `PYTHONPATH=. python results/v0.2g_prereg_drafts/power_v02g.py > results/v0.2g_prereg_drafts/POWER.md` from committed trials.csv only: benchmark_v0.2d (seed 20261123), benchmark_v0.2d_rep (20261124), benchmark_v0.2e (20261130) and heldout2_v0.2f (20261207). Simulation rates. Test: exact two-sided McNemar at 0.05 on paired trials. Power is exact, from the two discordant-pair rates (`experiments/v02f_rig_power.py`). 'n for 80%' is paired trials in the cell, rounded up to 10.

Scenario rates are assumptions, not data. f = the fraction of the fixable trials that a change fixes. 'Fixable' = trials where C fails and the named reference controller seats, on the same trial. h = a harm rate: trials the change newly loses, per paired trial.

## (1) Observed discordance in the cells each C fix targets

| Fix | Cell (source, seed) | C vs | Pairs | C-only / other-only | C-only / other-only rate | C failures |
|---|---|---|---|---|---|---|
| 1 depth hold | arm heldout2 ft_drift (20261207) | D | 80 | 0 / 19 | 0.00% / 23.75% | 19 |
| 1 depth hold | arm heldout2 ft_drift, bad units (20261207) | D | 80 | 8 / 0 | 10.00% / 0.00% | - |
| 3 jam progress | gantry heldout2 grasp (20261207) | F | 80 | 0 / 19 | 0.00% / 23.75% | 20 |
| 3 jam progress | arm heldout2 grasp (20261207) | F | 80 | 2 / 17 | 2.50% / 21.25% | 19 |
| 2 wall signature | arm standard friction_1 (3 seeds: 0/7, 0/6, 0/5) | I | 300 | 0 / 18 | 0.00% / 6.00% | 18 |
| 2 wall signature | arm standard friction_0.6 (3 seeds: 0/0, 0/0, 0/0) | I | 300 | 0 / 0 | 0.00% / 0.00% | 0 |
| 3 jam progress (secondary) | gantry heldout heldout_mischar_2mm (3 seeds) | J | 300 | 56 / 39 | 18.67% / 13.00% | 71 |
| 3 jam progress (secondary) | arm heldout heldout_mischar_2mm (3 seeds) | J | 300 | 74 / 25 | 24.67% / 8.33% | 114 |

Fix 4 (socket-axis reference) has no outcome cell: C passed 0 tilted bad units on every seed, and G's one (benchmark_v0.2e arm mf_noise_1mm trial 130) is about 1 in 600. Its effect endpoint is a measurement (tilt verdicts that read more than 1 deg under the true tilt: 234 of 8,320 on the development seeds, `results/v0.2f_tilt_diagnosis/REPORT.md` item 1), not a McNemar test.

## (2) Power of C2 against C in each target cell (scenarios)

p(C2-only) = f x fixable rate; p(C-only) = h. Fixable rate from table (1): the other-only rate.

| Cell | Fixable rate | f | h | n for 80% | power at the planned n | the same at alpha 0.0125 (Holm, 4 tests) |
|---|---|---|---|---|---|---|
| arm heldout2 ft_drift, success vs D-fixable | 23.75% | 1.0 | 0.0% | 40 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, success vs D-fixable | 23.75% | 1.0 | 0.5% | 40 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, success vs D-fixable | 23.75% | 0.75 | 0.0% | 50 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, success vs D-fixable | 23.75% | 0.75 | 0.5% | 50 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, success vs D-fixable | 23.75% | 0.5 | 0.0% | 70 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, success vs D-fixable | 23.75% | 0.5 | 0.5% | 80 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, bad units (C's own) | 10.00% | 1.0 | 0.0% | 80 | 1.00 at 200 | 1.00 |
| arm heldout2 ft_drift, bad units (C's own) | 10.00% | 1.0 | 0.5% | 100 | 1.00 at 200 | 0.98 |
| arm heldout2 ft_drift, bad units (C's own) | 10.00% | 0.75 | 0.0% | 110 | 1.00 at 200 | 0.99 |
| arm heldout2 ft_drift, bad units (C's own) | 10.00% | 0.75 | 0.5% | 130 | 0.96 at 200 | 0.88 |
| arm heldout2 ft_drift, bad units (C's own) | 10.00% | 0.5 | 0.0% | 160 | 0.94 at 200 | 0.79 |
| arm heldout2 ft_drift, bad units (C's own) | 10.00% | 0.5 | 0.5% | 220 | 0.75 at 200 | 0.53 |
| gantry heldout2 grasp, success vs F-fixable | 23.75% | 1.0 | 0.0% | 40 | 1.00 at 200 | 1.00 |
| gantry heldout2 grasp, success vs F-fixable | 23.75% | 1.0 | 0.5% | 40 | 1.00 at 200 | 1.00 |
| gantry heldout2 grasp, success vs F-fixable | 23.75% | 0.75 | 0.0% | 50 | 1.00 at 200 | 1.00 |
| gantry heldout2 grasp, success vs F-fixable | 23.75% | 0.75 | 0.5% | 50 | 1.00 at 200 | 1.00 |
| gantry heldout2 grasp, success vs F-fixable | 23.75% | 0.5 | 0.0% | 70 | 1.00 at 200 | 1.00 |
| gantry heldout2 grasp, success vs F-fixable | 23.75% | 0.5 | 0.5% | 80 | 1.00 at 200 | 1.00 |
| arm heldout2 grasp, success vs F-fixable | 21.25% | 1.0 | 0.0% | 40 | 1.00 at 200 | 1.00 |
| arm heldout2 grasp, success vs F-fixable | 21.25% | 1.0 | 0.5% | 40 | 1.00 at 200 | 1.00 |
| arm heldout2 grasp, success vs F-fixable | 21.25% | 0.75 | 0.0% | 50 | 1.00 at 200 | 1.00 |
| arm heldout2 grasp, success vs F-fixable | 21.25% | 0.75 | 0.5% | 60 | 1.00 at 200 | 1.00 |
| arm heldout2 grasp, success vs F-fixable | 21.25% | 0.5 | 0.0% | 80 | 1.00 at 200 | 1.00 |
| arm heldout2 grasp, success vs F-fixable | 21.25% | 0.5 | 0.5% | 90 | 1.00 at 200 | 0.99 |
| arm standard friction_1, success vs I-fixable | 6.00% | 1.0 | 0.0% | 140 | 1.00 at 400 | 1.00 |
| arm standard friction_1, success vs I-fixable | 6.00% | 1.0 | 0.5% | 180 | 1.00 at 400 | 0.99 |
| arm standard friction_1, success vs I-fixable | 6.00% | 0.75 | 0.0% | 180 | 1.00 at 400 | 1.00 |
| arm standard friction_1, success vs I-fixable | 6.00% | 0.75 | 0.5% | 260 | 0.96 at 400 | 0.88 |
| arm standard friction_1, success vs I-fixable | 6.00% | 0.5 | 0.0% | 270 | 0.98 at 400 | 0.91 |
| arm standard friction_1, success vs I-fixable | 6.00% | 0.5 | 0.5% | 460 | 0.73 at 400 | 0.50 |

The heldout2 rates are from one seed, 80 pairs per family. The friction rates pool three seeds, 300 pairs per condition.

## (3) Harm detection: C2 against C on a whole cell

p(C-only) = h (trials C2 newly loses), p(C2-only) = g (trials it newly wins elsewhere in the cell).

| Pairs in the cell | h | g | power to see C2 below C |
|---|---|---|---|
| 600 | 0.25% | 0.00% | 0.00 |
| 600 | 0.50% | 0.00% | 0.08 |
| 600 | 1.00% | 0.00% | 0.56 |
| 600 | 1.00% | 0.50% | 0.09 |
| 900 | 0.25% | 0.00% | 0.03 |
| 900 | 0.50% | 0.00% | 0.30 |
| 900 | 1.00% | 0.00% | 0.89 |
| 900 | 1.00% | 0.50% | 0.16 |
| 1,000 | 0.25% | 0.00% | 0.04 |
| 1,000 | 0.50% | 0.00% | 0.38 |
| 1,000 | 1.00% | 0.00% | 0.93 |
| 1,000 | 1.00% | 0.50% | 0.18 |
| 2,000 | 0.25% | 0.00% | 0.38 |
| 2,000 | 0.50% | 0.00% | 0.93 |
| 2,000 | 1.00% | 0.00% | 1.00 |
| 2,000 | 1.00% | 0.50% | 0.37 |

Zero bad units in n trials has a Wilson 95% upper bound of 3.84 / (n + 3.84): 1.9% at 200, 0.64% at 600, 0.19% at 2,000.

## (4) Seat-and-align scenarios: C against K (I plus a seat-and-align step; K2 = F plus the same step)

Scenario: K turns a fraction f of I's bad units (declared, not seated) into seated parts and changes nothing else. Then C-only(K) = C-only(I) minus f x (C-only trials where I passed a bad unit), and K-only = I-only plus f x (trials where both C and I failed and I passed a bad unit). Standard: the three benchmark seeds pooled, 6,000 pairs per machine. heldout2: seed 20261207, 80 pairs per family.

| Cell | Pairs | C-only / I-only (observed) | C-only where I bad unit | both fail, I bad unit | f | C-only / K-only rate | n for 80% | power at the planned n | the same at alpha 0.0125 |
|---|---|---|---|---|---|---|---|---|---|
| gantry standard (3 seeds) | 6,000 | 175 / 13 | 111 | 8 | 1.0 | 1.07% / 0.35% | 2,330 | 0.73 at 2,000 | 0.52 |
| gantry standard (3 seeds) | 6,000 | 175 / 13 | 111 | 8 | 0.5 | 1.99% / 0.28% | 640 | 1.00 at 2,000 | 1.00 |
| gantry heldout2 tilt | 80 | 7 / 0 | 7 | 0 | 1.0 | 0.00% / 0.00% | no difference | 0.00 at 200 | 0.00 |
| gantry heldout2 tilt | 80 | 7 / 0 | 7 | 0 | 0.5 | 4.38% / 0.00% | 180 | 0.87 at 200 | 0.65 |
| gantry heldout2 yaw | 80 | 50 / 0 | 50 | 0 | 1.0 | 0.00% / 0.00% | no difference | 0.00 at 200 | 0.00 |
| gantry heldout2 yaw | 80 | 50 / 0 | 50 | 0 | 0.5 | 31.25% / 0.00% | 30 | 1.00 at 200 | 1.00 |
| arm standard (3 seeds) | 6,000 | 156 / 44 | 95 | 19 | 1.0 | 1.02% / 1.05% | > 1,000,000 | 0.04 at 2,000 | 0.01 |
| arm standard (3 seeds) | 6,000 | 156 / 44 | 95 | 19 | 0.5 | 1.81% / 0.89% | 2,670 | 0.67 at 2,000 | 0.45 |
| arm heldout2 tilt | 80 | 12 / 0 | 12 | 0 | 1.0 | 0.00% / 0.00% | no difference | 0.00 at 200 | 0.00 |
| arm heldout2 tilt | 80 | 12 / 0 | 12 | 0 | 0.5 | 7.50% / 0.00% | 110 | 1.00 at 200 | 0.99 |
| arm heldout2 yaw | 80 | 48 / 0 | 48 | 1 | 1.0 | 0.00% / 1.25% | 640 | 0.04 at 200 | 0.00 |
| arm heldout2 yaw | 80 | 48 / 0 | 48 | 1 | 0.5 | 30.00% / 0.62% | 30 | 1.00 at 200 | 1.00 |

K against I on bad units: p(I-only bad unit) = f x I's bad-unit rate, p(K-only) = 0.

| Cell | I bad-unit rate | f | n for 80% | power at the planned n | the same at alpha 0.0125 |
|---|---|---|---|---|---|
| gantry standard (3 seeds) | 1.98% | 1.0 | 400 | 1.00 at 2,000 | 1.00 |
| gantry standard (3 seeds) | 1.98% | 0.5 | 800 | 1.00 at 2,000 | 1.00 |
| gantry heldout2 tilt | 8.75% | 1.0 | 90 | 1.00 at 200 | 1.00 |
| gantry heldout2 tilt | 8.75% | 0.5 | 180 | 0.87 at 200 | 0.65 |
| gantry heldout2 yaw | 62.50% | 1.0 | 20 | 1.00 at 200 | 1.00 |
| gantry heldout2 yaw | 62.50% | 0.5 | 30 | 1.00 at 200 | 1.00 |
| arm standard (3 seeds) | 1.90% | 1.0 | 420 | 1.00 at 2,000 | 1.00 |
| arm standard (3 seeds) | 1.90% | 0.5 | 840 | 1.00 at 2,000 | 1.00 |
| arm heldout2 tilt | 15.00% | 1.0 | 60 | 1.00 at 200 | 1.00 |
| arm heldout2 tilt | 15.00% | 0.5 | 110 | 1.00 at 200 | 0.99 |
| arm heldout2 yaw | 61.25% | 1.0 | 20 | 1.00 at 200 | 1.00 |
| arm heldout2 yaw | 61.25% | 0.5 | 30 | 1.00 at 200 | 1.00 |

## (5) Gentle retract: torn good latches (development seeds, v0.2f code)

From `results/v0.2f_baseline_retract_cap/dev/*/trials.csv`, uncapped controllers only (the v0.2e behaviour), seeds 2026 and 2027, 20 trials per condition. The benchmarks before v0.2f do not log `final_latch_intact`.

| Machine | Suite | Ctrl | Good-part trials | Torn on good parts | Rate | f | n for 80% (gentle vs uncapped) | power at 600 | power at 1,200 | power at 1,200, alpha 0.0125 |
|---|---|---|---|---|---|---|---|---|---|---|
| gantry | latching | D | 120 | 2 | 1.67% | 1.0 | 480 | 0.93 | 1.00 | 1.00 |
| gantry | latching | D | 120 | 2 | 1.67% | 0.5 | 950 | 0.38 | 0.93 | 0.78 |
| gantry | latching | F | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latching | H | 120 | 2 | 1.67% | 1.0 | 480 | 0.93 | 1.00 | 1.00 |
| gantry | latching | H | 120 | 2 | 1.67% | 0.5 | 950 | 0.38 | 0.93 | 0.78 |
| gantry | latching | I | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latching | J | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latch_spread | D | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latch_spread | F | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latch_spread | H | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latch_spread | I | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| gantry | latch_spread | J | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latching | D | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latching | F | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latching | H | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latching | I | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latching | J | 120 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latch_spread | D | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latch_spread | F | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latch_spread | H | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latch_spread | I | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |
| arm | latch_spread | J | 240 | 0 | 0.00% | 1.0 | no difference | 0.00 | 0.00 | 0.00 |

600 = latching 3 good conditions x 200 trials (as v0.2e), or latch_spread 6 good conditions x 100; 1,200 = latching at 400 trials per condition. D's and H's tears were the same two gantry `mf_noise_1mm` trials, seed 2027 trials 17 and 19 (`results/v0.2f_baseline_retract_cap/REPORT.md`).

## (6) CPU seconds per trial (mean `wall_time_s`), per run and controller

Load differed between runs; benchmark_v0.2e ran at --workers 9 on a quiet machine, heldout2 at --workers 2 at load 40-50. Sum of `wall_time_s` / workers matched both runs' wall time to within about 10%.

| Run folder | C | D | E | F | H | I | J |
|---|---|---|---|---|---|---|---|
| gantry_standard | 0.52 | 0.27 | 0.67 | 0.24 | 0.27 | 0.24 | 0.50 |
| gantry_latching | 1.13 | 0.70 | 0.90 | 0.75 | 1.06 | 1.24 | 1.20 |
| gantry_heldout | 0.77 | 0.46 | 0.54 | 0.50 | 0.45 | 0.47 | 0.68 |
| gantry_latch_spread | 0.97 | 0.39 | 0.94 | 0.32 | 0.83 | 0.83 | 0.80 |
| gantry_heldout2 | 0.99 | 0.57 | 1.06 | 0.44 | 0.70 | 0.65 | 0.89 |
| arm_standard | 0.90 | 0.47 | 0.35 | 0.52 | 0.47 | 0.52 | 0.91 |
| arm_latching | 1.82 | 0.89 | 0.44 | 1.23 | 1.34 | 1.82 | 1.81 |
| arm_heldout | 1.37 | 0.70 | 0.30 | 0.83 | 0.71 | 0.88 | 1.29 |
| arm_latch_spread | 1.84 | 0.67 | 0.50 | 0.72 | 1.37 | 1.53 | 1.59 |
| arm_heldout2 | 1.85 | 0.83 | 0.53 | 0.94 | 1.22 | 1.47 | 1.95 |

The benchmark folders appear three times (three seeds); the means pool them.
