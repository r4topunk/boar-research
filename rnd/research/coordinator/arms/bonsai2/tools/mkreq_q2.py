"""BONSAI2-2B Q2 request maker (0 LLM calls; public/agent-written inputs only).
Items: arms/numguard/review/{health,multiturn,final-probes,final-probes-mt}.jsonl (58 health probes; multi-turn ones carry
item.history.turns = their earlier USER turns only, no assistant turn: the probe files have none) + bench/v0.1 dng-* and vit-hlt-* (6).
Config = the first row of runs/b2-smoke-C-v01.requests.jsonl (cut 7 claim config: kit boar-crypto + boar-wikivoyage-en, quickFirst true,
alwaysComplete false, seed 42, arm cut7) with modelId set from argv.
Usage: python3 -I mkreq_q2.py <modelId> <runId> <out.requests.jsonl>"""
import json, re, sys
A = "<workspace>/rnd/research/coordinator/arms"; V1 = "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl"
base = json.loads(open(f"{A}/bonsai2/runs/b2-smoke-C-v01.requests.jsonl").readline())
mid, run, out = sys.argv[1:4]; cfg = dict(base["config"]); cfg["modelId"] = mid
items = []
for f in ["health", "multiturn", "final-probes", "final-probes-mt"]:
    for l in open(f"{A}/numguard/review/{f}.jsonl"):
        if not l.strip(): continue
        q = json.loads(l); it = {"id": q["id"], "question": q["question"], "lang": "en"}
        if q.get("turns"): it["history"] = {"turns": [{"role": "user", "text": t} for t in q["turns"]]}
        items.append(it)
for l in open(V1):
    q = json.loads(l)
    if re.match(r"^(dng-|vit-hlt-)", q["id"]): items.append({"id": q["id"], "question": q["question"], "lang": "en"})
rows = [{"protocol": base["protocol"], "runId": run, "item": it, "config": cfg, "seed": base["seed"]} for it in items]
assert len({r["item"]["id"] for r in rows}) == len(rows)
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows))
print(f"{out}: {len(rows)} requests ({sum('history' in r['item'] for r in rows)} with history)")
