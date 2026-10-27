#!/usr/bin/env python3
"""DETECTOR-HN step 1 (0 LLM): dump the cooking/money packs' thread titles (articles table only), drop the 40 cm self-test
oracle threads (by pack + article id; their text is never read), stratified 80/20 split by pack, seed 42.
Writes data/titles.{train,heldout}.jsonl ({id, pack, article_id, title}) and data/titles.stats.json."""
import json, sqlite3, random, hashlib
B = "<workspace>/"; A = B + "rnd/research/coordinator/arms/"; O = A + "detector-hn/data/"
ORA = json.load(open(A + "coverage-map/aggregates/cm-oracle.json"))
excl = {(v["pack"], int(v["article_id"])) for v in ORA.values()}
tr, ho, st = [], [], {"excluded_selftest_threads": len(excl)}
for pack in ("qa-cooking-se", "qa-money-se"):
    db = sqlite3.connect(f"file:{B}shared-data/packs/wave3/{pack}.sqlite?mode=ro", uri=True)
    rows = [(i, t) for i, t in db.execute("select id, title from articles order by id")]
    seen, items = set(), []
    for i, t in rows:
        t = " ".join((t or "").split())
        if (pack, i) in excl or not t or t.lower() in seen: continue
        seen.add(t.lower()); items.append({"id": f"{pack}:{i}", "pack": pack, "article_id": i, "title": t})
    rng = random.Random(42); rng.shuffle(items); k = int(round(len(items) * .8))
    tr += items[:k]; ho += items[k:]
    st[pack] = {"articles": len(rows), "kept_unique": len(items), "train": k, "heldout": len(items) - k,
                "dropped_selftest": sum(1 for i, _ in rows if (pack, i) in excl)}
for name, xs in (("train", tr), ("heldout", ho)):
    p = O + f"titles.{name}.jsonl"
    with open(p, "w") as f:
        for x in xs: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    st[name] = {"n": len(xs), "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()}
json.dump(st, open(O + "titles.stats.json", "w"), indent=1); print(json.dumps(st, indent=1))
