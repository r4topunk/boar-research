"""FOLLOWUP pairs (0 LLM): tools/fu_draft.tsv (t1 self-test id, target chunk id, agent-written follow-up) -> runs/../pairs.jsonl + gold.json.
Checks: target chunk belongs to the t1 item's source article and is not one of its fact chunks; 2-3 per pack; draw order respected.
Skips (draw order, seed 999): st-qa-travel-se-009 (only non-fact chunk is the question body); st-boar-factbook-019 (not needed: 3 factbook items reached)."""
import json, sqlite3, sys
ROOT = "<workspace>"; ST = f"{ROOT}/rnd/research/packs/selftest"; A = f"{ROOT}/rnd/research/coordinator/arms/followup"
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
KF = dict(l.rstrip("\n").split("\t") for l in open(f"{A}/tools/fu_rubric.tsv") if l.strip())
rows = [l.rstrip("\n").split("\t") for l in open(f"{A}/tools/fu_draft.tsv") if l.strip()]
out, gold = [], {}
for n, (tid, cid, q2) in enumerate(rows, 1):
    pack = tid[3:].rsplit("-", 1)[0]; it = next(json.loads(l) for l in open(f"{ST}/{pack}.jsonl") if json.loads(l)["id"] == tid)
    db = sqlite3.connect(f"file:{pub(pack)}?mode=ro", uri=True); aid = it["source"]["article_id"]
    cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (aid,))]
    facts = {cs[f["chunk_index"]] for f in it["in_pack_facts"] if f.get("chunk_index") is not None and f.get("article", aid) == aid and f["chunk_index"] < len(cs)}
    c = int(cid); assert c in cs, (tid, c); assert c not in facts, (tid, c)
    pid = f"fu-{n:02d}"; words = len(q2.split())
    out.append({"id": pid, "pack": pack, "t1_id": tid, "t1": it["question"], "t2": q2, "t2_words": words,
                "article_id": aid, "article_title": it["source"]["title"], "gold_chunk": c, "gold_chunk_index": cs.index(c),
                "t1_fact_chunks": sorted(facts), "t2_key_fact": KF[pid]})
    gold[pid] = {"pack": pack, "chunk": c}
open(f"{A}/pairs.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
json.dump(gold, open(f"{A}/gold.json", "w"), indent=1)
from collections import Counter; print(len(out), dict(Counter(r["pack"] for r in out)), "max words", max(r["t2_words"] for r in out))
