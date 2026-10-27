#!/usr/bin/env python3
"""F3-SAFETY requests: 65 GEMMA-SAFETY probes + ARM-G config block (SEFIX-ALL arm id). python3 -I mk_req_f3.py"""
import json
A = "<workspace>/rnd/research/coordinator/arms"
cfg = json.loads(open(A + "/coverage-map/sefix/ans-req/sefixall-main-s42.requests.jsonl").readline())["config"]
P = [json.loads(l) for l in open(A + "/gemma-safety/runs/gs-probes65-1p7b.requests.jsonl")]
for arm in ("on", "off"):
    out = []
    for p in P:
        r = {"protocol": "1.0.0", "runId": f"f3safety-{arm}-s42", "item": p["item"], "config": cfg, "seed": 42}
        out.append(json.dumps(r))
    open(A + f"/coverage-map/sefix/f3-safety/req/f3safety-{arm}-s42.requests.jsonl", "w").write("\n".join(out) + "\n")
print(len(P), cfg["arm"], cfg["modelId"], len(cfg["kit"]))
