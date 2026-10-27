#!/usr/bin/env python3
"""UXMATRIX helper (0 LLM): for every v0.1 keyed item delivered at chunk level under SEFIX-124 (replay sefix/replays/main.F1F2F4.jsonl),
the packs of the kept chunks whose body alone gives share_v01 >= 0.5 (the CHUNKLEVEL rule). Usage: python3 -I deliv_packs.py <out json>"""
import json, sys, re, os, glob, unicodedata, importlib.util
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; CM = A + "coverage-map/"; R = A + "retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location")); b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
exec("\n".join(src[a:b]))
CL = json.load(open(CM + "sefix/chunklevel-124.json"))["per_item"]["sefix F1F2F4"]
rows = {r["id"]: r for r in rd(CM + "sefix/replays/main.F1F2F4.jsonl")}
out = {}
for i, f in CL.items():
    if not f or f["set"] != "v0.1" or not f["chunk"]: continue
    hits = []
    for c in rows[i]["keptFull"]:
        s = share_v01(QS[i], [c["body"]]) or 0.0
        if s >= 0.5: hits.append(dict(pack=c["chunkId"].split(":")[1].replace("local-", ""), title=c["title"], share=round(s, 3)))
    out[i] = dict(packs=sorted({h["pack"] for h in hits}), hits=hits)
json.dump(out, open(sys.argv[1], "w"), indent=1); print(len(out)); [print(k, v["packs"]) for k, v in out.items()]
