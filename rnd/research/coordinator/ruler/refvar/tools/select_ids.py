"""REFVAR id selection (0 LLM): 20 of the v0.1 57 dev ids, stratified by bench category.
Strata (category -> n): proportional to 57 -> 20, danger + danger-situation merged, travel-local + travel-practical merged.
Within a stratum: ascending sha256("refvar-2026-10-21|" + id); the first n are taken. No answer, reference or judgment is read."""
import json, hashlib, sys
A = "<workspace>/rnd/research/coordinator/arms/"
ids = [l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip()]
Q = {json.loads(l)["id"]: json.loads(l)["category"] for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
MERGE = {"danger-situation": "danger", "travel-local": "travel", "travel-practical": "travel"}
N = {"comparison": 2, "crypto": 3, "danger": 2, "explanation": 4, "health": 1, "honesty-refusal": 2, "reasoning": 4, "synthesis": 1, "travel": 1}
assert sum(N.values()) == 20
st = {}
for i in ids: st.setdefault(MERGE.get(Q[i], Q[i]), []).append(i)
assert set(st) == set(N), (set(st), set(N))
out = []
for k in sorted(N):
    out += sorted(st[k], key=lambda i: hashlib.sha256(f"refvar-2026-10-21|{i}".encode()).hexdigest())[:N[k]]
for i in out: print(i)
