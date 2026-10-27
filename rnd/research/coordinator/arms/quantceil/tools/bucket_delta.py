#!/usr/bin/env python3
"""QUANTCEIL addendum 1: paired Δ (Q − H, per-item ratio = BOAR points / reference points over the 3 dims, mean of both orders)
by LOSSMAP primary bucket of H and by the wrong_fact axis. usage: bucket_delta.py <Q.judgments> <H.judgments> <lossmap-H.json> [ids]"""
import json, sys, random
from collections import defaultdict
def ratios(f):
    acc = defaultdict(lambda: [0.0, 0.0])
    for l in open(f):
        r = json.loads(l)
        if not r.get("ok"): continue
        b = r["mapped"]["boar"]; g = r["mapped"]["ref"]
        acc[r["queryId"]][0] += sum(b.values()); acc[r["queryId"]][1] += sum(g.values())
    return {k: v[0] / v[1] for k, v in acc.items() if v[1]}
Q, H = ratios(sys.argv[1]), ratios(sys.argv[2]); L = json.load(open(sys.argv[3]))
ids = [l.strip() for l in open(sys.argv[4])] if len(sys.argv) > 4 else sorted(set(Q) & set(H))
ids = [i for i in ids if i in Q and i in H]
prim = {i["id"]: i["primary"] for i in L["items"]}; wrong = {i["id"]: i["labels"]["wrong_fact"] for i in L["items"]}
def ci(d, n=4000):
    random.seed(7); m = []
    for _ in range(n): s = [random.choice(d) for _ in d]; m.append(sum(s) / len(s))
    m.sort(); return round(m[int(0.025 * n)], 3), round(m[int(0.975 * n)], 3)
groups = defaultdict(list)
for i in ids: groups["all"].append(i); groups["primary=" + prim.get(i, "?")].append(i); groups["wrong_fact=" + str(wrong.get(i))].append(i)
for g, its in sorted(groups.items(), key=lambda x: -len(x[1])):
    d = [Q[i] - H[i] for i in its]
    if len(d) >= 3: print(f"{g:28s} n={len(d):3d} dRatio={sum(d)/len(d):+.3f} CI={ci(d)} Q={sum(Q[i] for i in its)/len(its):.3f} H={sum(H[i] for i in its)/len(its):.3f} up/same/down={sum(x>0.02 for x in d)}/{sum(abs(x)<=0.02 for x in d)}/{sum(x<-0.02 for x in d)}")
