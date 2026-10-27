#!/usr/bin/env python3
"""IN-PACK stratum map for bench v0.4 (0 LLM). Reads ONLY id, family, type, tags (minus anchor_vexact_question)
and whether context carries lat/lon. Never reads or prints question text, turns, checklist, references, notes.
Usage: inpack_map.py <items.jsonl> <out.json>"""
import json, sys, hashlib, collections

ITEMS, OUT = sys.argv[1], sys.argv[2]
EXPECT = "f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594"
assert hashlib.sha256(open(ITEMS, "rb").read()).hexdigest() == EXPECT, "items sha mismatch"

# Rule R1 (topical domain match; frozen candidate). pack -> predicate on tag record t.
TRIG = {
  # travel guides / visa rules / Q&A on visas, borders, practical travel
  "boar-wikivoyage-en": lambda t: t["family"] == "travel" or t["has_location"],
  "boar-visa-en":       lambda t: t["family"] == "travel",
  "qa-travel-se":       lambda t: t["family"] == "travel",
  "area-tile+world-places": lambda t: t["has_location"],
  # Ethereum / crypto / mechanism design
  "boar-crypto":        lambda t: t["family"] == "tech",
  "qa-ethereum-se":     lambda t: t["family"] == "tech",
  "qa-bitcoin-se":      lambda t: t["family"] == "tech",
  "boar-vitalik-blog-en": lambda t: t["family"] == "tech",
  # everyday health / first aid
  "boar-medlineplus-en": lambda t: t["health_safety"],
  "boar-firstaid-en":   lambda t: t["health_safety"],
  "qa-health-se":       lambda t: t["health_safety"],
  # country facts
  "boar-factbook":      lambda t: t["family"] == "place",
  # no tag identifies their subject -> never trigger under R1 (stated, not hidden)
  "qa-outdoors-se":     lambda t: False,
  "qa-cooking-se":      lambda t: False,
  "qa-money-se":        lambda t: False,
}
GENERAL = {"native-kit(300+corpus-standard+corpus-full)", "boar-simplewiki-en"}  # never make an item in-pack

SETS = {
  "a": [],  # native Essential kit: general only
  "b": ["boar-wikivoyage-en", "boar-visa-en", "boar-crypto", "boar-medlineplus-en", "boar-firstaid-en",
        "boar-factbook", "area-tile+world-places"],  # A-union, PERSONA-MAP-v1 draft r1
  "c": ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
        "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "qa-cooking-se", "qa-money-se",
        "boar-vitalik-blog-en", "boar-visa-en"],  # 11 HF-published + wave-4 (vitalik, visa); nist-crypto excluded
}
PERSONA = {"travel": ["boar-wikivoyage-en", "boar-visa-en", "area-tile+world-places"], "tech": ["boar-crypto"],
           "science": ["boar-medlineplus-en", "boar-firstaid-en"], "place": ["boar-factbook"], "humanities": []}

rows = []
for line in open(ITEMS):
    r = json.loads(line)
    tg = {k: v for k, v in (r.get("tags") or {}).items() if k != "anchor_vexact_question"}
    ctx = r.get("context") or {}
    t = {"family": r["family"], "type": r["type"], "has_location": ("lat" in ctx and "lon" in ctx),
         "health_safety": bool(tg.get("health_safety")), **{k: tg.get(k) for k in
         ("situation", "region", "time_sensitive", "over_refusal", "one_b_fail", "anchor_vexact", "multiturn_shape")}}
    out = {"id": r["id"], "tags": t}
    for s, packs in SETS.items():
        m = [p for p in packs if TRIG[p](t)]
        out[f"inpack_{s}"] = bool(m); out[f"packs_{s}"] = m
    m = [p for p in PERSONA[t["family"]] if TRIG[p](t)]
    out["inpack_persona"] = bool(m); out["packs_persona"] = m
    rows.append(out)

json.dump({"rule": "R1 topical domain match (INPACK-STRATUM-2026-10-21.md section 2)", "items_sha256": EXPECT,
           "n": len(rows), "items": rows}, open(OUT, "w"), indent=1, sort_keys=False)
# counts
def tab(key):
    c = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for o in rows:
        k = o["tags"][key] if key != "ALL" else "ALL"
        c[k][0] += 1
        for i, s in enumerate(["a", "b", "c", "persona"]): c[k][i + 1] += o[f"inpack_{s}"]
    print(f"\n{key}: n / in_a / in_b / in_c / in_own_persona")
    for k, v in sorted(c.items(), key=lambda x: str(x[0])): print(f"  {k}: {v}")
for k in ("ALL", "family", "type", "situation", "health_safety", "has_location", "region", "time_sensitive", "over_refusal", "one_b_fail", "anchor_vexact"):
    tab(k)
