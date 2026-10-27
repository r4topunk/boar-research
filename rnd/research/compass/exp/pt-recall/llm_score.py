import json, re, sys
rows=[json.loads(l) for l in open("aug.jsonl")]; L=json.load(open(sys.argv[1] if len(sys.argv)>1 else "llm.json"))
en=lambda q:re.search(r"\b(the|my|what|should|is|how|i|a)\b",q.lower()) and not re.search(r"[ãõç]",q)
G={"mirror PT danger":lambda r:r["set"]=="mirror","eval PT danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and not en(r["q"]),
   "eval EN danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and en(r["q"]),"eval PT non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and not en(r["q"]),
   "eval EN non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and en(r["q"])}
for g,f in G.items():
    sub=[r for r in rows if f(r)]; print(f"{g:20} n={len(sub):3} yes={sum(L[r['id']]=='yes' for r in sub)}")
print("misses:",[r["id"] for r in rows if r["label"]=="danger" and L[r["id"]]!="yes"])
print("FPs:",[(r["id"],r["q"][:60]) for r in rows if r["label"]!="danger" and L[r["id"]]=="yes"])
