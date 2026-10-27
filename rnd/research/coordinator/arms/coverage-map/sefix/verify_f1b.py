"""python3 -I verify_v3.py <name>... : v3 file vs its v2 source (read-only)."""
import sqlite3, sys, hashlib, os, json
S = "<workspace>/shared-data"; V = S + "/packs/v3proto"
SRC = {"qa-cooking-se": S + "/packs/wave3", "qa-money-se": S + "/packs/wave3"}
def sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""): h.update(b)
    return h.hexdigest()
out = {}
for n in sys.argv[1:]:
    s = sqlite3.connect(f"file:{SRC[n]}/{n}.sqlite?mode=ro", uri=True); v = sqlite3.connect(f"file:{V}/{n}.sqlite?mode=ro", uri=True)
    nc = v.execute("select count(*) from chunks").fetchone()[0]; ns = s.execute("select count(*) from chunks").fetchone()[0]
    nv = v.execute("select count(*) from chunk_vecs").fetchone()[0]
    miss = v.execute("select count(*) from chunks c left join chunk_vecs x on x.chunk_id=c.id where x.chunk_id is null").fetchone()[0]
    bad = v.execute("select count(*) from chunk_vecs where length(vec)!=384 or scale is null or scale<=0").fetchone()[0]
    mv = dict(v.execute("select key,value from meta").fetchall()); ms = dict(s.execute("select key,value from meta").fetchall())
    diff = {k: (ms.get(k), mv.get(k)) for k in set(ms) | set(mv) if ms.get(k) != mv.get(k)}
    out[n] = dict(chunks_src=ns, chunks_v3=nc, chunk_vecs=nv, chunks_without_vec=miss, bad_rows=bad, emb_sha_same=ms["embeddingModelSha256"] == mv["embeddingModelSha256"],
                  emb_sha=mv["embeddingModelSha256"][:12], meta_diff=diff, src_sha=sha(f"{SRC[n]}/{n}.sqlite")[:12], v3_sha=sha(f"{V}/{n}.sqlite")[:12],
                  src_bytes=os.path.getsize(f"{SRC[n]}/{n}.sqlite"), v3_bytes=os.path.getsize(f"{V}/{n}.sqlite"),
                  ok=(nv == nc == ns and miss == 0 and bad == 0 and ms["embeddingModelSha256"] == mv["embeddingModelSha256"] and set(diff) <= {"densechunk"}))
print(json.dumps(out, indent=1))
