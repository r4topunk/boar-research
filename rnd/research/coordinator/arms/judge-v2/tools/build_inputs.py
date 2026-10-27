#!/usr/bin/env python3
"""JUDGE-V2 inputs (0 LLM). Builds data/items-dev97.jsonl (id, set, question, notes = the item's `rubric` author notes, reference = the frozen
reference answer the v1 judge uses) and data/answers-K0main.jsonl (the cached mini K0 MAIN control answers, id/text/declined) and
data/answers-ref.jsonl (reference answers as answers, for the v2 denominator). Dev sets only: bench v0.1 public (57) + qa-cooking-se / qa-money-se self-tests (40)."""
import json, os, sys
B = "<workspace>"; BE = f"{B}/boar-eval/bench"; A = f"{B}/rnd/research/coordinator/arms"; D = f"{A}/judge-v2/data"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(f"{A}/lp-screens/main-97.ids").read().split()
src = {"v01": (f"{BE}/v0.1/questions.public.jsonl", f"{BE}/v0.1/refs/refs.jsonl")}
for u in ("qa-cooking-se", "qa-money-se"): src[u] = (f"{BE}/selftest/{u}/questions.jsonl", f"{BE}/selftest/{u}/refs/refs.jsonl")
Q, R, S = {}, {}, {}
for u, (qf, rf) in src.items():
    for q in rd(qf): Q[q["id"]] = q; S[q["id"]] = u
    for r in rd(rf):
        if r.get("ok"): R[r["id"]] = r["answer"]
T = {t["itemId"]: t for t in rd(f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl")}
os.makedirs(D, exist_ok=True)
with open(f"{D}/items-dev97.jsonl", "w") as f, open(f"{D}/answers-K0main.jsonl", "w") as g, open(f"{D}/answers-ref.jsonl", "w") as h:
    for i in ids:
        q = Q[i]; assert i in R and i in T and not T[i].get("error"), i
        f.write(json.dumps(dict(id=i, set=S[i], question=q["question"], notes=q.get("rubric") or [], reference=R[i]), ensure_ascii=False) + "\n")
        g.write(json.dumps(dict(id=i, text=T[i]["answer"]["text"], declined=bool(T[i]["answer"].get("declined"))), ensure_ascii=False) + "\n")
        h.write(json.dumps(dict(id=i, text=R[i], declined=False), ensure_ascii=False) + "\n")
print(len(ids), "items;", sum(bool(Q[i].get("rubric")) for i in ids), "with author notes")
