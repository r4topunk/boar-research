"""ARTHEAD 0-LLM projection: if the engine appended, for the first m distinct own-pack articles in the OBSERVED raw list
(cut-7 replay), their chunks at positions 0..j (by start), would a fact chunk be present? Counts over 180 / 137 / families.
Also the same over the observed raw ∪ pool(8) article order. python3 -I arthead.py"""
import json, sqlite3, collections, re
exec(open('diag137.py').read().split('FACTS = ')[0])
R = json.load(open('diag137.json')); ARMS2 = ARMS; dbs = {}
refs = {}
for p in PACKS:
    for l in open(f"{ARMS}/h8st/runs/st-{p}.ref.jsonl"): r = json.loads(l); refs[r['id']] = r
def own(lst, p):
    return [int(m.group(2)) for x in (lst or []) for m in [re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", x.get("chunkId") or "")] if m and m.group(1) == p]
T = collections.Counter()
for x in R:
    p = x['pack']; db = dbs.setdefault(p, sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)); r = refs[x['id']]
    fcs = {y['chunk'] for y in x['all']}
    for src in ('raw', 'raw+pool'):
        lst = own(r['raw'], p) + (own(r.get('pool'), p) if src == 'raw+pool' else [])
        arts = []
        for c in lst:
            a = db.execute("SELECT article_id FROM chunks WHERE id=?", (c,)).fetchone()[0]
            if a not in arts: arts.append(a)
        for m in (1, 2, 3):
            for j in (1, 2):
                add = set()
                for a in arts[:m]: add |= {i for i, in [(z,) for z in [row[0] for row in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (a,))][:j + 1]]}
                hit = bool(fcs & (add | set(own(r['kept'], p))))
                grp = 'u137' if not x['S_kept_ST2'] else 'k43'; fam = 'SE' if p.startswith('qa-') else 'topic'
                for g in ('all', grp, f"{grp}-{fam}"): T[(src, m, j, g)] += hit
                T[(src, m, j, 'added_chunks')] += len(add - set(own(r['kept'], p)))
for src in ('raw', 'raw+pool'):
    for m in (1, 2, 3):
        for j in (1, 2):
            print(src, f"m={m} j={j}", {g: T[(src, m, j, g)] for g in ('all', 'u137', 'u137-SE', 'u137-topic', 'k43')}, 'mean added', round(T[(src, m, j, 'added_chunks')] / 180, 2))
