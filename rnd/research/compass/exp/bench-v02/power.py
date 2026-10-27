# CI half-width of the quality ratio vs number of judged items, from existing Android 4B judgments (read-only).
import json, collections, numpy as np
B="<workspace>/boar-eval/runs/night-2026-10-01/"
K=("correctness","completeness","usefulness"); mean=lambda s: sum(s[k] for k in K)/3
def load(run):
    J=collections.defaultdict(dict)
    for l in open(B+run+".judgments.jsonl"):
        r=json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]]=r["mapped"]
    return {q:((mean(v["boarA"]["boar"])+mean(v["boarB"]["boar"]))/2,(mean(v["boarA"]["ref"])+mean(v["boarB"]["ref"]))/2) for q,v in J.items() if len(v)==2}
runs=[load("and-qwen-s42"),load("and-qwen-s43")]
items=sorted(set(runs[0])&set(runs[1])); n0=len(items)
S=np.array([[r[q][0] for q in items] for r in runs]); Rf=np.array([[r[q][1] for q in items] for r in runs])
ratio=S.sum()/Rf.sum(); print(f"items {n0}  ratio(2 runs) {ratio:.3f}  ref mean {Rf.mean():.2f}  boar mean {S.mean():.2f}")
rng=np.random.default_rng(11)
def boot(n_items, runs_k=2, B_=4000):
    out=[]
    for _ in range(B_):
        ii=rng.integers(0,n0,n_items)
        rr=rng.integers(0,2,(n_items,runs_k))
        s=S[rr,ii[:,None]].mean(1).sum(); f=Rf[rr,ii[:,None]].mean(1).sum(); out.append(s/f)
    lo,hi=np.percentile(out,[2.5,97.5]); return (hi-lo)/2
for n in (57,80,100,120,150,200):
    print(f"  n={n:3}  half-width 2 runs {boot(n,2):.4f}   3 runs {boot(n,3):.4f}")
