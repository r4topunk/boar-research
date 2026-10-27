#!/usr/bin/env python3
"""Read-only: print JSON {title: {"resolved", "len", "sections", "text"}} for titles (stdin JSON list) from a format-2 pack.
Usage: f2text.py PACK.sqlite < titles.json   (also run on the Mac mini for boar-wiki-en-top100k via ssh)."""
import json, sqlite3, sys, compression.zstd as z
db = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
out = {}
for t in json.load(sys.stdin):
    row = db.execute("SELECT id, title, block_id, off, len FROM articles WHERE title = ? COLLATE NOCASE ORDER BY views DESC LIMIT 1", (t,)).fetchone()
    if not row:
        r = db.execute("SELECT article_id FROM redirects WHERE title = ? COLLATE NOCASE LIMIT 1", (t,)).fetchone()
        if r: row = db.execute("SELECT id, title, block_id, off, len FROM articles WHERE id = ?", (r[0],)).fetchone()
    if not row: out[t] = None; continue
    blk = z.decompress(db.execute("SELECT zdata FROM blocks WHERE id = ?", (row[2],)).fetchone()[0])
    text = blk[row[3]:row[3] + row[4]].decode("utf-8", "replace")
    out[t] = {"resolved": row[1], "len": len(text), "sections": [l.strip("# ").strip() for l in text.splitlines() if l.startswith("## ")], "text": text}
json.dump(out, sys.stdout)
