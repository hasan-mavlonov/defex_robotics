# sim_randomization_v0.2f run log

- Pre-registration: `PREREGISTRATION.md`, committed at 341c798 and 16d2adc. Frozen code:
  c87f942.
- Started from **69cbaa4**, which adds only `results/sim_randomization_v0.2f/run.sh` (the
  pre-registered commands plus these log lines) after the pre-registration.
- `git status --porcelain --untracked-files=all` outside `results/` at the start: empty
  (`run_log_raw.txt`).
- Both `config.json` files: `git_commit` 69cbaa4404e6b474ab19aecd709c1910f7bc6cfa,
  `git_dirty: false`.
- Environment: Python 3.12.11, MuJoCo 3.17.0, Darwin arm64 (Apple Silicon), 10 cores,
  `--workers 4`.
- Seed 20261205, 12 randomized variants plus variant 0, `--g-model pinned`.

| Run | Start (UTC) | End (UTC) | Wall time | Trials | Load average at start (1/5/15 min) |
|---|---|---|---|---|---|
| gantry | 2026-11-02 23:24:55 | 2026-11-03 00:04:56 | 2,400 s (40.0 min) | 11,856 | 7.99 / 16.77 / 17.50 |
| arm | 2026-11-03 00:04:56 | 2026-11-03 01:36:22 | 5,485 s (91.4 min) | 14,196 | 82.51 / 62.37 / 55.51 |
| tables | 01:36:22 | 01:36:24 | | | |

- In all: 26,052 trials in 2 h 11 min. The estimate was about 129 min.
- Load average at the arm's end: 13.68 / 16.94 / 33.44. Mid-arm, a check read
  135.92 / 163.62 / 155.47. Other agents' jobs were running throughout.
- Both runs finished on the first attempt, with no errors and nothing repeated. The
  first result was read after the tables were written.
- Raw log: `run_log_raw.txt`. Run time per machine: `{gantry,arm}/run_time.json`.
- `events.json.gz` for both machines is kept locally, not committed. No reported
  number needs it.
