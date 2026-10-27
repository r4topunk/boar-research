#!/usr/bin/env python3
"""W78-BINARY: build a 1-bit sign sidecar of a pack's int8 lead vectors (0 LLM).
File <out_dir>/<manifestSha256[:16]>.leadbits = b'W78LB1\\0\\0' + uint32 n + uint32 dims + int32 article_id[n] (ascending)
+ uint8 bits[n * dims/8] (bit d of row i = lead_vecs.vec[d] > 0, LSB-first within each byte). Also writes <name>.json (pack path, sha, counts).
Usage: python3 -I build_leadbits.py <out_dir> <pack.sqlite> [...]"""
import sys, os, json, sqlite3, struct, hashlib, time
import numpy as np
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for pack in sys.argv[2:]:
    t0 = time.time()
    db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
    meta = dict(db.execute("select key, value from meta"))
    dims = int(meta["dims"]); man = meta["manifestSha256"]
    rows = db.execute("select article_id, vec from lead_vecs order by article_id").fetchall()
    ids = np.array([r[0] for r in rows], dtype="<i4")
    m = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.int8).reshape(len(rows), dims)
    assert all(len(r[1]) == dims for r in rows)
    bits = np.packbits(m > 0, axis=1, bitorder="little")
    assert bits.shape == (len(rows), dims // 8)
    blob = b"W78LB1\0\0" + struct.pack("<II", len(rows), dims) + ids.tobytes() + bits.tobytes()
    name = man[:16] + ".leadbits"; p = os.path.join(out, name)
    open(p, "wb").write(blob)
    info = dict(pack=pack, name=meta.get("name"), manifestSha256=man, rows=len(rows), dims=dims, bytes=len(blob),
                int8_lead_bytes=int(m.size), sha256=hashlib.sha256(blob).hexdigest(), build_s=round(time.time() - t0, 2))
    json.dump(info, open(p + ".json", "w"), indent=1)
    print(json.dumps(info))
