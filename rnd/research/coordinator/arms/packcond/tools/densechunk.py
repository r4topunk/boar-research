#!/usr/bin/env python3
"""PACKCOND DENSECHUNK D0: chunk-level dense headroom + fusion simulation for the format-2 packs. 0 LLM, 0 judge calls.
Inputs: shared-data/packs/work/densechunk/{wikivoyage,crypto}.{i8,scales.f32,ids.i32,meta.tsv} (tools/densechunk_embed.mjs --full),
q-v02.f32(+.ids) (engine search query of p4b-v02.jsonl through the replay shim's embedding call), the pack sqlites (titles,
lead_vecs), aggregates/packcond-H-v02.json (F0 hit chunks), aggregates/p4-diag.json (F0 articles), aggregates/p4b-diag.json
(gold targets, lead ranks), aggregates/sectionhit.json (buckets + lexical baselines), blind p4b-v02.jsonl (raw lists, raw_ids,
prefix_n; `query` is never read here). Scoring uses the dequantized int8 vectors (vec x scale), cosine as pure.cosineSimilarityInt8.
Outputs: aggregates/densechunk.json (ids/titles/sections/chunk ids/ranks/cosines/booleans only) and
blind/bench-v02/runs-packcond/densechunk-v02.jsonl (per-item simulated lists). Prints counts only.
usage: python3 -I tools/densechunk.py      (after: densechunk_embed.mjs --full for both packs and --query-jsonl)"""
import json, sqlite3, time, statistics as st, sys
import numpy as np
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packcond/tools")
import p4_diag as P
from p4b_diag import gmatch

ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/packcond"; D = f"{ROOT}/blind/bench-v02/runs-packcond"
W = f"{ROOT}/shared-data/packs/work/densechunk"
PACKS = {"wikivoyage": (f"{ROOT}/shared-data/packs/boar-wikivoyage-en.sqlite", "local-boar-wikivoyage-en"),
         "crypto": (f"{ROOT}/shared-data/crypto/boar-crypto.sqlite", "local-boar-crypto")}
SOURCES = ["enwiki", "enwikivoyage", "enwikibooks", "appropedia", "usgov", "eips", "ethspecs", "ethereumorg", "bips"]
LABEL = {"enwikivoyage": "Wikivoyage", "enwikibooks": "Wikibooks", "appropedia": "Appropedia", "usgov": "US government", "eips": "Ethereum EIPs/ERCs",
         "ethspecs": "Ethereum specs", "ethereumorg": "ethereum.org", "bips": "Bitcoin BIPs"}
import os
if os.environ.get("DENSE_PACKS"): PACKS = {k: v for k, v in PACKS.items() if k in os.environ["DENSE_PACKS"].split(",")}  # smoke test only
K, TOP, FLOOR, GATE = 6, 12, 0.55, 0.70  # k, semanticSearch topK*2, MIN_SEMANTIC_SIMILARITY, ANSWER_MIN_SIMILARITY (gateByRelevance)
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]

def load_pack(name):
    path, pid = PACKS[name]
    i8 = np.fromfile(f"{W}/{name}.i8", dtype=np.int8).reshape(-1, 384)
    sc = np.fromfile(f"{W}/{name}.scales.f32", dtype=np.float32)
    ids = np.fromfile(f"{W}/{name}.ids.i32", dtype=np.int32)
    meta = [l.rstrip("\n").split("\t", 2) for l in open(f"{W}/{name}.meta.tsv")]
    aid = np.array([int(m[1]) for m in meta], dtype=np.int32); sec = [m[2] if len(m) > 2 else "" for m in meta]
    assert len(i8) == len(sc) == len(ids) == len(meta)
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    art = {r[0]: (r[1], SOURCES[r[2]] if r[2] < len(SOURCES) else "enwiki") for r in db.execute("SELECT id, title, source FROM articles")}
    deq = i8.astype(np.float32) * sc[:, None]
    unit = deq / np.maximum(np.linalg.norm(deq, axis=1, keepdims=True), 1e-12)
    lead = db.execute("SELECT article_id, vec FROM lead_vecs").fetchall()
    lid = np.array([r[0] for r in lead], dtype=np.int32); lv = np.frombuffer(b"".join(r[1] for r in lead), dtype=np.int8).reshape(-1, 384).astype(np.float32)
    lv /= np.maximum(np.linalg.norm(lv, axis=1, keepdims=True), 1e-12)
    row_of = {int(c): j for j, c in enumerate(ids)}
    by_art = {}
    for j, a in enumerate(aid): by_art.setdefault(int(a), []).append(j)
    title_id = {}
    for a, (t, s) in art.items(): title_id.setdefault(t.lower(), a)
    return {"name": name, "pid": pid, "i8": i8, "unit": unit, "ids": ids, "aid": aid, "sec": sec, "art": art, "row_of": row_of, "by_art": by_art,
            "title_id": title_id, "lead_id": lid, "lead": lv, "n": len(ids)}

