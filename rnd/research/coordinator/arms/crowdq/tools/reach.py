#!/usr/bin/env python3
"""CROWDQ step 2 reach check + crowding attribution + precheck (0 LLM). Usage: python3 -I reach.py [--json out]
Fact article kept = item source.url found in a kept source string (URL match only: a bare-title match gives false positives,
e.g. factbook "Austria" vs kit "Wikivoyage: Austria"; same matching as on S's cut-7 traces = 59/180; band ruling QUEUE 15:0x: P must be 40 ± 4 = 36..44).
Kept-source attribution: URL in the source string looked up in the 9 packs' article_meta.url; else by label (Wikivoyage -> kit
boar-wikivoyage-en, anything else unmatched -> kit/other (boar-crypto or seed corpus)).
Precheck: item changed vs S if kept (title, section) list differs or timing.promptTokens differs."""
import json, re, sqlite3, os, sys, collections
B = "<workspace>"; H = f"{B}/rnd/research/coordinator/arms"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
pub = lambda p: f"{B}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
URL = {}
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True)
    for (u,) in db.execute("SELECT url FROM article_meta"):
        if u: URL.setdefault(u, p)
U = re.compile(r"https?://[^\s)]+")
LIB = re.compile(r"^[^:]{2,40}:\s+")
def owner(s):
    for u in U.findall(s.get("source") or ""):
        if u in URL: return URL[u]
    if (s.get("source") or "").startswith("Wikivoyage"): return "kit:wikivoyage"
    return "kit:other"
def url_in(u, src):  # audit F9: exact URL or path-segment prefix match (substring matched .../wiki/Google inside .../wiki/Google_AdSense)
    if not u: return False
    for v in U.findall(src or ""):
        v = v.rstrip(".,;:'\"]>")
        if v == u or (v.startswith(u) and v[len(u)] in "/#?"): return True
    return False
load = lambda f: {t["itemId"]: t for t in map(json.loads, open(f))}
def fact(t, it):
    u, ft = it["source"].get("url"), it["source"]["title"].casefold()
    return any(url_in(u, s.get("source")) for s in t["retrieval"]["kept"])
out = {"per_pack": {}, "items": []}; tot = collections.Counter(); own_all = collections.Counter()
for p in PACKS:
    items = {j["id"]: j for j in map(json.loads, open(f"{B}/rnd/research/packs/selftest/{p}.jsonl"))}
    S = load(f"{H}/packs/selftest-runs/st-{p}-cut7-s42.traces.jsonl"); P = load(f"{H}/crowdq/runs/st-{p}-cut7-all9-s42.traces.jsonl")
    c = collections.Counter(); own = collections.Counter()
    for i, it in items.items():
        s, q = S[i], P[i]; ks = [(x["title"], x["section"]) for x in s["retrieval"]["kept"]]; kp = [(x["title"], x["section"]) for x in q["retrieval"]["kept"]]
        ch = ks != kp or s["timing"].get("promptTokens") != q["timing"].get("promptTokens")
        ow = [owner(x) for x in q["retrieval"]["kept"]]; own.update(ow); own_all.update(ow)
        row = {"id": i, "pack": p, "fact_S": fact(s, it), "fact_P": fact(q, it), "raw_S": len(s["retrieval"]["raw"]), "raw_P": len(q["retrieval"]["raw"]),
               "kept_S": len(ks), "kept_P": len(kp), "own_kept_S": sum(owner(x) == p for x in s["retrieval"]["kept"]), "own_kept_P": sum(o == p for o in ow),
               "changed": ch, "kept_changed": ks != kp, "pt_S": s["timing"].get("promptTokens"), "pt_P": q["timing"].get("promptTokens"), "kept_P_owners": ow,
               "err_P": q.get("error"), "kit_P": len(q["config"]["kit"])}
        out["items"].append(row)
        for k in ("fact_S", "fact_P", "raw_S", "raw_P", "kept_S", "kept_P", "own_kept_S", "own_kept_P", "changed", "kept_changed"): c[k] += row[k]
    c["kept_from_P_by_owner"] = dict(own.most_common()); out["per_pack"][p] = dict(c); tot.update({k: v for k, v in c.items() if k != "kept_from_P_by_owner"})
it = out["items"]; n = len(it)
out["total"] = dict(tot) | {"n": n, "changed_share": round(tot["changed"] / n, 3), "kit_list_lens": sorted({r["kit_P"] for r in it}), "errors_P": sum(bool(r["err_P"]) for r in it),
    "kept_P_by_owner": dict(own_all.most_common()), "kept_P_share_by_owner": {k: round(v / sum(own_all.values()), 3) for k, v in own_all.most_common()},
    "band": [36, 44], "in_band": 36 <= tot["fact_P"] <= 44, "precheck_pass": tot["changed"] / n >= 0.20}
for f in ("SE", "topic"):
    r = [x for x in it if (x["pack"].startswith("qa-")) == (f == "SE")]
    out[f] = {"n": len(r), "fact_S": sum(x["fact_S"] for x in r), "fact_P": sum(x["fact_P"] for x in r), "own_kept_S": sum(x["own_kept_S"] for x in r), "own_kept_P": sum(x["own_kept_P"] for x in r)}
for p, c in out["per_pack"].items(): print(p, {k: v for k, v in c.items() if k != "kept_from_P_by_owner"}, list(c["kept_from_P_by_owner"].items())[:4])
print("TOTAL", json.dumps(out["total"])); print("SE", out["SE"], "topic", out["topic"])
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
