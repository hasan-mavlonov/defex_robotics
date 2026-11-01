import csv,gzip,json,re,sys
for d in sys.argv[1:]:
    rows={(r['condition'],r['controller'],r['trial_index']):r for r in csv.DictReader(open(d+'/trials.csv'))}
    ev=json.load(gzip.open(d+'/events.json.gz'))
    out=[]
    for k,e in ev.items():
        c,ctrl,i=k.split('|')
        r=rows[(c,ctrl,i)]
        for x in e:
            if x[1]=='wall_yaw':
                m=re.search(r'half free travel (-?[\d.]+) mm \(>= (-?[\d.]+)',x[2])
                out.append((c,float(m.group(1)),float(m.group(2)),x[2].split('-> ')[-1][:4],r['success'],r['failure_reason'],r['final_depth_mm'][:5]))
    from collections import defaultdict
    g=defaultdict(list)
    for o in out:
        if o[3]=='PASS': g[(o[0],o[4],o[5])].append(o[1])
    print(d)
    for k,v in sorted(g.items()):
        v.sort(); print('  ',k,'n',len(v),'half-free min/p10/median',v[0],v[len(v)//10],v[len(v)//2], 'need',[o[2] for o in out if o[0]==k[0]][0])
