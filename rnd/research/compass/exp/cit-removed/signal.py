# Does the citation check's verdict predict judge labels on non-compact (4B-class) answers? Read-only over night traces.
import json, collections, re
B="<workspace>/boar-eval/runs/night-2026-10-01/"
def state(t):
    codes=t["route"]["reasonCodes"]; a=t["answer"]
    rem=[int(m.group(1)) for c in codes for m in [re.match(r"citations:removed-(\d+)",c)] if m]
    if any("uncited-on-topic" in c for c in codes) and rem: return "all-cit-removed (on-topic src)"
    if any("uncited-on-topic" in c for c in codes): return "uncited, on-topic src"
    if any("no-source-memory" in c for c in codes): return "memory (preface)"
    if a.get("shown") and t["answer"].get("cited"): return "cited"
    if a.get("shown"): return "shown, other"
    return "other"
for group,runs in [("Qwen3-4B",["and-qwen-s42","and-qwen-s43"]),("Gemma E4B",["and-gemma-s42","and-gemma-s43"])]:
    C=collections.defaultdict(collections.Counter)
    for run in runs:
        T={json.loads(l)["itemId"]:json.loads(l) for l in open(B+run+".traces.jsonl")}
        J=collections.defaultdict(list)
        for l in open(B+run+".judgments.jsonl"):
            r=json.loads(l)
            if r.get("ok"): J[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
        for q,t in T.items():
            if t["answer"]["declined"]: continue
            cs=J.get(q)
            if not cs or len(cs)!=2: continue
            c=sum(cs)/2; lab="pass" if c>=4 else "cw" if c<=1 else "fail"
            C[state(t)][lab]+=1
    print("==",group)
    for s,c in sorted(C.items(),key=lambda x:-sum(x[1].values())):
        n=sum(c.values()); print(f"   {s:32} n={n:3}  pass {c['pass']:2} ({c['pass']/n:.0%})  fail {c['fail']:2}  cw {c['cw']:2} ({c['cw']/n:.0%})")
