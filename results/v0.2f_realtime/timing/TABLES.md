# v0.2f tick timing tables

Development measurement on an Apple M5 laptop (4 performance + 6 efficiency cores) shared with other jobs; not the rig PC. Made by `python -m experiments.v02f_tick_timing --tables results/v0.2f_realtime/timing`. Times in microseconds per 500 Hz tick (budget 2000 us). total = StateEstimator.update + controller.step + CartesianMotionGenerator.update, wall clock, in the trial loop. replay = per-tick minimum of controller.step over 3 replays of the recorded observations (intrinsic cost, scheduling noise mostly removed). best = min(in-loop controller.step, its replays). cpu = thread CPU time of the same work as total. nogc = ticks without a Python GC collection.

## run1_gantry (loaded)

720 trials, 1996009 ticks, commit 4df8cae, 1-min load average per trial: min 31.4, mean 48.4, max 74.0. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.14/250.60, G 0.27/7.13, J 0.16/8.17, F 0.03/0.19, I 0.02/0.86.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 469173 | 47.1 | 203.1 | 7579.3 | 88191.7 | 2248 (51) | 249.4 | 1313.4 | 28 (28) | 16.5 | 47.3 | 62.0 | 1134.1 | 34 | 1 | 0 | 1115 |
| C | ALIGN | 15558 | 44.8 | 151.6 | 5235.1 | 10147.6 | 57 (0) | 195.1 | 224.3 | 0 (0) | 11.6 | 48.2 | 66.4 | 92.2 | 0 | 0 | 0 | 12 |
| C | APPROACH | 106201 | 46.5 | 216.6 | 7827.0 | 88191.7 | 578 (7) | 197.2 | 291.4 | 6 (6) | 23.2 | 54.2 | 55.4 | 59.9 | 0 | 0 | 0 | 242 |
| C | DETECT | 18741 | 48.9 | 356.8 | 7510.3 | 16099.6 | 87 (2) | 532.7 | 628.7 | 0 (0) | 21.4 | 136.8 | 229.9 | 480.6 | 0 | 0 | 0 | 38 |
| C | FAILURE | 7575 | 48.8 | 259.3 | 7473.7 | 48368.0 | 47 (2) | 196.2 | 226.3 | 1 (1) | 24.1 | 56.0 | 57.5 | 58.2 | 0 | 0 | 0 | 6 |
| C | IDLE | 144 | 62.2 | 151.4 | 155.2 | 155.4 | 0 (0) | 166.5 | 167.0 | 0 (0) | 33.1 | 39.4 | 63.0 | 66.6 | 0 | 0 | 0 | 0 |
| C | INSERT | 147915 | 47.0 | 192.7 | 7658.9 | 71561.0 | 707 (17) | 199.4 | 372.1 | 8 (8) | 15.2 | 35.6 | 48.8 | 163.5 | 0 | 0 | 0 | 424 |
| C | RECOVER | 13797 | 49.3 | 313.5 | 8685.1 | 45298.9 | 59 (1) | 1204.4 | 1313.4 | 1 (1) | 24.6 | 58.5 | 631.6 | 1134.1 | 34 | 1 | 0 | 17 |
| C | VERIFY | 159242 | 47.0 | 178.3 | 7518.8 | 78470.5 | 713 (22) | 205.8 | 394.5 | 12 (12) | 14.0 | 36.9 | 62.2 | 107.7 | 0 | 0 | 0 | 376 |
| G | ALL | 471297 | 47.3 | 195.4 | 8639.3 | 173348.5 | 2404 (55) | 262.3 | 1921.1 | 29 (29) | 16.5 | 45.1 | 62.0 | 1588.2 | 37 | 1 | 0 | 1113 |
| G | ALIGN | 16080 | 44.3 | 150.6 | 8591.5 | 148698.7 | 74 (1) | 192.0 | 249.0 | 1 (1) | 11.7 | 53.6 | 71.7 | 133.0 | 0 | 0 | 0 | 15 |
| G | APPROACH | 106201 | 46.7 | 205.0 | 8776.6 | 68584.6 | 572 (6) | 190.9 | 295.2 | 1 (1) | 23.3 | 54.2 | 55.7 | 60.0 | 0 | 0 | 0 | 225 |
| G | DETECT | 18640 | 49.2 | 497.9 | 7438.4 | 11834.0 | 92 (0) | 559.2 | 640.8 | 0 (0) | 21.7 | 143.0 | 227.9 | 489.6 | 0 | 0 | 0 | 26 |
| G | FAILURE | 7693 | 48.1 | 214.8 | 7605.9 | 106173.0 | 45 (1) | 187.6 | 195.8 | 1 (1) | 24.2 | 56.7 | 58.0 | 62.2 | 0 | 0 | 0 | 6 |
| G | IDLE | 144 | 65.4 | 264.3 | 8931.1 | 10376.0 | 1 (0) | 177.2 | 177.9 | 0 (0) | 36.3 | 72.2 | 75.5 | 76.0 | 0 | 0 | 0 | 0 |
| G | INSERT | 149017 | 47.1 | 175.7 | 8393.3 | 130044.5 | 733 (20) | 203.3 | 355.2 | 8 (8) | 15.4 | 35.6 | 49.1 | 295.0 | 0 | 0 | 0 | 449 |
| G | RECOVER | 14316 | 49.6 | 386.1 | 9033.4 | 157997.9 | 81 (2) | 1056.2 | 1921.1 | 1 (1) | 24.6 | 57.6 | 854.1 | 1588.2 | 37 | 1 | 0 | 12 |
| G | VERIFY | 159206 | 46.9 | 174.2 | 8751.1 | 173348.5 | 806 (25) | 217.0 | 431.7 | 17 (17) | 14.1 | 33.7 | 62.0 | 269.9 | 0 | 0 | 0 | 380 |
| J | ALL | 441168 | 41.9 | 191.5 | 6662.4 | 390256.4 | 1863 (54) | 205.3 | 649.8 | 28 (28) | 10.4 | 37.0 | 66.4 | 239.0 | 0 | 0 | 0 | 1167 |
| J | APPROACH | 107699 | 31.4 | 146.5 | 6105.8 | 306876.4 | 394 (14) | 164.1 | 326.1 | 10 (10) | 8.9 | 22.3 | 23.1 | 29.2 | 0 | 0 | 0 | 251 |
| J | DESCEND | 60809 | 30.6 | 132.6 | 6354.6 | 168094.2 | 203 (9) | 184.4 | 233.0 | 6 (6) | 7.1 | 17.8 | 55.7 | 74.7 | 0 | 0 | 0 | 191 |
| J | FAILURE | 2723 | 34.3 | 461.0 | 9239.5 | 20543.5 | 13 (1) | 512.5 | 180.2 | 0 (0) | 8.9 | 22.7 | 23.6 | 30.2 | 0 | 0 | 0 | 4 |
| J | IDLE | 144 | 48.0 | 108.5 | 2789.4 | 3236.2 | 1 (0) | 127.8 | 129.1 | 0 (0) | 18.0 | 30.8 | 34.7 | 34.8 | 0 | 0 | 0 | 0 |
| J | INSERT | 18607 | 36.0 | 244.6 | 6172.4 | 13251.3 | 72 (1) | 285.6 | 374.5 | 0 (0) | 10.9 | 26.8 | 99.4 | 239.0 | 0 | 0 | 0 | 29 |
| J | RECOVER | 11023 | 52.3 | 306.5 | 8506.4 | 163947.8 | 64 (2) | 220.2 | 522.5 | 1 (1) | 26.4 | 62.6 | 65.8 | 67.2 | 0 | 0 | 0 | 5 |
| J | SPIRAL | 54875 | 34.3 | 145.2 | 6492.4 | 207494.6 | 205 (7) | 179.7 | 335.9 | 4 (4) | 10.2 | 24.7 | 25.5 | 41.0 | 0 | 0 | 0 | 132 |
| J | TARE | 10367 | 26.9 | 121.9 | 5455.3 | 11669.2 | 29 (1) | 177.0 | 185.5 | 0 (0) | 5.3 | 36.0 | 42.4 | 81.2 | 0 | 0 | 0 | 39 |
| J | VERIFY | 174921 | 50.4 | 263.1 | 6896.4 | 390256.4 | 882 (19) | 219.5 | 649.8 | 7 (7) | 16.4 | 41.7 | 67.2 | 201.0 | 0 | 0 | 0 | 516 |
| F | ALL | 246429 | 32.7 | 180.6 | 8656.8 | 525052.1 | 1032 (23) | 170.9 | 309.6 | 16 (16) | 8.9 | 22.5 | 26.4 | 77.1 | 0 | 0 | 0 | 609 |
| F | APPROACH | 107546 | 31.2 | 194.1 | 8702.2 | 499473.0 | 463 (10) | 162.8 | 226.3 | 9 (9) | 8.8 | 22.3 | 23.3 | 27.6 | 0 | 0 | 0 | 268 |
| F | DESCEND | 56011 | 30.4 | 160.0 | 8286.7 | 525052.1 | 219 (7) | 180.1 | 212.1 | 5 (5) | 6.9 | 14.0 | 21.2 | 32.2 | 0 | 0 | 0 | 174 |
| F | FAILURE | 2693 | 31.6 | 107.1 | 4564.8 | 8161.2 | 9 (0) | 150.2 | 149.0 | 0 (0) | 9.0 | 22.9 | 23.3 | 23.5 | 0 | 0 | 0 | 3 |
| F | IDLE | 144 | 46.0 | 190.8 | 269.5 | 282.1 | 0 (0) | 145.6 | 147.5 | 0 (0) | 13.2 | 29.0 | 29.4 | 29.5 | 0 | 0 | 0 | 0 |
| F | INSERT | 15952 | 35.4 | 215.4 | 8841.0 | 19698.6 | 71 (0) | 182.6 | 309.6 | 0 (0) | 10.7 | 26.0 | 27.0 | 45.3 | 0 | 0 | 0 | 20 |
| F | SPIRAL | 54875 | 34.0 | 180.5 | 8841.2 | 376500.2 | 238 (6) | 184.7 | 264.1 | 2 (2) | 10.0 | 24.8 | 25.6 | 33.4 | 0 | 0 | 0 | 140 |
| F | TARE | 9208 | 26.3 | 124.5 | 7105.2 | 25314.8 | 32 (0) | 142.7 | 240.2 | 0 (0) | 5.3 | 33.7 | 42.9 | 77.1 | 0 | 0 | 0 | 4 |
| I | ALL | 367942 | 33.3 | 145.3 | 8649.5 | 393479.0 | 1513 (35) | 165.0 | 270.2 | 23 (23) | 9.2 | 22.7 | 26.5 | 69.7 | 0 | 0 | 0 | 702 |
| I | APPROACH | 107546 | 31.1 | 140.5 | 8298.0 | 319875.2 | 428 (8) | 154.9 | 204.2 | 5 (5) | 8.8 | 22.2 | 23.1 | 27.2 | 0 | 0 | 0 | 261 |
| I | DESCEND | 56011 | 30.5 | 154.5 | 8695.1 | 327680.7 | 227 (9) | 185.1 | 236.7 | 6 (6) | 6.9 | 17.0 | 21.0 | 34.5 | 0 | 0 | 0 | 176 |
| I | FAILURE | 8876 | 31.6 | 119.1 | 7792.6 | 393479.0 | 31 (1) | 133.0 | 151.4 | 1 (1) | 8.9 | 10.7 | 22.5 | 23.0 | 0 | 0 | 0 | 6 |
| I | IDLE | 144 | 46.4 | 498.1 | 3383.0 | 3864.2 | 1 (0) | 184.3 | 192.0 | 0 (0) | 14.8 | 25.7 | 28.7 | 29.0 | 0 | 0 | 0 | 0 |
| I | INSERT | 15952 | 35.6 | 152.1 | 8563.9 | 24934.5 | 74 (0) | 169.7 | 228.7 | 0 (0) | 10.7 | 26.3 | 27.0 | 36.7 | 0 | 0 | 0 | 24 |
| I | SPIRAL | 54875 | 33.8 | 144.3 | 9070.9 | 309712.2 | 232 (6) | 181.8 | 223.8 | 4 (4) | 10.1 | 24.5 | 25.3 | 41.4 | 0 | 0 | 0 | 141 |
| I | TARE | 9208 | 26.3 | 123.2 | 7464.0 | 12813.1 | 29 (0) | 140.3 | 179.1 | 0 (0) | 5.3 | 34.5 | 41.4 | 69.7 | 0 | 0 | 0 | 5 |
| I | VERIFY | 115330 | 34.3 | 152.2 | 8932.0 | 307478.5 | 491 (11) | 167.8 | 270.2 | 7 (7) | 9.5 | 23.1 | 26.7 | 31.7 | 0 | 0 | 0 | 89 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| G | mf_noise_1mm | 2026 | 0 | 4.422 | RECOVER -> ALIGN | 1.588 | 2.019 | 1.921 | 0 | _plan_correction 1.928; update_blocked 0.687; _contact_prior_update 0.515 |
| C | mf_stubbed_terminal | 2027 | 1 | 3.368 | RECOVER -> ALIGN | 1.134 | 1.186 | 1.201 | 0 | _plan_correction 1.099; update_blocked 0.435; best_probe 0.284 |
| G | mf_broken_latch | 2026 | 0 | 3.398 | RECOVER -> ALIGN | 0.934 | 0.960 | 0.965 | 0 | _plan_correction 0.917; update_blocked 0.306; _contact_prior_update 0.270 |
| G | mf_wrong_polarization | 2027 | 0 | 9.452 | RECOVER -> ALIGN | 0.906 | 0.932 | 0.937 | 0 | _plan_correction 0.890; update_blocked 0.296; _contact_prior_update 0.238 |
| G | noise_2mm | 2026 | 1 | 7.064 | RECOVER -> ALIGN | 0.899 | 0.925 | 0.930 | 0 | _plan_correction 0.884; update_blocked 0.316; _contact_prior_update 0.217 |
| G | noise_2mm | 2027 | 0 | 4.28 | RECOVER -> ALIGN | 0.899 | 0.981 | 0.987 | 0 | _plan_correction 0.942; update_blocked 0.360; _contact_prior_update 0.256 |
| G | mf_spread_half_latched | 2027 | 0 | 3.54 | RECOVER -> ALIGN | 0.883 | 11.865 | 1.435 | 0 | _plan_correction 11.769; update_blocked 10.742; best_probe 0.426 |
| G | mf_terminal_min | 2026 | 0 | 5.678 | RECOVER -> ALIGN | 0.882 | 1.629 | 1.640 | 0 | _plan_correction 1.542; _contact_prior_update 0.432; update_blocked 0.432 |
| G | noise_2mm | 2026 | 1 | 3.686 | RECOVER -> ALIGN | 0.875 | 1.122 | 1.127 | 0 | _plan_correction 1.080; update_blocked 0.406; _contact_prior_update 0.321 |
| G | mf_wrong_polarization | 2027 | 0 | 12.922 | RECOVER -> ALIGN | 0.875 | 0.900 | 0.904 | 0 | _plan_correction 0.857; update_blocked 0.281; _contact_prior_update 0.222 |
| G | mf_wrong_polarization | 2026 | 1 | 3.314 | RECOVER -> ALIGN | 0.873 | 0.900 | 0.905 | 0 | _plan_correction 0.856; update_blocked 0.291; _contact_prior_update 0.226 |
| G | mf_wrong_polarization | 2027 | 0 | 11.102 | RECOVER -> ALIGN | 0.866 | 1.793 | 1.766 | 0 | _plan_correction 1.704; _contact_prior_update 0.457; update_blocked 0.438 |
| G | mf_wrong_polarization | 2027 | 1 | 3.322 | RECOVER -> ALIGN | 0.864 | 0.915 | 0.920 | 0 | _plan_correction 0.874; update_blocked 0.315; _contact_prior_update 0.226 |
| G | noise_2mm | 2027 | 1 | 4.676 | RECOVER -> ALIGN | 0.858 | 0.882 | 0.887 | 0 | _plan_correction 0.843; update_blocked 0.282; _contact_prior_update 0.233 |
| G | mf_wrong_polarization | 2027 | 0 | 7.74 | RECOVER -> ALIGN | 0.855 | 2.586 | 1.530 | 0 | _plan_correction 2.529; update_blocked 1.470; _contact_prior_update 0.450 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 75 | 114.4 | 485.5 | 980.4 |
| C | AdaptiveInsertionController._begin_verify | 162 | 65.4 | 299.0 | 982.8 |
| C | AdaptiveInsertionController._click_in_trace | 75 | 48.4 | 174.1 | 176.0 |
| C | AdaptiveInsertionController._diagnose | 209 | 142.7 | 2428.4 | 4726.9 |
| C | AdaptiveInsertionController._plan_correction | 60 | 615.9 | 5532.6 | 10905.6 |
| C | AdaptiveInsertionController._record_contact | 209 | 13.1 | 26.9 | 91.2 |
| C | AdaptiveInsertionController._tilt_verdict | 75 | 34.9 | 84.6 | 86.5 |
| C | HoleLocalizer.best_probe | 34 | 162.4 | 329.0 | 333.4 |
| C | HoleLocalizer.entry_probability_at | 34 | 133.8 | 278.5 | 290.0 |
| C | HoleLocalizer.update_blocked | 34 | 429.6 | 7323.7 | 10348.0 |
| C | HoleLocalizer.update_entered | 2 | 38.1 | 49.9 | 50.2 |
| G | AdaptiveInsertionController._begin_latch_verify | 75 | 205.2 | 3160.9 | 6285.0 |
| G | AdaptiveInsertionController._begin_verify | 162 | 65.0 | 424.7 | 2064.7 |
| G | AdaptiveInsertionController._click_in_trace | 75 | 91.8 | 176.7 | 215.7 |
| G | AdaptiveInsertionController._diagnose | 213 | 151.4 | 449.1 | 5577.8 |
| G | AdaptiveInsertionController._plan_correction | 63 | 842.8 | 14301.8 | 18433.5 |
| G | AdaptiveInsertionController._record_contact | 213 | 13.7 | 26.2 | 120.4 |
| G | AdaptiveInsertionController._tilt_verdict | 75 | 63.2 | 2986.0 | 6074.5 |
| G | AdaptiveLearnedController._contact_prior_update | 37 | 232.9 | 11196.2 | 17204.1 |
| G | ContactLikelihood.localizer_log_term | 37 | 185.2 | 11084.6 | 17078.9 |
| G | ContactLikelihood.mixture_mean_mm | 37 | 23.4 | 62.6 | 72.7 |
| G | HoleLocalizer.best_probe | 37 | 144.5 | 1119.4 | 1509.5 |
| G | HoleLocalizer.entry_probability_at | 37 | 118.5 | 271.4 | 278.8 |
| G | HoleLocalizer.update_blocked | 37 | 303.3 | 7404.2 | 10742.5 |
| G | HoleLocalizer.update_entered | 2 | 36.5 | 46.8 | 47.0 |
| G | HoleLocalizer.update_log_term | 37 | 3.1 | 8.6 | 9.6 |
| J | AdaptiveInsertionController._begin_latch_verify | 72 | 84.0 | 231.9 | 233.0 |
| J | AdaptiveInsertionController._begin_verify | 151 | 42.3 | 179.0 | 2807.0 |
| J | AdaptiveInsertionController._click_in_trace | 72 | 24.4 | 103.5 | 107.0 |
| J | AdaptiveInsertionController._tilt_verdict | 72 | 7.1 | 82.4 | 85.4 |

