#!/usr/bin/env python3
"""Why is the fact chunk unreached? 0-LLM diagnosis over EXISTING public replay outputs (no engine run).
in : oracle-st/tools/oracle-facts.json (fact chunks per item), densechunk-st/aggregates/d0-st2.json (the ORACLE 137/43 split),
     h8st/runs/st-<pack>.ref.jsonl (cut-7 tk2off replay: raw, pool = extra retrieve(q, 8), kept, diag sub/comp/ground),
     rnd/research/packs/selftest/<pack>.jsonl, the published pack sqlite files (read-only).
Replica of WikiPack.bm25Candidates + the searchDetailed relevance gate (wikiPack.ts:465-488, :663-681, :337-341, :850-880):
stems via an FTS5 temp table with the pack tokenizer, idf from df / fts5vocab, queryTerms (df <= 2 %, keepMin 3), MATCH OR of
terms, bm25(fts, 2, 1, 1) LIMIT 80, + 0.5 log10(1 + views), per-article cap 2, gate coverage(title + text) >= 0.5, limit = k.
Title hits (named articles) are NOT replicated; observed raw lists are used for everything the replay saw.
out: h8st/tools/diag/diag137.json (+ stdout tables). Run: python3 -I diag137.py"""
import json, math, re, sqlite3, subprocess, collections, os
ROOT = "<workspace>"; ARMS = f"{ROOT}/rnd/research/coordinator/arms"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
STOP = set(("a about above after again against all also am an and any are as at be because been before being below "
            "between both but by can could compare comparison describe did difference differences do does doing down "
            "during each explain few for from further give had has have having he her here hers him his how i if in "
            "into is it its itself just know like me mean means more most much my no nor not now of off on once only "
            "or other our out over own please same she should show so some such summarize tell than that the their "
            "them then there these they this those through to too under until up us very versus vs was we were what "
            "when where which while who whom whose why will with would you your").split())
WORD = re.compile(r"[^\W_]+", re.U)
def pub(p): return next(f"{ROOT}/shared-data/packs/{w}/{p}.sqlite" for w in ("wave2", "wave1") if os.path.exists(f"{ROOT}/shared-data/packs/{w}/{p}.sqlite"))
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
FACTS = json.load(open(f"{ARMS}/oracle-st/tools/oracle-facts.json"))
D0 = {x["id"]: x["off"]["chunk_kept"] for x in json.load(open(f"{ARMS}/densechunk-st/aggregates/d0-st2.json"))["items"]}
num = lambda c: int(c.rsplit(":", 1)[1])
def js_slice(s, a, b): u = s.encode("utf-16-le"); return u[2 * a:2 * b].decode("utf-16-le", errors="surrogatepass")
def prefix_of(st): return st[:-1] if st.endswith("i") and len(st) > 3 else st
def count_at_boundary(pfx, text):
    i = text.find(pfx)
    while i >= 0:
        if i == 0 or not (text[i - 1].isalnum()): return 1
        i = text.find(pfx, i + 1)
    return 0
def coverage(text, stems):
    low = text.lower(); tot = sum(i for _, i in stems) or 1
    return sum(i for s, i in stems if count_at_boundary(prefix_of(s), low)) / tot
def match_term(st):
    q = lambda t: '"' + t.replace('"', '""') + '"'
    return q(st[:-1]) + "*" if st.endswith("i") and len(st) > 4 else q(st)
ORDER = ["kept_cut7", "raw_dropped_grounding", "raw_dropped_compression", "raw_dropped_health", "raw_dropped_other",
         "cross_pack_or_fusion", "own_pack_rank", "relevance_gate", "article_cap", "article_found_other_chunk", "lexical_deep_rank", "lexical_no_match"]
