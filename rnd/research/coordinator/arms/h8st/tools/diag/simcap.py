"""0-LLM replica sweep (bm25 path only, coverage gate only; lead-cosine gate NOT modelled): fact chunk among the first N
gate-passing capped candidates under per-article cap / gate threshold variants. Directional only (replica = lower bound on
what passes the gate). Run: python3 -I simcap.py"""
import json, math, sqlite3, collections
src = open('diag137.py').read(); exec(src.split('res = []')[0])
R = {x['id']: x for x in json.load(open('diag137.json'))}
V = [(cap, g) for cap in (2, 3, 99) for g in (0.5, 0.35, 0.0)]
tally = {v: collections.Counter() for v in V}
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    db.execute("CREATE VIRTUAL TABLE temp.qtok USING fts5(x, tokenize='porter unicode61 remove_diacritics 2')")
    db.execute("CREATE VIRTUAL TABLE temp.qtok_v USING fts5vocab(temp, qtok, 'row')")
    db.execute("CREATE VIRTUAL TABLE temp.fts_v USING fts5vocab(main, fts, 'row')")
    n_idx = int(dict(db.execute("SELECT key, value FROM meta").fetchall())["indexedChunks"]); blocks = {}; arts = {}
    def chunk(cid):
        aid, s, e = db.execute("SELECT article_id, start, end FROM chunks WHERE id=?", (cid,)).fetchone()
        if aid not in arts:
            t, bid, off, ln = db.execute("SELECT title, block_id, off, len FROM articles WHERE id=?", (aid,)).fetchone()
            if bid not in blocks:
                z = db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
                blocks[bid] = subprocess.run(["zstd", "-dc"], input=bytes(z), capture_output=True, check=True).stdout
            arts[aid] = (t, blocks[bid][off:off + ln].decode())
        t, txt = arts[aid]; return t, js_slice(txt, s, e).strip()
    for x in [v for v in R.values() if v['pack'] == p]:
        q = x['query']; words = [w for w in WORD.findall(q.lower()) if len(w) > 1 and w not in STOP]
        db.execute("DELETE FROM temp.qtok"); db.execute("INSERT INTO temp.qtok (x) VALUES (?)", (" ".join(words),)); st = []
        for (term,) in db.execute("SELECT term FROM temp.qtok_v").fetchall():
            r = db.execute("SELECT doc FROM df WHERE term=?", (term,)).fetchone() or db.execute("SELECT doc FROM temp.fts_v WHERE term=?", (term,)).fetchone()
            if r and r[0] > 0: st.append((term, math.log(n_idx / r[0])))
        rk = sorted(st, key=lambda z: -z[1]); terms = [s for s, i in rk if i >= math.log(50)]; terms = terms if len(terms) >= 3 else [s for s, _ in rk[:3]]
        if not terms: continue
        rows = db.execute("SELECT f.rowid, f.s, c.article_id, c.start, a.views FROM (SELECT rowid, bm25(fts, 2, 1, 1) AS s FROM fts WHERE fts MATCH ? ORDER BY s LIMIT 80) f JOIN chunks c ON c.id=f.rowid JOIN articles a ON a.id=c.article_id",
                          (" OR ".join(map(match_term, terms)),)).fetchall()
        srt = sorted(rows, key=lambda z: (-(-z[1] + 0.5 * math.log10(1 + z[4])), -z[2], -z[3]))
        cov = {z[0]: coverage("%s %s" % chunk(z[0]), st) for z in srt}
        fcs = {y['chunk'] for y in x['all']}
        for cap, g in V:
            per = collections.Counter(); hits = []
            for z in srt:
                per[z[2]] += 1
                if per[z[2]] > cap: continue
                if cov[z[0]] >= g: hits.append(z[0])
            for N in (4, 8):
                if fcs & set(hits[:N]): tally[(cap, g)][('all', N)] += 1; tally[(cap, g)][('u137' if not x['S_kept_ST2'] else 'k43', N)] += 1
for v in V: print('cap', v[0], 'gate', v[1], {f"{a}@{n}": tally[v][(a, n)] for a in ('all', 'u137') for n in (4, 8)})