## run2_arm (loaded)

720 trials, 3186355 ticks, commit 4df8cae, 1-min load average per trial: min 30.8, mean 78.1, max 183.6. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.15/163.86, G 0.30/4.18, J 0.17/0.93, F 0.02/1.03, I 0.02/0.08.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 751134 | 49.1 | 230.6 | 2322.8 | 45503.7 | 904 (20) | 245.5 | 1531.0 | 7 (7) | 17.9 | 40.1 | 58.4 | 1212.0 | 46 | 2 | 0 | 527 |
| C | ALIGN | 18450 | 46.9 | 181.0 | 1886.3 | 8430.4 | 18 (0) | 238.8 | 390.5 | 0 (0) | 11.9 | 52.9 | 79.3 | 103.3 | 0 | 0 | 0 | 13 |
| C | APPROACH | 106201 | 48.3 | 214.7 | 2147.4 | 45503.7 | 116 (1) | 195.6 | 293.6 | 1 (1) | 23.4 | 53.5 | 55.9 | 67.3 | 0 | 0 | 0 | 65 |
| C | DETECT | 45327 | 57.2 | 361.0 | 2870.0 | 15014.7 | 65 (1) | 606.3 | 920.7 | 0 (0) | 25.0 | 56.9 | 259.6 | 512.5 | 1 | 0 | 0 | 59 |
| C | FAILURE | 8278 | 52.1 | 301.6 | 2743.0 | 11590.6 | 19 (0) | 234.1 | 358.9 | 0 (0) | 24.6 | 57.0 | 59.2 | 61.1 | 0 | 0 | 0 | 5 |
| C | IDLE | 144 | 64.4 | 200.3 | 881.1 | 992.9 | 0 (0) | 214.4 | 216.7 | 0 (0) | 33.4 | 67.6 | 70.6 | 71.0 | 0 | 0 | 0 | 0 |
| C | INSERT | 348634 | 43.8 | 212.0 | 2184.7 | 31021.0 | 395 (12) | 212.3 | 397.8 | 5 (5) | 15.3 | 35.5 | 50.0 | 142.0 | 0 | 0 | 0 | 237 |
| C | RECOVER | 15213 | 51.7 | 327.5 | 2451.8 | 4487.6 | 24 (0) | 1216.3 | 1531.0 | 0 (0) | 25.1 | 57.9 | 652.9 | 1212.0 | 45 | 2 | 0 | 10 |
| C | VERIFY | 208887 | 49.7 | 242.0 | 2414.7 | 31848.0 | 267 (6) | 228.9 | 670.7 | 1 (1) | 18.2 | 41.1 | 55.3 | 214.8 | 0 | 0 | 0 | 138 |
| G | ALL | 739691 | 49.5 | 408.3 | 4175.6 | 121283.5 | 2005 (32) | 268.0 | 1852.8 | 8 (8) | 17.8 | 41.5 | 61.6 | 1498.2 | 37 | 3 | 0 | 531 |
| G | ALIGN | 16035 | 46.4 | 334.2 | 3811.4 | 18576.3 | 35 (0) | 326.3 | 541.1 | 0 (0) | 11.8 | 52.9 | 79.7 | 126.4 | 0 | 0 | 0 | 9 |
| G | APPROACH | 106201 | 49.0 | 460.5 | 4402.0 | 121283.5 | 312 (3) | 222.0 | 383.1 | 2 (2) | 23.3 | 54.1 | 55.8 | 60.9 | 0 | 0 | 0 | 76 |
| G | DETECT | 37736 | 56.5 | 402.3 | 3373.2 | 11237.8 | 94 (4) | 648.3 | 892.4 | 0 (0) | 24.8 | 61.9 | 269.2 | 723.7 | 3 | 0 | 0 | 51 |
| G | FAILURE | 7545 | 51.4 | 360.2 | 3833.0 | 17094.5 | 27 (0) | 207.9 | 232.2 | 0 (0) | 24.3 | 57.0 | 58.9 | 59.4 | 0 | 0 | 0 | 3 |
| G | IDLE | 144 | 68.9 | 321.6 | 1644.2 | 1862.3 | 0 (0) | 204.1 | 206.3 | 0 (0) | 37.6 | 72.3 | 79.7 | 80.9 | 0 | 0 | 0 | 0 |
| G | INSERT | 343756 | 46.8 | 390.8 | 4077.2 | 57942.1 | 872 (8) | 232.8 | 1572.0 | 4 (4) | 15.3 | 35.8 | 50.4 | 137.8 | 0 | 0 | 0 | 229 |
| G | RECOVER | 13602 | 51.8 | 664.2 | 3751.5 | 12460.3 | 39 (3) | 1542.0 | 1852.8 | 0 (0) | 24.8 | 58.0 | 807.3 | 1498.2 | 34 | 3 | 0 | 7 |
| G | VERIFY | 214672 | 50.1 | 417.9 | 4355.6 | 40146.9 | 626 (14) | 255.7 | 649.8 | 2 (2) | 18.1 | 41.5 | 61.6 | 231.0 | 0 | 0 | 0 | 156 |
| J | ALL | 709025 | 48.6 | 190.4 | 2765.1 | 27053.8 | 1118 (34) | 204.0 | 573.8 | 16 (16) | 10.8 | 37.3 | 65.9 | 477.7 | 0 | 0 | 0 | 509 |
| J | APPROACH | 108843 | 32.8 | 137.2 | 2643.3 | 19797.9 | 146 (8) | 147.9 | 265.2 | 6 (6) | 9.0 | 22.2 | 22.8 | 27.2 | 0 | 0 | 0 | 58 |
| J | DESCEND | 217027 | 31.2 | 137.9 | 2404.1 | 27053.8 | 285 (7) | 150.5 | 361.7 | 3 (3) | 7.2 | 17.5 | 21.0 | 157.1 | 0 | 0 | 0 | 136 |
| J | DETECT | 75 | 39.1 | 330.1 | 332.2 | 332.4 | 0 (0) | 337.9 | 338.2 | 0 (0) | 14.4 | 261.5 | 285.6 | 288.3 | 0 | 0 | 0 | 1 |
| J | FAILURE | 3340 | 34.9 | 217.7 | 4107.7 | 13757.4 | 10 (1) | 147.9 | 164.8 | 1 (1) | 9.0 | 9.9 | 12.5 | 13.7 | 0 | 0 | 0 | 2 |
| J | IDLE | 144 | 47.4 | 148.4 | 175.3 | 179.0 | 0 (0) | 150.0 | 153.5 | 0 (0) | 17.9 | 35.3 | 37.3 | 37.6 | 0 | 0 | 0 | 0 |
| J | INSERT | 57858 | 36.6 | 176.1 | 2647.1 | 17721.4 | 82 (6) | 344.7 | 559.5 | 0 (0) | 10.9 | 26.5 | 149.4 | 477.7 | 0 | 0 | 0 | 92 |
| J | RECOVER | 12583 | 55.2 | 255.7 | 2243.6 | 7586.8 | 16 (1) | 324.8 | 231.8 | 0 (0) | 27.3 | 63.8 | 65.6 | 67.9 | 0 | 0 | 0 | 19 |
| J | SPIRAL | 61700 | 39.2 | 191.0 | 2724.6 | 14623.4 | 95 (1) | 169.5 | 227.5 | 1 (1) | 12.7 | 29.0 | 30.6 | 32.6 | 0 | 0 | 0 | 38 |
| J | TARE | 10673 | 27.2 | 120.2 | 1853.6 | 5600.6 | 11 (0) | 172.6 | 240.6 | 0 (0) | 5.5 | 35.2 | 42.1 | 68.2 | 0 | 0 | 0 | 13 |
| J | VERIFY | 236782 | 53.7 | 260.2 | 3107.3 | 23490.5 | 473 (10) | 216.8 | 573.8 | 5 (5) | 20.4 | 47.5 | 66.7 | 205.0 | 0 | 0 | 0 | 150 |
| F | ALL | 418352 | 34.7 | 108.0 | 537.2 | 15506.5 | 92 (3) | 147.8 | 243.3 | 3 (3) | 8.8 | 17.3 | 29.2 | 66.0 | 0 | 0 | 0 | 266 |
| F | APPROACH | 108105 | 32.5 | 101.4 | 494.0 | 12113.4 | 22 (1) | 138.0 | 188.0 | 1 (1) | 9.0 | 21.0 | 22.2 | 26.2 | 0 | 0 | 0 | 69 |
| F | DESCEND | 186958 | 30.3 | 98.1 | 531.5 | 15506.5 | 41 (2) | 140.1 | 243.3 | 2 (2) | 7.1 | 16.9 | 17.8 | 36.3 | 0 | 0 | 0 | 123 |
| F | FAILURE | 2619 | 33.7 | 94.6 | 305.6 | 577.1 | 0 (0) | 133.7 | 143.2 | 0 (0) | 9.1 | 9.8 | 11.5 | 12.3 | 0 | 0 | 0 | 1 |
| F | IDLE | 144 | 45.3 | 109.1 | 111.3 | 111.7 | 0 (0) | 128.2 | 128.3 | 0 (0) | 13.5 | 23.7 | 28.7 | 28.9 | 0 | 0 | 0 | 0 |
| F | INSERT | 49493 | 36.0 | 111.5 | 580.8 | 7303.8 | 10 (0) | 145.3 | 218.2 | 0 (0) | 10.7 | 25.2 | 26.4 | 40.3 | 0 | 0 | 0 | 28 |
| F | SPIRAL | 61700 | 38.8 | 124.9 | 685.6 | 10168.9 | 16 (0) | 167.9 | 219.6 | 0 (0) | 12.5 | 28.8 | 29.9 | 42.2 | 0 | 0 | 0 | 41 |
| F | TARE | 9333 | 26.6 | 107.8 | 341.1 | 4609.1 | 3 (0) | 131.5 | 179.5 | 0 (0) | 5.4 | 32.6 | 39.6 | 66.0 | 0 | 0 | 0 | 4 |
| I | ALL | 568153 | 35.0 | 106.4 | 535.8 | 66698.5 | 129 (7) | 149.6 | 299.3 | 6 (6) | 9.1 | 21.3 | 29.3 | 68.8 | 0 | 0 | 0 | 365 |
| I | APPROACH | 108105 | 32.5 | 100.9 | 476.5 | 9180.9 | 25 (2) | 134.3 | 182.7 | 1 (1) | 9.0 | 21.0 | 22.2 | 32.6 | 0 | 0 | 0 | 72 |
| I | DESCEND | 186958 | 30.3 | 93.0 | 502.4 | 10809.9 | 38 (2) | 136.8 | 211.8 | 2 (2) | 7.0 | 17.0 | 20.3 | 35.6 | 0 | 0 | 0 | 128 |
| I | FAILURE | 8610 | 33.7 | 103.4 | 420.0 | 11977.4 | 2 (1) | 136.6 | 174.1 | 1 (1) | 9.0 | 11.7 | 22.1 | 22.3 | 0 | 0 | 0 | 6 |
| I | IDLE | 144 | 46.2 | 118.8 | 167.4 | 174.7 | 0 (0) | 131.3 | 131.7 | 0 (0) | 14.3 | 29.3 | 30.9 | 31.2 | 0 | 0 | 0 | 0 |
| I | INSERT | 49493 | 35.8 | 106.2 | 453.8 | 7669.5 | 7 (1) | 147.0 | 210.3 | 1 (1) | 10.7 | 25.3 | 26.4 | 31.9 | 0 | 0 | 0 | 29 |
| I | SPIRAL | 61700 | 38.7 | 119.9 | 666.3 | 38432.8 | 25 (0) | 171.9 | 299.3 | 0 (0) | 12.5 | 29.0 | 30.4 | 41.8 | 0 | 0 | 0 | 38 |
| I | TARE | 9333 | 27.4 | 110.7 | 393.2 | 1737.2 | 0 (0) | 133.8 | 152.5 | 0 (0) | 5.4 | 33.1 | 38.6 | 68.8 | 0 | 0 | 0 | 3 |
| I | VERIFY | 143810 | 35.3 | 111.8 | 612.4 | 66698.5 | 32 (1) | 154.1 | 273.3 | 1 (1) | 9.6 | 22.7 | 26.2 | 29.6 | 0 | 0 | 0 | 89 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| G | mf_terminal_min | 2026 | 0 | 7.876 | RECOVER -> ALIGN | 1.498 | 2.138 | 1.234 | 0 | _plan_correction 2.076; _contact_prior_update 1.199; localizer_term 0.993 |
| G | mf_terminal_max_broken_latch | 2027 | 0 | 5.174 | RECOVER -> ALIGN | 1.473 | 1.869 | 1.853 | 0 | _plan_correction 1.768; update_blocked 0.590; _contact_prior_update 0.342 |
| C | mf_terminal_max_broken_latch | 2026 | 1 | 5.38 | RECOVER -> ALIGN | 1.212 | 1.447 | 1.458 | 0 | _plan_correction 1.355; update_blocked 0.606; entry_probability_at 0.314 |
| G | generalization_tight | 2026 | 0 | 7.442 | RECOVER -> ALIGN | 1.156 | 1.658 | 1.640 | 0 | _plan_correction 1.570; update_blocked 0.493; best_probe 0.316 |
| C | mf_terminal_min | 2026 | 0 | 8.534 | RECOVER -> ALIGN | 1.141 | 1.237 | 1.248 | 0 | _plan_correction 1.146; update_blocked 0.446; best_probe 0.310 |
| G | noise_2mm | 2027 | 0 | 6.964 | RECOVER -> ALIGN | 0.962 | 0.986 | 0.991 | 0 | _plan_correction 0.946; update_blocked 0.428; _contact_prior_update 0.169 |
| G | mf_stubbed_terminal | 2026 | 0 | 5.25 | RECOVER -> ALIGN | 0.908 | 3.444 | 1.807 | 0 | _plan_correction 3.349; _contact_prior_update 1.996; localizer_term 1.773 |
| G | generalization_combined | 2027 | 0 | 4.81 | RECOVER -> ALIGN | 0.878 | 1.647 | 1.657 | 0 | _plan_correction 1.560; update_blocked 0.547; _contact_prior_update 0.311 |
| G | noise_2mm | 2026 | 1 | 8.516 | RECOVER -> ALIGN | 0.840 | 1.763 | 1.765 | 1 | _plan_correction 1.624; update_blocked 0.519; _contact_prior_update 0.309 |
| G | mf_latch_early | 2027 | 0 | 5.268 | RECOVER -> ALIGN | 0.828 | 1.200 | 1.129 | 0 | _plan_correction 1.154; update_blocked 0.419; _contact_prior_update 0.257 |
| G | noise_2mm | 2027 | 0 | 9.076 | RECOVER -> ALIGN | 0.821 | 0.912 | 0.919 | 0 | _plan_correction 0.869; update_blocked 0.350; _contact_prior_update 0.161 |
| G | mf_noise_1mm | 2027 | 0 | 5.664 | RECOVER -> ALIGN | 0.819 | 0.872 | 0.878 | 0 | _plan_correction 0.828; update_blocked 0.319; _contact_prior_update 0.164 |
| G | generalization_tight | 2027 | 1 | 5.382 | RECOVER -> ALIGN | 0.812 | 0.877 | 0.882 | 0 | _plan_correction 0.838; update_blocked 0.373; _contact_prior_update 0.142 |
| G | mf_spread | 2026 | 1 | 5.32 | RECOVER -> ALIGN | 0.812 | 0.931 | 0.941 | 0 | _plan_correction 0.888; update_blocked 0.348; entry_probability_at 0.166 |
| G | mf_wrong_polarization | 2027 | 0 | 6.56 | RECOVER -> ALIGN | 0.809 | 0.942 | 0.947 | 0 | _plan_correction 0.898; update_blocked 0.372; _contact_prior_update 0.170 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 86 | 213.7 | 939.8 | 1633.3 |
| C | AdaptiveInsertionController._begin_verify | 172 | 91.4 | 796.9 | 1636.0 |
| C | AdaptiveInsertionController._click_in_trace | 86 | 142.3 | 660.4 | 1457.2 |
| C | AdaptiveInsertionController._diagnose | 238 | 154.8 | 1215.7 | 3713.0 |
| C | AdaptiveInsertionController._plan_correction | 75 | 661.1 | 1687.7 | 2396.3 |
| C | AdaptiveInsertionController._record_contact | 238 | 13.3 | 32.9 | 54.3 |
| C | AdaptiveInsertionController._tilt_verdict | 86 | 44.6 | 252.1 | 383.1 |
| C | HoleLocalizer.best_probe | 45 | 172.6 | 412.6 | 455.8 |
| C | HoleLocalizer.entry_probability_at | 45 | 148.9 | 861.3 | 1240.7 |
| C | HoleLocalizer.update_blocked | 45 | 384.5 | 745.5 | 842.5 |
| C | HoleLocalizer.update_entered | 2 | 29.9 | 30.4 | 30.4 |
| G | AdaptiveInsertionController._begin_latch_verify | 86 | 285.7 | 3704.8 | 3794.0 |
| G | AdaptiveInsertionController._begin_verify | 175 | 99.8 | 3375.2 | 3795.8 |
| G | AdaptiveInsertionController._click_in_trace | 86 | 182.4 | 3192.5 | 3600.8 |
| G | AdaptiveInsertionController._diagnose | 229 | 153.1 | 632.4 | 2886.7 |
| G | AdaptiveInsertionController._plan_correction | 64 | 771.7 | 3445.3 | 3608.9 |
| G | AdaptiveInsertionController._record_contact | 229 | 13.9 | 56.7 | 222.1 |
| G | AdaptiveInsertionController._tilt_verdict | 86 | 47.3 | 590.7 | 3311.8 |
| G | AdaptiveLearnedController._contact_prior_update | 34 | 270.4 | 2252.8 | 2379.5 |
| G | ContactPrior.localizer_term | 34 | 92.0 | 2087.8 | 2242.8 |
| G | HoleLocalizer.best_probe | 34 | 232.0 | 1326.9 | 1782.5 |
| G | HoleLocalizer.entry_probability_at | 34 | 164.6 | 491.9 | 566.2 |
| G | HoleLocalizer.update_blocked | 34 | 413.4 | 1384.8 | 1504.3 |
| G | HoleLocalizer.update_entered | 2 | 102.7 | 137.5 | 138.2 |
| G | HoleLocalizer.update_gaussian | 34 | 118.4 | 218.5 | 233.5 |
| J | AdaptiveInsertionController._begin_latch_verify | 77 | 164.6 | 806.2 | 1099.5 |
| J | AdaptiveInsertionController._begin_verify | 159 | 87.6 | 493.9 | 715.3 |
| J | AdaptiveInsertionController._click_in_trace | 77 | 89.4 | 694.2 | 962.9 |
| J | AdaptiveInsertionController._diagnose | 3 | 94.5 | 94.7 | 94.7 |
| J | AdaptiveInsertionController._record_contact | 3 | 12.8 | 15.2 | 15.3 |
| J | AdaptiveInsertionController._tilt_verdict | 77 | 6.4 | 110.8 | 113.5 |

