"""DETFP M1-M3 (0 LLM): the 7 detector FPs on v0.2 in the cut 6 (= cut 7 on v0.2) two-seed claim runs. Script-only on blind:
reads traces (codes/outcome only) and Opus judgments (scores only); writes ids, codes, scores. Usage: python3 -I detfp_cost.py <out.json>"""
import json, sys
B = "<private held-out dir>"
IDS = "v02-reasoning-A02 v02-reasoning-A03 v02-reasoning-A06 v02-reasoning-A07 v02-reasoning-B01 v02-reasoning-B09 v02-crypto-B03".split()
K = ("correctness", "completeness", "usefulness")
out = {"layer": {}, "scores": {}}
b, r = {}, {}
for s in ("s42", "s43"):
    for l in open(f"{B}/cut6-v02-{s}.traces.jsonl"):
        t = json.loads(l)
        if t["itemId"] not in IDS: continue
        d = [e for e in t["events"] if e.get("type") == "done"]
        rc = (d[-1].get("receipt") or {}) if d else {}
        codes = rc.get("reasonCodes") or t["route"].get("reasonCodes") or []
        out["layer"].setdefault(t["itemId"], {})[s] = {"outcome": t["route"].get("outcome"), "modelId": rc.get("modelId"),
            "codes": [c for c in codes if c.startswith(("detector", "grounding:health", "answer:", "healthgap", "numguard"))]}
    J = [json.loads(l) for l in open(f"{B}/cut6-v02-{s}.judgments.jsonl")]
    assert all(j["judgeModel"] == "claude-opus-5-5" for j in J if j.get("ok")), "non-Opus row"
    for j in J:
        if not j.get("ok"): continue
        m = j["mapped"]; b.setdefault(j["queryId"], []).append(sum(m["boar"][k] for k in K) / 3); r.setdefault(j["queryId"], []).append(sum(m["ref"][k] for k in K) / 3)
items = sorted(b); assert len(items) == 110, len(items)
bi = {i: sum(b[i]) / len(b[i]) for i in items}; ri = {i: sum(r[i]) / len(r[i]) for i in items}
raw = sum(bi.values()) / sum(ri.values()); mb = sum(bi.values()) / 110
si = {i: bi[i] / ri[i] for i in items}; ms = sum(si.values()) / 110
C = sum(mb - bi[i] for i in IDS) / sum(ri.values()); C2 = sum(ms - si[i] for i in IDS) / 110
others = [i for i in items if i not in IDS]
out["scores"] = {i: {"b_s42_s43": b[i], "b": round(bi[i], 3), "r": round(ri[i], 3), "ratio": round(si[i], 3)} for i in IDS}
out["summary"] = {"n": 110, "seeds_per_item_min": min(len(b[i]) for i in items), "raw_ratio_claim": round(raw, 4), "mean_b_110": round(mb, 3),
    "mean_b_7": round(sum(bi[i] for i in IDS) / 7, 3), "mean_b_103": round(sum(bi[i] for i in others) / 103, 3), "mean_r_7": round(sum(ri[i] for i in IDS) / 7, 3),
    "ceiling_ratio_exact": round(C, 4), "ceiling_per_item_ratio": round(C2, 4), "raw_if_7_at_mean": round(raw + C, 4)}
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))
