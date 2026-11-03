# v0.2f latch fit: fitting the terminal and latch model to logged force-depth curves


Result: the fitter recovers 13 of the 14 judged quantities within the pre-committed
tolerance on the nominal part and on at least 9 of 10 off-nominal parts. The latch
hook stiffness fails the rule (nominal within; 6 of 10 off-nominal within, the rule
needs 8). By RULE.md, the fitter as a whole therefore **fails** the synthetic recovery
rule. The failure appears only on parts with high terminal friction on the compliant
(10 N/mm) simulated gantry. With a 200 N/mm servo the same parts give 11 of 11.

All of this is synthetic. The curves come from the MuJoCo simulator, and the fitting
model has the same form as the one that made them. Recovering synthetic parameters is
not the same as fitting a real curve. It shows that the fitter and its optimizer
work, and that they handle noise, bias, depth offset and rig dynamics. It does not
show that a real Micro-Fit follows this model.

Pass rule: RULE.md, committed at b00e936 before the run. Run: summary.json
(git_commit b00e936). Its git_dirty is true only because experiments/latch_fit_tables.py
was an untracked new file during the run. The run does not import it, and the dirty
check now ignores untracked files. Rows: recovery.csv (8 designs x 11 parts x 14
quantities). Tables: `PYTHONPATH=. python -m experiments.latch_fit_tables`.

## What the fitter does

defex/calibration/latch_fit.py uses numpy only, with no MuJoCo; a test checks this.

- Input: one or more logged moves of one part. Each move is a CSV `t_s,depth_mm,fz_n`
  in the convention of hardware/TEST_PROTOCOL.md section 4: depth is positive into
  the socket, and force is positive pushing the plug out. A move is a slow guarded
  push on the socket axis to the floor. It can be followed by a guarded pull in the
  same file. The fitter splits a move at its deepest point. It uses the pull only up
  to its first rebound: a stiff hook caught by a compliant servo rings, and the model
  is quasi-static. A move can be marked `latch=False`, meaning a push with the latch
  disabled.
- Model: the piecewise-linear shapes of defex/sim/mating.py. A test checks that the
  forward model equals `MatingForce.axial_force` along a push and pull, for three
  parts, to within 1e-6 N. There are 12 part parameters:
  - terminals: wipe, lead, peak force, slide force;
  - latch: rise, peak force, fall, snap drop, post-snap stroke;
  - from a pull: the hook's free play, its stiffness, and the terminals'
    pre-sliding (bristle) length.

  Snap drop is an extension. mating.py drops the latch force to zero at the snap
  (drop = 1). The fit leaves it free, so a real latch that keeps some ramp force after
  the click shows as drop < 1. The nuisance parameters are, per move, the seat depth
  in the logged frame (the depth offset) and a force offset (imperfect tare), plus one
  floor stiffness.
- All depths are fitted as distances back from the seat. With a free depth offset,
  absolute depths cannot be identified; the seat (where the floor starts) anchors
  them. `LatchFit.mating_depths_mm` converts back to the simulator's mouth-referenced
  depths, with the seat at the drawing's socket depth.
- Not fitted: the latch retention (a guarded pull at 50% of it never breaks the latch)
  and the defect end stops.
- Objective: soft-L1 (smooth Huber) on the residual. The data are binned at 0.01 mm
  of logged depth (median force per bin, push and pull separately), and the loss
  scale is three times the free-space noise. The intent is the same as the median
  objective of contact_fit.py: robust to spikes and to unmodelled dynamics. Unlike a
  plain median, it does not ignore features that cover less than half the samples.
  The click is 0.1 mm of a 9 mm move, and a plain median would not see it.
  Minimizer: projected Levenberg-Marquardt with reweighting, from 24 starts. A fit
  takes about 2 s.
- Which parameters are free depends on the data (`identifiable()`):
  - terminals: from any move;
  - latch shape: from a latched push;
  - snap drop: only with a latched pull or a latch-disabled push;
  - play, hook stiffness and bristle: only with a latched pull.

