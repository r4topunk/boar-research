#!/usr/bin/env python3
"""LITETHINK aggregation (0 LLM). Estimator = packs-l2/tools/l2_agg.py (load/setstats/paired unchanged), as lite5/tools/agg_180.py.
Arms: T512, T256 (runs/litethink-t<B>-st20-<pack>-s42.judgments.haiku55-low.jsonl) vs NT = LITE5-180 ON Haiku rows on the 20 selftest20 ids.
Split = LITE6 bucket (thin / invented / rest). Writes aggregates/litethink.json; prints table + frozen verdicts (LITETHINK-criterion.md)."""
import json, os, statistics as st, glob
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/litethink"; R5 = f"{A}/lite5/runs/180"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
ids = [l.strip() for l in open(f"{A}/lite2/selftest20.ids") if l.strip()]
BUD = [b for b in (512, 256) if all(os.path.exists(f"{H}/runs/litethink-t{b}-st20-{p}-s42.judgments.haiku55-low.jsonl") for p in SE + TOPIC)]
J = {"NT": {}}; TR = {"NT": {}}
for p in SE + TOPIC:
    J["NT"].update({q: v for q, v in load(f"{R5}/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl").items() if q in ids})
    for l in open(f"{R5}/lite5-180-on-{p}-s42.traces.jsonl"):
        t = json.loads(l)
        if t["itemId"] in ids: TR["NT"][t["itemId"]] = t
    for b in BUD:
        J.setdefault(f"T{b}", {}).update(load(f"{H}/runs/litethink-t{b}-st20-{p}-s42.judgments.haiku55-low.jsonl"))
        for l in open(f"{H}/runs/litethink-t{b}-st20-{p}-s42.traces.jsonl"):
            t = json.loads(l); TR.setdefault(f"T{b}", {})[t["itemId"]] = t
for k in J: assert set(J[k]) == set(ids), (k, len(J[k]))
L6 = {x["id"]: x for x in json.load(open(f"{A}/lite6/aggregates/lite6.json"))["items"]}
buck = {q: (L6[q].get("bucket") if L6[q].get("bucket") in ("thin", "invented") else "rest") for q in ids}
def tstats(k, B=None):
    T = TR[k]; r = [T[q]["timing"].get("reasoningTokens") or 0 for q in ids]; tot = [T[q]["timing"]["totalMs"] / 1000 for q in ids]
    tt = [(T[q]["timing"].get("ttftMs") or 0) / 1000 for q in ids]; w = [len((T[q]["answer"].get("text", "") if isinstance(T[q]["answer"], dict) else "").split()) for q in ids]
    rs = sorted(r); o = {"reasoning_p50": st.median(r), "reasoning_p90": rs[int(0.9 * (len(rs) - 1))], "reasoning_max": max(r), "reasoning_zero": sum(x == 0 for x in r),
         "total_p50_s": round(st.median(tot), 2), "ttft_p50_s": round(st.median(tt), 2), "answer_words_p50": st.median(w), "prompt_p50": st.median(T[q]["timing"].get("promptTokens") or 0 for q in ids)}
    if B: o["budget_hit_share"] = round(sum(x >= B - 8 for x in r) / len(r), 3)
    return o
out = {"criterion_sha256": open(f"{H}/LITETHINK-criterion.sha256").read().split()[0], "n": len(ids), "judge": "claude-haiku-5-5 effort low, N=4 shards, both orders",
       "estimator": "l2_agg.py per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId", "stats": {k: setstats(J[k], ids) for k in J},
       "timing": {"NT": tstats("NT"), **{f"T{b}": tstats(f"T{b}", b) for b in BUD}}, "paired": {}, "split": {}, "verdict": {}, "per_item": {}}
cap = 2 * out["timing"]["NT"]["total_p50_s"]
for b in BUD:
    k = f"T{b}"; pr = paired(J[k], J["NT"], ids); out["paired"][f"{k}-NT"] = pr
    out["split"][k] = {g: paired(J[k], J["NT"], [q for q in ids if buck[q] == g]) for g in ("thin", "invented", "rest") if any(buck[q] == g for q in ids)}
    d, lo = pr["d_raw"], pr["d_raw_ci"][0]; tok = out["timing"][k]["total_p50_s"] <= cap
    out["verdict"][k] = "LEVER-shaped (Haiku, dev)" if d >= 0.03 and lo > 0 and tok else "DIRECTION" if d >= 0.03 else "FLAT" if d > -0.03 else "NEGATIVE"
if len(BUD) == 2: out["paired"]["T512-T256"] = paired(J["T512"], J["T256"], ids)
for q in ids:
    out["per_item"][q] = {"bucket": buck[q], **{k: round(J[k][q]["s"] - J[k][q]["r"], 3) for k in J}, **{f"r{k}": TR[k][q]["timing"].get("reasoningTokens") or 0 for k in TR},
                          **{f"ans{k}": (TR[k][q]["answer"].get("text", "") if isinstance(TR[k][q]["answer"], dict) else "")[:160] for k in TR}}
json.dump(out, open(f"{H}/aggregates/litethink.json", "w"), indent=1)
for k, v in out["stats"].items(): print(k, v["raw"], v["raw_ci"], "wtl", v["win_tie_loss"], out["timing"][k])
for c, pr in out["paired"].items(): print(c, pr)
for k, s in out["split"].items(): print(k, {g: (x["n"], x["d_raw"], x["d_raw_ci"]) for g, x in s.items()})
print("VERDICT", out["verdict"], "time cap", cap)
