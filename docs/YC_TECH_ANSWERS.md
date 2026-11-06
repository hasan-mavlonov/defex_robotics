# Technical answers for the CTO, one question at a time

Each answer has a short version (about 20 seconds), a longer one (about 60 seconds),
and the numbers behind it for follow-ups. "Site" means defexrobotics.com
([`SITE_SNAPSHOT_2026-11-06.md`](SITE_SNAPSHOT_2026-11-06.md)). "Repo" means this
simulation (`README.md`, `defex/control/adaptive_fsm.py`, `defex/config.py`).

---

## T1. How does this actually work? How does your product work in more detail?

### Short version (say this first)

> A board comes in on a pallet. One camera finds the connector's socket; a second checks
> how the robot is holding the plug. The robot presses the plug in using its wrist force
> sensor. If it misses the hole, it works out where the hole is from how the plug is
> resting, and tries again. Then it tests the result: it feels the latch click, pulls,
> feels both walls, and checks every wire electrically. Pass goes to the tote, fail goes
> to a locked reject bin, and every unit is logged.

### Longer version (if they say "more detail")

> Six steps, the same for every part.
>
> 1. **See.** "One camera finds the header. One below checks the plug in the fingers."
>    So before every press we know roughly where the socket is and how the plug sits in
>    the gripper.
> 2. **Press.** The robot pushes under force control, not position control, and it is
>    compliant sideways, so "the chamfer guides it home." That's the slope at the
>    socket's mouth.
> 3. **Recover if it misses.** If the plug lands on the surface, the wrist sensor's
>    torque tells us exactly where the plug is resting. From that we compute where the
>    hole must be and try the most likely spot. We don't spiral blindly. If it's still
>    blocked, we try small twists.
> 4. **Test.** This is the core. The robot feels the latch click in the force signal,
>    then pulls. "A plug that moves fails." For plugs without a latch, it pushes gently
>    left and right to feel both socket walls, then straightens the twist and the lean.
>    Then an electrical test checks continuity and isolation on every wire.
> 5. **Decide.** "Seated? Held? Every wire?" Pass or fail. It only says done after the
>    test.
> 6. **Log and sort.** "Every unit logged: what it saw, what it felt, the verdict." Good
>    ones go to the tote; rejects are locked away.
>
> Today the insertion and the touch test run in a physics simulation of a gantry and a
> UR5e arm. The real robot is what we're building now.

### What's built and what isn't (say it before they ask)

| Part | Status |
|---|---|
| Force-controlled press, contact recovery, touch test (walls, twist, latch click, pull) | **Built in simulation** (MuJoCo, gantry and UR5e). Tested on about 100,000 paired trials per round. |
| Camera noise and the in-hand plug estimate | **Simulated** as noisy one-shot estimates. No real camera software yet. |
| Electrical test, continuity and isolation per wire | **Not built.** Shown only in the site's scripted prototype. [CONFIRM: which tester hardware you plan to use.] |
| Pallet, tote, reject bin, logging | **Not built.** Shown in the site's scripted prototype. |
| The physical robot | **Not built.** "We are building it now." |

### The numbers behind each step (for follow-ups)

**1. See (repo: what the controller is given)**
- The socket pose comes from vision **once, before motion**. Simulated noise: 0.3 mm
  (x, y, z), 0.5 deg yaw, 0.3 deg tilt. The tests sweep this up to 2 mm.
- The plug pose in the gripper comes once, after the grasp: 0.1 mm and 0.3 deg.
- The wrist force/torque sensor runs at 500 Hz. Noise 0.03 N and 0.5 N mm, plus a bias
  that is zeroed ("tared") in free air before each attempt.
- The controller never sees the true socket position. A test fails the build if control
  code imports the simulator or its ground truth.

**2. Press (repo `INSERT`)**
- Force control: the downward speed is proportional to the error from a **6 N** target,
  capped at 10 mm/s. On the Micro-Fit latching connector the target is **35.2 N**:
  1.1 x the datasheet's 32 N maximum mating force.
- Software compliance (admittance): the plug can slide and twist on contact. Tilt
  compliance switches on once the plug is confidently inside.
- It is a stall if the plug gains less than 0.15 mm in 0.4 s while pushing above 70% of
  the target. Limits: 20 N total, 10 N sideways, 0.35 N m. The cell's protective stop is
  30 N; the Micro-Fit's is 48 N.
