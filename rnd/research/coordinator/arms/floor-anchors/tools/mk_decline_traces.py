#!/usr/bin/env python3
"""FLOOR-ANCHORS decline traces (0 LLM). Usage: python3 -I mk_decline_traces.py
Writes traces/fa-decline-{a,b,c}.traces.jsonl in the judge's trace format (protocol 1.0.0 fields judge.mjs reads: runId, itemId,
question, engine.commit/arm, answer.text; answer.declined=false so no z override applies anywhere) for the 30 ids in decline-30.ids.
(a) and (b) are fixed strings; (c) = texts/c-fluent-template.txt with {question} replaced by the item's question text (no other edit)."""
import json, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
ids = open(f"{H}/decline-30.ids").read().split()
T = {"a": open(f"{H}/texts/a-bare-refusal.txt").read().strip(), "b": open(f"{H}/texts/b-hedged.txt").read().strip(),
     "c": open(f"{H}/texts/c-fluent-template.txt").read().strip()}
os.makedirs(f"{H}/traces", exist_ok=True)
for v, t in T.items():
    with open(f"{H}/traces/fa-decline-{v}.traces.jsonl", "w") as f:
        for i in ids:
            text = t.replace("{question}", Q[i]["question"]) if v == "c" else t
            f.write(json.dumps({"protocol": "1.0.0", "runId": f"fa-decline-{v}", "itemId": i, "question": Q[i]["question"],
                                "engine": {"commit": "none", "arm": f"floor-anchors-decline-{v}", "dirty": False},
                                "runtime": {"adapter": "none (fixed text, FLOOR-ANCHORS)", "model": "none"},
                                "answer": {"text": text, "cited": [], "shown": [], "declined": False, "warnings": []}}, ensure_ascii=False) + "\n")
    print(v, len(ids))
