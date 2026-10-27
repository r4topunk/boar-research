#!/usr/bin/env python3
"""Parity of a DG run vs the MINI-BASELINE K1 traces (0 LLM). Usage: python3 -I parity_dg.py <run traces.jsonl>
Per item: answer.text byte-identical, route.reasonCodes identical, kept titles identical, promptTokens/outputTokens. Exit 1 on any answer mismatch."""
import json, sys
LP = "<workspace>/rnd/research/coordinator/arms/litepacks/traces/mini"
base = {}
for s in ("cm", "v01"):
    for l in open(f"{LP}/lp-K1-{s}-s42.mini.traces.jsonl"):
        t = json.loads(l); base[t["itemId"]] = t
bad = 0
for l in open(sys.argv[1]):
    t = json.loads(l); b = base[t["itemId"]]
    same = t["answer"]["text"] == b["answer"]["text"]; bad += not same
    print(t["itemId"], "answer", "IDENTICAL" if same else "DIFF", "| reasonCodes", t["route"]["reasonCodes"] == b["route"]["reasonCodes"],
          "| kept", [k["title"] for k in t["retrieval"]["kept"]] == [k["title"] for k in b["retrieval"]["kept"]],
          "| tokens", (t["timing"]["promptTokens"], t["timing"]["outputTokens"]), "vs", (b["timing"]["promptTokens"], b["timing"]["outputTokens"]),
          "| totalMs", t["timing"]["totalMs"], "vs", b["timing"]["totalMs"])
print("answers identical:", "ALL" if not bad else f"{bad} differ")
sys.exit(1 if bad else 0)
