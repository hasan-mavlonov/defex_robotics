"""Sample size and power for the rig test (v0.2f), from the paired benchmark rows.

    python -m experiments.v02f_rig_power > hardware/RIG_POWER.md

Rates come from results/benchmark_v0.2d (seed 20261123), benchmark_v0.2d_rep (20261124) and benchmark_v0.2e
(20261130): per machine and suite, C against I, J and F on the same trials. Two metrics: success (the trials
where only one of the two succeeded) and bad units passed on good-part trials (only one of the two passed a bad
unit). The test is the exact two-sided McNemar test at 0.05 that the benchmarks use; power is computed exactly
from the two discordant-pair rates (normal approximation for more than NORMAL_D discordant pairs).
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np

RUNS = (("benchmark_v0.2d", "20261123"), ("benchmark_v0.2d_rep", "20261124"), ("benchmark_v0.2e", "20261130"))
GOOD = {
    "latching": {"mf_nominal", "mf_moderate", "mf_noise_1mm"},
    "latch_spread": {"mf_spread", "mf_latch_early", "mf_latch_late", "mf_latch_weak", "mf_terminal_max",
                     "mf_terminal_min"},
}
# The rig's own conditions (hardware/TEST_PROTOCOL.md), as extra "suites" cut from the benchmark suites.
RIG = {"rig housing-only": ("standard", {"nominal", "lateral_3mm", "noise_1mm", "noise_2mm"}),
       "rig Micro-Fit": ("latching", {"mf_nominal", "mf_moderate", "mf_noise_1mm"})}
SUITES = ("standard", "latching", "heldout", "latch_spread", *RIG)
OTHERS = (("spiral_rcc_pull", "I"), ("spiral_rcc_verify", "J"), ("spiral_rcc", "F"))
C = "adaptive"
ALPHA = 0.05
POWER = 0.80
N_MAX = 1_000_000
NORMAL_D = 1500
Z = 1.96  # as defex.logging.metrics.wilson_interval


def ok(r: dict) -> bool:
    return r["success"] == "True"


def escape(r: dict) -> bool:
    return not ok(r) and r["protective_stop"] != "True" and r["declared_success"] != "False"


def wilson_upper_zero(n: int, z: float = Z) -> float:
    """Wilson 95% upper bound for 0 events in n trials."""
    return z * z / (n + z * z)


def n_for_zero_upper(rate: float, z: float = Z) -> int:
    """Smallest n at which 0 events out of n has a Wilson upper bound below ``rate``."""
    return math.floor(z * z * (1 - rate) / rate) + 1


def _log_binom_pmf(k: np.ndarray, n: int, p: float) -> np.ndarray:
    if p <= 0.0:
        return np.where(k == 0, 0.0, -np.inf)
    if p >= 1.0:
        return np.where(k == n, 0.0, -np.inf)
    lg = math.lgamma(n + 1) - np.array([math.lgamma(x + 1) + math.lgamma(n - x + 1) for x in k])
    return lg + k * math.log(p) + (n - k) * math.log1p(-p)


def _norm_cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def critical(d: int, alpha: float = ALPHA) -> int:
    """Largest m with 2 P(K <= m) <= alpha for K ~ Bin(d, 1/2), or -1: reject iff min(b, c) <= m."""
    if d == 0:
        return -1
    if d > NORMAL_D:
        m = math.floor(d / 2 - 0.5 - math.sqrt(d / 4) * 1.959963984540054)
        return max(m, -1)
    k = np.arange(d + 1)
    cdf = np.cumsum(np.exp(_log_binom_pmf(k, d, 0.5)))
    hits = np.nonzero(2 * cdf <= alpha + 1e-12)[0]
    hits = hits[hits < d / 2]
    return int(hits[-1]) if hits.size else -1


def reject_given_d(d: int, q: float, alpha: float = ALPHA) -> float:
    """P(exact McNemar rejects | d discordant pairs, each one a 'first-only' pair with probability q)."""
    m = critical(d, alpha)
    if m < 0:
        return 0.0
    if d > NORMAL_D:
        mu, sd = d * q, math.sqrt(d * q * (1 - q)) or 1e-12
        return min(1.0, _norm_cdf((m + 0.5 - mu) / sd) + 1 - _norm_cdf((d - m - 0.5 - mu) / sd))
    k = np.arange(d + 1)
    pmf = np.exp(_log_binom_pmf(k, d, q))
    return float(min(1.0, pmf[: m + 1].sum() + pmf[d - m:].sum()))


def power(n: int, p10: float, p01: float, alpha: float = ALPHA, cache: dict | None = None) -> float:
    """Power of the exact two-sided McNemar test with n pairs and discordant-pair rates p10, p01."""
    pd = p10 + p01
    if n <= 0 or pd <= 0:
        return 0.0
    q = p10 / pd
    mu, sd = n * pd, math.sqrt(n * pd * (1 - pd))
    lo, hi = max(0, int(mu - 9 * sd - 5)), min(n, int(mu + 9 * sd + 5))
    ds = np.arange(lo, hi + 1)
    w = np.exp(_log_binom_pmf(ds, n, pd))
    cache = {} if cache is None else cache
    r = np.array([cache.setdefault((int(d), q), reject_given_d(int(d), q, alpha)) for d in ds])
    return float(min(1.0, (w * r).sum()))


def n_for_power(p10: float, p01: float, target: float = POWER, n_max: int = N_MAX) -> int | None:
    """About the smallest n with power >= target (bisection on a nearly monotone curve, rounded up to 10).

    None when the two rates are equal (nothing to detect) or n_max is not enough.
    """
    if p10 == p01:
        return None
    cache: dict = {}
    hi = 10
    while power(hi, p10, p01, cache=cache) < target:
        hi *= 2
        if hi > n_max:
            return None
    lo = hi // 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if power(mid, p10, p01, cache=cache) >= target:
            hi = mid
        else:
            lo = mid
    return int(math.ceil(hi / 10) * 10)


def load_pairs(root: Path) -> dict[tuple[str, str, str], dict]:
    """(machine, suite, other) -> counts of paired good-part trials of C against ``other`` in one run."""
    out: dict = {}
    for f in sorted(root.glob("*_*/trials.csv")):
        machine, suite = f.parent.name.split("_", 1)
        rows = {}
        for r in csv.DictReader(open(f)):
            rows[(r["controller"], r["condition"], r["trial_index"])] = r
        cuts = [(suite, GOOD.get(suite))]
        cuts += [(name, conds) for name, (s, conds) in RIG.items() if s == suite]
        for name, keep in cuts:
            for other, _ in OTHERS:
                keys = [k for k in rows if k[0] == C and (keep is None or k[1] in keep) and (other,) + k[1:] in rows]
                pairs = [(rows[k], rows[(other,) + k[1:]]) for k in keys]
                if not pairs:
                    continue
                out[(machine, name, other)] = {
                    "n": len(pairs),
                    "b": sum(ok(x) and not ok(y) for x, y in pairs), "c": sum(ok(y) and not ok(x) for x, y in pairs),
                    "eb": sum(escape(x) and not escape(y) for x, y in pairs),
                    "ec": sum(escape(y) and not escape(x) for x, y in pairs),
                    "sc": sum(ok(x) for x, _ in pairs), "so": sum(ok(y) for _, y in pairs),
                    "ecc": sum(escape(x) for x, _ in pairs), "eco": sum(escape(y) for _, y in pairs),
                }
    return out


def fmt_n(n: int | None, p10: float, p01: float) -> str:
    if n is None:
        return "no difference" if p10 == p01 else f"> {N_MAX:,}"
    return f"{n:,}"


def pose_rows(results: Path) -> list[str]:
    """Where the bad units passed by F, H, I and J are: depth, tilt and yaw, pooled over the three runs."""
    out = ["| Ctrl | Part | Bad units | At full depth | Of those, tilt > 3 deg | yaw > 3 deg | neither | "
           "max of abs(tilt), abs(yaw) at full depth: median, 95th pct, max (deg) |", "|---|---|---|---|---|---|---|---|"]
    for ctrl, letter in (("spiral_rcc", "F"), ("spiral_pull", "H"), ("spiral_rcc_pull", "I"),
                         ("spiral_rcc_verify", "J"), (C, "C")):
        for part, full in (("housing-only", 14.5), ("Micro-Fit", 7.5)):
            esc = []
            for run, _ in RUNS:
                for f in sorted((results / run).glob("*_*/trials.csv")):
                    suite = f.parent.name.split("_", 1)[1]
                    if (part == "Micro-Fit") != (suite in GOOD):
                        continue
                    esc += [r for r in csv.DictReader(open(f)) if r["controller"] == ctrl and r["group"] != "bad_part"
                            and (GOOD.get(suite) is None or r["condition"] in GOOD[suite]) and escape(r)]
            if not esc:
                out.append(f"| {letter} | {part} | 0 | | | | | |")
                continue
            fd = [r for r in esc if float(r["final_depth_mm"]) >= full]
            t = [abs(float(r["final_tilt_deg"])) for r in fd]
            y = [abs(float(r["final_yaw_deg"])) for r in fd]
            ang = [max(a, b) for a, b in zip(t, y)]
            q = (f"{np.median(ang):.2f}, {np.percentile(ang, 95):.2f}, {max(ang):.2f}" if ang else "")
            neither = sum(a <= 3 and b <= 3 for a, b in zip(t, y))
            out.append(f"| {letter} | {part} | {len(esc)} | {len(fd)} | {sum(a > 3 for a in t)} | "
                       f"{sum(b > 3 for b in y)} | {neither} | {q} |")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results"))
    a = ap.parse_args()
    per_run = {seed: load_pairs(a.results / run) for run, seed in RUNS}
    keys = sorted({k for d in per_run.values() for k in d},
                  key=lambda k: (k[0] != "gantry", SUITES.index(k[1]), [o for o, _ in OTHERS].index(k[2])))
    letter = dict(OTHERS)
    out = ["# Rig test: sample size and power", "",
           "Made by `python -m experiments.v02f_rig_power > hardware/RIG_POWER.md` from the per-trial rows of "
           "`results/benchmark_v0.2d` (seed 20261123), `benchmark_v0.2d_rep` (20261124) and `benchmark_v0.2e` "
           "(20261130). Simulation rates; a rig's rates will differ.", "",
           "**Test.** Exact two-sided McNemar at 0.05 on paired trials, as in the benchmarks. **Power** is "
           "computed exactly from the two discordant-pair rates: p(C only) and p(other only) per paired trial. "
           "**n** is the number of paired good-part trials (per controller) for 80% power, from the rates pooled "
           "over the three seeds; the last column uses each seed's own rates (seeds 20261123, 20261124, 20261130, in that order). "
           "\"no difference\": the pooled rates are equal, so no n is enough. The rig rows are the benchmark "
           "trials of the protocol's conditions only (housing-only: nominal, lateral_3mm, noise_1mm, "
           "noise_2mm; Micro-Fit: mf_nominal, mf_moderate, mf_noise_1mm); per condition, divide n by 4 or 3.", "",
           "## Success, C against I, J and F", "",
           "| Machine | Suite | C vs | Pairs (3 seeds) | Success C / other | p(C only) / p(other only) | "
           "Power at 100 pairs | n for 80% power | n per seed |", "|---|---|---|---|---|---|---|---|---|"]
    pooled = {}
    for k in keys:
        cs = [d[k] for d in per_run.values() if k in d]
        tot = {f: sum(c[f] for c in cs) for f in cs[0]}
        pooled[k] = tot
        n = tot["n"]
        p10, p01 = tot["b"] / n, tot["c"] / n
        ns = [n_for_power(c["b"] / c["n"], c["c"] / c["n"]) for c in cs]
        rng = ", ".join(fmt_n(x, c["b"], c["c"]) for x, c in zip(ns, cs))
        out.append(f"| {k[0]} | {k[1]} | {letter[k[2]]} | {n:,} | {100 * tot['sc'] / n:.1f}% / "
                   f"{100 * tot['so'] / n:.1f}% | {100 * p10:.2f}% / {100 * p01:.2f}% | "
                   f"{power(100, p10, p01):.2f} | {fmt_n(n_for_power(p10, p01), p10, p01)} | {rng} |")
    out += ["", "## Bad units passed on good-part trials, C against I, J and F", "",
            "| Machine | Suite | C vs | Pairs (3 seeds) | Bad units C / other | p(C only) / p(other only) | "
            "Power at 100 pairs | n for 80% power | n per seed |", "|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        tot = pooled[k]
        cs = [d[k] for d in per_run.values() if k in d]
        n = tot["n"]
        p10, p01 = tot["eb"] / n, tot["ec"] / n
        ns = [n_for_power(c["eb"] / c["n"], c["ec"] / c["n"]) for c in cs]
        rng = ", ".join(fmt_n(x, c["eb"], c["ec"]) for x, c in zip(ns, cs))
        out.append(f"| {k[0]} | {k[1]} | {letter[k[2]]} | {n:,} | {tot['ecc']} / {tot['eco']} | "
                   f"{100 * p10:.2f}% / {100 * p01:.2f}% | {power(100, p10, p01):.2f} | "
                   f"{fmt_n(n_for_power(p10, p01), p10, p01)} | {rng} |")
    out += ["", "## Zero bad units: the Wilson 95% upper bound reachable at each n", "",
            "If a controller passes 0 bad units in n trials, the Wilson 95% upper bound on its rate is "
            "z^2 / (n + z^2).", "", "| n | 50 | 100 | 200 | 300 | 500 | 1,000 | 2,000 | 3,000 | 5,000 | 10,000 |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "| Upper bound for 0/n | " + " | ".join(f"{100 * wilson_upper_zero(n):.2f}%" for n in
                                              (50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000)) + " |", "",
            "n needed before 0/n has an upper bound below the other controller's pooled bad-unit rate (one-sample "
            "view; the paired test above is the pre-registered one):", "",
            "| Machine | Suite | Other | Other's bad-unit rate (3 seeds) | n for 0/n upper bound below it |",
            "|---|---|---|---|---|"]
    for k in keys:
        tot = pooled[k]
        r = tot["eco"] / tot["n"]
        out.append(f"| {k[0]} | {k[1]} | {letter[k[2]]} | {tot['eco']} / {tot['n']:,} = {100 * r:.2f}% | "
                   f"{n_for_zero_upper(r):,} |" if r > 0 else
                   f"| {k[0]} | {k[1]} | {letter[k[2]]} | 0 / {tot['n']:,} | not defined |")
    out += ["", "## Where the bad units are (all three seeds, good-part trials)", "",
            "Full depth: housing-only >= 14.5 mm of 15 mm, Micro-Fit >= 7.5 mm of 8 mm. The pass limits are "
            "abs(tilt) and abs(yaw) <= 3 deg, so a pose measurement for the rig has to resolve a few tenths of a degree "
            "around 3 deg at full depth.", ""]
    out += pose_rows(a.results)
    print("\n".join(out))


if __name__ == "__main__":
    main()
