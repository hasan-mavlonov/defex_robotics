# DRAFTS. Not sent. Hasan decides whether and when to send.

Nobody has been contacted. No web form was filled and no account was made. Contacts
were read from each vendor's public site on 2026-11-05. Where a vendor publishes no
sales email, the draft names its contact page; the text can be pasted into that form.

Each draft asks only what hardware/BOM.md needs. Change the quantities if the option
changes. Drafts 1-2 are the F/T sensor vendors. Drafts 3-4 are the other quote-only
lines. Draft 5 is optional: Zaber publishes prices, but its loop rate is the main open
risk of the gantry option.

---

## 1. ATI Industrial Automation (Novanta): Mini40 and RCC compliance device

**To:** ATI quote page https://ati.novanta.com/get-a-quote/ (no public sales email found;
phone +1 919-772-0115; contact page https://ati.novanta.com/contact-us/)

**Subject:** Quote request: Mini40 F/T sensor (SI-20-1 or SI-40-2) and a 9116-001-A compensator

Hello,

We are a robotics startup building a test bench for small connector insertions, and we
would like a quote for the following:

1. One Mini40 six-axis force/torque sensor. Please quote two calibrations, SI-20-1 and
   SI-40-2. Our insertion forces reach about 60 N along the tool axis, so we expect to
   need SI-40-2, but please tell us if you would recommend another calibration.
2. One Remote Center Compensator, 9116-001-A. Our simulation used the 9115-001-A values
   (lateral stiffness 33 lb/in, cocking stiffness 1600 in-lb/rad). Is 9116-001-A the
   current replacement, and are its stiffness values the same?

For each item, please tell us:
- the price, and any startup or academic pricing;
- the lead time;
- what calibration certificate is included, and its price if separate.

For the sensor:
- We run a 500 Hz control loop from a PC. Please quote the Net F/T (Ethernet) interface,
  and EtherCAT as an option. Please confirm the Net F/T output rate and latency for the
  Mini40.
- Please include the cable and any mounting adapter plates.

For the compensator:
- Can it carry 48 N in compression continuously, with about 60 N transients?
- Its tension rating is 5 lb. Can it carry a 29 N pull for one second?
- Can it be mounted directly below a Mini40, with a small gripper below it?

The sensor and compensator will be mounted on Zaber linear and goniometer stages, or on
a cobot (Franka Research 3 or UR3e). If either choice causes a mounting problem, please
let us know.

Thank you,

Hasan Mavlonov
CTO, Defex Robotics, Inc.

---

## 2. Bota Systems: MiniONE Gen A, MiniONE Pro Gen A, SensONE T5

