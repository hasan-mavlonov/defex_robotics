# BOM price check, November 2026

Research only. Nothing was bought, no vendor was contacted, no form was filled, no quote
was requested and no account was made. Every price below was read on 2026-11-05.

How to read this file:
- "F" means read on the vendor or reseller page. "S" means taken from a search result
  snippet because the page blocked automated reading or did not load. Re-check S numbers
  before ordering.
- "not public" means the vendor does not publish a price. It is not a guess.
- CHF prices are converted at **1.226 USD/CHF** (mid rate, 2026-11-05,
  https://www.poundsterlinglive.com/history/CHF-USD-2026). hardware/BOM.md used 1.21.
- "BOM price" is the price in hardware/BOM.md (looked up 2026-10-31).
- Prices exclude shipping, tax, import duty and tariffs unless stated.

## 1. Six-axis wrist F/T sensors

Force needs (BOM.md, TEST_PROTOCOL.md section 3): the harness aborts at 80% of range, so
the Micro-Fit needs at least 72.5 N axial range (58 N damage / 0.8). The housing-only
part needs at least 56.25 N to read its 45 N damage bound (45 / 0.8), and at least
37.5 N to read its 30 N stop (30 / 0.8). About 0.1 N resolution and a rate that supports
a 500 Hz loop.

| Item | BOM price | Price now (2026-11-05) | Source | Lead time | Notes |
|---|---|---|---|---|---|
| ATI Mini40 SI-20-1 (Fxy 20 N, Fz 60 N) | quote | **not public** at ATI. Reseller indication: "From $5,750" (Silicon Valley Robotics Center; the listing does not say which calibration or interface the price covers), backorder | F https://www.ati-ia.com/products/ft/ft_models.aspx?id=Mini40 ; F https://www.roboticscenter.ai/store/product/ati-mini40-ft/ | reseller: 4-6 weeks | Housing-only part: fits axially (80% of 60 N = 48 N, above the 45 N damage bound). Micro-Fit: does not fit (BOM.md). ATI quotes through https://ati.novanta.com/get-a-quote/ |
| ATI Mini40 SI-40-2 (Fxy 40 N, Fz 120 N, 2 N m; resolution 1/100 N Fxy, 1/50 N Fz) | not in BOM ("larger Mini40 calibration: unsourced") | **not public** | F https://www.ati-ia.com/products/ft/ft_models.aspx?id=Mini40 | not public | New row. Range now sourced: fits **both** parts (80% of Fz = 96 N). SI-80-4 (Fz 240 N, 1/25 N) also exists. Price needs the ATI quote |
| Bota MiniONE Pro Gen A (50 N, 1 N m) | quote | **not public**: the shop shows "CHF 0.00" (a placeholder) and "for lower price request a quote" | F https://shop.botasys.com/shop/force-torque-sensors-4/minione-pro-gen-a-2278 | 3-5 weeks for 1 unit | Micro-Fit: does not fit (BOM.md). Housing-only: 80% of 50 N = 40 N, above the 30 N stop but below the 45 N damage bound, so the saturation check fires before damage can be measured |
| Bota MiniONE Gen A (Fxy 80 N, Fz 100 N, 800 Hz) | CHF 3,045 (~$3,684) | **CHF 3,045 = $3,733**. Calibration certificate CHF 1,100 = $1,349 | F https://shop.botasys.com/shop/force-torque-sensors-4/minione-gen-a-2162 | 3-5 weeks for 1 unit | Price unchanged in CHF; +$49 from the exchange rate. Fits both parts. Cheapest priced sensor that fits |
| Bota SensONE T5 Gen A (Fxy 400 N, Fz 500 N, 3800 Hz) | CHF 5,617.50 | **CHF 5,617.50 = $6,887**. Certificate CHF 1,100 = $1,349 | F https://shop.botasys.com/shop/force-torque-sensors-4/sensone-gen-a-2322 | 3-5 weeks for 1 unit | Unchanged in CHF. The page shows one price for the T5 and T15 variants |
| OnRobot HEX-E QC (200 N) | $4,585 (Vention) | **$4,585** (Vention part ST-RB-028-0016); needs Compute Box ST-RB-028-0002 (price not checked) | F https://vention.com/parts/onrobot-force-torque-sensor-1422 | ships in 12 days | Unchanged. **New finding:** datasheet v1.5 gives noise-free resolution 0.2 N (Fxy) and **0.8 N (Fz)**, and 1 sigma noise 0.035 N / 0.15 N (F https://onrobot.com/storage/datasheets/hex/datasheet_hex-e_h_qc_v1.5_en.pdf). 0.8 N is coarser than the 0.1 N requirement. Rate still not stated |
| Robotiq FT 300-S (300 N, 100 Hz) | quote | **not public** at Robotiq. Reseller: $10,643, backorder | F https://www.roboticscenter.ai/es/store/product/robotiq-ft-300s-force-torque-sensor | reseller: 4-6 weeks | Too slow (100 Hz), as in BOM.md. No quote draft |
| UFactory 6-axis F/T 400 N (200 Hz) | $2,970-3,500, backorder | **$2,970** RobotShop, backorder; **$3,500** ufactory.us, out of stock | F https://www.robotshop.com/products/ufactory-6-axis-force-torque-sensor-xarm-850-400n ; F https://www.ufactory.us/product/6-axis-force-torque-sensor | not stated | Unchanged. Too slow (200 Hz) |

## 2. Cobots

| Item | BOM price | Price now | Source | Lead time | Notes |
|---|---|---|---|---|---|
| UR3e | $33,011 (Vention) | **$33,011** | F https://vention.com/parts/universal-robots-ur3e-collaborative-robot-arm-2446 | none stated (BOM: next day) | **The Vention page now shows an "Obsolete" label** next to the price, with an Add to cart button. Universal Robots' e-Series comparison sheet (May 2026) still lists the UR3e (S https://www.universal-robots.com/manuals/EN/DataSheets/comparison_e-series_pdf_online/comparison_e-Series_en.pdf). A search snippet gave $30,852 with 7 weeks lead time on Vention (S, not seen on the page). Confirm availability before choosing it |
| Franka Research 3 (FCI 1 kHz) | $29,218 (Vention) | **$29,218.06** (Vention part PR-FR-003-1000) | F https://vention.com/parts/franka-robotics-fr3-v2-4193 | ships next day | Unchanged. The page does not say whether the FCI licence is included. Generation Robots sells "Franka Research 3 + FCI licence" at price on request (F https://generationrobots.com/en/403992-7-axis-franka-research-3-robotic-arm-fci-licence.html). FCI licence status needs a question to Franka or Vention |
| Kinova Gen3 7DoF | $35,795 (RobotShop) | **$35,837.33** | F https://www.robotshop.com/products/kinova-gen3-robot-7dof-l53 | special order | +$42 |
| UFactory 850 (servo mode max 250 Hz) | $9,899 | **$8,999** on UFactory's own site (S); RobotShop $10,258.86 "includes tariffs" (S); Top3dshop $9,849 (S) | S https://usa.ufactory.cc/product-page/ufactory-850 (page refused the connection); S https://www.robotshop.com/products/ufactory-850-6-dof-robotic-arm-850mm-w-dc-control-box-2m-cables | BOM: 2-3 months; not re-confirmed (page did not load) | Possibly $900 lower than the BOM. Still 250 Hz |
| UFactory Lite 6 (+/-0.5 mm) | from $2,999 | **from $2,999** (ufactory.cc); ufactory.us shows $3,349 "starting at" | F https://www.ufactory.cc/lite-6-collaborative-robot/ ; F https://www.ufactory.us/product/6-axis-force-torque-sensor | not stated | Too coarse (+/-0.5 mm) |
| UR5e (the modelled arm; not a BOM row) | unsourced | **not public** at UR. Indications: Vention's cell BOMs price it at $34,527 (S, third-party blog, Aug 2026); guides give $30,000-45,000 | S https://www.grabarobot.com/blog/vention-robot-cell-price-guide-2026/ ; S https://standardbots.com/articles/universal-robot-price | not found | Secondary sources only |

## 3. Gantry and wrist stages

All Zaber prices are "starting price, direct to North American customers".

| Item | BOM price | Price now | Source | Lead time | Notes |
|---|---|---|---|---|---|
| Zaber X-LRQ150AL-DE51 (Z; 100 N cont., 230 N peak) | $5,883 | **$5,883** | F https://www.zaber.com/products/linear-stages/X-LRQ-DE/details/X-LRQ150AL-DE51 | **4-10 days** (BOM: 4-7) | Unchanged price |
| Zaber X-LSM100A (X, Y; 25 N cont. thrust) | $2,610 | **$2,610** each | F https://www.zaber.com/products/linear-stages/X-LSM/details/X-LSM100A | 1-5 days | Unchanged. **Now sourced:** max centred load 250 N; moment capacity pitch 4 N m, roll 10 N m, yaw 4 N m. A 30 N push at more than about 130 mm lever arm exceeds 4 N m; the real lever arm depends on the frame |
| Zaber X-GSM40 / X-GSM60 (goniometers; 30 N) | $2,741 each | **$2,741** each | F https://www.zaber.com/products/goniometer-stages/X-GSM | 4-7 days | Unchanged. 30 N is below the Micro-Fit push. For the housing-only part, 30 N equals the protective stop: the 3-8 N push and C's 20 N abort are inside it, the 45 N damage bound is not |
| Zaber X-RSW60A-E03 (yaw; 2.25 N m) | $3,015 | **$3,015** | F https://www.zaber.com/products/rotary-stages/X-RSW/details/X-RSW60A-E03 | 1-5 days | Unchanged. **Now sourced:** max centred load 200 N (BOM: "axial load unsourced"); above the 58 N Micro-Fit damage bound |
| FUYU FSL40 modules (DIY) | ~$90 | about $50-90 depending on stroke and seller (S) | S https://academy.greenestep.com/products/fuyu-fsl40-linear-module-rail-version-20-ball-screw-linear-stage-nema-23-cnc/51612821 ; S https://kingfahad.sa/products/fuyu-fsl40-linear-guide-version-20-table-ball-screw-motion-c/215612705/ | not stated | Low confidence, as in BOM.md. Load still unsourced |
| Dynamixel XM430-W350 (DIY wrist) | $333 | **$333.39**, backorder | F https://www.robotshop.com/products/robotis-dynamixel-xm430-w350-r-smart-servo-actuator | not stated | Unchanged |

Not priced (not in BOM.md either): Zaber power supplies, data cables and mounting plates;
breadboard or frame; PC.

## 4. Passive RCC wrist

| Item | BOM price | Price now | Source | Lead time | Notes |
|---|---|---|---|---|---|
| ATI 9115-001-A compliance device | unsourced (quote) | **not public** | F https://ati-ia.com/products/compliance/Compensator_Models.aspx ; F https://www.ati-ia.com/es-MX/products/compliance/compensator_9115DataSheet.aspx | not public | **New finding:** ATI lists the 9115 series under "Previous Product Versions". The current RCC page lists a **9116-001-A** with the same maximum loads (compression 80 lb = 356 N, cocking 30 lbf-in, lateral 1.5 lb). The 9115 datasheet gives for 9115-001-A: tension 5 lb (about 22 N), lateral stiffness 33 lb/in, cocking stiffness 1600 in-lb/rad. Whether 9116-001-A has the same stiffness (the simulation's `CompliantStageConfig` values) is not stated. The 356 N compression rating is above the 48 N stop and 58 N damage bound (this answers the BOM's "axial load unsourced"). The 22 N tension rating is below the 29 N Micro-Fit pull test and C's 36 N retract cap; it matters only on the Micro-Fit. No public price found; a different ATI product (L1A125E lateral compliance compensator) lists at $2,099 at one reseller (S https://www.nextdayautomation.com/products/new-ati-l1a125e-lateral-compliance-compensator-0-175-18-g1-8-220lbs-max), which is not an equivalent |

## 5. Socket jig (unsourced in BOM.md; indications only)

| Item | BOM price | Indication now | Source | Notes |
|---|---|---|---|---|
| Manual two-axis tilt (example: Thorlabs GNL20 dual-axis goniometer pair) | unsourced | $356 | S https://www.thorlabs.com/catalogpages/346.pdf (catalog page; edition date not shown) | Load rating under a 30 N or 48 N push not checked |
| Manual XY micrometer table and manual rotary | unsourced | not found | | Not priced |
| Motorized XY + rotary + high-load tilt | unsourced | not priced | | |

## 6. Final pose measurement (unsourced in BOM.md; indications only)

| Item | BOM price | Indication now | Source | Notes |
|---|---|---|---|---|
| Laser triangulation heads, 4-6 (example: Panasonic HG-C1030, 30 mm range) | unsourced | about $609 each, $600 at 5+, 8 in stock, 10-day ship (one distributor) | S https://www.ibselectronics.com/part/sunx/hg-c1030/2147660/ (page returned 403) | The snippet's "0.1 um resolution" needs the datasheet; repeatability not confirmed. 4-6 heads: about $2,400-3,700. Analog read-out hardware not priced |
| Laser triangulation, alternative (Micro-Epsilon optoNCDT 1220) | unsourced | EUR 470 per unit (S); the product page shows no price | S https://www.micro-epsilon.com/distance-sensors/laser-sensors/optoncdt-1220/?sLang=us | Page says "repeatability from 3.7 um", measuring rate 2 kHz |
| Two machine-vision cameras (example: FLIR Blackfly S BFS-U3-51S5M-C, 5 MP mono) | unsourced | $1,305 each at Edmund Optics (S) | S https://www.edmundoptics.com/p/bfs-u3-51s5m-c-usb3-blackfly-s-monochrome-camera/37239/ (page returned 403) | A Basler ace 2 a2A2590-60um was listed at EUR 365.59 at Mouser Europe (S), a cheaper class. Lenses and markers not priced |
| Go/no-go gauge, reference plug, gauge blocks | unsourced | not priced (machined to order) | | |
| Offline CMM or measuring microscope | unsourced | not priced | | |

## 7. Test parts

| Item | BOM price | Price now | Source | Lead time | Notes |
|---|---|---|---|---|---|
| Molex 43025-0408 receptacle housing (4 ckt, dual row) | unsourced | about $0.21-0.42 each (LCSC: $0.42 at 1, $0.21 at 1,000+; 3,223 in stock) | S https://www.lcsc.com/product-detail/C293524.html ; S https://octopart.com/part/molex/43025-0408 | in stock (S) | About 70 sets for the protocol: under $30 |
| Molex 43045-0429 vertical header (4 ckt) | unsourced | DigiKey $2.17 at 1, $1.12 at volume, 3,628 in stock (via FindChips) | S https://www.findchips.com/detail/0430450429/Molex (page returned 403) | **7 weeks** factory lead time listed (S) | 70 sets: under $160 |
| Molex 43030-0001 female crimp terminal | $0.10 (S) | about $0.0345 each (DigiKey via FindChips; Avnet $0.0344 in reels of 12,000); ichome $0.13 at 1 | S https://findchips.com/detail/0430300001/Molex | 11 weeks listed (S); 236,730 in stock (S) | The single-piece price is probably higher than $0.0345; re-check on DigiKey. A crimp tool is needed and not priced |
| Molex 43650-0200 / 43645-0200 (2 ckt) | $1.07 / $0.39 (S) | not re-checked | | | These do not match the model (BOM.md); not needed |
| Amphenol RJHSE-5380 RJ45 | $1.72 (S) | not re-checked | | | Not used by the protocol |
| Housing-only test part to `rect_12x8.json` | unsourced | **not public** (machined or printed to order) | | | Quote draft in QUOTE_DRAFTS.md |

DigiKey, FindChips and Edmund Optics returned HTTP 403 to automated reading, so every
number from them is S.

## 8. Totals per rig option (priced lines only, 2026-11-05)

Same parts as BOM.md's "Three rig options" table. None of these totals includes the RCC,
socket jig, pose measurement, test parts, Zaber power supplies and cables, frame or PC.

| Option | Parts | BOM.md total | Now | Change |
|---|---|---|---|---|
| 1. Desk gantry + F/T | 2 x X-LSM100A $5,220; X-LRQ150AL-DE51 $5,883; X-GSM40 + X-GSM60 $5,482; X-RSW60A-E03 $3,015; Bota MiniONE Gen A $3,733 | "~$23.3k + F/T (~$3.7k)" | **$23,333** (stages $19,600 + sensor $3,733); $24,682 with the calibration certificate | +$49 (exchange rate). **BOM.md wording:** the five stages add to $19,600, so "~$23.3k" already includes the $3.7k sensor; "+ F/T" counts it twice |
| 2a. UR3e + F/T | UR3e $33,011; Bota SensONE T5 $6,887 | ~$39.8k | **$39,898**; $41,247 with the certificate | +$90 (exchange rate). UR3e now "Obsolete" on Vention |
| 3a. UFactory 850 + F/T | UFactory 850 $8,999 (S); Bota MiniONE Gen A $3,733 | ~$13.6k | **$12,732** at UFactory's own price (S); $13,992 at RobotShop's tariff-inclusive price (S) | about -$850 at the official price, if the S number holds |
| Not a BOM option: Franka FR3 + F/T | FR3 $29,218; Bota MiniONE Gen A $3,733 | | **$32,951**; FCI licence status not stated | Cheaper than 2a and has a published 1 kHz external loop (BOM.md) |

Price indications for the lines BOM.md left unsourced (all S, low confidence):
- manual two-axis tilt (GNL20): $356;
- 4-6 laser heads (HG-C1030): about $2,400-3,700;
- two cameras (Blackfly S): $2,610;
- Micro-Fit parts for about 70 sets: under $200, plus terminals and a crimp tool.

## 9. What changed since 2026-10-31

- No priced line went up in its own currency. CHF lines are $49-90 higher because the
  franc moved from 1.21 to 1.226 USD.
- UR3e: Vention now labels it "Obsolete". UR's May 2026 sheet still lists it.
- UFactory 850: possibly $8,999 at UFactory (BOM: $9,899); S only, page did not load.
- Kinova Gen3: +$42.
- X-LRQ150AL-DE51 lead time 4-10 days (was 4-7).
- ATI 9115 series is a previous product version; 9116-001-A appears to be the current
  part with the same load ratings. Compression 356 N now sourced; tension 22 N.
- OnRobot HEX-E: Fz noise-free resolution 0.8 N, too coarse for the 0.1 N requirement.
- Mini40 SI-40-2 (Fz 120 N) range now sourced: it would fit both parts; price needs a quote.
- Zaber X-LSM100A moment ratings and X-RSW60A-E03 centred load (200 N) now sourced.
- Bota MiniONE Pro: no public price (shop placeholder CHF 0.00).
- BOM.md option 1 total wording counts the F/T sensor twice (see section 8).
