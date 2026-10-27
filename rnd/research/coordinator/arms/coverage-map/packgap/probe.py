# PACK-GAP 0-LLM probe: per item, FTS query in each pack on disk, verify the key fact by regex in the chunk body.
import json, sys, re, sqlite3, functools
from compression import zstd
SD="<workspace>/shared-data/"
PF={"boar-crypto":SD+"crypto/boar-crypto.sqlite","boar-wikivoyage-en":SD+"packs/boar-wikivoyage-en.sqlite",
"boar-simplewiki-en":SD+"packs/v3proto/boar-simplewiki-en.sqlite","boar-factbook":SD+"packs/v3proto/boar-factbook.sqlite",
"boar-medlineplus-en":SD+"packs/v3proto/boar-medlineplus-en.sqlite","boar-firstaid-en":SD+"packs/v3proto/boar-firstaid-en.sqlite",
"boar-visa-en":SD+"packs/wave4/boar-visa-en.sqlite","qa-health-se":SD+"packs/v3proto/qa-health-se.sqlite",
"qa-outdoors-se":SD+"packs/v3proto/qa-outdoors-se.sqlite","qa-travel-se":SD+"packs/v3proto/qa-travel-se.sqlite",
"wiki-vital5":SD+"packs/wiki-vital5.sqlite",
# on disk, NOT in K13
"qa-ethereum-se":SD+"packs/v3proto/qa-ethereum-se.sqlite","qa-bitcoin-se":SD+"packs/v3proto/qa-bitcoin-se.sqlite",
"boar-preparedness-en":SD+"preparedness-v3/boar-preparedness-en.sqlite","boar-wiki-en-top100k":SD+"packs/boar-wiki-en-top100k.sqlite"}
K13={"boar-crypto","boar-wikivoyage-en","boar-simplewiki-en","boar-factbook","boar-medlineplus-en","boar-firstaid-en","boar-visa-en","qa-health-se","qa-outdoors-se","qa-travel-se","wiki-vital5","qa-cooking-se","qa-money-se"}
DB={k:sqlite3.connect(f"file:{v}?mode=ro",uri=True) for k,v in PF.items()}
@functools.lru_cache(maxsize=4096)
def block(pk,bid): return zstd.decompress(DB[pk].execute("select zdata from blocks where id=?",(bid,)).fetchone()[0])
def chunk(pk,cid):
    if pk=="wiki-vital5":
        r=DB[pk].execute("select title, body from chunks where id=?",(cid,)).fetchone(); return r
    r=DB[pk].execute("select article_id,start,end from chunks where id=?",(cid,)).fetchone()
    if not r: return None
    b,off,ln,t=DB[pk].execute("select block_id,off,len,title from articles where id=?",(r[0],)).fetchone()
    return t, block(pk,b)[off:off+ln].decode("utf-8","replace")[r[1]:r[2]]
# id: (fts query, [regexes that must ALL match one chunk body])
P=json.load(open(sys.argv[1]))
out={}
for i,(q,rx) in P.items():
    out[i]={}
    for pk in PF:
        tbl="chunks_fts" if pk=="wiki-vital5" else "fts"
        try: rows=DB[pk].execute(f"select rowid from {tbl} where {tbl} match ? order by rank limit 300",(q,)).fetchall()
        except sqlite3.OperationalError as e: out[i][pk]="ERR "+str(e); continue
        for (rid,) in rows:
            c=chunk(pk,rid)
            if not c: continue
            body=c[0]+"\n"+c[1]
            if all(re.search(r,body,re.I|re.S) for r in rx):
                m=re.search(rx[0],body,re.I|re.S); s=max(0,m.start()-60)
                out[i][pk]={"chunk":rid,"title":c[0],"snip":re.sub(r"\s+"," ",body[s:m.end()+80])}
                break
    hit=[p for p in out[i] if isinstance(out[i][p],dict)]
    print(i, "| K13:", [p for p in hit if p in K13], "| other:", [p for p in hit if p not in K13])
json.dump(out,open(sys.argv[2],"w"),indent=1)
