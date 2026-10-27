#!/usr/bin/env python3
"""ENGINE-RC v0.4 turn-k requests (runs on the mini, 0 LLM): from turns.template.jsonl rows with prevTurn == k-1 and the traces of turns 1..k-1,
history as ChatScreen sends it (validation-1024 v3_stage2.py rule: prior messages with text, last VERBATIM_MESSAGE_COUNT 6, {role, text}, assistant text
= trace answer.text exactly as the user saw it; an empty earlier answer leaves only the user turn). Never prints item text.
usage: python3 -I v04_stage.py <seed dir> <k>   -> <seed dir>/req/t<k>.requests.jsonl"""
import json, sys, os
D, K = sys.argv[1], int(sys.argv[2])
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
Q, ANS = {}, {}
for j in range(1, K):
    for r in rd(f"{D}/req/t{j}.requests.jsonl"): Q[(r["item"]["id"], j)] = r["item"]["question"]
    for t in rd(f"{D}/out/t{j}/traces.jsonl"): ANS[(t["itemId"], j)] = ((t.get("answer") or {}).get("text") or "")
out = []
for r in rd(f"{D}/turns.template.jsonl"):
    it = r["item"]
    if it["prevTurn"] != K - 1: continue
    i = it["id"]; turns = []
    for j in range(1, K):
        turns.append({"role": "user", "text": Q[(i, j)]})
        if ANS.get((i, j)): turns.append({"role": "assistant", "text": ANS[(i, j)]})
    it = {k: v for k, v in it.items() if k != "prevTurn"}; it["history"] = {"turns": turns[-6:]}
    out.append(json.dumps(dict(r, item=it), ensure_ascii=False))
p = f"{D}/req/t{K}.requests.jsonl"; open(p, "w").write("\n".join(out) + ("\n" if out else ""))
print(f"t{K}: {len(out)} requests")