## run2_gantry (loaded)

720 trials, 1996009 ticks, commit 4df8cae, 1-min load average per trial: min 39.3, mean 62.3, max 101.3. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.15/173.85, G 0.28/8.15, J 0.17/3.67, F 0.03/1.26, I 0.03/0.16.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 469173 | 47.0 | 234.3 | 1826.6 | 64288.0 | 437 (33) | 259.5 | 1465.9 | 27 (27) | 16.8 | 35.4 | 60.9 | 1276.8 | 34 | 1 | 0 | 1127 |
| C | ALIGN | 15558 | 34.5 | 212.9 | 1039.5 | 9010.2 | 11 (0) | 243.5 | 278.2 | 0 (0) | 11.9 | 43.8 | 60.6 | 143.5 | 0 | 0 | 0 | 15 |
| C | APPROACH | 106201 | 47.1 | 241.2 | 2066.0 | 18556.3 | 110 (4) | 213.9 | 301.3 | 3 (3) | 23.6 | 54.0 | 56.3 | 70.4 | 0 | 0 | 0 | 229 |
| C | DETECT | 18741 | 49.7 | 329.4 | 2156.0 | 8904.7 | 23 (2) | 638.9 | 676.3 | 2 (2) | 21.7 | 138.8 | 233.1 | 338.0 | 0 | 0 | 0 | 42 |
| C | FAILURE | 7575 | 50.3 | 247.3 | 1506.6 | 9715.7 | 3 (0) | 215.9 | 345.3 | 0 (0) | 24.8 | 32.2 | 58.0 | 59.4 | 0 | 0 | 0 | 3 |
| C | IDLE | 144 | 63.7 | 181.9 | 1270.0 | 1451.5 | 0 (0) | 199.2 | 202.5 | 0 (0) | 33.5 | 68.8 | 71.2 | 71.5 | 0 | 0 | 0 | 0 |
| C | INSERT | 147915 | 46.4 | 223.3 | 1795.6 | 23457.4 | 139 (13) | 231.0 | 390.8 | 10 (10) | 15.6 | 35.6 | 49.5 | 148.0 | 0 | 0 | 0 | 439 |
| C | RECOVER | 13797 | 49.7 | 300.8 | 2120.4 | 17272.8 | 15 (1) | 767.7 | 1465.9 | 1 (1) | 25.2 | 58.6 | 651.2 | 1276.8 | 34 | 1 | 0 | 7 |
| C | VERIFY | 159242 | 41.5 | 225.2 | 1738.1 | 64288.0 | 136 (13) | 231.1 | 452.9 | 11 (11) | 14.5 | 32.7 | 61.4 | 138.0 | 0 | 0 | 0 | 392 |
| G | ALL | 471297 | 47.2 | 207.9 | 1172.7 | 124798.5 | 200 (37) | 259.8 | 2001.1 | 30 (29) | 16.8 | 32.7 | 59.2 | 944.5 | 38 | 0 | 0 | 1117 |
| G | ALIGN | 16080 | 36.3 | 179.7 | 576.8 | 6927.5 | 1 (0) | 201.8 | 266.7 | 0 (0) | 12.0 | 42.3 | 56.8 | 167.8 | 0 | 0 | 0 | 12 |
| G | APPROACH | 106201 | 47.2 | 211.0 | 1145.0 | 124798.5 | 49 (5) | 207.4 | 380.7 | 4 (4) | 23.6 | 53.7 | 56.1 | 64.1 | 0 | 0 | 0 | 231 |
| G | DETECT | 18640 | 49.8 | 276.2 | 1174.7 | 4751.3 | 5 (0) | 609.4 | 688.4 | 0 (0) | 22.1 | 136.9 | 228.0 | 506.7 | 1 | 0 | 0 | 33 |
| G | FAILURE | 7693 | 49.5 | 221.9 | 730.6 | 15168.2 | 4 (1) | 297.5 | 238.5 | 1 (1) | 24.8 | 33.6 | 60.3 | 63.1 | 0 | 0 | 0 | 9 |
| G | IDLE | 144 | 66.0 | 257.1 | 1722.2 | 1964.1 | 0 (0) | 219.6 | 224.3 | 0 (0) | 36.0 | 44.1 | 70.9 | 75.3 | 0 | 0 | 0 | 0 |
| G | INSERT | 149017 | 46.6 | 200.4 | 1059.6 | 18268.0 | 58 (12) | 232.0 | 369.6 | 8 (8) | 15.7 | 26.5 | 49.5 | 162.1 | 0 | 0 | 0 | 429 |
| G | RECOVER | 14316 | 49.8 | 249.4 | 1917.3 | 13281.1 | 12 (2) | 1761.4 | 2001.1 | 3 (2) | 25.3 | 58.8 | 878.7 | 944.5 | 37 | 0 | 0 | 12 |
| G | VERIFY | 159206 | 41.4 | 202.6 | 1202.4 | 21004.7 | 71 (17) | 224.5 | 400.2 | 14 (14) | 14.6 | 30.6 | 40.1 | 108.3 | 0 | 0 | 0 | 391 |
| J | ALL | 441168 | 41.3 | 198.5 | 1166.2 | 79204.1 | 231 (30) | 229.0 | 478.3 | 25 (25) | 10.6 | 31.2 | 67.3 | 125.9 | 0 | 0 | 0 | 1139 |
| J | APPROACH | 107699 | 31.6 | 154.1 | 846.2 | 11988.6 | 42 (5) | 168.1 | 478.3 | 4 (4) | 9.1 | 21.7 | 23.1 | 31.2 | 0 | 0 | 0 | 234 |
| J | DESCEND | 60809 | 30.6 | 154.9 | 1028.1 | 12431.3 | 29 (5) | 205.7 | 469.4 | 5 (5) | 7.3 | 17.2 | 52.3 | 86.7 | 0 | 0 | 0 | 188 |
| J | FAILURE | 2723 | 32.7 | 160.6 | 645.3 | 1127.0 | 0 (0) | 232.2 | 175.9 | 0 (0) | 9.2 | 22.0 | 23.0 | 29.5 | 0 | 0 | 0 | 5 |
| J | IDLE | 144 | 48.7 | 503.7 | 4444.4 | 5067.5 | 1 (0) | 162.0 | 163.2 | 0 (0) | 17.5 | 26.2 | 34.4 | 35.3 | 0 | 0 | 0 | 0 |
| J | INSERT | 18607 | 36.3 | 175.2 | 723.4 | 7025.4 | 4 (0) | 303.4 | 348.8 | 0 (0) | 11.2 | 26.7 | 92.7 | 125.9 | 0 | 0 | 0 | 28 |
| J | RECOVER | 11023 | 52.4 | 239.3 | 1047.9 | 7738.6 | 6 (1) | 231.2 | 244.9 | 1 (1) | 27.1 | 30.7 | 63.6 | 78.4 | 0 | 0 | 0 | 10 |
| J | SPIRAL | 54875 | 34.7 | 199.2 | 2152.6 | 21404.9 | 58 (6) | 198.7 | 279.9 | 5 (5) | 10.5 | 24.2 | 25.6 | 31.9 | 0 | 0 | 0 | 137 |
| J | TARE | 10367 | 26.9 | 133.9 | 548.1 | 11116.2 | 5 (1) | 169.8 | 184.2 | 0 (0) | 5.5 | 33.1 | 40.2 | 77.9 | 0 | 0 | 0 | 18 |
| J | VERIFY | 174921 | 45.7 | 222.8 | 1164.3 | 79204.1 | 86 (12) | 242.8 | 370.5 | 10 (10) | 16.9 | 38.5 | 68.9 | 90.8 | 0 | 0 | 0 | 519 |
| F | ALL | 246429 | 33.3 | 178.6 | 1483.5 | 114434.7 | 170 (19) | 192.0 | 281.6 | 16 (16) | 9.1 | 21.9 | 27.0 | 76.3 | 0 | 0 | 0 | 600 |
| F | APPROACH | 107546 | 31.9 | 175.5 | 1526.1 | 114434.7 | 79 (8) | 178.2 | 281.6 | 8 (8) | 9.0 | 21.7 | 23.1 | 28.7 | 0 | 0 | 0 | 239 |
| F | DESCEND | 56011 | 31.0 | 162.9 | 1243.9 | 15818.3 | 34 (5) | 193.2 | 208.4 | 5 (5) | 7.2 | 13.6 | 21.6 | 37.5 | 0 | 0 | 0 | 184 |
| F | FAILURE | 2693 | 33.2 | 299.1 | 2015.3 | 17845.2 | 3 (0) | 221.6 | 228.0 | 0 (0) | 9.1 | 14.0 | 16.3 | 21.1 | 0 | 0 | 0 | 4 |
| F | IDLE | 144 | 46.4 | 185.8 | 609.6 | 679.1 | 0 (0) | 167.3 | 169.8 | 0 (0) | 13.5 | 23.3 | 27.7 | 28.3 | 0 | 0 | 0 | 0 |
| F | INSERT | 15952 | 36.5 | 186.3 | 1745.9 | 28974.1 | 13 (0) | 211.9 | 229.2 | 0 (0) | 11.1 | 26.8 | 28.2 | 63.2 | 0 | 0 | 0 | 23 |
| F | SPIRAL | 54875 | 35.5 | 191.9 | 1495.2 | 31736.5 | 37 (6) | 207.3 | 265.1 | 3 (3) | 10.4 | 24.4 | 25.3 | 33.7 | 0 | 0 | 0 | 142 |
| F | TARE | 9208 | 26.7 | 151.1 | 1280.9 | 5919.5 | 4 (0) | 163.6 | 232.5 | 0 (0) | 5.4 | 30.4 | 47.0 | 76.3 | 0 | 0 | 0 | 8 |
| I | ALL | 367942 | 33.8 | 182.9 | 1445.1 | 48087.6 | 264 (24) | 187.3 | 422.3 | 22 (22) | 9.4 | 17.7 | 26.8 | 75.2 | 0 | 0 | 0 | 689 |
| I | APPROACH | 107546 | 31.8 | 172.5 | 1517.0 | 23602.9 | 88 (8) | 181.4 | 260.5 | 8 (8) | 9.1 | 11.0 | 22.7 | 27.5 | 0 | 0 | 0 | 247 |
| I | DESCEND | 56011 | 31.2 | 177.3 | 1676.6 | 12822.3 | 48 (6) | 192.7 | 257.1 | 5 (5) | 7.2 | 17.0 | 21.0 | 35.6 | 0 | 0 | 0 | 175 |
| I | FAILURE | 8876 | 32.2 | 174.3 | 984.4 | 6619.5 | 4 (1) | 155.7 | 204.7 | 1 (1) | 9.1 | 10.6 | 22.1 | 23.6 | 0 | 0 | 0 | 6 |
| I | IDLE | 144 | 45.9 | 244.6 | 1364.4 | 1540.0 | 0 (0) | 204.4 | 214.4 | 0 (0) | 14.3 | 20.1 | 23.4 | 23.7 | 0 | 0 | 0 | 0 |
| I | INSERT | 15952 | 35.7 | 194.6 | 1515.3 | 17277.4 | 12 (0) | 183.4 | 206.5 | 0 (0) | 11.0 | 26.2 | 27.7 | 36.2 | 0 | 0 | 0 | 28 |
| I | SPIRAL | 54875 | 34.3 | 187.6 | 1295.9 | 17628.9 | 30 (5) | 190.7 | 422.3 | 5 (5) | 10.3 | 12.8 | 25.4 | 42.8 | 0 | 0 | 0 | 142 |
| I | TARE | 9208 | 26.8 | 142.9 | 793.8 | 16662.0 | 6 (0) | 170.4 | 226.5 | 0 (0) | 5.5 | 33.5 | 44.4 | 75.2 | 0 | 0 | 0 | 7 |
| I | VERIFY | 115330 | 34.6 | 192.0 | 1426.6 | 48087.6 | 76 (4) | 192.4 | 335.4 | 3 (3) | 9.8 | 23.3 | 27.0 | 48.3 | 0 | 0 | 0 | 84 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| C | mf_terminal_max_broken_latch | 2027 | 0 | 3.41 | RECOVER -> ALIGN | 1.277 | 1.340 | 1.277 | 0 | _plan_correction 1.249; update_blocked 0.480; best_probe 0.373 |
| G | mf_spread | 2026 | 0 | 3.454 | RECOVER -> ALIGN | 0.944 | 2.631 | 1.864 | 0 | _plan_correction 2.571; update_blocked 0.754; entry_probability_at 0.710 |
| G | mf_terminal_max_broken_latch | 2027 | 0 | 3.41 | RECOVER -> ALIGN | 0.938 | 1.816 | 1.826 | 0 | _plan_correction 1.725; update_blocked 0.531; _contact_prior_update 0.504 |
| G | mf_stubbed_terminal | 2026 | 0 | 3.974 | RECOVER -> ALIGN | 0.937 | 1.021 | 1.026 | 0 | _plan_correction 0.978; _contact_prior_update 0.331; update_blocked 0.304 |
| G | mf_noise_1mm | 2026 | 0 | 4.422 | RECOVER -> ALIGN | 0.911 | 1.064 | 1.069 | 0 | _plan_correction 1.022; update_blocked 0.376; _contact_prior_update 0.318 |
| G | noise_2mm | 2027 | 0 | 4.28 | RECOVER -> ALIGN | 0.902 | 1.100 | 1.105 | 0 | _plan_correction 1.056; update_blocked 0.390; _contact_prior_update 0.294 |
| G | mf_moderate | 2027 | 0 | 3.448 | RECOVER -> ALIGN | 0.901 | 1.965 | 1.920 | 0 | _plan_correction 1.850; update_blocked 0.575; _contact_prior_update 0.475 |
| G | mf_broken_latch | 2026 | 0 | 3.398 | RECOVER -> ALIGN | 0.901 | 2.010 | 1.964 | 0 | _plan_correction 1.910; update_blocked 0.577; _contact_prior_update 0.539 |
| G | mf_moderate | 2027 | 0 | 5.266 | RECOVER -> ALIGN | 0.901 | 2.003 | 1.806 | 0 | _plan_correction 1.903; _contact_prior_update 0.662; update_blocked 0.447 |
| G | mf_stubbed_terminal | 2027 | 1 | 3.368 | RECOVER -> ALIGN | 0.893 | 2.146 | 1.977 | 0 | _plan_correction 2.044; update_blocked 0.667; _contact_prior_update 0.577 |
| G | mf_wrong_polarization | 2026 | 0 | 7.812 | RECOVER -> ALIGN | 0.893 | 0.989 | 0.995 | 0 | _plan_correction 0.947; update_blocked 0.339; _contact_prior_update 0.249 |
| G | mf_terminal_max | 2026 | 1 | 3.406 | RECOVER -> ALIGN | 0.893 | 0.959 | 0.964 | 0 | _plan_correction 0.917; update_blocked 0.311; _contact_prior_update 0.266 |
| G | mf_noise_1mm | 2027 | 0 | 4.276 | RECOVER -> ALIGN | 0.888 | 0.991 | 0.996 | 0 | _plan_correction 0.948; update_blocked 0.305; _contact_prior_update 0.282 |
| G | mf_terminal_max_broken_latch | 2026 | 1 | 4.192 | RECOVER -> ALIGN | 0.887 | 0.963 | 0.968 | 0 | _plan_correction 0.923; update_blocked 0.324; _contact_prior_update 0.257 |
| G | mf_wrong_polarization | 2026 | 0 | 3.38 | RECOVER -> ALIGN | 0.884 | 0.909 | 0.914 | 0 | _plan_correction 0.868; update_blocked 0.273; _contact_prior_update 0.257 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 75 | 110.8 | 663.6 | 910.3 |
| C | AdaptiveInsertionController._begin_verify | 162 | 70.9 | 708.9 | 915.5 |
| C | AdaptiveInsertionController._click_in_trace | 75 | 48.9 | 385.2 | 414.0 |
| C | AdaptiveInsertionController._diagnose | 209 | 101.6 | 442.3 | 958.0 |
| C | AdaptiveInsertionController._plan_correction | 60 | 646.9 | 3730.0 | 6803.3 |
| C | AdaptiveInsertionController._record_contact | 209 | 13.6 | 119.3 | 542.0 |
| C | AdaptiveInsertionController._tilt_verdict | 75 | 34.1 | 242.5 | 585.5 |
| C | HoleLocalizer.best_probe | 34 | 151.5 | 443.3 | 478.1 |
| C | HoleLocalizer.entry_probability_at | 34 | 128.7 | 356.3 | 360.7 |
| C | HoleLocalizer.update_blocked | 34 | 325.0 | 4363.2 | 6161.1 |
| C | HoleLocalizer.update_entered | 2 | 39.9 | 53.8 | 54.1 |
| G | AdaptiveInsertionController._begin_latch_verify | 75 | 114.4 | 1035.6 | 2831.3 |
| G | AdaptiveInsertionController._begin_verify | 162 | 68.8 | 350.9 | 2833.7 |
| G | AdaptiveInsertionController._click_in_trace | 75 | 51.7 | 883.0 | 2676.8 |
| G | AdaptiveInsertionController._diagnose | 213 | 137.8 | 572.3 | 1464.2 |
| G | AdaptiveInsertionController._plan_correction | 63 | 908.8 | 2250.4 | 2570.7 |
| G | AdaptiveInsertionController._record_contact | 213 | 13.3 | 59.9 | 126.3 |
| G | AdaptiveInsertionController._tilt_verdict | 75 | 41.2 | 135.1 | 140.8 |
| G | AdaptiveLearnedController._contact_prior_update | 37 | 326.7 | 667.4 | 670.4 |
| G | ContactLikelihood.localizer_log_term | 37 | 272.7 | 563.2 | 564.8 |
| G | ContactLikelihood.mixture_mean_mm | 37 | 28.3 | 70.0 | 74.2 |
| G | HoleLocalizer.best_probe | 37 | 168.1 | 474.8 | 479.9 |
| G | HoleLocalizer.entry_probability_at | 37 | 135.9 | 595.1 | 709.8 |
| G | HoleLocalizer.update_blocked | 37 | 375.8 | 722.9 | 754.2 |
| G | HoleLocalizer.update_entered | 2 | 26.9 | 28.8 | 28.9 |
| G | HoleLocalizer.update_log_term | 37 | 3.9 | 20.5 | 24.1 |
| J | AdaptiveInsertionController._begin_latch_verify | 72 | 54.1 | 459.7 | 723.5 |
| J | AdaptiveInsertionController._begin_verify | 151 | 43.4 | 155.4 | 728.6 |
| J | AdaptiveInsertionController._click_in_trace | 72 | 17.3 | 113.2 | 127.4 |
| J | AdaptiveInsertionController._tilt_verdict | 72 | 5.9 | 116.0 | 169.5 |

