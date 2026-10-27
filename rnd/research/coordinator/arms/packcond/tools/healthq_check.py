#!/usr/bin/env python3
"""HEALTHQ step 0 (0 calls): on the v0.2 items whose trace carries grounding:health-strict, does the engine's health search
query keep the destinations the question names (Wikivoyage guide titles, exact or redirect)? Prints ids, counts, booleans only.
Inputs: blind/bench-v02/live/v0.2/questions.v02-new.jsonl (id, question), blind/bench-v02/runs-packcond/p4b-v02.jsonl (id, query,
codes, raw_titles), shared-data/packs/boar-wikivoyage-en.sqlite (articles, redirects). Never prints question or query text."""
import json, re, sqlite3, sys
ROOT="<workspace>"
Q=f"{ROOT}/blind/bench-v02/live/v0.2/questions.v02-new.jsonl"; R=f"{ROOT}/blind/bench-v02/runs-packcond/p4b-v02.jsonl"
db=sqlite3.connect(f"file:{ROOT}/shared-data/packs/boar-wikivoyage-en.sqlite?mode=ro", uri=True)
SRC_VOY=1  # SOURCES index of enwikivoyage in wikiPack.ts
def resolve(t):
    r=db.execute("SELECT id FROM articles WHERE title=? COLLATE NOCASE AND source=? ORDER BY views DESC LIMIT 1",(t,SRC_VOY)).fetchone()
    if r: return r[0]
    r=db.execute("SELECT r.article_id FROM redirects r JOIN articles a ON a.id=r.article_id WHERE r.title=? AND a.source=? LIMIT 1",(t,SRC_VOY)).fetchone()
    return r[0] if r else None
STOP={"what","where","when","which","who","how","why","is","are","do","does","can","should","i","my","the","a","an","in","on","at","to","for","of","and","or","if","it","there","this","that","we","our","you","your","me","us"}
def places(q):
    words=re.findall(r"[\w'’()-]+", q)
    out={}
    n=len(words)
    for i in range(n):
        if not words[i][:1].isupper(): continue
        for L in (4,3,2,1):
            if i+L>n: break
            cand=" ".join(words[i:i+L]).strip(",.?!")
            if L==1 and (cand.lower() in STOP or i==0): continue
            if L>1 and not all(w[:1].isupper() for w in words[i:i+L]): continue
            aid=resolve(cand)
            if aid is not None: out[aid]=cand; break
    return out
qs={}
for l in open(Q):
    try:
        o=json.loads(l); qs[o["id"]]=o.get("question") or o.get("query") or ""
    except Exception: pass
rows=[json.loads(l) for l in open(R) if l.strip()]
hs=[r for r in rows if any(c=="grounding:health-strict" for c in r.get("codes",[]))]
print("health-strict items:", len(hs), "| all items:", len(rows))
tot_named=tot_dropped=items_named=items_dropped=0
for r in hs:
    q=qs.get(r["id"],""); eq=(r.get("query") or "").lower()
    pl=places(q)
    kept=[t for t in pl.values() if t.lower() in eq]
    dropped=[t for t in pl.values() if t.lower() not in eq]
    raw_n=len(r.get("raw") or r.get("raw_titles") or [])
    items_named+=bool(pl); items_dropped+=bool(dropped); tot_named+=len(pl); tot_dropped+=len(dropped)
    print(f'{r["id"]}: named_guides={len(pl)} kept_in_query={len(kept)} dropped={len(dropped)} query_changed={eq!=q.lower().strip()} raw_n={raw_n} empty_raw={raw_n==0}')
print(f"summary: items naming a guide {items_named}/{len(hs)}; items with a dropped guide {items_dropped}/{len(hs)}; guides named {tot_named}, dropped {tot_dropped}")
