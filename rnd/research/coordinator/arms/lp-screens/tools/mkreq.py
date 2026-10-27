#!/usr/bin/env python3
"""LP-SCREENS requests (0 LLM). Usage: python3 -I mkreq.py <K0|K1> <ids file> <runId> <config.arm> <out requests.jsonl>
Rows are the LITEPACKS requests (arms/litepacks/runs/req/lp-<K>-{v01,cm}-s42.requests.jsonl: Qwen3-1.7B, seed 42, quickFirst + packHeadPass a2 +
packDense2 append-budget, the pack set's sha-pinned kit) for the given ids, in ids-file order, with runId and config.arm replaced (the adapter checks
config.arm against the tree's ARM file; nothing else reads it). Everything else is byte-for-byte the LITEPACKS request."""
import json, sys
K, idf, run, arm, out = sys.argv[1:6]
LP = "<workspace>/rnd/research/coordinator/arms/litepacks/runs/req"
by = {}
for s in ("v01", "cm"):
    for l in open(f"{LP}/lp-{K}-{s}-s42.requests.jsonl"):
        r = json.loads(l); by[r["item"]["id"]] = r
ids = [x for x in open(idf).read().split() if x]
miss = [i for i in ids if i not in by]
if miss: sys.exit(f"ids not in LITEPACKS {K} requests: {miss}")
with open(out, "w") as f:
    for i in ids:
        r = json.loads(json.dumps(by[i])); r["runId"] = run; r["config"]["arm"] = arm; f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(ids)} requests -> {out}")
