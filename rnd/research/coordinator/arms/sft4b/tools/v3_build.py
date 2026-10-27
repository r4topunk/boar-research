"""SFT4B v3 step 1c-2: contexts (SFT4B-criterion-addendum-2, sha 653745c7...).
Per candidate (runs/v3/candidates.jsonl) and the engine's raw top-6 for its question (runs/v3/replay/<pack>.raw.jsonl):
  distractors = raw hits minus every chunk of the gold article (rank order); if < 2 remain usable, BM25 neighbours from the
  same pack (sqlite FTS5 over the question's words, gold article excluded) are appended.
Examples (seed 42):
  hold-out (84): 17 gold-absent (distractors only), 67 gold-present; train: all 1,499 articles gold-present + a gold-absent
  copy of a random 420 (same question, distractor-only context; the final selection sets the 15-25 % share).
  gold-present: 90 % designated two-gold (≈ half are downgraded when compression drops the 2nd chunk) (both pool chunks of the article, else the adjacent chunk of the same article).
  n distractors uniform in 2..5 (two-gold: 2..4; gold-absent: 3..5).
Rendering = render_prompt.render_raw (cut-7 compressContext budget 1200 + assembleChatMessages): pass 1 gives the kept set;
  distractors the compression dropped are replaced by unused ones (up to 8 attempts; BM25 pool 25); accepted if every gold chunk is kept
  (a two-gold whose 2nd chunk is dropped becomes single-gold) and >= 3 passages are shown (gold-absent: >= 3 distractors);
  pass 2 re-renders the same kept set in a random order (`order`: gold position random).
Writes runs/v3/contexts.jsonl. Usage: python3 -I v3_build.py"""
import json, os, random, re, sqlite3, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zstd_shim  # noqa: E402,F401
from render_prompt import PackDB, chunk_input, render_raw, ARM  # noqa: E402

V3 = f"{ARM}/runs/v3"; ATT = 8
STOP = set("a an the of to in on for and or is are was were be been do does did what which who whom how why when where can could "
           "should would will my your i you it its this that these those with from by at as about into than then there their they "
           "have has had not no if so any some much many more most".split())


def art_of(pack, cid):
    db = PackDB.get(pack).db
    r = db.execute("SELECT article_id FROM chunks WHERE id=?", (cid,)).fetchone()
    return r[0] if r else None


def adjacent(pack, aid, cids):
    db = PackDB.get(pack).db
    ids = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY id", (aid,))]
    for c in cids:
        for n in (c + 1, c - 1):
            if n in ids and n not in cids: return n
    return None


def bm25(pack, question, aid, exclude, n=25):
    words = [w for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in STOP and len(w) > 2]
    if not words: return []
    db = PackDB.get(pack).db
    q = " OR ".join(f'"{w}"' for w in dict.fromkeys(words))
    out = []
    try:
        rows = db.execute("SELECT rowid FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT 120", (q,)).fetchall()
    except sqlite3.Error:
        return []
    for (cid,) in rows:
        if cid in exclude: continue
        a = art_of(pack, cid)
        if a is None or a == aid: continue
        out.append(cid)
        if len(out) >= n: break
    return out


