"""SFT4B v3 step 1a: candidates = the 1,500 disjoint train articles (v1/v2 question per article, as write_v2.v1_questions) and the
84 v2 hold-out articles (v2 question). Writes runs/v3/candidates.jsonl and one replay question file per pack
(runs/v3/replay/<pack>.questions.jsonl, ids "<split>:<pack>:<article_id>"). Usage: python3 -I v3_prep.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zstd_shim  # noqa: E402,F401
from write_v2 import v1_questions, ARM  # noqa: E402

out = f"{ARM}/runs/v3"; os.makedirs(f"{out}/replay", exist_ok=True)
cands = []
for k, v in sorted(v1_questions("train").items()):
    cands.append({"split": "train", "pack": k[0], "article_id": k[1], "title": v["title"], "chunk_ids": v["chunk_ids"], "question": v["question"]})
for l in open(f"{ARM}/data/holdout.v2.meta.jsonl"):
    m = json.loads(l)
    cands.append({"split": "holdout", "pack": m["pack"], "article_id": m["article_id"], "title": m["title"], "chunk_ids": m["chunk_ids"], "question": m["question"]})
for c in cands: c["cid"] = f"{c['split']}:{c['pack']}:{c['article_id']}"
assert len({c["cid"] for c in cands}) == len(cands)
with open(f"{out}/candidates.jsonl", "w") as f:
    for c in cands: f.write(json.dumps(c) + "\n")
packs = sorted({c["pack"] for c in cands})
for p in packs:
    with open(f"{out}/replay/{p}.questions.jsonl", "w") as f:
        for c in cands:
            if c["pack"] == p: f.write(json.dumps({"id": c["cid"], "question": c["question"]}) + "\n")
print(len(cands), {s: sum(c["split"] == s for c in cands) for s in ("train", "holdout")}, packs)
