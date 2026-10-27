import json, re, sqlite3, unicodedata
from compression import zstd
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"; SD="<workspace>/shared-data/packs/wave3/"; BE="<workspace>/boar-eval/bench/selftest/"
O=json.load(open(C+"aggregates/cm-oracle.json"))
nrm=lambda s: re.sub(r"\s+"," ",unicodedata.normalize("NFKC",s or "").lower().replace("’","'")).strip()
tk=lambda s: set(w for w in re.findall(r"[a-z0-9]+",nrm(s)) if len(w)>=3)
Q={}
for pk in ("qa-cooking-se","qa-money-se"):
    for l in open(f"{BE}{pk}/questions.jsonl"):
        q=json.loads(l); Q[q["id"]]=q
out={}
for i in O:
    o=O[i]; pk=o["pack"]; aid=o["article_id"]
    db=sqlite3.connect(f"file:{SD}{pk}.sqlite?mode=ro",uri=True)
    b,off,ln,t,views=db.execute("select block_id,off,len,title,views from articles where id=?",(aid,)).fetchone()
    txt=zstd.decompress(db.execute("select zdata from blocks where id=?",(b,)).fetchone()[0])[off:off+ln].decode("utf-8","replace")
    ch=list(db.execute("select id,start,end from chunks where article_id=? order by id",(aid,)))
    st=Q[i]["selftest"]; facts=[]
    for f in st["in_pack_facts"]:
        qq=nrm(f.get("quote","")); T=tk(qq); best=None
        for j,(cid,s,en) in enumerate(ch):
            c=nrm(txt[s:en]); sc=1.0 if qq and qq in c else (len(T&tk(c))/len(T) if T else 0)
            if best is None or sc>best[0]: best=(sc,j,cid)
        facts.append(dict(fact=f["fact"],chunk_index=best[1],chunk_id=best[2],match=round(best[0],2),selftest_chunk_index=f.get("chunk_index")))
    out[i]=dict(pack=pk,article_id=aid,title=t,views=views,n_chunks=len(ch),chunk_ids=[c[0] for c in ch],facts=facts,gold=st.get("gold") or Q[i].get("gold"),keys=list(st.keys()))
json.dump(out,open(C+"sefix/gold_cm40.json","w"),indent=1)
print(len(out))
