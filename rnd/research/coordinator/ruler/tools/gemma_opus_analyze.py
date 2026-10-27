#!/usr/bin/env python3
"""GEMMA-OPUS-MAIN analysis (0 calls). python3 -I gemma_opus_analyze.py <out.json>
Opus per-item rows = for each arm and id, the unit (id, answer text) from ../gemma-opus-main/in/set.json: reused source row pair or this pass's
outputs (../gemma-opus-main/out/*.judgments.jsonl), via cv5_opus_pool.pool (identical frame filter). Metrics = confirm_report.py definitions on
Opus labels (null-cal labels.py). Haiku = the existing agg_run aggregates of the same traces."""
import json, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP
A = "<workspace>/rnd/research/coordinator/arms"; sys.path.insert(0, A + "/null-cal/tools"); from labels import label
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/gemma-opus-main/"
S = json.load(open(HERE + "in/set.json")); ids = sorted(x for x in open(f"{A}/lp-screens/main-97.ids").read().split() if x)
HAG = dict(ctl42=f"{A}/lp-screens/control/aggregates/lpctl-K0-main-s42.json", gem42=f"{A}/gemma4-e2b/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json",
           ctl43=f"{A}/gemma4-e2b-confirm/runs/c43/aggregates/gemma4-e2b-confirm-c43-K0-main-s42.json",
           gem43=f"{A}/gemma4-e2b-confirm/runs/g43/aggregates/gemma4-e2b-confirm-g43-K0-main-s42.json")
P = {}
for u, (fr, fq) in S["frames"].items(): P.update(CP.pool(fr, fq))
arms = ["ctl42", "gem42"] + (["ctl43", "gem43"] if S["do_s43"] else [])
D, H, missing = {}, {}, []
for a in arms:
    T = {(j := json.loads(l)).get("itemId") or j.get("queryId"): j for l in open(S["traces"][a]) if l.strip()}
    D[a] = {}; H[a] = json.load(open(HAG[a]))["items"]
    for i in ids:
        t = T[i]["answer"]; k = CP.key(i, t["text"])
        if k not in P: missing.append(f"{a}:{i}"); continue
        ms = [P[k]["boarA"], P[k]["boarB"]]; mean = lambda x: sum(x.values()) / 3
        D[a][i] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2,
                       corr=sum(m["boar"]["correctness"] for m in ms) / 2, text=t["text"], declined=bool(t.get("declined")), src=P[k]["src"])
