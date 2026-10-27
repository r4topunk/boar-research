import json, numpy as np, collections
from terms import regex_condition
exec(open("evalcls.py").read().split("def run")[0])
qtext={r["id"]:r["q"] for r in rows}
def emb_pred(v,tau=.75,mu=.03):
    s=C@v; o=np.argsort(-s); return conds[o[0]] if s[o[0]]>=tau and s[o[0]]-s[o[1]]>=mu else None
for name,f in [("regex",lambda i,v:regex_condition(qtext[i])),("embedding .75/.03",lambda i,v:emb_pred(v)),
               ("regex, else embedding",lambda i,v:(lambda r:r if r and not r.startswith("MULTI") else (None if r else emb_pred(v)))(regex_condition(qtext[i])))]:
    R=collections.Counter(); bad=[]
    for i,y,v,s in items:
        p=f(i,v); p=None if (p and p.startswith("MULTI")) else p
        if y=="NEG": R["neg_fire" if p else "neg_quiet"]+=1; bad+= [(i,y,p)] if p else []
        elif y in conds: R["correct" if p==y else ("WRONG" if p else "abstain")]+=1; bad+= [(i,y,p)] if p and p!=y else []
        else: R["other_fire" if p else "other_quiet"]+=1; bad+= [(i,y,p)] if p else []
    print(f"{name:24} "+", ".join(f"{k} {v}" for k,v in sorted(R.items())), "| errors:", bad)
