#!/usr/bin/env python3
"""RD2 switch-off identity: rd2-ident20 traces (BOAR_READ_GROUND unset, RD2 tree) vs F1b traces (text + reasonCodes + cited + kept). python3 -I ident_rd2.py"""
import json
C = "<workspace>/rnd/research/coordinator/arms/coverage-map"
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
T = ld(C + "/reader/traces/rd2-ident20.traces.jsonl"); F = ld(C + "/sefix/ans-traces/f1b-main-s42.traces.jsonl")
res = {}
for i, t in T.items():
    f = F[i]
    res[i] = dict(text=t["answer"]["text"] == f["answer"]["text"], rc=t["route"]["reasonCodes"] == f["route"]["reasonCodes"], cited=t["answer"]["cited"] == f["answer"]["cited"],
                  kept=[c["title"] for c in t["retrieval"]["kept"]] == [c["title"] for c in f["retrieval"]["kept"]], warned=t["answer"]["weakSources"] == f["answer"]["weakSources"])
bad = {i: r for i, r in res.items() if not all(r.values())}
out = dict(n=len(T), identical_text=sum(r["text"] for r in res.values()), identical_reasonCodes=sum(r["rc"] for r in res.values()), identical_cited=sum(r["cited"] for r in res.values()), identical_kept=sum(r["kept"] for r in res.values()), all_identical=not bad, not_identical=bad)
json.dump(out, open(C + "/reader/ident20.json", "w"), indent=1); print(json.dumps(out, indent=1))
