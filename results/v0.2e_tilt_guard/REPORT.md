# v0.2e tilt guard: report

Branch `v0.2e/tilt-guard` from 966a5f5 (code c60e2a5, evidence f69528a). Simulation
only. Dev seeds 2026 and 2027 only. Commands: `run.sh`. Collector and tables:
`experiments/v02e_tilt_guard.py`. Paired tables: `TABLES.md` (C, G, J) and `OTHERS.md`
(A, B, D, E, F, H, I). Raw rows: `runs/`. Written by the lead from the development
agent's report (the agent could not create report files).

## The gap

The benchmark_v0.2d pre-registration says: "On C's arm floor-impact path its window can
be at a few newtons (no force guard)." `_tilt_evidence` divides the window torque by
max(Fz, 1e-9). At low force any leftover torque reads as a centre of pressure far past
the edge, and the verdict then rests on the axis estimate alone. Two paths into
`_begin_latch_verify` have no force guarantee: the arm's floor-impact settle and a
timed-out proof push (1.5 s). The bottomed, stall, held re-seat and held proof paths
require at least 0.7-0.8 x the insert target. J's hand-over window is empty.

## What the design and selection assumed

No force threshold was ever stated. The design text reasons about "the bottoming
wrench", and its tables took the CoP from the DETECT diagnosis, which has no CoP below
2 N. In the design and selection files (30 N code), the DETECT axial force at every
VERIFY start was at least 13.3 N; those files do not hold the check's own window force.

## The guard

`AdaptiveConfig.tilt_check_force_guard = True`. Floor = `cavity_tilt_lever_mm` x insert
target / (`tilt_check_edge_fraction` x smaller plug half-width) = 1.0 mm x 35.2 N /
(0.875 x 3.425 mm) = 11.75 N. Under the floor, or with no samples, the check gives no
verdict, the same as `tilt_check` off; it also applies to the re-check after a failed
check in the same attempt. Why this floor: C's tilt dead band leaves up to 1 mm x force
of torque on the plug while it pushes at the target; at a lower window force that reads
as a CoP of 1 mm x 35.2 N / F, which reaches the 3.0 mm edge bound at 11.75 N. It was
fixed before any run and uses no new number. Nothing new is imported under
`defex/control`.

## Results

Paired 966a5f5 against the branch, same collector: C, G and J; arm and gantry;
`latching` and `latch_spread` (16 conditions), 20 trials, seeds 2026 and 2027; 3,840
trials per version.

| | Count |
|---|---|
| Tilt verdicts before | 4,822 |
| Under the floor before | 1,120, all PASS |
| of which C and G, arm floor impact | 8 (4 trials, each in C and G) |
| of which J, empty hand-over window | 1,112 (562 arm, 550 gantry) |
| Blocked by the guard | 1,120 |
| Trials whose row changed | 0 |

The 8 floor-impact verdicts were at 8.2-10.3 N, with the plug axis 0.83-2.30 deg off
the estimate and CoP 0.03-0.06 of the half-width. Window forces at the other verdicts:
arm bottomed 28.1-35.3 N, stall 23.0-28.1 N, proof 34.7-35.1 N, floor impact 8.2-16.7 N;
gantry bottomed down to 20.1 N. No proof push timed out. The two failing verdicts (arm
`mf_terminal_max_broken_latch`, seed 2026, trial 12, C and G) were at 29.3 N and are
unchanged. The low-force wrong verdict the guard removes did not occur on these seeds;
only the unit tests show it. Other controllers (A, B, D, E, F, H, I), seed 2026, 2
trials per condition, both suites and machines: 448 trials, 0 changed.

## Folds and re-aims (disclosed in v0.2d, not changed)

The guard reads only the window's axial force; it does not touch `R_corr` or the axis
comparison. On verdicts it keeps, a wrong fold or re-aim defeats the check exactly as
before.

## Tests

7 new tests in `tests/test_tilt_check.py`; full suite on the branch: 202 passed.

## Not done

No validation or reserved seed; no 30 N run; the other-controller check is small.
