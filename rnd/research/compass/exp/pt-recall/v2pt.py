import json, re, numpy as np
from sklearn.linear_model import LogisticRegression
rows=[json.loads(l) for l in open("aug.jsonl")]; C={**json.load(open("emb.json")),**json.load(open("emb-extra.json"))}
V1=json.load(open("../health-embed-v1/emb.json")); P2=json.load(open("prototypes.v2pt.json"))
nz=lambda a:(lambda x:x/np.linalg.norm(x,axis=-1,keepdims=True))(np.array(a))
ptpos=P2["pos"][len(V1["pos"]):]; ptneg=P2["neg"][len(V1["neg"]):]
P=nz(V1["pos"]+[C[t] for t in ptpos]); N=nz(V1["neg"]+[C[t] for t in ptneg])
lr=LogisticRegression(C=10,max_iter=2000,class_weight="balanced").fit(np.vstack([P,N]),[1]*len(P)+[0]*len(N))
h1=json.load(open("../health-embed-v1/health-lr.v1.json")); w1,b1=np.array(h1["w"]),h1["b"]
en=lambda q:re.search(r"\b(the|my|what|should|is|how|i|a)\b",q.lower()) and not re.search(r"[ãõç]",q)
X=nz([C[r["q"]] for r in rows]); p2=lr.predict_proba(X)[:,1]; p1=1/(1+np.exp(-(X@w1+b1)))
G={"mirror PT danger":lambda r:r["set"]=="mirror","eval PT danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and not en(r["q"]),
   "eval EN danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and en(r["q"]),"eval PT non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and not en(r["q"]),
   "eval EN non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and en(r["q"])}
for g,f in G.items():
    i=[k for k,r in enumerate(rows) if f(r)]
    print(f"{g:20} n={len(i):3}  v1: {(p1[i]>.5).sum():3}   v2pt: {(p2[i]>.5).sum():3}   v2pt max-nondanger/min-danger p: {p2[i].max() if 'non' in g else p2[i].min():.3f}")
print("v2pt mirror misses:",[(rows[k]["id"],round(p2[k],2)) for k in range(len(rows)) if rows[k]["set"]=="mirror" and p2[k]<=.5])
print("v2pt FPs:",[(rows[k]["id"],round(p2[k],2)) for k in range(len(rows)) if rows[k]["label"]!="danger" and p2[k]>.5])
print("v2pt eval misses:",[(rows[k]["id"],round(p2[k],2)) for k in range(len(rows)) if rows[k]["set"]=="eval" and rows[k]["label"]=="danger" and p2[k]<=.5])
