#!/usr/bin/env python3
"""cmp_run.py <runs dir>: G2 identity (v0.1 EN s44, ctl vs arm) and the 192 dev chat messages: every routing/reason-code change."""
import json, sys
D = sys.argv[1]
ld = lambda n: {t["itemId"]: t for t in map(json.loads, open(f"{D}/{n}.traces.jsonl"))}
def pas(t):
    r = t.get("retrieval") or {}
    return [[(x.get("title"), x.get("section"), x.get("source")) for x in (r.get(k) or [])] for k in ("raw", "kept", "dropped")]
def codes(t): return [c for c in t["route"]["reasonCodes"] if not c.startswith("route-gate:")]
c, a = ld("ctl-v01-s44"), ld("arm-v01-s44")
txt = sum(c[i]["answer"]["text"] != a[i]["answer"]["text"] for i in c)
tier = sum(c[i]["route"]["tier"] != a[i]["route"]["tier"] for i in c)
ps = sum(pas(c[i]) != pas(a[i]) for i in c); cd = sum(codes(c[i]) != codes(a[i]) for i in c)
print(f"G2 v0.1 EN s44: items {len(c)}/{len(a)}; text identical {len(c)-txt}/{len(c)}, tier identical {len(c)-tier}/{len(c)}, passages identical {len(c)-ps}/{len(c)}, reason codes identical (excl route-gate) {len(c)-cd}/{len(c)}; errors ctl {sum(bool(t['error']) for t in c.values())} arm {sum(bool(t['error']) for t in a.values())}")
for i in c:
    if codes(c[i]) != codes(a[i]) or c[i]["answer"]["text"] != a[i]["answer"]["text"]: print("  DIFF", i, codes(c[i]), codes(a[i]))
c, a = ld("ctl-chat"), ld("arm-chat")
print(f"\nchat 192 (ctl {len(c)}, arm {len(a)}): ")
nr = 0; ntxt = 0; ntier = 0
for i in c:
    x, y = c[i], a[i]
    rc = codes(x) != codes(y); tx = x["answer"]["text"] != y["answer"]["text"]; ti = x["route"]["tier"] != y["route"]["tier"]
    nr += rc; ntxt += tx; ntier += ti
    if rc or ti: print(f"  ROUTING {i}: tier {x['route']['tier']}->{y['route']['tier']} codes -{[k for k in codes(x) if k not in codes(y)]} +{[k for k in codes(y) if k not in codes(x)]} text_changed={tx}")
print(f"reason-code diffs {nr}, tier diffs {ntier}, answer-text diffs (incl. generation nondeterminism) {ntxt}")
nonrt = [i for i in c if codes(c[i]) == codes(a[i]) and c[i]["answer"]["text"] != a[i]["answer"]["text"]]
print("text differs with identical routing:", nonrt)
