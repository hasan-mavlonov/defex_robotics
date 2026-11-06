# Hardware-in-the-loop rig options (W7)

Research only: nothing has been bought and no vendor has been contacted.
**Every purchase, and the choice of rig, needs Hasan's approval (ASK HASAN).** This file
lists options and does not pick one. Prices were looked up on 2026-10-31.
"F" means read on the vendor or reseller page; "S" means from a search snippet
because the page blocked automated reading. Re-check S numbers before ordering.
"unsourced" means no price or lead time was looked up. CHF converted at about
1.21 USD/CHF (2026-10-25 snapshot).

## Requirements the rig must meet (from the simulation and TEST_PROTOCOL.md)

- **Forces.** The force budget is per part (`results/v0.2d_force_budget/REPORT.md`):
  - Micro-Fit: every controller pushes at 35.2 N; abort 40 N, protective stop 48 N,
    damage 58 N.
  - Housing-only part: 3-8 N insertion force, C's abort 20 N, stop 30 N, damage 45 N.
  - The earlier "1-30 N" covered only the housing-only part.
  - Axial: the actuator and every part in the load path must push at least 48 N
    continuously and carry about 60 N transients (the simulation's measured force passes
    58 N on a few trials per cell).
  - The F/T sensor needs an axial range of at least 72.5 N (58 N / 0.8, because the
    harness aborts at 80% of range), with about 0.1 N resolution. A 60 N range is the
    bare minimum (80% = the 48 N stop) and cannot measure the damage bound.
  - Torque: stop at 0.6 N m.
- **Positioning:** 0.02-0.05 mm.
- **Control loop:** 500 Hz. The wrist F/T sensor must be fast enough to see a latch
  snap.
- **Wrist:** rigid for A, C and H, and a passive RCC for F, I and J.
- **Socket jig:** sets x, y, yaw and tilt (up to 3 deg about any horizontal axis) for
  every trial, and measures them.
- **Final pose measurement:** plug relative to socket, about 0.1 deg in yaw and tilt
  near 3 deg (TEST_PROTOCOL.md section 5).

## Components

Rows marked **does not fit** fail one of the requirements above.

### 6-axis wrist F/T sensors

| Sensor | Range | Resolution / noise | Max rate | Interface | Price | Lead time | Source | Fits the force budget? |
|---|---|---|---|---|---|---|---|---|
| ATI Mini40 SI-20-1 | Fxy 20 N, Fz 60 N, 1 N m | 1/200 N (Fxy), 1/100 N (Fz) | 7000 Hz (Net F/T RDT, 288 us latency); EtherCAT 1000 Hz | Net F/T, EtherCAT, DAQ | quote | quote | F [A1][A3] | **does not fit** the Micro-Fit: the 80% saturation check fires at 48 N (the stop), and it cannot read 58 N. Fits the housing-only part. A larger Mini40 calibration: unsourced |
| Bota MiniONE Pro Gen A | 50 N, 1 N m | 6 sigma: 0.02 N (Fxy), 0.0125 N (Fz) | 2000-3800 Hz | Ethernet / EtherCAT, USB | quote | 3-5 weeks | F [A6][A7] | **does not fit** the Micro-Fit: 35.2 N is 70% of range, the 40 N abort is at the 80% saturation point, and the stop and damage bounds are above range |
| Bota MiniONE Gen A | Fxy 80 N, Fz 100 N, 1.5 N m | 6 sigma: 0.15 N, 0.10 N | 800 Hz | USB, serial | CHF 3,045 (~$3,684), certificate +CHF 1,100 | 3-5 weeks | F [A8][A9] | yes (80% of Fz = 80 N) |
| Bota SensONE T5 Gen A | Fxy 400 N, Fz 500 N | 6 sigma: 0.055 N, 0.025 N | 3800 Hz | Ethernet / EtherCAT, USB | CHF 5,617.50 | 3-5 weeks | F [A10] | yes |
| OnRobot HEX-E QC | 200 N | 1 sigma 0.035 N (Fxy), 0.15 N (Fz) | not stated | Compute Box | $4,585 (Vention) | 12 days | F [A12][A13] | range yes; rate unknown |
| Robotiq FT 300-S | 300 N | 0.1 N | **100 Hz: too slow** | RS-485 | quote | | F [A15][A16] | range yes; too slow |
| UFactory F/T 400 N | 400 N | not stated | **200 Hz: too slow** | SDK/TCP | $2,970-3,500, backorder | | F [A18][A19] | range yes; too slow |

