# DEEPTHINK-2 per-category diagnostic (= deepthink/tools/dtcat.py; script-only; counts/aggregates only). Arm A (T2) vs arm B (T or D), judged ids only.
# python3 dtcat.py <label> <ids file> "<T judgments, space-sep>" "<D judgments, space-sep>" [out.json]
import json, glob, statistics as st, collections, sys
V="<private held-out dir>"
def rd(p): return [json.loads(l) for l in open(p) if l.strip()]
def pairs(p):
    by={}
    for r in rd(p):
        if r.get("ok"): by.setdefault(r["queryId"],{})[r["order"]]=r["mapped"]
    out={}
    for id,o in by.items():
        if "boarA" in o and "boarB" in o:
            m=lambda s:(s["correctness"]+s["completeness"]+s["usefulness"])/3
            out[id]=(st.mean(m(o[k]["boar"]) for k in o), st.mean(m(o[k]["ref"]) for k in o), st.mean(o[k]["boar"]["correctness"] for k in ("boarA","boarB")))
    return out
def load(files):
    acc={}
    for f in files:
        for id,v in pairs(f).items(): acc.setdefault(id,[]).append(v)
    return {id:tuple(st.mean(x[i] for x in v) for i in range(3)) for id,v in acc.items()}
cat={}
for q in glob.glob(f"{V}/**/items*.jsonl",recursive=True)+glob.glob(f"{V}/**/questions*.jsonl",recursive=True):
    for x in rd(q):
        if "id" in x and "category" in x: cat[x["id"]]=x["category"]
label, idf, tf, df = sys.argv[1:5]
want=set(open(idf).read().split()); T=load(tf.split()); D=load(df.split())
ids=sorted(want&set(T)&set(D))
ratio=lambda S,xs: sum(S[i][0] for i in xs)/sum(S[i][1] for i in xs)
def row(xs):
    return {"n":len(xs),"T":round(ratio(T,xs),3),"D":round(ratio(D,xs),3),"d":round(ratio(T,xs)-ratio(D,xs),3),
            "better":sum(T[i][0]>D[i][0]+1e-9 for i in xs),"same":sum(abs(T[i][0]-D[i][0])<=1e-9 for i in xs),"worse":sum(T[i][0]<D[i][0]-1e-9 for i in xs),
            "corrT":round(st.mean(T[i][2] for i in xs),2),"corrD":round(st.mean(D[i][2] for i in xs),2)}
by=collections.defaultdict(list)
for i in ids: by[cat.get(i,"?")].append(i)
res={"label":label,"all":row(ids),"byCategory":{c:row(xs) for c,xs in sorted(by.items(),key=lambda kv:-len(kv[1]))}}
print(f"== {label}: n={len(ids)}  all {res['all']}")
for c,r in res["byCategory"].items(): print(f"  {c:18s} {r}")
if len(sys.argv)>5: json.dump(res,open(sys.argv[5],"w"),indent=1)
