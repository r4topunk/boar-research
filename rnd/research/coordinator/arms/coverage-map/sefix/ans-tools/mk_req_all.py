#!/usr/bin/env python3
"""SEFIX-ALL answer screen requests = ARM-G requests (compose/screen/req) with arm id cut7-headpass-x2+litepacks+sefixall; settings unchanged (packHeadPass a2, packDense2 append-budget), v2 kit shas unchanged. python3 -I mk_req_all.py"""
import json
A = "<workspace>/rnd/research/coordinator/arms/coverage-map"
out = []
for l in open(A + "/compose/screen/req/cmp-G-K10-main-s42.requests.jsonl"):
    r = json.loads(l); r["runId"] = "sefixall-main-s42"; r["config"]["arm"] = "cut7-headpass-x2+litepacks+sefixall"; out.append(json.dumps(r))
open(A + "/sefix/ans-req/sefixall-main-s42.requests.jsonl", "w").write("\n".join(out) + "\n")
print(len(out), json.loads(out[0])["config"]["settings"])
