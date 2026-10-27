#!/usr/bin/env python3
"""DILUTION-K inputs (0 LLM): request files k1/k2/k3 = the ORACLE-REAL requests with runId/arm renamed; the oracle file is ORACLE-REAL's unchanged.
Usage: build_inputs.py"""
import json
D = "<workspace>/rnd/research/coordinator/arms/dilution-k/"; OR = D + "../oracle-real/"
for k in (1, 2, 3):
    run = f"dilution-k{k}-K3-v01gold-s42"
    with open(D + f"runs/req/{run}.requests.jsonl", "w") as w:
        for l in open(OR + "runs/req/oracle-K3-v01gold-s42.requests.jsonl"):
            r = json.loads(l); r["runId"] = run; r["config"]["arm"] = f"cut7-headpass-x2+litepacks+oracle-real+k{k}"; w.write(json.dumps(r) + "\n")
print("ok")
