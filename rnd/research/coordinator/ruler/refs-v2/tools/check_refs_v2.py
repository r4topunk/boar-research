#!/usr/bin/env python3
"""Validate a references-v2 archive (0 LLM). Prints counts only, never question or answer text.
usage: python3 -I tools/check_refs_v2.py <claude|codex> [--manifest]   (--manifest writes/updates refs/v2/MANIFEST.json for that family)
Checks: 75/75 ok rows, one row per id, turn count = item turns, >= 1 source URL per row (flagged, not fatal), model ids, prompt/items/generator
shas constant, no mention of BOAR in answers, words summary; exit 0 only if every hard check passes."""
import hashlib, json, re, statistics, sys, collections
from pathlib import Path
BOAR = Path("<workspace>"); ITEMS = BOAR / "boar-eval/bench/v0.4/items.jsonl"; OUT = BOAR / "boar-eval/bench/v0.4/refs/v2"
ITEMS_SHA = "f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594"
fam = sys.argv[1]; f = OUT / f"{fam}.jsonl"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ITEMS) == ITEMS_SHA, "items sha"
items = {json.loads(l)["id"]: json.loads(l) for l in ITEMS.read_text().splitlines() if l.strip()}
rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
ok = [r for r in rows if r.get("ok")]; ids = collections.Counter(r["id"] for r in ok)
hard = []
if set(ids) != set(items): hard.append(f"ids: {len(set(ids))}/{len(items)} present; missing {sorted(set(items) - set(ids))}")
if any(c > 1 for c in ids.values()): hard.append(f"duplicate ids {[k for k, c in ids.items() if c > 1]}")
for r in ok:
    if len(r["turns"]) != len(items[r["id"]]["turns"]): hard.append(f"{r['id']} turn count")
    if re.search(r"\bboar\b", r["answer"], re.I): hard.append(f"{r['id']} mentions BOAR")  # word match: "board", "aboard" are not hits (fix 2026-10-21)
for k in ("promptSha256", "itemsSha256", "generatorSha256"):
    v = {r[k] for r in ok}
    if len(v) != 1: hard.append(f"{k} not constant: {v}")
nosrc = [r["id"] for r in ok if not r["sources"]]
words = [r["words"] for r in ok]
models = collections.Counter(m for r in ok for m in r["models"])
asof = collections.Counter(t["asOfDate"] for r in ok for t in r["turns"])
rep = {"family": fam, "file": str(f), "sha256": sha(f), "rows_ok": len(ok), "rows_total": len(rows), "items": len(items),
       "multi_turn_rows": sum(r["multiTurn"] for r in ok), "location_rows": sum(r["hasLocation"] for r in ok),
       "rows_without_sources": nosrc, "sources_median": statistics.median(len(r["sources"]) for r in ok) if ok else None,
       "words_median": statistics.median(words) if words else None, "words_p10_p90": [sorted(words)[len(words) // 10], sorted(words)[9 * len(words) // 10]] if words else None,
       "models": dict(models), "asOfDates": dict(asof), "promptSha256": next(iter({r["promptSha256"] for r in ok}), None),
       "generatorSha256": next(iter({r["generatorSha256"] for r in ok}), None), "hard_failures": hard}
print(json.dumps(rep, indent=1))
if "--manifest" in sys.argv and not hard:
    mp = OUT / "MANIFEST.json"; man = json.loads(mp.read_text()) if mp.exists() else {"bench": "v0.4", "items_sha256": ITEMS_SHA, "families": {}}
    man["families"][fam] = {k: rep[k] for k in ("sha256", "rows_ok", "models", "asOfDates", "promptSha256", "generatorSha256", "rows_without_sources", "words_median")}
    mp.write_text(json.dumps(man, indent=1) + "\n"); print(f"MANIFEST updated: {mp}")
sys.exit(1 if hard else 0)
