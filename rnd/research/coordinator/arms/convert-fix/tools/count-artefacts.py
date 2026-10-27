#!/usr/bin/env python3 -I
"""usage: count-artefacts.py <pack.sqlite> <out.json> [mod=1]   (python >= 3.14, read-only, 0 LLM)
Counts chunks whose text has a number-less unit/measure artefact; also literal '{{convert' leftovers and 'stretches .'"""
import sys, re, json, sqlite3
from compression import zstd
ART = re.compile(r" stretches \.|\b(is|was|measures|about|of) \.(?=\s|$)")
ART_UNIT = re.compile(r"\b(?:is|are|was|were|about|of|than|over|around|up to|nearly|reaches?|long|tall|high|wide|deep)\s+[.,;)](?=\s|$)", re.I)
pack, out = sys.argv[1], sys.argv[2]; mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
tot_art = db.execute("select count(*) from articles").fetchone()[0]; tot_ch = db.execute("select count(*) from chunks").fetchone()[0]
q = ("select a.id aid, a.title, a.block_id, a.off, a.len, c.start, c.end from articles a join chunks c on c.article_id=a.id "
     + (f"where a.id % {mod} = 0 " if mod > 1 else "") + "order by a.block_id, a.id, c.id")
cid = None; blk = None; last = None; t16 = None
n = hit = hit2 = lit = 0; arts = set(); arts2 = set(); ex = []
for r in db.execute(q):
    if r[2] != cid: blk = zstd.decompress(db.execute("select zdata from blocks where id=?", (r[2],)).fetchone()[0]); cid = r[2]
    if r[0] != last: t16 = blk[r[3]:r[3] + r[4]].decode("utf-8").encode("utf-16-le"); last = r[0]
    ch = t16[r[5] * 2:r[6] * 2].decode("utf-16-le", "replace"); n += 1
    if "{{convert" in ch.lower(): lit += 1
    m = ART.search(ch)
    if m:
        hit += 1; arts.add(r[0])
        if len(ex) < 12: ex.append({"title": r[1], "ctx": ch[max(0, m.start() - 70):m.end() + 40].replace("\n", " ")})
    if ART_UNIT.search(ch): hit2 += 1; arts2.add(r[0])
res = {"pack": pack.split("/")[-1], "mod": mod, "articles_total": tot_art, "chunks_total": tot_ch, "chunks_scanned": n,
       "chunks_task_regex": hit, "articles_task_regex": len(arts), "chunks_broad_regex": hit2, "articles_broad_regex": len(arts2),
       "chunks_literal_convert": lit, "examples": ex}
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print({k: v for k, v in res.items() if k != "examples"})
