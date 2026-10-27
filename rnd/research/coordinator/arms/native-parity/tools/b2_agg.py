#!/usr/bin/env python3
"""B2-HARNESS-17S aggregation (0 LLM). Estimator = arms/device-x6/tools/agg_device.py (B 2000 seed 11), 51 CV5 ids.
Per 100: correct = mean correctness over both orders >= 4; CE = <= 1.5 (ship15b_analyze.py thresholds; no declines in native arms)."""
import json, statistics, collections
A = "<workspace>/rnd/research/coordinator/arms/"; ARM = A + "native-parity/"
src = open(A + "device-x6/tools/agg_device.py").read().split("P, D, N = sys.argv")[0]; ad = {}; exec(src, ad)
ids = open(ARM + "cv5-51.ids").read().split()
def corr(p):
    J = collections.defaultdict(list)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
    return {q: sum(v) / len(v) for q, v in J.items()}
F = {"N-17S": ARM + "judgments/native-N-17S-v01-s42.judgments.jsonl", "N-S": ARM + "judgments/native-N-S-v01-s42.judgments.jsonl",
     "N-D": ARM + "judgments/native-N-D-v01-s42.judgments.jsonl", "ours17_K0": A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl",
     "ours17_K1_succinct": A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl", "CB17": A + "cb17/judgments/cb17-main-s42-v01.judgments.jsonl"}
L = {k: ad["load"](p) for k, p in F.items()}
out = {"judge": "Haiku 5.5-low judge.v1-low, both orders", "ids": len(ids), "files": F, "sets": {}, "paired": {}}
for k, d in L.items():
    c = [i for i in ids if i in d]
    if len(c) < 45: out["sets"][k] = {"n": len(c), "skipped": True}; continue
    s = ad["setstats"](d, c); cr = corr(F[k])
    s["correct_per100"] = round(100 * sum(cr[q] >= 4 for q in c) / len(c), 1); s["ce_per100"] = round(100 * sum(cr[q] <= 1.5 for q in c) / len(c), 1)
    out["sets"][k] = s
for a, b in [("N-17S", "N-S"), ("N-17S", "N-D"), ("N-S", "N-D"), ("ours17_K0", "N-17S"), ("CB17", "N-17S"), ("ours17_K1_succinct", "N-17S")]:
    c = [i for i in ids if i in L[a] and i in L[b]]
    if len(c) >= 45: out["paired"][f"{a} - {b}"] = ad["paired"](L[a], L[b], c)
c = ids; ca, cb = corr(F["N-17S"]), corr(F["N-S"])
out["d_ce_per100_17S_minus_S"] = round(100 * (sum(ca[q] <= 1.5 for q in c) - sum(cb[q] <= 1.5 for q in c)) / len(c), 1)
gen = [json.loads(l) for l in open(ARM + "runs/b2-gen.jsonl")] ; g3 = [json.loads(l) for l in open(ARM + "runs/s3-gen.jsonl")]
out["gen"] = {"N-17S": {"n": len(gen), "nonempty": sum(bool(r["text"]) for r in gen), "think": sum("<think>" in r["text"] for r in gen),
                        "at_cap": sum(bool(r["stopped_limit"]) for r in gen), "tokens_p50": statistics.median(r["tokens_predicted"] for r in gen),
                        "chars_p50": statistics.median(len(r["text"]) for r in gen)},
              "N-S": {"tokens_p50": statistics.median(r["tokens_predicted"] for r in g3 if r["arm"] == "N-S"),
                      "chars_p50": statistics.median(len(r["text"]) for r in g3 if r["arm"] == "N-S")}}
p = out["paired"]["N-17S - N-S"]; d, lo = p["d_above_min"], p["d_above_min_ci"][0]
out["valid"] = bool(out["gen"]["N-17S"]["nonempty"] >= 49 and out["gen"]["N-17S"]["think"] == 0 and len([i for i in ids if i in L["N-17S"]]) == 51)
out["verdict_haiku"] = "PASS" if d >= 0.05 and lo > 0 else "FAIL"
out["opus_trigger"] = bool(0.02 <= d <= 0.08)
json.dump(out, open(ARM + "aggregates/B2-HARNESS-17S.json", "w"), indent=1); print(json.dumps(out, indent=1))
