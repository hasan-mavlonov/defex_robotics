# Offline rule applied (stopping split, grid NLL of G's combined posterior, weight 1)

Source: `offline/gantry.json`, `offline/arm.json` (`offline.sh`; tables in `offline/tables.md`).
Candidates only; `g_v1` and `g_lp` are listed in the JSON for information (their stopping-split
numbers are partly in-sample: both were early-stopped on seeds 3026-3030).

| Backend | residual K=2 tempered | residual K=2 | residual K=3 | posterior K=3 | ratio K=3 | Carried to seed 4002 |
|---|---|---|---|---|---|---|
| gantry | 2.089 | 2.756 | 2.979 | 2.942 | 3.181 | residual K=2 tempered, residual K=2, posterior K=3 |
| arm | 1.962 | 3.472 | 3.231 | 3.258 | 3.839 | residual K=2 tempered, residual K=3, posterior K=3 |
