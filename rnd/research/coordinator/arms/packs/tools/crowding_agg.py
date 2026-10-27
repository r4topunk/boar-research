#!/usr/bin/env python3
"""T-K4a CROWDING aggregation (run with python3 -I). Reads the replay outputs of crowding.sh and writes
aggregates/crowding.json with ids, pack ids, categories, counts, shares and timings ONLY (no query/passage text; the
replay files' `query` field is never read into the output). Rule (D-K3d, frozen): a peer pack is default-eligible when its
share of kept slots <= 0.40 and the kit's gold hits (resolvable gold, raw top-6 and kept) are not lower than the baseline,
on both sets; else "user-selected only".
Gold: boar-eval gold sources.json, match rule = replay-pg.ts goldMatch (scorers/retrieval.py; same normalisation as
arms/packcond/tools/p4_diag.py / densechunk.py). Resolvable = the gold article title (before '#') exists as an article in
the kit packs (boar-crypto, boar-wikivoyage-en), labelled as packHitToChunk labels it. Pack of a slot = `pack` field
(chunkId prefix, replay-crowd.ts)."""
import json, os, re, sqlite3, statistics, collections, sys

ROOT = "<workspace>"
ARM = f"{ROOT}/rnd/research/coordinator/arms/packs"
SE = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se"]
PACKS = SE + ["boar-firstaid-en", "boar-medlineplus-en"]
RUNS = PACKS + ["se5"]
WAVE2 = "--wave2" in sys.argv  # T-K6b: the two wave-2 packs as peers -> aggregates/crowding-wave2.json
if WAVE2: PACKS = RUNS = ["boar-factbook", "boar-simplewiki-en"]
WAVE3 = "--wave3" in sys.argv  # wave 3 (2026-10-13): qa-cooking-se, qa-money-se as peers -> aggregates/crowding-wave3.json
if WAVE3: PACKS = RUNS = ["qa-cooking-se", "qa-money-se"]
KIT = {"boar-crypto": f"{ROOT}/shared-data/crypto/boar-crypto.sqlite", "boar-wikivoyage-en": f"{ROOT}/shared-data/packs/boar-wikivoyage-en.sqlite"}
SETS = {
    "v02": dict(dir=f"{ROOT}/blind/bench-v02/runs-packs", q=f"{ROOT}/blind/bench-v02/live/v0.2/questions.v02-new.jsonl",
                gold=f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json"),
    "v01": dict(dir=f"{ARM}/replay", q=f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl",
                gold=f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json"),
}
MATCH = {  # categories where a pack "belongs" (category table)
    "qa-travel-se": {"travel-practical", "travel-local", "local-food"},
    "qa-ethereum-se": {"crypto"}, "qa-bitcoin-se": {"crypto"},
    "qa-health-se": {"health", "danger", "danger-situation"},
    "qa-outdoors-se": {"danger", "danger-situation", "travel-practical"},
    "boar-firstaid-en": {"health", "danger", "danger-situation"},
    "boar-medlineplus-en": {"health", "danger", "danger-situation"},
    "boar-factbook": {"comparison", "reasoning", "travel-practical", "travel-local"},  # T-K6b: country facts
    "boar-simplewiki-en": {"explanation", "comparison", "reasoning", "synthesis"},  # T-K6b: general knowledge
    "qa-cooking-se": {"local-food", "health", "explanation"},  # wave 3: cooking / food safety
    "qa-money-se": {"reasoning", "comparison", "crypto", "travel-practical"},  # wave 3: personal finance
}
SRC = ["enwiki", "enwikivoyage", "enwikibooks", "appropedia", "usgov", "eips", "ethspecs", "ethereumorg", "bips",
       "stackexchange", "medlineplus", "factbook", "simplewiki"]
LABEL = {"enwiki": "Wikipedia", "enwikivoyage": "Wikivoyage", "enwikibooks": "Wikibooks", "appropedia": "Appropedia",
         "usgov": "US government", "eips": "Ethereum EIPs/ERCs", "ethspecs": "Ethereum specs", "ethereumorg": "ethereum.org",
         "bips": "Bitcoin BIPs", "stackexchange": "Stack Exchange", "medlineplus": "MedlinePlus"}

LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).lower()
bare = lambda t: LIB.sub("", str(t or ""), count=1)

def gold_match(g, ref, article_only=False):
    i = g.find("#"); title, sec = (g, "") if i < 0 else (g[:i], g[i + 1:])
    if norm(title) != norm(ref["title"]) and (LIB.search(title) or norm(title) != norm(bare(ref["title"]))): return False
    return article_only or not sec or norm(sec) == norm(ref.get("section"))

def kit_titles():
    full, bares = set(), set()
    for p in KIT.values():
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        for s, t in con.execute("select source, title from articles"):
            src = SRC[s]; lab = t if src == "enwiki" else f"{LABEL.get(src, 'Source')}: {t}"
            full.add(norm(lab)); bares.add(norm(t))
        con.close()
    return full, bares

def resolvable(g, KT):
    full, bares = KT; i = g.find("#"); title = g if i < 0 else g[:i]
    return norm(title) in full if LIB.search(title) else (norm(title) in full or norm(title) in bares)

def load(f):
    """replay lines -> {id: line}; slot pack ids normalised ("local-<id>" -> "<id>", as the app names side-loaded packs)."""
    if not os.path.exists(f): return None
    out = {}
    for r in map(json.loads, open(f)):
        for L in (r.get("raw") or [], r.get("kept") or []):
            for x in L: x["pack"] = re.sub(r"^local-", "", x.get("pack") or "seed")
        out[r["id"]] = r
    return out
key = lambda L: [(x["title"], x.get("section"), x.get("pack")) for x in L or []]
p50 = lambda xs: round(statistics.median(xs), 1) if xs else None

def gold_counts(R, G, ids):
    """-> resolvable gold hits raw6/kept and all-gold hits raw6/kept (gold strings matched, summed over items)."""
    c = collections.Counter(); per = {}
    for i in ids:
        r = R[i]; g = G.get(i)
        if not isinstance(g, list) or not g: continue
        raw6, kept = (r.get("raw") or [])[:6], r.get("kept") or []
        h = {n: sum(any(gold_match(x, y) for y in L) for x in gs)
             for n, gs, L in (("res_raw6", G["_res"][i], raw6), ("res_kept", G["_res"][i], kept), ("all_raw6", g, raw6), ("all_kept", g, kept))}
        c.update(h); per[i] = h
    return dict(c), per

def main():
    KT = kit_titles(); out = {"rule": "share_kept <= 0.40 and resolvable gold raw6/kept not lower than baseline (both sets)",
                              "tree": "wt/packs", "config": "--deep --gate rules --k 6 --pool 20; v02 --tasks-from dt512 s42 traces", "sets": {}}
    for st, S in SETS.items():
        cat = {}
        for l in open(S["q"]):
            if l.strip(): r = json.loads(l); cat[r["id"]] = r.get("category")
        G = {k: v for k, v in json.load(open(S["gold"])).items() if isinstance(v, list)}
        G["_res"] = {i: [g for g in v if resolvable(g, KT)] for i, v in G.items()}
        B = load(f"{S['dir']}/{st}-base.jsonl"); ids = sorted(B)
        retr = [i for i in ids if B[i].get("k") is not None]
        gb, gbper = gold_counts(B, G, ids)
        so = {"n": len(ids), "retrieving": len(retr), "gold_items": sum(1 for i in ids if G.get(i)),
              "gold_strings": sum(len(G.get(i) or []) for i in ids), "gold_resolvable_strings": sum(len(G["_res"].get(i, [])) for i in ids),
              "base": {"kept_slots": sum(len(B[i]["kept"]) for i in ids), "empty_kept": sum(1 for i in retr if not B[i]["kept"]),
                       "p50_ms": p50([B[i]["ms"] for i in retr if B[i].get("ms") is not None]), "gold": gb,
                       "kept_slots_by_pack": dict(collections.Counter(x["pack"] for i in ids for x in B[i]["kept"]))},
              "runs": {}}
        for lab in RUNS:
            R = load(f"{S['dir']}/{st}-{lab}.jsonl")
            if R is None: so["runs"][lab] = None; continue
            assert sorted(R) == ids, (st, lab)
            mine = set(SE) if lab == "se5" else {lab}
            ks = sum(len(R[i]["kept"]) for i in ids)
            ps = sum(1 for i in ids for x in R[i]["kept"] if x["pack"] in mine)
            raw6 = sum(1 for i in ids for x in (R[i].get("raw") or [])[:6] if x["pack"] in mine)
            g, gper = gold_counts(R, G, ids)
            lost = sorted(i for i in gbper if gper.get(i, {}).get("res_kept", 0) < gbper[i]["res_kept"] or gper.get(i, {}).get("res_raw6", 0) < gbper[i]["res_raw6"])
            rr = [i for i in ids if R[i].get("k") is not None]
            catt = collections.defaultdict(lambda: collections.Counter())
            for i in ids:
                n = sum(1 for x in R[i]["kept"] if x["pack"] in mine)
                c = catt[cat.get(i)]; c["items"] += 1; c["pack_slots"] += n; c["kept_slots"] += len(R[i]["kept"]); c["items_pack_ge1"] += n > 0
            m = set().union(*(MATCH[p] for p in mine))
            def side(sel):
                c = collections.Counter()
                for k_, v in catt.items():
                    if sel(k_): c.update(v)
                return dict(c, share=round(c["pack_slots"] / max(1, c["kept_slots"]), 3))
            res = {"kept_slots": ks, "pack_kept_slots": ps, "share_kept": round(ps / max(1, ks), 3),
                   "items_pack_ge1": sum(1 for i in ids if any(x["pack"] in mine for x in R[i]["kept"])),
                   "pack_raw6_slots": raw6, "share_raw6": round(raw6 / max(1, sum(len((R[i].get("raw") or [])[:6]) for i in ids)), 3),
                   "gold": g, "gold_items_lower": lost,
                   "empty_kept": sum(1 for i in rr if not R[i]["kept"]), "changed_kept": sum(1 for i in ids if key(R[i]["kept"]) != key(B[i]["kept"])),
                   "changed_raw": sum(1 for i in ids if key(R[i]["raw"]) != key(B[i]["raw"])),
                   "retrieving": len(rr), "p50_ms": p50([R[i]["ms"] for i in rr if R[i].get("ms") is not None]),
                   "category": {"matching": sorted(m), "in": side(lambda k_: k_ in m), "out": side(lambda k_: k_ not in m),
                                "by_category": {k_: dict(v) for k_, v in sorted(catt.items(), key=lambda kv: str(kv[0]))}}}
            if lab == "se5":
                res["kept_slots_by_pack"] = dict(collections.Counter(x["pack"] for i in ids for x in R[i]["kept"]))
            res["gold_not_lower"] = g.get("res_raw6", 0) >= gb.get("res_raw6", 0) and g.get("res_kept", 0) >= gb.get("res_kept", 0)
            res["pass"] = res["share_kept"] <= 0.40 and res["gold_not_lower"]
            so["runs"][lab] = res
        out["sets"][st] = so
    out["verdict"] = {lab: ("default-eligible" if all((out["sets"][s]["runs"].get(lab) or {}).get("pass") for s in SETS) else "user-selected only")
                      for lab in RUNS if all(out["sets"][s]["runs"].get(lab) for s in SETS)}
    os.makedirs(f"{ARM}/aggregates", exist_ok=True)
    json.dump(out, open(f"{ARM}/aggregates/crowding{'-wave2' if WAVE2 else '-wave3' if WAVE3 else ''}.json", "w"), indent=1)
    for st, so in out["sets"].items():
        b = so["base"]; print(st, "n", so["n"], "retr", so["retrieving"], "base kept", b["kept_slots"], "empty", b["empty_kept"], "p50", b["p50_ms"], "gold", b["gold"], "res strings", so["gold_resolvable_strings"])
        for lab, r in so["runs"].items():
            if r: print(f"  {lab:20s} share {r['share_kept']:.3f} ({r['pack_kept_slots']}/{r['kept_slots']}) items>=1 {r['items_pack_ge1']} raw6sh {r['share_raw6']:.3f} gold {r['gold']} lower {len(r['gold_items_lower'])} empty {r['empty_kept']} chg {r['changed_kept']} p50 {r['p50_ms']} in {r['category']['in'].get('pack_slots',0)}/{r['category']['in'].get('kept_slots',0)} out {r['category']['out'].get('pack_slots',0)}/{r['category']['out'].get('kept_slots',0)}")
    print("verdict", out["verdict"])

if __name__ == "__main__": main()
