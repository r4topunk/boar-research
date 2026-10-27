"""Fact chunk position inside its article (0 = first chunk by start) and article size, by diag class. python3 -I pos.py"""
import json, sqlite3, collections, os
exec(open('diag137.py').read().split('FACTS = ')[0])
R = json.load(open('diag137.json')); dbs = {}
out = collections.defaultdict(list)
for x in R:
    p = x['pack']; db = dbs.setdefault(p, sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True))
    best = None
    for y in x['all']:
        aid = db.execute("SELECT article_id FROM chunks WHERE id=?", (y['chunk'],)).fetchone()[0]
        ids = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (aid,))]
        pos = ids.index(y['chunk']); best = pos if best is None else min(best, pos); n = len(ids)
    fam = 'SE' if p.startswith('qa-') else 'topic'
    grp = 'u137' if not x['S_kept_ST2'] else 'k43'
    out[(grp, fam)].append((best, n, x['best']['cls']))
for k, v in sorted(out.items()):
    c = collections.Counter(min(b, 4) for b, n, _ in v)
    print(k, 'n', len(v), 'min fact pos (4=4+)', dict(sorted(c.items())), 'median art chunks', sorted(n for _, n, _ in v)[len(v)//2])
af = [b for k, v in out.items() if k[0] == 'u137' for b, n, cls in v if cls in ('article_cap', 'article_found_other_chunk')]
print('article-found (56) min fact pos', dict(sorted(collections.Counter(min(b, 4) for b in af).items())))
