# Offline check of candidate C1: answers that OPEN by denying the question's premise, on non-compact tiers. Pattern frozen before looking.
import json, re, collections
B="<workspace>/boar-eval/runs/night-2026-10-01/"
Q={json.loads(l)["id"]:json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
PREFACE=re.compile(r"^This answer is not from an offline source[^\n]*\n+|^Esta resposta n[ãa]o [^\n]*\n+", re.I)
DENY=re.compile(r"^(no[,.!]|nope|there (is|are|was|were) no\b|[^.]{0,80}\b(does|do|did|is|are|was|were|has|have|had) not\b|[^.]{0,80}\b(doesn't|don't|didn't|isn't|aren't|wasn't|weren't|hasn't|haven't|never)\b|n[ãa]o[,.]|n[ãa]o (h[áa]|existe|existem)\b)", re.I)
rows=[]
for run in ["and-qwen-s42","and-qwen-s43","and-gemma-s42","and-gemma-s43"]:
    T={json.loads(l)["itemId"]:json.loads(l) for l in open(B+run+".traces.jsonl")}
    J=collections.defaultdict(list)
    for l in open(B+run+".judgments.jsonl"):
        r=json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
    for q,t in T.items():
        a=t["answer"]
        if a["declined"] or q not in Q: continue
        cs=J.get(q)
        if not cs or len(cs)!=2: continue
        c=sum(cs)/2; lab="pass" if c>=4 else "cw" if c<=1 else "fail"
        body=PREFACE.sub("",a["text"].strip()); first=re.split(r"(?<=[.!?])\s",body,1)[0]
        rows.append({"run":run,"id":q,"cat":Q[q]["category"],"lab":lab,"deny":bool(DENY.search(first)),"cited":bool(a.get("cited")),"first":first[:120]})
C=collections.Counter((r["deny"],r["cited"],r["lab"]) for r in rows)
for d in (True,False):
    for ci in (False,True):
        n=sum(C[(d,ci,l)] for l in ("pass","fail","cw"))
        if n: print(f"denial-opening={d!s:5} cited={ci!s:5} n={n:3}  pass {C[(d,ci,'pass')]:2}  fail {C[(d,ci,'fail')]:2}  cw {C[(d,ci,'cw')]:2}")
print("\ndenial-opening, uncited:")
for r in rows:
    if r["deny"] and not r["cited"]: print(f"  {r['lab']:4} {r['run']:14} {r['id']:12} [{r['cat']}] {r['first']!r}")
