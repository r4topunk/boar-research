#!/usr/bin/env python3
"""Frozen prediction for the E1-PAR blockcache run (arm D) from the replay of the 11-question e1par order. 0 LLM.
usage: predict_e1par.py <replay out dir> <arm dir>"""
import json, sys
OUT, ARM = sys.argv[1], sys.argv[2]
PERQ = "<workspace>/rnd/research/coordinator/arms/e1-partime/aggregates/perq-aunion73-a.json"
def pct(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
def per_item(o, s):
    L = [json.loads(l) for l in open(f"{OUT}/{o}-{s}.blocklog.jsonl")]; R = [json.loads(l) for l in open(f"{OUT}/{o}-{s}.replay.jsonl")]
    items = [r for r in R if r.get("raw") is not None and r.get("query")]; qi, cur, per = 0, None, {}
    for x in L:
        if x["e"] == "search":
            if qi < len(items) and x["query"] == items[qi]["query"]: cur = items[qi]["id"]; qi += 1
        elif x["e"] == "miss":
            p = x["pack"].replace("local-", ""); per.setdefault(cur, {}); per[cur][p] = per[cur].get(p, 0) + 1
    return per, sum(1 for x in L if x["e"] == "miss"), {r["id"]: [h["title"] for h in r.get("raw") or []] for r in R}
m16, n16, r16 = per_item("E", "16"); m256, n256, r256 = per_item("E", "256")
assert r16 == r256
qs = {q["queryId"]: q for q in json.load(open(PERQ))}
ids = [json.loads(l)["id"] for l in open(f"{OUT}/../q/E.jsonl")][1:] if False else None
res = {"misses_16": n16, "misses_256": n256, "gain": round(1 - n256 / n16, 3), "raw_identical": True}
for cost in (16.0, 12.5, 8.0):
    sA, sB, sD, sDs, tA, tB, tD = [], [], [], [], [], [], []
    for qid, q in qs.items():
        if qid not in m16 or not q.get("packs"): continue
        sv = {p: min(max(0.0, (m16[qid].get(p, 0) - m256.get(qid, {}).get(p, 0)) * cost), max(0.0, q["packs"][p]["js_ms"])) for p in q["packs"]}
        win = {p: q["packs"][p]["window_ms"] - sv[p] for p in q["packs"]}
        js = sum(max(0.0, q["packs"][p]["js_ms"] - sv[p]) for p in q["packs"])
        a = q["search_ms"]; b = q["par_js_lb_ms"]; d = max(js, max(win.values())); ds = sum(win.values())
        sA.append(a); sB.append(b); sD.append(d); sDs.append(ds)
        tA.append(q["total_ms"]); tB.append(q["total_ms"] - (a - b)); tD.append(q["total_ms"] - (a - d))
    res[f"{cost}ms"] = {"n": len(sA), "A_search_p50_s": round(pct(sA, .5) / 1000, 2), "B_search_p50_s": round(pct(sB, .5) / 1000, 2),
                        "D_search_p50_s": round(pct(sD, .5) / 1000, 2), "D_serial_search_p50_s": round(pct(sDs, .5) / 1000, 2),
                        "A_answer_p50_s": round(pct(tA, .5) / 1000, 2), "B_answer_p50_s": round(pct(tB, .5) / 1000, 2), "D_answer_p50_s": round(pct(tD, .5) / 1000, 2)}
json.dump(res, open(f"{ARM}/aggregates/e1par-d-prediction.json", "w"), indent=1); print(json.dumps(res, indent=1))
