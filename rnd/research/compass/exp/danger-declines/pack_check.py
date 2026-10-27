# Would the catalog's preparedness pack (v3, 53d8bcef…) give the danger items an on-topic source? BM25 over its FTS (title+section+body).
import json, re, sqlite3
db = sqlite3.connect("<workspace>/shared-data/preparedness-v3/boar-preparedness.sqlite")
for t in ["Burn", "Carbon monoxide poisoning", "Heat stroke", "Jellyfish", "Altitude sickness", "Frostbite", "Snakebite", "Hypothermia", "Nosebleed", "Earthquake", "First Aid/Burns", "Box jellyfish", "Heat illness"]:
    r = db.execute("select title from articles where title like ? limit 3", (f"%{t}%",)).fetchall()
    print(f"{t:28} -> {[x[0] for x in r]}")
STOP = set("a an the i my me is are was to of in on at it and or what should do how after while with for be can from just they their them his her this that our we you your get got right now very".split())
Q = [json.loads(l) for l in open("<workspace>/rnd/kiln/exp-10-main-baseline/questions.danger17.jsonl")]
print()
for q in Q:
    if q["lang"] != "en": continue
    words = [w for w in re.findall(r"[a-z]+", q["question"].lower()) if w not in STOP and len(w) > 2]
    m = " OR ".join(words)
    rows = db.execute("select a.title, c.id from fts join chunks c on c.id = fts.rowid join articles a on a.id = c.article_id where fts match ? order by bm25(fts) limit 4", (m,)).fetchall()
    print(f"{q['id']:12} {[r[0] for r in rows]}")
