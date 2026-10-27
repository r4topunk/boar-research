"""Read the boar-factbook v3proto pack (read-only): articles with text, page_id, url/license/attribution, aliases."""
import sqlite3
from compression import zstd
SRC = "<workspace>/shared-data/packs/v3proto/boar-factbook.sqlite"
def articles(path=SRC):
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True); blocks = {}
    meta = {r[0]: r[1:] for r in c.execute("select article_id, url, license, attribution from article_meta")}
    al = {}
    for t, a in c.execute("select title, article_id from redirects"): al.setdefault(a, []).append(t)
    out = []
    for aid, src, pid, title, views, b, off, ln in c.execute("select id, source, page_id, title, views, block_id, off, len from articles order by id"):
        if b not in blocks: blocks = {b: zstd.decompress(c.execute("select zdata from blocks where id=?", (b,)).fetchone()[0])}
        text = blocks[b][off:off + ln].decode("utf8")
        u, li, at = meta.get(aid, (None, None, None))
        out.append(dict(id=aid, page_id=pid, title=title, views=views, text=text, url=u, license=li, attribution=at, aliases=sorted(al.get(aid, []))))
    return out
def chunks(path=SRC):
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    return c.execute("select id, article_id, start, end from chunks order by id").fetchall()
