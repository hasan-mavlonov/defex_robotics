# Rig test: sample size and power

Made by `python -m experiments.v02f_rig_power > hardware/RIG_POWER.md` from the per-trial rows of `results/benchmark_v0.2d` (seed 20261123), `benchmark_v0.2d_rep` (20261124) and `benchmark_v0.2e` (20261130). Simulation rates; a rig's rates will differ.

**Test.** Exact two-sided McNemar at 0.05 on paired trials, as in the benchmarks. **Power** is computed exactly from the two discordant-pair rates: p(C only) and p(other only) per paired trial. **n** is the number of paired good-part trials (per controller) for 80% power, from the rates pooled over the three seeds; the last column uses each seed's own rates (seeds 20261123, 20261124, 20261130, in that order). "no difference": the pooled rates are equal, so no n is enough. The rig rows are the benchmark trials of the protocol's conditions only (housing-only: nominal, lateral_3mm, noise_1mm, noise_2mm; Micro-Fit: mf_nominal, mf_moderate, mf_noise_1mm); per condition, divide n by 4 or 3.

## Success, C against I, J and F

| Machine | Suite | C vs | Pairs (3 seeds) | Success C / other | p(C only) / p(other only) | Power at 100 pairs | n for 80% power | n per seed |
|---|---|---|---|---|---|---|---|---|
| gantry | standard | I | 6,000 | 99.2% / 96.5% | 2.92% / 0.22% | 0.06 | 350 | 290, 300, 490 |
| gantry | standard | J | 6,000 | 99.2% / 98.0% | 1.57% / 0.33% | 0.00 | 1,030 | 1,090, 720, 1,470 |
| gantry | standard | F | 6,000 | 99.2% / 96.5% | 2.92% / 0.22% | 0.06 | 350 | 290, 300, 490 |
| gantry | latching | I | 1,800 | 96.8% / 98.4% | 1.06% / 2.67% | 0.02 | 1,200 | 1,420, 690, 2,140 |
| gantry | latching | J | 1,800 | 96.8% / 98.4% | 1.06% / 2.67% | 0.02 | 1,200 | 1,420, 690, 2,140 |
| gantry | latching | F | 1,800 | 96.8% / 98.8% | 0.78% / 2.72% | 0.03 | 780 | 700, 510, 1,560 |
| gantry | heldout | I | 1,500 | 85.4% / 84.5% | 10.27% / 9.33% | 0.03 | 17,870 | 920, 13,850, 3,020 |
| gantry | heldout | J | 1,500 | 85.4% / 89.5% | 6.80% / 10.93% | 0.11 | 860 | 4,130, 1,250, 320 |
| gantry | heldout | F | 1,500 | 85.4% / 84.5% | 10.27% / 9.33% | 0.03 | 17,870 | 920, 13,850, 3,020 |
| gantry | latch_spread | I | 1,800 | 100.0% / 99.9% | 0.06% / 0.00% | 0.00 | 14,230 | 4,750, no difference, no difference |
| gantry | latch_spread | J | 1,800 | 100.0% / 100.0% | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | latch_spread | F | 1,800 | 100.0% / 99.0% | 1.00% / 0.00% | 0.00 | 790 | 950, 680, 790 |
| gantry | rig housing-only | I | 1,200 | 96.3% / 83.7% | 13.50% / 0.83% | 0.95 | 70 | 70, 60, 110 |
| gantry | rig housing-only | J | 1,200 | 96.3% / 91.7% | 6.08% / 1.42% | 0.26 | 290 | 500, 140, 410 |
| gantry | rig housing-only | F | 1,200 | 96.3% / 83.7% | 13.50% / 0.83% | 0.95 | 70 | 70, 60, 110 |
| gantry | rig Micro-Fit | I | 1,800 | 96.8% / 98.4% | 1.06% / 2.67% | 0.02 | 1,200 | 1,420, 690, 2,140 |
| gantry | rig Micro-Fit | J | 1,800 | 96.8% / 98.4% | 1.06% / 2.67% | 0.02 | 1,200 | 1,420, 690, 2,140 |
| gantry | rig Micro-Fit | F | 1,800 | 96.8% / 98.8% | 0.78% / 2.72% | 0.03 | 780 | 700, 510, 1,560 |
| arm | standard | I | 6,000 | 98.0% / 96.2% | 2.60% / 0.73% | 0.02 | 810 | 1,000, 640, 820 |
| arm | standard | J | 6,000 | 98.0% / 96.8% | 1.97% / 0.77% | 0.01 | 1,580 | 3,160, 1,080, 1,360 |
| arm | standard | F | 6,000 | 98.0% / 96.2% | 2.60% / 0.73% | 0.02 | 810 | 1,000, 640, 820 |
| arm | latching | I | 1,800 | 93.3% / 94.0% | 3.44% / 4.11% | 0.02 | 13,620 | 5,410, no difference, 870 |
| arm | latching | J | 1,800 | 93.3% / 94.2% | 3.33% / 4.17% | 0.02 | 8,690 | 5,410, 184,840, 700 |
| arm | latching | F | 1,800 | 93.3% / 94.2% | 3.39% / 4.28% | 0.02 | 7,820 | 12,640, 194,260, 760 |
| arm | heldout | I | 1,500 | 78.3% / 79.9% | 9.67% / 11.33% | 0.04 | 6,050 | 100,570, 1,820, 6,990 |
| arm | heldout | J | 1,500 | 78.3% / 77.9% | 8.27% / 7.87% | 0.03 | 79,640 | 8,880, 12,280, 13,540 |
| arm | heldout | F | 1,500 | 78.3% / 79.9% | 9.67% / 11.33% | 0.04 | 6,050 | 100,570, 1,820, 6,990 |
| arm | latch_spread | I | 1,800 | 99.7% / 99.8% | 0.11% / 0.17% | 0.00 | 73,550 | 2,380, 4,750, 2,380 |
| arm | latch_spread | J | 1,800 | 99.7% / 99.8% | 0.11% / 0.22% | 0.00 | 22,410 | 2,380, 4,750, 1,580 |
| arm | latch_spread | F | 1,800 | 99.7% / 94.6% | 5.33% / 0.17% | 0.40 | 170 | 150, 170, 180 |
| arm | rig housing-only | I | 1,200 | 92.8% / 82.6% | 11.58% / 1.33% | 0.81 | 100 | 100, 90, 120 |
| arm | rig housing-only | J | 1,200 | 92.8% / 85.8% | 8.58% / 1.50% | 0.52 | 170 | 190, 130, 190 |
| arm | rig housing-only | F | 1,200 | 92.8% / 82.6% | 11.58% / 1.33% | 0.81 | 100 | 100, 90, 120 |
| arm | rig Micro-Fit | I | 1,800 | 93.3% / 94.0% | 3.44% / 4.11% | 0.02 | 13,620 | 5,410, no difference, 870 |
| arm | rig Micro-Fit | J | 1,800 | 93.3% / 94.2% | 3.33% / 4.17% | 0.02 | 8,690 | 5,410, 184,840, 700 |
| arm | rig Micro-Fit | F | 1,800 | 93.3% / 94.2% | 3.39% / 4.28% | 0.02 | 7,820 | 12,640, 194,260, 760 |

