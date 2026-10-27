import json, re, sys, numpy as np
rows=[json.loads(l) for l in open("aug.jsonl")]; C=json.load(open("emb.json"))
h=json.load(open("../health-embed-v1/health-lr.v1.json")); w,b=np.array(h["w"]),h["b"]
en=lambda q:re.search(r"\b(the|my|what|should|is|how|i|a)\b",q.lower()) and not re.search(r"[ãõç]",q)
for r in rows: v=np.array(C[r["q"]]); r["p"]=1/(1+np.exp(-(v/np.linalg.norm(v))@w-b))
G={"mirror PT":lambda r:r["set"]=="mirror","eval PT dng":lambda r:r["set"]=="eval" and r["label"]=="danger" and not en(r["q"]),
   "eval EN dng":lambda r:r["set"]=="eval" and r["label"]=="danger" and en(r["q"]),"FP non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger"}
for mf in ["llm.json","llm-4b.json"]:
    L=json.load(open(mf))
    for lo,hi in [(.25,.5),(.25,.8),(.25,1.01)]:
        f=lambda r:r["p"]>=hi or (lo<r["p"]<hi and L[r["id"]]=="yes")
        calls=sum(1 for r in rows if r["set"]=="eval" and lo<r["p"]<hi)
        print(f"{mf:12} band ({lo},{hi}): "+"  ".join(f"{g} {sum(f(r) for r in rows if gf(r))}/{sum(1 for r in rows if gf(r))}" for g,gf in G.items())+f"  calls {calls}/275")
print("eval danger p>=.8:",sum(1 for r in rows if r["set"]=="eval" and r["label"]=="danger" and r["p"]>=.8),"/39")
