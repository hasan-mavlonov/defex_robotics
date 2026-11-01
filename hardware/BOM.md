# Hardware-in-the-loop rig options (W7)

Research only: nothing has been bought and no vendor has been contacted.
**Every purchase needs Hasan's approval.** Prices were looked up on 2026-10-31.
"F" means read on the vendor or reseller page; "S" means from a search snippet
because the page blocked automated reading. Re-check S numbers before ordering.
CHF converted at about 1.21 USD/CHF (2026-10-25 snapshot).

Requirements the rig must meet (from the simulator): forces 1-30 N, positioning
0.02-0.05 mm, a 500 Hz control loop, a wrist F/T sensor fast enough to see a
latch snap.

## Components

### 6-axis wrist F/T sensors

| Sensor | Range | Resolution / noise | Max rate | Interface | Price | Lead time | Source |
|---|---|---|---|---|---|---|---|
| ATI Mini40 SI-20-1 | Fxy 20 N, Fz 60 N, 1 N m | 1/200 N (Fxy), 1/100 N (Fz) | 7000 Hz (Net F/T RDT, 288 us latency); EtherCAT 1000 Hz | Net F/T, EtherCAT, DAQ | quote | quote | F [A1][A3] |
| Bota MiniONE Pro Gen A | 50 N, 1 N m | 6 sigma: 0.02 N (Fxy), 0.0125 N (Fz) | 2000-3800 Hz | Ethernet / EtherCAT, USB | quote | 3-5 weeks | F [A6][A7] |
| Bota MiniONE Gen A | Fxy 80 N, Fz 100 N, 1.5 N m | 6 sigma: 0.15 N, 0.10 N | 800 Hz | USB, serial | CHF 3,045 (~$3,684), certificate +CHF 1,100 | 3-5 weeks | F [A8][A9] |
| Bota SensONE T5 Gen A | Fxy 400 N, Fz 500 N | 6 sigma: 0.055 N, 0.025 N | 3800 Hz | Ethernet / EtherCAT, USB | CHF 5,617.50 | 3-5 weeks | F [A10] |
| OnRobot HEX-E QC | 200 N | 1 sigma 0.035 N (Fxy), 0.15 N (Fz) | not stated | Compute Box | $4,585 (Vention) | 12 days | F [A12][A13] |
| Robotiq FT 300-S | 300 N | 0.1 N | **100 Hz: too slow** | RS-485 | quote | | F [A15][A16] |
| UFactory F/T 400 N | 400 N | not stated | **200 Hz: too slow** | SDK/TCP | $2,970-3,500, backorder | | F [A18][A19] |

The UR3e's built-in F/T (precision +/-2.0 N, S [B3]) is too coarse for 1 N contact work.

### Cobots with a real-time external loop

| Arm | Payload | Repeatability | Real-time interface | Price | Lead time | Source |
|---|---|---|---|---|---|---|
| UR3e | 3 kg | +/-0.03 mm | RTDE 500 Hz | $33,011 (Vention) | next day | F [B1][B2] |
| Franka Research 3 | 3 kg | <+/-0.1 mm | FCI 1 kHz (torque, position, Cartesian) | $29,218 (Vention; FCI licence to confirm) | next day | F [B4][B5] |
| Kinova Gen3 7DoF | 4 kg | not found | low-level torque 1 kHz | $35,795 (RobotShop) | special order | F [B7][B9] |
| UFactory 850 | 5 kg | +/-0.02 mm | servo mode max **250 Hz** | $9,899 | 2-3 months | F [B10][B11], S [B12] |
| UFactory Lite 6 | 0.6 kg | **+/-0.5 mm** | 250 Hz | from $2,999 | | F [B13] |

### Gantry and wrist stages

| Item | Travel | Repeatability | Load | Price | Lead time | Source |
|---|---|---|---|---|---|---|
| Zaber X-LRQ150AL-DE51 (linear, encoder) | 150 mm | <2 um | 100 N thrust | $5,883 | 4-7 days | F [C1] |
| Zaber X-LSM100A (linear) | 101.6 mm | <3 um | 25 N cont. | $2,610 | 1-5 days | F [C2] |
| Zaber X-GSM40 / X-GSM60 (goniometer, remote centre 40/60 mm above top) | | | **30 N** | $2,741 each | 4-7 days | F [C3] |
| Zaber X-RSW60A-E03 (rotary, encoder) | 360 deg | <0.02 deg | 2.25 N m | $3,015 | 1-5 days | F [C4] |
| FUYU FSL40 ball-screw modules (DIY) | to 1,500 mm | +/-0.02 mm (claimed) | | ~$90 | | S [C7][C8] |
| Dynamixel XM430-W350 (DIY wrist) | | 0.25 deg backlash (~0.13 mm at 30 mm) | 4.1 N m | $333 | backorder | F [C11][C12] |

Zaber stages use RS-232 ASCII; no 500 Hz external command rate is published, so
the actuator-side loop rate must be measured on the bench before relying on it.

### Test connectors (quantity 1, S from Digi-Key/Mouser snippets)

Molex Micro-Fit 3.0 header 43650-0200 $1.07; receptacle housing 43645-0200
$0.39; crimp terminal 43030-0001 $0.10; Amphenol RJ45 jack RJHSE-5380 $1.72.
Under $50 for a full set of test parts. [D1]-[D9]

## Three rig options

| | 1. Desk gantry + F/T | 2a. UR3e + F/T | 3a. Hybrid: UFactory 850 + F/T |
|---|---|---|---|
| Parts | 2 x X-LSM100A, X-LRQ150AL (Z), X-GSM40 + X-GSM60 (tilt), X-RSW60A (yaw), F/T | UR3e, Bota SensONE T5 | UFactory 850, Bota MiniONE Gen A |
| Approximate total (excl. PC, frame, quotes) | ~$23.3k + F/T (~$3.7k priced fallback) | ~$39.8k | ~$13.6k |
| Matches the simulator's fixture | yes (gantry + remote-centre wrist) | the W5 arm backend | partly |
| Contact forces, latch signature, F/T noise | yes | yes | yes (800 Hz sensor) |
| 500 Hz loop | sensor yes; actuators to be measured | yes, native both sides | no (250 Hz) |
| Serial-arm dynamics | no | yes | partly |
| Main risk | goniometers carry only 30 N; Zaber command rate | price | 2-3 month lead time; 250 Hz |

A cheaper DIY gantry (FUYU modules, closed-loop steppers, LinuxCNC at 1 kHz,
MiniONE Gen A) is ~$5.5-6.5k with low-confidence prices and unverified accuracy.

**Recommendation for Hasan to decide on:** option 1 with an ATI Mini40 SI-20-1
or Bota MiniONE Pro (quotes needed), after a bench check of the Zaber command
rate; it reproduces the simulator's fixture, so sim-versus-real compares like
with like. Option 2a if the pilot customer's cell will be a UR arm.

Quotes still needed: ATI (Mini40), Bota (MiniONE Pro), Franka (FCI licence).

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
