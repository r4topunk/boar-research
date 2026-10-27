#!/usr/bin/env python3
"""QMERGE v0.1 writer (copy of qwrite/tools/gen_qw.py; v0.1 60 public questions; leakage = numbers in rubric/reference text not in the question). QWRITE step 0 writer (criterion 80695f6a...): one 4B search query per self-test question via a running llama-server
(/v1/chat/completions, seed 42, temp 0, max_tokens 24). Writes runs/v01-qw-raw.jsonl (id, question, raw, query, s, gate, reason)
and runs/v01-qmap.json (id -> query, only gate-passing items; failures fall back to the engine's query = absent from the map)."""
import json, re, sys, time, urllib.request
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/qmerge"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8097"
PROMPT = "Rewrite as a 3-8 word search query naming the entity and the fact asked. Output only the query.\nQuestion: {question}"
NUM = re.compile(r"\S*\d\S*")
def nums(s): return {re.sub(r"[^\w.]", "", t).strip(".").lower() for t in NUM.findall(s or "")} - {""}
def clean(t):
    line = next((l for l in (t or "").splitlines() if l.strip()), "").strip()
    line = re.sub(r"^(search\s+)?query\s*:\s*", "", line, flags=re.I).strip().strip("\"'`").strip()
    return re.sub(r"[.?!;:,]+$", "", line).strip()
out = open(f"{A}/runs/v01-qw-raw.jsonl", "w"); qmap = {}; fails = 0
for p in ["v0.1"]:
    for l in open(f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl"):
        if not l.strip(): continue
        it = json.loads(l); q = it["question"]
        body = json.dumps({"messages": [{"role": "user", "content": PROMPT.format(question=q)}], "temperature": 0, "seed": 42,
                           "max_tokens": 24, "stream": False}).encode()
        t0 = time.time()
        r = json.load(urllib.request.urlopen(urllib.request.Request(f"{URL}/v1/chat/completions", body, {"Content-Type": "application/json"}), timeout=120))
        s = time.time() - t0; raw = r["choices"][0]["message"].get("content") or ""; qq = clean(raw)
        gold = " ".join(str(x) for x in (it.get("rubric") or [])) + " " + json.dumps({k: v for k, v in it.items() if k not in ("question", "id", "rubric", "history")})
        leak = sorted((nums(qq) & nums(gold)) - nums(q))
        reason = "empty" if not qq else "words>12" if len(qq.split()) > 12 else f"leak:{','.join(leak)}" if leak else ""
        if reason: fails += 1
        else: qmap[it["id"]] = qq
        out.write(json.dumps({"id": it["id"], "pack": p, "question": q, "raw": raw, "query": qq, "words": len(qq.split()), "s": round(s, 3),
                              "gate": not reason, "reason": reason, "usage": r.get("usage")}) + "\n"); out.flush()
json.dump(qmap, open(f"{A}/runs/v01-qmap.json", "w"), indent=1)
print(json.dumps({"n": sum(1 for _ in open(f"{A}/runs/v01-qw-raw.jsonl")), "pass": len(qmap), "fail": fails}))
