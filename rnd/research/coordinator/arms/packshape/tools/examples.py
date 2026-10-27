#!/usr/bin/env python3
"""PACKSHAPE before/after chunk examples (0 LLM): original chunk text vs the shaped chunk(s) holding the same fact. -> ../examples.json"""
import json, sqlite3, sys, os
from compression import zstd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
F = {"before": "<workspace>/shared-data/packs/v3proto/boar-factbook.sqlite", "after": "<workspace>/kiln-local/shape-packs/shaped/boar-factbook.sqlite"}
EX = [("Kyrgyzstan", "Capital: Bishkek", "Kyrgyzstan's capital is Bishkek"), ("Paraguay", "Electricity generation sources (hydroelectricity)", "electricity generation sources (hydroelectricity)"),
      ("Bahrain", "Energy consumption per capita", "energy consumption per capita")]
def chunks(f, title):
    c = sqlite3.connect(f"file:{f}?mode=ro", uri=True); aid, b, off, ln = c.execute("select id, block_id, off, len from articles where title=?", (title,)).fetchone()
    t = zstd.decompress(c.execute("select zdata from blocks where id=?", (b,)).fetchone()[0])[off:off + ln].decode()
    return [t[s:e] for s, e in c.execute("select start, end from chunks where article_id=? order by id", (aid,))]
out = []
for title, kb, ka in EX:
    b = next(x for x in chunks(F["before"], title) if kb in x); a = next(x for x in chunks(F["after"], title) if ka in x)
    out.append(dict(title=title, before=b, after=a, before_words=len(b.split()), after_words=len(a.split())))
json.dump(out, open(os.path.dirname(os.path.abspath(__file__)) + "/../examples.json", "w"), indent=1)
for x in out: print("=====", x["title"], x["before_words"], "->", x["after_words"]); print("BEFORE:\n" + x["before"]); print("AFTER:\n" + x["after"])
