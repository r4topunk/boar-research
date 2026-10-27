#!/usr/bin/env python3
"""exp-05 (1): cosine distributions question -> right article lead and question -> random article lead, WITHOUT and
WITH the BGE query prefix, against the SAME passage (lead) embeddings stored in the Wikipedia sample pack.

Re-does the measurement behind boar-app docs/KNOWLEDGE_PACKS.md (commit c87234a9: "right article p5 0.573 / median
0.776, random median 0.380 / p99 0.530"; the script itself was never committed):
- questions: eval/retrieval/questions.v1.jsonl (160, gold = one enwiki title), vectors from embed_queries.mjs;
- leads: boar-wiki-sample.sqlite `lead_vecs` (67,636 int8 vectors, embeddingModelSha256 ec38e8da…, built raw: no prefix);
- cosine exactly as the app (pure.ts cosineSimilarityInt8: on the int8 values, the stored scale does not matter);
- right  = cos(q, lead of the gold article), questions whose gold article has a lead vector;
- random = cos(q, every OTHER lead in the pack) (the full distribution instead of a sample, so p99 is stable).
Gap ("folga") = right p5 - random p99.

Cutoff re-positioning (same criterion as the 0.55 floor: keep ~98% of right, < 1% of random):
- MIN_SEMANTIC_SIMILARITY (0.55): new = right p2 of the prefixed distribution, reported with its random leak.
- ANSWER_MIN_SIMILARITY (0.7) and SEMANTIC_KEEP (0.7): high-confidence "keep without the question's words" gates.
  Mapped by quantile matching: the prefixed value that keeps the same share of right leads as 0.7 does raw.
Usage: python3 dist.py <pack.sqlite> qvecs.retrieval-v1.json questions.retrieval-v1.jsonl [out.json]
"""
import json, sqlite3, sys
import numpy as np

pack, qv_path, q_path = sys.argv[1:4]
out_path = sys.argv[4] if len(sys.argv) > 4 else "results/dist.json"
db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
ids, vecs = [], []
for aid, blob in db.execute("SELECT article_id, vec FROM lead_vecs ORDER BY article_id"):
    ids.append(aid)
    vecs.append(np.frombuffer(blob, dtype=np.int8))
ids = np.array(ids)
L = np.vstack(vecs).astype(np.float32)
L /= np.linalg.norm(L, axis=1, keepdims=True)
pos = {a: i for i, a in enumerate(ids)}


def article_id(title):
    r = db.execute("SELECT id FROM articles WHERE title = ? COLLATE NOCASE AND source = 0 ORDER BY views DESC LIMIT 1", (title,)).fetchone()
    if r:
        return r[0]
    r = db.execute("SELECT article_id FROM redirects WHERE title = ? LIMIT 1", (title,)).fetchone()
    return r[0] if r else None


Q = [json.loads(l) for l in open(q_path)]
QV = json.load(open(qv_path))
gold = {}
for q in Q:
    t = next((g["title"] for g in q.get("gold", []) if g.get("source") == "enwiki"), None)
    a = article_id(t) if t else None
    if a is not None and a in pos:
        gold[q["id"]] = pos[a]
res = {"pack_leads": int(len(ids)), "questions": len(Q), "questions_with_gold_lead": len(gold)}


def dist(variant):
    right, rnd = [], []
    for q in Q:
        if q["id"] not in gold:
            continue
        v = np.asarray(QV[variant][q["id"]], dtype=np.float32)
        v /= np.linalg.norm(v)
        s = L @ v
        g = gold[q["id"]]
        right.append(float(s[g]))
        rnd.append(np.delete(s, g))
    return np.array(right), np.concatenate(rnd)


def pct(a, p):
    return round(float(np.percentile(a, p)), 4)


for variant in ("raw", "prefixed"):
    r, x = dist(variant)
    res[variant] = {"right": {"n": len(r), "p2": pct(r, 2), "p5": pct(r, 5), "median": pct(r, 50)},
                    "random": {"n": int(len(x)), "median": pct(x, 50), "p99": pct(x, 99), "p99_4": pct(x, 99.4)},
                    "gap_p5_minus_p99": round(pct(r, 5) - pct(x, 99), 4)}
    res[variant]["_r"], res[variant]["_x"] = r, x

