# benchmark_v0.2e run log

- Pre-registration: `PREREGISTRATION.md`, committed in e0006a1. The code is frozen at
  ddd0d34, and e0006a1 changes only `results/`; `git diff --stat ddd0d34 e0006a1` shows
  one file, this folder's `PREREGISTRATION.md`.
- Start check, 2026-11-02 04:45 PST, at HEAD e0006a1, just after the commit and before
  the first command: `git status --porcelain --untracked-files=all -- . ':(exclude)results'`
  printed 0 lines. The check was run and read in the working session; it was not written
  to a file at the time.
- Started 2026-11-02 04:45 PST and finished 06:41 PST (1 h 56 min). One machine ran the
  pre-registered commands in order with `--workers 9`. The runner script skips a run that
  already has a `summary.json`; no run was skipped, repeated or dropped.
- All eight `config.json`: `git_commit` e0006a192eb358472558e35c043b9e9b0ef41696,
  `git_dirty: false`, `base_seed` 20261130, `workers` 9.
- Rows in `trials.csv`: on gantry and on arm, standard 20,000, latching 14,000, heldout
  5,000 and latch_spread 9,000. That makes 96,000 in all, as pre-registered.
- Environment (`config.json`): Python 3.12.11, MuJoCo 3.17.0, NumPy 2.5.4, macOS 27.0.1
  arm64, 10 CPUs.
- Per-run times (runner log):
  - gantry: standard 04:45-04:56, latching 04:56-05:16, heldout 05:16-05:20,
    latch_spread 05:20-05:30;
  - arm: standard 05:30-05:49, latching 05:49-06:18, heldout 06:18-06:25,
    latch_spread 06:25-06:41.
- After the run, `TABLES.md`, `AUDIT_TABLES.md`, `PAIRED_TABLES.md` and
  `HEADLINE_TABLES.md` were made with the pre-registered commands.
- A post-run check reran some benchmark_v0.2e trials on the benchmark_v0.2d code. It is
  not part of this run; see `../v0.2e_postrun_check/` and `REPORT.md`.
