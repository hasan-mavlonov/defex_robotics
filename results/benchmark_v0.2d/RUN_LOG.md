# benchmark_v0.2d run log

- Pre-registration: `PREREGISTRATION.md`, committed in 966a5f5 (code frozen at 42df5c8;
  966a5f5 changes only `results/`).
- Started 2026-11-01 23:20 PST, finished 2026-11-02 01:36 PST (2 h 16 min), one machine,
  the pre-registered commands in order, `--workers 9`.
- All eight `config.json`: `git_commit` 966a5f54e86582c4b0c763eb2f2abaae486ec85a,
  `git_dirty: false`, `base_seed` 20261123, `workers` 9.
- Rows in `trials.csv`: gantry and arm each standard 20,000, latching 14,000, heldout
  5,000, latch_spread 9,000; 96,000 in all, as pre-registered.
- Environment (`config.json`): Python 3.12.11, MuJoCo 3.17.0, NumPy 2.5.4, macOS 27.0.1
  arm64, 10 CPUs.
- Per-run times (runner log): gantry standard 23:20-23:34, latching 23:34-23:58, heldout
  23:58-00:03, latch_spread 00:03-00:14; arm standard 00:14-00:35, latching 00:35-01:08,
  heldout 01:08-01:16, latch_spread 01:16-01:36.
- Tables made after the run with the pre-registered commands: `TABLES.md`,
  `AUDIT_TABLES.md`, `PAIRED_TABLES.md`, `HEADLINE_TABLES.md`. No run was repeated or
  dropped.
