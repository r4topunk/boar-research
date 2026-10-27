"""T-K4b self-test sampling + fill (0 LLM calls).

  python3 -I selftest_draw.py draw [pack ...]        seeded draw (seed 11) of 60 candidates per pack
                                                      -> rnd/research/packs/selftest/draw-<pack>.json
                                                      (keeps any hand-written "chosen"/"rejects" already there)
  python3 -I selftest_draw.py show <pack> <id> [max]  print an article with chunk markers (authoring aid)
  python3 -I selftest_draw.py fill <pack> <draft.jsonl>
                                                      fill source{} and in_pack_facts[].chunk_index from the pack
                                                      -> rnd/research/packs/selftest/<pack>.jsonl

Draw protocol: eligible articles are split in length terciles; SE packs additionally in view terciles
(3x3 cells) and prefer questions with an accepted answer and >= 2 answers, skipping titles that look
closed/duplicate/meta; firstaid is stratified by source x length tercile; medlineplus by length x views.
60 candidates are drawn as evenly as possible across cells with random.Random(11). The 20 picks and the
40 one-word reject reasons are written by the author into the draw file. Prints counts only.
"""
import json, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selftest_common import Pack, PACKS, OUT_DIR, chunk_index, u16  # noqa: E402

SEED = 11
N_CAND = 60
BAD_TITLE = re.compile(r"\b(closed|duplicate|meta|off[- ]topic|this site|stack exchange)\b", re.I)


