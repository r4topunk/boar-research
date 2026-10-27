"""ARTHEAD on the cut-7 replay (h8st ref = tk2off tree; OFF fact chunk kept 35): fact chunk present under pass-through for
A1 = first own-pack article of raw, chunk at position 1; A2 = positions 1..2; per family; also kit/foreign check on v0.1 is
n/a (kit-only items have no installed pack). Also: share of items where A fires, added chunks, added chars. python3 -I arthead_cut7.py"""
import json, sqlite3, collections, re
exec(open('diag137.py').read().split('res = []')[0])
def own(lst, p): return [int(m.group(2)) for x in (lst or []) for m in [re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", x.get("chunkId") or "")] if m and m.group(1) == p]
T = collections.Counter(); add = collections.Counter(); chars = collections.Counter(); fire = collections.Counter()
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    for l in open(f"{ARMS}/h8st/runs/st-{p}.ref.jsonl"):
        r = json.loads(l); i = r['id']; fcs = {num(c) for c in FACTS[i]['fact_chunks']}; kept = set(own(r['kept'], p)); raw = own(r['raw'], p)
        arts = []
        for c in raw:
            a = db.execute("SELECT article_id FROM chunks WHERE id=?", (c,)).fetchone()[0]
            if a not in arts: arts.append(a)
        rows = db.execute("SELECT id, start, end FROM chunks WHERE article_id=? ORDER BY start", (arts[0],)).fetchall() if arts else []
        fam = 'SE' if p.startswith('qa-') else 'topic'
        for k, sl in (("OFF", slice(0, 0)), ("A1", slice(1, 2)), ("A2", slice(1, 3))):
            extra = {x[0] for x in rows[sl]} - kept
            T[(k, 'all')] += bool(fcs & (kept | extra)); T[(k, fam)] += bool(fcs & (kept | extra)); add[k] += len(extra)
            chars[k] += sum(x[2] - x[1] for x in rows[sl] if x[0] in extra); fire[k] += bool(extra)
for k in ("OFF", "A1", "A2"):
    print(f"{k}: present {T[(k, 'all')]} (SE {T[(k, 'SE')]}, topic {T[(k, 'topic')]}); fires on {fire[k]}/180; mean added chunks {add[k] / 180:.2f}; mean added chars {chars[k] / 180:.0f}")
