"""MICROD2Q inflation variant: rank the 137 items by the max token-Jaccard between their fact chunks' KEPT questions and the
self-test question (parse_filter inflation rows, jac_kept); the top 20 % (ceil(0.2 x 137) = 28 items; ties broken by item id)
lose the questions of their fact chunks; every other expansion is unchanged. Writes aggregates/deinfl-items.json and
aggregates/full.deinfl.questions.json. usage: python3 -I make_deinfl.py"""
import json, math, collections
A = "<workspace>/rnd/research/coordinator/arms/microd2q"
F = json.load(open(f"{A}/aggregates/full.json")); Q = json.load(open(f"{A}/aggregates/full.questions.json"))
best = collections.defaultdict(float); facts = collections.defaultdict(set)
for r in F["inflation"]:
    best[r["id"]] = max(best[r["id"]], r["jac_kept"]); facts[r["id"]].add((r["pack"], str(r["chunk"])))
ranked = sorted(best, key=lambda i: (-best[i], i)); k = math.ceil(0.2 * len(ranked)); top = ranked[:k]
removed = 0
for i in top:
    for p, c in facts[i]:
        if c in Q.get(p, {}): del Q[p][c]; removed += 1
json.dump(top, open(f"{A}/aggregates/deinfl-items.json", "w"))
json.dump(Q, open(f"{A}/aggregates/full.deinfl.questions.json", "w"))
print(json.dumps({"items": len(ranked), "removed_items": k, "removed_chunks": removed, "jac_cut": best[top[-1]], "jac_kept_quantiles": [round(sorted(best.values())[int(q * (len(best) - 1))], 3) for q in (0, .25, .5, .75, .8, .9, 1)]}))
