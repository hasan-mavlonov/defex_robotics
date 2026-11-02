# benchmark_v0.2d_rep run log

- Pre-registration: `PREREGISTRATION.md`, committed in 4060e8b on v0.2d/integration
  before the run. 4060e8b changes nothing outside `results/` since 42df5c8
  (`git diff --stat 42df5c8 4060e8b -- . ':(exclude)results'` is empty). The run used a
  separate worktree on branch `v0.2d/replication` at 4060e8b.
- Started 2026-11-02 01:37 PST, finished 03:55 PST (2 h 18 min), `--workers 9`, the
  pre-registered commands in order. Three development agents (one core in all) and a
  read-only audit ran on the same machine during the run; they wrote only to other
  worktrees.
- All eight `config.json`: `git_commit` 4060e8b6745bbcb3438d5ab227febbc1304c4ba3,
  `git_dirty: false`, `base_seed` 20261124, `workers` 9.
- At the start `git status --porcelain --untracked-files=all` outside `results/` in the
  run worktree was empty (fresh `git worktree add`).
- Rows in `trials.csv`: per machine standard 20,000, latching 14,000, heldout 5,000,
  latch_spread 9,000; 96,000 in all, as pre-registered.
- Environment: Python 3.12.11, MuJoCo 3.17.0, NumPy 2.5.4, macOS 27.0.1 arm64, 10 CPUs.
- Tables made after the run with the pre-registered commands: `TABLES.md`,
  `AUDIT_TABLES.md`, `PAIRED_TABLES.md`, `HEADLINE_TABLES.md`. No run was repeated or
  dropped.