# cutoffs
r0, x0 = res["raw"].pop("_r"), res["raw"].pop("_x")
r1, x1 = res["prefixed"].pop("_r"), res["prefixed"].pop("_x")
share = lambda a, t: round(float((a >= t).mean()), 4)
cut = {}
# MIN_SEMANTIC_SIMILARITY: same criterion as the original (keeps 98% right, <1% random)
old = 0.55
new = pct(r1, 2)
cut["MIN_SEMANTIC_SIMILARITY"] = {"old": old, "old_keeps_right": share(r0, old), "old_leaks_random": share(x0, old),
                                  "new": new, "new_keeps_right": share(r1, new), "new_leaks_random": share(x1, new),
                                  "rule": "right p2 of the prefixed distribution (keep ~98% of right)"}
for name in ("ANSWER_MIN_SIMILARITY", "SEMANTIC_KEEP"):
    old = 0.7
    keep = share(r0, old)
    new = round(float(np.quantile(r1, 1 - keep)), 4)
    cut[name] = {"old": old, "old_keeps_right": keep, "old_leaks_random": share(x0, old),
                 "new": new, "new_keeps_right": share(r1, new), "new_leaks_random": share(x1, new),
                 "rule": "quantile match: same share of right leads kept as 0.7 keeps without the prefix"}
res["cutoffs"] = cut
import os
os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
json.dump(res, open(out_path, "w"), indent=1)
print(json.dumps(res, indent=1))

# ---- robustness (added after the first run): bootstrap CI of the gap, paired rank of the gold lead, vitalik set ----
rng = np.random.default_rng(20261001)


def gap_ci(r, x_by_q, B=2000):
    """Bootstrap over questions (right values and their random rows resampled together)."""
    n = len(r)
    gaps = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        rr = r[idx]
        xx = np.concatenate([x_by_q[i] for i in idx])
        gaps.append(np.percentile(rr, 5) - np.percentile(xx, 99))
    return [round(float(np.percentile(gaps, 2.5)), 4), round(float(np.percentile(gaps, 97.5)), 4)]


def per_question(qset, qvecs, golds):
    rows = []
    for qid, g in golds.items():
        out = {"id": qid}
        for variant in ("raw", "prefixed"):
            v = np.asarray(qvecs[variant][qid], dtype=np.float32)
            v /= np.linalg.norm(v)
            s = L @ v
            out[variant] = {"right": float(s[g]), "rank": int((s > s[g]).sum()) + 1, "x": np.delete(s, g)}
        rows.append(out)
    return rows


def summarize(rows, label):
    o = {"n": len(rows)}
    for variant in ("raw", "prefixed"):
        r = np.array([x[variant]["right"] for x in rows])
        xs = [x[variant]["x"] for x in rows]
        ranks = np.array([x[variant]["rank"] for x in rows])
        o[variant] = {"gap_ci95": gap_ci(r, xs), "rank_median": float(np.median(ranks)),
                      "semantic_recall_at_6": round(float((ranks <= 6).mean()), 4), "semantic_recall_at_1": round(float((ranks <= 1).mean()), 4)}
    d = np.array([x["prefixed"]["right"] - x["raw"]["right"] for x in rows])
    better = int(sum(x["prefixed"]["rank"] < x["raw"]["rank"] for x in rows))
    worse = int(sum(x["prefixed"]["rank"] > x["raw"]["rank"] for x in rows))
    o["paired"] = {"right_cos_delta_median": round(float(np.median(d)), 4), "rank_better": better, "rank_worse": worse,
                   "rank_same": len(rows) - better - worse}
    return o


import urllib.parse
rob = {"retrieval_v1": summarize(per_question(Q, QV, {q: gold[q] for q in gold}), "retrieval_v1")}
if len(sys.argv) > 6:
    vq = [json.loads(l) for l in open(sys.argv[6])]
    vv = json.load(open(sys.argv[5]))
    vg = {}
    for q in vq:
        if q.get("duplicate_of"):
            continue
        for u in q.get("reference_sources", []):
            if "wikipedia.org/wiki/" in u:
                a = article_id(urllib.parse.unquote(u.split("/wiki/")[1]).replace("_", " "))
                if a is not None and a in pos:
                    vg[q["id"]] = pos[a]
                    break
    rob["vitalik"] = summarize(per_question(vq, vv, vg), "vitalik")
    rob["vitalik"]["questions_with_gold_lead"] = len(vg)
res["robustness"] = rob
json.dump(res, open(out_path, "w"), indent=1)
print(json.dumps(rob, indent=1))