## run4_arm_quiet (not loaded)

180 trials, 787178 ticks, commit 4df8cae, 1-min load average per trial: min 6.8, mean 7.6, max 8.6. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.13/128.11, G 0.23/1.62, J 0.14/0.24, F 0.02/0.05, I 0.02/0.06.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 194126 | 43.5 | 112.2 | 232.4 | 11224.8 | 5 (3) | 200.3 | 1170.6 | 3 (3) | 16.8 | 26.8 | 35.2 | 614.1 | 17 | 0 | 0 | 135 |
| C | ALIGN | 4894 | 32.7 | 98.1 | 146.3 | 5866.7 | 1 (1) | 146.4 | 313.0 | 1 (1) | 11.4 | 32.5 | 55.3 | 63.4 | 0 | 0 | 0 | 1 |
| C | APPROACH | 26566 | 46.2 | 109.0 | 149.1 | 585.5 | 0 (0) | 162.8 | 237.6 | 0 (0) | 22.9 | 24.5 | 25.5 | 27.7 | 0 | 0 | 0 | 18 |
| C | DETECT | 13176 | 52.0 | 148.1 | 343.3 | 7460.6 | 1 (0) | 345.5 | 640.8 | 0 (0) | 23.9 | 27.6 | 217.0 | 324.2 | 0 | 0 | 0 | 16 |
| C | FAILURE | 1985 | 48.8 | 111.9 | 172.2 | 286.7 | 0 (0) | 191.3 | 189.8 | 0 (0) | 23.7 | 24.8 | 26.2 | 26.3 | 0 | 0 | 0 | 2 |
| C | IDLE | 36 | 62.0 | 139.0 | 140.1 | 140.2 | 0 (0) | 154.4 | 154.4 | 0 (0) | 32.6 | 35.6 | 35.7 | 35.7 | 0 | 0 | 0 | 0 |
| C | INSERT | 90652 | 38.6 | 104.7 | 178.1 | 1466.8 | 0 (0) | 165.4 | 225.3 | 0 (0) | 15.0 | 22.6 | 26.7 | 101.3 | 0 | 0 | 0 | 58 |
| C | RECOVER | 4856 | 48.5 | 118.9 | 696.7 | 2976.3 | 1 (0) | 701.3 | 1170.6 | 0 (0) | 24.2 | 27.9 | 592.3 | 614.1 | 17 | 0 | 0 | 4 |
| C | VERIFY | 51961 | 44.2 | 114.6 | 184.1 | 11224.8 | 2 (2) | 182.6 | 240.8 | 2 (2) | 17.7 | 27.1 | 32.9 | 136.0 | 0 | 0 | 0 | 36 |
| G | ALL | 187878 | 44.7 | 118.0 | 252.5 | 5381.9 | 8 (4) | 204.2 | 1533.4 | 4 (4) | 17.7 | 27.4 | 37.4 | 788.3 | 11 | 0 | 0 | 134 |
| G | ALIGN | 4149 | 33.4 | 110.4 | 161.9 | 298.4 | 0 (0) | 151.1 | 294.3 | 0 (0) | 11.7 | 37.6 | 55.8 | 65.5 | 0 | 0 | 0 | 1 |
| G | APPROACH | 26566 | 47.1 | 112.7 | 168.6 | 2210.5 | 1 (0) | 165.2 | 236.8 | 0 (0) | 23.2 | 24.8 | 27.1 | 30.1 | 0 | 0 | 0 | 18 |
| G | DETECT | 10123 | 54.8 | 185.7 | 539.0 | 5381.9 | 2 (0) | 360.0 | 573.2 | 0 (0) | 25.0 | 39.4 | 232.8 | 284.3 | 0 | 0 | 0 | 13 |
| G | FAILURE | 1985 | 50.6 | 129.2 | 173.5 | 280.6 | 0 (0) | 168.3 | 169.8 | 0 (0) | 24.3 | 25.8 | 27.4 | 27.5 | 0 | 0 | 0 | 1 |
| G | IDLE | 36 | 62.8 | 159.0 | 169.8 | 171.0 | 0 (0) | 183.8 | 185.0 | 0 (0) | 35.5 | 38.0 | 38.3 | 38.3 | 0 | 0 | 0 | 0 |
| G | INSERT | 87980 | 39.2 | 108.5 | 188.7 | 4268.4 | 2 (1) | 169.3 | 222.8 | 1 (1) | 15.2 | 23.0 | 28.7 | 118.0 | 0 | 0 | 0 | 56 |
| G | RECOVER | 3933 | 50.1 | 129.6 | 903.3 | 4723.5 | 2 (2) | 909.2 | 1533.4 | 2 (2) | 25.0 | 28.2 | 771.9 | 788.3 | 11 | 0 | 0 | 3 |
| G | VERIFY | 53106 | 45.3 | 114.6 | 209.1 | 3975.6 | 1 (1) | 192.9 | 238.5 | 1 (1) | 18.0 | 27.3 | 34.4 | 132.6 | 0 | 0 | 0 | 42 |
| J | ALL | 175076 | 34.9 | 111.7 | 174.1 | 6129.3 | 5 (4) | 176.6 | 275.5 | 4 (4) | 9.2 | 29.1 | 30.5 | 245.5 | 0 | 0 | 0 | 112 |
| J | APPROACH | 27067 | 31.5 | 78.3 | 115.8 | 3899.1 | 2 (2) | 122.7 | 176.7 | 2 (2) | 9.0 | 9.6 | 10.7 | 14.0 | 0 | 0 | 0 | 10 |
| J | DESCEND | 60940 | 29.9 | 75.2 | 128.0 | 3273.2 | 1 (1) | 132.4 | 270.2 | 1 (1) | 7.2 | 9.0 | 11.7 | 84.7 | 0 | 0 | 0 | 38 |
| J | DETECT | 25 | 37.7 | 216.2 | 265.4 | 270.8 | 0 (0) | 270.0 | 275.5 | 0 (0) | 14.5 | 190.4 | 240.0 | 245.5 | 0 | 0 | 0 | 0 |
| J | FAILURE | 1234 | 32.0 | 76.9 | 96.6 | 100.0 | 0 (0) | 111.4 | 115.9 | 0 (0) | 9.1 | 9.5 | 10.9 | 11.9 | 0 | 0 | 0 | 0 |
| J | IDLE | 36 | 45.4 | 87.3 | 87.4 | 87.4 | 0 (0) | 100.6 | 100.6 | 0 (0) | 17.3 | 18.8 | 18.9 | 19.0 | 0 | 0 | 0 | 0 |
| J | INSERT | 13816 | 34.9 | 94.4 | 251.7 | 4360.8 | 1 (1) | 256.9 | 204.1 | 1 (1) | 10.9 | 23.6 | 105.9 | 201.0 | 0 | 0 | 0 | 19 |
| J | RECOVER | 3346 | 53.0 | 125.7 | 268.7 | 824.3 | 0 (0) | 272.8 | 210.8 | 0 (0) | 27.0 | 28.7 | 44.3 | 46.6 | 0 | 0 | 0 | 6 |
| J | SPIRAL | 6665 | 37.5 | 90.9 | 155.7 | 372.0 | 0 (0) | 170.0 | 177.2 | 0 (0) | 12.4 | 13.0 | 18.0 | 20.0 | 0 | 0 | 0 | 5 |
| J | TARE | 2683 | 26.2 | 65.4 | 113.4 | 144.7 | 0 (0) | 119.2 | 155.2 | 0 (0) | 5.3 | 29.1 | 32.4 | 34.9 | 0 | 0 | 0 | 0 |
| J | VERIFY | 59264 | 48.4 | 124.2 | 187.9 | 6129.3 | 1 (0) | 191.8 | 267.4 | 0 (0) | 20.2 | 29.5 | 34.7 | 136.6 | 0 | 0 | 0 | 34 |
| F | ALL | 96804 | 30.7 | 78.8 | 118.1 | 1007.0 | 0 (0) | 131.3 | 175.6 | 0 (0) | 7.5 | 12.8 | 13.6 | 31.0 | 0 | 0 | 0 | 64 |
| F | APPROACH | 26907 | 31.3 | 75.4 | 102.3 | 307.6 | 0 (0) | 117.3 | 175.6 | 0 (0) | 8.9 | 9.6 | 9.9 | 12.3 | 0 | 0 | 0 | 16 |
| F | DESCEND | 48381 | 29.0 | 71.4 | 119.1 | 1007.0 | 0 (0) | 131.5 | 155.6 | 0 (0) | 7.1 | 8.8 | 10.7 | 16.4 | 0 | 0 | 0 | 33 |
| F | FAILURE | 752 | 32.6 | 75.9 | 111.9 | 118.9 | 0 (0) | 121.0 | 141.0 | 0 (0) | 8.9 | 9.3 | 10.2 | 10.4 | 0 | 0 | 0 | 0 |
| F | IDLE | 36 | 42.9 | 94.3 | 96.0 | 96.2 | 0 (0) | 110.7 | 111.0 | 0 (0) | 12.4 | 13.7 | 13.9 | 13.9 | 0 | 0 | 0 | 0 |
| F | INSERT | 11745 | 34.5 | 82.2 | 133.0 | 330.0 | 0 (0) | 145.1 | 166.7 | 0 (0) | 10.8 | 12.5 | 14.3 | 19.7 | 0 | 0 | 0 | 9 |
| F | SPIRAL | 6665 | 37.5 | 91.1 | 123.0 | 379.1 | 0 (0) | 141.2 | 148.9 | 0 (0) | 12.5 | 13.3 | 17.2 | 21.3 | 0 | 0 | 0 | 4 |
| F | TARE | 2318 | 25.7 | 62.2 | 109.9 | 123.5 | 0 (0) | 117.0 | 136.8 | 0 (0) | 5.3 | 22.9 | 28.8 | 31.0 | 0 | 0 | 0 | 2 |
| I | ALL | 133294 | 32.3 | 81.4 | 123.9 | 4879.5 | 3 (3) | 134.8 | 208.6 | 3 (3) | 9.0 | 12.9 | 13.5 | 34.4 | 0 | 0 | 0 | 83 |
| I | APPROACH | 26907 | 31.3 | 75.6 | 107.3 | 3178.3 | 1 (1) | 118.8 | 208.6 | 1 (1) | 8.9 | 9.6 | 9.9 | 13.0 | 0 | 0 | 0 | 14 |
| I | DESCEND | 48381 | 29.2 | 73.0 | 130.3 | 2984.1 | 1 (1) | 131.9 | 146.4 | 1 (1) | 7.0 | 8.7 | 10.9 | 15.0 | 0 | 0 | 0 | 36 |
| I | FAILURE | 2167 | 32.8 | 77.1 | 98.9 | 121.2 | 0 (0) | 114.8 | 129.9 | 0 (0) | 9.0 | 9.6 | 10.4 | 11.3 | 0 | 0 | 0 | 0 |
| I | IDLE | 36 | 42.5 | 102.1 | 106.7 | 107.3 | 0 (0) | 125.1 | 125.8 | 0 (0) | 13.6 | 15.7 | 15.8 | 15.8 | 0 | 0 | 0 | 0 |
| I | INSERT | 11745 | 34.6 | 84.9 | 131.6 | 4879.5 | 1 (1) | 142.7 | 181.7 | 1 (1) | 10.8 | 11.7 | 14.8 | 19.2 | 0 | 0 | 0 | 8 |
| I | SPIRAL | 6665 | 37.4 | 92.6 | 126.7 | 397.5 | 0 (0) | 142.3 | 176.1 | 0 (0) | 12.5 | 13.3 | 18.0 | 18.9 | 0 | 0 | 0 | 2 |
| I | TARE | 2318 | 25.7 | 65.1 | 112.5 | 119.6 | 0 (0) | 123.0 | 128.6 | 0 (0) | 5.3 | 24.3 | 31.7 | 34.4 | 0 | 0 | 0 | 0 |
| I | VERIFY | 35075 | 33.8 | 84.6 | 132.8 | 336.8 | 0 (0) | 140.5 | 177.8 | 0 (0) | 9.5 | 11.5 | 12.0 | 19.0 | 0 | 0 | 0 | 23 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| G | mf_noise_1mm | 2026 | 0 | 5.982 | RECOVER -> ALIGN | 0.788 | 0.862 | 0.867 | 0 | _plan_correction 0.822; update_blocked 0.352; _contact_prior_update 0.148 |
| G | mf_spread | 2026 | 0 | 5.3 | RECOVER -> ALIGN | 0.786 | 0.814 | 0.819 | 0 | _plan_correction 0.771; update_blocked 0.294; _contact_prior_update 0.146 |
| G | mf_wrong_polarization | 2026 | 0 | 5.16 | RECOVER -> ALIGN | 0.778 | 0.900 | 0.906 | 0 | _plan_correction 0.855; update_blocked 0.337; _contact_prior_update 0.159 |
| G | mf_broken_latch | 2026 | 0 | 5.302 | RECOVER -> ALIGN | 0.778 | 0.803 | 0.808 | 0 | _plan_correction 0.761; update_blocked 0.292; _contact_prior_update 0.141 |
| G | mf_stubbed_terminal | 2026 | 0 | 5.25 | RECOVER -> ALIGN | 0.771 | 0.797 | 0.802 | 0 | _plan_correction 0.755; update_blocked 0.290; _contact_prior_update 0.142 |
| G | mf_wrong_polarization | 2026 | 0 | 9.172 | RECOVER -> ALIGN | 0.761 | 1.522 | 1.533 | 0 | _plan_correction 1.429; update_blocked 0.447; best_probe 0.302 |
| G | mf_terminal_min | 2026 | 0 | 4.328 | RECOVER -> ALIGN | 0.755 | 0.942 | 0.947 | 0 | _plan_correction 0.895; update_blocked 0.349; _contact_prior_update 0.163 |
| G | generalization_tight | 2026 | 0 | 4.464 | RECOVER -> ALIGN | 0.755 | 0.820 | 0.825 | 0 | _plan_correction 0.781; update_blocked 0.282; _contact_prior_update 0.162 |
| G | generalization_tight | 2026 | 0 | 5.954 | RECOVER -> ALIGN | 0.744 | 0.799 | 0.804 | 0 | _plan_correction 0.758; update_blocked 0.283; _contact_prior_update 0.150 |
| G | mf_terminal_min | 2026 | 0 | 7.876 | RECOVER -> ALIGN | 0.730 | 0.789 | 0.794 | 0 | _plan_correction 0.748; update_blocked 0.286; _contact_prior_update 0.143 |
| G | generalization_tight | 2026 | 0 | 7.442 | RECOVER -> ALIGN | 0.694 | 0.850 | 0.855 | 0 | _plan_correction 0.811; update_blocked 0.316; best_probe 0.156 |
| C | mf_broken_latch | 2026 | 0 | 5.302 | RECOVER -> ALIGN | 0.614 | 2.976 | 0.973 | 0 | _plan_correction 2.917; best_probe 0.329; update_blocked 0.277 |
| C | mf_terminal_min | 2026 | 0 | 8.534 | RECOVER -> ALIGN | 0.613 | 0.654 | 0.659 | 0 | _plan_correction 0.613; update_blocked 0.282; best_probe 0.147 |
| C | mf_terminal_min | 2026 | 0 | 4.328 | RECOVER -> ALIGN | 0.613 | 0.641 | 0.646 | 0 | _plan_correction 0.601; update_blocked 0.281; best_probe 0.137 |
| C | mf_spread | 2026 | 0 | 5.3 | RECOVER -> ALIGN | 0.607 | 0.638 | 0.643 | 0 | _plan_correction 0.598; update_blocked 0.291; best_probe 0.133 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 21 | 162.7 | 414.8 | 430.9 |
| C | AdaptiveInsertionController._begin_verify | 43 | 51.1 | 295.7 | 352.0 |
| C | AdaptiveInsertionController._click_in_trace | 21 | 99.0 | 335.3 | 360.9 |
| C | AdaptiveInsertionController._diagnose | 66 | 98.7 | 353.7 | 381.8 |
| C | AdaptiveInsertionController._plan_correction | 25 | 598.7 | 2475.9 | 2917.0 |
| C | AdaptiveInsertionController._record_contact | 66 | 12.4 | 24.9 | 25.8 |
| C | AdaptiveInsertionController._tilt_verdict | 21 | 31.9 | 63.2 | 63.9 |
| C | HoleLocalizer.best_probe | 17 | 146.7 | 321.6 | 329.4 |
| C | HoleLocalizer.entry_probability_at | 17 | 117.6 | 215.4 | 223.3 |
| C | HoleLocalizer.update_blocked | 17 | 281.4 | 437.2 | 437.8 |
| C | HoleLocalizer.update_entered | 1 | 26.6 | 26.6 | 26.6 |
| G | AdaptiveInsertionController._begin_latch_verify | 21 | 168.1 | 444.1 | 452.3 |
| G | AdaptiveInsertionController._begin_verify | 44 | 51.6 | 435.5 | 453.0 |
| G | AdaptiveInsertionController._click_in_trace | 21 | 101.0 | 378.4 | 385.9 |
| G | AdaptiveInsertionController._diagnose | 60 | 93.8 | 250.7 | 321.3 |
| G | AdaptiveInsertionController._plan_correction | 19 | 754.8 | 1332.6 | 1428.7 |
| G | AdaptiveInsertionController._record_contact | 60 | 12.4 | 30.0 | 33.5 |
| G | AdaptiveInsertionController._tilt_verdict | 21 | 31.7 | 38.0 | 38.0 |
| G | AdaptiveLearnedController._contact_prior_update | 11 | 147.9 | 272.1 | 284.2 |
| G | ContactPrior.localizer_term | 11 | 50.0 | 88.5 | 91.8 |
| G | HoleLocalizer.best_probe | 11 | 141.3 | 287.9 | 302.5 |
| G | HoleLocalizer.entry_probability_at | 11 | 120.5 | 227.4 | 235.5 |
| G | HoleLocalizer.update_blocked | 11 | 293.7 | 437.1 | 446.6 |
| G | HoleLocalizer.update_entered | 1 | 24.4 | 24.4 | 24.4 |
| G | HoleLocalizer.update_gaussian | 11 | 81.1 | 151.2 | 158.2 |
| J | AdaptiveInsertionController._begin_latch_verify | 19 | 101.4 | 321.4 | 336.0 |
| J | AdaptiveInsertionController._begin_verify | 40 | 52.4 | 305.3 | 336.7 |
| J | AdaptiveInsertionController._click_in_trace | 19 | 60.7 | 281.3 | 295.5 |
| J | AdaptiveInsertionController._diagnose | 1 | 89.0 | 89.0 | 89.0 |
| J | AdaptiveInsertionController._record_contact | 1 | 11.8 | 11.8 | 11.8 |
| J | AdaptiveInsertionController._tilt_verdict | 19 | 4.8 | 43.2 | 44.0 |

