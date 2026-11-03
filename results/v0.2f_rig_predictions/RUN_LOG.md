# v0.2f rig predictions: run log

- Pre-registration: `PREREGISTRATION.md` and `tables.py`, committed in dc938d1 on
  branch `v0.2f/hw`.
- Frozen-code check, before writing the pre-registration, at 4df8cae:
  `git diff --stat ddd0d34 HEAD -- . ':(exclude)results' ':(exclude)README.md' ':(exclude)docs'`
  printed nothing. The same command at dc938d1 printed nothing.
- Start check, at HEAD dc938d1, by the run script just before the first command:
  `git status --porcelain --untracked-files=all -- . ':(exclude)results'` printed 0 lines.
- Started 2026-11-02 15:04:47 PST and finished 16:07:00 PST (1 h 02 min). The
  pre-registered commands ran in order, with `--workers 2`. No run was repeated, skipped
  or dropped.
  - gantry standard 15:04:47-15:08:45;
  - gantry latching 15:08:45-15:22:17;
  - arm standard 15:22:17-15:30:43;
  - arm latching 15:30:43-16:07:00.
- **The run took longer than the about 45 minutes it was sized for.** Other agents were
  using the shared 10-core machine: `uptime` showed load averages of 28 at 15:08 and 40
  at 15:12 and 15:21. The 2-worker timing check, on an idle machine, had predicted about
  30 minutes. As the pre-registration says, the run was finished anyway.
- All four `config.json`: `git_commit` dc938d1062a62a183606e54e8a6d41b7dcd5390d,
  `git_dirty: false`, `base_seed` 20261201, `workers` 2.
- Rows in `trials.csv`: 1,200 for each standard run and 2,100 for each latching run, so
  6,600 in all, as pre-registered.
- No tracked file outside `results/` was edited during the run. The hardware documents,
  `experiments/v02f_rig_power.py` and `tests/test_v02f_rig.py` were drafted in the
  session's scratch area or as untracked files, and committed after the run.
- After the run, `TABLES.md` and `CONTEXT_v0.2e.md` were made with the pre-registered
  commands.
- **One post-run edit to `tables.py`, cosmetic.** The pose table's header and caption
  used "|tilt|" and "|yaw|". The pipes broke the markdown table, so they became
  "abs(tilt)" and "abs(yaw)". No number or rule changed. The diff is two strings, in the
  commit after the run.
- Development timing check (seed 2026, not reported): 96 gantry trials took 11 s and 84
  arm latching trials 33 s, at `--workers 2`. Its output stayed in the session's scratch
  area.
- `events.json.gz` is not committed: no reported number needs it.

## Extension to 100 trials per condition (PREREGISTRATION.md item 7)

- Asked for by the lead agent after the 50-trial report, so that the predictions cover
  the protocol's 100 trials per condition.
- Run from a clean, detached checkout of dc938d1, made with `git worktree add --detach`
  in the session's scratch area and removed after the run. The commands are the
  pre-registered ones with `--trials 100` and
  `--name v0.2f_rig_predictions/ext100/<machine>_<suite>`. The runner has no start-index
  option, so indices 0-49 were run again; that also gives the identity check below.
- Start check: `git status --porcelain --untracked-files=all -- . ':(exclude)results'`
  printed 0 lines at HEAD dc938d1.
- Started 2026-11-02 16:43:01 PST and finished 18:16:15 PST (1 h 33 min), at
  `--workers 2`. No run was repeated, skipped or dropped. Load averages were 17-90
  (other agents).
  - gantry standard 16:43:01-16:52:08;
  - gantry latching 16:52:08-17:25:24;
  - arm standard 17:25:24-17:39:50;
  - arm latching 17:39:50-18:16:15.
- All four `ext100/*/config.json`: `git_commit` dc938d1062a62a183606e54e8a6d41b7dcd5390d,
  `git_dirty: false`, `base_seed` 20261201, `workers` 2. Rows: 2,400 per standard run
  and 4,200 per latching run, so 13,200 in all.
- **Identity check** (`ext100/check_first50.py`, output in `ext100/CHECK_FIRST50.txt`):
  trial indices 0-49 of the extension against the committed 50-trial rows. 6,600 rows,
  237,600 fields, **0 differences**; `wall_time_s` was not compared. So the extension
  is used, as item 7 says.
- `TABLES.md` was regenerated from `ext100/` with the pre-registered `tables.py`. The
  50-trial tables and report are kept as `TABLES_50.md` and `REPORT_50.md`.
  `REPORT.md` is the 100-trial report.
- `events.json.gz` is not committed.
