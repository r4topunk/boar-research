#!/usr/bin/env python3
"""STYLE-SEFIX D arm requests (0 LLM): sefix124-main-s42 requests with personalityId detailed. python3 -I tools/mk_req.py"""
import json
A = "<workspace>/rnd/research/coordinator/arms"; out = []
for l in open(A + "/coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl"):
    r = json.loads(l); assert r["seed"] == 42 and r["config"]["arm"].endswith("+sefix124") and "personalityId" not in r["config"]["settings"]
    r["runId"] = "style-sefix-D-s42"; r["config"]["arm"] += "+detailed"; r["config"]["settings"]["personalityId"] = "detailed"; out.append(json.dumps(r, ensure_ascii=False))
open(A + "/style-sefix/req/style-sefix-D-s42.requests.jsonl", "w").write("\n".join(out) + "\n"); print(len(out))
