"""DENSECHUNK-ST step 0, D0 per item (public self-test items only; 0 LLM / 0 judge calls). Run: python3 -I d0_st.py [pack ...]
Per item: fact chunks = in_pack_facts (article = fact.article or source.article_id, chunk_index over the article's chunks by
start); fact article = source.article_id. Dense ranks with the engine's own query vector (replay --qvec) against the pack's
int8 chunk vectors (shared-data/packs/work/densechunk/<pack>.i8): full scan, and inside the two-stage candidates (lead top-50
articles from lead_vecs -> their chunks; reached = rank <= 12 and cos >= 0.55). Replay (runs/st-<pack>.jsonl, passes
off,on,off): fact chunk / fact article in raw[:6] and in kept, empty kept, churn, ms, the item pack's scan ms. Differential:
off vs the T-K2 tree on the published files (runs/st-<pack>.tk2.jsonl) and off vs off2. Writes aggregates/d0-st.json."""
import sys, os, json, re, base64, sqlite3, statistics as st
import numpy as np
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st"
WK = f"{ROOT}/shared-data/packs/work/densechunk"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = {p for p in PACKS if p.startswith("qa-")}
M, K2, FLOOR, K = 50, 12, 0.55, 6
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or "")
    return int(m.group(2)) if m and m.group(1) == pack else None
def pct(a, q):
    a = sorted(a); return None if not a else a[min(len(a) - 1, int(round(q * (len(a) - 1))))]

def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get((l["mode"], l["id"]), 0); seen[(l["mode"], l["id"])] = n + 1
        out.setdefault(l["mode"] + ("2" if n else ""), {})[l["id"]] = l
    return out

def norm_rows(X):
    X = X.astype(np.float32); n = np.linalg.norm(X, axis=1); n[n == 0] = 1; return X / n[:, None]

def do_pack(p):
    items = load(f"{ST}/{p}.jsonl")
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    def art_chunks(a): return [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (a,))]
    lead = db.execute("SELECT article_id, vec FROM lead_vecs ORDER BY article_id").fetchall()
    lead_ids = np.array([r[0] for r in lead]); L = norm_rows(np.frombuffer(b"".join(r[1] for r in lead), dtype=np.int8).reshape(-1, 384))
    ids = np.frombuffer(open(f"{WK}/{p}.ids.i32", "rb").read(), dtype=np.int32)
    C8 = np.frombuffer(open(f"{WK}/{p}.i8", "rb").read(), dtype=np.int8).reshape(-1, 384)
    cnorm = np.linalg.norm(C8.astype(np.float32), axis=1); cnorm[cnorm == 0] = 1
    pos = {int(c): i for i, c in enumerate(ids)}
    runf = f"{ARM}/runs/st-{p}.jsonl"; tk2f = f"{ARM}/runs/st-{p}.tk2.jsonl"
    R = passes(load(runf)) if os.path.exists(runf) else {}
    T = {l["id"]: l for l in load(tk2f)} if os.path.exists(tk2f) else {}
    nlead = len(lead)
    rows = []
    for it in items:
        i = it["id"]; fa = it["source"]["article_id"]
        fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            a = f.get("article", fa); cs = art_chunks(a)
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        row = {"id": i, "pack": p, "family": "SE" if p in SE else "topic", "fact_article": fa, "fact_chunks": sorted(fcs)}
        off = R.get("off", {}).get(i)
        if off and off.get("qvec"):
            q = np.frombuffer(base64.b64decode(off["qvec"]), dtype=np.float32); q = q / (np.linalg.norm(q) or 1)
            cos = np.empty(len(ids), dtype=np.float32)
            for s in range(0, len(ids), 200000): cos[s:s + 200000] = (C8[s:s + 200000].astype(np.float32) @ q) / cnorm[s:s + 200000]
            order = np.argsort(-cos, kind="stable"); rank = np.empty(len(ids), dtype=np.int64); rank[order] = np.arange(1, len(ids) + 1)
            fr = [int(rank[pos[c]]) for c in fcs if c in pos]
            row["full_rank"] = min(fr) if fr else None
            row["full_cos"] = round(float(max(cos[pos[c]] for c in fcs if c in pos)), 4) if fr else None
            ls = L @ q; lo = np.argsort(-ls, kind="stable")
            row["fact_article_lead_rank"] = int(np.where(lead_ids[lo] == fa)[0][0]) + 1 if fa in set(lead_ids.tolist()) else None
            top = set(lead_ids[lo[:M]].tolist())
            cand = np.array([pos[c] for c, a in ch_art.items() if a in top and c in pos])
            cc = cos[cand]; co = cand[np.argsort(-cc, kind="stable")]
            crank = {int(ids[j]): r + 1 for r, j in enumerate(co)}
            tr = [crank[c] for c in fcs if c in crank]
            row["two_stage_rank"] = min(tr) if tr else None
            row["two_stage_reached"] = bool(tr) and any(crank[c] <= K2 and cos[pos[c]] >= FLOOR for c in fcs if c in crank)
            row["full_reached"] = bool(fr) and any(rank[pos[c]] <= K2 and cos[pos[c]] >= FLOOR for c in fcs if c in pos)
        for mode in ("off", "on", "off2"):
            l = R.get(mode, {}).get(i)
            if not l: continue
            raw = [cid(x, p) for x in l["raw"][:K]]; kept = [cid(x, p) for x in l["kept"]]
            row[mode] = {"chunk_raw6": any(c in fcs for c in raw if c), "art_raw6": any(ch_art.get(c) == fa for c in raw if c),
                         "chunk_kept": any(c in fcs for c in kept if c), "art_kept": any(ch_art.get(c) == fa for c in kept if c),
                         "kept_n": len(l["kept"]), "raw_n": len(l["raw"]), "ms": l["ms"], "sem_in_raw6": sum(x.get("via") == "semantic" for x in l["raw"][:K]),
                         "raw_ids": [x.get("chunkId") for x in l["raw"]], "kept_ids": [x.get("chunkId") for x in l["kept"]],
                         "scan": [d for d in l.get("dense", []) if d["leads"] == nlead]}
        if "off" in row and "on" in row:
            row["churn_raw"] = row["off"]["raw_ids"] != row["on"]["raw_ids"]; row["churn_kept"] = row["off"]["kept_ids"] != row["on"]["kept_ids"]
        if "off" in row and "off2" in row: row["off_repeat_same"] = row["off"]["raw_ids"] == row["off2"]["raw_ids"] and row["off"]["kept_ids"] == row["off2"]["kept_ids"]
        if i in T and off:
            key = lambda l: json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]] + [[x.get("chunkId"), x.get("title")] for x in l["kept"]])
            row["tk2_same"] = key(T[i]) == key(off)
        rows.append(row)
    return rows

