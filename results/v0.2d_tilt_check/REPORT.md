# v0.2d tilt check: report

Development work on `v0.2d/tilt-check` (from `v0.2c/next` b94b971). Simulation only.
Ground truth fails a plug tilted more than 3.0 deg. C's VERIFY did not look at tilt.
Commands: [`run.sh`](run.sh). Rule, committed before the runs it ranks:
[`SELECTION_RULE.md`](SELECTION_RULE.md) (91bfd9a).

## Diagnosis

Design data: C, training seeds 3001-3030, 40 trials ([`DESIGN_TABLES.md`](DESIGN_TABLES.md), `design/`).

| Machine, VERIFY | Trials | Declared seated | Tilt escapes |
|---|---|---|---|
| arm, latching (`mf_noise_1mm`) | 1,200 | 977 | 3 |
| gantry, latching | 1,200 | 1,037 | 0 |
| arm, housing only (`noise_1mm`, `noise_2mm`, `friction_1`) | 3,600 | 3,085 | 1 |
| gantry, housing only | 3,600 | 3,439 | 1 |

**Latching, arm (seeds 3004/17, 3015/20, 3024/3).** The rate-mode top-face conform
turns the plug to its 3.89 deg limit on both axes. The plug slides into the lead-in
during the conform, and INSERT keeps that rotation. The plug enters about 5 deg
tilted. The in-cavity tilt compliance only turns it back until the wall torque is
inside its dead band. The plug then latches wedged at the cavity's tilt limit: the
Micro-Fit's 0.30 mm clearance allows 2.26 deg per axis at 7.7 mm engaged, and 3.20 deg
on the diagonal. The escapes are at 3.17-3.26 deg, 7.73 mm deep, at the cavity
corner. Push-click-pull passes.

At the bottom, C can see two things. Its plug axis is 3.4-3.5 deg off its own
socket-axis estimate. The bottoming CoP is at 0.89-1.10 of the half-width, against a
median of 0.58 in seated good parts (the floor takes the push at a corner; terminal
and latch forces act at the centre).

**Latching, gantry.** No escape. The soft wrist lets the walls straighten the plug
(median true tilt 0.04 deg, against 0.81 on the arm).

**Housing only.**

- Arm 3009/0: 3.09 deg about y, from the camera's tilt error. The seat conform stopped
  its y axis on the first tick, at low axial force. The wall probes run along y and do
  not see tilt about y.
- Gantry 3021/21: 3.05 deg about x. The 0.8 s admittance seat conform turned the plug
  by 1.0 deg and ran out of time. This matches the undiagnosed mode in
  `results/v0.2c_verify_fixes`.

The rect cavity allows 3.9 deg per axis, so these plugs are not wall-held. Good
passes at least as extreme as the escape (arm of 3,084 / gantry of 3,438):

| Observable | Arm | Gantry |
|---|---|---|
| plug axis off the estimate | 1,949 | 186 |
| CoP after the seat conform | 2,493 | 299 |
| y-wall free travel | 18 | 161 |
| seat conform left an axis not flat (arm) | 708 | - |

On the gantry, 330 passes timed out in the seat conform. No signal C has separates
these escapes from good passes, so no housing-only check was proposed.

## The check

`AdaptiveConfig.tilt_check`, `tilt_check_deg = 2.5`, `tilt_check_edge_fraction =
0.875`. VERIFY fails at the start of the latch check when the plug axis is more than
`tilt_check_deg` off C's socket-axis estimate (camera plus flat-face folds, `R_corr`)
**and** the bottoming CoP is beyond `tilt_check_edge_fraction` of the half-width. A
failure takes the normal failed-VERIFY path. A latched plug is held by the retract
cap, re-seated and re-checked; within the attempt a plug still turned past the bound
fails again, and C leaves it declared not seated (`aborted:stuck_during_retract`).
Both inputs are controller-visible (encoders, F/T, C's own estimates).

## Selection (dev seeds; [`selection/TABLES.md`](selection/TABLES.md))

- S1: latching + latch_spread, seeds 2026/2027, 100 trials. S2: `mf_noise_1mm`, seeds
  3033-3040, 100 trials. C and G, both machines, 16,000 base trials (code 91bfd9a).
- Only trials where a candidate acts were re-run (f5f1356). The 276 re-runs where the
  check never failed matched their base trials.
- Base tilt escapes: 8 (arm latching C 3, G 4; gantry latching C 1).

| Candidate | Escapes left | Net good lost (allowed) | Result |
|---|---|---|---|
| tilt_k1 (2.0, 0.875) | 3 | 7 (10) | passes |
| tilt_k2 (2.5, 0.875) | 3 | 3 (10) | passes, selected |
| tilt_k3 (1.5, 0.75) | 2 | 11 (12) | fails G4: 2 extra protective stops in the arm latching C cell and in both arm latch_spread cells |

For tilt_k2: false rejects and bad parts passed are unchanged (0) everywhere. It adds
1 stop in four arm cells. It never acts on the gantry.

- Removed escapes became time limits (2027/86 C and G, 3040/78 G) or a protective stop
  on the retract (2027/40 C and G).
- Lost good parts: 2026/37 C and G (left in place at 2.74 deg true tilt) and 3035/11 G.
- Escapes left:
  - 3037/31 C: CoP 0.87.
  - 3035/81 G: a wrong flat-face fold, plug axis 0.08 deg off the estimate, true tilt
    3.24 deg.
  - Gantry 3037/87 C: checked after a held re-seat, axis 1.63 deg off, CoP 0.56.

## Validation (seed 4003, once, tilt_k2; [`validation/TABLES.md`](validation/TABLES.md))

**GO.**

- One trial acted on (G arm `mf_noise_1mm` 7: axis 4.53 deg off, true tilt 2.55 deg),
  which ended in a time limit: 1 good part lost (allowed 2).
- Tilt escapes 1 / 1: G `mf_noise_1mm` 77, axis 1.36 deg off, CoP 0.87, not acted on.
- No change in stops, bad parts passed or false rejects. Nothing acted on the gantry.

## Equivalence (`equivalence/`)

b94b971 against aa1d4d6 (tilt_k2 installed), dev seed 2026, latching suite +
nominal/noise_1mm/noise_2mm, 20 trials, C and G, both machines: 800 trials, 28,000
`trials.csv` fields, 0 differences (wall time ignored). 618 tilt verdicts were logged,
all PASS.

## Uncertain

- Escapes are rare: 8 on 16,000 dev trials, 1 on 3,200 arm validation trials. The
  check removed none on 4003.
- A wrong flat-face fold, or a CoP just under the bound, defeats it. An edge-only rule
  would act on about 3 times more good-part trials (61 against 19; 9 times on seated good parts, 36 against 4; selection data, not a tested candidate).
- It flags in-spec plugs at the wall limit (2.4-2.9 deg).
- Retracting a wedged plug can trip the 0.6 N m stop.
- The collector missed latch checks after a held re-seat in 92 gantry selection
  trials. Fixed and re-run (44ea9a7); the selection was unchanged, but the validation
  had already started.
- Housing-only tilt escapes remain (about 1 per 3,100-3,400 noisy passes per machine).
- All of this ran at the 30 N insert target (b94b971 base); not yet tested at 35.2 N.
- Not tested for J.
