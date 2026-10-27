"""Shared helpers for the pack self-test scripts (T-K4b). Read-only on the packs."""
import os, re, sqlite3

BOAR = "<workspace>"
PACK_DIR = os.path.join(BOAR, "shared-data/packs/wave1")
PACK_DIRS = [os.path.join(BOAR, "shared-data/packs/wave4"), os.path.join(BOAR, "shared-data/packs/wave3"), PACK_DIR, os.path.join(BOAR, "shared-data/packs/wave2")]  # wave3 first (2026-10-13)
OUT_DIR = os.path.join(BOAR, "rnd/research/coordinator/arms/pack-nist/selftest")  # PACK-NIST: arm-local copy
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en",
         "qa-cooking-se", "qa-money-se", "boar-nist-crypto"]  # wave 3 (2026-10-13)
SOURCES = ["enwiki", "enwikivoyage", "enwikibooks", "appropedia", "usgov", "eips", "ethspecs", "ethereumorg",
           "bips", "stackexchange", "medlineplus", "factbook", "simplewiki"]


class Pack:
    def __init__(self, name):
        import zstandard
        self.name = name
        path = next((os.path.join(d, name + ".sqlite") for d in PACK_DIRS
                     if os.path.exists(os.path.join(d, name + ".sqlite"))), None)
        if path is None:
            raise FileNotFoundError(name)
        self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        self.dz = zstandard.ZstdDecompressor()
        self._blk = (None, None)

    def rows(self):
        return self.db.execute("SELECT id, source, title, views, block_id, off, len FROM articles ORDER BY id").fetchall()

    def block(self, bid):
        if self._blk[0] != bid:
            z = self.db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
            self._blk = (bid, self.dz.decompress(z, max_output_size=1 << 27))
        return self._blk[1]

    def text(self, aid):
        b, o, l = self.db.execute("SELECT block_id, off, len FROM articles WHERE id=?", (aid,)).fetchone()
        return self.block(b)[o:o + l].decode("utf-8")

    def title(self, aid):
        return self.db.execute("SELECT title FROM articles WHERE id=?", (aid,)).fetchone()[0]

    def source(self, aid):
        return SOURCES[self.db.execute("SELECT source FROM articles WHERE id=?", (aid,)).fetchone()[0]]

    def chunks(self, aid):
        return self.db.execute("SELECT start, end FROM chunks WHERE article_id=? ORDER BY start", (aid,)).fetchall()

    def meta(self, aid):
        cols = {c[1] for c in self.db.execute("PRAGMA table_info(article_meta)")}
        if "attribution" in cols:
            r = self.db.execute("SELECT url, license, attribution FROM article_meta WHERE article_id=?", (aid,)).fetchone()
            return r or (None, None, None)
        # boar-simplewiki-en has no attribution column: derive the CC BY-SA credit line from url + title
        r = self.db.execute("SELECT url, license FROM article_meta WHERE article_id=?", (aid,)).fetchone()
        if not r:
            return (None, None, None)
        return (r[0], r[1], f"\"{self.title(aid)}\", Simple English Wikipedia contributors ({r[0]})")


def u16(s):
    """Length of s in UTF-16 code units (the engine's chunk offsets are JS string offsets)."""
    return len(s.encode("utf-16-le")) // 2


def chunk_index(text, chunks, quote):
    i = text.find(quote)
    if i < 0:
        return None
    pos = u16(text[:i])
    idx = 0
    for k, (s, e) in enumerate(chunks):
        if s <= pos:
            idx = k
    return idx


WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def words(s):
    return WORD.findall(s.lower())


def jaccard(a, b):
    A, B = set(words(a)), set(words(b))
    return len(A & B) / max(1, len(A | B))


def shared_span(a, b, n=6):
    wa, wb = words(a), words(b)
    grams = {tuple(wb[i:i + n]) for i in range(len(wb) - n + 1)}
    for i in range(len(wa) - n + 1):
        if tuple(wa[i:i + n]) in grams:
            return " ".join(wa[i:i + n])
    return None


def se_names(attribution):
    """Display names from a Stack Exchange attribution line ('Q by NAME (url); A by NAME (no profile)')."""
    return [m.strip() for m in re.findall(r"(?:Q|A) by (.+?) \((?:https?://[^)]*|no profile)\)", attribution or "")]
