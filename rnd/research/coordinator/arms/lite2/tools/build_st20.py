#!/usr/bin/env python3
"""LITE2: from the 9 packs' SELFTEST-SCORES files build (1) bench-st20/ = merged judge bench (questions + refs lines copied verbatim, the 20 ids),
(2) runs/c4b-st20-s42.{traces,judgments.haiku55-low,requests}.jsonl = the 4B with-pack control (cut 7 + claim kit + pack, MacBook, 2026-10-13) filtered to the 20 ids,
(3) runs/{l,t2}-st20-s42.requests.jsonl = the same requests with only modelId (and runId) changed."""
import json, hashlib, os, sys
P = "<workspace>/rnd/research/coordinator/arms/packs/selftest-runs"; B = "<workspace>/boar-eval/bench/selftest"
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = [l.strip() for l in open(f"{H}/selftest20.ids") if l.strip()]; want = set(ids)
packs = sorted({i[3:].rsplit("-", 1)[0] for i in ids})
rd = lambda p: [l for l in open(p) if l.strip()]
q, r, tr, jd, rq = [], [], [], [], []
for p in packs:
    q += [l for l in rd(f"{B}/{p}/questions.jsonl") if json.loads(l)["id"] in want]
    r += [l for l in rd(f"{B}/{p}/refs/refs.jsonl") if json.loads(l)["id"] in want]
    tr += [l for l in rd(f"{P}/st-{p}-cut7-s42.traces.jsonl") if json.loads(l)["itemId"] in want]
    jd += [l for l in rd(f"{P}/st-{p}-cut7-s42.judgments.jsonl") if json.loads(l)["queryId"] in want]
    rq += [l for l in rd(f"{P}/st-{p}-cut7-s42.requests.jsonl") if json.loads(l)["item"]["id"] in want]
assert len(q) == len(r) == len(tr) == len(rq) == 20, (len(q), len(r), len(tr), len(rq))
assert {json.loads(l)["judgeModel"] for l in jd} == {"claude-haiku-5-5"} and sum(json.loads(l)["ok"] in (True, "True") for l in jd) == 40, len(jd)
bd = f"{H}/bench-st20"; os.makedirs(f"{bd}/refs", exist_ok=True)
open(f"{bd}/questions.jsonl", "w").writelines(q); open(f"{bd}/refs/refs.jsonl", "w").writelines(r)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump({"bench": "selftest-lite2-st20", "questions": "questions.jsonl", "refs": "refs/refs.jsonl",
           "_note": "LITE2: the 20 selftest20.ids items of the 9 SELFTEST-SCORES packs, lines copied verbatim from boar-eval/bench/selftest/<pack>/; dev only"}, open(f"{bd}/bench.json", "w"), indent=1)
json.dump({"bench": "selftest-lite2-st20", "frozen": True, "n_items": 20, "n_ok": 20, "questions_sha256": sha(f"{bd}/questions.jsonl"), "jsonl_sha256": sha(f"{bd}/refs/refs.jsonl")}, open(f"{bd}/refs/MANIFEST.json", "w"), indent=1)
R = f"{H}/runs"
open(f"{R}/c4b-st20-s42.traces.jsonl", "w").writelines(tr); open(f"{R}/c4b-st20-s42.judgments.haiku55-low.jsonl", "w").writelines(jd); open(f"{R}/c4b-st20-s42.requests.jsonl", "w").writelines(rq)
for run, mid in (("l-st20-s42", "qwen3-1.7b-q4km"), ("t2-st20-s42", "bonsai2-2b-ptq1_0")):
    out = []
    for l in rq:
        x = json.loads(l); assert x["config"]["modelId"] == "qwen3-4b-instruct-2507-q4km" and x["config"]["arm"] == "cut7"
        x["runId"] = run; x["config"]["modelId"] = mid; out.append(json.dumps(x, separators=(",", ":"), ensure_ascii=False) + "\n")
    open(f"{R}/{run}.requests.jsonl", "w").writelines(out)
for f in ["bench-st20/questions.jsonl", "bench-st20/refs/refs.jsonl", "runs/c4b-st20-s42.traces.jsonl", "runs/c4b-st20-s42.judgments.haiku55-low.jsonl", "runs/l-st20-s42.requests.jsonl", "runs/t2-st20-s42.requests.jsonl"]:
    print(sha(f"{H}/{f}")[:16], f)
print("packs", packs, "kits", sorted({json.dumps([k["id"] for k in json.loads(l)["config"]["kit"]]) for l in rq})[:3], "...")
