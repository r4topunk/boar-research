#!/usr/bin/env python3
"""QUANTLITE declared split (descriptive): per LITE6 bucket of the Q4 item (below-4B items: thin/not_read/invented/identical; above-4B items -> 'above'),
mean BOAR score Q8 vs Q4 (paired.mjs perItem sa/sb) and up/same/down. Writes aggregates/split-q8.json."""
import json, collections
A = "<workspace>/rnd/research/coordinator/arms"
L6 = {r["id"]: r for r in json.load(open(f"{A}/lite6/aggregates/lite6.json"))["items"]}
P = json.load(open(f"{A}/quantlite/runs/quantlite-q8-st20-s42.Q8stvsQ4X.haiku55-low.json"))["perItem"]
g = collections.defaultdict(list)
for r in P:
    l = L6[r["id"]]; b = l["bucket"] if l["side"] == "below" else l["side"]; g[b].append(r)
out = {b: {"n": len(v), "q8_mean": round(sum(r["sa"] for r in v) / len(v), 3), "q4_mean": round(sum(r["sb"] for r in v) / len(v), 3),
           "up_same_down": [sum(r["sa"] > r["sb"] for r in v), sum(r["sa"] == r["sb"] for r in v), sum(r["sa"] < r["sb"] for r in v)]} for b, v in sorted(g.items())}
json.dump(out, open(f"{A}/quantlite/aggregates/split-q8.json", "w"), indent=1); print(json.dumps(out))