def terciles(vals):
    s = sorted(vals)
    return s[len(s) // 3], s[2 * len(s) // 3]


def tier(v, cuts):
    return 0 if v < cuts[0] else (1 if v < cuts[1] else 2)


FB_REGION = {"africa": "africa", "europe": "europe", "central-asia": "asia", "east-n-southeast-asia": "asia",
             "middle-east": "asia", "south-asia": "asia", "north-america": "americas",
             "central-america-n-caribbean": "americas", "south-america": "americas",
             "australia-oceania": "oceania"}
# simplewiki broad topic: keyword hits in the first 1200 chars (title + lead); >= 2 hits for the top topic, else skipped
SW_TOPICS = {
    "science": "physics chemistry chemical mathematics mathematical theorem equation atom atoms molecule element "
               "energy force planet star galaxy astronomy orbit universe particle quantum geology mineral "
               "physicist chemist mathematician scientist experiment theory temperature",
    "history": "war battle empire dynasty king queen emperor revolution century ancient medieval treaty army "
               "politician president prime minister monarch kingdom invasion colonial reign historical",
    "geography": "city town village river mountain lake island county province region capital population "
                 "located district state municipality sea ocean valley border census commune",
    "biology/health": "species animal plant disease medical medicine health cell cells bird fish mammal insect "
                      "genus family bacteria virus symptoms treatment body organ blood infection evolution",
    "technology": "computer software technology internet engine machine device electronic programming network "
                  "aircraft car vehicle railway company digital system invented engineering video game",
    "arts/society": "music singer band album song film actor actress novel writer painter art artist television "
                    "religion football player sport team language culture philosophy poet book",
}
SW_KW = {t: set(v.split()) for t, v in SW_TOPICS.items()}
SW_BAD = re.compile(r"^(list of|lists of|\d{1,4}( bc)?$|\d{3,4}s$|(january|february|march|april|may|june|july|august|"
                    r"september|october|november|december)( \d+)?$)|disambiguation|^leap year", re.I)


def sw_topic(title, text):
    w = re.findall(r"[a-z]+", (title + " " + text[:1200]).lower())
    score = {t: sum(1 for x in w if x in kw) for t, kw in SW_KW.items()}
    best = max(score, key=lambda t: (score[t], t))
    return best if score[best] >= 2 else None


def fb_population(text):
    m = re.search(r"^Population: ([\d,]+)", text.split("\n## ", 1)[0], re.M)
    return int(m.group(1).replace(",", "")) if m else None


def eligible(pack):
    out = []
    if pack.name == "boar-factbook":
        for aid, src, title, views, bid, off, ln in pack.rows():
            t = pack.block(bid)[off:off + ln].decode("utf-8")
            url = pack.meta(aid)[0] or ""
            m = re.search(r"/master/([^/]+)/", url)
            reg = FB_REGION.get(m.group(1) if m else "")
            pop = fb_population(t)
            if ln < 1500 or reg is None or not pop:
                continue
            out.append({"id": aid, "source": src, "title": title, "views": pop, "len": ln, "region": reg})
        return out
    if pack.name == "boar-simplewiki-en":
        for aid, src, title, views, bid, off, ln in pack.rows():
            if ln < 1500 or SW_BAD.search(title):
                continue
            t = pack.block(bid)[off:off + ln].decode("utf-8")
            top = sw_topic(title, t)
            if top is None:
                continue
            out.append({"id": aid, "source": src, "title": title, "views": views, "len": ln, "topic": top})
        return out
    se = pack.name.startswith("qa-")
    for aid, src, title, views, bid, off, ln in pack.rows():
        if ln < 1500 or BAD_TITLE.search(title):
            continue
        if se:
            t = pack.block(bid)[off:off + ln].decode("utf-8")
            n_ans = t.count("\n### Answer (score")
            if n_ans < 2 or "accepted)" not in t:
                continue
        out.append({"id": aid, "source": src, "title": title, "views": views, "len": ln})
    return out


def draw(name):
    pack = Pack(name)
    pool = eligible(pack)
    lc = terciles([a["len"] for a in pool])
    vc = terciles([a["views"] for a in pool])
    cells = {}
    for a in pool:
        if name == "boar-firstaid-en":
            key = (a["source"], tier(a["len"], lc))
        elif name == "boar-factbook":
            key = (a["region"], tier(a["views"], vc))  # views field holds the Key-facts population
        elif name == "boar-simplewiki-en":
            key = (a["topic"], tier(a["len"], lc))
        elif name == "boar-nist-crypto":  # PACK-NIST: document family x length tercile
            fam = a["title"].split(" — ")[0] if " — " in a["title"] else "NIST glossary"
            key = (fam, tier(a["len"], lc))
        else:
            key = (tier(a["len"], lc), tier(a["views"], vc))
        a["cell"] = list(key)
        cells.setdefault(key, []).append(a)
    rng = random.Random(SEED)
    keys = sorted(cells)
    for k in keys:
        rng.shuffle(cells[k])
    cand, i = [], 0
    while len(cand) < N_CAND and any(cells[k] for k in keys):
        k = keys[i % len(keys)]
        if cells[k]:
            cand.append(cells[k].pop())
        i += 1
    path = os.path.join(OUT_DIR, f"draw-{name}.json")
    prev = json.load(open(path)) if os.path.exists(path) else {}
    doc = {
        "pack": name, "seed": SEED, "eligible": len(pool),
        "strata": "source x length tercile" if name == "boar-firstaid-en" else
                  "region (url path -> africa/europe/asia/americas/oceania) x population tercile (Key facts); "
                  "entries without a Key-facts population (oceans, Antarctica, World) excluded; 'views' = population"
                  if name == "boar-factbook" else
                  "broad topic (keyword heuristic on title+lead, >=2 hits) x length tercile; list/date/year/"
                  "disambiguation titles excluded" if name == "boar-simplewiki-en" else
                  "document family (title prefix; glossary groups = 'NIST glossary') x length tercile" if name == "boar-nist-crypto" else
                  ("length tercile x views tercile; accepted answer and >=2 answers required" if name.startswith("qa-")
                   else "length tercile x views tercile"),
        "length_cuts": lc, "views_cuts": vc,
        "candidates": [{k: a[k] for k in ("id", "title", "source", "views", "len", "cell")} for a in cand],
        "chosen": prev.get("chosen", []),
        "rejects": prev.get("rejects", {}),
    }
    if "comparison_partners" in prev:  # wave-2: second article of comparison items -> item's primary article
        doc["comparison_partners"] = prev["comparison_partners"]
    if "replacements" in prev:  # wave 3: drafted items replaced after the fact (reason per article id)
        doc["replacements"] = prev["replacements"]
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(doc, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"{name}: eligible={len(pool)} cells={len(keys)} candidates={len(cand)} chosen={len(doc['chosen'])} rejects={len(doc['rejects'])}")


def show(name, aid, mx=6000):
    pack = Pack(name)
    t = pack.text(aid)
    ch = pack.chunks(aid)
    # insert chunk markers at UTF-16 offsets
    out, pos16, k = [], 0, 0
    starts = [s for s, _ in ch]
    for c in t:
        if k < len(starts) and pos16 >= starts[k]:
            out.append(f"\n<<C{k}>>")
            k += 1
        out.append(c)
        pos16 += u16(c)
    s = "".join(out)
    print(f"[{aid}] {pack.title(aid)} | {pack.source(aid)} | chars={len(t)} chunks={len(ch)}")
    print(s[:mx])


def fill(name, draft):
    pack = Pack(name)
    rows = [json.loads(l) for l in open(draft) if l.strip()]
    out = []
    for n, r in enumerate(rows, 1):
        aid = r["source"]["article_id"] if isinstance(r.get("source"), dict) else r["article_id"]
        url, lic, attr = pack.meta(aid)
        t, ch = pack.text(aid), pack.chunks(aid)
        facts = []
        for f in r["in_pack_facts"]:
            if "article" in f:  # wave-2 format: each fact names its article (comparison items cite two)
                fa = f["article"]
                facts.append({"fact": f["fact"], "quote": f["quote"],
                              "chunk_index": chunk_index(pack.text(fa), pack.chunks(fa), f["quote"]), "article": fa})
            else:
                facts.append({"fact": f["fact"], "quote": f["quote"], "chunk_index": chunk_index(t, ch, f["quote"])})
        out.append({
            "id": f"st-{name}-{n:03d}",
            "pack": name,
            "category": r["category"],
            "style": r.get("style"),
            "question": r["question"],
            "answer": r["answer"],
            "rubric": r["rubric"],
            "in_pack_facts": facts,
            "source": {"article_id": aid, "title": pack.title(aid), "url": url, "license": lic,
                       "attribution": attr, "pack_source": pack.source(aid)},
        })
    with open(os.path.join(OUT_DIR, f"{name}.jsonl"), "w") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    miss = sum(1 for o in out for f in o["in_pack_facts"] if f["chunk_index"] is None)
    print(f"{name}: rows={len(out)} quotes_not_found={miss}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "draw":
        for p in (sys.argv[2:] or PACKS):
            draw(p)
    elif cmd == "show":
        show(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 6000)
    elif cmd == "fill":
        fill(sys.argv[2], sys.argv[3])