if missing: sys.exit(f"MISSING Opus units {len(missing)}: {','.join(missing[:20])}")
L = {a: {i: label(D[a][i]) for i in ids} for a in arms}; LH = {a: {i: label(H[a][i]) for i in ids} for a in arms}
B = 2000
def U(k, xs): return sum(0 if D[k][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
def UD(k, xs): return sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
def UH(k, xs): return sum(0 if H[k][i]["declined"] else H[k][i]["s"] for i in xs) / sum(H[k][i]["sref"] for i in xs)
def ceu(k, xs): return sum(L[k][i]["CEu"] for i in xs) / len(xs)
def ci(f, pool):
    rnd = random.Random(11); b = []
    for _ in range(B): b.append(f([rnd.choice(pool) for _ in pool]))
    b.sort(); return [round(b[50], 4), round(b[1949], 4)]
def rank(v):
    o = sorted(range(len(v)), key=lambda j: v[j]); r = [0.0] * len(v); j = 0
    while j < len(o):
        k = j
        while k + 1 < len(o) and v[o[k + 1]] == v[o[j]]: k += 1
        for m in range(j, k + 1): r[o[m]] = (j + k) / 2
        j = k + 1
    return r
def spearman(x, y):
    rx, ry = rank(x), rank(y); mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    c = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); return c / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
def arm_stats(a):
    return dict(U_opus=round(U(a, ids), 4), U_haiku=round(UH(a, ids), 4), offset=round(U(a, ids) - UH(a, ids), 4),
                offset_ci=ci(lambda xs: U(a, xs) - UH(a, xs), ids),
                spearman_s=round(spearman([D[a][i]["s"] for i in ids], [H[a][i]["s"] for i in ids]), 3),
                CE_agree=sum(L[a][i]["CE"] == LH[a][i]["CE"] for i in ids), correct_agree=sum((D[a][i]["corr"] >= 4) == (H[a][i]["corr"] >= 4) for i in ids),
                CEu_opus=sum(L[a][i]["CEu"] for i in ids), CEu_haiku=sum(LH[a][i]["CEu"] for i in ids),
                CEu_haiku_only=sorted(i for i in ids if LH[a][i]["CEu"] and not L[a][i]["CEu"]), CEu_opus_only=sorted(i for i in ids if L[a][i]["CEu"] and not LH[a][i]["CEu"]),
                n_reused=sum("gemma-opus-main/out" not in D[a][i]["src"] for i in ids))
def pair(c, g, name):
    cov = [i for i in ids if L[c][i]["shown"]]; both = [i for i in ids if L[c][i]["shown"] and L[g][i]["shown"]]
    UC = lambda k, xs: sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
    f = lambda xs: U(g, xs) - U(c, xs); fh = lambda xs: UH(g, xs) - UH(c, xs)
    return dict(name=name, ctl=c, cand=g, n=len(ids), U_ctl=round(U(c, ids), 4), U_cand=round(U(g, ids), 4), dU=round(f(ids), 4), dU_ci=ci(f, ids),
                dU_haiku=round(fh(ids), 4), dU_haiku_ci=ci(fh, ids), better_worse=[sum(D[g][i]["s"] > D[c][i]["s"] for i in ids), sum(D[g][i]["s"] < D[c][i]["s"] for i in ids)],
                CEu_ctl=round(ceu(c, ids), 4), CEu_cand=round(ceu(g, ids), 4), dCEu=round(ceu(g, ids) - ceu(c, ids), 4), dCEu_ci=ci(lambda xs: ceu(g, xs) - ceu(c, xs), ids),
                CEu_count=[sum(L[c][i]["CEu"] for i in ids), sum(L[g][i]["CEu"] for i in ids)], CE_count=[sum(L[c][i]["CE"] for i in ids), sum(L[g][i]["CE"] for i in ids)],
                decline_count=[sum(L[c][i]["decline"] for i in ids), sum(L[g][i]["decline"] for i in ids)],
                warned_count=[sum(L[c][i]["warned"] for i in ids), sum(L[g][i]["warned"] for i in ids)],
                refused_R_count=[sum(L[c][i]["R"] for i in ids), sum(L[g][i]["R"] for i in ids)],
                Udefault_ctl=round(UD(c, ids), 4), Udefault_cand=round(UD(g, ids), 4), Udefault_d=round(UD(g, ids) - UD(c, ids), 4), Udefault_d_ci=ci(lambda xs: UD(g, xs) - UD(c, xs), ids),
                both_shown=len(both), Uboth_ctl=round(UC(c, both), 4), Uboth_cand=round(UC(g, both), 4), Uboth_d=round(UC(g, both) - UC(c, both), 4), Uboth_d_ci=ci(lambda xs: UC(g, xs) - UC(c, xs), both),
                covered=len(cov), Ucov_d=round(UC(g, cov) - UC(c, cov), 4), Ucov_d_ci=ci(lambda xs: UC(g, xs) - UC(c, xs), cov),
                changed_text=sum(D[g][i]["text"] != D[c][i]["text"] for i in ids))
out = dict(criterion_sha256=open(HERE + "../GEMMA-OPUS-MAIN-criterion.sha256").read().split()[0], arms={a: arm_stats(a) for a in arms},
           s42=pair("ctl42", "gem42", "seed 42 (primary)"))
p = out["s42"]; out["verdict"] = "GO" if (p["dU"] >= 0.03 and p["dU_ci"][0] > 0) else "NULL"
if S["do_s43"]:
    out["s43"] = pair("ctl43", "gem43", "seed 43 (report only)")
    def Up(sides, xs): return sum((0 if D[k][i]["declined"] else D[k][i]["s"]) for k in sides for i in xs) / sum(D[k][i]["sref"] for k in sides for i in xs)
    def CEp(sides, xs): return sum(L[k][i]["CEu"] for k in sides for i in xs) / (len(sides) * len(xs))
    cs, gs = ["ctl42", "ctl43"], ["gem42", "gem43"]; fp = lambda xs: Up(gs, xs) - Up(cs, xs); fce = lambda xs: CEp(gs, xs) - CEp(cs, xs)
    out["pooled"] = dict(U_ctl=round(Up(cs, ids), 4), U_cand=round(Up(gs, ids), 4), dU=round(fp(ids), 4), dU_ci=ci(fp, ids), dCEu=round(fce(ids), 4), dCEu_ci=ci(fce, ids),
                         CEu_count=[sum(L[k][i]["CEu"] for k in cs for i in ids), sum(L[k][i]["CEu"] for k in gs for i in ids)],
                         refused_R_count=[sum(L[k][i]["R"] for k in cs for i in ids), sum(L[k][i]["R"] for k in gs for i in ids)])
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
