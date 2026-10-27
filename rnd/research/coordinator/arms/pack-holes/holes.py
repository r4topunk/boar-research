#!/usr/bin/env python3 -I
"""Read-only hole scan of BOAR knowledge packs.
usage: holes.py <pack.sqlite> <out.json> [--articles-mod N] [--examples 10]
A "hole" = text left where a wikitext template was stripped (numbers, names, dates, units missing).
Chunk text = article text[start:end] (offsets are UTF-16 code units, as in the JS builder).
"""
import sys, re, json, sqlite3, random
from collections import Counter, defaultdict
from compression import zstd  # python >= 3.14

PREP = r"(?:of|near|in|at|to|from|and|the|with|by|between|or|as|is|was|were|are|for|about|over|than|around|approximately|up to|under|until|since|on|a|an)"
UNIT = (r"(?:km|kms|kilomet(?:er|re)s?|miles?|met(?:er|re)s?|cm|mm|kg|kilograms?|lbs?|pounds?|tonnes?|"
        r"°C|°F|%|percent|km2|km²|m²|sq mi|square (?:kilomet(?:er|re)s?|miles?)|hectares?|acres?|million|billion|trillion|"
        r"mph|km/h|kph|litres?|liters?)")
# H-name -> regex. Patterns are anchored on what a stripped template leaves behind.
PATTERNS = {
    "empty_paren":      re.compile(r"\(\s*[,;:–—-]?\s*\)"),
    "paren_lead_punct": re.compile(r"\(\s*[,;:]"),                      # "( , born ...)"
    "paren_dash_only":  re.compile(r"\(\s*(?:born|died|b\.|d\.|c\.|ca\.)?\s*[–—-]\s*(?:\)|[,;])"),  # "( – )", "(born –)"
    "prep_punct":       re.compile(r"\b" + PREP + r"\s+[.,;:)](?![.\d])", re.I),          # "speeds of up to ."
    "unit_no_number":   re.compile(r"(?<![\d.,/])(?<!thousands )(?<!hundreds )(?<!tens )(?<!dozens )(?<!millions )(?<!billions )(?<!few )(?<!several )(?<!many )(?<!couple )(?<!per )\b(?:is|are|was|were|of|about|to|from|and|by|than|over|around|approximately|up to|under|at|nearly|almost|roughly|reaches?|reached)\s+" + UNIT + r"\b(?![\w-])"),
    "born_died_empty":  re.compile(r"\((?:born|died|b\.|d\.)\s*[,;)]|\b(?:born|died)\s+(?:in|on|at)\s*[,.;)]"),
    "orphan_modifier":  re.compile(r"(?<![\w\d)])-(?:long|wide|high|tall|deep|old|year|day|hour|minute|mile|km|kilometre|metre|meter|foot|storey|story|acre|hectare)\b"),
    "lang_label_empty": re.compile(r"\((?:[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)?:\s*(?:[,;)]|$))"),   # "(Japanese: )"
    "between_and":      re.compile(r"\bbetween\s+and\b|\bfrom\s+to\b(?!\s+and)"),
    "double_space":     re.compile(r"\S {2,}\S"),
    "space_punct":      re.compile(r"[A-Za-z0-9] [,;](?!\d)"),         # weak: "word ,"
    "line_lead_punct":  re.compile(r"(?m)^[,.;:)]\s"),
}
STRONG = [k for k in PATTERNS if k not in ("space_punct", "double_space")]
# fact-bearing = a number/amount/date/name is missing from the sentence; cosmetic = pronunciation/native-name parentheses
FACT = ["prep_punct", "unit_no_number", "between_and", "paren_dash_only", "born_died_empty", "orphan_modifier"]

def u16(b: bytes):
    return b.decode("utf-8")

def scan(pack, out, mod, nex):
    db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    tot_art = db.execute("select count(*) from articles").fetchone()[0]
    tot_chunks = db.execute("select count(*) from chunks").fetchone()[0]
    stats = Counter(); fact_hit = 0; per = Counter(); examples = defaultdict(list); strong_hit = 0
    hole_chunk_ids = []
    cache_id, cache = None, None
    q = ("select a.id aid, a.title, a.block_id, a.off, a.len, c.id cid, c.start, c.end from articles a "
         "join chunks c on c.article_id=a.id " + (f"where a.id % {mod} = 0 " if mod > 1 else "") + "order by a.block_id, a.id, c.id")
    art_text = {}
    last_aid = None; text16 = None
    rng = random.Random(7)
    for r in db.execute(q):
        if r["block_id"] != cache_id:
            cache = zstd.decompress(db.execute("select zdata from blocks where id=?", (r["block_id"],)).fetchone()[0]); cache_id = r["block_id"]
        if r["aid"] != last_aid:
            text16 = cache[r["off"]:r["off"] + r["len"]].decode("utf-8").encode("utf-16-le"); last_aid = r["aid"]
        chunk = text16[r["start"] * 2:r["end"] * 2].decode("utf-16-le", "replace")
        stats["chunks"] += 1
        hit = False; fh = False
        for name, rx in PATTERNS.items():
            m = rx.search(chunk)
            if m:
                per[name] += 1
                if name in STRONG: hit = True
                if name in FACT: fh = True
                ex = examples[name]
                s = chunk[max(0, m.start() - 70): m.end() + 40].replace("\n", " ")
                # reservoir of nex examples
                n = per[name]
                item = {"title": r["title"], "chunk_id": r["cid"], "ctx": s}
                if len(ex) < nex: ex.append(item)
                else:
                    j = rng.randrange(n)
                    if j < nex: ex[j] = item
        if fh: fact_hit += 1
        if hit:
            strong_hit += 1; hole_chunk_ids.append(r["cid"])
    res = {"pack": pack.split("/")[-1], "articles_total": tot_art, "chunks_total": tot_chunks, "article_mod": mod,
           "chunks_scanned": stats["chunks"], "chunks_with_strong_hole": strong_hit,
           "share_strong": strong_hit / max(1, stats["chunks"]), "chunks_with_fact_hole": fact_hit, "share_fact": fact_hit / max(1, stats["chunks"]), "per_pattern": dict(per),
           "per_pattern_share": {k: v / max(1, stats["chunks"]) for k, v in per.items()},
           "examples": examples, "strong_patterns": STRONG, "hole_chunk_ids": hole_chunk_ids[:200000]}
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(res["pack"], "scanned", stats["chunks"], "strong", strong_hit, f"{res['share_strong']:.4%}", dict(per))

if __name__ == "__main__":
    a = sys.argv[1:]
    mod = int(a[a.index("--articles-mod") + 1]) if "--articles-mod" in a else 1
    nex = int(a[a.index("--examples") + 1]) if "--examples" in a else 10
    scan(a[0], a[1], mod, nex)
