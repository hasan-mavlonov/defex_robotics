# v0.2e post-run check: two cells rerun on the benchmark_v0.2d code

This check was not pre-registered. It was run after benchmark_v0.2e's results had been
read, and it changes no benchmark_v0.2e verdict. It asks one question: are two
differences from benchmark_v0.2d caused by the v0.2e code or by the new seed?

- gantry mis-characterized vision: C 81.4%, against 87.6% and 87.2% on seeds 20261123
  and 20261124. G also fell, on `heldout_mischar_2mm`.
- arm latching good parts: C 92.0%, against 94.3% and 93.7%, which put C below F.

## Runs

`run.sh` ran the benchmark_v0.2e command on these trials from
`v0.2d/integration` at 92cee67. That commit's code outside `results/`, `README.md` and
`docs/` is identical to 42df5c8, the benchmark_v0.2d code; `git diff --stat 42df5c8
92cee67` with those paths excluded is empty. Both `config.json` files record
`git_dirty: false`. Seed 20261130, `--workers 9`.

- `gantry_heldout/`: C and G on `heldout_mischar_2mm` and `heldout_worst_case`, 100
  trials each.
- `arm_latching/`: C on `mf_noise_1mm`, 200 trials.

A trial is fixed by its base seed, condition and trial index, so these rows pair with
the same trials in `../benchmark_v0.2e/`.

## Result

`PYTHONPATH=. python results/v0.2e_postrun_check/compare.py <this run>/trials.csv
results/benchmark_v0.2e/<run>/trials.csv`:

| Cell | Ctrl | Trials | Seated, v0.2d code / v0.2e code | Outcome changes | Rows changed (all fields but wall time) |
|---|---|---|---|---|---|
| gantry heldout, the two conditions | C | 200 | 118 / 118 | 0 | 0 |
| gantry heldout, the two conditions | G | 200 | 158 / 158 | 0 | 0 |
| arm latching, `mf_noise_1mm` | C | 200 | 152 / 152 | 0 | 0 |

On these trials the v0.2e code gives exactly the rows of the v0.2d code. C's drop in
the conditions where it fell most therefore comes from the seed's draw of scenarios,
not from the three v0.2e fixes. The check covers C and G only (not F), two of the five
gantry heldout conditions and one of the three arm latching good-part conditions. It
does not exercise fix 1, which acts only on arm `generalization_combined` trials.
The arm trials include four where the v0.2e tilt guard gave no tilt verdict
(`mf_noise_1mm` trials 0, 3, 96 and 176). Their rows are also identical, so the guard
changed nothing there.
