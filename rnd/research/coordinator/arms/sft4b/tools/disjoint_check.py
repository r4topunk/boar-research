"""SFT4B stage 0, step 1: excluded-article list + seeded training/hold-out pool, disjoint from every self-test item.

Excluded per pack (11 packs, public self-test files only):
  - each item's source.article_id, plus any in_pack_facts[].article id;
  - every candidate article of the pack's item draw (draw-<pack>.json; conservative: drawn sources were item candidates);
  - every article whose title stem equals, or word-prefixes / is word-prefixed by, an excluded title's stem
    (stem = lowercase ASCII words, light suffix strip, "Library: " prefixes removed).
Pool (seed 42): eligible = not excluded, >= 1 chunk with 300..4000 chars of text; hold-out 100 articles reserved FIRST
(round-robin over packs: 10 for the first pack, 9 for the rest), then training candidates per pack
(140 for the 9 wave-1/2 packs, 120 for the 2 wave-3 packs = 1,500), 1-2 adjacent chunks each (2 with p 0.4);
Stack Exchange packs: the first chunk is drawn among answer chunks (a '# Answer…' heading precedes it) when the post has one.
Writes data/excluded-articles.json (ids + sha256 of title stems per pack), data/pool.jsonl, data/holdout-pool.jsonl,
aggregates/disjoint.json. Re-check mode (--check): asserts 0 overlaps of pool/hold-out (and any later dataset files given)
with the excluded ids and stems. Run: python3 -I disjoint_check.py [--check data/train.jsonl ...]"""
import hashlib, json, os, random, re, sys
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packs/tools")
from selftest_common import Pack, PACKS, OUT_DIR as ST, u16  # noqa: E402

ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, AGG = f"{ARM}/data", f"{ARM}/aggregates"
WAVE3 = {"qa-cooking-se", "qa-money-se"}
N_TRAIN = {p: (120 if p in WAVE3 else 140) for p in PACKS}
N_HOLD = 100
LIB = re.compile(r"^[^:]{2,40}:\s+")


def stem_word(t):
    if len(t) > 5 and t.endswith("ies"): return t[:-3] + "y"
    if len(t) > 4 and (t.endswith("es") or t.endswith("ed")): return t[:-2]
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"): return t[:-1]
    if len(t) > 5 and t.endswith("ing"): return t[:-3]
    return t


def tstem(title):
    return tuple(stem_word(w) for w in re.findall(r"[a-z0-9]+", LIB.sub("", title or "").lower()))


def h(s): return hashlib.sha256(" ".join(s).encode()).hexdigest()[:16]


def related(a, b):
    """same stem, or one is a word-prefix of the other (both non-empty)."""
    if not a or not b: return False
    n = min(len(a), len(b))
    return a[:n] == b[:n]


def build():
    rng = random.Random(42)
    excl, elig = {}, {}
    for p in PACKS:
        pk = Pack(p)
        ids = set()
        for l in open(f"{ST}/{p}.jsonl"):
            it = json.loads(l)
            ids.add(it["source"]["article_id"])
            for f in it.get("in_pack_facts", []):
                if f.get("article") is not None: ids.add(f["article"])
        dr = f"{ST}/draw-{p}.json"
        draw_ids = {c["id"] for c in json.load(open(dr)).get("candidates", [])} if os.path.exists(dr) else set()
        rows = pk.db.execute("SELECT id, title FROM articles").fetchall()
        title = dict(rows)
        stems = {tstem(title[i]) for i in ids | draw_ids if i in title}
        # long single-word stems only for prefix matching; exact match for everything
        by_first = {}
        for s in stems: by_first.setdefault(s[0] if s else "", []).append(s)
        same = set()
        for aid, t in rows:
            s = tstem(t)
            if not s: continue
            if any(related(s, x) for x in by_first.get(s[0], [])): same.add(aid)
        ex = ids | draw_ids | same
        excl[p] = {"item_articles": sorted(ids), "draw_articles": sorted(draw_ids - ids),
                   "same_stem_articles": sorted(same - ids - draw_ids), "all": sorted(ex),
                   "stems_sha16": sorted(h(s) for s in stems)}
        # eligible articles: shuffled ids, chunk-length check done lazily while sampling
        cand = [aid for aid, _ in rows if aid not in ex]
        rng.shuffle(cand)
        elig[p] = (pk, cand, {tstem(title[i]) for i in ex if i in title}, title)
    return excl, elig, rng


def pick_chunks(pk, aid, rng):
    text = pk.text(aid)
    rows = pk.db.execute("SELECT id, start, end FROM chunks WHERE article_id=? ORDER BY start", (aid,)).fetchall()
    # chunk offsets are JS (UTF-16) offsets: slice on the UTF-16 encoding
    b = text.encode("utf-16-le")
    good = [k for k, (cid, s, e) in enumerate(rows) if 300 <= len(b[2 * s:2 * e].decode("utf-16-le", "ignore").strip()) <= 4000]
    if pk.name.startswith("qa-"):  # Stack Exchange: prefer answer chunks (a heading "Answer ..." precedes the chunk)
        ans = [k for k in good if re.search(r"^#+\s+Answer", b[:2 * rows[k][1]].decode("utf-16-le", "ignore"), re.M)]
        good = ans or good
    if not good: return None
    k = rng.choice(good)
    ks = [k]
    if rng.random() < 0.4 and k + 1 < len(rows) and (k + 1) in good: ks.append(k + 1)
    return [rows[j][0] for j in ks], [j for j in ks]


