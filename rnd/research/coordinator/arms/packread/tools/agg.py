#!/usr/bin/env python3
"""PACKREAD aggregation (0 LLM): per-item score = mean of the 3 dims over both judge orders; Q = sum s / sum s_ref; item bootstrap B 2000 seed 11;
paired contrast vs a base run on shared ids. Usage: python3 -I agg.py <base judgments> <judgments ...>"""
import json, sys, random
def load(p):
    by = {}
    for l in open(p):
        r = json.loads(l)
        if str(r.get("ok")) != "True": continue
        m = r["mapped"] if isinstance(r["mapped"], dict) else json.loads(r["mapped"].replace("'", '"'))
        mr = lambda d: sum(d.values()) / len(d)
        by.setdefault(r["queryId"], []).append((mr(m["boar"]), mr(m["ref"]), m["winner"]))
    return {q: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v), v) for q, v in by.items() if len(v) == 2}
def ratio(d, ids): return sum(d[i][0] for i in ids) / sum(d[i][1] for i in ids)
def ci(fn, ids, B=2000, seed=11):
    rnd = random.Random(seed); xs = sorted(fn([rnd.choice(ids) for _ in ids]) for _ in range(B)); return round(xs[50], 3), round(xs[1949], 3)
base = load(sys.argv[1]); print(f"{'run':38} {'n':>3} {'Q':>6} {'CI':>15} {'vs base':>8} {'paired CI':>17}")
for p in sys.argv[1:]:
    d = load(p); ids = sorted(set(d) & set(base)); name = p.rsplit("/", 1)[-1].replace(".judgments.jsonl", "")
    q = ratio(d, ids); c = ci(lambda s: ratio(d, s), ids); dl = q - ratio(base, ids); pc = ci(lambda s: ratio(d, s) - ratio(base, s), ids, seed=1)
    print(f"{name:38} {len(ids):>3} {q:6.3f} {str(c):>15} {dl:+8.3f} {str(pc):>17}")
