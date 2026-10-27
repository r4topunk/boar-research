#!/usr/bin/env python3
"""PACK-NIST paired delta (method of arms/packs/SELFTEST-SCORES: per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11).
Per item: system and reference mean rubric (correctness, completeness, usefulness), averaged over both orders.
Usage: python3 -I paired_delta.py <runs dir> <run A> <run B> [--json out]   (Δ = A − B)"""
import json, sys, random, collections
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
D, A, B = sys.argv[1:4]
def load(run):
    g = collections.defaultdict(list)
    for l in open(f"{D}/{run}.judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok") and r.get("mapped"): g[r["queryId"]].append(r["mapped"])
    return {q: (sum(mr(x["boar"]) for x in v) / len(v), sum(mr(x["ref"]) for x in v) / len(v)) for q, v in g.items() if len(v) == 2}
a, b = load(A), load(B); ids = sorted(set(a) & set(b))
ratio = lambda d, I, k: sum(d[i][0] for i in I) / sum(d[i][1] for i in I) if k == "raw" else sum(d[i][0] - 1 for i in I) / sum(d[i][1] - 1 for i in I)
out = {"n": len(ids), "A": A, "B": B}
rng = random.Random(11)
boots = [[rng.choice(ids) for _ in ids] for _ in range(2000)]
for k in ("raw", "above_min"):
    pt = ratio(a, ids, k) - ratio(b, ids, k)
    bs = sorted(ratio(a, I, k) - ratio(b, I, k) for I in boots)
    out[k] = {"A": round(ratio(a, ids, k), 4), "B": round(ratio(b, ids, k), 4), "delta": round(pt, 4), "ci95": [round(bs[49], 4), round(bs[1949], 4)]}
out["better"] = sum(a[i][0] > b[i][0] for i in ids); out["worse"] = sum(a[i][0] < b[i][0] for i in ids)
out["wins_vs_gold_A"] = sum(a[i][0] > a[i][1] for i in ids)
print(json.dumps(out))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
