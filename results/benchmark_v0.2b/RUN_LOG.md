# benchmark_v0.2b run log

All six runs use the pre-registered command, commit 54f3097 (code frozen at
8e29f2e), seed 20261102, `--workers 9`. Final row counts: 14,000, 9,800 and 3,500 per machine for the
standard, latching and heldout suites (54,600 in total).

| Run | Started (PDT) | Finished (PDT) | Notes |
|---|---|---|---|
| gantry_standard | 2026-10-31 23:22 | 23:31 | |
| gantry_latching | 23:31 | 23:50 | |
| gantry_heldout | 23:50 | 23:53 | |
| arm_standard | 23:53 | 2026-11-01 00:24 | |
| arm_latching, first attempt | 00:24 | 01:17, killed | no rows written |
| arm_heldout | 01:17 PDT | 01:30 PDT | |
| arm_latching, second attempt | 01:30 PDT | 01:26 PST | complete, 9,800 rows |

Daylight saving time ended during the second arm_latching attempt (02:00 PDT
became 01:00 PST), so its end time reads earlier than its start.

## The arm_latching restart

The first arm_latching attempt stopped at 01:17:41 PDT with
`concurrent.futures.process.BrokenProcessPool: A process in the process pool was
terminated abruptly`. No `trials.csv` or `summary.json` was written, and nothing
from the attempt was read.

Cause: at 01:17:35 PDT a development agent working in a separate worktree
(v0.2c arm baselines) ran

```
pkill -9 -f "multiprocessing.spawn" -P $(pgrep -f tune_baselines | head -1)
```

to stop its own tuning workers. `pgrep` returned nothing, so `-P` received no
parent id and the command sent SIGKILL to every `multiprocessing.spawn` worker on
the machine, including this run's. There is no crash report and no traceback from
a worker, which fits an external SIGKILL and not a fault in the simulation.

The run was restarted with the identical command, commit and seed. Each trial's
scenario and noise come from the base seed, condition and trial index, so a
restart reproduces the same trials; no choice was made between attempts. Later
runs were wrapped in a retry (`rm -rf` of the partial folder, then the same
command, at most four attempts) in case of another external kill.
