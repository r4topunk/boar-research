"""T-K4b self-test checks (0 LLM calls). Prints counts only (failing item ids + check names on failure).

  python3 -I selftest_check.py [pack ...]

Checks per item: schema; answer 40-120 words; rubric 3-5 fact bullets + exactly one "Penalize:" bullet;
1-3 in_pack_facts, each quote <= 300 chars and a verbatim substring of the article (the fact's own
"article" id when present: wave-2 packs, comparison items cite two articles), chunk_index matches
the pack; word-Jaccard(question, quote) <= 0.30 for every quote; no 6-word span shared by the question and
any cited article; no SE display name (from attribution) in question/answer/rubric; English (ASCII share >= 0.97,
common English stopwords present). Per pack: 20 items, ids st-<pack>-NNN, distinct articles,
>= 8 items with a fact at chunk_index >= 1, style mix (each of first-person/direct/imperative >= 5).
"""
import json, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_common import Pack, PACKS, OUT_DIR, chunk_index, jaccard, shared_span, se_names, words  # noqa: E402

STOP = {"the", "a", "is", "of", "to", "and", "in", "for", "it", "or", "you", "be"}
KEYS = {"id", "pack", "category", "style", "question", "answer", "rubric", "in_pack_facts", "source"}


def english(s):
    if not s:
        return False
    ascii_share = sum(c.isascii() for c in s) / len(s)
    return ascii_share >= 0.97 and len(STOP & set(words(s))) >= 2


def check(name):
    path = os.path.join(OUT_DIR, f"{name}.jsonl")
    rows = [json.loads(l) for l in open(path) if l.strip()]
    pack = Pack(name)
    fails = Counter()
    bad = []
    nonlead = 0
    styles = Counter()
    for n, r in enumerate(rows, 1):
        errs = []
        if set(r) != KEYS:
            errs.append("schema")
        if r.get("id") != f"st-{name}-{n:03d}":
            errs.append("id")
        styles[r.get("style")] += 1
        aid = r["source"]["article_id"]
        text, ch = pack.text(aid), pack.chunks(aid)
        url, lic, attr = pack.meta(aid)
        if (r["source"].get("url"), r["source"].get("license"), r["source"].get("attribution")) != (url, lic, attr):
            errs.append("source-meta")
        if r["source"].get("title") != pack.title(aid):
            errs.append("source-title")
        if not (40 <= len(r["answer"].split()) <= 120):
            errs.append("answer-len")
        rub = r["rubric"]
        pen = [b for b in rub if b.startswith("Penalize:")]
        if len(pen) != 1 or not (3 <= len(rub) - 1 <= 5):
            errs.append("rubric")
        facts = r["in_pack_facts"]
        if not (1 <= len(facts) <= 3):
            errs.append("facts-n")
        has_nonlead = False
        arts_cited = {aid}
        for f in facts:
            q = f["quote"]
            ftext, fch = text, ch
            if "article" in f:  # wave-2 format: the fact names its article (comparisons cite two)
                arts_cited.add(f["article"])
                ftext, fch = pack.text(f["article"]), pack.chunks(f["article"])
            if len(q) > 300:
                errs.append("quote-len")
            if q not in ftext:
                errs.append("quote-verbatim")
                continue
            if chunk_index(ftext, fch, q) != f["chunk_index"]:
                errs.append("chunk-index")
            if f["chunk_index"] >= 1:
                has_nonlead = True
            if jaccard(r["question"], q) > 0.30:
                errs.append("jaccard")
        nonlead += has_nonlead
        if any(shared_span(r["question"], pack.text(a), 6) for a in arts_cited):
            errs.append("6gram")
        blob = " ".join([r["question"], r["answer"], " ".join(rub)])
        for nm in se_names(attr):
            if len(nm) >= 4 and re.search(r"(?<![\w@])" + re.escape(nm) + r"(?![\w])", blob):
                errs.append("personal-name")
        if not english(r["question"] + " " + r["answer"]):
            errs.append("english")
        for e in errs:
            fails[e] += 1
        if errs:
            bad.append((r["id"], sorted(set(errs))))
    arts = len({r["source"]["article_id"] for r in rows})
    pack_errs = []
    if len(rows) != 20:
        pack_errs.append("count")
    if arts != len(rows):
        pack_errs.append("dup-article")
    if nonlead < 8:
        pack_errs.append("nonlead<8")
    if min(styles.get(s, 0) for s in ("first-person", "direct", "imperative")) < 5:
        pack_errs.append("style-mix")
    ok = not bad and not pack_errs
    print(f"{name}: items={len(rows)} nonlead={nonlead} styles={dict(styles)} item_fails={len(bad)} "
          f"pack_fails={pack_errs or 0} {'PASS' if ok else 'FAIL'}")
    for i, e in bad:
        print(f"  {i}: {','.join(e)}")
    return ok


if __name__ == "__main__":
    packs = sys.argv[1:] or [p for p in PACKS if os.path.exists(os.path.join(OUT_DIR, f"{p}.jsonl"))]
    res = [check(p) for p in packs]
    print(f"packs={len(res)} pass={sum(res)}")
    sys.exit(0 if all(res) else 1)
