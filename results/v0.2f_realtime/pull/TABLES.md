# v0.2f pull overshoot tables

Development measurement, seeds 2026 and 2027, made by `python -m experiments.v02f_pull_overshoot --tables results/v0.2f_realtime/pull` from the episodes.csv files in this folder (model runs only, counterfactual runs excluded).
Peak = most negative tared, filtered axial F/T force from the pull start to 0.1 s after the guard ends the pull, sign flipped. Hook = the simulator's latch-hook force (2 kHz). Retention and latch break threshold: 58 N.

## Pulls per machine and controller

| machine | ctrl | trials | pulls | held (guard tripped on force) | target N | peak/target p50 | p99 | max | > 1.10 | > 1.25 | max peak N | max hook N (window) | hook > 58 N | max meas. abs(F) N | abs(F) > 48 N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry | C | 640 | 799 | 357 | 35.2 | 0.842 | 1.051 | 1.063 | 0 | 0 | 37.4 | 40.9 | 0 | 37.5 | 0 |
| gantry | G | 640 | 801 | 360 | 35.2 | 0.842 | 1.051 | 1.070 | 0 | 0 | 37.7 | 40.8 | 0 | 37.7 | 0 |
| gantry | H | 640 | 690 | 345 | 35.2 | 0.973 | 1.056 | 1.070 | 0 | 0 | 37.7 | 41.0 | 0 | 37.7 | 0 |
| gantry | I | 640 | 758 | 358 | 35.2 | 0.836 | 1.056 | 1.085 | 0 | 0 | 38.2 | 41.3 | 0 | 39.6 | 0 |
| gantry | J | 640 | 740 | 358 | 35.2 | 0.881 | 1.064 | 1.109 | 1 | 0 | 39.1 | 41.9 | 0 | 39.1 | 0 |
| arm | C | 640 | 860 | 349 | 35.2 | 0.845 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 | 0 |
| arm | G | 640 | 867 | 356 | 35.2 | 0.858 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 | 0 |
| arm | H | 640 | 731 | 340 | 35.2 | 0.866 | 1.001 | 1.204 | 1 | 0 | 42.4 | 25.6 | 0 | 42.4 | 0 |
| arm | I | 640 | 780 | 354 | 35.2 | 0.837 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 | 0 |
| arm | J | 640 | 753 | 354 | 35.2 | 0.851 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.6 | 0 | 35.2 | 0 |

## Pulls over 1.10 x target

| machine | suite | seed | condition | ctrl | trial | pull | target N | trip N | peak N | ratio | hook N | held | after | outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm | latching | 2026 | mf_noise_1mm | H | 7 | 0 | 35.2 | -35.074 | 42.362 | 1.204 | 0.0 | False | repush | aborted:excess_torque |
| gantry | latch_spread | 2027 | mf_spread | J | 6 | 0 | 35.2 | -35.814 | 39.052 | 1.109 | 40.992 | True | release | none |

## Latch breaks (whole trial)

| machine | ctrl | trials with a broken latch | in a pull window | where (state/phase) | max hook N in trial |
|---|---|---|---|---|---|
| gantry | C | 0 | 0 |  | 40.9 |
| gantry | G | 0 | 0 |  | 40.8 |
| gantry | H | 2 | 0 | APPROACH/: 2 | 59.1 |
| gantry | I | 0 | 0 |  | 41.3 |
| gantry | J | 0 | 0 |  | 41.9 |
| arm | C | 0 | 0 |  | 28.9 |
| arm | G | 0 | 0 |  | 27.2 |
| arm | H | 0 | 0 |  | 25.6 |
| arm | I | 0 | 0 |  | 25.6 |
| arm | J | 0 | 0 |  | 25.6 |

## Good parts: guard-tripped pulls by trial outcome

| machine | ctrl | held pulls on good parts | of those, trial not seated | not-seated with latch broken |
|---|---|---|---|---|
| gantry | C | 357 | 0 | 0 |
| gantry | G | 360 | 0 | 0 |
| gantry | H | 345 | 0 | 0 |
| gantry | I | 358 | 0 | 0 |
| gantry | J | 358 | 0 | 0 |
| arm | C | 349 | 1 | 0 |
| arm | G | 356 | 1 | 0 |
| arm | H | 340 | 1 | 0 |
| arm | I | 354 | 0 | 0 |
| arm | J | 354 | 0 | 0 |
