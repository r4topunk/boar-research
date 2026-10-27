#!/usr/bin/env python3
"""OCCDECL stage-1 report (0 LLM). Usage: python3 -I report.py [--json out]
Per variant x pack set: GATE v2 line (from the run's gate2.txt/json), CE-unwarned, false refusals, U_cov; OCC routes; OCC tokens per call;
mini wall per answer (trace timing.totalMs) vs the mini control (lpctl-<K>-main + poolctl-<K>-st180) and vs the null-ws run (Qwen only, run
the same evening; reference for mini load); OCC tg rate (occPredictedTokens / occPredictedMs); projected Pixel decode per OCC call (criterion)."""
import json, statistics as st, sys, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; O = f"{A}/occdecl"; NC = f"{A}/null-cal"
ld = lambda p: {r["itemId"]: r for r in map(json.loads, open(p))} if os.path.exists(p) else {}
med = lambda xs: round(st.median(xs), 1) if xs else None
def pct(xs, q): xs = sorted(xs); return xs[int(q * (len(xs) - 1))] if xs else None
out = {}; tg = collections.defaultdict(list)
for V in "AB":
    for K in ("K0", "K1"):
        run = f"occdecl-{V}-{K}-screen2-{K}-s42"; tp = f"{O}/arms/occdecl-{V}/traces/{run}.traces.jsonl"
        if not os.path.exists(tp): continue
        c = ld(tp); ids = open(f"{NC}/pool/screen2-{K}.ids").read().split()
        k = {**ld(f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl"), **ld(f"{NC}/control/traces/poolctl-{K}-st180-s42.traces.jsonl")}
        nw = ld(f"{NC}/arms/null-ws/traces/null-ws-{K}-screen2-{K}-s42.traces.jsonl")
        occ = [json.loads(l) for l in open(f"{O}/sidecar/{run}.occ.jsonl")] if os.path.exists(f"{O}/sidecar/{run}.occ.jsonl") else []
        g = json.load(open(f"{O}/arms/occdecl-{V}/aggregates/{run}.gate2.json"))
        gl = open(f"{O}/arms/occdecl-{V}/aggregates/{run}.gate2.txt").read().strip()
        w = lambda T, xs: [T[i]["timing"]["totalMs"] for i in xs if i in T and not T[i].get("error")]
        oi = sorted({x["itemId"] for x in occ if x["route"].startswith("occ")})
        calls = [x for x in occ if x["route"].startswith("occ")]; tok = [x["occTokens"] for x in calls]
        ans = [x["occTokens"] for x in calls if x["route"] == "occ"]
        for x in calls:
            if x.get("occPredictedMs"): tg[V].append(x["occPredictedTokens"] / x["occPredictedMs"] * 1000)
        cw, kw, nww = med(w(c, ids)), med(w(k, ids)), med(w(nw, ids))
        r = dict(gate=gl, verdict=g["verdict"], net=g["net"], fixed_u=len(g["fixed_u"]), by_refusal=len(g["fixed_by_refusal"]), new_CEu=len(g["new_CEu"]),
                 CEu_ctl_cand=[g["ceu_ctl"], g["ceu_cand"]], false_ref=g["false_ref"], U_cov_delta=g["U_cov_delta"], U_cov_ci=g["U_cov_ci"], sent_worse=g["sent_worse"],
                 declines_ctl_cand=[g["declines_ctl"], g["declines_cand"]], routes=dict(collections.Counter(x["route"] for x in occ)),
                 occ_calls=len(calls), occ_tokens_all_median_p90_max=[med(tok), pct(tok, .9), max(tok) if tok else None], occ_tokens_answered_median=med(ans),
                 forced=sum(1 for x in calls if x.get("forced")),
                 wall_ms_median_all_cand_ctl_nullws=[cw, kw, nww], wall_ratio_vs_ctl=round(cw / kw, 2), wall_ratio_vs_nullws=round(cw / nww, 2) if nww else None,
                 latency_clause_le_1_5x=cw <= 1.5 * kw, wall_ms_median_occ_items_cand_ctl_nullws=[med(w(c, oi)), med(w(k, oi)), med(w(nw, oi))],
                 ctl_output_tokens_median_occ_items=med([k[i]["timing"]["outputTokens"] for i in oi if i in k and k[i]["timing"].get("outputTokens")]),
                 load1m_median_cand_ctl=[med([c[i]["runtime"].get("loadAvg1m", 0) for i in ids if i in c]), med([k[i]["runtime"].get("loadAvg1m", 0) for i in ids if i in k])])
        out[f"{V}-{K}"] = r
tgA, tgB = med(tg["A"]), med(tg["B"])
proj = {}
for V in "AB":
    toks = [v["occ_tokens_all_median_p90_max"][0] for kk, v in out.items() if kk.startswith(V)]
    if not toks or not tgA: continue
    t = st.median(toks); ratio = 1.0 if V == "A" else (tgB / tgA if tgB else None)
    if ratio: proj[V] = dict(median_occ_tokens=t, tg_ratio_vs_A=round(ratio, 2), pixel_s_at_12_16=[round(t / (12 * ratio), 1), round(t / (16 * ratio), 1)])
out["tg_mini_median_tok_s"] = dict(A=tgA, B=tgB); out["pixel_projection"] = proj
print(json.dumps(out, indent=1))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
