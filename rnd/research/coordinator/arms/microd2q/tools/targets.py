"""MICROD2Q target set (0 LLM; criterion sha 5988da96...). For the 137 unreached items (diag137.json S_kept_ST2 false):
fact chunks (oracle-facts.json) + every chunk of the fact articles (item's pack) + top-N BM25 competitors per item from the
kit (boar-crypto, boar-wikivoyage-en) and the item's pack. BM25 = replica of WikiPack.bm25Candidates' SQL (diag137.py):
stems via an FTS5 temp table with the pack tokenizer, idf from df / fts5vocab, terms with df <= 2 % (idf >= ln 50), keepMin 3,
MATCH OR, bm25(fts, 2, 1, 1); query = the engine's search query from the cut-7 replay (h8st runs st-<pack>.ref.jsonl).
usage: python3 -I targets.py [--count-only] -> tools/targets.json (+ stdout counts). Read-only on the published packs."""
import json, math, re, sqlite3, subprocess, sys, collections, os
ROOT = "<workspace>"; ARMS = f"{ROOT}/rnd/research/coordinator/arms"; ST = f"{ROOT}/rnd/research/packs/selftest"
OUT = f"{ARMS}/microd2q/tools/targets.json"
STOP = set(("a about above after again against all also am an and any are as at be because been before being below "
            "between both but by can could compare comparison describe did difference differences do does doing down "
            "during each explain few for from further give had has have having he her here hers him his how i if in "
            "into is it its itself just know like me mean means more most much my no nor not now of off on once only "
            "or other our out over own please same she should show so some such summarize tell than that the their "
            "them then there these they this those through to too under until up us very versus vs was we were what "
            "when where which while who whom whose why will with would you your").split())
WORD = re.compile(r"[^\W_]+", re.U)
KIT = {"boar-crypto": f"{ROOT}/shared-data/crypto/boar-crypto.sqlite", "boar-wikivoyage-en": f"{ROOT}/shared-data/packs/boar-wikivoyage-en.sqlite"}
def pub(p): return KIT.get(p) or next(f"{ROOT}/shared-data/packs/{w}/{p}.sqlite" for w in ("wave2", "wave1") if os.path.exists(f"{ROOT}/shared-data/packs/{w}/{p}.sqlite"))
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
num = lambda c: int(c.rsplit(":", 1)[1])
def match_term(st):
    q = lambda t: '"' + t.replace('"', '""') + '"'
    return q(st[:-1]) + "*" if st.endswith("i") and len(st) > 4 else q(st)
class Pack:
    def __init__(s, pid):
        s.id = pid; s.db = db = sqlite3.connect(f"file:{pub(pid)}?mode=ro", uri=True)
        db.execute("CREATE VIRTUAL TABLE temp.qtok USING fts5(x, tokenize='porter unicode61 remove_diacritics 2')")
        db.execute("CREATE VIRTUAL TABLE temp.qtok_v USING fts5vocab(temp, qtok, 'row')")
        db.execute("CREATE VIRTUAL TABLE temp.fts_v USING fts5vocab(main, fts, 'row')")
        m = dict(db.execute("SELECT key, value FROM meta").fetchall()); s.n = int(m["indexedChunks"]); s.name = m.get("name", pid)
        s.hasdf = bool(db.execute("SELECT 1 FROM sqlite_master WHERE name='df'").fetchone())
    def stems(s, text):
        words = [w for w in WORD.findall(text.lower()) if len(w) > 1 and w not in STOP]
        if not words: return []
        s.db.execute("DELETE FROM temp.qtok"); s.db.execute("INSERT INTO temp.qtok (x) VALUES (?)", (" ".join(words),))
        out = []
        for (term,) in s.db.execute("SELECT term FROM temp.qtok_v").fetchall():
            r = (s.db.execute("SELECT doc FROM df WHERE term=?", (term,)).fetchone() if s.hasdf else None) or s.db.execute("SELECT doc FROM temp.fts_v WHERE term=?", (term,)).fetchone()
            if r and r[0] > 0: out.append((term, math.log(s.n / r[0])))
        return out
    def top(s, query, n):
        ranked = sorted(s.stems(query), key=lambda x: -x[1])
        terms = [t for t, idf in ranked if idf >= math.log(50)]; terms = terms if len(terms) >= 3 else [t for t, _ in ranked[:3]]
        if not terms: return []
        return s.db.execute("SELECT rowid, bm25(fts, 2, 1, 1) AS sc FROM fts WHERE fts MATCH ? ORDER BY sc LIMIT ?", (" OR ".join(map(match_term, terms)), n)).fetchall()
    def article_chunks(s, cid):
        aid = s.db.execute("SELECT article_id FROM chunks WHERE id=?", (cid,)).fetchone()[0]
        return aid, [r[0] for r in s.db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (aid,))]