The UR3e's built-in F/T (precision +/-2.0 N, S [B3]) is too coarse for 1 N contact
work. Lateral forces were not checked against the Fxy ranges. The Mini40's 20 N Fxy
(80% = 16 N) is the one most at risk.

### Cobots with a real-time external loop

| Arm | Payload | Repeatability | Real-time interface | Price | Lead time | Source |
|---|---|---|---|---|---|---|
| UR3e | 3 kg | +/-0.03 mm | RTDE 500 Hz | $33,011 (Vention) | next day | F [B1][B2] |
| Franka Research 3 | 3 kg | <+/-0.1 mm | FCI 1 kHz (torque, position, Cartesian) | $29,218 (Vention; FCI licence to confirm) | next day | F [B4][B5] |
| Kinova Gen3 7DoF | 4 kg | not found | low-level torque 1 kHz | $35,795 (RobotShop) | special order | F [B7][B9] |
| UFactory 850 | 5 kg | +/-0.02 mm | servo mode max **250 Hz** | $9,899 | 2-3 months | F [B10][B11], S [B12] |
| UFactory Lite 6 | 0.6 kg | **+/-0.5 mm** | 250 Hz | from $2,999 | | F [B13] |

The simulation's arm is the MuJoCo Menagerie UR5e. None of these arms is modelled, so
their predictions come from the `arm` rows labelled "different arm"
(`results/v0.2f_rig_predictions/PREREGISTRATION.md`). A UR5e (not listed, unsourced)
would match the model. Whether each arm's own wrist and joints carry a 48 N axial push at
the plug was not checked.

### Gantry and wrist stages

| Item | Travel | Repeatability | Load | Price | Lead time | Source | Fits the force budget? |
|---|---|---|---|---|---|---|---|
| Zaber X-LRQ150AL-DE51 (linear, encoder) | 150 mm | <2 um | 100 N thrust | $5,883 | 4-7 days | F [C1] | yes as the insertion (Z) axis |
| Zaber X-LSM100A (linear) | 101.6 mm | <3 um | 25 N cont. | $2,610 | 1-5 days | F [C2] | **does not fit** as the insertion axis (25 N < 35.2 N). As X or Y, its normal and moment load under a 48 N push is unsourced |
| Zaber X-GSM40 / X-GSM60 (goniometer, remote centre 40/60 mm above top) | | | **30 N** | $2,741 each | 4-7 days | F [C3] | **does not fit**: 30 N is below the 35.2 N push, the 40 N abort and the 48 N stop, on the plug side or under the socket |
| Zaber X-RSW60A-E03 (rotary, encoder) | 360 deg | <0.02 deg | 2.25 N m | $3,015 | 1-5 days | F [C4] | axial load capacity unsourced |
| FUYU FSL40 ball-screw modules (DIY) | to 1,500 mm | +/-0.02 mm (claimed) | | ~$90 | | S [C7][C8] | load unsourced |
| Dynamixel XM430-W350 (DIY wrist) | | 0.25 deg backlash (~0.13 mm at 30 mm) | 4.1 N m | $333 | backorder | F [C11][C12] | backlash is close to the 0.1 deg pose target |

Zaber stages use RS-232 ASCII. No 500 Hz external command rate is published, so the
actuator-side loop rate must be measured on the bench before relying on it.

Replacements for the goniometers (all unsourced): higher-load goniometers; a manual
tilt platform locked during the trial; or wedge blocks (see "Socket jig").

### Passive RCC wrist (for F, I and J)

| Item | Why | Price | Lead time |
|---|---|---|---|
| ATI 9115-001-A compliance device (size 000) | the simulation's RCC lateral and cocking stiffness come from its datasheet (`CompliantStageConfig` in `defex/config.py`) | unsourced (quote) | unsourced |

Its axial load rating against the 48 N stop and 58 N damage bound is unsourced. The
earlier BOM had no RCC, so F, I and J could not have run.

### Socket jig (sets x, y, yaw and tilt per trial)

