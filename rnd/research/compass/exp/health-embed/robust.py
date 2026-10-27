import json, numpy as np
from sklearn.linear_model import LogisticRegression
E=[json.loads(l) for l in open("eval.jsonl")]; B=json.load(open("emb.json")); RX=json.load(open("regex.json"))
nz=lambda a:(lambda x:x/np.linalg.norm(x,axis=1,keepdims=True))(np.array(a))
P,N,X=nz(B["pos"]),nz(B["neg"]),nz(B["eval"])
y=np.array([e["label"]!="neg" for e in E]); dz=np.array([e["label"]=="danger" for e in E])
hm=np.array(["hm-fresh" in e["src"] for e in E]); pt=np.array([any(c in e["q"].lower() for c in "ãçõéêáó") or e["q"].lower().startswith(("qual","quant","o que","como","em que","meu","minha","fui","acho","estou","uma ","liste","fale","desde")) for e in E])
fit=lambda Pi,Ni:LogisticRegression(C=10,max_iter=2000,class_weight="balanced").fit(np.vstack([Pi,Ni]),[1]*len(Pi)+[0]*len(Ni))
p=fit(P,N).predict_proba(X)[:,1]>.5
for name,rx in [("iosmain",RX["iosmain"]),("fix08c",RX["fix08c"])]:
    u=p|np.array(rx); print(f"{name} OR logreg: danger {u[dz].sum()}/{dz.sum()} hm {u[hm].sum()}/{hm.sum()} FP {u[~y].sum()}")
print(f"PT-ish neg FP {p[~y&pt].sum()}/{(~y&pt).sum()}  EN neg FP {p[~y&~pt].sum()}/{(~y&~pt).sum()}; PT danger rec {p[dz&pt].sum()}/{(dz&pt).sum()} EN danger rec {p[dz&~pt].sum()}/{(dz&~pt).sum()}")
rng=np.random.default_rng(0); R=[]
for _ in range(200):
    ip=rng.choice(len(P),int(.7*len(P)),replace=False); ineg=rng.choice(len(N),int(.7*len(N)),replace=False)
    q=fit(P[ip],N[ineg]).predict_proba(X)[:,1]>.5; R.append((q[dz].sum(),q[hm].sum(),q[~y].sum()))
R=np.array(R); print("70%% prototype subsample x200: danger rec median %d (5-95%%: %d-%d)/39, hm %d (%d-%d)/16, FP %d (%d-%d)/232"%(np.median(R[:,0]),*np.percentile(R[:,0],[5,95]),np.median(R[:,1]),*np.percentile(R[:,1],[5,95]),np.median(R[:,2]),*np.percentile(R[:,2],[5,95])))
