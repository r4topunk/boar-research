#!/usr/bin/env python3
"""PACKPROOF own-article table (0 LLM): per item the fact articles (source article + comparison partners) with url and title from the published pack. -> ../in/own.json"""
import json, sqlite3
P = "<workspace>/rnd/research/coordinator/arms/packproof"; ST = "<workspace>/rnd/research/packs/selftest/"; SD = "<workspace>/shared-data/packs/"
WAVE = {"boar-factbook": "wave2", "boar-simplewiki-en": "wave2", "qa-cooking-se": "wave3", "qa-money-se": "wave3"}
SUPP = ["qa-cooking-se", "qa-money-se"]  # supplementary rows (UXMATRIX cm 40)
own = {}
for p in json.load(open(P + "/in/items.json"))["packs"] + SUPP:
    db = sqlite3.connect(f"file:{SD}{WAVE.get(p, 'wave1')}/{p}.sqlite?mode=ro", uri=True)
    for l in open(ST + p + ".jsonl"):
        x = json.loads(l); ids = [x["source"]["article_id"]] + [f["article"] for f in x["in_pack_facts"] if "article" in f]
        arts = []
        for a in dict.fromkeys(ids):
            t = db.execute("select title from articles where id=?", (a,)).fetchone()[0]; u = db.execute("select url from article_meta where article_id=?", (a,)).fetchone()[0]
            arts.append(dict(article=a, title=t, url=u))
        assert arts[0]["title"] == x["source"]["title"] and arts[0]["url"] == x["source"]["url"], x["id"]
        own[x["id"]] = arts
json.dump(own, open(P + "/in/own.json", "w"), indent=0); print(len(own), sum(len(v) > 1 for v in own.values()), "with partners")
