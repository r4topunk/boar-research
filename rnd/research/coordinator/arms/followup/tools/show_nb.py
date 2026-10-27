"""Authoring aid (0 LLM): for a self-test item, print question, fact chunk indices and the neighbour chunks' text (first N chars).
Usage: .venv python -I show_nb.py <item id> [chars]"""
import json, sys
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packs/tools")
from selftest_common import Pack
ST = "<workspace>/rnd/research/packs/selftest"
iid = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 500
pack = iid[3:].rsplit("-", 1)[0]
it = next(json.loads(l) for l in open(f"{ST}/{pack}.jsonl") if json.loads(l)["id"] == iid)
P = Pack(pack); aid = it["source"]["article_id"]; text = P.text(aid); ch = P.db.execute("SELECT id, start, end FROM chunks WHERE article_id=? ORDER BY start", (aid,)).fetchall()
fi = sorted({f["chunk_index"] for f in it["in_pack_facts"] if f.get("chunk_index") is not None and f.get("article", aid) == aid})
print(f"== {iid} | {P.title(aid)} | aid {aid} | chunks {len(ch)} | fact idx {fi}\nQ: {it['question']}")
def seg(c):
    # chunks rows: (id, start, end) in UTF-16 offsets
    b = text.encode("utf-16-le"); return b[c[1]*2:c[2]*2].decode("utf-16-le")
for i, c in enumerate(ch):
    tag = "FACT" if i in fi else "nb"
    print(f"-- [{i}] id {c[0]} {tag}: " + " ".join(seg(c).split())[:N])
