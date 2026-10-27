#!/usr/bin/env python3
"""0-LLM attribution of DEVICE-X6's native - phone raw gap (57 v0.1 ids, existing Haiku judgments) by pipeline stage.
Exact item decomposition: d_raw = sum_i (Sn_i / sum Rn - Sp_i / sum Rp); each item's term is summed inside its stage bucket.
Stage per item (first match): D = our phone answer came from a deterministic layer (instant tier, no generate: code);
then, for generated answers, his fact-in-context (FACTPRESENT rule on the X6-replica harness context, parity 69/73 titles) x ours
(RAG-FUNNEL K0 kept_present, used only where the K0 1.7B kept titles equal the phone cut 7 kept titles, else 'ours?')."""
import json, sys, importlib.util, collections
B = "<workspace>/"; ARM = B + "rnd/research/coordinator/arms/native-parity/"; X6 = B + "rnd/research/coordinator/arms/device-x6/"
spec = importlib.util.spec_from_file_location("ad", X6 + "tools/agg_device.py")
src = open(X6 + "tools/agg_device.py").read().split("P, D, N = sys.argv")[0]; ad = {}; exec(src, ad)
spec2 = importlib.util.spec_from_file_location("ag", ARM + "tools/agg.py")
agsrc = open(ARM + "tools/agg.py").read().split("# ---- his side ----")[0]; ag = {"__file__": ARM + "tools/agg.py"}; exec(agsrc, ag)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
N = ad["load"](X6 + "judgments/native-x6-v01.judgments.jsonl"); P = ad["load"](X6 + "judgments/phone-cut7-v01.judgments.jsonl")
ids = sorted(set(N) & set(P))
PT = {t["itemId"]: t for t in rd(X6 + "judgments/phone-cut7-v01.traces.jsonl")}
HX = {r["id"]: r for r in rd(ARM + "work/out/x6replica.jsonl")}
K0 = {t["itemId"]: t for t in rd(B + "rnd/research/coordinator/arms/litepacks/traces/lp-K0-v01-s42.traces.jsonl")}
FUN = json.load(open(B + "rnd/research/coordinator/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
RN = sum(N[i]["r"] for i in ids); RP = sum(P[i]["r"] for i in ids)
d_raw = sum(N[i]["s"] for i in ids) / RN - sum(P[i]["s"] for i in ids) / RP
buckets = collections.defaultdict(lambda: {"n": 0, "contrib": 0.0, "ids": [], "dS": []})
for i in ids:
    rc = PT[i]["route"]["reasonCodes"]; det = PT[i]["route"]["tier"] == "instant" and not any(c.startswith("generate:") for c in rc)
    h = HX[i]; his = ag["present"](i, h["kept"]) if i in FUN else None
    pk = [k["title"] for k in PT[i]["retrieval"]["kept"]]; kk = [k["title"] for k in K0[i]["retrieval"]["kept"]] if i in K0 else None
    ours = (FUN[i]["K0"]["kept_present"] if (i in FUN and kk == pk) else None)
    if det: b = "D our deterministic layer answered"
    elif i not in FUN: b = "G unkeyed (no fact rule)"
    else: b = f"G his_fact={'Y' if his else 'N'} ours_fact={'?' if ours is None else ('Y' if ours else 'N')}"
    c = N[i]["s"] / RN - P[i]["s"] / RP
    x = buckets[b]; x["n"] += 1; x["contrib"] += c; x["ids"].append(i); x["dS"].append(round(N[i]["s"] - P[i]["s"], 2))
out = {"n": len(ids), "d_raw_native_minus_phone": round(d_raw, 4),
       "buckets": {k: {"n": v["n"], "contrib": round(v["contrib"], 4), "mean_dS": round(sum(v["dS"]) / v["n"], 3), "ids": v["ids"]} for k, v in sorted(buckets.items())}}
json.dump(out, open(ARM + "aggregates/x6-attribution.json", "w"), indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "ids"} for k, v in out["buckets"].items()}, indent=0), out["d_raw_native_minus_phone"])
