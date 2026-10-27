#!/usr/bin/env python3
"""CONVERT-FIX-SHIP 0-LLM parity: replay A (published pack) vs B (candidate) + pack text diff + self-test quote checks.
usage: python3.14 -I ship_compare.py <packA> <packB> <replayA.jsonl> <replayB.jsonl> <source-label> <selftest.jsonl|-> <out.json> [titles-of-interest,...]
source-label = substring of raw[].source that marks the pack (e.g. simple.wikipedia.org, Wikivoyage)."""
import sys, json, sqlite3, hashlib
from compression import zstd

def texts(pack):
    db = sqlite3.connect(f"file:{pack}?mode=ro", uri=True); out = {}; bid0 = None; blk = None
    for title, bid, off, ln in db.execute("select title,block_id,off,len from articles order by block_id,id"):
        if bid != bid0: blk = zstd.decompress(db.execute("select zdata from blocks where id=?", (bid,)).fetchone()[0]); bid0 = bid
        out[title] = blk[off:off + ln].decode("utf-8")
    return out

pA, pB, rA, rB, label, st, outp = sys.argv[1:8]; extra = sys.argv[8].split(",") if len(sys.argv) > 8 else []
TA, TB = texts(pA), texts(pB)
changed = {t for t in TA if t in TB and TA[t] != TB[t]} | (set(TA) ^ set(TB))
load = lambda p: {d["id"]: d for d in map(json.loads, open(p))}
A, B = load(rA), load(rB)
norm = lambda t: t.split(": ", 1)[1] if t.startswith("Wikivoyage: ") else t
def packtitles(d): return [norm(x["title"]) for x in d["raw"] if label in (x.get("source") or "")]
rows = []
for i in A:
    a, b = A[i], B[i]
    ra, rb = [x["title"] for x in a["raw"]], [x["title"] for x in b["raw"]]
    sa, sb = a.get("sources") or [], b.get("sources") or []
    if ra == rb and sa == sb: continue
    diff_titles = {norm(t) for t in (set(ra) ^ set(rb)) | (set(sa) ^ set(sb))}
    pack_diff = [t for t in diff_titles if t in TA or t in TB]
    explained = any(t in changed for t in pack_diff)
    rows.append({"id": i, "raw_changed": ra != rb, "kept_changed": sa != sb, "rawA": ra, "rawB": rb, "keptA": sa, "keptB": sb,
                 "pack_titles_in_diff": pack_diff, "changed_article_in_diff": [t for t in pack_diff if t in changed], "explained": explained,
                 "recallA": a.get("recall"), "recallB": b.get("recall")})
res = {"articles_A": len(TA), "articles_B": len(TB), "changed_articles": len(changed), "n_items": len(A),
       "raw_changed": sum(r["raw_changed"] for r in rows), "kept_changed": sum(r["kept_changed"] for r in rows),
       "unexplained": [r["id"] for r in rows if not r["explained"]], "rows": rows}
# self-test checks: quote present in source article (A, B); source article in raw / kept (A, B); any pack passage kept
if st != "-":
    sts = []
    for l in open(st):
        d = json.loads(l); t = d["source"]["title"]; qs = [f["quote"] for f in d.get("in_pack_facts", [])]
        a, b = A.get(d["id"]), B.get(d["id"])
        sts.append({"id": d["id"], "title": t, "article_changed": t in changed,
                    "quotes_in_A": sum(q in TA.get(t, "") for q in qs), "quotes_in_B": sum(q in TB.get(t, "") for q in qs), "quotes": len(qs),
                    "src_kept_A": bool(a) and t in a.get("sources", []), "src_kept_B": bool(b) and t in b.get("sources", []),
                    "pack_raw_A": len(packtitles(a)) if a else None, "pack_raw_B": len(packtitles(b)) if b else None})
    res["selftest"] = sts
    res["selftest_sum"] = {k: sum(1 for s in sts if s[k]) for k in ("src_kept_A", "src_kept_B", "article_changed")} | {
        "quotes_ok_A": sum(s["quotes_in_A"] == s["quotes"] for s in sts), "quotes_ok_B": sum(s["quotes_in_B"] == s["quotes"] for s in sts),
        "pack_passage_raw_A": sum(1 for s in sts if s["pack_raw_A"]), "pack_passage_raw_B": sum(1 for s in sts if s["pack_raw_B"])}
for t in extra:
    res.setdefault("probe_titles", {})[t] = {"changed": t in changed, "A_snip": TA.get(t, "")[:0], "lenA": len(TA.get(t, "")), "lenB": len(TB.get(t, ""))}
json.dump(res, open(outp, "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "selftest", "probe_titles")}, ensure_ascii=False))
for r in rows: print(r["id"], "raw" if r["raw_changed"] else "", "kept" if r["kept_changed"] else "", "explained" if r["explained"] else "UNEXPLAINED", r["changed_article_in_diff"][:4], f"recall {r['recallA']}->{r['recallB']}")
