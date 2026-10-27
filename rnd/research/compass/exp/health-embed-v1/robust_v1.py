import json, numpy as np
from sklearn.linear_model import LogisticRegression
E=[json.loads(l) for l in open("../health-embed/eval.jsonl")]; B=json.load(open("emb.json"))
nz=lambda a:(lambda x:x/np.linalg.norm(x,axis=1,keepdims=True))(np.array(a))
P,N,X=nz(B["pos"]),nz(B["neg"]),nz(B["eval"])
dz=np.array([e["label"]=="danger" for e in E]); pub=np.array(["pub" in e["src"] for e in E])
fit=lambda a,b:LogisticRegression(C=10,max_iter=2000,class_weight="balanced").fit(np.vstack([a,b]),[1]*len(a)+[0]*len(b))
p=fit(P,N).predict_proba(X)[:,1]
o=np.argsort(-p*(~dz))[:5]; print("top non-danger p:",[(E[i]["id"],round(p[i],3)) for i in o])
print("danger p<0.6:",[(E[i]["id"],round(p[i],3)) for i in np.where(dz&(p<.6))[0]])
rng=np.random.default_rng(0);R=[]
for _ in range(200):
    a=rng.choice(len(P),int(.7*len(P)),replace=False);b=rng.choice(len(N),int(.7*len(N)),replace=False)
    q=fit(P[a],N[b]).predict_proba(X)[:,1]>.5;R.append((q[dz].sum(),q[~dz&~pub].sum(),q[~dz&pub].sum()))
R=np.array(R);f=lambda c:f"median {np.median(R[:,c]):.0f} (5-95%: {np.percentile(R[:,c],5):.0f}-{np.percentile(R[:,c],95):.0f})"
print("70% subsample x200: danger",f(0),"/39; FP non-bench",f(1),"/181; FP bench-public",f(2),"/55")
