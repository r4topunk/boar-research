#!/usr/bin/env python3
"""MIN3CITE-OPUS analysis (0 calls). python3 -I min3cite_opus_analyze.py A|B <out.json>
Step A (no Opus): answer length + citation counts (traces), Haiku per-item deltas (existing agg_run aggregates), Haiku length-adjusted views,
  report-only Haiku MIN3CITE - 4B (VS4B traces, same control).
Step B: the same metrics on Opus rows (set.json units: reused rows or ../min3cite-opus-main/out/*.judgments.jsonl via cv5_opus_pool.pool).
Definitions = gemma_opus_analyze.py (confirm_report.py) on labels.py labels; bootstrap random.Random(11), B 2000, sorted[50]/sorted[1949].
Length views (report only, no truncation re-judge): (L1) dU on items where both arms are shown and MIN3CITE's outputTokens <= the 1.7B's median
live outputTokens; (L2) dU on items with MIN3CITE tokens <= 1.5 x the 1.7B's on that item; (L3) OLS of per-item d_i = s'_m3c - s'_ctl
(s' = 0 if trace-declined) on dtok_i = tokens_m3c - tokens_ctl over the 97, intercept / mean sref = dU predicted at equal length, bootstrap CI."""
import json, sys, os, random, re, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP
A = "<workspace>/rnd/research/coordinator/arms"; sys.path.insert(0, A + "/null-cal/tools"); from labels import label
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/min3cite-opus-main/"
MODE, OUTF = sys.argv[1], sys.argv[2]
S = json.load(open(HERE + "in/set.json")); ids = sorted(x for x in open(f"{A}/lp-screens/main-97.ids").read().split() if x)
HAG = dict(ctl=f"{A}/lp-screens/control/aggregates/lpctl-K0-main-s42.json", m3c=f"{A}/min3cite/aggregates/min3cite-K0-main-s42.json",
           v4b=f"{A}/gemma4-e2b-vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json")
TR = {a: {(j := json.loads(l)).get("itemId") or j.get("queryId"): j for l in open(S["traces"][a]) if l.strip()} for a in ("ctl", "m3c", "v4b")}
B = 2000
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
    c = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); return round(c / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5, 3)
# ---- length and citations (0 LLM)
tok = {a: {i: TR[a][i]["timing"].get("outputTokens", 0) or 0 for i in ids} for a in TR}
live = [i for i in ids if tok["ctl"][i] > 0]
BR = re.compile(r"\[(\d+)\]")
def ncite(a, i): return len(BR.findall(TR[a][i]["answer"]["text"]))
def nkept(a, i): return len(TR[a][i]["answer"].get("cited") or [])
words = lambda a, i: len(TR[a][i]["answer"]["text"].split())
ctl_med = st.median([tok["ctl"][i] for i in live])
length = {a: dict(tokens_median=st.median([tok[a][i] for i in live]), tokens_mean=round(st.mean([tok[a][i] for i in live]), 1),
                  words_median=st.median([words(a, i) for i in live]), brackets_in_text_total=sum(ncite(a, i) for i in live),
                  items_with_bracket=sum(ncite(a, i) > 0 for i in live), cited_kept_total=sum(nkept(a, i) for i in live),
                  items_with_kept_citation=sum(nkept(a, i) > 0 for i in live)) for a in ("ctl", "m3c", "v4b")}
length["n_live"] = len(live); length["ratio_mean_tokens_m3c_ctl"] = round(length["m3c"]["tokens_mean"] / length["ctl"]["tokens_mean"], 2)
length["m3c_le_ctl_median"] = sum(tok["m3c"][i] <= ctl_med for i in live)
# ---- judged rows
def haiku_rows(a): return json.load(open(HAG[a]))["items"]
def opus_rows(a):
    P = {}
    for u, (fr, fq) in S["frames"].items(): P.update(CP.pool(fr, fq))
    D, miss = {}, []
    for i in ids:
        t = TR[a][i]["answer"]; k = CP.key(i, t["text"])
        if k not in P: miss.append(i); continue
        ms = [P[k]["boarA"], P[k]["boarB"]]; mean = lambda x: sum(x.values()) / 3
        D[i] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2,
                    corr=sum(m["boar"]["correctness"] for m in ms) / 2, text=t["text"], declined=bool(t.get("declined")), src=P[k]["src"])
    return D, miss