D = [x for x in json.load(open(f"{ARMS}/h8st/tools/diag/diag137.json")) if not x["S_kept_ST2"]]
FACTS = json.load(open(f"{ARMS}/oracle-st/tools/oracle-facts.json"))
assert len(D) == 137
P = {}
def pack(pid):
    if pid not in P: P[pid] = Pack(pid)
    return P[pid]
N = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--n=")), 50)); NOWN = round(0.7 * N); NKIT = N - NOWN  # 6k cap: largest N <= 50 with total <= 6000
T = collections.defaultdict(lambda: {"roles": set(), "items": set()})  # (pack, chunk) -> roles/items
items = {}
for x in D:
    i, p = x["id"], x["pack"]; F = FACTS[i]
    q = {l["id"]: l for l in load(f"{ARMS}/h8st/runs/st-{p}.ref.jsonl")}[i]["query"] or x["query"]
    fcs = [num(c) for c in F["fact_chunks"]]; items[i] = {"pack": p, "query": q, "fact_chunks": fcs, "split": x["best"]["cls"]}
    for c in fcs:
        T[(p, c)]["roles"].add("fact"); T[(p, c)]["items"].add(i)
        _, cs = pack(p).article_chunks(c)
        for c2 in cs: T[(p, c2)]["roles"].add("article"); T[(p, c2)]["items"].add(i)
    # Competitors (6k-cap reading, fixed before any generation): the item's pack top-NOWN by raw bm25 + the kit's top-NKIT
    # (boar-crypto and boar-wikivoyage-en lists interleaved by rank: crypto 1, voyage 1, crypto 2, ...), NOWN + NKIT = N (7:3), N = the largest <= 50 that keeps the target set <= 6000 chunks (the criterion's generation cap).
    own = [r[0] for r in pack(p).top(q, NOWN)]
    kc, kv = [r[0] for r in pack("boar-crypto").top(q, NKIT)], [r[0] for r in pack("boar-wikivoyage-en").top(q, NKIT)]
    inter = []
    for j in range(NKIT):
        if j < len(kc): inter.append(("boar-crypto", kc[j]))
        if j < len(kv): inter.append(("boar-wikivoyage-en", kv[j]))
    inter = inter[:NKIT]
    for rid in own: T[(p, rid)]["roles"].add("comp"); T[(p, rid)]["items"].add(i)
    for pid, rid in inter: T[(pid, rid)]["roles"].add("comp"); T[(pid, rid)]["items"].add(i)
    items[i]["comps"] = {"own": len(own), "kit": dict(collections.Counter(pid for pid, _ in inter))}
cnt = collections.Counter(); byrole = collections.Counter()
for (pid, c), v in T.items():
    cnt[pid] += 1
    byrole["fact" if "fact" in v["roles"] else "article" if "article" in v["roles"] else "comp"] += 1
print(json.dumps({"NOWN": NOWN, "NKIT": NKIT, "total": len(T), "by_pack": cnt, "by_role": byrole}))
if "--count-only" in sys.argv: sys.exit(0)
json.dump({"NOWN": NOWN, "NKIT": NKIT, "items": items, "targets": [{"pack": pid, "chunk": c, "roles": sorted(v["roles"]), "items": sorted(v["items"])} for (pid, c), v in sorted(T.items())]}, open(OUT, "w"))
print("wrote", OUT)
