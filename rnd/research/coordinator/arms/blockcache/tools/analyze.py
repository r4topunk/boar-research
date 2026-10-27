#!/usr/bin/env python3
"""BLOCKCACHE analysis (0 LLM). usage: analyze.py <replay out dir> <arm dir>
Reads <order>-<size>.blocklog.jsonl / .replay.jsonl (tools/run_replay.sh), the phone traces of aunion73-a and
PARTIME perq-aunion73-a.json; writes aggregates/blockcache-summary.json, perq-projection.json, parity.json."""
import json, os, sys
OUT, ARM = sys.argv[1], sys.argv[2]
B = "<workspace>"
PERQ = f"{B}/rnd/research/coordinator/arms/e1-partime/aggregates/perq-aunion73-a.json"
PHONE = f"{B}/handoff/pixel8-2026-10-20/bench/results/aunion73-a"
MS_PER_BLOCK = 16.0
# sensitivity: 16.0 = frozen (PARTIME block phase per FETCHED block); per decompression it is 16.0 / (replay misses / phone fetched rows); 8.0 = half (materialize not removed by a hit)
COSTS = [16.0, None, 8.0]
ORDERS, SIZES = ["S", "R1", "R2", "R3", "M"], ["16", "64", "256", "0"]
def pct(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
def load(o, s):
    L = [json.loads(l) for l in open(f"{OUT}/{o}-{s}.blocklog.jsonl")]
    R = [json.loads(l) for l in open(f"{OUT}/{o}-{s}.replay.jsonl")]
    # attribute searches to items: a marker equal to the next retrieving item's query starts that item
    items = [r for r in R if r.get("raw") is not None and r.get("query")]
    qi, cur, per = 0, None, {}
    for x in L:
        if x["e"] == "search":
            if qi < len(items) and x["query"] == items[qi]["query"]: cur = items[qi]["id"]; qi += 1
            per.setdefault(cur, {})
        elif x["e"] == "miss":
            p = x["pack"].replace("local-", ""); per.setdefault(cur, {}); per[cur][p] = per[cur].get(p, 0) + 1
    assert qi == len(items), (o, s, qi, len(items))
    misses = [x for x in L if x["e"] == "miss"]
    bypack = {}
    for x in misses: p = x["pack"].replace("local-", ""); bypack[p] = bypack.get(p, 0) + 1
    distinct = {}
    for x in misses: distinct.setdefault(x["pack"].replace("local-", ""), set()).add(x["id"])
    raw = {r["id"]: [(h["title"], h.get("section"), h.get("source")) for h in (r.get("raw") or [])] for r in R}
    return {"misses": len(misses), "by_pack": bypack, "distinct_blocks": {k: len(v) for k, v in distinct.items()},
            "peak_held_bytes": max([x["held"] for x in misses] or [0]), "searches": sum(1 for x in L if x["e"] == "search"),
            "per_item": per, "raw": raw}
D = {o: {s: load(o, s) for s in SIZES} for o in ORDERS}
# parity: ordered raw lists identical across sizes within each order (and S-16 vs the unpatched engine if present)
parity = {o: {s: sum(1 for i in D[o]["16"]["raw"] if D[o][s]["raw"][i] != D[o]["16"]["raw"][i]) for s in SIZES} for o in ORDERS}
up = f"{OUT}/S-unpatched.replay.jsonl"
if os.path.exists(up):
    U = {json.loads(l)["id"]: [(h["title"], h.get("section"), h.get("source")) for h in (json.loads(l).get("raw") or [])] for l in open(up)}
    parity["S16_vs_unpatched_engine_diffs"] = sum(1 for i in U if U[i] != D["S"]["16"]["raw"][i])
# phone validation: compressed blocks fetched per search (PARTIME rule) vs replay misses at 16, per question and pack
b = json.load(open(f"{PHONE}/bench.json")); rows = {json.loads(l)["queryId"]: json.loads(l)["query"] for l in open(f"{PHONE}/rows.jsonl") if l.strip()}
qid = {v: k for k, v in rows.items()}; phone = {}
for q in b["timeline"]:
    it = q["items"]; sw = [i for i in it if i.get("name") == "search-wikipacks"]
    if not sw: continue
    s0, s1 = sw[0]["t"] - sw[0]["ms"], sw[0]["t"]; d = {}
    for i in it:
        if i.get("name") == "sql" and (i.get("label") or "").startswith("boar-") and s0 <= i["t"] - i["ms"] <= s1 and "FROM blocks" in i["label"]:
            p = i["label"].split("|")[0]; d[p] = d.get(p, 0) + (i.get("n") or 0)
    phone[qid.get(q["query"])] = d
pv = [(sum(phone[k].values()), sum(D["S"]["16"]["per_item"].get(k, {}).values())) for k in phone if k in D["S"]["16"]["per_item"]]
valid = {"n_questions": len(pv), "phone_blocks_total": sum(a for a, _ in pv), "replay_misses16_total": sum(b_ for _, b_ in pv),
         "ratio_replay_over_phone": round(sum(b_ for _, b_ in pv) / max(1, sum(a for a, _ in pv)), 3),
         "phone_per_search_p50": pct([a for a, _ in pv], .5), "replay16_per_search_p50": pct([b_ for _, b_ in pv], .5)}
# projection on S (phone order), per question and pack: saved = (m16 - mX) * 16 ms
qs = json.load(open(PERQ)); proj = {}; perq_out = []
COSTS = [16.0, round(16.0 / valid["ratio_replay_over_phone"], 2), 8.0]
for cost in COSTS:
 for s in SIZES:
     T_ser, T_par, T_par0, saved_all = [], [], [], []
     for q in qs:
         if not q.get("packs"): T_ser.append(q["total_ms"]); T_par.append(q["total_ms"]); T_par0.append(q["total_ms"]); continue
         m16 = D["S"]["16"]["per_item"].get(q["queryId"], {}); mx = D["S"][s]["per_item"].get(q["queryId"], {})
         sv = {p: max(0.0, (m16.get(p, 0) - mx.get(p, 0)) * cost) for p in q["packs"]}
         # a pack window cannot lose more than its own JS time (clamp)
         sv = {p: min(sv[p], max(0.0, q["packs"][p]["js_ms"])) for p in sv}
         win = {p: q["packs"][p]["window_ms"] - sv[p] for p in q["packs"]}
         js = sum(max(0.0, q["packs"][p]["js_ms"] - sv[p]) for p in q["packs"])
         ser = sum(win.values()); par = max(js, max(win.values()))
         T_ser.append(q["total_ms"] - (q["search_ms"] - ser))
         T_par.append(q["total_ms"] - (q["search_ms"] - par))
         T_par0.append(q["total_ms"] - (q["search_ms"] - max(q["par_js_lb_ms"], 0)))
         saved_all.append(sum(sv.values()))
         if s == "256" and cost == 16.0: perq_out.append({"queryId": q["queryId"], "saved_ms": round(sum(sv.values())), "saved_by_pack": {p: round(v) for p, v in sv.items()}})
     proj[f"{s}@{cost}ms"] = {"T_p50_serial_s": round(pct(T_ser, .5) / 1000, 2), "T_p90_serial_s": round(pct(T_ser, .9) / 1000, 2),
                "T_p50_promiseall_s": round(pct(T_par, .5) / 1000, 2), "T_p90_promiseall_s": round(pct(T_par, .9) / 1000, 2),
                "saved_per_search_p50_ms": round(pct(saved_all, .5)), "saved_per_search_mean_ms": round(sum(saved_all) / len(saved_all))}
proj["baseline_promiseall_alone_p50_s"] = round(pct(T_par0, .5) / 1000, 2)
summ = {"ms_per_block_costs": COSTS, "validation_vs_phone": valid, "parity_raw_diffs_vs_16": parity, "projection_S": proj, "runs": {}}
for o in ORDERS:
    summ["runs"][o] = {}
    for s in SIZES:
        r = D[o][s]
        summ["runs"][o][s] = {"misses": r["misses"], "gain_vs_16": round(1 - r["misses"] / D[o]["16"]["misses"], 4), "searches": r["searches"],
                              "misses_per_search": round(r["misses"] / r["searches"], 1), "peak_held_MB": round(r["peak_held_bytes"] / 2**20, 2),
                              "extra_held_MB_vs_16": round((r["peak_held_bytes"] - D[o]["16"]["peak_held_bytes"]) / 2**20, 2),
                              "by_pack": r["by_pack"], "distinct_blocks": r["distinct_blocks"]}
gS = summ["runs"]["S"]["256"]["gain_vs_16"]; gR = sum(summ["runs"][o]["256"]["gain_vs_16"] for o in ["R1", "R2", "R3"]) / 3
xb = summ["runs"]["S"]["256"]["extra_held_MB_vs_16"]
summ["kill_at_256"] = {"gain_S": gS, "gain_shuffled_mean": round(gR, 4), "extra_MB": xb,
                       "fail_gain": gS < 0.30, "fail_bytes": xb > 32, "fail_order": gR < 0.5 * gS,
                       "parity_ok": all(v == 0 for o in ORDERS for v in parity[o].values())}
summ["kill_at_256"]["verdict"] = "CLOSED" if (summ["kill_at_256"]["fail_gain"] or summ["kill_at_256"]["fail_bytes"] or summ["kill_at_256"]["fail_order"]) else "GO"
os.makedirs(f"{ARM}/aggregates", exist_ok=True)
json.dump(summ, open(f"{ARM}/aggregates/blockcache-summary.json", "w"), indent=1)
json.dump(perq_out, open(f"{ARM}/aggregates/perq-projection-256.json", "w"), indent=1)
print(json.dumps({k: summ[k] for k in ["validation_vs_phone", "parity_raw_diffs_vs_16", "projection_S", "kill_at_256"]}, indent=1))
for o in ORDERS:
    for s in SIZES:
        r = summ["runs"][o][s]; print(o, s, r["misses"], r["gain_vs_16"], r["peak_held_MB"], r["extra_held_MB_vs_16"], r["by_pack"])
