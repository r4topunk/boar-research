#!/usr/bin/env python3
"""SMOLLM3-3B stage-2 verdict (0 LLM). Usage: python3 -I stage2_verdict.py <candidate MAIN agg.json> <lpctl-K0-main-s42.json>
PASS iff dU >= +0.03 and paired bootstrap CI low (2.5 pct) > 0 and dCEu_rate <= +0.02 (SMOL-criterion.md §4).
U = agg_run.py U (sum s / sum sref, s := 0 for declined). CEu = CE and not warned under null-cal/tools/labels.py (GATE v2 labels).
Bootstrap: items resampled with replacement, B 2000, seed 11 (as agg_run.py). Also reports the default-mode U (s := 0 when R) for information."""
import json, sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../null-cal/tools")); from labels import label
C = json.load(open(sys.argv[1]))["items"]; K = json.load(open(sys.argv[2]))["items"]; ids = sorted(K); assert set(ids) == set(C), "item sets differ"
LC = {i: label(C[i]) for i in ids}; LK = {i: label(K[i]) for i in ids}
U = lambda X, xs: sum(0 if X[i]["declined"] else X[i]["s"] for i in xs) / sum(X[i]["sref"] for i in xs)
UD = lambda L, xs: sum(0 if L[i]["R"] else L[i]["s"] for i in xs) / sum(L[i]["sref"] for i in xs)
rnd = random.Random(11); bs = []; bsd = []
for _ in range(2000):
    s = [rnd.choice(ids) for _ in ids]; bs.append(U(C, s) - U(K, s)); bsd.append(UD(LC, s) - UD(LK, s))
bs.sort(); bsd.sort()
dU = U(C, ids) - U(K, ids); ci = (bs[50], bs[1949])
ceu_c = sum(LC[i]["CEu"] for i in ids) / len(ids); ceu_k = sum(LK[i]["CEu"] for i in ids) / len(ids); dceu = ceu_c - ceu_k
ok = dU >= 0.03 and ci[0] > 0 and dceu <= 0.02
out = dict(n=len(ids), U_ctl=round(U(K, ids), 4), U_cand=round(U(C, ids), 4), dU=round(dU, 4), dU_ci=[round(x, 4) for x in ci],
           CEu_ctl=round(ceu_k, 4), CEu_cand=round(ceu_c, 4), dCEu=round(dceu, 4),
           Udefault_ctl=round(UD(LK, ids), 4), Udefault_cand=round(UD(LC, ids), 4), dUdefault=round(UD(LC, ids) - UD(LK, ids), 4), dUdefault_ci=[round(bsd[50], 4), round(bsd[1949], 4)],
           R_ctl=sum(LK[i]["R"] for i in ids), R_cand=sum(LC[i]["R"] for i in ids), verdict="PASS" if ok else "FAIL")
print(json.dumps(out))
