# heldout2_v0.2f pre-registration

Written and committed before the run. Nothing below changes after the first trial of the
reported seed has run. If the run exposes a bug, the bug gets a fix, a new
pre-registration and a fresh seed. No result is read until both runs have finished; a run
that stops early is repeated with the same command, and `RUN_LOG.md` says so.

## Question

The W2 `heldout` suite was used in W4 development (`results/w4_development/REPORT.md`,
lines 7-10), so it is no longer an out-of-sample test. This run is a new, clean held-out
test of the frozen v0.2e controllers on five families of disturbance that no one has
developed against.

Published results, read post hoc (`results/benchmark_v0.2e`, and the evidence analysis
on branch `v0.2f/pack`): C's standard-suite lead over I sits in high camera error
(vision sigma 1-2 mm, `generalization_combined`); C loses to I on `heldout_worst_case`,
the 1.5 mm hand-eye bias and arm friction 1.0; C's 0 bad units come from its VERIFY.
The question here is whether those patterns hold on disturbances nobody developed
against:

1. Does C seat more good parts than the best fair baseline (D, E, F, H, I), per machine
   and family, and per machine over the whole suite?
2. Does C pass fewer bad units than H and I?
3. Does G add anything over C? How does J compare with C and with I?

The families were chosen from the lead agent's candidate list for a physical basis and
for being new, not for how C or any baseline might do on them. They were fixed before
any trial of them ran (code commit 6ccb8ea).

## Families and levels

All five use the `MODERATE` backdrop of the noise and friction sweeps (socket up to 3 mm
off, yaw up to 5 deg, tilt up to 3 deg, all seen by the camera) and nominal sensors
(vision sigma 0.3 mm). Each adds one error no sensor reports. Controllers are told the
nominal accuracy (`characterized_noise` = nominal) and the drawing, as the README's
"what C is told" rules say: the connector drawing, the programmed socket pose, the
fixture limits and the characterized vision accuracy, never the error itself. None of
the ten conditions is in `standard`, `heldout`, `latching` or `latch_spread`: in those,
socket tilt and yaw are seen by the camera, in-hand errors are measured
(`generalization_combined`), the F/T bias is constant and tared out, and clearance is
told when it changes (`generalization_tight`, `heldout_worst_case`).