| Option | What it sets | Notes | Cost |
|---|---|---|---|
| Manual micrometer XY table + manual rotary + manual two-axis tilt platform, all lockable | x, y, yaw, tilt | about 1,600 settings for the protocol; slow | unsourced |
| Wedge blocks (fixed tilt angles) on a rotary stage that sets the tilt azimuth, under a rotary that sets yaw | tilt in steps only | the simulation draws tilt uniformly in 0-3 deg, so the steps miss the drawn tilt; trials outside the 0.05 deg tolerance are reported separately | unsourced |
| Motorized XY + rotary + high-load tilt stages | all four, automatically | fastest; every stage under the socket carries the push (48 N stop) | unsourced |

The set pose is measured on every trial (`jig.csv`, TEST_PROTOCOL.md section 6).

### Final pose measurement (TEST_PROTOCOL.md section 5)

| Item | Role in the protocol | Cost class | Price |
|---|---|---|---|
| Laser triangulation displacement sensors, 4-6 heads, and a bridge fixed to the jig | primary | medium | unsourced |
| Two machine-vision cameras, lenses, fiducial markers | check | low | unsourced |
| Go/no-go gauge, machined per part | check | low | unsourced |
| Reference plug and gauge blocks at known tilt, yaw and depth | session check of all of the above | low | unsourced |
| Offline measurement (CMM or measuring microscope), sample of trials | check | high per sample or a lab service | unsourced |

### Test parts

- **Micro-Fit 3.0, 4 circuits, dual row, as modelled**
  (`assets/connectors/microfit3_4ckt.json`):
  - receptacle housing 43025-0408;
  - vertical header 43045-0429;
  - female crimp terminals 43030-0001 (S [D5], $0.10).
  - Prices and lead times of the housing and header: unsourced.
  - The protocol uses about 70 sets (replaced every 25 insertions), plus spares and the
    four kinds of deliberately bad parts.
- The earlier list had 2-circuit single-row parts (header 43650-0200 $1.07, receptacle
  43645-0200 $0.39; S [D1][D3]). **They do not match the model**, which is the
  4-circuit dual-row part: other cross-section, twice the terminals, and so other
  mating forces.
- **Housing-only test part**: a plug and socket made to
  `assets/connectors/rect_12x8.json`; material pair not chosen; price and lead time
  unsourced.
- Amphenol RJ45 jack RJHSE-5380 $1.72 (S [D9]). There is an RJ45 connector file
  (`assets/connectors/rj45_8p8c.json`), but the protocol does not use it.

## Three rig options

| | 1. Desk gantry + F/T | 2a. UR3e + F/T | 3a. Hybrid: UFactory 850 + F/T |
|---|---|---|---|
| Parts | 2 x X-LSM100A (X, Y), X-LRQ150AL (Z), X-GSM40 + X-GSM60 (tilt; **do not fit**, replace), X-RSW60A (yaw), F/T | UR3e, Bota SensONE T5 | UFactory 850, Bota MiniONE Gen A |
| Approximate total (excl. PC, frame, quotes) | ~$23.3k + F/T (~$3.7k priced fallback), including the two goniometers that must be replaced | ~$39.8k | ~$13.6k |
| Not in the total, all options | RCC, socket jig, pose measurement, test parts: unsourced | same | same |
| Matches the simulator's fixture | yes (gantry + remote-centre wrist) | partly (the model is a UR5e) | partly |
| Contact forces, latch signature, F/T noise | yes, with an F/T that fits the budget | yes | yes (800 Hz sensor) |
| 500 Hz loop | sensor yes; actuators to be measured | yes, native both sides | no (250 Hz) |
| Serial-arm dynamics | no | yes | partly |
| Main risk | the goniometers carry only 30 N; Zaber command rate | price; arm not the modelled one | 2-3 month lead time; 250 Hz |

A cheaper DIY gantry (FUYU modules, closed-loop steppers, LinuxCNC at 1 kHz, MiniONE
Gen A) is ~$5.5-6.5k. Its prices are low-confidence and its accuracy and load are
unverified.

## Decisions for Hasan

