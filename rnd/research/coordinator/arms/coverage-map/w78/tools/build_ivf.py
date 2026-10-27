#!/usr/bin/env python3
"""W78C: IVF sidecar over a pack's int8 lead vectors (0 LLM): spherical k-means, k = 256, seed 42, init = 256 random rows, 25 Lloyd iterations, max-cosine assignment.
Skips packs with rows < 39 * k. File <out_dir>/<manifestSha256[:16]>.ivf256 = b'W78CIV\\0\\0' + uint32 n + uint32 dims + uint32 k + int32 article_id[n] (ascending)
+ float32 centroids[k*dims] (unit norm) + uint32 listStart[k+1] + uint32 row[n] (row = index in ascending article_id order, ascending within each list).
Usage: python3 -I build_ivf.py <out_dir> <pack.sqlite> [...]"""
import sys, os, json, sqlite3, struct, hashlib, time
import numpy as np
K = 256; ITERS = 25
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for pack in sys.argv[2:]:
    t0 = time.time()
    db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
    meta = dict(db.execute("select key, value from meta"))
    dims = int(meta["dims"]); man = meta["manifestSha256"]
    rows = db.execute("select article_id, vec from lead_vecs order by article_id").fetchall()
    n = len(rows)
    if n < 39 * K:
        print(json.dumps(dict(pack=pack, rows=n, skipped="rows < 39 x 256"))); continue
    ids = np.array([r[0] for r in rows], dtype="<i4")
    x = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.int8).reshape(n, dims).astype(np.float32)
    nr = np.linalg.norm(x, axis=1); nr[nr == 0] = 1; x /= nr[:, None]
    t1 = time.time()
    rng = np.random.default_rng(42)
    C = x[rng.choice(n, K, replace=False)].copy()
    def assign(C):
        a = np.empty(n, dtype=np.int64)
        for s in range(0, n, 65536): a[s:s + 65536] = (x[s:s + 65536] @ C.T).argmax(1)
        return a
    for it in range(ITERS):
        a = assign(C)
        S = np.zeros_like(C); np.add.at(S, a, x)
        cnt = np.bincount(a, minlength=K)
        for j in np.where(cnt == 0)[0]: S[j] = x[rng.integers(n)]  # empty list: reseed
        C = S / np.maximum(np.linalg.norm(S, axis=1, keepdims=True), 1e-9)
    a = assign(C)
    kmeans_s = time.time() - t1
    order = np.argsort(a, kind="stable").astype("<u4")  # ascending row within each list
    cnt = np.bincount(a, minlength=K); start = np.concatenate([[0], np.cumsum(cnt)]).astype("<u4")
    blob = b"W78CIV\0\0" + struct.pack("<III", n, dims, K) + ids.tobytes() + C.astype("<f4").tobytes() + start.tobytes() + order.tobytes()
    name = f"{man[:16]}.ivf256"; p = os.path.join(out, name)
    open(p, "wb").write(blob)
    info = dict(pack=pack, name=meta.get("name"), manifestSha256=man, rows=n, dims=dims, k=K, iters=ITERS, bytes=len(blob), list_min=int(cnt.min()), list_p50=int(np.median(cnt)),
                list_max=int(cnt.max()), empty_lists=int((cnt == 0).sum()), sha256=hashlib.sha256(blob).hexdigest(), kmeans_assign_s=round(kmeans_s, 2), build_s=round(time.time() - t0, 2))
    json.dump(info, open(p + ".json", "w"), indent=1)
    print(json.dumps(info))
