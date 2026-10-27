#!/usr/bin/env python3
"""T-K4c generation checks for a self-test run (0 LLM calls).
Usage: python3 -I selftest_agg.py <pack> <traces.jsonl> [--json out.json]
Per item: answer non-empty, retrieval fired (raw > 0), kept count, kept from the pack (kept title is an article title of
shared-data/packs/wave1/<pack>.sqlite, or source/url mentions stackexchange), fact article (item source.title) in raw / kept / shown.
Note: the cut 7 tree predates T-K2 source codes, so SE rows are labelled "enwiki" (SOURCES[9] -> fallback); pack membership is by title."""
import json, os, re, sqlite3, statistics, sys
B = "<workspace>"; pack, tp = sys.argv[1], sys.argv[2]
items = {j["id"]: j for j in (json.loads(l) for l in open(f"{B}/rnd/research/coordinator/arms/pack-nist/selftest/{pack}.jsonl") if l.strip())}
pd = next(d for d in (f"{B}/shared-data/packs/wave4", f"{B}/shared-data/packs/wave3", f"{B}/shared-data/packs/wave2", f"{B}/shared-data/packs/wave1") if os.path.exists(f"{d}/{pack}.sqlite"))  # wave3, then wave2, then wave1
db = sqlite3.connect(f"file:{pd}/{pack}.sqlite?mode=ro", uri=True)
titles = {r[0].casefold() for r in db.execute("select title from articles")}
T = {}
for l in open(tp):
    t = json.loads(l); T[t["itemId"]] = t
rows = []
for iid, it in items.items():
    t = T.get(iid); ft = it["source"]["title"].casefold()
    # PACK-NIST: the engine labels usgov rows "US government: <title>"; strip that label before matching (titles may contain ':')
    tl = lambda s: re.sub(r"^us government: ", "", (s.get("title") or "").casefold())
    if not t: rows.append({"id": iid, "missing": True}); continue
    r = t.get("retrieval") or {}; raw, kept = r.get("raw") or [], r.get("kept") or []
    inpack = lambda s: tl(s) in titles or "stackexchange" in (s.get("source") or "").lower()
    shown = [re.sub(r"^us government: ", "", x.casefold() if isinstance(x, str) else (x.get("title") or "").casefold()) for x in (t["answer"].get("shown") or [])]
    rows.append({"id": iid, "error": t.get("error"), "nonempty": bool((t["answer"].get("text") or "").strip()), "words": len((t["answer"].get("text") or "").split()),
                 "tier": t["route"].get("tier"), "task": t["route"].get("task"), "raw": len(raw), "kept": len(kept), "kept_pack": sum(map(inpack, kept)),
                 "raw_pack": sum(map(inpack, raw)), "fact_raw": any(tl(s) == ft for s in raw),
                 "fact_kept": any(tl(s) == ft for s in kept), "fact_shown": ft in shown,
                 "declined": t["answer"].get("declined"), "totalMs": t["timing"].get("totalMs"), "src_labels": sorted({(s.get("source") or "")[:40] for s in kept if inpack(s)})})
ok = [x for x in rows if not x.get("missing")]; n = len(items); s = lambda k: sum(1 for x in ok if x.get(k))
tm = [x["totalMs"] for x in ok if x["totalMs"]]
summ = {"n": n, "traces": len(ok), "errors": sum(1 for x in ok if x["error"]), "nonempty": s("nonempty"), "retrieval_fired": sum(1 for x in ok if x["raw"] > 0),
        "kept_total": sum(x["kept"] for x in ok), "kept_from_pack": sum(x["kept_pack"] for x in ok), "items_with_pack_kept": sum(1 for x in ok if x["kept_pack"]),
        "fact_article_in_raw": s("fact_raw"), "fact_article_in_kept": s("fact_kept"), "fact_article_shown": s("fact_shown"), "declined": s("declined"),
        "tiers": dict(statistics.Counter(x["tier"] for x in ok)) if hasattr(statistics, "Counter") else None,
        "p50_s": round(statistics.median(tm) / 1000, 1) if tm else None, "p90_s": round(sorted(tm)[int(0.9 * (len(tm) - 1))] / 1000, 1) if tm else None,
        "median_words": statistics.median(x["words"] for x in ok) if ok else None}
from collections import Counter; summ["tiers"] = dict(Counter(x["tier"] for x in ok)); summ["tasks"] = dict(Counter(x["task"] for x in ok))
summ["pack_kept_labels"] = dict(Counter(l for x in ok for l in x["src_labels"]))
for x in rows: print(json.dumps({k: v for k, v in x.items() if k != "src_labels"}))
print(json.dumps(summ))
if "--json" in sys.argv: json.dump({"summary": summ, "items": rows}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
