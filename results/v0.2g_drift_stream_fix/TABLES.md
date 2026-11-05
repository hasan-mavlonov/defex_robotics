# heldout2 F/T drift family: before and after the drift-stream fix

Rules and columns are heldout2_tables'. Each machine: 2 conditions x 40 trials x 10 controllers, seed 20261207. Before = heldout2_v0.2f (6ea164e); after = this folder (c3f967a).

# before

## (a) C against the best fair baseline (D, E, F, H, I), and G against C
| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |
| gantry, h2_ft_drift | C vs best of D/E/F/H/I (D) | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 | 1 | a fair baseline matches C: goes in the README headline; Hasan decides the pitch |
| gantry, h2_ft_drift | G vs C | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| arm, h2_ft_drift | C vs best of D/E/F/H/I (D) | 76.2% vs 100.0% (-23.8 pts) | 0 / 19 | 3.8e-06 | C below the best fair baseline, p < 0.05: goes in the README headline |
| arm, h2_ft_drift | G vs C | 76.2% vs 76.2% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
## (b) Bad units passed on good-part trials, C against H and I
| Machine, cell | Comparison | Bad units, C vs other | C-only / other-only | McNemar p | Outcome |
| gantry, h2_ft_drift | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_ft_drift | C vs I | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_ft_drift | C vs H | 8/80 (<= 18.5%) vs 0/80 | 8 / 0 | 0.0078 | C passes more than H |
| arm, h2_ft_drift | C vs I | 8/80 (<= 18.5%) vs 1/80 | 7 / 0 | 0.016 | C passes more than I |
## (c) J against C and against I
| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |
| gantry, h2_ft_drift | J vs C, seated | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (J-only / C-only) | 1 | J matches C |
| gantry, h2_ft_drift | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_ft_drift | J vs I, seated | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (J-only / I-only) | 1 | J matches I |
| gantry, h2_ft_drift | J vs I, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_ft_drift | J vs C, seated | 82.5% vs 76.2% (+6.2 pts) | 8 / 3 (J-only / C-only) | 0.23 | J matches C |
| arm, h2_ft_drift | J vs C, bad units passed | 5/80 (<= 13.8%) vs 8/80 | 1 / 4 | 0.38 | no significant difference |
| arm, h2_ft_drift | J vs I, seated | 82.5% vs 98.8% (-16.3 pts) | 0 / 13 (J-only / I-only) | 0.00024 | J below I |
| arm, h2_ft_drift | J vs I, bad units passed | 5/80 (<= 13.8%) vs 1/80 | 4 / 0 | 0.12 | no significant difference |
## (d) Throughput: success, cycle p50 / p95 of successes (s), protective stops, bad units, good units per hour (0 s / 60 s per stop)
| Machine, cell | Controller | Success | p50 | p95 | Stops | Bad units | Good units/h |
| gantry, h2_ft_drift | A | 17.5% | 4.32 | 4.32 | 63 | 3 | 221 / 13 |
| gantry, h2_ft_drift | B | 100.0% | 4.31 | 4.33 | 0 | 0 | 835 / 835 |
| gantry, h2_ft_drift | E | 100.0% | 10.82 | 10.83 | 0 | 0 | 333 / 333 |
| gantry, h2_ft_drift | D | 100.0% | 2.87 | 5.33 | 0 | 0 | 1187 / 1187 |
| gantry, h2_ft_drift | F | 100.0% | 2.43 | 2.44 | 0 | 0 | 1479 / 1479 |
| gantry, h2_ft_drift | H | 100.0% | 2.87 | 5.33 | 0 | 0 | 1187 / 1187 |
| gantry, h2_ft_drift | I | 100.0% | 2.43 | 2.44 | 0 | 0 | 1479 / 1479 |
| gantry, h2_ft_drift | J | 100.0% | 4.75 | 4.91 | 0 | 0 | 756 / 756 |
| gantry, h2_ft_drift | C | 100.0% | 5.27 | 5.49 | 0 | 0 | 679 / 679 |
| gantry, h2_ft_drift | G | 100.0% | 5.27 | 5.49 | 0 | 0 | 679 / 679 |
| arm, h2_ft_drift | A | 11.2% | 4.32 | 4.32 | 71 | 0 | 154 / 7 |
| arm, h2_ft_drift | B | 98.8% | 4.31 | 4.33 | 0 | 1 | 824 / 824 |
| arm, h2_ft_drift | E | 100.0% | 4.08 | 4.09 | 0 | 0 | 883 / 883 |
| arm, h2_ft_drift | D | 100.0% | 4.76 | 4.92 | 0 | 0 | 748 / 748 |
| arm, h2_ft_drift | F | 98.8% | 4.75 | 4.87 | 0 | 1 | 741 / 741 |
| arm, h2_ft_drift | H | 100.0% | 4.76 | 4.92 | 0 | 0 | 748 / 748 |
| arm, h2_ft_drift | I | 98.8% | 4.75 | 4.87 | 0 | 1 | 741 / 741 |
| arm, h2_ft_drift | J | 82.5% | 7.83 | 8.25 | 0 | 5 | 307 / 307 |
| arm, h2_ft_drift | C | 76.2% | 8.09 | 17.87 | 2 | 8 | 244 / 216 |
| arm, h2_ft_drift | G | 76.2% | 8.09 | 17.87 | 2 | 8 | 244 / 216 |
## (e) Per-condition success table per machine
### gantry, h2_ft_drift_0.1
### gantry, h2_ft_drift_0.3
### arm, h2_ft_drift_0.1
### arm, h2_ft_drift_0.3

# after