**To:** info@botasys.com (general address on https://www.botasys.com/contact; the same
page has a "Sales and Orders" form, and a quote page at https://botasys.com/quote/)

**Subject:** Quote request: MiniONE Gen A and SensONE T5, one unit each, with calibration certificates

Hello,

We are a robotics startup building a test bench for small connector insertions, and we
would like a quote for one unit of each of these sensors:

1. MiniONE Gen A (your shop lists CHF 3,045).
2. MiniONE Pro Gen A (your shop shows no price).
3. SensONE T5 Gen A (your shop lists CHF 5,617.50).

We will probably buy one of them. For each, please tell us:
- the price in USD and CHF, and any startup or academic pricing;
- the lead time to California (your shop says 3-5 weeks);
- the price of the calibration certificate (your shop lists CHF 1,100), and what it
  covers;
- shipping cost and import terms to the United States.

Technical questions:
- We run a 500 Hz control loop from a Linux PC. For the MiniONE Gen A on USB, what is
  the latency from sample to host at its 800 Hz rate?
- For the SensONE T5, please confirm the EtherCAT and Ethernet output rates and latency.
- Our insertion force reaches about 60 N axially and our protective stop is 48 N. Please
  confirm the MiniONE Gen A's Fz range of 100 N and its overload limit.
- Do you offer an adapter plate for mounting on Zaber stages, and robot integration kits
  for a Franka Research 3 or a UR3e?

Thank you,

Hasan Mavlonov
CTO, Defex Robotics, Inc.

---

## 3. Franka Robotics: FCI licence with a Franka Research 3

Needed only if Hasan picks the Franka arm. Vention lists the arm at $29,218.06 but does
not say whether the FCI licence is included.

**To:** sales@franka.de (listed under "Sales" on https://franka.de/contact)

**Subject:** Question: is the FCI licence included with a Franka Research 3 bought through Vention?

Hello,

We are considering one Franka Research 3 for a connector insertion test bench, and we
need the Franka Control Interface for a 1 kHz external control loop.

Vention lists the FR3 (part PR-FR-003-1000) at $29,218.06. Could you tell us:
- whether the FCI licence is included in that robot, or what it costs;
- the price of one FR3 with the FCI licence bought from you directly, and any startup or
  academic pricing;
- the lead time to California.

We would mount a six-axis wrist force/torque sensor (Bota or ATI) and a passive
compliance device on the flange. Our insertion forces reach about 48 N along the tool
axis, with transients near 60 N. Can the FR3 push 48 N at the flange near the middle of
its workspace while under FCI Cartesian or torque control?

Thank you,

Hasan Mavlonov
CTO, Defex Robotics, Inc.

---

## 4. Machine shop: housing-only test part

The part is custom (`assets/connectors/rect_12x8.json`). No shop has been chosen.

**To:** (Hasan picks a shop)

**Subject:** Quote request: small machined plug and socket test pair, 40 pairs

Hello,

We would like a quote for a simple rectangular plug and socket pair, used to test a
robot insertion. Dimensions (millimetres):
- Plug: 12.0 x 8.0 cross-section, 25.0 long. Mass about 4 g.
- Socket: a 13.0 x 9.0 pocket (0.5 radial clearance on each side), 15.0 deep, with a
  0.8 x 45 degree lead-in chamfer on the opening. Wall 2.5, floor 2.0.

Please quote:
- 40 plugs and 40 sockets (we can change the quantity);
- tolerance of +/-0.02 on the plug cross-section and the socket pocket, and how flat
  and square you can hold the plug's end faces;
- two material options: aluminium (anodised) and a plastic such as acetal or PBT;
- price, lead time, and an inspection report for a sample of parts.

We will send a drawing once we have your answer on tolerances.

Thank you,

Hasan Mavlonov
CTO, Defex Robotics, Inc.

---

## 5. Optional: Zaber technical question (not a quote)

Zaber prices are public. This asks about the gantry's main open risk.

**To:** contact@zaber.com (General Inquiries on https://www.zaber.com/contact; the same
page has an "Ask an Engineer" form)

**Subject:** Question: closed-loop command rate for six X-series stages from a PC

Hello,

We are planning a desk gantry for a connector insertion test from these stages:
2 x X-LSM100A (X, Y), 1 x X-LRQ150AL-DE51 (Z), 1 x X-RSW60A-E03 (yaw), and
X-GSM40 + X-GSM60 (tilt).

Our controller sends a new position or velocity setpoint to every axis every 2 ms
(500 Hz) and reads back positions at the same rate. Could you tell us:
- the highest setpoint update rate a PC can reach with these stages, per axis and for all
  six together;
- whether each stage can have its own serial or USB connection to the PC, and the
  fastest supported baud rate;
- whether a streamed or buffered motion mode, or another interface, gets closer to
  500 Hz.

Load questions:
- The X-GSM40 and X-GSM60 are rated at 30 N. With the plug side pushing up to 30 N along
  the vertical axis, centred at the remote centre, is that within rating? Is there a
  higher-load goniometer with a remote centre near 40-60 mm?
- With the two X-LSM100A stages carrying the Z stage, yaw stage and goniometers, and a
  30-48 N vertical push at the tool, what lever arm keeps the X-LSM100A within its 4 N m
  pitch and yaw moment ratings?

Thank you,

Hasan Mavlonov
CTO, Defex Robotics, Inc.
