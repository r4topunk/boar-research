#!/usr/bin/env python3
"""COVERAGE-MAP: oracle funnel for the 40 cooking/money self-tests (0 LLM). The fact's home is the item's own source article
(selftest.source.article_id, quotes verified in cm-oracle.json). Per replay: in-pack = the qa pack is in the kit; retrieved = a chunk of that
article in rawFull U wideFull; kept = a chunk of that article in keptFull. Usage: python3 -I cm_stage.py <out json> <label>=<replay jsonl>=<kit ids csv> ..."""
import json, sys
C = "<workspace>/rnd/research/coordinator/arms/coverage-map/"
O = json.load(open(C + "aggregates/cm-oracle.json")); res = {}
for arg in sys.argv[2:]:
    lab, fn, kit = arg.split("="); kit = kit.split(","); rows = {json.loads(l)["id"]: json.loads(l) for l in open(fn) if l.strip()}
    cnt = {}; per = {}
    for i, o in O.items():
        doc = f"pack:local-{o['pack']}:a{o['article_id']}"; r = rows[i]
        kept = any(c.get("docId") == doc for c in r["keptFull"]); ret = any(c.get("docId") == doc for c in r["rawFull"] + r.get("wideFull", []))
        st = "K" if kept else "S3" if ret else "S2" if o["pack"] in kit else "S1"
        per[i] = st; cnt[st] = cnt.get(st, 0) + 1
    res[lab] = dict(counts=cnt, items=per); print(lab, cnt)
json.dump(res, open(sys.argv[1], "w"), indent=1)
