#!/usr/bin/env python3
"""ORACLE-ST aggregation (0 LLM calls). Usage: python3 -I oracle_agg.py [--gen-only]  -> aggregates/oracle-st.json (+ stdout summary)
Estimator = arms/packs/tools/localjudge_agg.py's own functions (load / ratios / boot / paired / setstats: combineOrders per item, ratio of sums,
paired per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11), exec'd from that file unchanged.
Cells: S = arms/packs/selftest-runs/st-<pack>-cut7-s42 (Haiku .judgments.jsonl / Opus .judgments.opus.jsonl), ADD / ONLY = runs/st-<pack>-cut7-oracle{add,only}-s42.
Paired deltas never mix judges. Splits: pooled 180, per pack, SE vs topic, declared split = S kept a fact chunk (DENSECHUNK-ST2 d0-st2.json
items[].off.chunk_kept, the GROUND-ST OFF count 43/180) vs not; side split = the oracle chunk itself already kept (ADD trace code oracle:add-already-kept).
Generation: per cell n, errors, p50 s/item, kept count, prompt tokens, oracle codes, fact chunk text present in the final prompt (prompt dump)."""
import json, os, sys, statistics as stt, sqlite3
ROOT = "<workspace>"; ARMS = f"{ROOT}/rnd/research/coordinator/arms"; A = f"{ARMS}/oracle-st"; SR = f"{ARMS}/packs/selftest-runs"
src = open(f"{ARMS}/packs/tools/localjudge_agg.py").read(); exec(src[src.index("import json"):src.index("out = {}\n# calibration")]); A = f"{ARMS}/oracle-st"  # load, ratios, boot, ci, setstats, paired, PACKS (it sets its own A)
bsrc = open(f"{A}/tools/build_oracle.py").read(); exec(bsrc[bsrc.index("import hashlib"):bsrc.index("add, only, facts, missing")])  # pub, article_text, js_slice, js_trim
FACTS = json.load(open(f"{A}/tools/oracle-facts.json"))
D0 = {x["id"]: x["off"]["chunk_kept"] for x in json.load(open(f"{ARMS}/densechunk-st/aggregates/d0-st2.json"))["items"]}
L = lambda f: [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
def ctext(i):
    f = FACTS[i]; db = sqlite3.connect(f"file:{pub(f['pack'])}?mode=ro", uri=True); cid = int(f["oracle_chunk"].rsplit(":", 1)[1])
    aid, s0, e0 = db.execute("SELECT article_id, start, end FROM chunks WHERE id=?", (cid,)).fetchone(); return js_trim(js_slice(article_text(db, pub(f["pack"]), aid), s0, e0))
def gen(cell):
    rows, per = [], {}
    for p in PACKS:
        tr = L(f"{A}/runs/st-{p}-cut7-{cell}-s42.traces.jsonl") if cell != "S" else L(f"{SR}/st-{p}-cut7-s42.traces.jsonl")
        pr = {r["query"]: r["prompt"] for r in L(f"{A}/runs/st-{p}-cut7-{cell}-s42.prompts.jsonl")}
        for t in tr:
            i = t["itemId"]; codes = [c for c in t["route"]["reasonCodes"] if c.startswith("oracle:")]; P = pr.get(t["question"])
            ptxt = (P[0]["content"] if isinstance(P, list) else P) if P is not None else None
            per[i] = {"pack": p, "kept": len(t["retrieval"]["kept"]), "promptTokens": t["timing"]["promptTokens"], "s": t["timing"]["totalMs"] / 1000,
                      "error": bool(t.get("error")), "codes": codes, "llm_prompt": ptxt is not None,
                      "fact_in_prompt": (ctext(i) in ptxt) if (ptxt is not None and cell != "S") else None,
                      "already_kept": any(c.startswith("oracle:add-already-kept") for c in codes), "extractive": t["route"]["tier"] == "instant" or ptxt is None}
    v = list(per.values()); pt = [x["promptTokens"] for x in v if x["promptTokens"]]
    summ = {"n": len(v), "errors": sum(x["error"] for x in v), "p50_s": round(stt.median([x["s"] for x in v]), 2) if v else None,
            "kept_total": sum(x["kept"] for x in v), "kept_mean": round(sum(x["kept"] for x in v) / len(v), 2) if v else None,
            "kept_hist": {k: sum(x["kept"] == k for x in v) for k in sorted({x["kept"] for x in v})}, "promptTokens_p50": stt.median(pt) if pt else None,
            "items_with_llm_prompt": sum(x["llm_prompt"] for x in v), "fact_chunk_text_in_final_prompt": sum(bool(x["fact_in_prompt"]) for x in v),
            "oracle_codes": {k: sum(any(c.startswith(k) for c in x["codes"]) for x in v) for k in ("oracle:add:", "oracle:add-already-kept", "oracle:only-2", "oracle:only-1", "oracle:missing", "oracle:no-entry")}}
    return summ, per
def J(cell, judge, p):
    if cell == "S": return load(f"{SR}/st-{p}-cut7-s42.judgments{'.opus' if judge == 'opus' else ''}.jsonl")
    return load(f"{A}/runs/st-{p}-cut7-{cell}-s42.judgments{'.opus' if judge == 'opus' else ''}.jsonl")
def pooled(cell, judge):
    X, S = {}, {}
    for p in PACKS:
        x, s = J(cell, judge, p), J("S", judge, p)
        for q in set(x) & set(s): X[q], S[q] = x[q], s[q]
    return X, S
def deltas(cell, judge, addper):
    X, S = pooled(cell, judge); ids = sorted(X)
    if not ids: return None
    sub = lambda f: [q for q in ids if f(q)]
    groups = {"pooled": ids, "SE": sub(lambda q: FACTS[q]["family"] == "SE"), "topic": sub(lambda q: FACTS[q]["family"] == "topic"),
              "S_kept_fact_chunk": sub(lambda q: D0[q]), "S_not_kept_fact_chunk": sub(lambda q: not D0[q])}
    if addper: groups |= {"oracle_chunk_already_kept": sub(lambda q: addper.get(q, {}).get("already_kept")), "oracle_chunk_appended": sub(lambda q: q in addper and not addper[q]["already_kept"])}
    groups |= {f"pack:{p}": sub(lambda q, p=p: FACTS[q]["pack"] == p) for p in PACKS}
    out = {"n_total": len(ids), "cell": setstats(X, ids), "S": setstats(S, ids)}
    for g, gi in groups.items():
        if len(gi) >= 2: out[g] = paired(X, S, gi)
    return out
res = {"criterion_sha256": open(f"{A}/ORACLE-ST-criterion.sha256").read().split()[0], "patch_sha256": open(f"{A}/oracle.vs-cut7.patch.sha256").read().split()[0], "gen": {}, "judge": {}}
per = {}
for cell in ("oracleadd", "oracleonly"):
    res["gen"][cell], per[cell] = gen(cell)
res["gen"]["S"], _ = gen("S")
if "--gen-only" not in sys.argv:
    for cell in ("oracleadd", "oracleonly"):
        for judge in ("opus", "haiku"):
            d = deltas(cell, judge, per.get("oracleadd"))
            if d: res["judge"][f"{cell}-{judge}"] = d
    o = res["judge"].get("oracleadd-opus", {}).get("pooled")
    if o and res["judge"]["oracleadd-opus"]["n_total"] == 180:
        dp, lo = o["d_raw"], o["d_raw_ci"][0]
        res["verdict"] = {"rule": "READER-WALL" if dp <= 0.03 else "RETRIEVAL-HEADROOM" if (dp >= 0.08 and lo > 0.03) else "IN-BETWEEN", "add_minus_s_opus": dp, "ci": o["d_raw_ci"]}
res["items"] = {c: per[c] for c in per}
json.dump(res, open(f"{A}/aggregates/oracle-st.json", "w"), indent=1)
print(json.dumps(res["gen"], indent=None))
for k, v in res["judge"].items():
    print(f"== {k}: n {v['n_total']} cell raw {v['cell']['raw']} {v['cell']['raw_ci']} vs S {v['S']['raw']} {v['S']['raw_ci']}")
    for g in [g for g in v if g not in ("n_total", "cell", "S")]: print(f"   {g}: {json.dumps(v[g])}")
print("verdict", res.get("verdict"))
