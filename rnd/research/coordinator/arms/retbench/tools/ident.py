#!/usr/bin/env python3
"""RETBENCH identity: replays/<name> (switches off on rs-RETBENCH) vs the rs-SEFIX reference replays (kept chunk ids + raw titles + reason codes). python3 -I ident.py [name]"""
import json, sys, os
A = "<workspace>/rnd/research/coordinator/arms"; RB = A + "/retbench"; n = sys.argv[1] if len(sys.argv) > 1 else "base"
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
REF = {"main": A + "/coverage-map/sefix/replays/main.F1F2F4.jsonl", "st": A + "/qrewrite/replays/st.base.jsonl", "topics": A + "/topics27/replay/misses.A1.jsonl",
       "f8": A + "/uxmatrix/u5/replays/qform.on.jsonl", "ls": A + "/uxmatrix/u5/replays/longsession.on.jsonl"}
kid = lambda r: [c.get("chunkId") for c in (r.get("keptFull") or [])]
out = {}
for s, f in REF.items():
    if s == "st":
        mine = {}
        for g in ("on-k13", "on-k13+qa-bitcoin-se", "on-k13+qa-ethereum-se"):
            p = f"{RB}/replays/{n}/st.{g}.jsonl"
            if os.path.exists(p): mine.update(rd(p))
    else:
        p = f"{RB}/replays/{n}/{s}.jsonl"; mine = rd(p) if os.path.exists(p) else {}
    if not mine: continue
    ref = rd(f)
    k = [i for i in ref if i in mine and kid(mine[i]) == kid(ref[i])]
    rt = [i for i in ref if i in mine and [c["title"] for c in mine[i].get("raw") or []] == [c["title"] for c in ref[i].get("raw") or []]]
    rc = [i for i in ref if i in mine and mine[i].get("reasonCodes") == ref[i].get("reasonCodes")]
    out[s] = dict(n=len(ref), kept_ids=len(k), raw_titles=len(rt), reason_codes=len(rc), kept_diff=sorted(set(ref) - set(k))[:20])
    print(s, out[s])
json.dump(out, open(f"{RB}/aggregates/identity.{n}.json", "w"), indent=1)
