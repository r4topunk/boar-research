#!/usr/bin/env python3
"""RU requests (0 LLM). Usage: python3 -I mkreq.py <out requests.jsonl>
= the LITEPACKS K3 requests (arms/litepacks/runs/req/lp-K3-{v01,cm,st}-s42.requests.jsonl, unchanged bytes except runId) for
MAIN 97 (arms/lp-screens/main-97.ids) + the 80 candidate-pack self-tests (st-boar-*), runId ru-K3-dump-s42."""
import json, sys
A = "<workspace>/rnd/research/coordinator/arms"
req = {}
for s in ("v01", "cm", "st"):
    for l in open(f"{A}/litepacks/runs/req/lp-K3-{s}-s42.requests.jsonl"):
        r = json.loads(l); req[r["item"]["id"]] = r
main = [l.strip() for l in open(f"{A}/lp-screens/main-97.ids") if l.strip()]
cand = sorted(i for i in req if i.startswith("st-boar-"))
assert len(main) == 97 and len(cand) == 80
with open(sys.argv[1], "w") as f:
    for i in main + cand:
        r = dict(req[i]); r["runId"] = "ru-K3-dump-s42"; f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(main) + len(cand))
