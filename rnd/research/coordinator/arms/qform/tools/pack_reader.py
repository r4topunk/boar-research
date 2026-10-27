"""Read-only reader for BOAR format-2 packs (zstd blocks, UTF-16 chunk offsets as in wikiPack.ts). Stdlib only (python 3.14)."""
import sqlite3
from compression import zstd

SOURCES = ["enwiki", "enwikivoyage", "enwikibooks", "appropedia", "usgov", "eips", "ethspecs", "ethereumorg",
           "bips", "stackexchange", "medlineplus", "factbook", "simplewiki"]


class Pack:
    def __init__(self, path):
        self.path = path
        self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        self._blk = (None, None)

    def block(self, bid):
        if self._blk[0] != bid:
            z = self.db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
            self._blk = (bid, zstd.decompress(z))
        return self._blk[1]

    def text(self, aid):
        b, o, l = self.db.execute("SELECT block_id, off, len FROM articles WHERE id=?", (aid,)).fetchone()
        return self.block(b)[o:o + l].decode("utf-8")

    def title(self, aid):
        return self.db.execute("SELECT title FROM articles WHERE id=?", (aid,)).fetchone()[0]

    def chunks(self, aid):
        """[(chunk_id, start, end)] ordered by start (UTF-16 offsets)."""
        return self.db.execute("SELECT id, start, end FROM chunks WHERE article_id=? ORDER BY start", (aid,)).fetchall()

    def chunk_text(self, aid, idx):
        t16 = self.text(aid).encode("utf-16-le")
        cid, s, e = self.chunks(aid)[idx]
        return cid, t16[2 * s:2 * e].decode("utf-16-le").strip()

    def articles(self):
        return self.db.execute("SELECT id, source, title, views, block_id, off, len FROM articles ORDER BY id").fetchall()
