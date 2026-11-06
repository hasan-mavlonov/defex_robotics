# benchmark_v0.2c run log

All eight runs use the pre-registered command, commit b479e17 (code frozen at
45f8b06, the commit after it adds only the pre-registration), seed 20261116,
`--workers 9`. Every `config.json` shows `git_commit` b479e17 and
`git_dirty: false`. Final row counts per machine: 18,000 (standard), 12,600
(latching), 4,500 (heldout), 8,100 (latch_spread); 86,400 in total, as
pre-registered.

| Run | Started (PST, 2026-11-01) | Finished | Notes |
|---|---|---|---|
| gantry_standard | 10:23 | 10:33 | |
| gantry_latching | 10:33 | 10:49 | |
| gantry_heldout | 10:49 | 10:52 | |
| gantry_latch_spread | 10:52 | 11:01 | |
| arm_standard, first attempt | 11:01 | stopped | paused by the operator; only `config.json` written |
| arm_standard | 11:57 | 12:14 | complete, 18,000 rows |
| arm_latching | 12:14 | 12:37 | |
| arm_heldout | 12:37 | 12:43 | |
| arm_latch_spread | 12:43 | 12:56 | |

Total compute: about 1.6 hours, against the 3.5 hours estimated.

## The arm_standard restart

The first arm_standard attempt was stopped on purpose a few minutes after it
started, because the operator asked for all work to pause. It had written only
`config.json`: no `trials.csv` and no `summary.json`, and nothing from it was
read. The runner deletes a run folder without `summary.json` before starting
it, and the run was repeated with the identical command, commit and seed. Each
trial's scenario and noise come from the base seed, the condition and the trial
index, so a restart produces the same trials.

The four gantry results were looked at during the pause; no code, setting or
pre-registered rule changed between the gantry runs and the arm runs (all eight
at b479e17, clean tree).

## After the run

`experiments/cp2_audit.py` had the title "benchmark_v0.2b" written into it. The
title now uses the folder name; the tables it prints are unchanged (re-running it
on `results/benchmark_v0.2b` reproduces the committed `AUDIT_TABLES.md` byte for
byte).