def main():
    rng = random.Random(42)
    cands = [json.loads(l) for l in open(f"{V3}/candidates.jsonl")]
    raw = {}
    for p in sorted({c["pack"] for c in cands}):
        for l in open(f"{V3}/replay/{p}.raw.jsonl"):
            d = json.loads(l); raw[d["id"]] = d
    ho = [c for c in cands if c["split"] == "holdout"]; tr = [c for c in cands if c["split"] == "train"]
    ho_absent = set(c["cid"] for c in rng.sample(ho, 17))
    tr_absent = set(c["cid"] for c in rng.sample(tr, 420))
    exs = []
    for c in cands:
        modes = ["absent"] if c["cid"] in ho_absent else ["present"]
        if c["split"] == "train" and c["cid"] in tr_absent: modes.append("absent")
        for m in modes: exs.append({**c, "mode": m, "xid": f"{c['cid']}:{m}"})
    stats = Counter()
    for e in exs:
        p, aid = e["pack"], e["article_id"]
        r = raw.get(e["cid"], {"raw": []})
        e["replay"] = {"task": r.get("task"), "query": r.get("query"), "k": r.get("k"), "n_raw": len(r.get("raw", []))}
        if e["mode"] == "present":
            gold = list(e["chunk_ids"])
            two = rng.random() < 0.90
            if two and len(gold) < 2:
                n = adjacent(p, aid, gold); gold = gold + [n] if n is not None else gold
            if not two: gold = gold[:1]
            e["gold_ids"] = gold; e["two_gold_designated"] = len(gold) == 2
            nd = rng.randint(2, 4 if len(gold) == 2 else 5)
        else:
            e["gold_ids"] = []; e["two_gold_designated"] = False; nd = rng.randint(3, 5)
        e["n_distractors_target"] = nd
        pool, seen = [], set()
        gold_chunk_ids = {f"pack:{p}:{g}" for g in e["chunk_ids"]}
        for x in r.get("raw", []):
            cid = x["chunkId"]; m = re.match(r"pack:local-([^:]+):(\d+)$", cid)
            if m and m.group(1) == p and art_of(p, int(m.group(2))) == aid: stats["raw_gold_article_hit"] += 1; continue
            if not x.get("body") or cid in seen: continue
            if m and m.group(1) == p: dist = {"src": "raw", **chunk_input(p, int(m.group(2)))}
            else: dist = {"src": "raw", "chunkId": cid, "title": x["title"], "body": x["body"]}
            seen.add(cid); pool.append(dist)
        used = {int(d["chunkId"].rsplit(":", 1)[1]) for d in pool if d["chunkId"].startswith(f"pack:{p}:")}
        for cid in bm25(p, e["question"], aid, used | set(e["chunk_ids"])):
            pool.append({"src": "bm25", **chunk_input(p, cid)})
        e["dist_pool"] = pool
        e["gold_inputs"] = [chunk_input(p, g) for g in e["gold_ids"]]
        assert not (gold_chunk_ids & {d["chunkId"] for d in pool})
    # rendering: up to 3 attempts, replacing dropped distractors with the next unused ones
    for e in exs:
        e["cur"] = e["dist_pool"][:e["n_distractors_target"]]; e["next"] = e["n_distractors_target"]; e["done"] = False
    for att in range(ATT):
        todo = [e for e in exs if not e["done"]]
        if not todo: break
        lines = []
        for e in todo:
            ch = e["gold_inputs"] + e["cur"]; ch = ch[:]; rng.shuffle(ch); e["inp"] = ch
            lines.append({"id": e["xid"], "question": e["question"], "chunks": [{k: v for k, v in c.items() if k != "src"} for c in ch]})
        out = {o["id"]: o for o in render_raw(lines)}
        for e in todo:
            o = out[e["xid"]]; kept = o["kept"]
            gk = [f"pack:{e['pack']}:{g}" for g in e["gold_ids"]]
            dk = [d for d in e["cur"] if d["chunkId"] in kept]
            gold_ok = (gk[0] in kept) if gk else True
            need = 2 if e["mode"] == "present" else 3
            if gold_ok and len(dk) >= need:
                if len(gk) == 2 and gk[1] not in kept: e["gold_ids"] = e["gold_ids"][:1]; e["gold_inputs"] = e["gold_inputs"][:1]; stats["two_gold_downgraded"] += 1
                e["done"] = True; e["kept1"] = kept; e["attempts"] = att + 1
                continue
            if not gold_ok: e["fail"] = "gold_dropped_by_compression"
            else:
                drop = [d for d in e["cur"] if d["chunkId"] not in kept]
                add = e["dist_pool"][e["next"]:e["next"] + len(drop)]; e["next"] += len(add)
                if not add: e["fail"] = "too_few_distractors_kept"
                e["cur"] = dk + add
            if att == ATT - 1 and not e.get("done"): e.setdefault("fail", "too_few_distractors_kept")
    ok = [e for e in exs if e["done"]]
    lines = []
    for e in ok:
        order = list(e["kept1"]); rng.shuffle(order); e["order"] = order
        ch = e["inp"]  # same input order as the accepted pass-1 render (compression depends on it)
        lines.append({"id": e["xid"], "question": e["question"], "chunks": [{k: v for k, v in c.items() if k != "src"} for c in ch], "keep": order, "order": order})
    out = {o["id"]: o for o in render_raw(lines)}
    with open(f"{V3}/contexts.jsonl", "w") as f:
        for e in ok:
            o = out[e["xid"]]
            assert o["kept"] == e["order"], e["xid"]
            gk = [f"pack:{e['pack']}:{g}" for g in e["gold_ids"]]
            gpos = [o["kept"].index(g) + 1 for g in gk]
            src = {d["chunkId"]: d["src"] for d in e["cur"]}
            rec = {k: e[k] for k in ("xid", "cid", "split", "pack", "article_id", "title", "question", "mode", "chunk_ids", "gold_ids", "two_gold_designated", "replay", "attempts")}
            rec |= {"messages": o["messages"], "kept": o["kept"], "gold_chunk_ids": gk, "gold_pos": gpos,
                    "distractor_chunk_ids": [k for k in o["kept"] if k not in gk], "distractor_src": [src.get(k) for k in o["kept"] if k not in gk],
                    "passages": o["messages"][0]["content"].split("\n\nContext:\n", 1)[1]}
            f.write(json.dumps(rec) + "\n")
            stats[f"ok_{e['split']}_{e['mode']}"] += 1; stats[f"n_shown_{len(o['kept'])}"] += 1
            if e["mode"] == "present": stats[f"gold_n_{len(gk)}"] += 1; stats[f"gold_pos1_{gpos[0]}"] += 1
            for s in rec["distractor_src"]: stats[f"dist_src_{s}"] += 1
    for e in exs:
        if not e["done"]: stats[f"fail_{e['split']}_{e['mode']}_{e.get('fail')}"] += 1
    print(json.dumps(dict(sorted(stats.items())), indent=0))


if __name__ == "__main__":
    main()
