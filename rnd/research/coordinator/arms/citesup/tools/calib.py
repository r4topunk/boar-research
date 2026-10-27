#!/usr/bin/env python3
"""CITESUP calibration (criterion step 3-4). Usage: python3 -I calib.py <sidecar.citesup.jsonl> [...] -- <traces.jsonl:control pool.json> [...]
Prints the decision count, the cos distribution, tau = max cos + 0.001 rounded up to 3 decimals (fallback 0.80 if none), and the identity
check traces text == control text per id (log mode must be inert)."""
import json, math, sys
a = sys.argv[1:]; k = a.index("--"); sides, pairs = a[:k], a[k + 1:]
cos, errs, checks = [], 0, 0
for f in sides:
    for l in open(f):
        r = json.loads(l)
        if r.get("kind") != "check": continue
        checks += 1
        for d in r["decisions"]:
            if d.get("cos") is None: errs += 1
            else: cos.append(d["cos"])
cos.sort()
q = lambda p: cos[min(len(cos) - 1, int(p * len(cos)))] if cos else None
print(f"check records {checks}, decisions with cos {len(cos)}, errors {errs}")
if cos: print("cos min/p25/p50/p75/p90/max", [round(x, 4) for x in (cos[0], q(.25), q(.5), q(.75), q(.9), cos[-1])])
tau = math.ceil((cos[-1] + 0.001) * 1000) / 1000 if cos else 0.80
print(f"TAU {tau:.3f}{'' if cos else ' (FALLBACK: no 1.7B decision logged)'}")
bad = 0; resc = 0
for f in sides:
    for l in open(f):
        r = json.loads(l)
        if r.get("kind") == "check": resc += sum(bool(d.get("rescued")) for d in r["decisions"])
checked_items = {json.loads(l)["item"] for f in sides for l in open(f) if json.loads(l).get("kind") == "check"}
print(f"rescued in log mode: {resc} (must be 0)"); bad += resc
for p in pairs:  # traces:control pool.json:control traces[,more]
    tr, cj, ctr = p.split(":"); ctl = json.load(open(cj))["items"]
    R = {}
    for f in ctr.split(","):
        for l in open(f): t = json.loads(l); R[t["itemId"]] = json.dumps(t["retrieval"], sort_keys=True)
    n = drift = 0
    for l in open(tr):
        t = json.loads(l); n += 1; i = t["itemId"]
        if ctl[i]["text"] != t["answer"]["text"]:
            drift += 1; ok = R.get(i) == json.dumps(t["retrieval"], sort_keys=True) and i not in checked_items
            print(("drift ok " if ok else "DIFF NOT EXPLAINED ") + i); bad += not ok
    print(f"identity {tr.split('/')[-1]}: {n} rows, {drift} decode-drift rows")
print("LOG MODE OK (decision-level, amendment 2)" if not bad else f"LOG MODE FAIL {bad}")