def main():
    os.makedirs(DATA, exist_ok=True); os.makedirs(AGG, exist_ok=True)
    excl, elig, rng = build()
    used = {p: 0 for p in PACKS}  # index into each shuffled candidate list
    hold, pool = [], []

    def take(p, n, out, split):
        pk, cand, _, title = elig[p]
        got = 0
        while got < n and used[p] < len(cand):
            aid = cand[used[p]]; used[p] += 1
            r = pick_chunks(pk, aid, rng)
            if not r: continue
            out.append({"split": split, "pack": p, "article_id": aid, "title": title[aid], "chunk_ids": r[0], "chunk_index": r[1]})
            got += 1
        return got

    for i, p in enumerate(PACKS):
        take(p, 10 if i == 0 else 9, hold, "holdout")
    for p in PACKS:
        take(p, N_TRAIN[p], pool, "train")
    with open(f"{DATA}/holdout-pool.jsonl", "w") as f:
        for r in hold: f.write(json.dumps(r) + "\n")
    with open(f"{DATA}/pool.jsonl", "w") as f:
        for r in pool: f.write(json.dumps(r) + "\n")
    json.dump({"seed": 42, "packs": excl}, open(f"{DATA}/excluded-articles.json", "w"), indent=0)
    check([f"{DATA}/pool.jsonl", f"{DATA}/holdout-pool.jsonl"])


def extra_holdout(fail_file):
    """Replacement hold-out articles (one per article that failed 5 writer rounds), same pack, drawn with seed 4242 from the
    eligible articles used by neither the training pool nor the hold-out; appended to data/holdout-pool-extra.jsonl."""
    excl, elig, _ = build()
    used = {(r["pack"], r["article_id"]) for fn in ("pool", "holdout-pool", "holdout-pool-extra") if os.path.exists(f"{DATA}/{fn}.jsonl")
            for r in map(json.loads, open(f"{DATA}/{fn}.jsonl"))}
    rng = random.Random(4242); out = []
    for cid in open(fail_file).read().split():
        p = cid.rsplit(":", 1)[0]; pk, cand, _, title = elig[p]
        c2 = sorted(cand); rng.shuffle(c2)
        for aid in c2:
            if (p, aid) in used: continue
            r = pick_chunks(pk, aid, rng)
            if not r: continue
            used.add((p, aid)); out.append({"split": "holdout", "pack": p, "article_id": aid, "title": title[aid], "chunk_ids": r[0],
                                            "chunk_index": r[1], "replaces": cid}); break
    with open(f"{DATA}/holdout-pool-extra.jsonl", "a") as f:
        for r in out: f.write(json.dumps(r) + "\n")
    print("extra hold-out articles", len(out))


def check(files):
    ex = json.load(open(f"{DATA}/excluded-articles.json"))["packs"]
    titles = {}
    res = {"files": {}, "excluded_counts": {p: {k: len(v) for k, v in e.items() if k != "stems_sha16"} for p, e in ex.items()}}
    hold_ids = set()
    for hf in ("holdout-pool", "holdout-pool-extra"):
        if os.path.exists(f"{DATA}/{hf}.jsonl"):
            hold_ids |= {(r["pack"], r["article_id"]) for r in map(json.loads, open(f"{DATA}/{hf}.jsonl"))}
    for fn in files:
        rows = [json.loads(l) for l in open(fn) if l.strip()]
        ov_id = ov_stem = ov_hold = 0
        for r in rows:
            p, aid = r["pack"], r["article_id"]
            if aid in set(ex[p]["all"]): ov_id += 1
            if p not in titles: titles[p] = Pack(p)
            if h(tstem(titles[p].title(aid))) in set(ex[p]["stems_sha16"]): ov_stem += 1
            if r.get("split", "train") == "train" and (p, aid) in hold_ids: ov_hold += 1
        res["files"][os.path.relpath(fn, ARM)] = {"n": len(rows), "articles": len({(r["pack"], r["article_id"]) for r in rows}),
                                                  "per_pack": {p: sum(r["pack"] == p for r in rows) for p in PACKS},
                                                  "overlap_excluded_ids": ov_id, "overlap_same_stem": ov_stem, "train_in_holdout": ov_hold}
    json.dump(res, open(f"{AGG}/disjoint.json", "w"), indent=1)
    bad = sum(v["overlap_excluded_ids"] + v["overlap_same_stem"] + v["train_in_holdout"] for v in res["files"].values())
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "per_pack"} for k, v in res["files"].items()}))
    print("excluded total", sum(len(e["all"]) for e in ex.values()), "overlaps", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--extra-holdout":
        extra_holdout(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "--check":
        check(sys.argv[2:])
    else:
        main()