Tools:
- experiments/latch_fit_sim.py makes the synthetic logged move on the MuJoCo gantry.
  It does a guarded push to the 35.2 N insert target and a guarded pull to 29 N, and
  logs every 2 ms through SensorSuite: F/T bias 0.3 N untared, noise 0.03 N, encoder
  noise 0.002 mm, plus a depth offset.
- experiments/latch_fit_report.py is the overlay report, with a CLI for the rig day:
  `PYTHONPATH=. python -m experiments.latch_fit_report --csv a.csv [--csv b.csv] [--disabled c.csv] --out DIR`.
  It writes two files:
  - latch_fit.png: logged and fitted force against seat-referenced depth, and the
    residual against a +/-15% band;
  - latch_fit.json: the fitted values, the values to put in the connector JSON's
    `model` block, and the four values that have no place in the JSON.
- experiments/latch_fit_recovery.py runs this study. experiments/latch_fit_tables.py
  prints the tables below.

## Recovery (judged design: one push + guarded pull at 1 mm/s per part)

Seed 2026 (development). The parts are the nominal part plus 10 parts drawn uniformly
in the latch_spread bands (RULE.md lists them). Tolerance is max(15% of truth, floor);
the floors are 0.03 mm, 0.5 N, and 0.15 for snap drop. Source: recovery.csv,
summary.json.

| quantity | truth (nominal) | nominal error | tolerance (nominal) | off-nominal within | worst abs error, 11 parts | pass |
|---|---|---|---|---|---|---|
| terminal wipe (mm) | 1.75 | -0.010 | 0.26 | 10/10 | 0.022 | PASS |
| terminal lead (mm) | 0.3 | +0.003 | 0.045 | 10/10 | 0.004 | PASS |
| terminal peak, 4 circuits (N) | 20 | +0.06 | 3.0 | 10/10 | 0.81 | PASS |
| terminal slide, 4 circuits (N) | 12 | -0.009 | 1.8 | 10/10 | 0.017 | PASS |
| latch onset to seat (mm) | 1.6 | -0.007 | 0.24 | 9/10 | 0.220 | PASS |
| latch rise (mm) | 1.0 | +0.003 | 0.15 | 9/10 | 0.231 | PASS |
| latch peak (N) | 6 | -0.012 | 0.9 | 10/10 | 0.136 | PASS |
| latch fall (mm) | 0.1 | +0.023 | 0.03 | 10/10 | 0.026 | PASS |
| snap drop (fraction) | 1.0 | 0.000 | 0.15 | 10/10 | 0.012 | PASS |
| post-snap stroke (mm) | 0.5 | -0.033 | 0.075 | 10/10 | 0.033 | PASS |
| latch play (mm) | 0.1 | +0.022 | 0.03 | 10/10 | 0.025 | PASS |
| latch stiffness (N/mm) | 200 | -1.6 | 30 | 6/10 | 157 | **FAIL** |
| bristle (mm) | 0.05 | -0.002 | 0.03 | 10/10 | 0.009 | PASS |
| depth offset (seat error, mm) | 0 | -0.011 | 0.03 | 10/10 | 0.022 | PASS |

Overall by the rule: FAIL (latch stiffness).

Where it misses, and what is systematic:
- **Latch stiffness** misses on off03, off07, off08 and off09 (fitted 141, 118, 43 and
  149 N/mm, against 200). These are the four parts with terminal scale 1.36 to 1.56.
  The guarded pull stops at 29 N, so the hook carries only 29 - 12 x scale = 10 to
  13 N, about 0.05 mm of spring. On the 10 N/mm gantry the plug rings on the hook
  within that stretch. All 11 parts pass with a 200 N/mm servo and at 2 mm/s; 7 pass
  at 0.5 mm/s.
- **Latch rise and onset** miss once (off09, +0.23 mm). Its latch onset (6.56 mm)
  falls on the terminal peak (6.55 mm), so the onset kink is hidden in the terminal
  kink. The terminal peak error on that part is -0.81 N, which is within tolerance.
