#!/usr/bin/env python3
"""QWEN35-2B stage-2 verdict (0 LLM). Usage: python3 -I verdict2.py <candidate MAIN agg.json> <mini K0 MAIN control agg.json (lp-screens lpctl-K0-main-s42)> [--json out]
Inputs are tools/agg_run.py aggregates (items[id] = corr, s, sref, declined, CE, warned, refusal_like, text).
U        = sum(0 if declined else s) / sum(sref)   (agg_run.py / greedy verdict.py definition, engine-declined items score 0)
CEu rate = CE-unwarned count / n, with the corrected labels of arms/null-cal/tools/labels.py (CEu = not decline, corr <= 1.5, no warning line)
Paired item bootstrap B 2000, seed 11, 2.5 / 97.5 percentiles.
PASS iff U delta >= +0.03 AND paired CI low of U delta > 0 AND CEu rate delta <= +0.02 (frozen in QWEN35-criterion.md)."""
import json, os, random, sys
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/null-cal/tools"); from labels import label
c, k = (json.load(open(p)) for p in sys.argv[1:3]); C, K = c["items"], k["items"]
ids = sorted(i for i in C if i in K); LC = {i: label(C[i]) for i in ids}; LK = {i: label(K[i]) for i in ids}
def met(src, L, xs):
    sr = sum(src[i]["sref"] for i in xs)
    return dict(U=sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sr, CEu=sum(L[i]["CEu"] for i in xs) / len(xs),
                R=sum(L[i]["R"] for i in xs) / len(xs), decline=sum(L[i]["decline"] for i in xs) / len(xs))
rnd = random.Random(11); B = 2000; bs = {q: [] for q in ("U", "CEu", "R", "decline")}
for _ in range(B):
    s = [rnd.choice(ids) for _ in ids]; x, y = met(C, LC, s), met(K, LK, s)
    for q in bs: bs[q].append(x[q] - y[q])
x, y = met(C, LC, ids), met(K, LK, ids)
d = {q: dict(d=round(x[q] - y[q], 4), ci=[round(sorted(v)[int(0.025 * B)], 4), round(sorted(v)[int(0.975 * B) - 1], 4)]) for q, v in bs.items()}
p_u = d["U"]["d"] >= 0.03 and d["U"]["ci"][0] > 0; p_ce = d["CEu"]["d"] <= 0.02
out = dict(n=len(ids), cand={q: round(v, 4) for q, v in x.items()}, control={q: round(v, 4) for q, v in y.items()}, deltas=d,
           ceu_counts=[sum(LC[i]["CEu"] for i in ids), sum(LK[i]["CEu"] for i in ids)], ce_counts=[sum(LC[i]["CE"] for i in ids), sum(LK[i]["CE"] for i in ids)],
           clauses=dict(U=p_u, CEu=p_ce), verdict="PASS" if p_u and p_ce else "NO")
print(json.dumps(out, indent=1))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
