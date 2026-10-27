#!/usr/bin/env python3
"""ORACLE-ST stage 0: oracle files for the 180 public self-test items (9 packs x 20). Run: python3 -I build_oracle.py
in : rnd/research/packs/selftest/<pack>.jsonl (in_pack_facts[].chunk_index, source.article_id), shared-data/packs/{wave2,wave1}/<pack>.sqlite
out: tools/oracle-add.json, tools/oracle-only.json  ({queryId: {pack, article_id, chunk_index, mode, question}}; the oracle chunk = the
     FIRST in_pack_facts entry with a chunk_index (article = fact.article if given, else source.article_id), chunks ordered by start as d0_st2.py)
     tools/oracle-facts.json  (per item: oracle chunkId, all fact chunkIds (d0_st2 definition), lead chunkId, chunk text sha256 (UTF-16 slice, trimmed))
Fails loudly (exit 2) if > 5 % of items lack article_id/chunk_index or the index is out of range."""
import hashlib, json, os, sqlite3, subprocess, sys
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/oracle-st"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
def pub(p): return next(f"{ROOT}/shared-data/packs/{w}/{p}.sqlite" for w in ("wave2", "wave1") if os.path.exists(f"{ROOT}/shared-data/packs/{w}/{p}.sqlite"))
_blocks = {}
def article_text(db, path, aid):
    bid, off, ln = db.execute("SELECT block_id, off, len FROM articles WHERE id=?", (aid,)).fetchone()
    if (path, bid) not in _blocks:
        z = db.execute("SELECT zdata FROM blocks WHERE id=?", (bid,)).fetchone()[0]
        _blocks[(path, bid)] = subprocess.run(["zstd", "-dc"], input=bytes(z), capture_output=True, check=True).stdout
    return _blocks[(path, bid)][off:off + ln].decode("utf-8")
def js_slice(s, a, b):  # JS String.prototype.slice on UTF-16 code units
    u = s.encode("utf-16-le"); return u[2 * a:2 * b].decode("utf-16-le", errors="surrogatepass")
def js_trim(s): return s.strip(" \t\n\r\v\f                 　﻿")
add, only, facts, missing = {}, {}, {}, []
for p in PACKS:
    path = pub(p); db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    items = [json.loads(l) for l in open(f"{ST}/{p}.jsonl") if l.strip()]; assert len(items) == 20, p
    for it in items:
        i = it["id"]; fa = it.get("source", {}).get("article_id")
        fl = [f for f in it.get("in_pack_facts", []) if f.get("chunk_index") is not None]
        if fa is None or not fl: missing.append(i); continue
        f0 = fl[0]; art = f0.get("article", fa)
        bystart = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (art,))]
        if f0["chunk_index"] >= len(bystart): missing.append(i); continue
        allc = sorted({[r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))][f["chunk_index"]]
                       for f in fl if f["chunk_index"] < db.execute("SELECT count(*) FROM chunks WHERE article_id=?", (f.get("article", fa),)).fetchone()[0]})
        byid = db.execute("SELECT id, start, end FROM chunks WHERE article_id=? ORDER BY id", (art,)).fetchall()
        txt = article_text(db, path, art)
        lead = byid[1] if txt.startswith("Key facts:", byid[0][1]) and len(byid) > 1 else byid[0]  # (startsWith on code points; ASCII prefix)
        cid = bystart[f0["chunk_index"]]; s, e = db.execute("SELECT start, end FROM chunks WHERE id=?", (cid,)).fetchone()
        ctext = js_trim(js_slice(txt, s, e))
        e0 = {"pack": p, "article_id": art, "chunk_index": f0["chunk_index"], "question": it["question"]}
        add[i] = {**e0, "mode": "add"}; only[i] = {**e0, "mode": "only"}
        facts[i] = {"pack": p, "family": "SE" if p.startswith("qa-") else "topic", "oracle_chunk": f"pack:{p}:{cid}", "fact_chunks": [f"pack:{p}:{c}" for c in allc],
                    "lead_chunk": f"pack:{p}:{lead[0]}", "fact_is_lead": lead[0] == cid, "n_facts": len(fl), "n_distinct_fact_chunks": len(allc),
                    "chunk_text_sha256": hashlib.sha256(ctext.encode()).hexdigest(), "chunk_chars": len(ctext)}
n = len(add) + len(missing)
print(f"oracle coverage {len(add)}/{n}; missing {len(missing)} {missing}")
if len(missing) > 0.05 * n: print("FAIL: > 5 % missing"); sys.exit(2)
for name, obj in (("oracle-add.json", add), ("oracle-only.json", only), ("oracle-facts.json", facts)):
    json.dump(obj, open(f"{ARM}/tools/{name}", "w"), indent=1, ensure_ascii=False)
    print(name, hashlib.sha256(open(f"{ARM}/tools/{name}", "rb").read()).hexdigest()[:16])
print("items with >1 distinct fact chunk:", sum(v["n_distinct_fact_chunks"] > 1 for v in facts.values()), "| oracle chunk = lead:", sum(v["fact_is_lead"] for v in facts.values()))
