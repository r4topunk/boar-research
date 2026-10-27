#!/usr/bin/env python3
"""Read-only pack query (0 LLM). Usage:
  packq.py <sw|top> fts '<fts5 query>' [limit]      -> matching chunks (title / section / text)
  packq.py <sw|top> title '<article title>' [grep]  -> chunks of one article, optionally only those containing <grep> (case-insensitive)
Packs: sw = v3proto boar-simplewiki-en (99bcec30), top = boar-wiki-en-top100k (9123b372), wv = boar-wikivoyage-en (ff8595e3), cr = boar-crypto (ae9fbd2c). Opened with mode=ro."""
import sqlite3, sys, functools
from compression import zstd
P = {"sw": "<workspace>/shared-data/packs/v3proto/boar-simplewiki-en.sqlite",
     "top": "<workspace>/shared-data/packs/boar-wiki-en-top100k.sqlite",
     "wv": "<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite",
     "cr": "<workspace>/shared-data/crypto/boar-crypto.sqlite"}
db = sqlite3.connect(f"file:{P[sys.argv[1]]}?mode=ro", uri=True)
@functools.lru_cache(maxsize=64)
def block(bid): return zstd.decompress(db.execute("select zdata from blocks where id=?", (bid,)).fetchone()[0])
def art_text(aid):
    b, off, ln, t = db.execute("select block_id, off, len, title from articles where id=?", (aid,)).fetchone()
    return t, block(b)[off:off + ln].decode("utf-8", "replace")
def chunk(cid):
    aid, s, e = db.execute("select article_id, start, end from chunks where id=?", (cid,)).fetchone()
    t, txt = art_text(aid)
    return t, txt.encode()[s:e].decode("utf-8", "replace") if False else txt[s:e]
mode, q = sys.argv[2], sys.argv[3]
if mode == "fts":
    lim = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    for (rid,) in db.execute("select rowid from fts where fts match ? order by rank limit ?", (q, lim)):
        t, c = chunk(rid); print(f"--- [{rid}] {t}\n{c[:700]}\n")
else:
    g = sys.argv[4].lower() if len(sys.argv) > 4 else None
    r = db.execute("select id from articles where title = ? collate nocase", (q,)).fetchone()
    if not r:
        r = db.execute("select article_id from redirects where title = ?", (q,)).fetchone()
    if not r: print("NO ARTICLE"); sys.exit()
    for cid, s, e in db.execute("select id, start, end from chunks where article_id=? order by start", (r[0],)):
        t, c = chunk(cid)
        if g is None or g in c.lower(): print(f"--- [{cid}] {t}\n{c[:900]}\n")
