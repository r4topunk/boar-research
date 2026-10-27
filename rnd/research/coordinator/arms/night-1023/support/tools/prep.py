#!/usr/bin/env python3
"""SUPPORT prep (0 LLM). python3 -I prep.py <out prep.json (outside the repo: contains pack text)>
Builds one unit per (item, ordered kept-chunk bodies); arm (F1F2F4 replay) and control (B0 replay) share a unit when the kept lists are identical.
Gold = reference answer (v0.1 refs.jsonl / selftest refs.jsonl) + rubric (questions.public.jsonl / questions.jsonl)."""
import json, sys, glob, hashlib
A = "<workspace>/rnd/research/coordinator/arms"; BE = "<workspace>/boar-eval/bench"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(A + "/lp-screens/main-97.ids").read().split()
refs = {r["id"]: r for r in rd(BE + "/v0.1/refs/refs.jsonl")}; qs = {r["id"]: r for r in rd(BE + "/v0.1/questions.public.jsonl")}
for d in glob.glob(BE + "/selftest/*/"):
    for r in rd(d + "refs/refs.jsonl"): refs[r["id"]] = r
    for r in rd(d + "questions.jsonl"): qs[r["id"]] = r
REP = {"X": {r["id"]: r for r in rd(A + "/coverage-map/sefix/replays/main.F1F2F4.jsonl")}, "C": {r["id"]: r for r in rd(A + "/retrieve-sweep/replay/B0.main.jsonl")}}
units = {}; map_ = {}
for i in ids:
    for arm in ("X", "C"):
        kept = REP[arm][i]["keptFull"]; bodies = [c["body"] for c in kept]
        k = hashlib.sha256(json.dumps([i, bodies], ensure_ascii=False).encode()).hexdigest()[:16]
        map_[f"{arm}:{i}"] = dict(unit=k if bodies else None, n=len(bodies), titles=[c["title"] for c in kept])
        if bodies and k not in units:
            fmt = lambda bs: "\n\n".join(f"[{j+1}] {c['title']}\n{c['body']}" for j, c in enumerate(bs))
            units[k] = dict(key=k, id=i, question=qs[i]["question"], gold=refs[i]["answer"], rubric=qs[i]["rubric"], n=len(kept), chunks=fmt(kept), chunks_rev=fmt(list(reversed(kept))))
json.dump(dict(units=list(units.values()), map=map_), open(sys.argv[1], "w"), ensure_ascii=False)
print("units", len(units), "arm/ctl items with 0 kept:", {a: sum(1 for i in ids if not map_[f'{a}:{i}']['unit']) for a in ('X', 'C')}, "shared units", sum(1 for i in ids if map_[f'X:{i}']['unit'] and map_[f'X:{i}']['unit'] == map_[f'C:{i}']['unit']))
