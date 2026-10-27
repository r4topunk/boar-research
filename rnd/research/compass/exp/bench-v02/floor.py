# Rubric floor: what the judge gives declined answers (read-only over night judgments).
import json, collections, numpy as np, glob
B="<workspace>/boar-eval/runs/night-2026-10-01/"
K=("correctness","completeness","usefulness"); mean=lambda s: sum(s[k] for k in K)/3
dec=[]; ans=[]; per_dim=collections.defaultdict(list); refs=[]
for run in ["ios-main-s42","ios-main-s43","ios-main-s44","and-qwen-s42","and-qwen-s43","and-gemma-s42","and-gemma-s43"]:
    T={json.loads(l)["itemId"]:json.loads(l) for l in open(B+run+".traces.jsonl")}
    J=collections.defaultdict(list)
    for l in open(B+run+".judgments.jsonl"):
        r=json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"])
    for q,v in J.items():
        if len(v)!=2 or q not in T: continue
        b=np.mean([mean(x["boar"]) for x in v]); refs.append(np.mean([mean(x["ref"]) for x in v]))
        if T[q]["answer"]["declined"]:
            dec.append(b); [per_dim[k].append(np.mean([x["boar"][k] for x in v])) for k in K]
        else: ans.append(b)
F=np.mean(dec); R=np.mean(refs)
print(f"declined answers judged: n={len(dec)}  mean rubric {F:.2f}/5 (per dim: "+", ".join(f"{k} {np.mean(per_dim[k]):.2f}" for k in K)+f"); answered n={len(ans)} mean {np.mean(ans):.2f}; ref mean {R:.2f}")
print(f"decline-everything system ratio ≈ {F/R:.3f}")
# floor-adjusted ratio for the Android 4B and the iPhone 1.5B (s42+s43), floor = 1.0 (rubric minimum) and floor = declined mean
for grp,runs in [("Android Qwen3-4B",["and-qwen-s42","and-qwen-s43"]),("iPhone 1.5B",["ios-main-s42","ios-main-s43"]),("Android Gemma E4B",["and-gemma-s42","and-gemma-s43"])]:
    S=[];Rr=[]
    for run in runs:
        J=collections.defaultdict(list)
        for l in open(B+run+".judgments.jsonl"):
            r=json.loads(l)
            if r.get("ok"): J[r["queryId"]].append(r["mapped"])
        for q,v in J.items():
            if len(v)==2: S.append(np.mean([mean(x["boar"]) for x in v])); Rr.append(np.mean([mean(x["ref"]) for x in v]))
    S,Rr=np.array(S),np.array(Rr)
    raw=S.sum()/Rr.sum(); f1=(S-1).sum()/(Rr-1).sum(); fd=(S-F).clip(min=None).sum()/(Rr-F).sum()
    print(f"{grp:18} raw {raw:.3f}  floor=1 (rubric min) {f1:.3f}  floor=declined mean {fd:.3f}")
