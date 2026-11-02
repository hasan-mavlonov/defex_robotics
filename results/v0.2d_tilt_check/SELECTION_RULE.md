# v0.2d tilt check: selection rule

Written and committed before any run it ranks. Development seeds only; validation seed 4003
is run once, at the end, for the go/no-go. Seeds 20261102, 20261116 (spent), 20261123
(reserved) and 4002 (spent) are not run.

## What is being chosen

Whether controller C (and G, which shares C's VERIFY) gets a tilt check at the start of the
latching VERIFY (`AdaptiveConfig.tilt_check`, default off), and with which bounds. VERIFY fails,
and C takes the normal failed-VERIFY path, when both hold:

* the measured plug axis is more than `tilt_check_deg` off C's socket-axis estimate (camera,
  plus the tilts measured by flat top-face conforms, `R_corr`);
* the centre of pressure of the bottoming wrench (recent samples, first third discarded) lies
  beyond `tilt_check_edge_fraction` of the plug's half-width on an axis.

Within the attempt that failed it, a plug still turned beyond `tilt_check_deg` fails again
(after a held retract the re-seat unloads the walls; the plug has not left the cavity).

Candidates (`variants.json`):

| Candidate | `tilt_check_deg` | `tilt_check_edge_fraction` |
|---|---|---|
| tilt_k1 | 2.0 | 0.875 |
| tilt_k2 | 2.5 | 0.875 |
| tilt_k3 | 1.5 | 0.75 |

They come from the design data (`design/`, training seeds 3001-3030, C only): on the arm,
`mf_noise_1mm`, 1,200 trials, the three tilt escapes all had a plug axis 3.4-3.5 deg off the
estimate and a bottoming CoP at 0.89-1.10 of the half-width; seated good parts sat at a median
0.58 of the half-width. On the gantry (1,200 trials) no latching plug passed tilted and no
candidate would act.

The housing-only VERIFY gets no candidate. In the design data each machine had one tilt escape
in about 3,100-3,400 passes (arm: seed 3009, `noise_2mm`, trial 0; gantry: seed 3021,
`noise_2mm`, trial 21). Every observable looked at (plug axis against the estimate, seat-conform
outcome per axis, CoP after the seat conform, seat-conform timeout) is shared by hundreds of
good passes; see REPORT.md.

## Data for the selection (none of it used for the design)

* S1: the `latching` and `latch_spread` suites (16 conditions), seeds 2026 and 2027, 100 trials
  per condition, gantry and arm, C and G.
* S2: `mf_noise_1mm`, seeds 3033-3040, 100 trials per seed, gantry and arm, C and G.

Procedure (commands in `run.sh`): C and G run with the check off through
`experiments.v02d_tilt_features`, which records the check's evidence at every start of a latch
check. The evidence is a pure function and a passing verdict changes no state, so a candidate
changes a trial only from the first latch check where its verdict fails. Those trials are re-run
with the candidate on (`adaptive@tilt_kN`, `adaptive_learned@tilt_kN`); every other trial is the
base trial. The housing-only suites cannot reach the check (`_begin_latch_verify` runs only for
latching parts), so they are not re-run; the equivalence run shows both claims.

## Measures, per cell (machine x suite x controller)

* Tilt escapes: good-part trials declared seated, not seated in ground truth, final tilt above
  3.0 deg, no protective stop.
* Good-part successes lost (seated with the check off, not with it on) and gained; net loss.
* False rejects (seated in ground truth, declared failed).
* Other escapes (declared seated, not seated, tilt within 3.0 deg), bad parts passed (bad-part
  conditions declared seated), protective stops.

## Gates (a candidate passes if all hold on S1 + S2)

* G1: it removes at least half of the base tilt escapes, and at least one. With no base tilt
  escape on S1 + S2 no candidate passes and the check is not installed.
* G2: net good-part successes lost, summed over all cells, at most 2 x the tilt escapes removed;
  in every cell at most max(2, 1% of the cell's good-part trials).
* G3: false rejects added in every cell at most max(2, 1% of the cell's good-part trials).
* G4: in no cell more bad parts passed, more other escapes, or more than one extra protective stop.

Among passing candidates: fewest tilt escapes left; then smallest net loss; then fewest trials
acted on. If none passes, the check stays in the code switched off, and the report says why.

## Validation (seed 4003, once, the chosen candidate only)

Same suites as S1 (latching and latch_spread, 16 conditions, 100 trials), gantry and arm, C and G,
same procedure. GO, and `tilt_check` becomes the default with the chosen bounds, if:

* tilt escapes with the check at most those without;
* G2 with the allowance 2 x max(1, tilt escapes removed), G3 and G4 as above.

Otherwise NO-GO: the default stays off. The tables come from
`python -m experiments.v02d_tilt_select table ... --validation`.

## Equivalence

After the decision, C and G with the installed setting (or the candidate, if NO-GO) against the
code before this work (b94b971), through `experiments.robustness`, on dev seed 2026: gantry and
arm, the latching suite (20 trials) and nominal / noise_1mm / noise_2mm (20 trials). Every
`trials.csv` field except `wall_time_s` must match, or the difference must be a trial where the
check failed (a `tilt ... FAIL` event).
