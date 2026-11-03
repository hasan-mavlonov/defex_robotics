# Replay run log

Code 2dc7009 (v0.2f/pack), seed 20261130, `--workers 2`, controllers
adaptive,spiral_rcc,spiral_rcc_pull,spiral_rcc_verify, run one after another by a shell
loop (`experiments.robustness --suite S --backend B --trials N --seed 20261130 --workers 2
--no-plots --name v0.2f_evidence/replay_20261130/B_S --controllers ... --conditions ...`).

| Run | Conditions | Trials per condition | Start | End |
|---|---|---|---|---|
| gantry standard | noise_1mm, noise_2mm, generalization_combined | 100 | 15:19:44 | 15:25:07 |
| gantry heldout | heldout_mischar_1mm, heldout_mischar_2mm, heldout_worst_case | 100 | 15:25:07 | 15:34:59 |
| arm standard | noise_1mm, noise_2mm, generalization_combined | 100 | 15:34:59 | 15:52:48 |
| arm heldout | heldout_mischar_1mm, heldout_mischar_2mm | 100 | 15:52:49 | 16:04:24 |
| gantry latching | mf_noise_1mm | 200 | 16:04:24 | 16:15:05 |
| arm latching | mf_noise_1mm | 200 | 16:15:05 | 16:37:17 |

Total 77.5 minutes on 2026-11-02, against the 52 estimated in `RUN_PLAN.md` and the 60
minute cap. The machine was shared with other agents (load average 9-24). The latching
runs were not dropped; the cap was passed during the last one.

`git_dirty` is False for the first run and True for the other five. During the replay the
analysis files `experiments/v02f_evidence.py` and `tests/test_v02f_evidence.py` were
edited; neither is used by the runner. Every committed column of all 6,000 replayed rows
equals benchmark_v0.2e (`../TOLERANCE.md` (1)).

`events.json.gz` was deleted, not committed. No reported number needs it.
