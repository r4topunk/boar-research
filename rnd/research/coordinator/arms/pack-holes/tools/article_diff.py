#!/usr/bin/env python3 -I
"""usage: article_diff.py <packA.sqlite> <packB.sqlite> <scanA.json> <out.json>   (python >= 3.14, read-only)
Which article titles have different cleaned text in B vs A, and which articles of A carry >= 1 hole chunk (scanA.hole_chunk_ids)."""
import sys, json, sqlite3, hashlib
from compression import zstd

def texts(pack):
    db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
    out = {}; blk = {}
    for aid, title, bid, off, ln in db.execute("select id,title,block_id,off,len from articles order by block_id,id"):
        if bid not in blk:
            blk = {bid: zstd.decompress(db.execute("select zdata from blocks where id=?", (bid,)).fetchone()[0])}
        out[title] = (aid, hashlib.sha1(blk[bid][off:off + ln]).hexdigest(), ln)
    return db, out

dbA, A = texts(sys.argv[1]); dbB, B = texts(sys.argv[2]); scan = json.load(open(sys.argv[3]))
changed = sorted(t for t in A if t in B and A[t][1] != B[t][1])
missing = sorted(set(A) ^ set(B))
holes = set(scan["hole_chunk_ids"]); art_with_hole = set()
for cid, aid in dbA.execute("select id, article_id from chunks"):
    if cid in holes: art_with_hole.add(aid)
titleA = {v[0]: t for t, v in A.items()}
hole_titles = sorted(titleA[a] for a in art_with_hole if a in titleA)
res = {"articles_A": len(A), "articles_B": len(B), "titles_only_in_one": missing[:50], "n_titles_only_in_one": len(missing),
       "n_changed": len(changed), "bytes_A": sum(v[2] for v in A.values()), "bytes_B": sum(v[2] for v in B.values()),
       "changed_titles": changed, "A_titles_with_hole_chunk": hole_titles}
json.dump(res, open(sys.argv[4], "w"), ensure_ascii=False)
print({k: v for k, v in res.items() if not isinstance(v, list)}, "A_hole_articles", len(hole_titles))
