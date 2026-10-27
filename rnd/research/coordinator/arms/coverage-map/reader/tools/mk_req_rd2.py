#!/usr/bin/env python3
"""RD2 requests = F1b requests (sefix/ans-req) with runId and arm id changed. usage: mk_req_rd2.py RUNID [IDFILE]  -> reader/req/RUNID.requests.jsonl"""
import json, sys
C = "<workspace>/rnd/research/coordinator/arms/coverage-map"
run = sys.argv[1]; keep = set(open(sys.argv[2]).read().split()) if len(sys.argv) > 2 else None
out = []
for l in open(C + "/sefix/ans-req/f1b-main-s42.requests.jsonl"):
    r = json.loads(l)
    if keep is not None and r["item"]["id"] not in keep: continue
    r["runId"] = run; r["config"]["arm"] = "cut7-headpass-x2+litepacks+f1b+rd2"; out.append(json.dumps(r))
open(f"{C}/reader/req/{run}.requests.jsonl", "w").write("\n".join(out) + "\n"); print(run, len(out))
