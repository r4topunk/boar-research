#!/usr/bin/env python3
"""SEARCHPORT identity (0 LLM): kept ids (keptFull chunkIds in order) of replays/<a> vs replays/<b> for MAIN 97, ST 180, probes 65; also raw ids.
usage: ident.py <a> <b>"""
import json, sys
SP = "<workspace>/rnd/research/coordinator/arms/searchport/replays/"
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
a, b = sys.argv[1:3]
for label, files in (("MAIN", ["main"]), ("ST", ["st.on-k13", "st.on-k13+qa-bitcoin-se", "st.on-k13+qa-ethereum-se"]), ("probes", ["probes"])):
    A, B = {}, {}
    for f in files:
        try: A.update(rd(f"{SP}{a}/{f}.jsonl")); B.update(rd(f"{SP}{b}/{f}.jsonl"))
        except FileNotFoundError: pass
    if not A or not B: print(label, "missing"); continue
    ids = sorted(set(A) & set(B))
    k = sum([c["chunkId"] for c in A[i]["keptFull"]] == [c["chunkId"] for c in B[i]["keptFull"]] for i in ids)
    r = sum([c["chunkId"] for c in A[i]["raw"]] == [c["chunkId"] for c in B[i]["raw"]] for i in ids)
    pr = sum(A[i].get("prompt") == B[i].get("prompt") for i in ids)
    print(f"{label}: kept identical {k}/{len(ids)}, raw identical {r}/{len(ids)}, prompt identical {pr}/{len(ids)}")