- **Small biases appear on every part:**
  - seat: -0.002 to -0.022 mm;
  - post-snap stroke: -0.017 to -0.033 mm;
  - latch fall: +0.01 to +0.026 mm;
  - play: +0.003 to +0.025 mm.

  The seat and post-snap biases come from the soft MuJoCo floor contact: the linear
  floor model puts the seat a little shallow. Fall and play sit close to their
  0.03 mm floor. On the compliant gantry the click is a snap-through (see
  Identifiability), so only 1 to 3 samples trace the fall.

### Diagnostics (not judged; same 11 parts)

Parts within tolerance, out of 11 (recovery.csv):

| quantity | main | F/T noise x10 | push only | 0.5 mm/s | 2 mm/s | 5 mm/s | 200 N/mm servo | + latch-disabled push |
|---|---|---|---|---|---|---|---|---|
| terminal wipe, lead, peak, slide | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 |
| latch onset to seat, rise | 10 | 11 | 11 | 10 | 11 | 10 | 11 | 11 |
| latch peak | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 |
| latch fall | 11 | 9 | 11 | 11 | 11 | 11 | 11 | 11 |
| snap drop | 11 | 11 | fixed | 11 | 11 | 11 | 11 | 11 |
| post-snap stroke | 11 | 11 | 10 | 11 | 11 | 11 | 11 | 11 |
| latch play | 11 | 11 | fixed | 11 | 11 | 9 | 11 | 11 |
| latch stiffness | 7 | 10 | fixed | 7 | 11 | 10 | 11 | 7 |
| bristle | 11 | 11 | fixed | 11 | 11 | 11 | 11 | 11 |
| depth offset | 11 | 11 | 10 | 11 | 11 | 11 | 11 | 11 |
| median abs residual, N (median part) | 0.020 | 0.108 | 0.025 | 0.017 | 0.026 | 0.037 | 0.016 | 0.019 |

recovery_nominal_overlay.png overlays the nominal synthetic case: logged, fitted and
true model, and the residual against the +/-15% band.

## Identifiability

There are two sources, both in summary.json. One is the recovery runs above. The
other is a local study (`identifiability`): parameter correlations from the
Gauss-Newton information matrix of the fitter's own model at the nominal part, with
0.03 N noise per 2 ms sample at 1 mm/s.

1. **Absolute depth trades against the depth offset, with one curve or many.** Every
   depth feature moves with the unknown zero of the logged depth. Only distances from
   the seat can be identified, so the push must reach the floor. The absolute depths
   in the connector JSON then rest on the drawing's socket depth (8.0 mm, assumed).
2. **Terminal slide trades against snap drop and latch peak (push only).** After the
   click, the push sees slide + (1 - drop) x peak. Through the rise it sees slide plus
   a ramp that starts inside the terminal ramp. Correlations with a push only:
   - slide / drop: 0.988;
   - slide / latch peak: -0.979;
   - latch peak / drop: -0.969.

   The pull sees -slide, and adding it lowers the slide/drop correlation to 0.709.
   Adding a latch-disabled push lowers it to 0.407. So the fitter fixes snap drop at 1
   when there is no pull and no latch-disabled push.
3. **Post-snap stroke trades against latch play (push + pull).** The pull sees the
   hook catch at seat - post-snap - play. Only the snap location on the push separates
   the two. The correlation is -0.950 with push + pull, and -0.952 with a
   latch-disabled push added. Latch fall against post-snap: -0.867.
4. **On a compliant rig the click is a snap-through, which hides snap drop, fall and
   post-snap stroke at any speed.**
   - The falling side of the latch ramp has a negative stiffness of peak/fall: 60 N/mm
     nominal, 90 N/mm at 1.5x peak.
   - If the rig's axial stiffness at the tool is below that, the plug jumps through
     the fall when the force drops. The jump is about drop/stiffness: 0.6 mm on the
     10 N/mm gantry. That is longer than the 0.5 mm post-snap stroke, so the plug lands
     on the floor.
   - A handful of samples then trace the fall and the post-snap plateau, whatever the
     commanded speed. Speed does not change this, because the force stored in the
     servo drives the jump, not the motion.
   - A stiffer rig fixes it: at 200 N/mm the fall is traced and every quantity
     recovers on 11/11. Logging faster than every 2 ms adds samples in the jump.
