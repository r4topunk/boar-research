import json, re, collections
SP="<scratch>"
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"
G=json.load(open(C+"autopsy52/work/gold_cm.json")); L=json.load(open(C+"autopsy52/work/list52.json"))
R={json.loads(l)["id"]:json.loads(l) for l in open(C+"compose/replays/main.N10.gidf.jsonl") if l.strip()}
NAME={"Personal Finance & Money Stack Exchange Q&A":"qa-money-se"}
D=collections.defaultdict(list)
for l in open(SP+"aut52.dump.jsonl"):
    d=json.loads(l); D[d["query"]].append(d)
names=sorted({d["pack"] for v in D.values() for d in v}); print(names)
out={}
for i,g in G.items():
    q=R[i]["query"]; rows=[d for d in D.get(q,[]) if (("cooking" in d["pack"]) if g["pack"]=="qa-cooking-se" else ("Money" in d["pack"]))]
    if not rows: print(i,"NO DUMP", q[:50]); continue
    res={}
    for d in rows:
        kk="raw" if d["k"]!=12 else "wide"
        aut=d["aut"] or {}; pool=aut.get("pool",[]); A=g["article_id"]; gch=set(f["chunk_id"] for f in g["facts"])
        pa=[j for j,p in enumerate(pool) if p[1]==A]; pc=[j for j,p in enumerate(pool) if p[0] in gch]
        rej=[r for r in aut.get("rej",[]) if any(p[0]==r[0] and p[1]==A for p in pool)]
        ha=[j for j,h in enumerate(d["hits"]) if h[1]==A]; hc=[j for j,h in enumerate(d["hits"]) if h[0] in gch]
        lead=d.get("lead") or []; la=[j for j,x in enumerate(lead) if x[0]==A]
        res[kk]=dict(terms=aut.get("terms"), npool=len(pool), poolA=pa[:2], poolC=pc[:2], rejA=rej, hitsA=ha, hitsC=hc, nhits=len(d["hits"]), leadA=la[0] if la else ">300", leadS=lead[la[0]][1] if la else None, lead1=lead[0] if lead else None, ids=d.get("ids"),
                     hits=[(h[1],h[3],h[2]) for h in d["hits"]][:8])
    out[i]=res
    w=res.get("wide",{}); r=res.get("raw",{})
    print(f"{i[3:]:18} {L[i]['stage']} terms={w.get('terms')} pool={w.get('npool')} poolA={w.get('poolA')} poolC={w.get('poolC')} rejA={w.get('rejA')} hitsA(raw/wide)={r.get('hitsA')}/{w.get('hitsA')} nh={r.get('nhits')}/{w.get('nhits')} leadA={w.get('leadA')} {w.get('leadS')} lead1={w.get('lead1')}")
json.dump(out,open(C+"autopsy52/work/perpack_cm.json","w"),indent=1)
