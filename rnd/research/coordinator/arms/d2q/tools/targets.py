#!/usr/bin/env python3
"""D2Q target set (criterion 83b06185): all chunks of the 22 own articles of the 20 factbook self-tests + random.Random(42).sample(2000) of the rest. -> ../targets.json"""
import json, sqlite3, random
B = "<workspace>/"; D = B + "rnd/research/coordinator/arms/d2q/"
own = json.load(open(B + "rnd/research/coordinator/arms/packproof/in/own.json"))
db = sqlite3.connect(f"file:{B}shared-data/packs/v3proto/boar-factbook.sqlite?mode=ro", uri=True)
titles = sorted({a["title"] for k, v in own.items() if k.startswith("st-boar-factbook") for a in v})
arts = [db.execute("select id from articles where title=?", (t,)).fetchone()[0] for t in titles]
ownc = [r[0] for a in arts for r in db.execute("select id from chunks where article_id=? order by id", (a,))]
rest = sorted(set(r[0] for r in db.execute("select id from chunks")) - set(ownc))
rnd = random.Random(42).sample(rest, 2000)
json.dump(dict(titles=titles, own_articles=arts, own_chunks=ownc, random_chunks=rnd, n_total=len(ownc) + len(rest)), open(D + "targets.json", "w"))
print(len(titles), len(ownc), len(rest), len(rnd), rnd[:3])
