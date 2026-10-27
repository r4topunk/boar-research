#!/usr/bin/env python3
"""exp-27 L1 read-through: arm traces (+ judgments) vs and-qwen-s44. Usage: compare.py ARM.traces.jsonl [ARM.judgments.jsonl]"""
import json, sys, statistics as st
B = "<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44"
load = lambda p: [json.loads(l) for l in open(p) if l.strip()]
bt = {t["itemId"]: t for t in load(B + ".traces.jsonl")}
at = {t["itemId"]: t for t in load(sys.argv[1])}
def scores(path):
    out = {}
    for j in load(path):
        if j.get("ok") and j.get("mapped"):
            b = j["mapped"]["boar"]; out.setdefault(j["queryId"], []).append((st.mean(b.values()), b["correctness"]))
    return {k: (st.mean(x for x, _ in v), st.mean(c for _, c in v)) for k, v in out.items()}
bs = scores(B + ".judgments.jsonl"); as_ = scores(sys.argv[2]) if len(sys.argv) > 2 else {}
same = changed = 0; deltas = []
for i, t in at.items():
    g = [e for e in t["events"] if e.get("kind") == "rr-gate"]
    drop = [d for e in g for d in e.get("dropped", [])]
    ms = [e["ms"] for e in g]
    if not drop:
        same += t["answer"]["text"] == bt[i]["answer"]["text"]; continue
    changed += 1
    print(f"\n=== {i} | dropped {drop} | gate ms {ms} | scores {[s['score'] for e in g for s in e['scored']]}")
    print(f"Q: {t['question']}")
    print(f"BASE ({bs.get(i)}): {bt[i]['answer']['text'][:700]}")
    print(f"ARM  ({as_.get(i)}): {t['answer']['text'][:700]}")
    if i in as_ and i in bs: deltas.append(as_[i][0] - bs[i][0])
n_unch = len(at) - changed
print(f"\nitems {len(at)}; changed {changed}; unchanged with identical answer {same}/{n_unch}; judged changed {len(deltas)}; mean Δ {st.mean(deltas) if deltas else float('nan'):+.3f}")
