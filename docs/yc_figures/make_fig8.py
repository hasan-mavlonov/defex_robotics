import csv, statistics, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
repo, cell, out = sys.argv[1], sys.argv[2], sys.argv[3]
SURF="#fcfcfb"; INK="#0b0b0b"; INK2="#52514e"; GRID="#e6e5e0"; BLUE="#2a78d6"; ORANGE="#eb6834"; GRAY="#8a8984"
plt.rcParams.update({"figure.facecolor":SURF,"axes.facecolor":SURF,"savefig.facecolor":SURF,"axes.edgecolor":GRID,
  "text.color":INK,"xtick.color":INK2,"ytick.color":INK2,"font.size":11,"axes.spines.top":False,"axes.spines.right":False,"axes.spines.left":False})
rows=list(csv.DictReader(open(f"{repo}/results/v0.2g_noverify_dev/{cell}/trials.csv")))
T=lambda v:v=="True"
ctls=[("adaptive","C Defex\nwith VERIFY",BLUE),("adaptive@noverify","C Defex\nNO VERIFY",GRAY),
      ("spiral_rcc_pull","I spiral\n+ pull test",ORANGE),("spiral_rcc_verify","J spiral\n+ Defex VERIFY",BLUE)]
stats=[]
for c,_,_ in ctls:
    d=[r for r in rows if r["controller"]==c]
    s=sum(T(r["success"]) for r in d); n=len(d)
    esc=sum(T(r["declared_success"]) and not T(r["gt_seated"]) for r in d)
    med=statistics.median(float(r["cycle_time_s"]) for r in d if T(r["success"]))
    stats.append((100*s/n, esc, med, n))
fig,axs=plt.subplots(1,3,figsize=(15,4.6))
panels=[("Seated correctly (%)",0,"{:.1f}%",(90,100.8)),("Bad plugs called 'done'",1,"{:d}",None),("Time per good part (median, s)",2,"{:.2f} s",None)]
for ax,(title,i,fmt,yl) in zip(axs,panels):
    vals=[st[i] for st in stats]
    ax.bar(range(4),vals,0.62,color=[c for _,_,c in ctls])
    if yl: ax.set_ylim(*yl)
    else: ax.set_ylim(0,max(vals)*1.18 if max(vals)>0 else 1)
    for k,v in enumerate(vals):
        ax.text(k,v+(0.15 if yl else max(vals)*0.02),fmt.format(v),ha="center",va="bottom",fontsize=10)
    ax.set_xticks(range(4)); ax.set_xticklabels([l for _,l,_ in ctls],fontsize=9)
    ax.set_yticks([]); ax.set_title(title,loc="left",fontsize=12,fontweight="bold",pad=14)
n=stats[0][3]
fig.suptitle(f"What happens if Defex skips VERIFY? {cell.replace('_',' ')}, same {n:,} sockets for all four (development seed 2026)",fontsize=12,y=1.04)
fig.text(0.5,-0.04,"Without VERIFY, Defex is faster but ships crooked plugs at the same rate as spiral search. VERIFY is what removes them.",ha="center",color=INK2)
fig.savefig(out,dpi=200,bbox_inches="tight",pad_inches=0.25)
