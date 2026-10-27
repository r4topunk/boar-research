#!/usr/bin/env python3
"""NULLCAL pool requests (0 LLM): like lp-screens/tools/mkreq.py but also reads the LITEPACKS st (180 self-test) requests.
Usage: python3 -I mkreq_pool.py <K0|K1> <ids file> <runId> <config.arm> <out requests.jsonl>. Rows are byte-for-byte the LITEPACKS requests except runId and config.arm."""
import json, sys
K, idf, run, arm, out = sys.argv[1:6]
LP = "<workspace>/rnd/research/coordinator/arms/litepacks/runs/req"
by = {}
for s in ("v01", "cm", "st"):
    for l in open(f"{LP}/lp-{K}-{s}-s42.requests.jsonl"):
        r = json.loads(l); by[r["item"]["id"]] = r
ids = [x for x in open(idf).read().split() if x]
miss = [i for i in ids if i not in by]
if miss: sys.exit(f"ids not in LITEPACKS {K} requests: {miss}")
with open(out, "w") as f:
    for i in ids:
        r = json.loads(json.dumps(by[i])); r["runId"] = run; r["config"]["arm"] = arm; f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(ids)} requests -> {out}")
