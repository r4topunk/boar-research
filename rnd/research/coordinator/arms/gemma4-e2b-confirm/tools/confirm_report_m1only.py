#!/usr/bin/env python3
"""GEMMA4-E2B-CONFIRM report (0 LLM). Usage: python3 -I confirm_report.py <out.json>   (paths are fixed below; frozen with CONFIRM-criterion.md)
Labels = null-cal/tools/labels.py (GATE v2 labels). U = agg_run.py U (s := 0 for declined). Bootstrap: items resampled with replacement, B 2000, seed 11,
CI = sorted[50], sorted[1949] (as stage2_verdict.py). Pairs: candidate vs control on the same item ids (paired within seed / pack set).
Pooled K0 = the two K0 seeds (42, 43) stacked: U_pooled = sum s / sum sref over both seeds' rows (control and candidate each paired within its own seed);
the bootstrap resamples ITEMS (97) and carries both seeds' rows of a resampled item together. Also the plain mean of the two per-seed dU."""
import json, sys, os, random
A = "<workspace>/rnd/research/coordinator/arms"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
J = lambda p: json.load(open(p))["items"]
P = dict(
    ctl42K0=A + "/lp-screens/control/aggregates/lpctl-K0-main-s42.json",
    gem42K0=A + "/gemma4-e2b/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json",
    ctl43K0=A + "/gemma4-e2b-confirm/runs/c43/aggregates/gemma4-e2b-confirm-c43-K0-main-s42.json",
    gem43K0=A + "/gemma4-e2b-confirm/runs/g43/aggregates/gemma4-e2b-confirm-g43-K0-main-s42.json")
D = {k: J(v) for k, v in P.items()}; ids = sorted(D["ctl42K0"])
for k in D: assert set(D[k]) == set(ids), k
L = {k: {i: label(D[k][i]) for i in ids} for k in D}
B = 2000
def U(k, xs): return sum(0 if D[k][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
def UD(k, xs): return sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
def ceu(k, xs): return sum(L[k][i]["CEu"] for i in xs) / len(xs)
def ci(f, pool):
    rnd = random.Random(11); b = []
    for _ in range(B): b.append(f([rnd.choice(pool) for _ in pool]))
    b.sort(); return [round(b[50], 4), round(b[1949], 4)]
def pair(c, g, name):
    cov = [i for i in ids if L[c][i]["shown"]]
    UC = lambda k, xs: sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)  # U on covered: refused := 0
    f = lambda xs: U(g, xs) - U(c, xs)
    r = dict(name=name, ctl=c, cand=g, n=len(ids), U_ctl=round(U(c, ids), 4), U_cand=round(U(g, ids), 4), dU=round(f(ids), 4), dU_ci=ci(f, ids),
             CEu_ctl=round(ceu(c, ids), 4), CEu_cand=round(ceu(g, ids), 4), dCEu=round(ceu(g, ids) - ceu(c, ids), 4),
             CEu_count=[sum(L[c][i]["CEu"] for i in ids), sum(L[g][i]["CEu"] for i in ids)],
             CE_count=[sum(L[c][i]["CE"] for i in ids), sum(L[g][i]["CE"] for i in ids)],
             decline_count=[sum(L[c][i]["decline"] for i in ids), sum(L[g][i]["decline"] for i in ids)],
             warned_count=[sum(L[c][i]["warned"] for i in ids), sum(L[g][i]["warned"] for i in ids)],
             refused_R_count=[sum(L[c][i]["R"] for i in ids), sum(L[g][i]["R"] for i in ids)],
             Udefault_ctl=round(UD(c, ids), 4), Udefault_cand=round(UD(g, ids), 4), Udefault_d=round(UD(g, ids) - UD(c, ids), 4),
             Udefault_d_ci=ci(lambda xs: UD(g, xs) - UD(c, xs), ids),
             covered=len(cov), Ucov_ctl=round(UC(c, cov), 4), Ucov_cand=round(UC(g, cov), 4), Ucov_d=round(UC(g, cov) - UC(c, cov), 4),
             Ucov_d_ci=ci(lambda xs: UC(g, xs) - UC(c, xs), cov),
             changed_text=sum(D[g][i]["text"] != D[c][i]["text"] for i in ids))
    return r
out = dict(M1_seed43_K0=pair("ctl43K0", "gem43K0", "M1 K0 seed 43"),
           M1_seed42_K0_ref=pair("ctl42K0", "gem42K0", "stage 2 K0 seed 42 (reference, recomputed)"))
# pooled K0, two seeds
def Up(sides, xs): return sum((0 if D[k][i]["declined"] else D[k][i]["s"]) for k in sides for i in xs) / sum(D[k][i]["sref"] for k in sides for i in xs)
def CEp(sides, xs): return sum(L[k][i]["CEu"] for k in sides for i in xs) / (len(sides) * len(xs))
def Rp(sides, xs): return sum(L[k][i]["R"] for k in sides for i in xs)
cs, gs = ["ctl42K0", "ctl43K0"], ["gem42K0", "gem43K0"]
fp = lambda xs: Up(gs, xs) - Up(cs, xs)
fce = lambda xs: CEp(gs, xs) - CEp(cs, xs)
out["pooled_K0_two_seed"] = dict(n_items=len(ids), n_rows=2 * len(ids), U_ctl=round(Up(cs, ids), 4), U_cand=round(Up(gs, ids), 4), dU=round(fp(ids), 4), dU_ci=ci(fp, ids),
    CEu_ctl=round(CEp(cs, ids), 4), CEu_cand=round(CEp(gs, ids), 4), dCEu=round(fce(ids), 4), dCEu_ci=ci(fce, ids),
    CEu_count=[sum(L[k][i]["CEu"] for k in cs for i in ids), sum(L[k][i]["CEu"] for k in gs for i in ids)],
    refused_R_count=[Rp(cs, ids), Rp(gs, ids)], mean_of_seed_dU=round((out["M1_seed42_K0_ref"]["dU"] + out["M1_seed43_K0"]["dU"]) / 2, 4))
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out.items(): print(k, json.dumps(v))
