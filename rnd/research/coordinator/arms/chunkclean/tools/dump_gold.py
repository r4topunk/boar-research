#!/usr/bin/env python3
"""CHUNKCLEAN (0 LLM): dump the 30 ORACLE-REAL gold chunks (title + text exactly as packHitToChunk gets them) to JSON. Usage: dump_gold.py <out json>"""
import json, sys, sqlite3
from compression import zstd
SD = "<workspace>/shared-data/"; OR = "<workspace>/rnd/research/coordinator/arms/oracle-real/"
PF = {"boar-crypto": SD + "crypto/boar-crypto.sqlite", "boar-wikivoyage-en": SD + "packs/boar-wikivoyage-en.sqlite",
      "boar-simplewiki-en": SD + "packs/v3proto/boar-simplewiki-en.sqlite", "boar-factbook": SD + "packs/v3proto/boar-factbook.sqlite",
      "boar-medlineplus-en": SD + "packs/v3proto/boar-medlineplus-en.sqlite", "boar-firstaid-en": SD + "packs/v3proto/boar-firstaid-en.sqlite"}
DB = {k: sqlite3.connect(f"file:{v}?mode=ro", uri=True) for k, v in PF.items()}
def chunk(pk, cid):
    a, s, e = DB[pk].execute("select article_id, start, end from chunks where id=?", (cid,)).fetchone()
    b, off, ln, t = DB[pk].execute("select block_id, off, len, title from articles where id=?", (a,)).fetchone()
    txt = zstd.decompress(DB[pk].execute("select zdata from blocks where id=?", (b,)).fetchone()[0])[off:off + ln].decode("utf-8", "replace")
    return t, txt[s:e].strip()
o = {}
for i, e in json.load(open(OR + "tools/oracle-file.json")).items():
    t, x = chunk(e["pack"], e["chunk_id"]); o[i] = dict(question=e["question"], pack=e["pack"], chunk_id=e["chunk_id"], title=t, text=x)
json.dump(o, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
print(len(o), "chunks; chars", sorted(len(v["text"]) for v in o.values()))
