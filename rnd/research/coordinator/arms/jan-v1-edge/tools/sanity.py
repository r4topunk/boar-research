#!/usr/bin/env python3
"""JAN-V1-EDGE run sanity + length/wall vs the control traces (0 LLM). Usage: python3 -I sanity.py <cand traces.jsonl> <control traces.jsonl>[,<more>]"""
import json, sys
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
C = rd(sys.argv[1]); K = {}
for f in sys.argv[2].split(","): K.update(rd(f))
ids = [i for i in C if i in K]
bad = dict(errors=sum(bool(C[i].get("error")) for i in C), genfail=sum("generation_failed" in json.dumps(C[i]) for i in C),
           sha=sum(C[i]["runtime"]["versions"].get("model.sha256") != "bdde4346e5e0ecc8b679dd6ca43d4e66d85c50227cda5287428d65489fad0c59" for i in C),
           leak=sum(any(t in C[i]["answer"]["text"] for t in ("<think>", "</think>")) for i in C),
           reasoning=sum((C[i]["timing"].get("reasoningTokens") or 0) > 0 for i in C))
live = [i for i in ids if (K[i]["timing"].get("outputTokens") or 0) > 0]
m = lambda X, k, xs: sum(X[i]["timing"].get(k) or 0 for i in xs) / len(xs)
print(json.dumps(dict(n=len(C), matched=len(ids), **bad, live=len(live), out_tok_cand=round(m(C, "outputTokens", live), 1), out_tok_ctl=round(m(K, "outputTokens", live), 1),
      totalMs_cand=round(m(C, "totalMs", ids)), totalMs_ctl=round(m(K, "totalMs", ids)), wall_ratio=round(m(C, "totalMs", ids) / m(K, "totalMs", ids), 3),
      wall_ratio_live=round(m(C, "totalMs", live) / m(K, "totalMs", live), 3))))
