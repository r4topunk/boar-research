#!/usr/bin/env python3
"""GEMMA4-E2B run sanity + length/wall vs the control traces (0 LLM). Usage: python3 -I sanity.py <cand traces.jsonl> <control traces.jsonl>[,<more>]"""
import json, sys
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
C = rd(sys.argv[1]); K = {}
for f in sys.argv[2].split(","): K.update(rd(f))
ids = [i for i in C if i in K]
bad = dict(errors=sum(bool(C[i].get("error")) for i in C), genfail=sum("generation_failed" in json.dumps(C[i]) for i in C),
           sha=sum(C[i]["runtime"]["versions"].get("model.sha256") != "740185b21d22ceb83a11c3aa62ad5842ef32c70f6096d756bbee85a1e4ec34b8" for i in C),
           leak=sum(any(t in C[i]["answer"]["text"] for t in ("<|channel>", "<channel|>", "<|think|>")) for i in C),
           reasoning=sum((C[i]["timing"].get("reasoningTokens") or 0) > 0 for i in C))
live = [i for i in ids if (K[i]["timing"].get("outputTokens") or 0) > 0]
m = lambda X, k, xs: sum(X[i]["timing"].get(k) or 0 for i in xs) / len(xs)
print(json.dumps(dict(n=len(C), matched=len(ids), **bad, live=len(live), out_tok_cand=round(m(C, "outputTokens", live), 1), out_tok_ctl=round(m(K, "outputTokens", live), 1),
      totalMs_cand=round(m(C, "totalMs", ids)), totalMs_ctl=round(m(K, "totalMs", ids)), wall_ratio=round(m(C, "totalMs", ids) / m(K, "totalMs", ids), 3),
      wall_ratio_live=round(m(C, "totalMs", live) / m(K, "totalMs", live), 3))))
