# DEEPROUTE out-of-sample check of the R2/R8 routing signals on cut 6 claim traces (script-only; prints counts only, never item text)
import json, glob, re, sys, statistics as st
B="<workspace>"
def rd(p): return [json.loads(l) for l in open(p) if l.strip()]
def has(t, rx): return any(re.match(rx, c) for c in t.get("route",{}).get("reasonCodes",[]))
def maj(vals): return sum(vals) > len(vals)/2
def load(traces_paths, judg_paths, ids_filter=None):
    T={}
    for p in traces_paths:
        for t in rd(p):
            if t.get("error"): continue
            T.setdefault(t["itemId"],[]).append(t)
    J={}
    for p in judg_paths:
        by={}
        for r in rd(p):
            if not r.get("ok"): continue
            by.setdefault(r["queryId"],{})[r["order"]]=r["mapped"]
        for id,o in by.items():
            if "boarA" in o and "boarB" in o:
                c=(o["boarA"]["boar"]["correctness"]+o["boarB"]["boar"]["correctness"])/2
                J.setdefault(id,[]).append(c)
    rows=[]
    for id,ts in T.items():
        if ids_filter and id not in ids_filter: continue
        if id not in J: continue
        rows.append(dict(id=id,
            noSource=maj([has(t, r"^grounding:(no-good-source|no-source-memory)$") for t in ts]),
            offTopic=maj([has(t, r"^instant:off-topic$") for t in ts]),
            weak=maj([bool(t["answer"].get("weakSources")) for t in ts]),
            declined=maj([bool(t["answer"].get("declined")) for t in ts]),
            tier=ts[0].get("route",{}).get("tier"), task=ts[0].get("route",{}).get("task"),
            corr=st.mean(J[id]), nseeds=len(ts)))
    return rows
def report(name, rows, cat):
    n=len(rows); print(f"\n== {name}: n={n} (seeds per item: {sorted(set(r['nseeds'] for r in rows))})")
    for sig in ["noSource","offTopic","weak","declined"]:
        s=[r for r in rows if r[sig]]; o=[r for r in rows if not r[sig]]
        f=lambda xs: (f"{st.mean([x['corr'] for x in xs]):.2f}", f"{sum(1 for x in xs if x['corr']<=2)}/{len(xs)}") if xs else ("-","-")
        print(f"  {sig:9s}: routed {len(s):3d} ({100*len(s)/n:4.1f}%)  4B corr mean routed/other {f(s)[0]}/{f(o)[0]}  corr<=2 routed/other {f(s)[1]} / {f(o)[1]}")
    r8=[r for r in rows if r["noSource"] or r["offTopic"]]
    print(f"  R8 (noSource|offTopic): routed {len(r8)} ({100*len(r8)/n:.1f}%)  corr<=2 captured {sum(1 for r in r8 if r['corr']<=2)}/{sum(1 for r in rows if r['corr']<=2)}")
    if cat:
        from collections import defaultdict
        d=defaultdict(lambda:[0,0])
        for r in rows:
            c=cat.get(r["id"],"?"); d[c][1]+=1; d[c][0]+= 1 if r["noSource"] else 0
        print("  R2 by category: " + ", ".join(f"{c} {v[0]}/{v[1]}" for c,v in sorted(d.items())))
    tiers={}; 
    for r in rows: tiers[r["tier"]]=tiers.get(r["tier"],0)+1
    print("  tiers:", tiers)
# v0.2
D=f"{B}/blind/bench-v02/runs-cut6"
cat={}
for q in glob.glob(f"{B}/blind/bench-v02/**/questions*.jsonl", recursive=True):
    for x in rd(q):
        if "id" in x and "category" in x: cat[x["id"]]=x["category"]
rows=load([f"{D}/cut6-v02-s42.traces.jsonl",f"{D}/cut6-v02-s43.traces.jsonl"],[f"{D}/cut6-v02-s42.judgments.jsonl",f"{D}/cut6-v02-s43.judgments.jsonl"])
report("v0.2 held-out (burnt→dev), cut 6, s42+s43", rows, cat)
# V-para
V=f"{B}/blind/V-para/runs-cut6"
ids=set(l.strip() for l in open(f"{V}/judged.ids") if l.strip())
rows=load([f"{V}/cut6-vpara-s42.traces.jsonl",f"{V}/cut6-vpara-s43.traces.jsonl"],[f"{V}/cut6-vpara-s42.judgments.jsonl",f"{V}/cut6-vpara-s43.judgments.jsonl"], ids)
report("V-para (51 judged), cut 6 config (b), s42+s43", rows, None)
# v0.1 reference (same signal on the v0.1 cut6 claim run)
rows=load([f"{D}/cut6-v01-s42.traces.jsonl",f"{D}/cut6-v01-s43.traces.jsonl"],[f"{D}/cut6-v01-s42.judgments.jsonl",f"{D}/cut6-v01-s43.judgments.jsonl"])
report("v0.1 (dev, in-sample reference), cut 6, s42+s43", rows, None)
