#!/usr/bin/env python3
"""GREEDY stage-2 verdict (0 LLM). Usage: python3 -I verdict.py <candidate main agg.json> <mini K0 MAIN control agg.json> [--json out]
Reads tools/agg_run.py aggregates (items[id] = corr, s, sref, declined, CE, warned, refusal_like, text). Paired item bootstrap B 2000 seed 11, 2.5/97.5 pct.
CE rate = CE count / non-declined answers (agg_run definition). decline+refusal rate = refusal_like count / n (refusal_like already includes declined)."""
import json, random, sys
c, k = (json.load(open(p)) for p in sys.argv[1:3]); C, K = c["items"], k["items"]
ids = [i for i in C if i in K]; W = None
def met(src, xs):
    it = [src[i] for i in xs]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["declined"]]
    return dict(U=sum(0 if x["declined"] else x["s"] for x in it) / sr, Q=sum(x["s"] for x in it) / sr, CE=sum(x["CE"] for x in nd) / len(nd) if nd else 0.0,
                RF=sum(x["refusal_like"] for x in it) / len(it))
rnd = random.Random(11); B = 2000; bs = {k_: [] for k_ in ("U", "Q", "CE", "RF")}
for _ in range(B):
    s = [rnd.choice(ids) for _ in ids]; x, y = met(C, s), met(K, s)
    for q in bs: bs[q].append(x[q] - y[q])
x, y = met(C, ids), met(K, ids)
d = {q: dict(d=round(x[q] - y[q], 4), ci=[round(sorted(v)[int(0.025 * B)], 4), round(sorted(v)[int(0.975 * B) - 1], 4)]) for q, v in bs.items()}
def ce_split(src):
    w = [i for i in ids if src[i]["warned"]]; u = [i for i in ids if not src[i]["warned"]]
    f = lambda xs: (sum(src[i]["CE"] for i in xs), len(xs))
    return dict(warned=f(w), unwarned=f(u))
p_ce = d["CE"]["d"] <= -0.05 and d["CE"]["ci"][1] < 0
p_rf = d["RF"]["d"] <= 0.03; p_u = d["U"]["d"] >= -0.01
out = dict(n=len(ids), cand=x, control=y, deltas=d, ce_counts=[sum(C[i]["CE"] for i in ids), sum(K[i]["CE"] for i in ids)],
           warned=[sum(C[i]["warned"] for i in ids), sum(K[i]["warned"] for i in ids)], ce_split_cand=ce_split(C), ce_split_control=ce_split(K),
           clauses=dict(CE=p_ce, refusal=p_rf, U=p_u), verdict="PASS" if p_ce and p_rf and p_u else "NO")
print(json.dumps(out, indent=1))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
