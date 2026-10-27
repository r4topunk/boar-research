#!/usr/bin/env python3
"""FTDATA 1k (copy of the pilot sampler; changes vs pilot marked "1k:"): seeded sample of passages from the local BOAR knowledge packs.

Criterion: ../FTDATA-1K-criterion.md (sha 1a6b43dc...). Seed 47, 1,000 examples, 2-4 passages each, <= 1,200 words.
1k: pilot titles (passages-50.jsonl source_titles) excluded; quotas x20; distractor articles are not marked used
(usgov source 4 has 206 articles: 140 unique gold + ~70 unique distractors would exhaust it); gold articles stay unique;
exhaustion guard: after 50*len(pool) failed draws a gold draw relaxes min chunks to 2, then raises.
Sources: enwiki + enwikivoyage (packs/boar-wiki-sample.sqlite), crypto (crypto/boar-crypto.sqlite),
usgov (preparedness-v3/boar-preparedness-en.sqlite, source 4). Bench exclusion: titles from boar-eval/bench/v0.1
(reference URLs, gold city/wikivoyage fields) plus any article title found verbatim in a v0.1 question text.
Never touches blind/, rnd/veil/ or bench v0.2. Text extraction mirrors src/rag/wikiPack.ts (zstd blocks; chunk
offsets are UTF-16 code units). Usage: python3 sample_passages_1k.py [out.jsonl]
"""
import json, random, re, sqlite3, subprocess, sys, urllib.parse
from pathlib import Path

SEED = 47
N = 1000
MAX_WORDS = 1200
MIN_GOLD_WORDS = 200  # pilot choice: enough source text for a 120-220 word answer without padding
BOAR = Path("<workspace>")
SD = BOAR / "shared-data"
BENCH = BOAR / "boar-eval/bench/v0.1"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "passages-1k.jsonl"
PILOT_PASSAGES = Path(__file__).resolve().parent.parent / "passages-50.jsonl"
SOURCES = ["enwiki", "enwikivoyage", "enwikibooks", "appropedia", "usgov", "eips", "ethspecs", "ethereumorg", "bips"]
# (label, db, allowed source ids, quota)
PLAN = [
    ("enwiki", SD / "packs/boar-wiki-sample.sqlite", [0], 520),
    ("enwikivoyage", SD / "packs/boar-wiki-sample.sqlite", [1], 200),
    ("crypto", SD / "crypto/boar-crypto.sqlite", None, 140),
    ("usgov", SD / "preparedness-v3/boar-preparedness-en.sqlite", [4], 140),
]
SKIP_TITLE = re.compile(r"^(List of|Index of|Outline of|Timeline of)|\(disambiguation\)|^\d{4}( in |$)", re.I)


def bench_exclusions():
    titles, qtexts = set(), []
    for line in (BENCH / "questions.public.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        q = json.loads(line)
        qtexts.append(q["question"].lower())
        for u in q.get("reference_sources", []):
            m = re.search(r"wiki(?:pedia|voyage)\.org/wiki/([^#?\s]+)", u)
            if m:
                titles.add(urllib.parse.unquote(m.group(1)).replace("_", " ").lower())
    for g in (BENCH / "gold").glob("*.json"):
        if g.name == "sources.json":
            continue
        d = json.loads(g.read_text())
        for k in ("city", "wikivoyage"):
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, str):
                titles.add(v.replace("_", " ").lower())
    return titles, qtexts


def pilot_titles():  # 1k: disjoint from the pilot
    return {t.lower() for l in PILOT_PASSAGES.read_text().splitlines() if l.strip() for t in json.loads(l)["source_titles"]}


def excluded(title, titles, qtexts):
    t = title.lower()
    if t in titles:
        return True
    if len(t) >= 4:
        pat = re.compile(r"\b" + re.escape(t) + r"\b")
        if any(pat.search(q) for q in qtexts):
            return True
    return False


class Pack:
    def __init__(self, path):
        self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        self.blocks = {}

    def block(self, bid):
        if bid not in self.blocks:
            z = self.db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
            self.blocks[bid] = subprocess.run(["zstd", "-d", "-c", "-q"], input=z, capture_output=True, check=True).stdout
        return self.blocks[bid]

    def article(self, aid):
        title, src, bid, off, ln = self.db.execute(
            "SELECT title, source, block_id, off, len FROM articles WHERE id=?", (aid,)).fetchone()
        text = self.block(bid)[off:off + ln].decode("utf-8", "replace")
        u16 = text.encode("utf-16-le")
        chunks = [u16[2 * s:2 * e].decode("utf-16-le", "replace").strip()
                  for s, e in self.db.execute("SELECT start, end FROM chunks WHERE article_id=? ORDER BY start", (aid,))]
        return title, SOURCES[src] if src < len(SOURCES) else str(src), [c for c in chunks if len(c.split()) >= 25]


def words(ps):
    return sum(len(p["text"].split()) for p in ps)


