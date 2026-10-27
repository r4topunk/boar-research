# v1 threshold selection. Rule declared before looking at outputs: fit LR on v1 prototypes;
# selection set = Compass eval minus every bench-public item ("pub" in src); non-danger = neg + health_info
# (matches QUEUE #4 D2). tau = smallest value in a 0.50..0.95 grid (step .05) with FP <= 1% on selection non-danger.
# Bench public is then reported as a check only.
import json, numpy as np, hashlib
from sklearn.linear_model import LogisticRegression
E=[json.loads(l) for l in open("../health-embed/eval.jsonl")]; B=json.load(open("emb.json"))
nz=lambda a:(lambda x:x/np.linalg.norm(x,axis=1,keepdims=True))(np.array(a))
P,N,X=nz(B["pos"]),nz(B["neg"]),nz(B["eval"])
lr=LogisticRegression(C=10,max_iter=2000,class_weight="balanced").fit(np.vstack([P,N]),[1]*len(P)+[0]*len(N))
p=lr.predict_proba(X)[:,1]
dz=np.array([e["label"]=="danger" for e in E]); pub=np.array(["pub" in e["src"] for e in E]); hm=np.array(["hm-fresh" in e["src"] for e in E])
sel=~pub
for t in np.arange(.5,.96,.05):
    fp=(p[sel&~dz]>t).sum(); n=(sel&~dz).sum()
    print(f"tau={t:.2f} sel: danger {(p[sel&dz]>t).sum()}/{(sel&dz).sum()} hm {(p[hm]>t).sum()}/{hm.sum()} FP {fp}/{n}={fp/n:.1%} | bench-public check: danger {(p[pub&dz]>t).sum()}/{(pub&dz).sum()} FP {(p[pub&~dz]>t).sum()}/{(pub&~dz).sum()}")
tau=next(t for t in np.arange(.5,.96,.05) if (p[sel&~dz]>t).sum()/(sel&~dz).sum()<=.01)
print("selected tau", round(tau,2))
for i in np.where(~dz&(p>tau))[0]: print("  FP",round(p[i],3),E[i]["id"],E[i]["q"][:80])
for i in np.where(dz&(p<=tau))[0]: print("  miss",round(p[i],3),E[i]["id"],E[i]["q"][:80])
for i in [j for j,e in enumerate(E) if e["id"] in ("vit-hlt-003","vit-sci-001","vit-hum-004")]: print("  v0-FP now",round(p[i],3),E[i]["id"])
json.dump({"model":"bge-small-en-v1.5-q8_0.gguf via embed.mjs (no prefix, L2-normalized)","rule":f"danger if sigmoid(w.x+b) > {round(tau,2)}","tau":round(float(tau),2),"b":float(lr.intercept_[0]),"w":[round(float(v),6) for v in lr.coef_[0]],"prototypes_sha256":hashlib.sha256(open("prototypes.json","rb").read()).hexdigest()},open("health-lr.v1.json","w"))
