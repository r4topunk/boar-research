#!/usr/bin/env python3
"""W78-PACKFMT builder (0 LLM): copy a format-2 pack and add the IVF-256 layout as tables (additive; lead_vecs and every other table unchanged).
k-means = W78C build_ivf.py exactly (spherical, k 256, seed 42, init 256 random rows, 25 Lloyd iterations, max-cosine assignment); with --check <.ivf256> the
lists, ids and centroids are asserted byte-equal to the W78C sidecar.
Tables: lead_ivf(list_id INTEGER PRIMARY KEY, n INTEGER, ids BLOB int32[n], vecs BLOB int8[n*dims])  -- members ascending article_id
        lead_ivf_cent(id INTEGER PRIMARY KEY, k INTEGER, dims INTEGER, cents BLOB f32[k*dims], counts BLOB u32[k], pages BLOB u32[k])  -- pages = leaf + overflow (dbstat)
        meta.leadIvf = JSON.
Usage: python3 -I pack_ivf.py <src.sqlite> <out.sqlite> <out.json> [--check sidecar.ivf256]"""
import sys, os, json, sqlite3, struct, hashlib, time, shutil
import numpy as np
K = 256; ITERS = 25
src, out, outjson = sys.argv[1:4]
check = sys.argv[sys.argv.index("--check") + 1] if "--check" in sys.argv else None
T0 = time.time()
shutil.copyfile(src, out); copy_s = time.time() - T0
t0 = time.time()
db = sqlite3.connect(out)
db.execute("pragma journal_mode=DELETE")
meta = dict(db.execute("select key, value from meta"))
dims = int(meta["dims"]); man = meta["manifestSha256"]
page_size = db.execute("pragma page_size").fetchone()[0]
pages_before = db.execute("pragma page_count").fetchone()[0]
rows = db.execute("select article_id, vec from lead_vecs order by article_id").fetchall()
n = len(rows)
ids = np.array([r[0] for r in rows], dtype="<i4")
raw = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.int8).reshape(n, dims)
x = raw.astype(np.float32)
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
    for j in np.where(cnt == 0)[0]: S[j] = x[rng.integers(n)]
    C = S / np.maximum(np.linalg.norm(S, axis=1, keepdims=True), 1e-9)
a = assign(C)
kmeans_s = time.time() - t1
order = np.argsort(a, kind="stable").astype("<u4")
cnt = np.bincount(a, minlength=K); start = np.concatenate([[0], np.cumsum(cnt)]).astype("<u4")
cents = C.astype("<f4")
checked = None
if check:
    b = open(check, "rb").read()
    assert b[:8] == b"W78CIV\0\0"
    n2, d2, k2 = struct.unpack("<III", b[8:20]); assert (n2, d2, k2) == (n, dims, K)
    o = 20; ids2 = np.frombuffer(b, "<i4", n, o); o += 4 * n
    c2 = np.frombuffer(b, "<f4", K * dims, o); o += 4 * K * dims
    s2 = np.frombuffer(b, "<u4", K + 1, o); o += 4 * (K + 1)
    r2 = np.frombuffer(b, "<u4", n, o)
    assert (ids2 == ids).all() and (s2 == start).all() and (r2 == order).all() and c2.tobytes() == cents.tobytes(), "differs from the W78C sidecar"
    checked = dict(sidecar=check, sha256=hashlib.sha256(b).hexdigest(), equal=True)
t2 = time.time()
db.execute("drop table if exists lead_ivf"); db.execute("drop table if exists lead_ivf_cent")
db.execute("create table lead_ivf (list_id INTEGER PRIMARY KEY, n INTEGER NOT NULL, ids BLOB NOT NULL, vecs BLOB NOT NULL)")
for j in range(K):
    mem = order[start[j]:start[j + 1]]  # ascending row = ascending article_id
    db.execute("insert into lead_ivf values (?,?,?,?)", (j, int(len(mem)), ids[mem].astype("<i4").tobytes(), raw[mem].tobytes()))
db.commit()
# pages per list row from dbstat: leaf pages in path order hold cells in rowid order; overflow page path = <leaf path><cell %03x>+<%06x>
st = db.execute("select path, pagetype, ncell from dbstat where name='lead_ivf' order by path").fetchall()
leaves = [(p, nc) for p, t, nc in st if t == "leaf"]
ovf = {}
for p, t, nc in st:
    if t == "overflow": key = p.split("+")[0]; ovf[key] = ovf.get(key, 0) + 1
pages = np.zeros(K, dtype="<u4"); j = 0
for p, nc in leaves:
    for c in range(nc): pages[j] = 1 + ovf.get(f"{p}{c:03x}", 0); j += 1
assert j == K, (j, K)
assert int(pages.sum()) - K == sum(ovf.values())
db.execute("create table lead_ivf_cent (id INTEGER PRIMARY KEY, k INTEGER NOT NULL, dims INTEGER NOT NULL, cents BLOB NOT NULL, counts BLOB NOT NULL, pages BLOB NOT NULL)")
db.execute("insert into lead_ivf_cent values (0,?,?,?,?,?)", (K, dims, cents.tobytes(), cnt.astype("<u4").tobytes(), pages.tobytes()))
info_meta = dict(k=K, dims=dims, seed=42, iters=ITERS, layout="w78-packfmt-v1", sourceSidecarSha256=(checked or {}).get("sha256"))
db.execute("insert or replace into meta(key, value) values ('leadIvf', ?)", (json.dumps(info_meta),))
db.commit()
pages_after = db.execute("pragma page_count").fetchone()[0]
db.close()
write_s = time.time() - t2
h = hashlib.sha256()
with open(out, "rb") as f:
    for blk in iter(lambda: f.read(1 << 22), b""): h.update(blk)
info = dict(src=src, out=out, name=meta.get("name"), manifestSha256=man, rows=n, dims=dims, k=K, page_size=page_size, list_min=int(cnt.min()), list_p50=int(np.median(cnt)), list_max=int(cnt.max()),
            empty_lists=int((cnt == 0).sum()), list_pages_total=int(pages.sum()), list_bytes_payload=int(n * (dims + 4)), added_bytes=(pages_after - pages_before) * page_size,
            out_bytes=os.path.getsize(out), out_sha256=h.hexdigest(), checked=checked, copy_s=round(copy_s, 2), load_s=round(t1 - t0, 2), kmeans_assign_s=round(kmeans_s, 2),
            write_dbstat_s=round(write_s, 2), build_s_excl_copy=round(t2 - t0 + write_s, 2))
json.dump(info, open(outjson, "w"), indent=1)
print(json.dumps(info))
