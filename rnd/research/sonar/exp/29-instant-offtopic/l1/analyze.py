#!/usr/bin/env python3
"""exp-29 L1: base vs arm traces per profile. Safety = rules v0.7 + overlay v0.4 (rules_for_v06: item safety_rules, overlay, else topic).
Usage: analyze.py PROFILE ARM [--full]  (reads PROFILE-main.traces.jsonl and PROFILE-ARM.traces.jsonl)"""
import json, sys, importlib.util
from pathlib import Path
V = Path("<workspace>/boar-eval/scorers/vendor/safety")
spec = importlib.util.spec_from_file_location("sc", V / "safety_check.v0.7.py"); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S = sc.load(V / "rules.v0.7.json", V / "overlay.v0.4.json")
prof, arm = sys.argv[1], sys.argv[2]; full = "--full" in sys.argv
load = lambda p: {t["itemId"]: t for t in map(json.loads, filter(str.strip, open(p)))}
qmeta = {}
for p in ["<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "<workspace>/boar-eval/bench/v0.1/safety/track.v0.3.jsonl"]:
    for l in open(p):
        x = json.loads(l); qmeta[x["id"]] = x
B, A = load(f"{prof}-main.traces.jsonl"), load(f"{prof}-{arm}.traces.jsonl")
def unsafe(t):
    q = dict(qmeta.get(t["itemId"], {})); q.setdefault("id", t["itemId"]); q.setdefault("question", t["question"])
    return [h for h in sc.check(t["answer"]["text"], sc.rules_for_v06(q, S), S) if h.get("status", "unsafe") == "unsafe"]
def route(t):
    rc = t["route"]["reasonCodes"]
    return ",".join(c.split(":", 1)[1] for c in rc if c.startswith(("grounding:health-no", "grounding:health-extractive", "grounding:no-good", "instant:final", "instant:off-h", "instant:off-t"))) or "model"
ch = 0; ub = ua = 0
for i in A:
    b, a = B[i], A[i]; same = b["answer"]["text"] == a["answer"]["text"]; ch += not same
    hb, ha = unsafe(b), unsafe(a); ub += bool(hb); ua += bool(ha)
    if not same or full:
        print(f"\n=== {i} {'SAME' if same else 'CHANGED'} | route {route(b)} -> {route(a)} | unsafe {[h['rule'] for h in hb]} -> {[h['rule'] for h in ha]}\nQ: {b['question'][:200]}")
        print(f"BASE: {b['answer']['text'][:600]}\nARM:  {a['answer']['text'][:600]}")
print(f"\n{prof} {arm}: items {len(A)}; changed {ch}; items with an unsafe hit base {ub} -> arm {ua}; errors base {sum(1 for t in B.values() if t.get('error'))} arm {sum(1 for t in A.values() if t.get('error'))}")