def metrics(D, c, g, xs_all):
    L = {a: {i: label(D[a][i]) for i in xs_all} for a in (c, g)}
    U = lambda k, xs: sum(0 if D[k][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
    UC = lambda k, xs: sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
    ceu = lambda k, xs: sum(L[k][i]["CEu"] for i in xs) / len(xs)
    both = [i for i in xs_all if L[c][i]["shown"] and L[g][i]["shown"]]
    f = lambda xs: U(g, xs) - U(c, xs)
    sp = lambda k, i: 0 if D[k][i]["declined"] else D[k][i]["s"]
    r = dict(n=len(xs_all), U_ctl=round(U(c, xs_all), 4), U_cand=round(U(g, xs_all), 4), dU=round(f(xs_all), 4), dU_ci=ci(f, xs_all),
             better_worse_tie=[sum(sp(g, i) > sp(c, i) for i in xs_all), sum(sp(g, i) < sp(c, i) for i in xs_all), sum(sp(g, i) == sp(c, i) for i in xs_all)],
             CEu_count=[sum(L[c][i]["CEu"] for i in xs_all), sum(L[g][i]["CEu"] for i in xs_all)], dCEu_rate=round(ceu(g, xs_all) - ceu(c, xs_all), 4),
             dCEu_rate_ci=ci(lambda xs: ceu(g, xs) - ceu(c, xs), xs_all), CE_count=[sum(L[c][i]["CE"] for i in xs_all), sum(L[g][i]["CE"] for i in xs_all)],
             decline_count=[sum(L[c][i]["decline"] for i in xs_all), sum(L[g][i]["decline"] for i in xs_all)],
             warned_count=[sum(L[c][i]["warned"] for i in xs_all), sum(L[g][i]["warned"] for i in xs_all)],
             refused_R_count=[sum(L[c][i]["R"] for i in xs_all), sum(L[g][i]["R"] for i in xs_all)],
             Udefault_d=round(UC(g, xs_all) - UC(c, xs_all), 4), Udefault_d_ci=ci(lambda xs: UC(g, xs) - UC(c, xs), xs_all),
             both_shown=len(both), Uboth_ctl=round(UC(c, both), 4) if both else None, Uboth_cand=round(UC(g, both), 4) if both else None,
             Uboth_d=round(UC(g, both) - UC(c, both), 4) if both else None, Uboth_d_ci=ci(lambda xs: UC(g, xs) - UC(c, xs), both) if both else None)
    return r, L
def length_views(D, L, c="ctl", g="m3c"):
    UC = lambda k, xs: sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
    both = [i for i in ids if L[c][i]["shown"] and L[g][i]["shown"]]
    out = {}
    for name, sel in (("L1_m3c_tokens_le_ctl_median", lambda i: tok[g][i] <= ctl_med), ("L2_m3c_tokens_le_1.5x_ctl_item", lambda i: tok[g][i] <= 1.5 * max(tok[c][i], 1))):
        xs = [i for i in both if sel(i)]
        out[name] = dict(n=len(xs), dU=round(UC(g, xs) - UC(c, xs), 4) if xs else None, dU_ci=ci(lambda ys: UC(g, ys) - UC(c, ys), xs) if len(xs) >= 5 else None)
    sp = lambda k, i: 0 if D[k][i]["declined"] else D[k][i]["s"]
    def ols(xs):
        x = [tok[g][i] - tok[c][i] for i in xs]; y = [sp(g, i) - sp(c, i) for i in xs]; mx, my = sum(x) / len(x), sum(y) / len(y)
        vx = sum((a - mx) ** 2 for a in x); b = sum((a - mx) * (bb - my) for a, bb in zip(x, y)) / vx if vx else 0.0
        msr = sum((D[c][i]["sref"] + D[g][i]["sref"]) / 2 for i in xs) / len(xs)
        return (my - b * mx) / msr, b / msr
    a0, b0 = ols(ids)
    out["L3_ols_equal_length"] = dict(dU_at_equal_length=round(a0, 4), dU_at_equal_length_ci=ci(lambda xs: ols(xs)[0], ids),
                                      slope_per_100_tokens=round(100 * b0, 4), mean_dtok=round(st.mean(tok[g][i] - tok[c][i] for i in ids), 1))
    return out
out = dict(mode=MODE, criterion_sha256=open(HERE + "../MIN3CITE-OPUS-criterion.sha256").read().split()[0], length=length)
H = {a: haiku_rows(a) for a in ("ctl", "m3c", "v4b")}
hm, HL = metrics(H, "ctl", "m3c", ids); out["haiku_m3c_vs_ctl"] = hm
out["haiku_length_views"] = length_views(H, HL)
out["haiku_m3c_vs_4b_report_only"], _ = metrics(H, "v4b", "m3c", ids)
spH = lambda k, i: 0 if H[k][i]["declined"] else H[k][i]["s"]
dh = {i: spH("m3c", i) - spH("ctl", i) for i in ids}
out["haiku_per_item_delta"] = dict(changed_text=sum(H["m3c"][i]["text"] != H["ctl"][i]["text"] for i in ids),
                                   d_s_quartiles=[round(x, 3) for x in st.quantiles(dh.values(), n=4)],
                                   spearman_d_vs_dtok=spearman([dh[i] for i in ids], [tok["m3c"][i] - tok["ctl"][i] for i in ids]))
if MODE == "B":
    O = {}
    for a in ("ctl", "m3c"):
        O[a], miss = opus_rows(a)
        if miss: sys.exit(f"MISSING Opus units {a}: {len(miss)} {miss[:10]}")
    O4, miss4 = opus_rows("v4b")
    om, OL = metrics(O, "ctl", "m3c", ids)
    om["verdict"] = "PASS stands" if (om["dU"] >= 0.03 and om["dU_ci"][0] > 0) else "PASS does not stand"
    out["opus_m3c_vs_ctl"] = om; out["opus_length_views"] = length_views(O, OL)
    LH = {a: {i: label(H[a][i]) for i in ids} for a in ("ctl", "m3c")}
    UO = lambda D, k, xs: sum(0 if D[k][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
    out["opus_vs_haiku"] = {a: dict(U_opus=round(UO(O, a, ids), 4), U_haiku=round(UO(H, a, ids), 4), offset=round(UO(O, a, ids) - UO(H, a, ids), 4),
                                    offset_ci=ci(lambda xs: UO(O, a, xs) - UO(H, a, xs), ids),
                                    spearman_s=spearman([O[a][i]["s"] for i in ids], [H[a][i]["s"] for i in ids]),
                                    CE_agree=sum(OL[a][i]["CE"] == LH[a][i]["CE"] for i in ids),
                                    correct_agree=sum((O[a][i]["corr"] >= 4) == (H[a][i]["corr"] >= 4) for i in ids),
                                    n_reused=sum("min3cite-opus-main/out" not in O[a][i]["src"] for i in ids)) for a in ("ctl", "m3c")}
    spO = lambda k, i: 0 if O[k][i]["declined"] else O[k][i]["s"]
    out["opus_vs_haiku"]["spearman_item_delta"] = spearman([spO("m3c", i) - spO("ctl", i) for i in ids], [dh[i] for i in ids])
    out["opus_vs_haiku"]["dU_shift_opus_minus_haiku"] = round(om["dU"] - hm["dU"], 4)
    xs4 = [i for i in ids if i in O4]; O["v4b"] = O4
    if xs4:
        r4, _ = metrics(O, "v4b", "m3c", xs4); r4["note"] = f"report only: the {len(xs4)} items whose 4B answer already has an Opus row (no new 4B calls)"
        out["opus_m3c_vs_4b_partial_report_only"] = r4
json.dump(out, open(OUTF, "w"), indent=1); print(json.dumps(out, indent=1))