| Family | Part | Levels | What the controllers do not know | Basis |
|---|---|---|---|---|
| `h2_tilt_unseen` | housing only (`rect_12x8`) | 2 deg, 3 deg | The receptacle is tilted this much about a random horizontal axis, relative to what the camera measures. | A through-hole receptacle soldered proud on one edge: 0.5 mm and 0.75 mm over its 14 mm short-side footprint give 2 and 3 deg. A camera that locates the board (fiducials) does not see the receptacle's own tilt. The cavity admits about 3.8 deg (1.0 mm over 15 mm); the score allows 3 deg. |
| `h2_yaw_unseen` | housing only | 2.5 deg, 4 deg (random sign) | The receptacle is rotated this much about its axis relative to what the camera measures. | Receptacle rotated in its footprint, or a camera mount rotated about its optical axis after a knock. The 12 x 8 mm plug enters the 13 x 9 mm cavity up to about 4.7 deg; the score allows 3 deg, so 4 deg needs a correction. |
| `h2_ft_drift` | housing only | 0.1 N/s and 0.001 N m/s; 0.3 N/s and 0.003 N m/s | The F/T zero drifts linearly from the first reading (fixed random directions per trial), so the tare at home no longer holds. | Thermal drift of a strain-gauge sensor and changing cable drag as the tool moves. Over a 6-10 s cycle: 0.6-1 N and 1.8-3 N. The rates are assumed; no datasheet drift figure was checked. Torque/force ratio 0.01 m, the ratio of the config's own per-trial biases (0.003 N m / 0.3 N). |
| `h2_mf_tolerance` | Micro-Fit 3.0 latching | clearance 0.10 mm with lead-in 0.3 mm; clearance 0.05 mm with lead-in 0.2 mm | The simulated part is tighter than the drawing; the controllers are told 0.15 mm and 0.4 mm. | Plug at the top and cavity at the bottom of their moulding tolerance. The model's 0.15 mm clearance and 0.4 mm lead-in are already assumed (asset `basis`); the tolerance used here is assumed too (a typical +/-0.05-0.1 mm on moulded housings), not read from the Molex drawing. Mating forces, latch and terminals unchanged. |
| `h2_mf_grasp_unseen` | Micro-Fit 3.0 latching | 0.2 mm slip and 1 deg; 0.4 mm slip and 2 deg (each a random sign) | The plug sits off in the fingers along y and rotated about x (the grasp's free directions in the model), and the in-hand estimate does not see it. | A plug that slips in flat fingers on pick-up, in a cell without an in-hand camera that trusts the fingers to centre it. The rotation is about the grip centre, 12 mm above the tip, so 2 deg also moves the tip 0.42 mm. |

Implementation (commit 6ccb8ea): `defex/tasks/conditions.py` (`heldout2_conditions`),
`defex/tasks/scenarios.py` (the unseen errors and the true part are drawn after every
other value and only when set), `defex/tasks/insertion.py` (the camera and the in-hand
estimate measure the seen pose; controllers get the drawing), `defex/perception/sensors.py`
(F/T drift on its own random stream, spawned only when drift is on). No change in
`defex/control`, `defex/recovery` or `defex/sim`. Every earlier condition keeps its
exact draws: 44 development rows (seed 2026; standard, heldout and latching on the
gantry, standard on the arm; C, I and B or C and I) were identical before and after the
change, and `tests/test_heldout2_conditions.py` checks the draws, the levels, what the
controllers are told and the drift.

## Development smoke test, disclosed

As the brief allows: C only, seed 2026, 3 trials per condition, both machines
(`results/dev_h2_smoke_C`, not committed). C seated 30 of 30 on the gantry and 28 of 30
on the arm. The two failures on the arm: `h2_ft_drift_0.3` trial 0 was a false accept
(C declared success, not seated: a bad unit), and `h2_mf_tol_0.05mm` trial 0 aborted
(`defect_suspected:hard_stop_short`, a false reject of a good part that was not
seated). No level was changed after the smoke test. No baseline's rate was looked at
during development: a timing slice with all ten controllers (2 trials per condition,
seed 2026) was run only to size the run; its rows were deleted unread.

## Frozen code

- Controllers: v0.2e, commit **ddd0d34**, unchanged. `git diff --stat ddd0d34 6ccb8ea --
  defex/control defex/recovery defex/sim` is empty. G's model files unchanged, not
  retrained: `assets/models/contact_prior_gantry.json` sha256
  `650bfd824020594afbe5a579f61942e26d00011fc90943a6695cd78af795269b`,
  `assets/models/contact_prior_arm.json` sha256
  `c17fdb80fbd305431c7e7cb7d0e7be48d6354822abef543c11a4aebc8065b3b2`.
- Run code: commit **6ccb8ea** (the heldout2 suite on top of ddd0d34's code). The run
  starts from the commit that adds this file, which changes only `results/`. Every
  `config.json` must show `git_dirty: false`. `RUN_LOG.md` records
  `git status --porcelain --untracked-files=all` outside `results/` at the start, the
  environment, the start and end times and the workers.

## Design

- Base seed **20261207**. No file under `results/` contains it before this one.
- Backends `gantry` and `arm`. Controllers A-J: fixed, correction, adaptive, spiral,
  correction_rcc, spiral_rcc, adaptive_learned, spiral_pull, spiral_rcc_pull,
  spiral_rcc_verify. Fair baselines D, E, F, H, I. J is not a fair baseline (it has C's
  VERIFY).
- **40 trials per condition**: 10 conditions x 10 controllers x 40 x 2 machines = 8,000
  paired trials; 80 per family per machine, 400 per machine for the whole suite. Sized
  from a timing slice on seed 2026 at `--workers 2` with the machine at load 37-49:
  200 trials took 86 s on the gantry and 129 s on the arm, about 110 s per trial index
  over both machines, so 40 trials are about 70 minutes.
- Power, stated so it is not found later: with 80 paired trials per family a McNemar
  test needs a discordant split of about 9 / 1 or wider to reach p < 0.05 (10 / 1 gives
  p = 0.012, 8 / 1 gives 0.039, 7 / 1 gives 0.070). Small differences will read as
  "matches".
- Commands, in this order, from the repository root:

```
for B in gantry arm; do
  python -m experiments.robustness --suite heldout2 --backend $B --trials 40 \
    --seed 20261207 --workers 2 --no-plots --name heldout2_v0.2f/${B}_heldout2 \
    --controllers fixed,correction,adaptive,spiral,correction_rcc,spiral_rcc,adaptive_learned,spiral_pull,spiral_rcc_pull,spiral_rcc_verify
done
python -m experiments.checkpoint_report results/heldout2_v0.2f > results/heldout2_v0.2f/TABLES.md
python -m experiments.heldout2_tables results/heldout2_v0.2f > results/heldout2_v0.2f/HELDOUT2_TABLES.md
```

## Metrics

Per machine, per family (two levels pooled) and over the whole suite:

1. Success rate per controller with Wilson 95% intervals; exact McNemar against C on
   paired trials.
2. Bad units passed on good-part trials (declared or left as success, not seated, no
   protective stop; `checkpoint_report.escape`): count, Wilson 95% upper bound, C
   against H and against I, paired exact McNemar. Every heldout2 trial is a good part,
   so there is no deliberately-bad-part metric in this run.
3. G against C, paired.
4. J against C and J against I, paired: success, and bad units.
5. Cycle time p50 and p95 of successes, good units per hour (0 s and 60 s per
   protective stop), protective stops, per controller.

## Decision rules, fixed in advance

As in benchmark_v0.2e (which takes them from benchmark_v0.2d), applied per cell. A cell
is a machine and a family (10 cells); the same rules are also applied to each machine's
whole suite (2 cells).

- "Best" fair baseline = highest success rate in that cell among D, E, F, H, I; ties go
  to the first of D, E, F, H, I (on housing-only parts F and I are identical, so F).
- If the best fair baseline matches C (McNemar p >= 0.05, or C ahead by less than 1
  point), the cell reads "a fair baseline matches C".
- If C is below the best fair baseline with p < 0.05, the cell reads "C below".
- C is reported as ahead only where it beats the best fair baseline with p < 0.05.
- Bad units on good-part trials: C is reported as passing fewer (or more) than H or I
  only where p < 0.05; otherwise "no significant difference".
- G is reported as helping only where it beats C with p < 0.05; otherwise "no
  measurable gain", or "worse" where C beats it with p < 0.05.
- J against C and against I: seated "J ahead" or "J below" only with p < 0.05 (direction
  from the discordant pairs), otherwise "J matches"; no 1-point margin. Bad units: "J
  passes fewer" or "J passes more" only with p < 0.05, otherwise "no significant
  difference", always with counts and Wilson upper bounds.
- Totals pooled over machines are descriptive and get no test.
- There is no correction for multiple comparisons (about 12 cells x 7 tests). Any
  outcome resting on 0.01 <= p < 0.05 is marked as such in the report.
- Zero counts are given with their Wilson upper bound.
- C's and J's cycle time and throughput are reported next to their success rate,
  including where they are worse.
- Whether these results change the pitch is Hasan's decision; the report does not
  pick it.

## Expected, from the published results only

These come from `results/benchmark_v0.2e/TABLES.md`, not from any heldout2 trial (C's
smoke-test rows above are disclosed separately and were not used here).

- With nominal vision (`noise_0mm`, `noise_0.5mm`, `mf_moderate`) C and the best fair
  baseline both seat close to 100% on both machines in v0.2e. The heldout2 families keep
  nominal vision, so a "matches" in most cells would be consistent with the published
  pattern that C's lead sits in high camera error.
- The unseen tilt and yaw families resemble the hand-eye bias family in kind (a pose
  error nobody told the controller), where I seated 100 of 100 on both machines and C 95
  (gantry) and 94 (arm).
- Bad units: on housing-only conditions in v0.2e, H and I passed tens of bad units and
  C none; on Micro-Fit good parts H passed 0 and I 0-3. Expected: C fewer than H and I
  on the housing-only families if their counts are large enough for p < 0.05 with 80
  trials, and no significant difference on the Micro-Fit families.

## Disclosed before the run

- Development seeds 2026 and 2027 have been used for every controller decision since
  W1; this suite was never run on them except the C-only smoke test and the unread
  timing slice above.
- The levels are a judgement, set before any trial; two of the bases (F/T drift rate,
  Micro-Fit tolerance) are assumed, not from a datasheet.
- The unseen socket rotation turns the socket about its mouth centre. A real receptacle
  lifted on one edge turns about that edge, which would also move the mouth by up to
  about 0.5 mm; that shift is not modelled.
- The in-hand slip is rigid for the whole cycle: the plug does not slip further on
  contact.
- 40 trials per condition is small; see Power above.