## Bad units passed on good-part trials, C against I, J and F

| Machine | Suite | C vs | Pairs (3 seeds) | Bad units C / other | p(C only) / p(other only) | Power at 100 pairs | n for 80% power | n per seed |
|---|---|---|---|---|---|---|---|---|
| gantry | standard | I | 6,000 | 0 / 119 | 0.00% / 1.98% | 0.01 | 400 | 330, 410, 500 |
| gantry | standard | J | 6,000 | 0 / 2 | 0.00% / 0.03% | 0.00 | 23,720 | 15,820, 15,820, no difference |
| gantry | standard | F | 6,000 | 0 / 119 | 0.00% / 1.98% | 0.01 | 400 | 330, 410, 500 |
| gantry | latching | I | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | latching | J | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | latching | F | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | heldout | I | 1,500 | 0 / 107 | 0.00% / 7.13% | 0.73 | 110 | 100, 130, 110 |
| gantry | heldout | J | 1,500 | 0 / 4 | 0.00% / 0.27% | 0.00 | 2,970 | 1,980, 3,960, 3,960 |
| gantry | heldout | F | 1,500 | 0 / 107 | 0.00% / 7.13% | 0.73 | 110 | 100, 130, 110 |
| gantry | latch_spread | I | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | latch_spread | J | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | latch_spread | F | 1,800 | 0 / 18 | 0.00% / 1.00% | 0.00 | 790 | 950, 680, 790 |
| gantry | rig housing-only | I | 1,200 | 0 / 107 | 0.00% / 8.92% | 0.89 | 90 | 80, 90, 110 |
| gantry | rig housing-only | J | 1,200 | 0 / 1 | 0.00% / 0.08% | 0.00 | 9,490 | no difference, 3,170, no difference |
| gantry | rig housing-only | F | 1,200 | 0 / 107 | 0.00% / 8.92% | 0.89 | 90 | 80, 90, 110 |
| gantry | rig Micro-Fit | I | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | rig Micro-Fit | J | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| gantry | rig Micro-Fit | F | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| arm | standard | I | 6,000 | 0 / 114 | 0.00% / 1.90% | 0.01 | 420 | 370, 410, 500 |
| arm | standard | J | 6,000 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| arm | standard | F | 6,000 | 0 / 114 | 0.00% / 1.90% | 0.01 | 420 | 370, 410, 500 |
| arm | latching | I | 1,800 | 0 / 4 | 0.00% / 0.22% | 0.00 | 3,560 | no difference, 4,750, 1,580 |
| arm | latching | J | 1,800 | 0 / 1 | 0.00% / 0.06% | 0.00 | 14,230 | no difference, no difference, 4,750 |
| arm | latching | F | 1,800 | 0 / 4 | 0.00% / 0.22% | 0.00 | 3,560 | no difference, 4,750, 1,580 |
| arm | heldout | I | 1,500 | 0 / 93 | 0.00% / 6.20% | 0.59 | 130 | 130, 140, 120 |
| arm | heldout | J | 1,500 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| arm | heldout | F | 1,500 | 0 / 93 | 0.00% / 6.20% | 0.59 | 130 | 130, 140, 120 |
| arm | latch_spread | I | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| arm | latch_spread | J | 1,800 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| arm | latch_spread | F | 1,800 | 0 / 96 | 0.00% / 5.33% | 0.44 | 150 | 160, 160, 140 |
| arm | rig housing-only | I | 1,200 | 0 / 101 | 0.00% / 8.42% | 0.86 | 100 | 90, 90, 120 |
| arm | rig housing-only | J | 1,200 | 0 / 0 | 0.00% / 0.00% | 0.00 | no difference | no difference, no difference, no difference |
| arm | rig housing-only | F | 1,200 | 0 / 101 | 0.00% / 8.42% | 0.86 | 100 | 90, 90, 120 |
| arm | rig Micro-Fit | I | 1,800 | 0 / 4 | 0.00% / 0.22% | 0.00 | 3,560 | no difference, 4,750, 1,580 |
| arm | rig Micro-Fit | J | 1,800 | 0 / 1 | 0.00% / 0.06% | 0.00 | 14,230 | no difference, no difference, 4,750 |
| arm | rig Micro-Fit | F | 1,800 | 0 / 4 | 0.00% / 0.22% | 0.00 | 3,560 | no difference, 4,750, 1,580 |

