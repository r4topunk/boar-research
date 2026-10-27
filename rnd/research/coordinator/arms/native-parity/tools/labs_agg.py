#!/usr/bin/env python3
"""RC1-LABS aggregation (0 LLM). Estimator = arms/device-x6/tools/agg_device.py (as vo_agg.py), 51 CV5 ids, B 2000 seed 11.
N-DL rows: judged changed (tool-answered) ids; other ids inherit the N-D rows. CE = LITEPACKS rule (non-declined, correctness mean <= 1.5)."""
import json, re, collections
A = "<workspace>/rnd/research/coordinator/arms/"; ARM = A + "native-parity/"
src = open(A + "device-x6/tools/agg_device.py").read().split("P, D, N = sys.argv")[0]; ad = {}; exec(src, ad)
ids = open(ARM + "cv5-51.ids").read().split(); ch = open(ARM + "runs/labs-changed.ids").read().split()
FND = ARM + "judgments/native-N-D-v01-s42.judgments.jsonl"; FDL = ARM + "judgments/native-N-DL-v01-s42.judgments.jsonl"
ND = ad["load"](FND); DLj = ad["load"](FDL)
DL = {i: (DLj[i] if i in ch else ND[i]) for i in ids if (i in DLj or i not in ch)}
assert all(i in DL for i in ids) and all(i in ND for i in ids), "incomplete rows"
def corr(path):
    c = collections.defaultdict(list)
    for l in open(path):
        r = json.loads(l)
        if r.get("ok"): c[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
    return {q: sum(v) / len(v) for q, v in c.items()}
cND = corr(FND); cDLj = corr(FDL); cDL = {i: (cDLj[i] if i in ch else cND[i]) for i in ids}
nd = {r["id"]: r["text"] for r in map(json.loads, open(ARM + "runs/s3-gen.jsonl")) if r["arm"] == "N-D"}
tl = {r["id"]: r for r in map(json.loads, open(ARM + "runs/rc1-labs-tools.jsonl"))}
txt = {"N-D": nd, "N-DL": {i: (tl[i]["text"] if tl[i]["lab"] else nd[i]) for i in ids}}
MODEL_DECLINE = re.compile(r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer"
    r"|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)
decl = lambda t: t == "" or (len(t) < 300 and bool(MODEL_DECLINE.search(t)))
ce = {a: {i: (not decl(txt[a][i])) and c[i] <= 1.5 for i in ids} for a, c in [("N-D", cND), ("N-DL", cDL)]}
health = [i for i in ids if i.startswith(("lan-hlt", "vit-hlt"))]
B1 = ["lan-cmp-001", "lan-exp-006", "lan-ref-001", "lan-ref-004", "lan-ref-005", "lan-rsn-002", "lan-rsn-007", "trv-002"]
ours = {r["itemId"]: r["answer"]["text"] for r in map(json.loads, open("<workspace>/boar-eval/runs/device-pixel8a/final-cut7-v01/traces.jsonl"))}
out = {"criterion_sha256": open(ARM + "RC1-LABS-criterion.sha256").read().split()[0], "tag": "v2.0.0-rc1 (46be7377)", "n_ids": len(ids),
       "facts_table": {"file": "lab_facts_facts_v1.json", "build": "r10", "sha256": "307753ffb80d2ec67088bcdb5ed4b9e7f8170b8d6117c0a3ecf5fd20d9c421f0", "entities": 4233},
       "slot_order": ["cohazard", "polyglot", "calc", "distance", "facts"], "fired": len(ch),
       "by_lab": dict(collections.Counter(tl[i]["lab"] for i in ch)), "throws": [i for i in ids if any(isinstance(v, str) and v.startswith("THROW") for v in tl[i]["perLab"].values())]}
out["tool_items"] = {i: {"lab": tl[i]["lab"], "tool": tl[i]["tool"], "corr_ND": round(cND[i], 2), "corr_NDL": round(cDL[i], 2), "s_ND": round(ND[i]["s"], 3),
                         "s_NDL": round(DL[i]["s"], 3), "right": cDL[i] >= 4, "ce_NDL": ce["N-DL"][i], "ce_ND": ce["N-D"][i],
                         "in_B1": i in B1, "text_equals_our_layer": tl[i]["text"] == ours.get(i)} for i in ch}
out["sets"] = {"N-D": ad["setstats"](ND, ids), "N-DL": ad["setstats"](DL, ids)}
out["paired_NDL_minus_ND"] = ad["paired"](DL, ND, ids)
out["paired_changed_only"] = ad["paired"](DL, ND, ch) if len(ch) >= 2 else None
out["ce_per_100"] = {a: round(100 * sum(ce[a].values()) / len(ids), 1) for a in ce}; out["ce_counts"] = {a: sum(ce[a].values()) for a in ce}
out["health_worse"] = [i for i in health if DL[i]["s"] < ND[i]["s"]]
out["B1"] = {"ids": B1, "answered_by_facts": sum(tl[i]["lab"] == "facts" for i in B1), "right": sum(tl[i]["lab"] == "facts" and cDL[i] >= 4 for i in B1),
             "text_identical_to_ours": sum(tl[i]["text"] == ours.get(i) for i in B1)}
out["determinism_check"] = {"ids": ["vit-hum-001", "vit-hum-002", "vit-hum-003"], "prompt_identical": 3, "text_identical_macbook_vs_mini": 0,
                            "note": "prompts byte-identical to step-3 N-D; MacBook CPU generation diverges from the mini after 8-165 chars (hardware, not pipeline); non-fired items inherit the mini N-D answers"}
d = out["paired_NDL_minus_ND"]
out["predictions"] = {"fires_6_10": 6 <= len(ch) <= 10, "U_rise_0.03_0.10": bool(0.03 <= d["d_above_min"] <= 0.10), "no_health_worse": not out["health_worse"], "U_delta_observed": d["d_above_min"]}
out["valid"] = all(i in DLj for i in ch)
json.dump(out, open(ARM + "aggregates/rc1-labs.json", "w"), indent=1)
print(json.dumps(out, indent=1))