def main():
    rng = random.Random(SEED)
    titles, qtexts = bench_exclusions()
    ptitles = pilot_titles()
    used, out, rejected = set(), [], {"bench": 0, "pilot": 0, "title_pattern": 0, "too_short": 0, "relaxed_gold": 0, "distractor_repeat": 0}
    seen_d = set()
    for label, path, srcs, quota in PLAN:
        pack = Pack(path)
        q = "SELECT id FROM articles" + (f" WHERE source IN ({','.join(map(str, srcs))})" if srcs else "")
        ids = [r[0] for r in pack.db.execute(q)]

        def draw(min_chunks, gold=True, avoid=None):
            tries = 0
            while True:
                tries += 1
                if tries > 50 * len(ids):  # 1k: exhaustion guard
                    if gold and min_chunks > 2:
                        min_chunks, tries = 2, 0; rejected["relaxed_gold"] += 1; continue
                    raise RuntimeError(f"{label}: pool exhausted (min_chunks={min_chunks}, gold={gold})")
                aid = rng.choice(ids)
                if (str(path), aid) in used or aid == avoid:
                    continue
                title, src, chunks = pack.article(aid)
                if SKIP_TITLE.search(title):
                    rejected["title_pattern"] += 1; continue
                if excluded(title, titles, qtexts):
                    rejected["bench"] += 1; continue
                if title.lower() in ptitles:
                    rejected["pilot"] += 1; continue
                if len(chunks) < min_chunks or (min_chunks > 1 and sum(len(c.split()) for c in chunks) < MIN_GOLD_WORDS):
                    rejected["too_short"] += 1; continue
                if gold:
                    used.add((str(path), aid))
                else:  # 1k: distractors are not marked used (repeats counted)
                    if (str(path), aid) in seen_d:
                        rejected["distractor_repeat"] += 1
                    seen_d.add((str(path), aid))
                return (title, src, chunks, aid) if gold else (title, src, chunks)

        for _ in range(quota):
            k = rng.choice([2, 3, 4])
            distractor = rng.random() < 0.5  # recipe: gold + distractor share (~45% in the 1k mix)
            n_gold = k - 1 if distractor else k
            title, src, chunks, gaid = draw(max(n_gold, 2))
            n_gold = min(n_gold, len(chunks))  # 1k: only differs from the pilot after a relaxed gold draw
            start = 0 if rng.random() < 0.5 else rng.randrange(0, len(chunks) - n_gold + 1)
            sel = chunks[start:start + n_gold]
            # grow the gold window (still <= 4 passages) until it has MIN_GOLD_WORDS
            lo, hi = start, start + n_gold
            while sum(len(c.split()) for c in sel) < MIN_GOLD_WORDS and len(sel) < (3 if distractor else 4):
                if hi < len(chunks): hi += 1
                elif lo > 0: lo -= 1
                else: break
                sel = chunks[lo:hi]
            if sum(len(c.split()) for c in sel) < MIN_GOLD_WORDS:  # merge neighbours into the passages instead
                per = max(1, -(-(len(chunks)) // len(sel)))
                sel = ["\n\n".join(chunks[i:i + per]) for i in range(0, len(chunks), per)][:len(sel)]
            ps = [{"title": title, "source": src, "text": c, "role": "gold"} for c in sel]
            if distractor:
                dt, dsrc, dch = draw(1, gold=False, avoid=gaid)
                ps.insert(rng.randrange(0, len(ps) + 1), {"title": dt, "source": dsrc, "text": rng.choice(dch), "role": "distractor"})
            while words(ps) > MAX_WORDS and len(ps) > 2:
                ps.pop(max(i for i, p in enumerate(ps) if p["role"] == "gold"))
            if words(ps) > MAX_WORDS:  # truncate last passage at a word boundary
                over = words(ps) - MAX_WORDS
                # 1k: if the overflow is >= the last passage (pilot code would blank it and stay over the cap),
                # truncate the longest passage instead. No RNG use, so other examples are unchanged.
                j = -1 if over < len(ps[-1]["text"].split()) else max(range(len(ps)), key=lambda i: len(ps[i]["text"].split()))
                ps[j]["text"] = " ".join(ps[j]["text"].split()[:-over])
            out.append({"id": f"ft1k-{len(out) + 1:04d}", "pack": label,
                        "source_titles": sorted({p["title"] for p in ps}), "passages": ps, "words": words(ps)})
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    w = sorted(r["words"] for r in out)
    print(json.dumps({"written": str(OUT), "n": len(out), "excl_titles": len(titles), "pilot_titles": len(ptitles),
                      "gold_overlaps_distractor": len({(a, b) for a, b in used} & seen_d), "rejected": rejected,
                      "words_min_med_max": [w[0], w[len(w) // 2], w[-1]],
                      "with_distractor": sum(any(p["role"] == "distractor" for p in r["passages"]) for r in out)}))


if __name__ == "__main__":
    main()