res = []
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    db.execute("CREATE VIRTUAL TABLE temp.qtok USING fts5(x, tokenize='porter unicode61 remove_diacritics 2')")
    db.execute("CREATE VIRTUAL TABLE temp.qtok_v USING fts5vocab(temp, qtok, 'row')")
    db.execute("CREATE VIRTUAL TABLE temp.fts_v USING fts5vocab(main, fts, 'row')")
    n_idx = int(dict(db.execute("SELECT key, value FROM meta").fetchall())["indexedChunks"])
    blocks, arts = {}, {}
    def article(aid):
        if aid not in arts:
            t, bid, off, ln, views = db.execute("SELECT title, block_id, off, len, views FROM articles WHERE id=?", (aid,)).fetchone()
            if bid not in blocks:
                z = db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
                blocks[bid] = subprocess.run(["zstd", "-dc"], input=bytes(z), capture_output=True, check=True).stdout
            arts[aid] = (t, blocks[bid][off:off + ln].decode("utf-8"), views)
        return arts[aid]
    def chunk(cid):
        aid, s, e = db.execute("SELECT article_id, start, end FROM chunks WHERE id=?", (cid,)).fetchone()
        t, txt, v = article(aid); return aid, t, js_slice(txt, s, e).strip()
    def stems(text):
        words = [w for w in WORD.findall(text.lower()) if len(w) > 1 and w not in STOP]
        if not words: return []
        db.execute("DELETE FROM temp.qtok"); db.execute("INSERT INTO temp.qtok (x) VALUES (?)", (" ".join(words),))
        out = []
        for (term,) in db.execute("SELECT term FROM temp.qtok_v").fetchall():
            r = db.execute("SELECT doc FROM df WHERE term=?", (term,)).fetchone() or db.execute("SELECT doc FROM temp.fts_v WHERE term=?", (term,)).fetchone()
            if r and r[0] > 0: out.append((term, math.log(n_idx / r[0])))
        return out
    refs = {l["id"]: l for l in load(f"{ARMS}/h8st/runs/st-{p}.ref.jsonl")}
    for it in load(f"{ST}/{p}.jsonl"):
        i = it["id"]; F = FACTS[i]; r = refs[i]; fcs = {num(c) for c in F["fact_chunks"]}
        fart = {db.execute("SELECT article_id FROM chunks WHERE id=?", (c,)).fetchone()[0] for c in fcs}
        mine = lambda lst: [int(m.group(2)) for x in (lst or []) for m in [re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", x.get("chunkId") or "")] if m and m.group(1) == p]
        raw, pool, kept = mine(r["raw"]), mine(r.get("pool")), mine(r["kept"])
        raw_all = len(r["raw"]); raw_foreign = raw_all - len(raw)
        dg = r.get("diag") or {}; dsub, dcomp, dgr = (set(mine([{"chunkId": c} for c in dg.get(k) or []])) for k in ("sub", "comp", "ground"))
        st = stems(r["query"] or it["question"]); ranked = sorted(st, key=lambda x: -x[1])
        terms = [s for s, idf in ranked if idf >= math.log(50)]; terms = terms if len(terms) >= 3 else [s for s, _ in ranked[:3]]
        rows = db.execute("SELECT f.rowid, f.s, c.article_id, c.start, a.views FROM (SELECT rowid, bm25(fts, 2, 1, 1) AS s FROM fts WHERE fts MATCH ? ORDER BY s LIMIT 3000) f "
                          "JOIN chunks c ON c.id = f.rowid JOIN articles a ON a.id = c.article_id", (" OR ".join(map(match_term, terms)),)).fetchall() if terms else []
        bm_rank = {row[0]: k + 1 for k, row in enumerate(sorted(rows, key=lambda x: x[1]))}  # 1 = best raw bm25
        pool80 = sorted(rows, key=lambda x: x[1])[:80]
        srt = sorted(pool80, key=lambda x: (-(-x[1] + 0.5 * math.log10(1 + x[4])), -x[2], -x[3]))
        per = collections.Counter(); capped = []
        for row in srt:
            per[row[2]] += 1
            if per[row[2]] <= 2: capped.append(row)
        # replica of the relevance-gated fill (bm25 path only)
        hits = []; gate = {}
        for row in capped:
            aid, t, txt = chunk(row[0]); ok = coverage(f"{t} {txt}", st) >= 0.5; gate[row[0]] = ok
            if ok and len(hits) < r["k"]: hits.append(row[0])
        in80 = {row[0] for row in pool80}; incap = {row[0] for row in capped}; art80 = {row[2] for row in pool80}
        per_fc = []
        for c in fcs:
            aid, t, txt = chunk(c)
            idx_terms = sum(1 for s in terms if db.execute("SELECT 1 FROM fts WHERE fts MATCH ? AND rowid=?", (match_term(s), c)).fetchone())
            cov_all = coverage(f"{t} {txt}", st)
            cov_idx = sum(idf for s, idf in st if db.execute("SELECT 1 FROM fts WHERE fts MATCH ? AND rowid=?", (match_term(s), c)).fetchone()) / (sum(i for _, i in st) or 1)
            if c in kept: cls = "kept_cut7"
            elif c in raw:
                cls = ("raw_dropped_health" if dg.get("health") else "raw_dropped_other") if not dg or dg.get("special") or dg.get("health") else \
                      ("raw_dropped_other" if c not in dsub else "raw_dropped_compression" if c not in dcomp else "raw_dropped_grounding" if c not in dgr else "raw_dropped_other")
            elif c in hits: cls = "cross_pack_or_fusion"
            elif c in incap and gate.get(c): cls = "own_pack_rank"
            elif c in incap: cls = "relevance_gate"
            elif c in in80: cls = "article_cap"
            elif aid in art80 or any(db.execute("SELECT article_id FROM chunks WHERE id=?", (x,)).fetchone()[0] == aid for x in raw + pool): cls = "article_found_other_chunk"
            elif c in bm_rank: cls = "lexical_deep_rank"
            else: cls = "lexical_no_match"
            per_fc.append({"chunk": c, "cls": cls, "bm25_rank": bm_rank.get(c), "in_pool80": c in in80, "gate_cov": round(cov_all, 3),
                           "idx_cov": round(cov_idx, 3), "terms_in_chunk": idx_terms, "n_terms": len(terms), "in_pool8": c in pool, "is_lead": num(F["lead_chunk"]) == c})
        best = min(per_fc, key=lambda x: ORDER.index(x["cls"]))
        res.append({"id": i, "pack": p, "family": F["family"], "S_kept_ST2": D0[i], "k": r["k"], "raw_n": raw_all, "raw_foreign": raw_foreign,
                    "own_raw_n": len(raw), "replica_hits": hits, "replica_vs_raw_own_same": hits == [x for x in raw if x in incap][:len(hits)],
                    "art_in_raw": any(db.execute("SELECT article_id FROM chunks WHERE id=?", (x,)).fetchone()[0] in fart for x in raw),
                    "n_fact_chunks": len(fcs), "best": best, "all": per_fc, "query": r["query"] or it["question"], "n_stems": len(st)})
    db.close()
json.dump(res, open(f"{ARMS}/h8st/tools/diag/diag137.json", "w"), indent=1)
def table(sub, name):
    c = collections.Counter(x["best"]["cls"] for x in sub); se = collections.Counter(x["best"]["cls"] for x in sub if x["family"] == "SE")
    print(f"\n{name} n={len(sub)}"); [print(f"  {k:28s} {c[k]:4d}  SE {se[k]:3d}  topic {c[k] - se[k]:3d}") for k in ORDER if c[k]]
table([x for x in res if not x["S_kept_ST2"]], "ORACLE 137 (ST2 OFF did not keep a fact chunk)")
table([x for x in res if x["S_kept_ST2"]], "ORACLE 43 (kept)")
table(res, "all 180")
u = [x for x in res if not x["S_kept_ST2"]]
for cls in ("lexical_no_match", "lexical_deep_rank", "article_found_other_chunk", "article_cap", "relevance_gate", "own_pack_rank"):
    s = [x["best"] for x in u if x["best"]["cls"] == cls]
    if s: print(cls, "median idx_cov", sorted(y["idx_cov"] for y in s)[len(s) // 2], "median gate_cov", sorted(y["gate_cov"] for y in s)[len(s) // 2],
                "median bm25_rank", sorted((y["bm25_rank"] or 9999) for y in s)[len(s) // 2], "is_lead", sum(y["is_lead"] for y in s))
print("replica own-pack agreement with observed raw (own chunks prefix):", sum(x["replica_vs_raw_own_same"] for x in res), "/", len(res))
