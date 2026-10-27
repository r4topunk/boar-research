import json, collections
B="<workspace>/boar-eval/runs/night-2026-10-01/"
Q={json.loads(l)["id"]:json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
C=collections.Counter(); rows=[]
for s in ("s42","s43","s44"):
    T={json.loads(l)["itemId"]:json.loads(l) for l in open(B+f"ios-main-{s}.traces.jsonl")}
    J=collections.defaultdict(list)
    for l in open(B+f"ios-main-{s}.judgments.jsonl"):
        r=json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
    for q,t in T.items():
        codes=t["route"]["reasonCodes"]; task=next((c.split(":")[1] for c in codes if c.startswith("task:")),"?")
        a=t["answer"]; mem=(not a["declined"]) and not a.get("shown") and not any("no-source" in c or "card" in c for c in codes)
        if task!="chat": continue
        cs=J.get(q); lab=None
        if cs and len(cs)==2:
            c=sum(cs)/2; lab="pass" if c>=4 else "cw" if c<=1 else "fail"
        st="memory" if mem else ("declined" if a["declined"] else "sourced" if a.get("shown") else "card/other")
        C[(st,lab, bool(Q.get(q,{}).get("danger")) or q.startswith("saf-"))]+=1
for k,v in sorted(C.items(),key=str): print(k,v)
