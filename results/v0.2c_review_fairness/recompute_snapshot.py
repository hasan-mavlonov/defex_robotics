import csv, sys, math, statistics
from math import comb
def b(x): return x == 'True'
def mcnemar(a, c):
    n = a + c
    if n == 0: return 1.0
    k = min(a, c)
    p = 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return c-h, c+h
def esc(r): return (not b(r['success'])) and (not b(r['protective_stop'])) and r['declared_success'] != 'False'
def load(path):
    rows = list(csv.DictReader(open(path)))
    return rows
folder = sys.argv[1]
for suite in sys.argv[2:]:
    rows = load(f"{folder}/{suite}/trials.csv")
    latch = 'latching' in suite
    by = {}
    for r in rows:
        bad = r['condition'] in ('mf_half_latched','mf_broken_latch','mf_stubbed_terminal','mf_wrong_polarization')
        if latch and bad: continue
        by.setdefault(r['controller'], {})[(r['condition'], r['trial_index'])] = r
    print('==', suite)
    C = by['adaptive']
    for ctl, d in by.items():
        n = len(d); k = sum(b(r['success']) for r in d.values())
        lo, hi = wilson(k, n)
        keys = set(d) & set(C)
        a = sum(b(C[x]['success']) and not b(d[x]['success']) for x in keys)
        c = sum(not b(C[x]['success']) and b(d[x]['success']) for x in keys)
        ct = [float(r['cycle_time_s']) for r in d.values()]
        stops = sum(b(r['protective_stop']) for r in d.values())
        fr = sum(r['declared_success']=='False' and b(r['gt_seated']) for r in d.values())
        e = sum(esc(r) for r in d.values())
        busy = sum(ct) + 60*stops
        print(f"{ctl:18s} {k}/{n} {100*k/n:.1f}% ({100*lo:.1f}-{100*hi:.1f}) esc={e} fr={fr} stops={stops} p50={statistics.median(ct):.2f} uph60={3600*k/busy:.0f} vsC {a}/{c} p={mcnemar(a,c):.2g}")
    if latch:
        for ctl in by:
            bad = [r for r in rows if r['controller']==ctl and r['condition'].startswith('mf_') and r['condition'] in ('mf_half_latched','mf_broken_latch','mf_stubbed_terminal','mf_wrong_polarization')]
            print('  bad', ctl, sum(esc(r) for r in bad), '/', len(bad), 'time/bad', round(statistics.mean(float(r['cycle_time_s']) for r in bad),2))
