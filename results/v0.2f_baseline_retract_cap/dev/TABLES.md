# Retract cap, paired: results/v0.2f_baseline_retract_cap/dev

Made by `python -m experiments.v02f_retract_cap_compare results/v0.2f_baseline_retract_cap/dev`. u = the baseline with `retract_pull_cap` off (`bare name`), k = the same controller with it on (`@cap`), same trials. Good = good-part trials (success; bad units = escapes on good parts); bad = deliberately bad parts passed. Torn = `final_latch_intact` False, any trial. Tripped = trials with a `gentle_retract` event in k that u does not have (J's VERIFY logs C's own).

| machine | suite | ctrl | trials | tripped | good seated u -> k (gain/loss) | torn u -> k (new) | bad units u -> k (new) | bad parts u -> k (new) | stops u -> k | rows differing without a trip | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gantry | latch_spread | D | 360 | 0 | 234 -> 234 of 240 (+0/-0) | 0 -> 0 (0) | 5 -> 5 (0) | 95 -> 95 (0) | 15 -> 15 | 0 | pass |
| gantry | latch_spread | F | 360 | 0 | 237 -> 237 of 240 (+0/-0) | 0 -> 0 (0) | 3 -> 3 (0) | 91 -> 91 (0) | 24 -> 24 | 0 | pass |
| gantry | latch_spread | H | 360 | 0 | 239 -> 239 of 240 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 15 -> 15 | 0 | pass |
| gantry | latch_spread | I | 360 | 0 | 240 -> 240 of 240 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 24 -> 24 | 0 | pass |
| gantry | latch_spread | J | 360 | 0 | 240 -> 240 of 240 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 24 -> 24 | 0 | pass |
| gantry | latching | D | 280 | 3 | 106 -> 106 of 120 (+0/-0) | 2 -> 2 (1) | 1 -> 0 (0) | 75 -> 75 (0) | 9 -> 9 | 0 | FAIL: tears |
| gantry | latching | F | 280 | 0 | 118 -> 118 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 101 -> 101 (0) | 14 -> 14 | 0 | pass |
| gantry | latching | H | 280 | 3 | 106 -> 106 of 120 (+0/-0) | 2 -> 2 (1) | 0 -> 0 (0) | 0 -> 0 (0) | 9 -> 9 | 0 | FAIL: tears |
| gantry | latching | I | 280 | 0 | 118 -> 118 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 14 -> 14 | 0 | pass |
| gantry | latching | J | 280 | 0 | 118 -> 118 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 26 -> 26 | 0 | pass |
| arm | latch_spread | D | 360 | 0 | 223 -> 223 of 240 (+0/-0) | 0 -> 0 (0) | 17 -> 17 (0) | 110 -> 110 (0) | 0 -> 0 | 0 | pass |
| arm | latch_spread | F | 360 | 0 | 230 -> 230 of 240 (+0/-0) | 0 -> 0 (0) | 10 -> 10 (0) | 118 -> 118 (0) | 0 -> 0 | 0 | pass |
| arm | latch_spread | H | 360 | 0 | 238 -> 238 of 240 (+0/-0) | 0 -> 0 (0) | 1 -> 1 (0) | 0 -> 0 (0) | 0 -> 0 | 0 | pass |
| arm | latch_spread | I | 360 | 0 | 240 -> 240 of 240 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 | 0 | pass |
| arm | latch_spread | J | 360 | 0 | 240 -> 240 of 240 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 | 0 | pass |
| arm | latching | D | 280 | 1 | 101 -> 101 of 120 (+0/-0) | 0 -> 0 (0) | 3 -> 3 (0) | 75 -> 75 (0) | 1 -> 1 | 0 | pass |
| arm | latching | F | 280 | 0 | 114 -> 114 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 90 -> 90 (0) | 0 -> 0 | 0 | pass |
| arm | latching | H | 280 | 2 | 101 -> 101 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 1 -> 1 | 0 | pass |
| arm | latching | I | 280 | 0 | 114 -> 114 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 | 0 | pass |
| arm | latching | J | 280 | 0 | 114 -> 114 of 120 (+0/-0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 (0) | 0 -> 0 | 0 | pass |

Per controller over all cells: D FAIL, F pass, H FAIL, I pass, J pass
D, F, H and I all pass: False. J passes: True.

## Trials with a trip

| machine | suite | seed | condition | ctrl | trial | uncapped | capped | rows differ | first trip |
|---|---|---|---|---|---|---|---|---|---|
| arm | latching | 2026 | mf_noise_1mm | D | 6 | False/protective_stop/torn=False/stop=True | False/protective_stop/torn=False/stop=True | True | pull 36.7 N above 36.0 N: stop pulling, plug held at 2.05 mm |
| arm | latching | 2026 | mf_noise_1mm | H | 6 | False/protective_stop/torn=False/stop=True | False/protective_stop/torn=False/stop=True | True | pull 36.7 N above 36.0 N: stop pulling, plug held at 2.05 mm |
| arm | latching | 2026 | mf_noise_1mm | H | 7 | False/aborted:excess_torque/torn=False/stop=False | False/aborted:excess_torque/torn=False/stop=False | True | pull 36.1 N above 36.0 N: stop pulling, plug held at 5.78 mm |
| gantry | latching | 2026 | mf_noise_1mm | D | 7 | False/protective_stop/torn=False/stop=True | False/protective_stop/torn=True/stop=True | True | pull 37.0 N above 36.0 N: stop pulling, plug held at 6.01 mm |
| gantry | latching | 2026 | mf_noise_1mm | H | 7 | False/protective_stop/torn=False/stop=True | False/protective_stop/torn=True/stop=True | True | pull 37.0 N above 36.0 N: stop pulling, plug held at 6.01 mm |
| gantry | latching | 2027 | mf_noise_1mm | D | 17 | False/protective_stop/torn=True/stop=True | False/protective_stop/torn=False/stop=True | True | pull 36.5 N above 36.0 N: stop pulling, plug held at 7.87 mm |
| gantry | latching | 2027 | mf_noise_1mm | D | 19 | False/false_accept/torn=True/stop=False | False/aborted:stuck_during_retract/torn=True/stop=False | True | pull 40.3 N above 36.0 N: stop pulling, plug held at 7.86 mm |
| gantry | latching | 2027 | mf_noise_1mm | H | 17 | False/protective_stop/torn=True/stop=True | False/protective_stop/torn=False/stop=True | True | pull 36.5 N above 36.0 N: stop pulling, plug held at 7.87 mm |
| gantry | latching | 2027 | mf_noise_1mm | H | 19 | False/aborted:retention_failed/torn=True/stop=False | False/aborted:stuck_during_retract/torn=True/stop=False | True | pull 40.3 N above 36.0 N: stop pulling, plug held at 7.86 mm |
