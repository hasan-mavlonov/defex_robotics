# Earlier benchmark runs (superseded)

These reports are kept so the run history in the top-level README can be checked.
Each run exposed a defect that was fixed before the reported run 3.

| File | Seed | Commit | Defect it exposed |
|---|---|---|---|
| `run1_seed20261024_commit33a624b_report.md` | 20261024 | `33a624b` | C's verification probes started before the axial preload settled; at mu = 1.0 floor friction stopped every probe before the walls did |
| `run2_seed20261025_commit01105e6_report.md` | 20261025 | `01105e6` | C's abort zeroed its compliance offsets while the plug was still in the cavity; one aborted trial tripped the torque stop |

Run 3 (the parent folder) uses seed 20261025 and commit `4510f7f`. Its success
outcomes match run 2 trial for trial; only the failure mode and retract timing of
aborted C trials changed. Run 1's other metrics are not comparable trial by trial,
since it used a different seed. Re-create either run with
`git checkout <commit> && python -m experiments.robustness --trials 100 --seed <seed> --record 1`.
