# v0.2f tilt diagnosis: decision on development seeds (before seed 4007)

By RULE.md (2f95377), from CAND_P.md, CAND_JW.md and CAND_JP.md (dev seeds 2026 and 2027):

- P (C, G): KEEP. 0 bad units or bad parts added, 0 net good-part rejections, 0 net stops. Acted on 15 trials
  (arm floor-impact settles), all with the same outcome.
- JW (J): KEEP. No row changed; first latch checks now get a verdict (191 -> 753 arm, 190 -> 740 gantry), all PASS.
- JP (J): KEEP. 0 net good-part rejections, 1 net stop added (gantry), at the bound of 1.
- Tie-break JP vs JW: equal bad units (0), equal good-part rejections (0) -> JW.

Validation on seed 4007, once: P and JW.