- Why the chamfer matters: the socket is 13 x 9 mm for a 12 x 8 mm plug (0.5 mm per
  side), with a 0.8 mm x 45 deg chamfer. The plug is guided in if it lands within about
  **1.3 mm** of centre (0.5 mm of gap plus 0.8 mm of chamfer).

**3. Recover (repo `DETECT` and `RECOVER`, the hardest part)**
- `DETECT` classifies the contact: on the top face, jammed part-way in, or seated.
- On the face:
  - The plug first settles flat, so leftover tilt doesn't look like an offset.
  - The wrist torque gives the **centre of pressure**: where the plug is supported.
  - A Bayesian grid over the hole's position (0.25 mm cells, +/-7 mm) combines that
    reading with every earlier blocked try. The next try goes to the most likely spot.
  - The forward model matched the simulator's contacts to **0.07 mm** on average (0.22 mm
    worst case).
  - After two confident tries that still block, it searches twist: +/-3, 6, 9, 12 deg.
- Jammed part-way in: it re-aims using the offsets the compliance already found.
- Hard limits: 8 attempts, 26 s, 6.5 mm sideways, 12 deg twist, 6 deg tilt.

**4. Test (repo `VERIFY`)**
- Plain housing:
  - **Bottoming:** depth reached *and* force held, so the plug is resting on the floor.
  - **Lean:** the plug settles flat to the floor.
  - **Walls:** a gentle push each way must meet at least **2 N** of push-back within
    about **1.2 mm**. A plug that is truly inside hits a wall both ways; one perched on
    the rim doesn't.
  - **Centre:** the plug moves to the middle between the walls it found.
  - **Twist:** on the gantry, it twists to both limits and parks in the middle. On the
    arm, it computes the twist from the free travel and accepts up to 2 deg.
- Latching connector (Micro-Fit 3.0):
  - looks for the **click** in the force trace;
  - checks tilt;
  - **pulls at 35.2 N**; the plug must not back out more than **1.05 mm** (0.6 x the
    1.75 mm terminal wipe);
  - after a failed pull: one re-push, then reject.
- What the test costs: about **1.9 s** per part on the gantry and **2.5 s** on the arm.
  Typical good cycle: 5.3 s against spiral search's 2.4 s (gantry).

**5. Decide**
- It says SUCCESS only after the test passes. Otherwise it retracts and retries, or
  declares FAILURE, which is a reject.
- Result in simulation: **0** bad plugs called good in 7,400 good parts per run, on three
  runs. Spiral search: 138-178. With the test switched off, our own robot passed 41 of
  2,000 on the gantry, about the same as spiral's 40.

**6. Compute**
- The control loop runs at 500 Hz (2 ms), the rate of the UR e-Series external control
  interface.
- The controller's own work takes about **45 us** at the median, in Python. The slowest
  tick (0.6-0.9 ms) is the hole-finder update after a blocked try, made with the robot at
  rest.

### Likely follow-ups, with short answers

| They ask | You say |
|---|---|
| "Why not just spiral search?" | It's faster, but it only checks depth. It called 138-178 crooked plugs good per 7,400; we called 0. |
| "How do you know where the hole is from one touch?" | The torque at the wrist tells us where the plug is supported. For a plug resting on a face with a hole in it, that point says which way the hole is. We combine every try in a probability map. |
| "Is that the AI?" | No, it's physics plus probability. The search is "a fixed routine, not a trained robot policy." Learning comes next: we're hiring a Robot Learning Engineer for it. |
| "What if the camera is worse than you think?" | That's where we lose ground. With a 1.5 mm hand-eye bias we don't tell it about, spiral search seats more than we do. We size the search from the camera's stated accuracy. |
| "Does it work on a real robot?" | Not yet. The simulation's predictions for the rig test are frozen in advance, so the rig can prove or disprove them. |
| "How does the electrical test work?" | [FILL: the tester, the fixture adapter, how long it takes.] It's not built yet. |

### Simple words for the terms (if a partner isn't a robotics person)

- **Force control:** push until you feel a set force, instead of moving to a set point.
- **Compliance:** the robot gives a little when it touches something, like a hand.
- **Chamfer:** the sloped edge at the socket's mouth that guides the plug.
- **Centre of pressure:** the point where the plug is resting, worked out from the wrist
  torque.
- **Tare:** zeroing the force sensor before touching anything.