def agg(rows):
    n = len(rows); a = {"n": n}
    for mode in ("off", "on"):
        r = [x[mode] for x in rows if mode in x]
        a[mode] = {k: sum(y[k] for y in r) for k in ("chunk_raw6", "art_raw6", "chunk_kept", "art_kept")} | {"empty_kept": sum(y["kept_n"] == 0 for y in r), "n": len(r)}
    a["full_reached"] = sum(bool(x.get("full_reached")) for x in rows); a["two_stage_reached"] = sum(bool(x.get("two_stage_reached")) for x in rows)
    a["lead_rank_le50"] = sum((x.get("fact_article_lead_rank") or 10**9) <= M for x in rows)
    fr = [x["full_rank"] for x in rows if x.get("full_rank")]; a["full_rank_median"] = st.median(fr) if fr else None
    a["full_rank_le"] = {k: sum(r <= k for r in fr) for k in (1, 3, 6, 12, 50)}
    a["churn_raw"] = sum(bool(x.get("churn_raw")) for x in rows); a["churn_kept"] = sum(bool(x.get("churn_kept")) for x in rows)
    a["sem_items_raw6"] = sum(1 for x in rows if x.get("on", {}).get("sem_in_raw6"))
    a["tk2_same"] = f"{sum(bool(x.get('tk2_same')) for x in rows)}/{sum('tk2_same' in x for x in rows)}"
    a["off_repeat_same"] = f"{sum(bool(x.get('off_repeat_same')) for x in rows)}/{sum('off_repeat_same' in x for x in rows)}"
    for mode in ("off", "on", "off2"):
        ms = [x[mode]["ms"] for x in rows if mode in x and x[mode]["ms"] is not None]
        a[f"ms_p50_{mode}"] = round(st.median(ms), 1) if ms else None
    sc = [s["leadMs"] + s["chunkMs"] for x in rows for s in x.get("on", {}).get("scan", [])]
    a["scan_ms"] = {"p50": pct(sc, .5), "p95": pct(sc, .95), "max": max(sc) if sc else None,
                    "first_load_ms": max([s["loadMs"] for x in rows for s in x.get("on", {}).get("scan", [])], default=None)}
    def enter_leave(k):
        return {"enter": sum(1 for x in rows if "on" in x and x["on"][k] and not x["off"][k]), "leave": sum(1 for x in rows if "on" in x and x["off"][k] and not x["on"][k])}
    a["chunk_raw6_enter_leave"] = enter_leave("chunk_raw6"); a["art_kept_enter_leave"] = enter_leave("art_kept")
    return a

def main():
    want = sys.argv[1:] or PACKS
    path = f"{ARM}/aggregates/d0-st.json"
    prev = json.load(open(path)) if os.path.exists(path) else {"items": []}
    items = [x for x in prev["items"] if x["pack"] not in want]
    for p in want:
        if not os.path.exists(f"{WK}/{p}.i8") or not os.path.exists(f"{ARM}/runs/st-{p}.jsonl"): print(f"skip {p} (not ready)"); continue
        items += do_pack(p); print(f"{p}: done")
    items.sort(key=lambda x: (PACKS.index(x["pack"]), x["id"]))
    slim = [{k: v for k, v in x.items()} for x in items]
    for x in slim:
        for m in ("off", "on", "off2"):
            if m in x: x[m] = {k: v for k, v in x[m].items() if k not in ("raw_ids", "kept_ids")} | {"raw_ids": x[m]["raw_ids"], "kept_ids": x[m]["kept_ids"]}
    out = {"criterion_sha256": "24793013f0fc121af1562cc23bdfa6980b25c86b2270b13784932506f6693b52", "M": M, "K2": K2, "floor": FLOOR,
           "packs_done": sorted({x["pack"] for x in items}, key=PACKS.index),
           "per_pack": {p: agg([x for x in items if x["pack"] == p]) for p in PACKS if any(x["pack"] == p for x in items)},
           "family": {f: agg([x for x in items if x["family"] == f]) for f in ("SE", "topic")},
           "all": agg(items), "items": slim}
    json.dump(out, open(path, "w"), indent=1)
    a = out["all"]; print(json.dumps({k: a[k] for k in ("n", "off", "on", "full_reached", "two_stage_reached", "churn_raw", "tk2_same", "ms_p50_off2", "ms_p50_on", "scan_ms")}))

main()
