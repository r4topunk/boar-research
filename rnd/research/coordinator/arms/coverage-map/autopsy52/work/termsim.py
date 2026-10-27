import json, sqlite3, math, collections
SP="<scratch>"
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"
G=json.load(open(C+"autopsy52/work/gold_cm.json"))
R={json.loads(l)["id"]:json.loads(l) for l in open(C+"compose/replays/main.N10.gidf.jsonl") if l.strip()}
D=collections.defaultdict(list)
for l in open(SP+"aut52.dump.jsonl"):
    d=json.loads(l); D[d["query"]].append(d)
DB={p:sqlite3.connect(f"file:<workspace>/shared-data/packs/wave3/{p}.sqlite?mode=ro",uri=True) for p in ("qa-cooking-se","qa-money-se")}
def mt(s): return f'"{s[:-1]}"*' if s.endswith("i") and len(s)>4 else f'"{s}"'
def run(db, terms, pool=80, per=2, prior=0.5):
    rows=db.execute(f"select f.rowid, f.s, c.article_id, a.views from (select rowid, bm25(fts,2,1,1) s from fts where fts match ? order by s limit ?) f join chunks c on c.id=f.rowid join articles a on a.id=c.article_id",(" OR ".join(map(mt,terms)),pool)).fetchall()
    sc=sorted(((-s+prior*math.log10(1+v)),a,r) for r,s,a,v in rows)[::-1]
    n=collections.Counter(); out=[]
    for s,a,r in sc:
        n[a]+=1
        if n[a]<=per: out.append((a,r))
    return out
def qt(stems, maxdf, keep):
    rk=sorted(stems,key=lambda x:-x[1]); k=[s for s,i in rk if i>=math.log(1/maxdf)]
    return k if len(k)>=keep else [s for s,i in rk[:keep]]
res={}
for i,g in G.items():
    d=[x for x in D[R[i]["query"]] if (("cooking" in x["pack"]) if g["pack"]=="qa-cooking-se" else ("Money" in x["pack"])) and x["k"]==12][0]
    st=d["stems"]; db=DB[g["pack"]]; A=g["article_id"]; row={}
    for name,terms in [("cur",qt(st,.02,3)),("df10",qt(st,.10,3)),("df25",qt(st,.25,3)),("all",[s for s,_ in st])]:
        lst=run(db,terms); arts=[]
        for a,_ in lst:
            if a not in arts: arts.append(a)
        row[name]=arts.index(A) if A in arts else None
    res[i]=dict(row, stems=[s for s,_ in sorted(st,key=lambda x:-x[1])], cur=qt(st,.02,3))
    print(f"{i[3:]:18}", {k:v for k,v in row.items()}, "dropped:", [s for s,idf in st if idf<math.log(50)])
json.dump(res,open(C+"autopsy52/work/termsim.json","w"),indent=1)
for k in ("cur","df10","df25","all"):
    v=[r[k] for r in res.values()]
    print(k, "top1",sum(x is not None and x<1 for x in v),"top3",sum(x is not None and x<3 for x in v),"pool",sum(x is not None for x in v))
