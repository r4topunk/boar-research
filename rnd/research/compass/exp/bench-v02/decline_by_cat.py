# Is the always-decline floor D the same across categories? (declines on honesty-refusal items may be judged correct)
import json, collections, numpy as np
B="<workspace>/boar-eval/runs/night-2026-10-01/"
Q={json.loads(l)["id"]:json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
CAT={"danger-situation":"danger","travel-local":"travel","travel-practical":"travel"}
K=("correctness","completeness","usefulness"); mr=lambda s: sum(s[k] for k in K)/3
D=collections.defaultdict(list); Rf=collections.defaultdict(list)
for run in ["ios-main-s42","ios-main-s43","ios-main-s44","and-qwen-s42","and-qwen-s43","and-gemma-s42","and-gemma-s43"]:
    T={json.loads(l)["itemId"]:json.loads(l) for l in open(B+run+".traces.jsonl")}
    J=collections.defaultdict(list)
    for l in open(B+run+".judgments.jsonl"):
        r=json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"])
    for q,v in J.items():
        if len(v)!=2 or q not in Q: continue
        c=CAT.get(Q[q]["category"],Q[q]["category"]); Rf[c].append(np.mean([mr(x["ref"]) for x in v]))
        if T[q]["answer"]["declined"]: D[c].append(np.mean([mr(x["boar"]) for x in v]))
mix={"explanation":21,"reasoning":21,"comparison":13,"crypto":13,"honesty-refusal":12,"health":8,"danger":10,"synthesis":6,"travel":6}
num=den=0
for c in mix:
    d=np.mean(D[c]) if D[c] else np.nan; r=np.mean(Rf[c])
    print(f"{c:16} declines n={len(D[c]):2} mean rubric {d:.2f}  ref {r:.2f}  D_c {d/r:.3f}")
    if D[c]: num+=mix[c]*d; den+=mix[c]*r
print(f"mix-weighted D for v0.2-new (categories with declines only): {num/den:.3f}")