## run4_gantry_quiet (not loaded)

180 trials, 500233 ticks, commit 4df8cae, 1-min load average per trial: min 7.2, mean 7.9, max 9.2. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.11/120.08, G 0.20/1.75, J 0.11/0.29, F 0.02/0.06, I 0.01/0.04.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 121906 | 43.0 | 106.3 | 205.1 | 4780.5 | 7 (7) | 195.0 | 1192.4 | 7 (7) | 15.8 | 26.1 | 36.2 | 620.7 | 11 | 0 | 0 | 275 |
| C | ALIGN | 4129 | 32.0 | 96.3 | 140.1 | 256.2 | 0 (0) | 144.4 | 186.9 | 0 (0) | 11.4 | 36.3 | 42.7 | 48.6 | 0 | 0 | 0 | 3 |
| C | APPROACH | 26566 | 44.5 | 104.4 | 144.9 | 3163.4 | 1 (1) | 158.4 | 190.7 | 1 (1) | 22.7 | 24.1 | 25.0 | 27.0 | 0 | 0 | 0 | 62 |
| C | DETECT | 5381 | 46.8 | 160.8 | 332.4 | 871.2 | 0 (0) | 337.7 | 544.8 | 0 (0) | 21.4 | 113.9 | 202.6 | 209.3 | 0 | 0 | 0 | 5 |
| C | FAILURE | 2314 | 47.0 | 108.7 | 139.6 | 207.9 | 0 (0) | 154.4 | 165.0 | 0 (0) | 24.0 | 25.2 | 26.2 | 26.6 | 0 | 0 | 0 | 0 |
| C | IDLE | 36 | 58.5 | 106.0 | 117.1 | 118.4 | 0 (0) | 130.5 | 131.7 | 0 (0) | 30.8 | 32.4 | 32.5 | 32.5 | 0 | 0 | 0 | 0 |
| C | INSERT | 38841 | 37.9 | 102.8 | 191.9 | 4780.5 | 5 (5) | 182.4 | 227.2 | 5 (5) | 14.9 | 21.7 | 26.0 | 135.6 | 0 | 0 | 0 | 106 |
| C | RECOVER | 4489 | 47.4 | 112.7 | 644.3 | 1183.0 | 0 (0) | 648.9 | 1192.4 | 0 (0) | 24.5 | 26.3 | 592.8 | 620.7 | 11 | 0 | 0 | 4 |
| C | VERIFY | 40150 | 37.4 | 107.7 | 158.8 | 3424.1 | 1 (1) | 172.8 | 186.6 | 1 (1) | 13.7 | 26.6 | 29.9 | 83.7 | 0 | 0 | 0 | 95 |
| G | ALL | 120693 | 43.6 | 108.7 | 218.4 | 7694.1 | 8 (8) | 219.4 | 970.2 | 8 (8) | 16.1 | 26.8 | 35.8 | 868.7 | 9 | 0 | 0 | 271 |
| G | ALIGN | 3917 | 32.7 | 99.1 | 138.7 | 236.7 | 0 (0) | 148.6 | 201.0 | 0 (0) | 11.5 | 36.9 | 42.5 | 49.8 | 0 | 0 | 0 | 3 |
| G | APPROACH | 26566 | 45.2 | 106.3 | 150.6 | 6290.3 | 2 (2) | 160.0 | 226.7 | 2 (2) | 22.8 | 24.3 | 25.3 | 26.5 | 0 | 0 | 0 | 58 |
| G | DETECT | 5482 | 47.3 | 160.1 | 366.4 | 509.1 | 0 (0) | 355.9 | 518.3 | 0 (0) | 21.5 | 37.9 | 203.6 | 213.9 | 0 | 0 | 0 | 3 |
| G | FAILURE | 2315 | 47.2 | 111.9 | 144.5 | 152.2 | 0 (0) | 158.6 | 167.3 | 0 (0) | 23.9 | 24.9 | 25.9 | 27.0 | 0 | 0 | 0 | 0 |
| G | IDLE | 36 | 61.6 | 126.5 | 129.9 | 130.3 | 0 (0) | 145.3 | 145.7 | 0 (0) | 34.1 | 36.0 | 36.1 | 36.1 | 0 | 0 | 0 | 0 |
| G | INSERT | 38163 | 38.4 | 104.9 | 233.9 | 3915.2 | 2 (2) | 217.8 | 236.3 | 2 (2) | 15.2 | 22.0 | 30.0 | 126.9 | 0 | 0 | 0 | 113 |
| G | RECOVER | 4104 | 47.5 | 118.2 | 887.9 | 965.3 | 0 (0) | 892.8 | 970.2 | 0 (0) | 24.5 | 26.1 | 818.2 | 868.7 | 9 | 0 | 0 | 1 |
| G | VERIFY | 40110 | 37.9 | 109.8 | 170.6 | 7694.1 | 4 (4) | 181.5 | 210.7 | 4 (4) | 13.8 | 27.0 | 30.8 | 83.9 | 0 | 0 | 0 | 93 |
| J | ALL | 107590 | 35.3 | 108.5 | 165.8 | 8859.2 | 6 (6) | 177.4 | 288.5 | 6 (6) | 9.9 | 28.6 | 32.5 | 176.0 | 0 | 0 | 0 | 293 |
| J | APPROACH | 27166 | 30.4 | 74.2 | 130.9 | 3635.1 | 1 (1) | 135.3 | 153.1 | 1 (1) | 8.8 | 9.4 | 10.5 | 14.6 | 0 | 0 | 0 | 67 |
| J | DESCEND | 22140 | 29.8 | 73.1 | 139.8 | 4738.1 | 1 (1) | 151.2 | 187.1 | 1 (1) | 7.2 | 9.0 | 12.5 | 70.2 | 0 | 0 | 0 | 75 |
| J | FAILURE | 799 | 31.8 | 70.8 | 181.6 | 351.8 | 0 (0) | 198.1 | 158.2 | 0 (0) | 8.8 | 9.3 | 10.0 | 10.2 | 0 | 0 | 0 | 1 |
| J | IDLE | 36 | 44.7 | 86.2 | 86.7 | 86.7 | 0 (0) | 100.9 | 101.0 | 0 (0) | 15.2 | 16.9 | 17.0 | 17.0 | 0 | 0 | 0 | 0 |
| J | INSERT | 4272 | 34.3 | 86.1 | 132.8 | 271.7 | 0 (0) | 140.8 | 288.5 | 0 (0) | 10.9 | 12.3 | 78.9 | 176.0 | 0 | 0 | 0 | 2 |
| J | RECOVER | 2419 | 49.8 | 112.7 | 256.8 | 4876.5 | 1 (1) | 265.2 | 204.3 | 1 (1) | 26.0 | 27.0 | 42.9 | 44.3 | 0 | 0 | 0 | 3 |
| J | SPIRAL | 4929 | 33.0 | 81.2 | 126.0 | 457.3 | 0 (0) | 140.5 | 157.0 | 0 (0) | 10.1 | 10.7 | 14.0 | 17.9 | 0 | 0 | 0 | 8 |
| J | TARE | 2622 | 25.6 | 71.5 | 123.1 | 239.8 | 0 (0) | 130.9 | 131.4 | 0 (0) | 5.3 | 25.9 | 30.9 | 32.6 | 0 | 0 | 0 | 4 |
| J | VERIFY | 43207 | 40.9 | 116.7 | 176.6 | 8859.2 | 3 (3) | 190.2 | 209.5 | 3 (3) | 16.0 | 29.0 | 34.8 | 75.1 | 0 | 0 | 0 | 133 |
| F | ALL | 60099 | 30.2 | 75.5 | 117.8 | 9545.9 | 3 (3) | 130.8 | 161.9 | 3 (3) | 8.6 | 11.0 | 13.0 | 30.1 | 0 | 0 | 0 | 151 |
| F | APPROACH | 27127 | 30.2 | 73.3 | 113.0 | 3198.9 | 2 (2) | 121.1 | 161.9 | 2 (2) | 8.7 | 9.3 | 9.7 | 12.3 | 0 | 0 | 0 | 59 |
| F | DESCEND | 21134 | 29.5 | 70.9 | 120.2 | 9545.9 | 1 (1) | 129.7 | 152.9 | 1 (1) | 7.1 | 8.8 | 11.0 | 16.2 | 0 | 0 | 0 | 76 |
| F | FAILURE | 789 | 31.0 | 77.7 | 155.3 | 285.5 | 0 (0) | 164.2 | 130.6 | 0 (0) | 8.8 | 9.2 | 9.6 | 9.7 | 0 | 0 | 0 | 1 |
| F | IDLE | 36 | 41.4 | 92.6 | 92.6 | 92.6 | 0 (0) | 107.6 | 107.7 | 0 (0) | 11.4 | 13.5 | 13.7 | 13.7 | 0 | 0 | 0 | 0 |
| F | INSERT | 3706 | 34.0 | 83.2 | 115.5 | 278.0 | 0 (0) | 132.5 | 143.8 | 0 (0) | 10.7 | 11.5 | 13.7 | 18.4 | 0 | 0 | 0 | 1 |
| F | SPIRAL | 4929 | 32.9 | 82.2 | 231.5 | 326.6 | 0 (0) | 235.0 | 153.9 | 0 (0) | 10.0 | 10.6 | 12.9 | 17.4 | 0 | 0 | 0 | 12 |
| F | TARE | 2378 | 25.4 | 60.5 | 103.9 | 120.8 | 0 (0) | 113.6 | 137.6 | 0 (0) | 5.2 | 21.1 | 26.3 | 30.1 | 0 | 0 | 0 | 2 |
| I | ALL | 89945 | 31.2 | 77.2 | 122.1 | 5899.9 | 5 (5) | 132.5 | 177.8 | 5 (5) | 8.8 | 11.1 | 18.8 | 31.0 | 0 | 0 | 0 | 180 |
| I | APPROACH | 27127 | 30.0 | 71.0 | 104.2 | 3007.8 | 2 (2) | 119.7 | 145.0 | 2 (2) | 8.7 | 9.3 | 9.6 | 11.6 | 0 | 0 | 0 | 65 |
| I | DESCEND | 21134 | 29.4 | 71.8 | 123.9 | 5899.9 | 2 (2) | 131.5 | 155.5 | 2 (2) | 7.1 | 8.7 | 11.2 | 15.8 | 0 | 0 | 0 | 78 |
| I | FAILURE | 2316 | 30.7 | 74.2 | 95.2 | 134.5 | 0 (0) | 111.7 | 149.1 | 0 (0) | 8.8 | 9.3 | 10.2 | 10.7 | 0 | 0 | 0 | 0 |
| I | IDLE | 36 | 40.8 | 83.6 | 84.3 | 84.4 | 0 (0) | 98.0 | 98.1 | 0 (0) | 12.1 | 13.8 | 13.8 | 13.8 | 0 | 0 | 0 | 0 |
| I | INSERT | 3706 | 34.0 | 80.2 | 191.8 | 4193.8 | 1 (1) | 197.0 | 149.5 | 1 (1) | 10.7 | 11.7 | 14.6 | 17.6 | 0 | 0 | 0 | 4 |
| I | SPIRAL | 4929 | 32.5 | 81.2 | 118.6 | 309.4 | 0 (0) | 130.1 | 142.5 | 0 (0) | 10.0 | 12.5 | 23.4 | 24.2 | 0 | 0 | 0 | 10 |
| I | TARE | 2378 | 25.2 | 61.8 | 121.0 | 339.3 | 0 (0) | 132.5 | 145.2 | 0 (0) | 5.2 | 22.9 | 30.2 | 31.0 | 0 | 0 | 0 | 3 |
| I | VERIFY | 28319 | 32.7 | 81.1 | 127.3 | 728.0 | 0 (0) | 144.9 | 177.8 | 0 (0) | 9.3 | 11.1 | 14.5 | 24.8 | 0 | 0 | 0 | 20 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| G | mf_broken_latch | 2026 | 0 | 3.398 | RECOVER -> ALIGN | 0.869 | 0.925 | 0.930 | 0 | _plan_correction 0.884; update_blocked 0.295; _contact_prior_update 0.253 |
| G | mf_noise_1mm | 2026 | 0 | 4.422 | RECOVER -> ALIGN | 0.848 | 0.940 | 0.945 | 0 | _plan_correction 0.900; _contact_prior_update 0.293; update_blocked 0.285 |
| G | mf_terminal_min | 2026 | 0 | 3.178 | RECOVER -> ALIGN | 0.824 | 0.965 | 0.970 | 0 | _plan_correction 0.925; update_blocked 0.337; _contact_prior_update 0.256 |
| G | mf_stubbed_terminal | 2026 | 0 | 3.974 | RECOVER -> ALIGN | 0.822 | 0.897 | 0.902 | 0 | _plan_correction 0.857; update_blocked 0.289; _contact_prior_update 0.250 |
| G | mf_spread | 2026 | 0 | 3.454 | RECOVER -> ALIGN | 0.819 | 0.890 | 0.894 | 0 | _plan_correction 0.849; update_blocked 0.287; _contact_prior_update 0.246 |
| G | mf_wrong_polarization | 2026 | 0 | 3.38 | RECOVER -> ALIGN | 0.815 | 0.860 | 0.864 | 0 | _plan_correction 0.819; update_blocked 0.282; _contact_prior_update 0.217 |
| G | mf_terminal_min | 2026 | 0 | 5.678 | RECOVER -> ALIGN | 0.769 | 0.857 | 0.862 | 0 | _plan_correction 0.818; update_blocked 0.275; _contact_prior_update 0.216 |
| G | mf_wrong_polarization | 2026 | 0 | 7.812 | RECOVER -> ALIGN | 0.761 | 0.874 | 0.878 | 0 | _plan_correction 0.834; update_blocked 0.285; _contact_prior_update 0.214 |
| G | mf_wrong_polarization | 2026 | 0 | 5.278 | RECOVER -> ALIGN | 0.757 | 0.865 | 0.870 | 0 | _plan_correction 0.824; update_blocked 0.282; _contact_prior_update 0.216 |
| C | mf_broken_latch | 2026 | 0 | 3.398 | RECOVER -> ALIGN | 0.621 | 0.646 | 0.651 | 0 | _plan_correction 0.604; update_blocked 0.276; best_probe 0.146 |
| C | mf_terminal_min | 2026 | 0 | 7.186 | RECOVER -> ALIGN | 0.603 | 0.672 | 0.677 | 0 | _plan_correction 0.632; update_blocked 0.307; best_probe 0.145 |
| C | mf_terminal_min | 2026 | 0 | 3.178 | RECOVER -> ALIGN | 0.601 | 0.625 | 0.630 | 0 | _plan_correction 0.585; update_blocked 0.257; best_probe 0.141 |
| C | mf_noise_1mm | 2026 | 0 | 4.422 | RECOVER -> ALIGN | 0.600 | 0.724 | 0.728 | 0 | _plan_correction 0.683; update_blocked 0.318; entry_probability_at 0.146 |
| C | mf_spread | 2026 | 0 | 3.454 | RECOVER -> ALIGN | 0.598 | 0.623 | 0.628 | 0 | _plan_correction 0.582; update_blocked 0.266; best_probe 0.144 |
| C | mf_wrong_polarization | 2026 | 0 | 3.38 | RECOVER -> ALIGN | 0.587 | 0.613 | 0.618 | 0 | _plan_correction 0.571; update_blocked 0.243; best_probe 0.143 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 19 | 93.1 | 202.9 | 220.5 |
| C | AdaptiveInsertionController._begin_verify | 42 | 34.0 | 179.3 | 222.5 |
| C | AdaptiveInsertionController._click_in_trace | 19 | 34.2 | 91.3 | 98.0 |
| C | AdaptiveInsertionController._diagnose | 58 | 89.1 | 308.7 | 313.8 |
| C | AdaptiveInsertionController._plan_correction | 19 | 582.0 | 1024.8 | 1099.9 |
| C | AdaptiveInsertionController._record_contact | 58 | 11.7 | 23.8 | 23.9 |
| C | AdaptiveInsertionController._tilt_verdict | 19 | 32.6 | 67.5 | 69.9 |
| C | HoleLocalizer.best_probe | 11 | 143.7 | 270.2 | 283.4 |
| C | HoleLocalizer.entry_probability_at | 11 | 112.2 | 229.8 | 239.0 |
| C | HoleLocalizer.update_blocked | 11 | 277.5 | 422.2 | 433.7 |
| C | HoleLocalizer.update_entered | 1 | 26.5 | 26.5 | 26.5 |
| G | AdaptiveInsertionController._begin_latch_verify | 19 | 87.8 | 203.6 | 224.7 |
| G | AdaptiveInsertionController._begin_verify | 42 | 61.1 | 174.9 | 226.5 |
| G | AdaptiveInsertionController._click_in_trace | 19 | 31.6 | 104.2 | 117.3 |
| G | AdaptiveInsertionController._diagnose | 56 | 89.9 | 330.2 | 363.5 |
| G | AdaptiveInsertionController._plan_correction | 17 | 817.7 | 921.2 | 925.3 |
| G | AdaptiveInsertionController._record_contact | 56 | 11.3 | 23.7 | 24.3 |
| G | AdaptiveInsertionController._tilt_verdict | 19 | 32.1 | 58.3 | 62.3 |
| G | AdaptiveLearnedController._contact_prior_update | 9 | 246.5 | 290.0 | 293.0 |
| G | ContactLikelihood.localizer_log_term | 9 | 202.8 | 239.7 | 242.0 |
| G | ContactLikelihood.mixture_mean_mm | 9 | 22.3 | 26.1 | 26.3 |
| G | HoleLocalizer.best_probe | 9 | 143.2 | 148.3 | 148.4 |
| G | HoleLocalizer.entry_probability_at | 9 | 112.0 | 123.3 | 124.1 |
| G | HoleLocalizer.update_blocked | 9 | 285.5 | 333.8 | 337.2 |
| G | HoleLocalizer.update_entered | 1 | 23.9 | 23.9 | 23.9 |
| G | HoleLocalizer.update_log_term | 9 | 3.1 | 4.0 | 4.1 |
| J | AdaptiveInsertionController._begin_latch_verify | 17 | 43.3 | 91.5 | 92.7 |
| J | AdaptiveInsertionController._begin_verify | 37 | 35.5 | 88.3 | 94.4 |
| J | AdaptiveInsertionController._click_in_trace | 17 | 13.9 | 25.5 | 25.5 |
| J | AdaptiveInsertionController._tilt_verdict | 17 | 4.7 | 41.6 | 42.0 |

