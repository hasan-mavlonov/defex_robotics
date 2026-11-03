# heldout2_v0.2f run log

- Pre-registration committed at 6ea164e (suite code 6ccb8ea; controllers as ddd0d34).
- Run started from commit **6ea164eb23248a9601d4587e81ba8390db6101bb**.
  `git status --porcelain --untracked-files=all -- . ':(exclude)results'` at the start: empty.
- Both `config.json` files: `git_commit` 6ea164e..., `git_dirty: false`, `workers: 2`,
  `base_seed: 20261207`, `n_trials_per_condition: 40`.
- Environment (`config.json`): Python 3.12.11, MuJoCo 3.17.0, NumPy 2.5.4, Apple Silicon Mac,
  10 cores shared with other agents. Load average 51 at the start, 47-51 after the gantry run,
  40 (1 min) / 88 (5 min) / 119 (15 min) at the end.
- Commands: exactly the pre-registered ones.

| Run | Start (UTC) | End (UTC) | Wall | Trials | Exit |
|---|---|---|---|---|---|
| gantry_heldout2 | 2026-11-02 23:38:13 | 2026-11-03 00:01:35 | 23 min 22 s | 4,000 | 0 |
| arm_heldout2 | 2026-11-03 00:01:35 | 2026-11-03 00:41:17 | 39 min 42 s | 4,000 | 0 |

Total 63 min 4 s for 8,000 trials (estimate in the pre-registration: about 70 min).
Neither run stopped early; nothing was repeated. No result was read before both runs had
finished. Tables made afterwards with the pre-registered commands: `TABLES.md`
(`experiments.checkpoint_report`) and `HELDOUT2_TABLES.md` (`experiments.heldout2_tables`).

Committed: `trials.csv`, `summary.json`, `summary.csv`, `config.json` per run. The
`events.json.gz` files (228 KB and 260 KB) are not committed; no reported number needs them.
