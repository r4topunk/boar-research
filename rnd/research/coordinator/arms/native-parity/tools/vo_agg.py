#!/usr/bin/env python3
"""VITAL-ONOFF aggregation (0 LLM). Estimator = arms/device-x6/tools/agg_device.py (as s3_agg.py), 51 CV5 ids, B 2000 seed 11.
N-DV rows: judged divergent ids; non-divergent ids inherit the N-D rows. CE = LITEPACKS rule (non-declined, correctness mean of orders <= 1.5)."""
import json, statistics, re, collections
A = "<workspace>/rnd/research/coordinator/arms/"; ARM = A + "native-parity/"
src = open(A + "device-x6/tools/agg_device.py").read().split("P, D, N = sys.argv")[0]; ad = {}; exec(src, ad)
ids = open(ARM + "cv5-51.ids").read().split(); div = open(ARM + "runs/vo-divergent.ids").read().split()
FND = ARM + "judgments/native-N-D-v01-s42.judgments.jsonl"; FDV = ARM + "judgments/native-N-DV-v01-s42.judgments.jsonl"
ND = ad["load"](FND); DVj = ad["load"](FDV)
DV = {i: (DVj[i] if i in div else ND[i]) for i in ids if (i in DVj or i not in div)}
assert all(i in DV for i in ids) and all(i in ND for i in ids), "incomplete rows"
def corr(path):
    c = collections.defaultdict(list)
    for l in open(path):
        r = json.loads(l)
        if r.get("ok"): c[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
    return {q: sum(v) / len(v) for q, v in c.items()}
cND = corr(FND); cDVj = corr(FDV); cDV = {i: (cDVj[i] if i in div else cND[i]) for i in ids}
gen = {a: {r["id"]: r for r in map(json.loads, open(ARM + f)) if r["arm"] == a} for a, f in [("N-D", "runs/s3-gen.jsonl"), ("N-DV", "runs/vo-gen.jsonl")]}
MODEL_DECLINE = re.compile(r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer"
    r"|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)
decl = lambda t: t == "" or (len(t) < 300 and bool(MODEL_DECLINE.search(t)))
ce = {a: {i: (not decl(gen[a][i]["text"])) and c[i] <= 1.5 for i in ids} for a, c in [("N-D", cND), ("N-DV", cDV)]}
health = [i for i in ids if i.startswith(("lan-hlt", "vit-hlt"))]
new_health_ce = [i for i in health if ce["N-DV"][i] and not ce["N-D"][i]]
prom = {r["id"]: r for r in map(json.loads, open(ARM + "work/vo-prompts.jsonl"))}
s3p = {r["id"]: r for r in map(json.loads, open(ARM + "work/s3-prompts.jsonl")) if r["arm"] == "N-D"}
out = {"criterion_sha256": open(ARM + "VITAL-ONOFF-criterion.sha256").read().split()[0], "n_ids": len(ids), "divergent": len(div), "divergent_ids": div,
       "kept_on": {"N-D": sum(bool(s3p[i]["kept"]) for i in ids), "N-DV": sum(bool(prom[i]["kept"]) for i in ids)},
       "kept_titles_N-DV": {i: [k["title"] for k in prom[i]["kept"]] for i in ids if prom[i]["kept"]},
       "prompt_tokens_p50": {"N-D": statistics.median(s3p[i]["promptTokens"] for i in ids), "N-DV": statistics.median(prom[i]["promptTokens"] for i in ids)},
       "identical_prompt_but_text_differs": [i for i in ids if prom[i]["prompt"] == s3p[i]["prompt"] and i in div]}
out["sets"] = {"N-D": ad["setstats"](ND, ids), "N-DV": ad["setstats"](DV, ids)}
out["paired_NDV_minus_ND"] = ad["paired"](DV, ND, ids)
out["paired_divergent_only"] = ad["paired"](DV, ND, div) if len(div) >= 2 else None
kept_div = [i for i in div if prom[i]["kept"]]
out["gen"] = {a: {"n": len(ids), "nonempty": sum(bool(gen[a][i]["text"]) for i in ids), "tokens_p50": statistics.median(gen[a][i]["tokens_predicted"] for i in ids),
                  "at_cap": sum(bool(gen[a][i]["stopped_limit"]) for i in ids), "chars_p50": statistics.median(len(gen[a][i]["text"]) for i in ids)} for a in gen}
out["ce_per_100"] = {a: round(100 * sum(ce[a].values()) / len(ids), 1) for a in ce}
out["ce_counts"] = {a: sum(ce[a].values()) for a in ce}
out["health"] = {i: {"kept": [k["title"] for k in prom[i]["kept"]], "ce_ND": ce["N-D"][i], "ce_NDV": ce["N-DV"][i], "corr_ND": cND[i], "corr_NDV": cDV[i],
                     "s_ND": round(ND[i]["s"], 3), "s_NDV": round(DV[i]["s"], 3)} for i in health}
out["new_health_ce"] = new_health_ce
lo, hi = out["paired_NDV_minus_ND"]["d_raw_ci"]
out["valid"] = out["gen"]["N-DV"]["nonempty"] >= 49 and all(i in DVj for i in div)
out["verdict"] = "INVALID" if not out["valid"] else ("GAIN" if lo > 0 and not new_health_ce else ("HARM" if hi < 0 else "NEUTRAL"))
json.dump(out, open(ARM + "aggregates/vital-onoff.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("kept_titles_N-DV",)}, indent=1))
