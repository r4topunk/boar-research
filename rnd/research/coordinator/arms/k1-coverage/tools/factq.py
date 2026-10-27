#!/usr/bin/env python3
"""Read-only multi-pack fact query (0 LLM), FACT-REACH 2026-10-21. Usage:
  factq.py <pack> fts '<fts5 query>' [limit] [grep]   -> matching chunks (title / text), optionally only chunks containing <grep>
  factq.py <pack> title '<article title>' [grep]      -> chunks of one article
Packs opened mode=ro. BOAR_PACKS overrides the root (the mini uses <runner>/shared-data/packs)."""
import sqlite3, sys, functools, os
from compression import zstd
R = os.environ.get("BOAR_PACKS", "<workspace>/shared-data/packs")
P = {"top": "boar-wiki-en-top100k.sqlite", "wv": "boar-wikivoyage-en.sqlite",
     "cr": "../crypto/boar-crypto.sqlite", "sw": "wave2/boar-simplewiki-en.sqlite",
     "fb": "wave2/boar-factbook.sqlite", "cook": "wave3/qa-cooking-se.sqlite", "money": "wave3/qa-money-se.sqlite",
     "trav": "wave1/qa-travel-se.sqlite", "eth": "wave1/qa-ethereum-se.sqlite", "btc": "wave1/qa-bitcoin-se.sqlite",
     "health": "wave1/qa-health-se.sqlite", "out": "wave1/qa-outdoors-se.sqlite", "fa": "wave1/boar-firstaid-en.sqlite",
     "med": "wave1/boar-medlineplus-en.sqlite", "visa": "wave4/boar-visa-en.sqlite", "vit": "wave4/boar-vitalik-blog-en.sqlite",
     "nist": "wave4/boar-nist-crypto.sqlite", "v5": "wiki-vital5.sqlite"}
db = sqlite3.connect(f"file:{os.path.join(R, P[sys.argv[1]])}?mode=ro", uri=True)
@functools.lru_cache(maxsize=64)
def block(bid): return zstd.decompress(db.execute("select zdata from blocks where id=?", (bid,)).fetchone()[0])
def art_text(aid):
    b, off, ln, t = db.execute("select block_id, off, len, title from articles where id=?", (aid,)).fetchone()
    return t, block(b)[off:off + ln].decode("utf-8", "replace")
def chunk(cid):
    aid, s, e = db.execute("select article_id, start, end from chunks where id=?", (cid,)).fetchone()
    t, txt = art_text(aid); return t, txt[s:e]
mode, q = sys.argv[2], sys.argv[3]
if mode == "fts":
    lim = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    g = sys.argv[5].lower() if len(sys.argv) > 5 else None
    for (rid,) in db.execute("select rowid from fts where fts match ? order by rank limit ?", (q, lim)):
        t, c = chunk(rid)
        if g and g not in c.lower(): continue
        if g:
            i = c.lower().find(g); c = c[max(0, i - 300):i + 400]
        print(f"--- [{rid}] {t}\n{c[:700]}\n")
else:
    g = sys.argv[4].lower() if len(sys.argv) > 4 else None
    r = db.execute("select id from articles where title = ? collate nocase", (q,)).fetchone()
    if not r: r = db.execute("select article_id from redirects where title = ?", (q,)).fetchone()
    if not r: print("NO ARTICLE"); sys.exit()
    for cid, s, e in db.execute("select id, start, end from chunks where article_id=? order by start", (r[0],)):
        t, c = chunk(cid)
        if g is None or g in c.lower(): print(f"--- [{cid}] {t}\n{c[:900]}\n")