## run5_arm_quiet (loaded)

180 trials, 800460 ticks, commit ff75d45, 1-min load average per trial: min 8.4, mean 9.8, max 10.7. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.14/146.80, G 0.24/1.67, J 0.17/0.35, F 0.02/0.05, I 0.02/0.05.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 191939 | 46.5 | 126.8 | 306.9 | 5335.4 | 8 (1) | 220.8 | 1307.4 | 0 (0) | 17.6 | 27.8 | 51.7 | 642.4 | 15 | 0 | 0 | 142 |
| C | ALIGN | 5179 | 36.7 | 121.4 | 287.4 | 604.2 | 0 (0) | 208.9 | 347.7 | 0 (0) | 11.7 | 37.4 | 60.5 | 82.2 | 0 | 0 | 0 | 4 |
| C | APPROACH | 26508 | 47.4 | 124.1 | 174.9 | 730.3 | 0 (0) | 174.9 | 202.5 | 0 (0) | 23.2 | 26.5 | 52.4 | 53.6 | 0 | 0 | 0 | 18 |
| C | DETECT | 14024 | 55.2 | 158.1 | 516.1 | 1128.8 | 0 (0) | 525.2 | 797.8 | 0 (0) | 25.0 | 31.6 | 223.7 | 304.6 | 0 | 0 | 0 | 18 |
| C | FAILURE | 1907 | 50.4 | 132.2 | 175.9 | 307.8 | 0 (0) | 185.8 | 185.9 | 0 (0) | 24.1 | 27.7 | 29.4 | 29.7 | 0 | 0 | 0 | 1 |
| C | IDLE | 36 | 63.4 | 201.7 | 216.4 | 218.1 | 0 (0) | 196.0 | 197.0 | 0 (0) | 32.7 | 36.3 | 36.7 | 36.8 | 0 | 0 | 0 | 0 |
| C | INSERT | 88082 | 40.1 | 118.0 | 306.3 | 5335.4 | 8 (1) | 181.9 | 343.4 | 0 (0) | 15.2 | 25.8 | 45.2 | 130.3 | 0 | 0 | 0 | 60 |
| C | RECOVER | 4134 | 49.9 | 139.1 | 1176.7 | 1301.5 | 0 (0) | 1187.0 | 1307.4 | 0 (0) | 24.5 | 26.6 | 628.3 | 642.4 | 15 | 0 | 0 | 5 |
| C | VERIFY | 52069 | 46.3 | 126.8 | 216.9 | 978.8 | 0 (0) | 187.5 | 470.9 | 0 (0) | 17.9 | 27.3 | 40.2 | 159.7 | 0 | 0 | 0 | 36 |
| G | ALL | 190328 | 46.5 | 126.2 | 284.3 | 9849.7 | 5 (3) | 201.6 | 1428.9 | 3 (3) | 17.6 | 27.7 | 52.1 | 811.5 | 12 | 0 | 0 | 135 |
| G | ALIGN | 4413 | 33.7 | 118.5 | 154.3 | 9849.7 | 1 (1) | 167.5 | 368.2 | 1 (1) | 11.7 | 39.7 | 64.2 | 89.2 | 0 | 0 | 0 | 2 |
| G | APPROACH | 26508 | 47.6 | 128.8 | 271.1 | 3179.8 | 2 (0) | 178.7 | 338.3 | 0 (0) | 23.2 | 26.0 | 51.8 | 54.7 | 0 | 0 | 0 | 22 |
| G | DETECT | 11190 | 55.5 | 158.4 | 386.0 | 945.5 | 0 (0) | 390.4 | 783.0 | 0 (0) | 24.5 | 43.3 | 242.6 | 324.9 | 0 | 0 | 0 | 19 |
| G | FAILURE | 1770 | 49.9 | 126.4 | 147.6 | 171.5 | 0 (0) | 151.5 | 186.4 | 0 (0) | 23.8 | 25.8 | 26.9 | 27.6 | 0 | 0 | 0 | 0 |
| G | IDLE | 36 | 65.7 | 128.9 | 129.5 | 129.5 | 0 (0) | 143.8 | 143.9 | 0 (0) | 36.4 | 59.1 | 68.3 | 69.4 | 0 | 0 | 0 | 0 |
| G | INSERT | 87690 | 40.2 | 116.5 | 196.7 | 7764.2 | 2 (2) | 172.1 | 327.9 | 2 (2) | 15.1 | 23.8 | 34.6 | 132.7 | 0 | 0 | 0 | 53 |
| G | RECOVER | 3722 | 50.9 | 135.5 | 875.1 | 1424.7 | 0 (0) | 880.1 | 1428.9 | 0 (0) | 24.5 | 26.9 | 774.3 | 811.5 | 12 | 0 | 0 | 1 |
| G | VERIFY | 54999 | 46.8 | 128.3 | 237.0 | 1018.9 | 0 (0) | 190.2 | 254.3 | 0 (0) | 17.9 | 27.8 | 51.2 | 184.2 | 0 | 0 | 0 | 38 |
| J | ALL | 174251 | 42.8 | 128.8 | 263.1 | 7707.9 | 7 (2) | 199.3 | 523.3 | 2 (2) | 10.5 | 29.3 | 44.5 | 233.6 | 0 | 0 | 0 | 125 |
| J | APPROACH | 27314 | 32.3 | 91.7 | 143.4 | 3444.2 | 2 (1) | 136.0 | 149.9 | 1 (1) | 9.0 | 11.2 | 21.8 | 35.4 | 0 | 0 | 0 | 12 |
| J | DESCEND | 52568 | 30.3 | 89.7 | 231.9 | 7707.9 | 1 (1) | 144.3 | 221.6 | 1 (1) | 7.2 | 9.1 | 17.0 | 85.5 | 0 | 0 | 0 | 37 |
| J | FAILURE | 996 | 34.1 | 352.6 | 2411.4 | 4804.3 | 3 (0) | 171.1 | 174.5 | 0 (0) | 8.7 | 9.3 | 10.7 | 11.1 | 0 | 0 | 0 | 0 |
| J | IDLE | 36 | 48.4 | 105.0 | 107.5 | 107.8 | 0 (0) | 127.7 | 128.0 | 0 (0) | 17.4 | 19.9 | 19.9 | 19.9 | 0 | 0 | 0 | 0 |
| J | INSERT | 15833 | 36.2 | 109.4 | 352.2 | 1754.8 | 0 (0) | 307.8 | 523.3 | 0 (0) | 10.8 | 12.5 | 121.2 | 233.6 | 0 | 0 | 0 | 22 |
| J | RECOVER | 3154 | 55.2 | 150.5 | 191.9 | 479.7 | 0 (0) | 203.4 | 287.8 | 0 (0) | 27.6 | 29.0 | 47.2 | 51.2 | 0 | 0 | 0 | 2 |
| J | SPIRAL | 12383 | 38.1 | 110.8 | 164.4 | 800.2 | 0 (0) | 161.7 | 176.9 | 0 (0) | 12.5 | 13.3 | 19.1 | 23.7 | 0 | 0 | 0 | 8 |
| J | TARE | 2684 | 27.0 | 85.5 | 138.1 | 255.8 | 0 (0) | 136.5 | 172.9 | 0 (0) | 5.4 | 32.6 | 38.1 | 64.9 | 0 | 0 | 0 | 2 |
| J | VERIFY | 59283 | 51.2 | 146.6 | 266.2 | 7164.7 | 1 (0) | 210.4 | 267.2 | 0 (0) | 20.6 | 30.4 | 54.0 | 188.9 | 0 | 0 | 0 | 42 |
| F | ALL | 104015 | 32.5 | 94.6 | 181.7 | 7337.7 | 2 (1) | 151.4 | 197.3 | 1 (1) | 8.6 | 13.1 | 21.1 | 36.3 | 0 | 0 | 0 | 69 |
| F | APPROACH | 27064 | 32.0 | 91.7 | 152.5 | 1411.4 | 0 (0) | 140.8 | 166.9 | 0 (0) | 8.9 | 9.7 | 20.9 | 21.5 | 0 | 0 | 0 | 19 |
| F | DESCEND | 47297 | 29.8 | 88.1 | 225.6 | 7337.7 | 1 (1) | 147.1 | 169.9 | 1 (1) | 7.1 | 9.1 | 17.3 | 18.5 | 0 | 0 | 0 | 34 |
| F | FAILURE | 757 | 33.6 | 97.9 | 329.6 | 366.0 | 0 (0) | 234.3 | 190.2 | 0 (0) | 9.1 | 9.5 | 10.3 | 10.7 | 0 | 0 | 0 | 1 |
| F | IDLE | 36 | 44.8 | 101.7 | 104.1 | 104.4 | 0 (0) | 121.7 | 122.1 | 0 (0) | 13.3 | 18.7 | 19.6 | 19.7 | 0 | 0 | 0 | 0 |
| F | INSERT | 14099 | 35.4 | 101.4 | 195.3 | 1810.0 | 0 (0) | 156.9 | 197.3 | 0 (0) | 10.7 | 12.9 | 19.9 | 28.5 | 0 | 0 | 0 | 7 |
| F | SPIRAL | 12383 | 37.6 | 110.1 | 235.7 | 2092.1 | 1 (0) | 166.5 | 183.2 | 0 (0) | 12.3 | 13.9 | 29.1 | 30.6 | 0 | 0 | 0 | 8 |
| F | TARE | 2379 | 26.4 | 81.8 | 150.5 | 310.5 | 0 (0) | 135.0 | 164.5 | 0 (0) | 5.3 | 30.4 | 34.7 | 36.3 | 0 | 0 | 0 | 0 |
| I | ALL | 139927 | 34.0 | 94.8 | 164.5 | 7324.3 | 3 (3) | 147.2 | 205.6 | 3 (3) | 9.1 | 13.1 | 21.5 | 40.0 | 0 | 0 | 0 | 92 |
| I | APPROACH | 27064 | 32.1 | 89.6 | 135.6 | 4507.0 | 2 (2) | 134.9 | 163.4 | 2 (2) | 9.0 | 10.8 | 21.3 | 22.3 | 0 | 0 | 0 | 16 |
| I | DESCEND | 47297 | 29.9 | 85.2 | 181.2 | 7324.3 | 1 (1) | 140.8 | 159.3 | 1 (1) | 7.1 | 9.1 | 16.7 | 17.3 | 0 | 0 | 0 | 36 |
| I | FAILURE | 2179 | 33.5 | 92.9 | 153.6 | 302.3 | 0 (0) | 127.0 | 138.2 | 0 (0) | 9.3 | 21.4 | 21.7 | 21.8 | 0 | 0 | 0 | 1 |
| I | IDLE | 36 | 44.7 | 92.7 | 93.0 | 93.0 | 0 (0) | 107.5 | 107.5 | 0 (0) | 14.2 | 16.7 | 16.9 | 17.0 | 0 | 0 | 0 | 0 |
| I | INSERT | 14099 | 35.4 | 102.5 | 159.8 | 882.5 | 0 (0) | 142.2 | 177.5 | 0 (0) | 10.7 | 13.3 | 25.4 | 27.5 | 0 | 0 | 0 | 7 |
| I | SPIRAL | 12383 | 37.7 | 110.8 | 192.2 | 1038.1 | 0 (0) | 160.2 | 205.6 | 0 (0) | 12.5 | 14.6 | 18.6 | 23.3 | 0 | 0 | 0 | 7 |
| I | TARE | 2379 | 26.7 | 76.1 | 118.3 | 140.9 | 0 (0) | 127.1 | 153.6 | 0 (0) | 5.3 | 31.3 | 37.1 | 40.0 | 0 | 0 | 0 | 1 |
| I | VERIFY | 34490 | 34.9 | 99.1 | 173.4 | 1419.0 | 0 (0) | 158.0 | 180.4 | 0 (0) | 9.6 | 11.6 | 19.9 | 26.2 | 0 | 0 | 0 | 24 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| G | mf_moderate | 2027 | 0 | 5.35 | RECOVER -> ALIGN | 0.811 | 0.838 | 0.843 | 0 | _plan_correction 0.794; update_blocked 0.326; _contact_prior_update 0.145 |
| G | mf_wrong_polarization | 2027 | 0 | 6.56 | RECOVER -> ALIGN | 0.796 | 0.899 | 0.904 | 0 | _plan_correction 0.855; update_blocked 0.362; _contact_prior_update 0.154 |
| G | noise_2mm | 2027 | 0 | 6.964 | RECOVER -> ALIGN | 0.792 | 0.906 | 0.914 | 0 | _plan_correction 0.849; update_blocked 0.322; _contact_prior_update 0.184 |
| G | mf_noise_1mm | 2027 | 0 | 5.664 | RECOVER -> ALIGN | 0.775 | 0.803 | 0.808 | 0 | _plan_correction 0.761; update_blocked 0.288; _contact_prior_update 0.146 |
| G | mf_terminal_max_broken_latch | 2027 | 0 | 5.174 | RECOVER -> ALIGN | 0.774 | 0.806 | 0.811 | 0 | _plan_correction 0.762; update_blocked 0.289; _contact_prior_update 0.144 |
| G | noise_2mm | 2027 | 0 | 15.79 | RECOVER -> ALIGN | 0.773 | 0.849 | 0.854 | 0 | _plan_correction 0.808; update_blocked 0.291; best_probe 0.166 |
| G | mf_latch_early | 2027 | 0 | 5.268 | RECOVER -> ALIGN | 0.771 | 0.836 | 0.841 | 0 | _plan_correction 0.793; update_blocked 0.317; _contact_prior_update 0.146 |
| G | mf_spread_half_latched | 2027 | 0 | 5.126 | RECOVER -> ALIGN | 0.763 | 0.788 | 0.794 | 0 | _plan_correction 0.746; update_blocked 0.283; _contact_prior_update 0.143 |
| G | noise_2mm | 2027 | 0 | 13.464 | RECOVER -> ALIGN | 0.759 | 0.883 | 0.888 | 0 | _plan_correction 0.841; update_blocked 0.343; _contact_prior_update 0.155 |
| G | generalization_combined | 2027 | 0 | 4.81 | RECOVER -> ALIGN | 0.758 | 0.872 | 0.877 | 0 | _plan_correction 0.830; update_blocked 0.349; _contact_prior_update 0.152 |
| G | noise_2mm | 2027 | 0 | 10.952 | RECOVER -> ALIGN | 0.750 | 0.848 | 0.853 | 0 | _plan_correction 0.806; update_blocked 0.300; best_probe 0.153 |
| G | noise_2mm | 2027 | 0 | 9.076 | RECOVER -> ALIGN | 0.736 | 1.425 | 1.429 | 0 | _plan_correction 1.350; update_blocked 0.438; _contact_prior_update 0.289 |
| C | noise_2mm | 2027 | 0 | 6.964 | RECOVER -> ALIGN | 0.642 | 0.840 | 0.845 | 0 | _plan_correction 0.798; update_blocked 0.391; entry_probability_at 0.172 |
| C | mf_moderate | 2027 | 0 | 5.35 | RECOVER -> ALIGN | 0.642 | 1.197 | 1.208 | 0 | _plan_correction 1.108; update_blocked 0.437; best_probe 0.287 |
| C | generalization_combined | 2027 | 0 | 4.81 | RECOVER -> ALIGN | 0.641 | 1.241 | 1.251 | 1 | _plan_correction 1.153; update_blocked 0.439; entry_probability_at 0.284 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 22 | 205.2 | 424.4 | 425.0 |
| C | AdaptiveInsertionController._begin_verify | 42 | 57.9 | 406.3 | 424.3 |
| C | AdaptiveInsertionController._click_in_trace | 22 | 122.0 | 290.1 | 294.5 |
| C | AdaptiveInsertionController._diagnose | 63 | 147.9 | 364.6 | 367.0 |
| C | AdaptiveInsertionController._plan_correction | 22 | 646.3 | 1204.3 | 1218.1 |
| C | AdaptiveInsertionController._record_contact | 63 | 13.6 | 26.1 | 26.8 |
| C | AdaptiveInsertionController._tilt_verdict | 22 | 40.5 | 82.5 | 82.7 |
| C | HoleLocalizer.best_probe | 15 | 165.4 | 338.0 | 346.2 |
| C | HoleLocalizer.entry_probability_at | 15 | 125.0 | 278.5 | 284.1 |
| C | HoleLocalizer.update_blocked | 15 | 322.6 | 490.9 | 491.4 |
| G | AdaptiveInsertionController._begin_latch_verify | 22 | 171.8 | 454.7 | 465.2 |
| G | AdaptiveInsertionController._begin_verify | 43 | 55.3 | 446.1 | 467.2 |
| G | AdaptiveInsertionController._click_in_trace | 22 | 109.1 | 322.6 | 333.7 |
| G | AdaptiveInsertionController._diagnose | 61 | 100.3 | 302.4 | 310.0 |
| G | AdaptiveInsertionController._plan_correction | 19 | 762.1 | 1261.3 | 1350.4 |
| G | AdaptiveInsertionController._record_contact | 61 | 12.3 | 28.3 | 28.9 |
| G | AdaptiveInsertionController._tilt_verdict | 22 | 32.5 | 66.0 | 66.4 |
| G | AdaptiveLearnedController._contact_prior_update | 12 | 151.3 | 277.1 | 288.6 |
| G | ContactPrior.localizer_term | 12 | 51.3 | 89.9 | 91.8 |
| G | HoleLocalizer.best_probe | 12 | 144.1 | 254.2 | 265.1 |
| G | HoleLocalizer.entry_probability_at | 12 | 119.3 | 222.6 | 234.9 |
| G | HoleLocalizer.update_blocked | 12 | 319.4 | 429.6 | 438.0 |
| G | HoleLocalizer.update_gaussian | 12 | 81.3 | 153.0 | 160.8 |
| J | AdaptiveInsertionController._begin_latch_verify | 18 | 133.6 | 1174.9 | 1310.1 |
| J | AdaptiveInsertionController._begin_verify | 38 | 57.4 | 915.9 | 1313.2 |
| J | AdaptiveInsertionController._click_in_trace | 18 | 76.0 | 1064.9 | 1209.8 |
| J | AdaptiveInsertionController._tilt_verdict | 18 | 6.4 | 87.8 | 96.9 |

