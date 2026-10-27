#!/usr/bin/env python3
"""cmp.py <cut3.traces> <cut4.traces> [--questions requests]: items whose tier, reason codes or answer text differ (stub replay)."""
import json, sys
ld = lambda p: {t["itemId"]: t for t in map(json.loads, open(p))}
a, b = ld(sys.argv[1]), ld(sys.argv[2])
q = {}
if len(sys.argv) > 3:
    for l in open(sys.argv[3]): r = json.loads(l); q[r["item"]["id"]] = r["item"]["question"]
inst = lambda t: t["route"]["tier"] == "instant"
same = tier = txt = lost = gained = 0
for k in a:
    x, y = a[k], b.get(k)
    if y is None: print("MISSING in cut4:", k); continue
    if x["route"]["tier"] != y["route"]["tier"]:
        tier += 1
        if inst(x): lost += 1
        if inst(y): gained += 1
        print(f"TIER {k}: {x['route']['tier']} -> {y['route']['tier']} | {q.get(k, x['question'])[:90]}\n    cut3: {x['answer']['text'][:160]!r}\n    cut4 codes: {[c for c in y['route']['reasonCodes'] if c.startswith('instant')]}")
    elif x["route"]["reasonCodes"] != y["route"]["reasonCodes"] or x["answer"]["text"] != y["answer"]["text"]:
        txt += 1; print(f"OTHER {k}: codes/text differ, tier {x['route']['tier']}")
    else: same += 1
print(f"items {len(a)}: identical {same}, tier changed {tier} (instant lost {lost}, instant gained {gained}), other diffs {txt}")
