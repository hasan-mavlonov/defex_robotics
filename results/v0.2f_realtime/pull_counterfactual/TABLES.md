# v0.2f pull overshoot tables

Development measurement, seeds 2026 and 2027, made by `python -m experiments.v02f_pull_overshoot --tables pull_counterfactual` from the episodes.csv files in this folder (counterfactual hook runs only: NOT the model).
Peak = most negative tared, filtered axial F/T force from the pull start to 0.1 s after the guard ends the pull, sign flipped. Hook = the simulator's latch-hook force (2 kHz). Retention and latch break threshold: 58 N.

## Pulls per machine and controller

| machine | ctrl | trials | pulls | held (guard tripped on force) | target N | peak/target p50 | p99 | max | > 1.10 | > 1.25 | max peak N | max hook N (window) | hook > 58 N | max meas. abs(F) N | abs(F) > 48 N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry (damping 300 N s/m) | C | 40 | 57 | 40 | 35.2 | 1.000 | 1.000 | 1.000 | 0 | 0 | 35.2 | 25.3 | 0 | 35.2 | 0 |
| gantry (damping 300 N s/m) | G | 40 | 57 | 40 | 35.2 | 1.000 | 1.000 | 1.000 | 0 | 0 | 35.2 | 25.3 | 0 | 35.2 | 0 |
| gantry (damping 300 N s/m) | H | 40 | 42 | 40 | 35.2 | 1.000 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.3 | 0 | 35.2 | 0 |
| gantry (damping 300 N s/m) | I | 40 | 48 | 40 | 35.2 | 1.000 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.2 | 0 | 35.2 | 0 |
| gantry (damping 300 N s/m) | J | 40 | 49 | 40 | 35.2 | 1.000 | 1.001 | 1.001 | 0 | 0 | 35.2 | 25.2 | 0 | 35.2 | 0 |
| gantry (stiffness 50000 N/m) | C | 40 | 64 | 33 | 35.2 | 1.000 | 1.102 | 1.103 | 5 | 0 | 38.8 | 25.2 | 0 | 38.8 | 0 |
| gantry (stiffness 50000 N/m) | G | 40 | 64 | 33 | 35.2 | 1.000 | 1.102 | 1.103 | 3 | 0 | 38.8 | 25.2 | 0 | 38.8 | 0 |
| gantry (stiffness 50000 N/m) | H | 40 | 49 | 33 | 35.2 | 1.000 | 1.276 | 1.291 | 6 | 2 | 45.4 | 28.0 | 0 | 45.4 | 0 |
| gantry (stiffness 50000 N/m) | I | 40 | 57 | 31 | 35.2 | 1.000 | 1.284 | 1.286 | 6 | 2 | 45.3 | 34.2 | 0 | 45.3 | 0 |
| gantry (stiffness 50000 N/m) | J | 40 | 58 | 31 | 35.2 | 1.000 | 1.103 | 1.103 | 2 | 0 | 38.8 | 28.4 | 0 | 38.8 | 0 |

## Pulls over 1.10 x target

| machine | suite | seed | condition | ctrl | trial | pull | target N | trip N | peak N | ratio | hook N | held | after | outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | H | 13 | 1 | 35.2 | -34.807 | 45.429 | 1.291 | 27.994 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | I | 19 | 1 | 35.2 | -34.876 | 45.251 | 1.286 | 34.177 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | I | 5 | 1 | 35.2 | -34.592 | 45.149 | 1.283 | 29.527 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | H | 2 | 1 | 35.2 | -33.315 | 44.361 | 1.260 | 27.383 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | I | 13 | 1 | 35.2 | -32.927 | 43.976 | 1.249 | 27.13 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | I | 2 | 1 | 35.2 | -31.785 | 43.201 | 1.227 | 26.721 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | H | 17 | 1 | 35.2 | -31.448 | 43.061 | 1.223 | 22.657 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | H | 11 | 1 | 35.2 | -30.935 | 42.457 | 1.206 | 28.022 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | H | 15 | 1 | 35.2 | -29.657 | 41.288 | 1.173 | 26.082 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | I | 17 | 1 | 35.2 | -29.354 | 40.928 | 1.163 | 21.401 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | H | 8 | 1 | 35.2 | -29.053 | 40.683 | 1.156 | 22.683 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | I | 11 | 1 | 35.2 | -28.165 | 39.609 | 1.125 | 26.145 | False | pull | protective_stop |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | C | 2 | 1 | 35.2 | -32.471 | 38.833 | 1.103 | 23.655 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | G | 2 | 1 | 35.2 | -32.471 | 38.833 | 1.103 | 23.655 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | J | 2 | 0 | 35.2 | -31.812 | 38.81 | 1.103 | 23.622 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | J | 2 | 1 | 35.2 | -31.809 | 38.809 | 1.103 | 23.638 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | C | 13 | 0 | 35.2 | -33.571 | 38.77 | 1.101 | 23.664 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | C | 13 | 1 | 35.2 | -33.567 | 38.77 | 1.101 | 23.649 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | C | 11 | 1 | 35.2 | -28.725 | 38.764 | 1.101 | 25.17 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | G | 11 | 1 | 35.2 | -28.725 | 38.764 | 1.101 | 25.17 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | C | 11 | 0 | 35.2 | -28.687 | 38.722 | 1.100 | 25.134 | False | retract | aborted:stuck_during_retract |
| gantry (stiffness 50000 N/m) | latch_spread | 2026 | mf_spread | G | 11 | 0 | 35.2 | -28.687 | 38.722 | 1.100 | 25.134 | False | retract | aborted:stuck_during_retract |

## Latch breaks (whole trial)

| machine | ctrl | trials with a broken latch | in a pull window | where (state/phase) | max hook N in trial |
|---|---|---|---|---|---|
| gantry (damping 300 N s/m) | C | 0 | 0 |  | 25.3 |
| gantry (damping 300 N s/m) | G | 0 | 0 |  | 25.3 |
| gantry (damping 300 N s/m) | H | 0 | 0 |  | 25.3 |
| gantry (damping 300 N s/m) | I | 0 | 0 |  | 25.2 |
| gantry (damping 300 N s/m) | J | 0 | 0 |  | 25.2 |
| gantry (stiffness 50000 N/m) | C | 0 | 0 |  | 25.8 |
| gantry (stiffness 50000 N/m) | G | 0 | 0 |  | 25.8 |
| gantry (stiffness 50000 N/m) | H | 0 | 0 |  | 32.9 |
| gantry (stiffness 50000 N/m) | I | 0 | 0 |  | 36.3 |
| gantry (stiffness 50000 N/m) | J | 0 | 0 |  | 28.4 |

## Good parts: guard-tripped pulls by trial outcome

| machine | ctrl | held pulls on good parts | of those, trial not seated | not-seated with latch broken |
|---|---|---|---|---|
| gantry (damping 300 N s/m) | C | 40 | 0 | 0 |
| gantry (damping 300 N s/m) | G | 40 | 0 | 0 |
| gantry (damping 300 N s/m) | H | 40 | 0 | 0 |
| gantry (damping 300 N s/m) | I | 40 | 0 | 0 |
| gantry (damping 300 N s/m) | J | 40 | 0 | 0 |
| gantry (stiffness 50000 N/m) | C | 33 | 0 | 0 |
| gantry (stiffness 50000 N/m) | G | 33 | 0 | 0 |
| gantry (stiffness 50000 N/m) | H | 33 | 0 | 0 |
| gantry (stiffness 50000 N/m) | I | 31 | 0 | 0 |
| gantry (stiffness 50000 N/m) | J | 31 | 0 | 0 |