## Zero bad units: the Wilson 95% upper bound reachable at each n

If a controller passes 0 bad units in n trials, the Wilson 95% upper bound on its rate is z^2 / (n + z^2).

| n | 50 | 100 | 200 | 300 | 500 | 1,000 | 2,000 | 3,000 | 5,000 | 10,000 |
|---|---|---|---|---|---|---|---|---|---|---|
| Upper bound for 0/n | 7.14% | 3.70% | 1.88% | 1.26% | 0.76% | 0.38% | 0.19% | 0.13% | 0.08% | 0.04% |

n needed before 0/n has an upper bound below the other controller's pooled bad-unit rate (one-sample view; the paired test above is the pre-registered one):

| Machine | Suite | Other | Other's bad-unit rate (3 seeds) | n for 0/n upper bound below it |
|---|---|---|---|---|
| gantry | standard | I | 119 / 6,000 = 1.98% | 190 |
| gantry | standard | J | 2 / 6,000 = 0.03% | 11,521 |
| gantry | standard | F | 119 / 6,000 = 1.98% | 190 |
| gantry | latching | I | 0 / 1,800 | not defined |
| gantry | latching | J | 0 / 1,800 | not defined |
| gantry | latching | F | 0 / 1,800 | not defined |
| gantry | heldout | I | 107 / 1,500 = 7.13% | 51 |
| gantry | heldout | J | 4 / 1,500 = 0.27% | 1,437 |
| gantry | heldout | F | 107 / 1,500 = 7.13% | 51 |
| gantry | latch_spread | I | 0 / 1,800 | not defined |
| gantry | latch_spread | J | 0 / 1,800 | not defined |
| gantry | latch_spread | F | 18 / 1,800 = 1.00% | 381 |
| gantry | rig housing-only | I | 107 / 1,200 = 8.92% | 40 |
| gantry | rig housing-only | J | 1 / 1,200 = 0.08% | 4,607 |
| gantry | rig housing-only | F | 107 / 1,200 = 8.92% | 40 |
| gantry | rig Micro-Fit | I | 0 / 1,800 | not defined |
| gantry | rig Micro-Fit | J | 0 / 1,800 | not defined |
| gantry | rig Micro-Fit | F | 0 / 1,800 | not defined |
| arm | standard | I | 114 / 6,000 = 1.90% | 199 |
| arm | standard | J | 0 / 6,000 | not defined |
| arm | standard | F | 114 / 6,000 = 1.90% | 199 |
| arm | latching | I | 4 / 1,800 = 0.22% | 1,725 |
| arm | latching | J | 1 / 1,800 = 0.06% | 6,912 |
| arm | latching | F | 4 / 1,800 = 0.22% | 1,725 |
| arm | heldout | I | 93 / 1,500 = 6.20% | 59 |
| arm | heldout | J | 0 / 1,500 | not defined |
| arm | heldout | F | 93 / 1,500 = 6.20% | 59 |
| arm | latch_spread | I | 0 / 1,800 | not defined |
| arm | latch_spread | J | 0 / 1,800 | not defined |
| arm | latch_spread | F | 96 / 1,800 = 5.33% | 69 |
| arm | rig housing-only | I | 101 / 1,200 = 8.42% | 42 |
| arm | rig housing-only | J | 0 / 1,200 | not defined |
| arm | rig housing-only | F | 101 / 1,200 = 8.42% | 42 |
| arm | rig Micro-Fit | I | 4 / 1,800 = 0.22% | 1,725 |
| arm | rig Micro-Fit | J | 1 / 1,800 = 0.06% | 6,912 |
| arm | rig Micro-Fit | F | 4 / 1,800 = 0.22% | 1,725 |