5. **The latch onset can hide in the terminal kink.** When the onset lands on the
   terminal peak or on the end of the terminal fall (off09), the rise and onset trade
   with the terminal peak. The correlation is -0.942 with a push only, -0.854 with
   push + pull, and -0.566 with a latch-disabled push added.
6. **Hook stiffness needs hook load.** The pull shows it only beyond the slide force,
   that is, over 29 N - slide. At terminal friction 1.4x nominal or more that is about
   10 N and 0.05 mm, which was not enough on the compliant gantry (6/10 off-nominal).
   A guarded pull never shows the retention.

With the simulator's noise (0.03 N), every parameter is locally identifiable from a
single push + pull. The information matrix has full rank (14 of 14), with standard
deviations below 0.002 mm and 0.02 N (summary.json). The high correlations still
matter: a real curve will not match the model exactly, and model error then moves
the fit along those directions, not noise.

What the protocol should log per part, based on the above. This is a recommendation;
the protocol file is not edited here.
- **2 push + pull moves at 1 mm/s.** These show repeatability, reach the floor, and
  guard the pull at 29 N. In the simulator, speed does not separate any pair: 0.5 to
  5 mm/s give the same recovery (recovery.csv).
- **1 push + pull at 5 mm/s**, to check that the real curve does not depend on speed.
  The model is quasi-static, so the simulator cannot show a rate effect; a real part
  can.
- **On one part per lot, 1 push + pull with the latch disabled** (thumb latch held
  open, or a receptacle with the latch arm cut off). This separates terminal slide
  from snap drop, and the terminal kink from the latch onset (points 2 and 5).
- **At least 3 parts.** The fit is per part, and the simulator's latch_spread bands
  are guesses. 4 cycles per part leaves margin under the 25-cycle replacement rule.
- **Rig axial stiffness above about 100 N/mm at the tool** if the click shape matters
  (point 4), and F/T logged at 1 kHz or faster if the rig can.

Format: the existing `t_s,depth_mm,fz_n` is enough, and no change is required. The
protocol should state what the fitter needs:
- one file per move, with push and pull in the same file;
- at least 0.5 mm of free travel logged before contact, for the force offset and the
  noise;
- the push must reach the floor;
- depth must be the plug tip on the socket axis, from encoders, with no slip in the
  gripper. The fitter would read any series compliance between encoder and tip as
  part compliance; it does not model it;
- which files are latch-disabled, and the commanded speed, recorded in a session
  manifest or the file name.

This is a separate move from the existing contact-calibration move (1 mm lateral
offset onto the lead-in, 2 mm/s). The latch fit needs an aligned move.

## Worked example: the datasheet curve as "real" data

No manufacturer publishes a Micro-Fit force-depth curve (w3_development/REPORT.md).
The "datasheet curve" here is the curve W3 pinned to the datasheet: the nominal model,
measured through the simulated wrist sensor in a 1 mm/s push and guarded pull on the
gantry. W3's test checks that its peak is within 15% of the model and under the 32 N
datasheet maximum. The curve was written as a protocol CSV
(worked/datasheet_curve.csv), read back with `LoggedMove.read_csv`, and fitted. Its
noise and offset use development seed 2027.

Fitted values against the model:

| parameter | fitted | model |
|---|---|---|
| terminal wipe (mm) | 1.741 | 1.75 |
| terminal lead (mm) | 0.303 | 0.3 |
| terminal peak (N) | 20.05 | 20 |
| terminal slide (N) | 11.99 | 12 |
| latch rise (mm) | 1.004 | 1.0 |
| latch peak (N) | 5.99 | 6 |
| latch fall (mm) | 0.124 | 0.1 |
| snap drop | 0.999 | 1 |
| post-snap stroke (mm) | 0.467 | 0.5 |
| latch play (mm) | 0.123 | 0.1 |
| hook stiffness (N/mm) | 197 | 200 |
| bristle (mm) | 0.049 | 0.05 |

