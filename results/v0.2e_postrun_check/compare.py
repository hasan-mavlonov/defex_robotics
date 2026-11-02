import csv,sys
from experiments.checkpoint_report import ok, escape
OUT=('success','declared_success','protective_stop','failure_reason')
def cmp(old,new):
    o={(r['controller'],r['condition'],r['trial_index']):r for r in csv.DictReader(open(old))}
    n={(r['controller'],r['condition'],r['trial_index']):r for r in csv.DictReader(open(new))}
    keys=[k for k in o]
    assert all(k in n for k in keys)
    for ctl in sorted({k[0] for k in keys}):
        ks=[k for k in keys if k[0]==ctl]
        oc=sum(any(o[k][f]!=n[k][f] for f in OUT) for k in ks)
        rc=sum(any(o[k][f]!=n[k][f] for f in o[k] if f!='wall_time_s') for k in ks)
        print(f'{ctl}: {len(ks)} trials; seated v0.2d code {sum(ok(o[k]) for k in ks)}, v0.2e code {sum(ok(n[k]) for k in ks)}; outcome changes {oc}; rows changed {rc}')
cmp(sys.argv[1],sys.argv[2])
