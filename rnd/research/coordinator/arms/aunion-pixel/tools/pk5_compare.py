#!/usr/bin/env python3
"""PK-5 identity: compare two replay-retrieval outputs (kept sources ordered; raw (title, section) ordered). 0 LLM.
usage: pk5_compare.py <A.jsonl> <B.jsonl> [--list]"""
import json, sys, statistics as st
a = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[1])}
b = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[2])}
ids = [i for i in a if i in b]
kept = raw = 0; diffs = []
for i in ids:
    x, y = a[i], b[i]
    ks = (x.get("sources") or []) == (y.get("sources") or [])
    rs = [(r["title"], r.get("section")) for r in x.get("raw") or []] == [(r["title"], r.get("section")) for r in y.get("raw") or []]
    kept += ks; raw += rs
    if not ks: diffs.append((i, x.get("sources"), y.get("sources")))
ms = lambda d: st.median([r["ms"] for r in d.values() if r.get("raw")])
print(json.dumps({"n": len(ids), "kept_identical": kept, "kept_pct": round(100 * kept / len(ids), 1), "raw_identical": raw,
                  "ms_p50_A": ms(a), "ms_p50_B": ms(b)}))
if "--list" in sys.argv:
    for i, s1, s2 in diffs: print(f"- {i}: A={s1} | B={s2}")
