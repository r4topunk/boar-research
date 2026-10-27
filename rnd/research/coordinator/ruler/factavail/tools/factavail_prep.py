#!/usr/bin/env python3
"""FACT-AVAIL prep (0 LLM): for every v0.4 checklist point, collect candidate passages from the A-union packs by lexical search.
usage: python3 -I factavail_prep.py <out_units.jsonl>
Per (item, point): two FTS5 queries per pack (q1 = the point's content words, q2 = the item's first user turn's content words), OR of quoted
terms, bm25 order, top 2 chunks per query per pack; union, deduplicated by (pack, chunk id), max 24 passages, pack order fixed.
Chunk text = the article text (zstd block) sliced with the chunk's UTF-16 offsets (same as arms/oracle-st/tools/build_oracle.py).
Prints counts only (never item, point or passage text)."""
import hashlib, json, re, sqlite3, subprocess, sys
BOAR = "<workspace>"
ITEMS = f"{BOAR}/boar-eval/bench/v0.4/items.jsonl"; ITEMS_SHA = "f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594"
PDIR = f"{BOAR}/shared-data/packs/persona-a-union"
PACKS = {  # A-union text packs (persona-map-v1 r1), file sha256 pinned
    "boar-wikivoyage-en": "ff8595e32f56b8b84e20", "boar-visa-en": "d1dd0ffb58a8e4f9b50a", "boar-crypto": "ae9fbd2c7a46a46a815d",
    "boar-medlineplus-en": "c9ac4dcfdae367d4502c", "boar-firstaid-en": "8cfab0b47ec8c5cb3284", "boar-factbook": "c585435354a413d04790"}
K_PER_QUERY, MAX_PASSAGES = 2, 24
STOP = set("""a an and are as at be been but by can could did do does for from had has have how i if in into is it its may might more most
must not of on or our should so such than that the their them then there these they this to too up was were what when where which while who
whom why will with would you your about also any each just like many much only other over some very use used using one two answer
question include includes including mention mentions mentioned state states explain explains give gives note notes should""".split())
sha = lambda b: hashlib.sha256(b).hexdigest()


def terms(text):
    ws = [w.lower() for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']+", text)]
    out = []
    for w in ws:
        w = w.strip("-'")
        if len(w) >= 3 and w not in STOP and w not in out: out.append(w)
    return out[:24]


def fts_query(ts):
    return " OR ".join('"' + t.replace('"', "") + '"' for t in ts)


class Pack:
    def __init__(self, name):
        p = f"{PDIR}/{name}.sqlite"
        h = sha(open(p, "rb").read())
        assert h.startswith(PACKS[name]), (name, h[:20])
        self.name, self.sha = name, h
        self.db = sqlite3.connect(f"file:{p}?mode=ro", uri=True); self.blocks = {}

    def article_text(self, aid):
        bid, off, ln, title = self.db.execute("SELECT block_id, off, len, title FROM articles WHERE id=?", (aid,)).fetchone()
        if bid not in self.blocks:
            z = self.db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
            self.blocks[bid] = subprocess.run(["zstd", "-dc"], input=bytes(z), capture_output=True, check=True).stdout
        return self.blocks[bid][off:off + ln].decode("utf-8"), title

    def chunk(self, cid):
        aid, s, e = self.db.execute("SELECT article_id, start, end FROM chunks WHERE id=?", (cid,)).fetchone()
        text, title = self.article_text(aid)
        u = text.encode("utf-16-le")
        return {"pack": self.name, "chunk": cid, "title": title, "text": u[2 * s:2 * e].decode("utf-16-le", errors="surrogatepass").strip()}

    def search(self, ts, k):
        if not ts: return []
        try:
            return [r[0] for r in self.db.execute("SELECT rowid FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT ?", (fts_query(ts), k))]
        except sqlite3.OperationalError:
            return []


def main():
    b = open(ITEMS, "rb").read(); assert sha(b) == ITEMS_SHA, "items sha"
    items = [json.loads(l) for l in b.decode().splitlines() if l.strip()]
    packs = [Pack(n) for n in PACKS]
    units, npass = [], []
    for it in items:
        q2 = terms(it["turns"][0])
        for k, point in enumerate(it["checklist"]):
            q1 = terms(point); seen, ps = set(), []
            for pk in packs:
                for cid in pk.search(q1, K_PER_QUERY) + pk.search(q2, K_PER_QUERY):
                    if (pk.name, cid) in seen: continue
                    seen.add((pk.name, cid)); ps.append(pk.chunk(cid))
            ps = ps[:MAX_PASSAGES]; npass.append(len(ps))
            units.append({"key": f"{it['id']}|{k}", "id": it["id"], "point_index": k, "n_points": len(it["checklist"]),
                          "question": "\n".join(it["turns"]), "point": point, "passages": ps})
    with open(sys.argv[1], "w") as f:
        for u in units: f.write(json.dumps(u, ensure_ascii=False) + "\n")
    print(json.dumps({"units": len(units), "items": len(items), "passages_median": sorted(npass)[len(npass) // 2],
                      "units_without_passages": sum(n == 0 for n in npass), "packs": {p.name: p.sha for p in packs},
                      "out_sha256": sha(open(sys.argv[1], "rb").read())}, indent=1))


if __name__ == "__main__":
    main()
