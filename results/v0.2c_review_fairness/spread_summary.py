import csv, glob, os, sys, json
from collections import Counter
base = sys.argv[1]
for d in sorted(glob.glob(base + '/*')):
    f = d + '/trials.csv'
    if not os.path.exists(d + '/summary.json'): continue
    cfg = json.load(open(d + '/config.json'))['environment']
    rows = list(csv.DictReader(open(f)))
    for ctl in ('adaptive', 'spiral_rcc'):
        r = [x for x in rows if x['controller'] == ctl]
        s = sum(x['success'] == 'True' for x in r)
        fr = sum(x['declared_success'] == 'False' and x['gt_seated'] == 'True' for x in r)
        lat = sum(x['gt_seated'] == 'True' for x in r)
        reasons = Counter(x['failure_reason'] for x in r if x['success'] != 'True')
        print(f"{os.path.basename(d):18s} {ctl:10s} success {s}/{len(r)} gt_seated {lat} false_rejects {fr} {dict(reasons)} [{cfg['git_commit'][:7]} dirty={cfg['git_dirty']}]")