## run5_gantry_quiet (loaded)

180 trials, 500282 ticks, commit ff75d45, 1-min load average per trial: min 7.3, mean 8.0, max 8.6. Controller reset (before the cycle, outside the loop), ms p50/max: C 0.13/131.69, G 0.20/1.60, J 0.14/0.28, F 0.02/0.08, I 0.02/0.05.

| ctrl | state | ticks | total p50 | p99 | p99.9 | max | total > 2 ms (with GC) | cpu p99.9 | cpu max nogc | cpu > 2 ms (with GC) | best p50 | p99 | p99.9 | max | best > 0.5 ms | > 1 ms | > 2 ms | ticks with GC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | ALL | 114199 | 43.2 | 111.8 | 228.2 | 8993.0 | 9 (7) | 202.4 | 1207.3 | 7 (7) | 15.9 | 26.5 | 38.2 | 619.0 | 9 | 0 | 0 | 282 |
| C | ALIGN | 3820 | 32.4 | 103.3 | 145.1 | 203.3 | 0 (0) | 151.6 | 208.9 | 0 (0) | 11.4 | 36.9 | 42.1 | 53.9 | 0 | 0 | 0 | 2 |
| C | APPROACH | 26508 | 44.7 | 110.9 | 174.5 | 3154.5 | 1 (1) | 173.1 | 231.1 | 1 (1) | 22.8 | 24.0 | 25.2 | 27.4 | 0 | 0 | 0 | 55 |
| C | DETECT | 4384 | 45.1 | 169.4 | 365.5 | 4675.1 | 2 (0) | 329.2 | 471.0 | 0 (0) | 21.1 | 119.2 | 202.9 | 212.6 | 0 | 0 | 0 | 10 |
| C | FAILURE | 1349 | 46.5 | 130.6 | 179.1 | 333.6 | 0 (0) | 167.1 | 169.8 | 0 (0) | 23.6 | 24.7 | 25.5 | 25.7 | 0 | 0 | 0 | 1 |
| C | IDLE | 36 | 58.7 | 148.2 | 157.3 | 158.3 | 0 (0) | 172.0 | 173.1 | 0 (0) | 31.1 | 34.4 | 34.9 | 35.0 | 0 | 0 | 0 | 0 |
| C | INSERT | 36336 | 37.7 | 106.0 | 192.1 | 4335.5 | 3 (3) | 185.5 | 268.0 | 3 (3) | 15.0 | 21.7 | 29.0 | 126.3 | 0 | 0 | 0 | 111 |
| C | RECOVER | 2961 | 47.0 | 130.0 | 1171.1 | 4539.2 | 1 (1) | 1181.4 | 1207.3 | 1 (1) | 24.3 | 25.9 | 599.1 | 619.0 | 9 | 0 | 0 | 5 |
| C | VERIFY | 38805 | 37.5 | 113.2 | 192.0 | 8993.0 | 2 (2) | 184.6 | 375.0 | 2 (2) | 13.8 | 26.9 | 30.8 | 80.0 | 0 | 0 | 0 | 98 |
| G | ALL | 118738 | 43.7 | 113.5 | 238.9 | 9096.8 | 9 (8) | 216.0 | 1043.6 | 8 (8) | 16.2 | 26.8 | 36.6 | 891.2 | 14 | 0 | 0 | 280 |
| G | ALIGN | 4484 | 33.5 | 106.3 | 179.4 | 9096.8 | 1 (0) | 185.6 | 215.6 | 0 (0) | 11.7 | 35.2 | 42.2 | 53.6 | 0 | 0 | 0 | 3 |
| G | APPROACH | 26508 | 45.3 | 112.0 | 162.7 | 620.0 | 0 (0) | 170.6 | 225.7 | 0 (0) | 23.0 | 24.7 | 25.6 | 28.0 | 0 | 0 | 0 | 60 |
| G | DETECT | 5285 | 47.5 | 162.8 | 437.8 | 619.0 | 0 (0) | 441.8 | 625.4 | 0 (0) | 22.0 | 40.5 | 207.0 | 217.0 | 0 | 0 | 0 | 8 |
| G | FAILURE | 1466 | 48.0 | 127.6 | 200.0 | 720.3 | 0 (0) | 189.3 | 200.0 | 0 (0) | 24.3 | 25.8 | 27.0 | 27.2 | 0 | 0 | 0 | 1 |
| G | IDLE | 36 | 61.2 | 68.6 | 68.9 | 68.9 | 0 (0) | 77.0 | 77.1 | 0 (0) | 34.2 | 37.3 | 37.4 | 37.4 | 0 | 0 | 0 | 0 |
| G | INSERT | 38262 | 38.7 | 110.0 | 194.6 | 9024.2 | 1 (1) | 187.0 | 210.0 | 1 (1) | 15.2 | 22.2 | 26.9 | 123.2 | 0 | 0 | 0 | 108 |
| G | RECOVER | 3877 | 48.6 | 132.0 | 970.5 | 1038.4 | 0 (0) | 975.2 | 1043.6 | 0 (0) | 25.0 | 27.6 | 827.4 | 891.2 | 14 | 0 | 0 | 3 |
| G | VERIFY | 38820 | 38.1 | 113.0 | 222.0 | 5067.7 | 7 (7) | 184.8 | 333.0 | 7 (7) | 14.1 | 27.2 | 30.9 | 85.1 | 0 | 0 | 0 | 97 |
| J | ALL | 113143 | 37.6 | 114.5 | 198.5 | 4645.4 | 6 (6) | 182.4 | 276.7 | 6 (6) | 10.5 | 29.2 | 30.7 | 84.0 | 0 | 0 | 0 | 290 |
| J | APPROACH | 26906 | 30.6 | 83.2 | 169.3 | 3494.7 | 2 (2) | 140.5 | 262.8 | 2 (2) | 8.9 | 9.6 | 10.4 | 14.9 | 0 | 0 | 0 | 55 |
| J | DESCEND | 13023 | 29.0 | 75.5 | 133.6 | 917.1 | 0 (0) | 152.0 | 157.7 | 0 (0) | 7.0 | 9.4 | 44.7 | 48.2 | 0 | 0 | 0 | 36 |
| J | FAILURE | 772 | 31.7 | 74.9 | 312.8 | 316.7 | 0 (0) | 316.4 | 129.3 | 0 (0) | 9.0 | 9.2 | 10.6 | 10.6 | 0 | 0 | 0 | 2 |
| J | IDLE | 36 | 45.2 | 91.4 | 94.4 | 94.7 | 0 (0) | 109.0 | 109.4 | 0 (0) | 15.7 | 17.6 | 17.8 | 17.8 | 0 | 0 | 0 | 0 |
| J | INSERT | 6668 | 34.0 | 92.6 | 248.7 | 458.6 | 0 (0) | 256.8 | 276.7 | 0 (0) | 10.8 | 12.2 | 72.2 | 84.0 | 0 | 0 | 0 | 19 |
| J | RECOVER | 3337 | 50.6 | 124.4 | 162.7 | 338.5 | 0 (0) | 179.8 | 197.8 | 0 (0) | 26.5 | 28.2 | 44.0 | 48.3 | 0 | 0 | 0 | 1 |
| J | SPIRAL | 13722 | 32.6 | 83.9 | 145.3 | 3653.6 | 1 (1) | 154.0 | 163.1 | 1 (1) | 10.1 | 11.0 | 12.6 | 22.3 | 0 | 0 | 0 | 39 |
| J | TARE | 2683 | 25.9 | 71.6 | 130.2 | 190.0 | 0 (0) | 136.4 | 164.9 | 0 (0) | 5.3 | 25.9 | 30.6 | 32.0 | 0 | 0 | 0 | 6 |
| J | VERIFY | 45996 | 41.1 | 122.1 | 234.6 | 4645.4 | 3 (3) | 197.2 | 253.3 | 3 (3) | 16.5 | 29.5 | 32.8 | 82.6 | 0 | 0 | 0 | 132 |
| F | ALL | 61011 | 30.5 | 87.3 | 273.5 | 3933.7 | 7 (4) | 153.4 | 259.2 | 4 (4) | 8.8 | 11.0 | 20.9 | 44.8 | 0 | 0 | 0 | 150 |
| F | APPROACH | 26862 | 30.0 | 90.9 | 414.2 | 3609.3 | 2 (2) | 149.8 | 259.2 | 2 (2) | 8.8 | 10.0 | 20.8 | 21.4 | 0 | 0 | 0 | 59 |
| F | DESCEND | 11510 | 28.2 | 84.9 | 279.2 | 3475.9 | 3 (1) | 176.2 | 242.0 | 1 (1) | 6.8 | 9.0 | 14.0 | 17.3 | 0 | 0 | 0 | 36 |
| F | FAILURE | 772 | 30.9 | 87.2 | 109.3 | 110.0 | 0 (0) | 116.9 | 117.7 | 0 (0) | 9.0 | 9.7 | 10.2 | 11.1 | 0 | 0 | 0 | 0 |
| F | IDLE | 36 | 40.6 | 2592.1 | 3799.6 | 3933.7 | 1 (0) | 175.7 | 177.8 | 0 (0) | 11.8 | 15.8 | 16.3 | 16.4 | 0 | 0 | 0 | 0 |
| F | INSERT | 5792 | 33.1 | 97.2 | 151.8 | 947.0 | 0 (0) | 154.6 | 161.3 | 0 (0) | 10.5 | 12.5 | 16.8 | 27.6 | 0 | 0 | 0 | 13 |
| F | SPIRAL | 13722 | 31.9 | 80.5 | 133.4 | 3331.6 | 1 (1) | 136.9 | 180.5 | 1 (1) | 10.0 | 10.7 | 12.2 | 21.6 | 0 | 0 | 0 | 41 |
| F | TARE | 2317 | 25.0 | 63.8 | 120.5 | 163.0 | 0 (0) | 128.9 | 154.6 | 0 (0) | 5.2 | 22.6 | 40.6 | 44.8 | 0 | 0 | 0 | 1 |
| I | ALL | 93191 | 31.5 | 80.4 | 135.5 | 7684.6 | 6 (5) | 143.7 | 172.9 | 5 (5) | 9.1 | 11.6 | 23.8 | 45.2 | 0 | 0 | 0 | 182 |
| I | APPROACH | 26862 | 30.3 | 77.3 | 128.2 | 5839.1 | 1 (1) | 138.2 | 169.4 | 1 (1) | 8.8 | 9.4 | 9.9 | 11.8 | 0 | 0 | 0 | 63 |
| I | DESCEND | 11510 | 28.5 | 79.3 | 161.3 | 5047.8 | 1 (1) | 142.6 | 157.5 | 1 (1) | 6.9 | 9.3 | 13.6 | 15.8 | 0 | 0 | 0 | 33 |
| I | FAILURE | 2335 | 30.1 | 73.3 | 118.4 | 274.4 | 0 (0) | 132.3 | 139.8 | 0 (0) | 8.8 | 10.7 | 20.8 | 21.5 | 0 | 0 | 0 | 1 |
| I | IDLE | 36 | 42.4 | 328.8 | 433.2 | 444.7 | 0 (0) | 155.3 | 156.0 | 0 (0) | 13.2 | 14.6 | 14.7 | 14.7 | 0 | 0 | 0 | 0 |
| I | INSERT | 5792 | 33.2 | 82.6 | 130.3 | 308.5 | 0 (0) | 137.7 | 163.1 | 0 (0) | 10.6 | 12.8 | 21.4 | 21.8 | 0 | 0 | 0 | 13 |
| I | SPIRAL | 13722 | 32.1 | 85.9 | 244.4 | 7684.6 | 2 (1) | 156.6 | 172.9 | 1 (1) | 10.0 | 23.0 | 24.0 | 24.8 | 0 | 0 | 0 | 44 |
| I | TARE | 2317 | 25.5 | 64.9 | 116.2 | 143.4 | 0 (0) | 125.6 | 156.3 | 0 (0) | 5.2 | 27.3 | 33.2 | 33.8 | 0 | 0 | 0 | 2 |
| I | VERIFY | 30617 | 32.1 | 79.8 | 135.4 | 4374.1 | 2 (2) | 147.0 | 162.9 | 2 (2) | 9.3 | 11.9 | 24.5 | 45.2 | 0 | 0 | 0 | 26 |

