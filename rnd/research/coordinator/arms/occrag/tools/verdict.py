#!/usr/bin/env python3
"""OCCRAG stage-2 verdict (0 LLM). Usage: python3 -I verdict.py <K0|K1> <candidate main agg.json> <mini K0 MAIN control agg.json> [--json out]
Both pack sets compare against the mini K0 MAIN control (arms/lp-screens/control/aggregates/lpctl-K0-main-s42.json), as the criterion states.
Reads tools/agg_run.py aggregates (items[id] = corr, s, sref, declined, CE, warned, refusal_like, text). Paired item bootstrap B 2000 seed 11, 2.5/97.5 pct.
CE rate = CE count / non-declined answers; decline+refusal rate = refusal_like count / n (refusal_like includes declined); U = sum(s, not declined) / sum(sref).
K0 PASS iff CE change <= -0.05 AND CE CI high < 0 AND refusal change <= +0.03 AND U change >= -0.01.
K1 PASS iff U change >= +0.03 AND U CI low > 0 AND CE change <= +0.02."""
import json, random, sys
K = sys.argv[1]; c, k = (json.load(open(p)) for p in sys.argv[2:4]); C, Kc = c["items"], k["items"]
ids = [i for i in C if i in Kc]
def met(src, xs):
    it = [src[i] for i in xs]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["declined"]]
    return dict(U=sum(0 if x["declined"] else x["s"] for x in it) / sr, Q=sum(x["s"] for x in it) / sr, CE=sum(x["CE"] for x in nd) / len(nd) if nd else 0.0,
                RF=sum(x["refusal_like"] for x in it) / len(it))
rnd = random.Random(11); B = 2000; bs = {q: [] for q in ("U", "Q", "CE", "RF")}
for _ in range(B):
    s = [rnd.choice(ids) for _ in ids]; x, y = met(C, s), met(Kc, s)
    for q in bs: bs[q].append(x[q] - y[q])
x, y = met(C, ids), met(Kc, ids)
d = {q: dict(d=round(x[q] - y[q], 4), ci=[round(sorted(v)[int(0.025 * B)], 4), round(sorted(v)[int(0.975 * B) - 1], 4)]) for q, v in bs.items()}
if K == "K0":
    cl = dict(CE=d["CE"]["d"] <= -0.05 and d["CE"]["ci"][1] < 0, refusal=d["RF"]["d"] <= 0.03, U=d["U"]["d"] >= -0.01)
else:
    cl = dict(U=d["U"]["d"] >= 0.03 and d["U"]["ci"][0] > 0, CE=d["CE"]["d"] <= 0.02)
out = dict(pack_set=K, n=len(ids), cand=x, control=y, deltas=d, ce_counts=[sum(C[i]["CE"] for i in ids), sum(Kc[i]["CE"] for i in ids)],
           warned=[sum(C[i]["warned"] for i in ids), sum(Kc[i]["warned"] for i in ids)], clauses=cl, verdict="PASS" if all(cl.values()) else "NO")
print(json.dumps(out, indent=1))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