Residual:
- median |error|: 0.020 N;
- in-band share: 100% of the 199 depth bins (0.01 mm) of the part's curve are inside
  +/-15% of the logged force (0.5 N floor);
- largest bin residual: 0.66 N;
- push peak: logged 20.39 N, fitted 20.46 N (+0.35%).

Plot: worked/datasheet_curve.png. The report CLI's JSON (`connector_json_model`) gives
the fitted `model` block, ready for the connector JSON.

A second curve tests a shape outside the model family: the same log with the part's
curve rounded (Gaussian over depth, sigma 0.05 mm, away from the floor;
worked/rounded_curve.csv and .png). The overlay still looks good:
- 96.5% of bins are inside the band;
- the largest residual is 3.7 N, at the rounded corner where the pull starts;
- the peak is within 3.9%.

But the parameters that sit at corners move:

| parameter | rounded curve | sharp curve |
|---|---|---|
| latch fall (mm) | 0.205 | 0.124 |
| post-snap stroke (mm) | 0.421 | 0.467 |
| latch play (mm) | 0.145 | 0.123 |
| hook stiffness (N/mm) | 148 | 197 |
| terminal peak (N) | 19.17 | 20.05 |

A real part with rounded corners will be fitted the same way: a good overlay, with
the corner parameters shifted.

Post-hoc changes in the worked example, labelled as such:
1. **In-band share.** The first version counted raw samples, including the floor
   contact and the long unloading at the floor, which a linear floor model does not
   follow. That gave 69% for the datasheet curve. The share now counts 0.01 mm bins
   and leaves out the floor contact (the last 0.02 mm before the fitted seat), which
   gives 100%.
2. **Rounded curve.** The first version smoothed raw samples by depth. This spread
   the dense floor samples into the post-snap region and moved the fitted seat by
   0.23 mm. It now smooths the true model on a uniform grid.

Both are fixes to how the worked example is built, made after seeing its output. They
do not change the fitter or the recovery rule. The rerun (`--only-worked`) started
from b00e936 with these two fixes uncommitted; they are committed with this report.

## What a real rig curve will add that synthetic recovery cannot show

- **Whether the model's form is right.** Here the data came from mating.py's own
  piecewise-linear shapes, so the fitter only had to find numbers. A real curve can
  differ in form:
  - rounded corners (as in the worked example);
  - a latch force that does not drop to zero (snap drop < 1);
  - terminal friction that differs between insertion and withdrawal. The datasheet
    gives 8 N maximum mating and 2.4 N minimum unmating per circuit; mating.py uses
    one slide value for both directions;
  - friction that changes with speed;
  - housing friction.

  The residual plot is where this shows. The fitted numbers can look reasonable while
  the form is wrong.
- **Rig effects the simulator does not have:** compliance between the encoders and the
  plug tip (gripper, fingers, F/T body), F/T drift and temperature, real sensor noise,
  and misalignment that adds wall friction.
- **Part-to-part and cycle-to-cycle spread.** The latch_spread bands used here are the
  simulator's guesses. Several parts and repeated cycles give the real spread, which
  is what the latching benchmark should use.
- **The latch's own dynamics:** how much the hook is damped, and how fast the click is.
  The simulator's undamped hook rings on a compliant servo; a real one may not.

## Uncertain, not done

- The fitter has not seen a real curve. Nothing here validates the Micro-Fit model.
- Latch stiffness is the weakest quantity and failed the rule. On a stiff rig it was
  fine in simulation.
- Fitted values for snap drop, play, hook stiffness and bristle have no place in the
  connector JSON. mating.py keeps play, hook stiffness and bristle as module constants
  and has no snap-drop term. Using these values needs a mating.py change (simulator
  side only). Not done here.
- Synthetic curves came from the gantry backend only; the arm was not used.
- Seed 2026 is a development seed. No validation seed was used, because there was no
  selection to validate.
- The worked example's curve and the nominal recovery case are the same kind of data
  (the nominal simulated curve). The worked example differs only in going through the
  CSV path and the report.
- `Tolerance()` in latch_fit.py defaults to a 0.05 mm floor. The recovery used the
  RULE's 0.03 mm, passed explicitly.
