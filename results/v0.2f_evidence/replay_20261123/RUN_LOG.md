# Replay run log, seeds 20261123 and 20261124

Code a57f4ad (branch v0.2f/replay-v02d: 42df5c8 + logging-only 22ef683 + the plan),
`git_dirty` False on all 12 configs. Controllers adaptive, spiral_rcc, spiral_rcc_pull,
spiral_rcc_verify. `--workers 6`: the 1-minute load was 4.23 at the start, above the limit
of 4 for 8 workers. Conditions as in `RUN_PLAN.md`. Outputs in `replay_20261123/` and
`../replay_20261124/`.

| Seed | Run | Start | End |
|---|---|---|---|
| 20261123 | gantry standard | 18:41:52 | 18:43:29 |
| 20261123 | gantry heldout | 18:43:29 | 18:45:24 |
| 20261123 | arm standard | 18:45:24 | 18:48:43 |
| 20261123 | arm heldout | 18:48:43 | 18:51:00 |
| 20261123 | gantry latching (mf_noise_1mm) | 18:51:00 | 18:53:08 |
| 20261123 | arm latching (mf_noise_1mm, mf_nominal) | 18:53:08 | 18:58:59 |
| 20261124 | gantry standard | 18:58:59 | 19:00:36 |
| 20261124 | gantry heldout | 19:00:36 | 19:02:25 |
| 20261124 | arm standard | 19:02:25 | 19:05:35 |
| 20261124 | arm heldout | 19:05:35 | 19:07:43 |
| 20261124 | gantry latching (mf_noise_1mm) | 19:07:43 | 19:09:43 |
| 20261124 | arm latching (mf_noise_1mm) | 19:09:43 | 19:13:19 |

Total 31.5 minutes on 2026-11-02 (estimate about 32). Load rose to 6-10 during the run
(other agents). `events.json.gz` deleted, not committed; no reported number needs it.