The earlier draft recommended option 1 with an ATI Mini40 SI-20-1 or a Bota MiniONE
Pro. Neither sensor fits the Micro-Fit force budget, and option 1's goniometers do not
either. That recommendation is withdrawn. Questions to settle before any quote:
- gantry (matches the simulated fixture) or cobot (matches the pilot cell, if the
  customer's cell is a cobot);
- which F/T sensor of those that fit;
- how the tilt is set and carried under a 48 N push;
- which pose measurement;
- the budget ceiling.

Quotes that would be needed (no vendor has been contacted):
- ATI: a Mini40 calibration with a larger range, and the 9115-001-A;
- Bota;
- Franka (FCI licence);
- Molex distributors for 43025-0408 and 43045-0429.

## Sources (all seen 2026-10-31)

[A1] https://www.ati-ia.com/products/ft/ft_models.aspx?id=Mini40 ·
[A3] https://ati-ia.com/products/ft/ft_SystemInterfaces.aspx ·
[A6] https://shop.botasys.com/shop/force-torque-sensors-4/minione-pro-gen-a-2278 ·
[A7] https://casscale.net/wp-content/uploads/2026/07/MIP-DATASHEET-REV-A.pdf ·
[A8] https://shop.botasys.com/shop/force-torque-sensors-4/minione-gen-a-2162 ·
[A9] https://casscale.net/wp-content/uploads/2026/07/MiniONEGenASeriesDatasheetRevB.pdf ·
[A10] https://shop.botasys.com/shop/force-torque-sensors-4/sensone-gen-a-2322 ·
[A12] https://onrobot.com/storage/datasheets/hex/datasheet_hex-e_h_qc_v1.5_en.pdf ·
[A13] https://vention.com/parts/onrobot-force-torque-sensor-1422 ·
[A15] https://robotiq.com/products/ft-300-force-torque-sensor ·
[A16] https://blog.robotiq.com/hubfs/Product-sheets/FT%20300/ur/Product_sheet-FT300S_FC_EN.pdf ·
[A18] https://www.robotshop.com/products/ufactory-6-axis-force-torque-sensor-xarm-850-400n ·
[A19] https://www.ufactory.us/product/6-axis-force-torque-sensor ·
[B1] https://vention.com/parts/universal-robots-ur3e-collaborative-robot-arm-2446 ·
[B2] https://docs.universal-robots.com/tutorials/communication-protocol-tutorials/rtde-guide.html ·
[B3] https://www.universal-robots.com/manuals/latest/en/datasheets/ur3e/ ·
[B4] https://vention.com/parts/franka-robotics-fr3-v2-4193 ·
[B5] https://frankarobotics.github.io/docs/overview.html ·
[B7] https://www.robotshop.com/products/kinova-gen3-robot-7dof-l53 ·
[B9] https://github.com/empriselab/kortex_hardware ·
[B10] https://www.ufactory.cc/xarm-collaborative-robot/ ·
[B11] https://docs.supportarticle.ufactory.cc/support_articles/developer/ufactory-servo-mode-guide.html ·
[B12] https://usa.ufactory.cc/product-page/ufactory-850 ·
[B13] https://www.ufactory.cc/lite-6-collaborative-robot/ ·
[C1] https://www.zaber.com/products/linear-stages/X-LRQ-DE/details/X-LRQ150AL-DE51 ·
[C2] https://www.zaber.com/products/linear-stages/X-LSM/details/X-LSM100A ·
[C3] https://www.zaber.com/products/goniometer-stages/X-GSM ·
[C4] https://www.zaber.com/products/rotary-stages/X-RSW/details/X-RSW60A-E03 ·
[C7] https://kingfahad.sa/products/fuyu-fsl40-linear-guide-version-20-table-ball-screw-motion-c/215612705/ ·
[C8] https://www.directindustry.com/prod/fuyu-technology/product-197091-2861749.html ·
[C11] https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/ ·
[C12] https://www.robotshop.com/products/robotis-dynamixel-xm430-w350-r-smart-servo-actuator ·
[D1] https://www.digikey.com/en/products/detail/molex-llc/0436500200/268989 ·
[D3] https://digikey.com/product-detail/en/molex-llc/43645-0200/WM1845-ND/268974 ·
[D5] https://www.digikey.com/en/products/detail/molex/0430300001/467796 ·
[D9] https://www.digikey.com/en/products/detail/amphenol-cs-commercial-products/RJHSE-5380/1242692