def disp(pk, a):  # packHitToChunk title
    t, s = pk["art"][a]; return t if s == "enwiki" else f"{LABEL.get(s, 'Source')}: {t}"

def main():
    t0 = time.time()
    PK = {n: load_pack(n) for n in PACKS}
    qids = open(f"{W}/q-v02.f32.ids").read().split()
    Q = np.fromfile(f"{W}/q-v02.f32", dtype=np.float32).reshape(-1, 384); Q /= np.linalg.norm(Q, axis=1, keepdims=True)
    qv = dict(zip(qids, Q))
    v02 = {r["id"]: r for r in load(f"{D}/p4b-v02.jsonl")}
    H32 = [l.strip() for l in open(f"{ARM}/inpack-H-v02.ids") if l.strip()]; R20 = [l.strip() for l in open(f"{ROOT}/rnd/research/coordinator/arms/random20-v02.ids") if l.strip()]
    p1 = {x["id"]: x for x in json.load(open(f"{ARM}/aggregates/packcond-H-v02.json"))["items"]}
    diag = {x["id"]: x for x in json.load(open(f"{ARM}/aggregates/p4-diag.json"))["H"]["items"]}
    p4b = {x["id"]: x for x in json.load(open(f"{ARM}/aggregates/p4b-diag.json"))["items"] if x["set"] == "v02"}
    sh = {x["id"]: x for x in json.load(open(f"{ARM}/aggregates/sectionhit.json"))["items"]}
    G2 = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json")).items() if isinstance(v, list) and v}
    GOLDRES = {i: [t for t in x["targets"] if t["kind"] == "gold" and t["resolved"]] for i, x in p4b.items()}
    GOLDRES = {i: v for i, v in GOLDRES.items() if v}

    # ---- validation: our query vectors vs the replay's lead cosines (p4b top lists)
    dif = []
    for i, r in v02.items():
        if i not in qv: continue
        for pkn, v in ((r.get("p4b") or {}).get("packs") or {}).items():
            if pkn not in PK: continue
            pk = PK[pkn]; li = {int(a): j for j, a in enumerate(pk["lead_id"])}
            for a in v["top"][:5]:
                if a["id"] in li: dif.append(abs(float(pk["lead"][li[a["id"]]] @ qv[i]) - a["cos"]))
    val = {"lead_cos_pairs": len(dif), "max_abs_diff": round(max(dif), 5), "p50_abs_diff": round(st.median(dif), 6)}
    print("validation vs replay lead cos:", val)

    cos_cache = {}
    def cos(i, pkn):
        if (i, pkn) not in cos_cache: cos_cache[(i, pkn)] = PK[pkn]["unit"] @ qv[i]
        return cos_cache[(i, pkn)]
    def rank_of(c, x): return int((c > x).sum()) + 1
    def topn(i, pkn, n=TOP, floor=FLOOR):
        c = cos(i, pkn); idx = np.argpartition(-c, n)[:n]; idx = idx[np.argsort(-c[idx])]
        return [(int(j), float(c[j])) for j in idx if c[j] >= floor]
    def art_rank(i, pkn, a):  # rank of article a among articles by best-chunk cosine
        c = cos(i, pkn); pk = PK[pkn]
        best = np.full(int(pk["aid"].max()) + 1, -2.0, dtype=np.float32); np.maximum.at(best, pk["aid"], c)
        return int((best > best[a]).sum()) + 1
    def lead_ranks(i, pkn):
        pk = PK[pkn]; lc = pk["lead"] @ qv[i]; order = np.argsort(-lc); return pk["lead_id"][order], lc

    rows = {}
    # ---- per-item dense measurement
    items = sorted(set(H32) | set(R20) | set(GOLDRES))
    for i in items:
        if i not in qv: rows[i] = {"id": i, "no_query": True, "inpack": i in H32, "r20": i in R20, "bucket": sh.get(i, {}).get("bucket")}; continue
        row = {"id": i, "inpack": i in H32, "r20": i in R20, "bucket": sh.get(i, {}).get("bucket"), "packs": {}}
        packs = (set(p1[i]["F0_packs"]) & set(PACKS)) if i in H32 else set()
        if i in R20 or not packs: packs |= set(PACKS)
        if i in GOLDRES: packs |= {t["pack"] for t in GOLDRES[i]} & set(PACKS)
        for pkn in sorted(packs):
            pk = PK[pkn]; c = cos(i, pkn); top = topn(i, pkn)
            hits = (p1.get(i, {}).get("packs", {}).get(pkn) or {}).get("hits", []) if i in H32 else []
            f0a = {int(pk["aid"][pk["row_of"][h["chunk"]]]) for h in hits if h["chunk"] in pk["row_of"]}
            f0a_diag = {pk["title_id"][t.lower()] for t in (diag.get(i, {}).get("f0_articles") or []) if pkn in (diag.get(i, {}).get("f0_packs") or []) and t.lower() in pk["title_id"]}
            hit_rows = []
            for h in hits:
                j = pk["row_of"].get(h["chunk"])
                if j is None: hit_rows.append({"chunk": h["chunk"], "missing": True}); continue
                hit_rows.append({"chunk": h["chunk"], "article": h["article"], "section": pk["sec"][j], "p": h["p"], "cos": round(float(c[j]), 4), "rank": rank_of(c, c[j])})
            allf0 = f0a | f0a_diag
            f0rows = [j for a in allf0 for j in pk["by_art"].get(a, [])]
            nonf0 = c.copy();
            if f0rows: nonf0[f0rows] = -2
            lid, lc = lead_ranks(i, pkn); lpos = {int(a): k + 1 for k, a in enumerate(lid[:50])}
            cand = [j for a in lid[:50] for j in pk["by_art"].get(int(a), [])]
            cc = c[cand]; ctop = [cand[k] for k in np.argsort(-cc)[:TOP] if cc[k] >= FLOOR]
            rec = {"n_chunks": pk["n"], "hits": hit_rows,
                   "best_f0_chunk_rank": min([h["rank"] for h in hit_rows if "rank" in h], default=None),
                   "best_f0_chunk_cos": max([h["cos"] for h in hit_rows if "cos" in h], default=None),
                   "f0_chunk_in_top12": any(int(pk["ids"][j]) in {h["chunk"] for h in hits} for j, _ in top),
                   "f0_articles": [pk["art"][a][0] for a in sorted(allf0)],
                   "first_f0_article_chunk_rank": min([rank_of(c, c[j]) for j in f0rows], default=None),
                   "f0_article_rank": min([art_rank(i, pkn, a) for a in allf0], default=None),
                   "top12": [{"chunk": int(pk["ids"][j]), "title": disp(pk, int(pk["aid"][j])), "section": pk["sec"][j], "cos": round(x, 4),
                              "f0_article": int(pk["aid"][j]) in allf0, "f0_chunk": int(pk["ids"][j]) in {h["chunk"] for h in hits}} for j, x in top],
                   "best_nonf0_cos": round(float(nonf0.max()), 4),
                   "f0_lead_rank": min([lpos.get(a, 10**6) for a in allf0], default=None),
                   "twostage_f0_chunk_in_top12": any(int(pk["ids"][j]) in {h["chunk"] for h in hits} for j in ctop),
                   "twostage_f0_article_in_top12": any(int(pk["aid"][j]) in allf0 for j in ctop)}
            if rec["f0_lead_rank"] == 10**6: rec["f0_lead_rank"] = ">50"
            rec["n_top12_f0_article"] = sum(t["f0_article"] for t in rec["top12"])
            for t in GOLDRES.get(i, []):
                if t["pack"] == pkn and t["id"] is not None:
                    js = pk["by_art"].get(int(t["id"]), [])
                    rec.setdefault("gold", []).append({"title": t["title"], "article_id": t["id"], "best_chunk_rank": min([rank_of(c, c[j]) for j in js], default=None),
                                                       "best_chunk_cos": round(max([float(c[j]) for j in js], default=-1), 4),
                                                       "in_top12": any(int(pk["aid"][j]) == int(t["id"]) for j, _ in top)})
            row["packs"][pkn] = rec
        if i in H32:
            ps = row["packs"].values()
            row["f0_chunk_in_top12"] = any(p["f0_chunk_in_top12"] for p in ps)
            row["best_f0_chunk_rank"] = min([p["best_f0_chunk_rank"] for p in ps if p["best_f0_chunk_rank"]], default=None)
            row["f0_article_rank"] = min([p["f0_article_rank"] for p in ps if p["f0_article_rank"]], default=None)
            row["twostage_f0_chunk_in_top12"] = any(p["twostage_f0_chunk_in_top12"] for p in ps)
        rows[i] = row

    # ---- fusion simulation over all 110 v0.2 items (both packs installed, as in the kit)
    def sem_list(i, floor):
        out = []
        for pkn, pk in PK.items():
            for j, x in topn(i, pkn):
                if x >= floor: out.append({"cid": f"pack:{pk['pid']}:{int(pk['ids'][j])}", "title": disp(pk, int(pk["aid"][j])), "section": pk["sec"][j], "score": x})
        return out
    def fuse(lex, sem):
        by = {}
        for L in (lex, sem):
            if not L: continue
            m = max(max(x["score"] for x in L), 1e-9)
            for x in L:
                if x["cid"] in by: by[x["cid"]]["score"] += x["score"] / m * 0.5; by[x["cid"]]["hybrid"] = True
                else: by[x["cid"]] = dict(x, score=x["score"] / m * 0.5)
        out, per = [], {}
        for x in sorted(by.values(), key=lambda z: -z["score"]):
            k = x["title"].strip().lower()
            if per.get(k, 0) >= 2: continue
            per[k] = per.get(k, 0) + 1; out.append(x)
            if len(out) >= K: break
        return out
    def raw_of(r):
        p = r.get("p4b") or {}
        return [dict(x, cid=c) for x, c in zip(r["raw"], p.get("raw_ids") or [None] * len(r["raw"]))]
    def simulate(i, variant, floor=FLOOR):
        r = v02[i]; p = r.get("p4b") or {}; raw = raw_of(r)
        if not p or p.get("no_retrieve") or not r.get("k") or i not in qv: return raw[:K]
        pre = raw[:p["prefix_n"]]; seen = {x["cid"] for x in pre}; rest = [x for x in raw[p["prefix_n"]:]]
        sem = sem_list(i, floor)
        if variant == "fused":
            n = len(rest); lex = [dict(x, score=(n - k) / n) for k, x in enumerate(rest)]
            fused = fuse(lex, sem)
            return (pre + [x for x in fused if x["cid"] not in seen])[:max(K, len(pre))]
        add = [x for x in sorted(sem, key=lambda z: -z["score"]) if x["cid"] not in seen][:2]
        seen |= {x["cid"] for x in add}
        return (pre + add + [x for x in rest if x["cid"] not in seen])[:K]
    F0hit = {i: {pkn: {h["article"].lower() for h in (v.get("hits") or [])} for pkn, v in p1[i]["packs"].items()} for i in H32}
    F0diag = {i: {pk: {t.lower() for t in diag[i]["f0_articles"]} for pk in diag[i]["f0_packs"]} for i in H32}
    F0chunk = {i: {f"pack:{PACKS[pkn][1]}:{h['chunk']}" if pkn in PACKS else None for pkn, v in p1[i]["packs"].items() for h in (v.get("hits") or [])} for i in H32}
    key6 = lambda L: [(x["title"], x.get("section")) for x in L[:K]]
    def metrics(L):  # L: id -> list
        return {"f0_article_raw6": sum(any(P.is_f0(x, F0hit[i]) for x in L[i][:K]) for i in H32),
                "f0_article_raw6_p4def": sum(any(P.is_f0(x, F0diag[i]) for x in L[i][:K]) for i in H32),
                "f0_chunk_raw6": sum(any(x.get("cid") in F0chunk[i] for x in L[i][:K]) for i in H32),
                "gold02_raw6_86": sum(any(gmatch(g, x) for g in G2[i] for x in L[i][:K]) for i in G2 if i in L),
                "gold02_raw6_resolvable": sum(any(gmatch(g, x) for g in G2[i] for x in L[i][:K]) for i in GOLDRES if i in G2),
                "r20_changed": sum(key6(L[i]) != key6(v02[i]["raw"]) for i in R20),
                "v02_changed": sum(key6(L[i]) != key6(v02[i]["raw"]) for i in v02)}
    base = {i: raw_of(v02[i])[:K] for i in v02}
    sims = {"baseline": base,
            "fused_055": {i: simulate(i, "fused", FLOOR) for i in v02},
            "fused_gate070": {i: simulate(i, "fused", GATE) for i in v02},
            "densefirst2_055": {i: simulate(i, "first", FLOOR) for i in v02},
            "densefirst2_gate070": {i: simulate(i, "first", GATE) for i in v02}}
    simt = {k: metrics(v) for k, v in sims.items()}
    for k, m in simt.items():
        m["f0_enter"] = sorted(i for i in H32 if any(P.is_f0(x, F0hit[i]) for x in sims[k][i]) and not any(P.is_f0(x, F0hit[i]) for x in base[i]))
        m["f0_leave"] = sorted(i for i in H32 if not any(P.is_f0(x, F0hit[i]) for x in sims[k][i]) and any(P.is_f0(x, F0hit[i]) for x in base[i]))
        print(k, {a: b for a, b in m.items() if not isinstance(b, list)}, "enter/leave", len(m["f0_enter"]), len(m["f0_leave"]))
    with open(f"{D}/densechunk-v02.jsonl", "w") as f:
        for i in v02:
            f.write(json.dumps({"id": i, **{k: [{kk: x.get(kk) for kk in ("title", "section", "cid", "hybrid")} for x in v[i][:K]] for k, v in sims.items()}}) + "\n")

    # ---- costs
    cost = {}
    for pkn, pk in PK.items():
        q = Q[0]; ts = []
        for _ in range(5): s = time.perf_counter(); _ = pk["unit"] @ q; ts.append((time.perf_counter() - s) * 1000)
        ts2 = []
        for _ in range(3): s = time.perf_counter(); _ = pk["i8"].astype(np.float32) @ q; ts2.append((time.perf_counter() - s) * 1000)
        n = pk["n"]; macs = n * 384; nl = len(pk["lead_id"])
        avgc = n / len(pk["art"])
        cost[pkn] = {"chunks": n, "int8_bytes": n * 384, "scale_bytes": n * 4, "total_mb": round(n * 388 / 1e6, 1),
                     "numpy_ms_prenormalized_f32": round(st.median(ts), 2), "numpy_ms_from_int8": round(st.median(ts2), 1),
                     "macs_per_query": macs, "phone_js_s_at_50M": round(macs / 50e6, 2), "phone_js_s_at_20M": round(macs / 20e6, 2),
                     "twostage_lead_macs": nl * 384, "twostage_chunk_macs_top50": int(50 * avgc * 384),
                     "twostage_phone_s_at_20M": round((nl * 384 + 50 * avgc * 384) / 20e6, 2), "twostage_phone_s_at_50M": round((nl * 384 + 50 * avgc * 384) / 50e6, 2)}
    print("cost:", cost)

    # ---- summary + buckets
    inp = [rows[i] for i in H32 if not rows[i].get("no_query")]
    def cnt(sel, f): return sum(1 for r in sel if f(r))
    ranks = [r["best_f0_chunk_rank"] for r in inp if r.get("best_f0_chunk_rank")]
    buckets = {}
    for b in sorted({rows[i].get("bucket") for i in H32}, key=str):
        sel = [rows[i] for i in H32 if rows[i].get("bucket") == b]; ok = [r for r in sel if not r.get("no_query")]
        bi = [r["id"] for r in sel]
        buckets[str(b)] = {"n": len(sel), "no_query": len(sel) - len(ok), "f0_chunk_top12": cnt(ok, lambda r: r["f0_chunk_in_top12"]),
                           "best_f0_chunk_rank_le12": cnt(ok, lambda r: (r["best_f0_chunk_rank"] or 1e9) <= 12), "best_f0_chunk_rank_le100": cnt(ok, lambda r: (r["best_f0_chunk_rank"] or 1e9) <= 100),
                           "median_best_f0_chunk_rank": (st.median([r["best_f0_chunk_rank"] for r in ok if r["best_f0_chunk_rank"]]) if any(r["best_f0_chunk_rank"] for r in ok) else None),
                           "f0_article_rank_le5": cnt(ok, lambda r: (r["f0_article_rank"] or 1e9) <= 5),
                           **{f"{k}_f0_article_raw6": sum(any(P.is_f0(x, F0hit[i]) for x in sims[k][i][:K]) for i in bi) for k in ("baseline", "fused_055", "fused_gate070", "densefirst2_055")}}
    stats = {n: json.load(open(f"{W}/{n}.stats.json")) for n in PACKS}
    summary = {"embedding_text": "${articles.title}\\n${sectionAt}: ${chunk text} (no section -> title\\n text); bge-small q8_0 via embedChunks; int8 via quantizeInt8; cosine on dequantized vectors",
               "sampling_fraction": 1.0, "embedded": stats, "validation": val,
               "inpack_n": len(H32), "inpack_with_query": len(inp),
               "gate_f0_chunk_in_dense_top12_cos055": cnt(inp, lambda r: r["f0_chunk_in_top12"]),
               "best_f0_chunk_rank_le": {n: cnt(inp, lambda r, n=n: (r["best_f0_chunk_rank"] or 1e9) <= n) for n in (1, 3, 6, 12, 50, 100, 1000)},
               "median_best_f0_chunk_rank": st.median(ranks) if ranks else None,
               "f0_article_rank_le": {n: cnt(inp, lambda r, n=n: (r["f0_article_rank"] or 1e9) <= n) for n in (1, 5, 12, 50)},
               "twostage_lead50_f0_chunk_in_top12": cnt(inp, lambda r: r["twostage_f0_chunk_in_top12"]),
               "sectionhit_baseline": {"article_raw": sum(1 for i in H32 if sh[i]["best"].get("article_in_raw")), "fact_chunk_raw": sum(1 for i in H32 if any(h.get("fact_chunk_in_raw") for h in sh[i]["hits"]))},
               "simulation": simt,
               "gate_sim_f0_article_raw6": {k: simt[k]["f0_article_raw6"] for k in simt},
               "gold_resolvable_items": sorted(GOLDRES), "buckets": buckets, "cost": cost, "seconds": round(time.time() - t0, 1)}
    print(json.dumps({k: summary[k] for k in ("gate_f0_chunk_in_dense_top12_cos055", "best_f0_chunk_rank_le", "median_best_f0_chunk_rank", "f0_article_rank_le", "twostage_lead50_f0_chunk_in_top12", "sectionhit_baseline")}))
    for b, v in buckets.items(): print(b, v)
    json.dump({"arm": "DENSECHUNK-D0", "set": "v0.2", "items": list(rows.values()), "summary": summary}, open(f"{ARM}/aggregates/densechunk.json", "w"), indent=1)
    print("wrote aggregates/densechunk.json and", f"{D}/densechunk-v02.jsonl")

if __name__ == "__main__": main()
