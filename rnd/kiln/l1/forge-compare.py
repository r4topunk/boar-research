#!/usr/bin/env python3
"""Forge step 0 identity: base vs arm-off and base vs arm-on on 5 fields (pre-answer sources with passage text,
retrieval.raw, retrieval.kept, route, answer text) + sqlite calls/question median (proof the flags reached the run)."""
import json, statistics, sys
D = sys.argv[1]
L = lambda n: {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{D}/{n}.traces.jsonl")}
def pre(t):  # the sources events (passage text kept by --event-source-text) emitted before the first token
    out = []
    for e in t["events"]:
        if e["type"] == "token": break
        if e["type"] == "sources": out.append(json.dumps(e.get("sources"), sort_keys=True))
    return out
F = {"pre-answer sources": pre, "retrieval.raw": lambda t: t["retrieval"]["raw"], "retrieval.kept": lambda t: t["retrieval"]["kept"],
     "route": lambda t: t["route"], "answer text": lambda t: t["answer"]["text"]}
def sql(t): return next((e["total"] for e in t["events"] if e.get("kind") == "sql-calls"), None)
base = L("base"); print(f"base: {len(base)} items, errors {sum(1 for t in base.values() if t.get('error'))}, sqlite calls/q median {statistics.median([sql(t) for t in base.values() if sql(t) is not None])}")
for n in ["arm-off", "arm-on"]:
    arm = L(n); ids = [i for i in base if i in arm]
    print(f"{n}: {len(arm)} items, errors {sum(1 for t in arm.values() if t.get('error'))}, sqlite calls/q median {statistics.median([sql(t) for t in arm.values() if sql(t) is not None])}")
    for k, f in F.items():
        diff = [i for i in ids if f(base[i]) != f(arm[i])]
        print(f"  {k}: {len(ids) - len(diff)}/{len(ids)} identical" + (f"  DIFF: {' '.join(diff)}" if diff else ""))
