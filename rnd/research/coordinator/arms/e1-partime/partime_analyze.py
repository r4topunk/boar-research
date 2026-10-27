#!/usr/bin/env python3
"""E1 PARTIME: replay-only estimate of parallel / bounded pack search on the Pixel 8a traces (0 LLM, 0 judge).
usage: partime_analyze.py <results_dir> <out_dir>   (reads aunion73-a and q17b73-a: rows.jsonl + bench.json timeline)
Span 't' is the END time (ms from question t0); start = t - ms. Pack window segmentation: pack i runs from the start
of its first sql span (pack 1: start of search-wikipacks) to the start of pack i+1's first sql span (last pack: end of
search-wikipacks). SQL_p = sum of that pack's sql spans (sequential awaits). JS_p = window_p - SQL_p (fzstd block
decompress, stemming, scoring on the single JS thread; it cannot overlap under Promise.all on one JS runtime)."""
import json, os, sys, statistics as st

def pct(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def lanes(ws, n):
    l = [0.0] * n
    for w in sorted(ws, reverse=True): l[l.index(min(l))] += w
    return max(l)

def per_question(q):
    it = q["items"]; r = {}
    sw = [i for i in it if i.get("name") == "search-wikipacks"]
    rt = [i for i in it if i.get("kind") == "retrieve"]
    r["retrieve_ms"] = sum(i["ms"] for i in rt)
    r["prefill_ms"] = sum((i.get("extra") or {}).get("promptMs") or 0 for i in it if i.get("name") == "llm-completion")
    r["decode_ms"] = sum((i.get("extra") or {}).get("predictedMs") or 0 for i in it if i.get("name") == "llm-completion")
    r["promptN"] = sum((i.get("extra") or {}).get("promptN") or 0 for i in it if i.get("name") == "llm-completion")
    r["cacheN"] = sum((i.get("extra") or {}).get("cacheN") or 0 for i in it if i.get("name") == "llm-completion")
    r["llm_init_ms"] = sum(i["ms"] for i in it if i.get("name") == "llm-init")
    r["llm_calls"] = sum(1 for i in it if i.get("name") == "llm-completion")
    if not sw: r["packs"] = None; return r
    s = sw[0]; s0, s1 = s["t"] - s["ms"], s["t"]
    sql = [i for i in it if i.get("name") == "sql" and s0 <= i["t"] - i["ms"] and i["t"] <= s1 + 1
           and (i.get("label") or "").split("|")[0].startswith("boar-")]
    order, first, sqlms = [], {}, {}
    for i in sql:
        db = i["label"].split("|")[0].replace(".sqlite", "")
        if db not in first: first[db] = i["t"] - i["ms"]; order.append(db)
        sqlms[db] = sqlms.get(db, 0) + i["ms"]
    packs = {}
    for k, db in enumerate(order):
        a = s0 if k == 0 else first[db]; b = first[order[k + 1]] if k + 1 < len(order) else s1
        packs[db] = {"window_ms": round(b - a, 1), "sql_ms": round(sqlms[db], 1), "js_ms": round(b - a - sqlms[db], 1)}
    r["packs"] = packs; r["search_ms"] = s["ms"]; r["order"] = order
    ws = [p["window_ms"] for p in packs.values()]; js = sum(p["js_ms"] for p in packs.values())
    r["serial_ms"] = sum(ws)
    r["par_ideal_ms"] = max(ws)                                    # every pack on its own thread (JS too)
    r["par_js_lb_ms"] = max(js, max(ws))                           # Promise.all, native SQL concurrent, JS serial: lower bound
    r["par_js_ub_ms"] = js + max(p["sql_ms"] for p in packs.values())  # same, no SQL/JS overlap on the longest pack
    r["two_ideal_ms"] = lanes(ws, 2)
    r["two_js_ms"] = max(js, lanes(ws, 2))
    r["js_total_ms"] = js
    return r

def run(results, name):
    rows = {json.loads(l)["query"]: json.loads(l) for l in open(os.path.join(results, name, "rows.jsonl")) if l.strip()}
    tl = json.load(open(os.path.join(results, name, "bench.json")))["timeline"]
    out = []
    for q in tl:
        row = rows[q["query"]]; d = per_question(q)
        d["queryId"] = row["queryId"]; d["total_ms"] = row["totalLatencyMs"]; d["ttft_ms"] = row.get("ttftMs")
        out.append(d)
    return out

def project(qs, field):
    """new total = total - (search_ms - field); rows without pack search unchanged."""
    return [q["total_ms"] - ((q["search_ms"] - q[field]) if q.get("packs") else 0) for q in qs]

if __name__ == "__main__" and sys.argv[1] not in ("--extra", "--drop"):
    res, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    agg = {}
    for name in ["aunion73-a", "q17b73-a"]:
        qs = run(res, name); json.dump(qs, open(os.path.join(outd, f"perq-{name}.json"), "w"), indent=0)
        P = [q for q in qs if q.get("packs")]
        packs = sorted({p for q in P for p in q["packs"]})
        dist = {}
        for p in packs:
            w = [q["packs"][p]["window_ms"] for q in P if p in q["packs"]]
            s = [q["packs"][p]["sql_ms"] for q in P if p in q["packs"]]
            dist[p] = {"n": len(w), "window_p50": round(pct(w, .5)), "window_p90": round(pct(w, .9)), "window_max": round(max(w)),
                       "window_sum_s": round(sum(w) / 1000, 1), "sql_share": round(sum(s) / sum(w), 2)}
        tot = [q["total_ms"] for q in qs]
        a = {"n_rows": len(qs), "n_pack_search": len(P), "per_pack": dist,
             "search_p50": round(pct([q["search_ms"] for q in P], .5)), "retrieve_p50": round(pct([q["retrieve_ms"] for q in P], .5)),
             "js_share_of_search": round(sum(q["js_total_ms"] for q in P) / sum(q["serial_ms"] for q in P), 3),
             "answer_p50_s": round(pct(tot, .5) / 1000, 2), "answer_p90_s": round(pct(tot, .9) / 1000, 2)}
        for f in ["serial_ms", "par_ideal_ms", "par_js_lb_ms", "par_js_ub_ms", "two_ideal_ms", "two_js_ms"]:
            a[f + "_p50"] = round(pct([q[f] for q in P], .5)); a[f + "_mean"] = round(st.mean(q[f] for q in P))
            if f != "serial_ms":
                pr = project(qs, f); a["T_p50_" + f.replace("_ms", "")] = round(pct(pr, .5) / 1000, 2)
                a["T_p90_" + f.replace("_ms", "")] = round(pct(pr, .9) / 1000, 2)
        # time budget over all 73 answers (sum) and over generating rows
        G = [q for q in qs if q["llm_calls"]]
        def share(sel):
            T = sum(q["total_ms"] for q in sel); R = sum(q["retrieve_ms"] for q in sel)
            Pf = sum(q["prefill_ms"] for q in sel); D = sum(q["decode_ms"] for q in sel); I = sum(q["llm_init_ms"] for q in sel)
            return {"n": len(sel), "total_s": round(T / 1000, 1), "retrieval": round(R / T, 3), "prefill": round(Pf / T, 3),
                    "decode": round(D / T, 3), "llm_init": round(I / T, 3), "other": round(1 - (R + Pf + D + I) / T, 3)}
        a["budget_all"] = share(qs); a["budget_generating"] = share(G)
        mid = sorted(qs, key=lambda q: q["total_ms"])[len(qs) // 2 - 7: len(qs) // 2 + 8]
        a["budget_p50_band15"] = share(mid)
        a["band15_llm_rows"] = sum(1 for q in mid if q["llm_calls"])
        a["gen_promptN_p50"] = pct([q["promptN"] for q in G], .5); a["gen_cacheN_p50"] = pct([q["cacheN"] for q in G], .5)
        a["gen_prefill_ms_p50"] = round(pct([q["prefill_ms"] for q in G], .5)); a["gen_decode_ms_p50"] = round(pct([q["decode_ms"] for q in G], .5))
        # (c) prefill ceilings: all prefill removed (hard ceiling, impossible) on generating rows
        a["T_p50_minus_all_prefill_ideal_par"] = round(pct([t - q["prefill_ms"] for t, q in zip(project(qs, "par_ideal_ms"), qs)], .5) / 1000, 2)
        a["T_p50_zero_search"] = round(pct([q["total_ms"] - (q["search_ms"] if q.get("packs") else 0) for q in qs], .5) / 1000, 2)
        agg[name] = a
    json.dump(agg, open(os.path.join(outd, "partime-summary.json"), "w"), indent=1)
    print(json.dumps(agg, indent=1))

# --- extra bounds (appended): block phase (fetch + fzstd decompress + materialize) per question, zero-search and
# no-block-phase projections, generating-row p50s. usage: partime_analyze.py --extra <results_dir> <out_dir>
def extra(res, outd):
    out = {}
    for name in ["aunion73-a", "q17b73-a"]:
        b = json.load(open(os.path.join(res, name, "bench.json")))
        qs = json.load(open(os.path.join(outd, f"perq-{name}.json")))
        blk = {}
        for q in b["timeline"]:
            it = q["items"]; sw = [i for i in it if i.get("name") == "search-wikipacks"]
            if not sw: continue
            s0, s1 = sw[0]["t"] - sw[0]["ms"], sw[0]["t"]
            sql = [i for i in it if i.get("name") == "sql" and (i.get("label") or "").startswith("boar-") and s0 <= i["t"] - i["ms"] <= s1]
            order, first, fb, n = [], {}, {}, 0
            for i in sql:
                db = i["label"].split("|")[0]
                if db not in first: first[db] = i["t"] - i["ms"]; order.append(db)
                if "FROM blocks" in i["label"]: fb.setdefault(db, i["t"] - i["ms"]); n += i.get("n") or 0
            t = 0
            for k, db in enumerate(order):
                e = first[order[k + 1]] if k + 1 < len(order) else s1
                if db in fb: t += e - fb[db]
            blk[q["query"]] = (t, n)
        rows = {json.loads(l)["queryId"]: json.loads(l)["query"] for l in open(os.path.join(res, name, "rows.jsonl")) if l.strip()}
        P = [q for q in qs if q.get("packs")]; G = [q for q in qs if q["llm_calls"]]
        bt = [blk[rows[q["queryId"]]][0] for q in P]; bn = [blk[rows[q["queryId"]]][1] for q in P]
        def proj(sel, f): return round(pct([f(q) for q in sel], .5) / 1000, 2)
        nob = lambda q: q["total_ms"] - (blk[rows[q["queryId"]]][0] if q.get("packs") else 0)
        zs = lambda q: q["total_ms"] - (q["search_ms"] if q.get("packs") else 0)
        out[name] = {"block_phase_share_of_search": round(sum(bt) / sum(q["serial_ms"] for q in P), 3),
                     "blocks_per_search_p50": pct(bn, .5), "block_phase_ms_p50": round(pct(bt, .5)),
                     "ms_per_block": round(sum(bt) / max(1, sum(bn)), 1),
                     "T_p50_no_block_phase": proj(qs, nob), "T_p50_zero_search": proj(qs, zs),
                     "gen_T_p50_observed": proj(G, lambda q: q["total_ms"]), "gen_T_p50_zero_search": proj(G, zs),
                     "gen_T_p50_par_js_lb": proj(G, lambda q: q["total_ms"] - ((q["search_ms"] - q["par_js_lb_ms"]) if q.get("packs") else 0)),
                     "gen_T_p50_par_ideal": proj(G, lambda q: q["total_ms"] - ((q["search_ms"] - q["par_ideal_ms"]) if q.get("packs") else 0)),
                     "gen_T_p50_no_block_phase": proj(G, nob),
                     "nongen_T_p50_observed": proj([q for q in qs if not q["llm_calls"]], lambda q: q["total_ms"]),
                     "n_gen": len(G), "n_nongen": len(qs) - len(G), "n_nongen_with_search": sum(1 for q in qs if not q["llm_calls"] and q.get("packs"))}
    json.dump(out, open(os.path.join(outd, "partime-extra.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--extra":
    extra(sys.argv[2], sys.argv[3])

# --- kit lever (appended): drop packs with 0 kept hits on this set (visa, medlineplus), serial and Promise.all.
# usage: partime_analyze.py --drop <out_dir>
def drop(outd, gone=("boar-visa-en", "boar-medlineplus-en")):
    qs = json.load(open(os.path.join(outd, "perq-aunion73-a.json"))); res = {"dropped": list(gone)}
    def nt(q, mode):
        if not q.get("packs"): return q["total_ms"]
        ps = {k: v for k, v in q["packs"].items() if k not in gone}
        ws = [p["window_ms"] for p in ps.values()]; js = sum(p["js_ms"] for p in ps.values())
        new = sum(ws) if mode == "serial" else max(js, max(ws)) if mode == "par_js_lb" else max(ws)
        return q["total_ms"] - (q["search_ms"] - new)
    for m in ["serial", "par_js_lb", "par_ideal"]:
        res["T_p50_" + m] = round(pct([nt(q, m) for q in qs], .5) / 1000, 2)
        res["T_p90_" + m] = round(pct([nt(q, m) for q in qs], .9) / 1000, 2)
    json.dump(res, open(os.path.join(outd, "partime-drop.json"), "w"), indent=1); print(json.dumps(res))

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--drop":
    drop(sys.argv[2])