Slowest ticks by best controller.step time (intrinsic cost):

| ctrl | condition | seed | trial | t s | state -> after | best ms | in-loop total ms | cpu ms | GC | largest sub-timers ms |
|---|---|---|---|---|---|---|---|---|---|---|
| G | mf_terminal_max_broken_latch | 2027 | 0 | 3.41 | RECOVER -> ALIGN | 0.891 | 1.019 | 1.024 | 0 | _plan_correction 0.977; update_blocked 0.361; _contact_prior_update 0.267 |
| G | mf_latch_early | 2027 | 0 | 3.422 | RECOVER -> ALIGN | 0.868 | 0.893 | 0.897 | 0 | _plan_correction 0.853; update_blocked 0.281; _contact_prior_update 0.251 |
| G | mf_moderate | 2027 | 0 | 3.448 | RECOVER -> ALIGN | 0.841 | 0.949 | 0.955 | 0 | _plan_correction 0.909; update_blocked 0.311; _contact_prior_update 0.253 |
| G | generalization_combined | 2027 | 0 | 3.302 | RECOVER -> ALIGN | 0.829 | 0.968 | 0.973 | 0 | _plan_correction 0.927; update_blocked 0.322; _contact_prior_update 0.262 |
| G | mf_wrong_polarization | 2027 | 0 | 3.272 | RECOVER -> ALIGN | 0.827 | 0.940 | 0.945 | 0 | _plan_correction 0.899; update_blocked 0.299; _contact_prior_update 0.256 |
| G | mf_wrong_polarization | 2027 | 0 | 7.74 | RECOVER -> ALIGN | 0.827 | 0.893 | 0.898 | 0 | _plan_correction 0.852; update_blocked 0.277; _contact_prior_update 0.225 |
| G | mf_wrong_polarization | 2027 | 0 | 11.102 | RECOVER -> ALIGN | 0.825 | 0.939 | 0.945 | 0 | _plan_correction 0.895; update_blocked 0.281; _contact_prior_update 0.236 |
| G | mf_wrong_polarization | 2027 | 0 | 12.922 | RECOVER -> ALIGN | 0.824 | 0.922 | 0.927 | 0 | _plan_correction 0.883; update_blocked 0.283; _contact_prior_update 0.238 |
| G | mf_spread_half_latched | 2027 | 0 | 3.54 | RECOVER -> ALIGN | 0.819 | 0.933 | 0.937 | 0 | _plan_correction 0.894; update_blocked 0.309; _contact_prior_update 0.254 |
| G | mf_wrong_polarization | 2027 | 0 | 9.452 | RECOVER -> ALIGN | 0.798 | 0.887 | 0.892 | 0 | _plan_correction 0.846; update_blocked 0.284; _contact_prior_update 0.220 |
| G | mf_moderate | 2027 | 0 | 5.266 | RECOVER -> ALIGN | 0.794 | 1.038 | 1.044 | 0 | _plan_correction 0.996; update_blocked 0.366; _contact_prior_update 0.271 |
| G | noise_2mm | 2027 | 0 | 4.28 | RECOVER -> ALIGN | 0.790 | 1.003 | 1.008 | 0 | _plan_correction 0.964; update_blocked 0.334; _contact_prior_update 0.314 |
| G | mf_noise_1mm | 2027 | 0 | 4.276 | RECOVER -> ALIGN | 0.782 | 0.986 | 0.991 | 0 | _plan_correction 0.942; update_blocked 0.311; _contact_prior_update 0.298 |
| G | mf_wrong_polarization | 2027 | 0 | 5.138 | RECOVER -> ALIGN | 0.759 | 0.845 | 0.849 | 0 | _plan_correction 0.804; update_blocked 0.251; _contact_prior_update 0.223 |
| C | generalization_combined | 2027 | 0 | 3.302 | RECOVER -> ALIGN | 0.619 | 1.186 | 1.194 | 0 | _plan_correction 1.103; update_blocked 0.462; best_probe 0.270 |

Sub-timers (inclusive, in-loop wall time, per tick that called them):

| ctrl | function | ticks | p50 us | p99 us | max us |
|---|---|---|---|---|---|
| C | AdaptiveInsertionController._begin_latch_verify | 18 | 88.8 | 278.6 | 299.5 |
| C | AdaptiveInsertionController._begin_verify | 39 | 35.9 | 171.6 | 178.1 |
| C | AdaptiveInsertionController._click_in_trace | 18 | 31.1 | 148.2 | 164.6 |
| C | AdaptiveInsertionController._diagnose | 49 | 89.4 | 203.1 | 205.5 |
| C | AdaptiveInsertionController._plan_correction | 14 | 622.3 | 1112.9 | 1114.4 |
| C | AdaptiveInsertionController._record_contact | 49 | 11.4 | 22.3 | 23.4 |
| C | AdaptiveInsertionController._tilt_verdict | 18 | 32.3 | 79.8 | 83.5 |
| C | HoleLocalizer.best_probe | 9 | 144.5 | 291.6 | 292.5 |
| C | HoleLocalizer.entry_probability_at | 9 | 126.8 | 240.9 | 241.4 |
| C | HoleLocalizer.update_blocked | 9 | 310.0 | 460.1 | 462.2 |
| G | AdaptiveInsertionController._begin_latch_verify | 18 | 94.9 | 281.5 | 284.6 |
| G | AdaptiveInsertionController._begin_verify | 39 | 34.7 | 264.2 | 286.4 |
| G | AdaptiveInsertionController._click_in_trace | 18 | 34.8 | 140.5 | 141.5 |
| G | AdaptiveInsertionController._diagnose | 55 | 91.3 | 322.6 | 323.2 |
| G | AdaptiveInsertionController._plan_correction | 19 | 882.6 | 992.8 | 996.3 |
| G | AdaptiveInsertionController._record_contact | 55 | 11.5 | 26.7 | 30.7 |
| G | AdaptiveInsertionController._tilt_verdict | 18 | 32.9 | 79.6 | 79.9 |
| G | AdaptiveLearnedController._contact_prior_update | 14 | 253.4 | 312.2 | 314.4 |
| G | ContactLikelihood.localizer_log_term | 14 | 209.5 | 262.7 | 264.3 |
| G | ContactLikelihood.mixture_mean_mm | 14 | 23.2 | 28.3 | 28.6 |
| G | HoleLocalizer.best_probe | 14 | 149.0 | 173.2 | 173.4 |
| G | HoleLocalizer.entry_probability_at | 14 | 116.7 | 132.6 | 133.2 |
| G | HoleLocalizer.update_blocked | 14 | 303.6 | 365.1 | 365.8 |
| G | HoleLocalizer.update_log_term | 14 | 3.0 | 3.9 | 4.0 |
| J | AdaptiveInsertionController._begin_latch_verify | 20 | 71.4 | 341.7 | 379.9 |
| J | AdaptiveInsertionController._begin_verify | 40 | 34.1 | 268.8 | 380.8 |
| J | AdaptiveInsertionController._click_in_trace | 20 | 17.5 | 58.5 | 64.0 |
| J | AdaptiveInsertionController._tilt_verdict | 20 | 6.8 | 292.2 | 342.9 |

