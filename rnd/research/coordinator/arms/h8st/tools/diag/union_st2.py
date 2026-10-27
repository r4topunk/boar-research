"""On the ST2 replay tree (wt/packs dt512+T-K2; OFF kept 43): fact chunk PRESENT under pass-through (appended chunks not
dropped by keep) for: D = dense extra-2 (ST2 'extra' appended list), A1/A2 = ARTHEAD (first own-pack article of the OFF raw
list, chunks at positions 1 / 1..2 by start, excluding already kept), and unions. 0 LLM. python3 -I union_st2.py"""
import json, sqlite3, collections, re
exec(open('diag137.py').read().split('res = []')[0])
ST2 = f"{ARMS}/densechunk-st/runs"; D0x = {x['id']: x for x in json.load(open(f"{ARMS}/densechunk-st/aggregates/d0-st2.json"))['items']}
def _cid(x): return x if isinstance(x, str) else (x.get("chunkId") or "")
def own(lst, p): return [int(m.group(2)) for x in (lst or []) for m in [re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", _cid(x))] if m and m.group(1) == p]
T = collections.Counter(); added = collections.Counter()
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); recs = collections.defaultdict(list)
    for l in open(f"{ST2}/st2-{p}.jsonl"): r = json.loads(l); recs[r['id']].append(r)
    for i, rs in recs.items():
        off = next(r for r in rs if r['mode'] == 'off'); fcs = {num(c) for c in FACTS[i]['fact_chunks']}
        kept = set(own(off['kept'], p)); raw = own(off['raw'], p)
        dense = set(own(D0x[i]['appended'], p))
        arts = []
        for c in raw:
            a = db.execute("SELECT article_id FROM chunks WHERE id=?", (c,)).fetchone()[0]
            if a not in arts: arts.append(a)
        heads = [row[0] for row in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (arts[0],))] if arts else []
        A1 = set(heads[1:2]) - kept; A2 = set(heads[1:3]) - kept; A0 = set(heads[0:2]) - kept
        cells = {"OFF": kept, "D": kept | dense, "A1": kept | A1, "A2": kept | A2, "A01": kept | A0, "D+A1": kept | dense | A1, "D+A2": kept | dense | A2}
        fam = 'SE' if p.startswith('qa-') else 'topic'
        for k, s in cells.items():
            T[(k, 'all')] += bool(fcs & s); T[(k, fam)] += bool(fcs & s); added[k] += len(s - kept)
for k in ("OFF", "D", "A1", "A2", "A01", "D+A1", "D+A2"):
    print(f"{k:5s} present {T[(k, 'all')]:3d}  SE {T[(k, 'SE')]:3d}  topic {T[(k, 'topic')]:3d}  mean added chunks {added[k] / 180:.2f}")
# residual after D+A2: diag137 class (cut-7 replay) of the items still without a fact chunk
DG = {x['id']: x for x in json.load(open('diag137.json'))}
res_ids = []
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); recs = collections.defaultdict(list)
    for l in open(f"{ST2}/st2-{p}.jsonl"): r = json.loads(l); recs[r['id']].append(r)
    for i, rs in recs.items():
        off = next(r for r in rs if r['mode'] == 'off'); fcs = {num(c) for c in FACTS[i]['fact_chunks']}
        kept = set(own(off['kept'], p)); raw = own(off['raw'], p); dense = set(own(D0x[i]['appended'], p)); arts = []
        for c in raw:
            a = db.execute("SELECT article_id FROM chunks WHERE id=?", (c,)).fetchone()[0]
            if a not in arts: arts.append(a)
        heads = [row[0] for row in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (arts[0],))] if arts else []
        if not fcs & (kept | dense | set(heads[1:3])): res_ids.append(i)
print("residual after D+A2:", len(res_ids), dict(collections.Counter(DG[i]['best']['cls'] for i in res_ids)))
print("residual SE/topic:", dict(collections.Counter(DG[i]['family'] for i in res_ids)))
