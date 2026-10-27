#!/usr/bin/env python3
"""COVERAGE-MAP: cooking/money self-test oracle (0 LLM). For each of the 40 cm items, is each in_pack_fact quote present in the item's own
source article (selftest.source.article_id) of the installed-on-disk pack file? Normalised substring, else >= 80 % of quote content tokens in one chunk.
Usage: python3 -I cm_oracle.py <out json>"""
import json, sys, re, sqlite3, unicodedata
from compression import zstd
SD = "<workspace>/shared-data/packs/wave3/"; BE = "<workspace>/boar-eval/bench/selftest/"
nrm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "").lower().replace("’", "'")).strip()
tk = lambda s: set(w for w in re.findall(r"[a-z0-9]+", nrm(s)) if len(w) >= 3)
out = {}
for pk in ("qa-cooking-se", "qa-money-se"):
    db = sqlite3.connect(f"file:{SD}{pk}.sqlite?mode=ro", uri=True)
    for l in open(f"{BE}{pk}/questions.jsonl"):
        q = json.loads(l); st = q["selftest"]; aid = st["source"]["article_id"]
        b, off, ln, t = db.execute("select block_id, off, len, title from articles where id=?", (aid,)).fetchone()
        txt = zstd.decompress(db.execute("select zdata from blocks where id=?", (b,)).fetchone()[0])[off:off + ln].decode("utf-8", "replace")
        chunks = [txt[s:e] for s, e in db.execute("select start, end from chunks where article_id=? order by id", (aid,))]
        hits = []
        for f in st["in_pack_facts"]:
            qq = nrm(f.get("quote", "")); T = tk(qq)
            hits.append(bool(qq and qq in nrm(txt)) or bool(T and any(len(T & tk(c)) / len(T) >= 0.8 for c in chunks)))
        out[q["id"]] = dict(pack=pk, article_id=aid, title=t, url=st["source"].get("url"), facts=[f["fact"] for f in st["in_pack_facts"]], quote_found=hits,
                            all_found=all(hits), any_found=any(hits))
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(sum(v["all_found"] for v in out.values()), sum(v["any_found"] for v in out.values()), len(out))