## (a) C against the best fair baseline (D, E, F, H, I), and G against C
| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |
| gantry, h2_ft_drift | C vs best of D/E/F/H/I (D) | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 | 1 | a fair baseline matches C: goes in the README headline; Hasan decides the pitch |
| gantry, h2_ft_drift | G vs C | 100.0% vs 100.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
| arm, h2_ft_drift | C vs best of D/E/F/H/I (D) | 80.0% vs 100.0% (-20.0 pts) | 0 / 16 | 3.1e-05 | C below the best fair baseline, p < 0.05: goes in the README headline |
| arm, h2_ft_drift | G vs C | 80.0% vs 80.0% (+0.0 pts) | 0 / 0 (C-only / G-only) | 1 | no measurable gain from G |
## (b) Bad units passed on good-part trials, C against H and I
| Machine, cell | Comparison | Bad units, C vs other | C-only / other-only | McNemar p | Outcome |
| gantry, h2_ft_drift | C vs H | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_ft_drift | C vs I | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_ft_drift | C vs H | 8/80 (<= 18.5%) vs 0/80 | 8 / 0 | 0.0078 | C passes more than H |
| arm, h2_ft_drift | C vs I | 8/80 (<= 18.5%) vs 0/80 | 8 / 0 | 0.0078 | C passes more than I |
## (c) J against C and against I
| Machine, cell | Comparison | Success | Discordant pairs | McNemar p | Rule outcome |
| gantry, h2_ft_drift | J vs C, seated | 98.8% vs 100.0% (-1.2 pts) | 0 / 1 (J-only / C-only) | 1 | J matches C |
| gantry, h2_ft_drift | J vs C, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| gantry, h2_ft_drift | J vs I, seated | 98.8% vs 100.0% (-1.2 pts) | 0 / 1 (J-only / I-only) | 1 | J matches I |
| gantry, h2_ft_drift | J vs I, bad units passed | 0/80 (<= 4.6%) vs 0/80 | 0 / 0 | 1 | no significant difference |
| arm, h2_ft_drift | J vs C, seated | 83.8% vs 80.0% (+3.7 pts) | 6 / 3 (J-only / C-only) | 0.51 | J matches C |
| arm, h2_ft_drift | J vs C, bad units passed | 4/80 (<= 12.2%) vs 8/80 | 0 / 4 | 0.12 | no significant difference |
| arm, h2_ft_drift | J vs I, seated | 83.8% vs 100.0% (-16.2 pts) | 0 / 13 (J-only / I-only) | 0.00024 | J below I |
| arm, h2_ft_drift | J vs I, bad units passed | 4/80 (<= 12.2%) vs 0/80 | 4 / 0 | 0.12 | no significant difference |
## (d) Throughput: success, cycle p50 / p95 of successes (s), protective stops, bad units, good units per hour (0 s / 60 s per stop)
| Machine, cell | Controller | Success | p50 | p95 | Stops | Bad units | Good units/h |
| gantry, h2_ft_drift | A | 17.5% | 4.32 | 4.32 | 63 | 3 | 221 / 13 |
| gantry, h2_ft_drift | B | 100.0% | 4.31 | 4.33 | 0 | 0 | 835 / 835 |
| gantry, h2_ft_drift | E | 100.0% | 10.82 | 10.83 | 0 | 0 | 333 / 333 |
| gantry, h2_ft_drift | D | 100.0% | 2.87 | 5.33 | 0 | 0 | 1190 / 1190 |
| gantry, h2_ft_drift | F | 100.0% | 2.43 | 2.44 | 0 | 0 | 1479 / 1479 |
| gantry, h2_ft_drift | H | 100.0% | 2.87 | 5.33 | 0 | 0 | 1190 / 1190 |
| gantry, h2_ft_drift | I | 100.0% | 2.43 | 2.44 | 0 | 0 | 1479 / 1479 |
| gantry, h2_ft_drift | J | 98.8% | 4.75 | 4.91 | 0 | 0 | 732 / 732 |
| gantry, h2_ft_drift | C | 100.0% | 5.27 | 5.59 | 0 | 0 | 679 / 679 |
| gantry, h2_ft_drift | G | 100.0% | 5.27 | 5.59 | 0 | 0 | 679 / 679 |
| arm, h2_ft_drift | A | 11.2% | 4.32 | 4.32 | 71 | 0 | 154 / 7 |
| arm, h2_ft_drift | B | 98.8% | 4.31 | 4.33 | 0 | 1 | 824 / 824 |
| arm, h2_ft_drift | E | 100.0% | 4.08 | 4.09 | 0 | 0 | 883 / 883 |
| arm, h2_ft_drift | D | 100.0% | 4.75 | 4.93 | 0 | 0 | 747 / 747 |
| arm, h2_ft_drift | F | 100.0% | 4.75 | 4.85 | 0 | 0 | 756 / 756 |
| arm, h2_ft_drift | H | 100.0% | 4.75 | 4.93 | 0 | 0 | 747 / 747 |
| arm, h2_ft_drift | I | 100.0% | 4.75 | 4.85 | 0 | 0 | 756 / 756 |
| arm, h2_ft_drift | J | 83.8% | 7.89 | 8.46 | 0 | 4 | 308 / 308 |
| arm, h2_ft_drift | C | 80.0% | 8.07 | 12.39 | 1 | 8 | 276 / 258 |
| arm, h2_ft_drift | G | 80.0% | 8.07 | 12.39 | 1 | 8 | 276 / 258 |
## (e) Per-condition success table per machine
### gantry, h2_ft_drift_0.1
### gantry, h2_ft_drift_0.3
### arm, h2_ft_drift_0.1
### arm, h2_ft_drift_0.3