## Where the bad units are (all three seeds, good-part trials)

Full depth: housing-only >= 14.5 mm of 15 mm, Micro-Fit >= 7.5 mm of 8 mm. The pass limits are abs(tilt) and abs(yaw) <= 3 deg, so a pose measurement for the rig has to resolve a few tenths of a degree around 3 deg at full depth.

| Ctrl | Part | Bad units | At full depth | Of those, tilt > 3 deg | yaw > 3 deg | neither | max of abs(tilt), abs(yaw) at full depth: median, 95th pct, max (deg) |
|---|---|---|---|---|---|---|---|
| F | housing-only | 433 | 392 | 151 | 242 | 0 | 3.45, 4.54, 5.02 |
| F | Micro-Fit | 118 | 4 | 4 | 0 | 0 | 3.07, 3.20, 3.23 |
| H | housing-only | 331 | 258 | 85 | 173 | 0 | 3.36, 4.25, 4.75 |
| H | Micro-Fit | 0 | | | | | |
| I | housing-only | 433 | 392 | 151 | 242 | 0 | 3.45, 4.54, 5.02 |
| I | Micro-Fit | 4 | 4 | 4 | 0 | 0 | 3.07, 3.20, 3.22 |
| J | housing-only | 6 | 5 | 0 | 1 | 4 | 0.23, 2.94, 3.61 |
| J | Micro-Fit | 1 | 1 | 1 | 0 | 0 | 3.10, 3.10, 3.10 |
| C | housing-only | 0 | | | | | |
| C | Micro-Fit | 0 | | | | | |
