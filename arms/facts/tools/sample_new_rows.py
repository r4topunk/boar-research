#!/usr/bin/env python3
"""r6 data review (FACTS-r6-criterion.md C): a seeded random sample of entities in the new asset that are NOT in the r5 asset,
printed with their values. Usage: python3 -I sample_new_rows.py <r5_asset.json> <new_asset.json> [seed=46] [n=60]
(the r5 asset is `git show 802c28bb:src/rag/facts.v1.json`)."""
import json, random, sys
old = {e["q"] for e in json.load(open(sys.argv[1]))["entities"]}
ents = [e for e in json.load(open(sys.argv[2]))["entities"] if e["q"] not in old]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 46
n = int(sys.argv[4]) if len(sys.argv) > 4 else 60
ents.sort(key=lambda e: e["q"])
pick = random.Random(seed).sample(ents, n)
print(f"# seed {seed}; {n} of {len(ents)} new entities (not in the r5 asset)")
for i, e in enumerate(pick, 1):
    vals = []
    for k in ("pop", "area", "elev", "height", "len", "depth", "inc", "end", "ctry", "t", "cap", "lang", "cont"):
        if k in e:
            v = e[k]
            vals.append(f"{k}={v[0]:,} ({v[1]})" if k == "pop" else f"{k}={v}")
    print(f"{i:02d} {e['q']} [{e['k']}] {e['n']} | {e.get('d', '')} | " + "; ".join(vals) + (f" | aliases: {', '.join(e['a'][:6])}" if e.get("a") else ""))
