#!/usr/bin/env python3
"""PACKPROOF host identity check (0 LLM): kept lists (title+source, in order) of gen/ident5 vs the mini sefix124-main-s42 traces."""
import json
P = "<workspace>/rnd/research/coordinator/arms/packproof"; M = "<workspace>/rnd/research/coordinator/arms/coverage-map/sefix/ans-traces/sefix124-main-s42.traces.jsonl"
kl = lambda t: [(k["title"], k["source"]) for k in t["retrieval"]["kept"]]
mini = {t["itemId"]: t for t in map(json.loads, open(M))}
n = ok = 0; rows = []
import sys; D = sys.argv[1] if len(sys.argv) > 1 else "ident5"
for t in map(json.loads, open(P + f"/gen/{D}/traces.jsonl")):
    m = mini[t["itemId"]]; same = kl(t) == kl(m); n += 1; ok += same
    rows.append(dict(id=t["itemId"], kept_same=same, n_kept=len(kl(t)), text_same=t["answer"]["text"] == m["answer"]["text"], host=t["runtime"]["host"], mini_host=m["runtime"]["host"]))
out = dict(pass_=ok == n == 5, kept_identical=f"{ok}/{n}", rows=rows); json.dump(out, open(P + f"/aggregates/{D}.json", "w"), indent=1); print(json.dumps(out, indent=1))
