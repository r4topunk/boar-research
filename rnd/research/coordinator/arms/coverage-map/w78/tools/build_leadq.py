#!/usr/bin/env python3
"""W78C: build a per-row-scaled 4-bit or 2-bit sidecar of a pack's int8 lead vectors (0 LLM).
File <out_dir>/<manifestSha256[:16]>.lead<bits> = b'W78CQ<bits>\\0\\0' + uint32 n + uint32 dims + int32 article_id[n] (ascending) + float32 factor[n] + uint8 codes[n*dims*bits/8].
int4: scale = max|v|/7, c = round(v/scale) in [-7,7], byte p = (c[2p]+8) | (c[2p+1]+8) << 4, factor = scale/||v||.
int2: levels (2c-3)*step/2, c = clip(floor(v/step)+2, 0, 3), step = argmin SSE over mean|v| x linspace(0.3, 2.0, 35), byte p = c[4p] | c[4p+1]<<2 | c[4p+2]<<4 | c[4p+3]<<6,
factor = (step/2)/||v||. Approx score = factor * sum_d q_d * level_d (a cosine estimate up to ||q||).
Usage: python3 -I build_leadq.py <out_dir> <4|2> <pack.sqlite> [...]"""
import sys, os, json, sqlite3, struct, hashlib, time
import numpy as np
out = sys.argv[1]; bits = int(sys.argv[2]); os.makedirs(out, exist_ok=True)
assert bits in (2, 4)
for pack in sys.argv[3:]:
    t0 = time.time()
    db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
    meta = dict(db.execute("select key, value from meta"))
    dims = int(meta["dims"]); man = meta["manifestSha256"]
    rows = db.execute("select article_id, vec from lead_vecs order by article_id").fetchall()
    ids = np.array([r[0] for r in rows], dtype="<i4")
    m = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.int8).reshape(len(rows), dims).astype(np.float32)
    norm = np.sqrt((m * m).sum(1)).astype(np.float32); norm[norm == 0] = 1
    if bits == 4:
        scale = np.abs(m).max(1) / 7; scale[scale == 0] = 1
        c = np.clip(np.rint(m / scale[:, None]), -7, 7).astype(np.int16) + 8
        codes = (c[:, 0::2] | (c[:, 1::2] << 4)).astype(np.uint8)
        factor = (scale / norm).astype("<f4"); rec = (c - 8) * scale[:, None]
    else:
        ma = np.abs(m).mean(1); ma[ma == 0] = 1
        best = None
        for t in np.linspace(0.3, 2.0, 35):
            step = ma * t
            c = np.clip(np.floor(m / step[:, None]) + 2, 0, 3)
            err = ((m - (2 * c - 3) * step[:, None] / 2) ** 2).sum(1)
            if best is None: best = (err, step.copy())
            else:
                b = err < best[0]; best[0][b] = err[b]; best[1][b] = step[b]
        step = best[1]; c = np.clip(np.floor(m / step[:, None]) + 2, 0, 3).astype(np.int16)
        codes = (c[:, 0::4] | (c[:, 1::4] << 2) | (c[:, 2::4] << 4) | (c[:, 3::4] << 6)).astype(np.uint8)
        factor = ((step / 2) / norm).astype("<f4"); rec = (2 * c - 3) * step[:, None] / 2
    assert codes.shape == (len(rows), dims * bits // 8)
    cosrec = ((rec * m).sum(1) / (np.sqrt((rec * rec).sum(1)) * norm + 1e-9)).mean()
    blob = f"W78CQ{bits}".encode() + b"\0\0" + struct.pack("<II", len(rows), dims) + ids.tobytes() + factor.tobytes() + codes.tobytes()
    name = f"{man[:16]}.lead{bits}"; p = os.path.join(out, name)
    open(p, "wb").write(blob)
    info = dict(pack=pack, name=meta.get("name"), manifestSha256=man, bits=bits, rows=len(rows), dims=dims, bytes=len(blob), scan_bytes_per_row=dims * bits // 8 + 4,
                int8_lead_bytes=int(m.size), mean_cos_reconstruction=round(float(cosrec), 4), sha256=hashlib.sha256(blob).hexdigest(), build_s=round(time.time() - t0, 2))
    json.dump(info, open(p + ".json", "w"), indent=1)
    print(json.dumps(info))
