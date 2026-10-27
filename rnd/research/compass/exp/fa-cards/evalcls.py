import json, numpy as np, collections
P=json.load(open("protos.json")); EP=json.load(open("emb-protos.json")); EV=json.load(open("../pt-recall/emb.json"))
L=json.load(open("labels.json")); rows=[json.loads(l) for l in open("../pt-recall/aug.jsonl")]
n=lambda v:(lambda a:a/np.linalg.norm(a))(np.array(v))
conds=list(P); C=np.array([n(np.mean([n(EP[t]) for t in P[c]],0)) for c in conds])
def lab(r):
    if r["set"]=="eval": return L.get(r["id"],"NEG") if r["label"]=="danger" else "NEG"
    base=r["id"].replace("-ptm-noacc","").replace("-ptm","")
    base={"hm-001":"vit-hm-001","saf-012":"saf-012","vit-hm-009":"vit-hm-009"}.get(base,base)
    return L.get(base,"other")
items=[(r["id"],lab(r),n(EV[r["q"]]),r["set"]) for r in rows]
def run(tau,mu,verbose=False):
    R=collections.Counter(); bad=[]
    for i,y,v,s in items:
        sims=C@v; o=np.argsort(-sims); top,sec=sims[o[0]],sims[o[1]]
        fire=top>=tau and top-sec>=mu; pred=conds[o[0]] if fire else None
        if y=="NEG": R["neg_fire" if fire else "neg_quiet"]+=1
        elif y in conds: R["correct" if pred==y else ("WRONG" if fire else "abstain")]+=1; 
        else: R["other_fire(wrong)" if fire else "other_quiet"]+=1
        if fire and pred!=y and y!="NEG": bad.append((i,y,pred,round(float(top),3),round(float(top-sec),3)))
        if fire and y=="NEG": bad.append((i,"NEG",pred,round(float(top),3),round(float(top-sec),3)))
    if verbose: print(bad)
    return R
for tau in (0.70,0.75,0.80):
    for mu in (0.0,0.03,0.05):
        R=run(tau,mu); print(f"tau={tau} mu={mu}: "+", ".join(f"{k} {v}" for k,v in sorted(R.items())))
print(); run(0.75,0.03,True)
