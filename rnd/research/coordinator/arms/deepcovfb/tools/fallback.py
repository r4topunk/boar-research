#!/usr/bin/env python3
"""DEEPCOV-FB step 0: fallback recombination + metrics over two deep-tier replays (no LLM, no judge).

Usage (repo root): python3 -I rnd/research/coordinator/arms/deepcovfb/tools/fallback.py
Inputs : arms/deepcovfb/replay-base.jsonl (curated kit), replay-peer.jsonl (kit + enwiki top-100k as a peer pack),
         boar-eval/bench/v0.1/gold/sources.json, shared-data/crypto/boar-crypto.sqlite (pack attribution).
Arms   : base | peer | fallback (base kept if non-empty, else peer kept[:CAP]) |
         fallback-raw (base kept if non-empty, else the enwiki-pack chunks of the peer run's top-20 pool, top CAP by rank;
         bypasses compressContext/onSubject/the 400-token cap) | fallback-raw6 (same from the peer `raw` top-6 only).
R2     : a retrieving item (engine asked retrieve) whose pre-answer sources event is empty.
Gold   : scorers/retrieval.py match rule (casefold, library prefix, optional #section) applied to the kept list.
Output : arms/deepcovfb/aggregates/replay-v01.json; table on stdout.
"""
import json, re, sqlite3, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
A = ROOT / "rnd/research/coordinator/arms/deepcovfb"
CAP = 8
GOLD = json.loads((ROOT / "boar-eval/bench/v0.1/gold/sources.json").read_text())
GOLD = {k: v for k, v in GOLD.items() if isinstance(v, list) and v}

_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).casefold()
bare = lambda t: _LIB.sub("", str(t or ""), count=1)
def match(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))):
        return False
    return not section or norm(section) == norm(ref.get("section"))
hit = lambda g, refs: any(match(g, r) for r in refs)

load = lambda f: {r["id"]: r for r in map(json.loads, open(A / f)) }
base, peer = load("replay-base.jsonl"), load("replay-peer.jsonl")
assert list(base) == list(peer), "item order differs"
ids = list(base)

# Pack attribution: a Wikipedia-labelled chunk whose title is not a Wikipedia article of the curated crypto pack.
con = sqlite3.connect(f"file:{ROOT / 'shared-data/crypto/boar-crypto.sqlite'}?mode=ro", uri=True)
CRYPTO_TITLES = {norm(t) for (t,) in con.execute("select title from articles")}
def is_pack(ref):
    return str(ref.get("source") or "").startswith("Wikipedia") and norm(bare(ref.get("title"))) not in CRYPTO_TITLES

retrieving = [i for i in ids if base[i]["k"] is not None]
def kept_of(arm, i):
    b = base[i]["kept"]
    if arm == "base": return b
    if arm == "peer": return peer[i]["kept"]
    if b: return b
    if arm == "fallback": return peer[i]["kept"][:CAP]
    if arm == "fallback-raw": return [r for r in peer[i].get("pool", []) if is_pack(r)][:CAP]
    if arm == "fallback-raw6": return [r for r in peer[i]["raw"] if is_pack(r)][:CAP]
ARMS = ["base", "peer", "fallback", "fallback-raw", "fallback-raw6"]

def r2_reason(i):
    c = base[i]["codes"]
    if "grounding:no-good-source" in c: return "grounding:no-good-source"
    if "grounding:health-no-source" in c: return "grounding:health-no-source"
    if not base[i]["raw"]: return "empty-raw (context:0->0)"
    return "other"
r2 = [i for i in retrieving if not base[i]["kept"]]
out = {"setup": {"tree": "wt/cut7", "tier": "deep (alwaysComplete + deepModelId, k 6, ctx 400)", "gate": "rules",
                 "detector": "lexical", "cap": CAP, "n": len(ids), "retrieving": len(retrieving), "gold_items": len(GOLD)},
       "r2": {"count": len(r2), "ids": r2, "reasons": {i: r2_reason(i) for i in r2},
              "gold_items_among_r2": [i for i in r2 if i in GOLD]},
       "arms": {}}
base_hit = {i: [g for g in GOLD[i] if hit(g, kept_of("base", i))] for i in GOLD}
for arm in ARMS:
    rec, with_gold, enters, leaves, empty, slots, pack_slots, emptied = [], [], [], [], [], 0, 0, []
    for i in ids:
        k = kept_of(arm, i)
        if i in retrieving:
            if not k: empty.append(i)
            if base[i]["kept"] and not k: emptied.append(i)
            slots += len(k); pack_slots += sum(is_pack(r) for r in k)
        if i in GOLD:
            h = [g for g in GOLD[i] if hit(g, k)]
            rec.append(len(h) / len(GOLD[i]))
            if h: with_gold.append(i)
            if h and not base_hit[i]: enters.append(i)
            if base_hit[i] and not h: leaves.append(i)
    out["arms"][arm] = {"recall_at_kept_39": round(statistics.mean(rec), 4), "items_gold_in_kept": len(with_gold),
                        "gold_enters": enters, "gold_leaves": leaves, "empty_kept": len(empty), "emptied_vs_base": emptied,
                        "kept_slots": slots, "pack_slots": pack_slots,
                        "pack_share": round(pack_slots / slots, 3) if slots else None,
                        "items_with_pack_chunk": sum(1 for i in retrieving if any(is_pack(r) for r in kept_of(arm, i)))}
# raw recall@6 (scorer's recall@k) for reference
for name, run in (("base", base), ("peer", peer)):
    out["arms"][name]["recall_at_6_raw_39"] = round(statistics.mean(
        sum(hit(g, run[i]["raw"][:6]) for g in GOLD[i]) / len(GOLD[i]) for i in GOLD), 4)
ms = lambda run: [run[i]["ms"] for i in retrieving if run[i]["ms"] is not None]
out["latency_ms"] = {n: {"p50": round(statistics.median(ms(r)), 1), "p90": round(sorted(ms(r))[int(0.9 * len(ms(r)))], 1)}
                     for n, r in (("base", base), ("peer", peer))}
fb = out["arms"]["fallback"]
out["gate"] = {"rule": "fallback: gold enters kept on >= 5 items and 0 items emptied (v0.1)",
               "enters": len(fb["gold_enters"]), "emptied": len(fb["emptied_vs_base"]),
               "pass": len(fb["gold_enters"]) >= 5 and not fb["emptied_vs_base"]}
(A / "aggregates").mkdir(exist_ok=True)
(A / "aggregates/replay-v01.json").write_text(json.dumps(out, indent=1) + "\n")
print(f"R2 {len(r2)}/{len(retrieving)}: " + ", ".join(f"{i}[{r2_reason(i)}]" for i in r2))
print("arm | recall@kept | gold-in-kept | enters | leaves | empty | emptied | pack slots/kept | items w/ pack chunk")
for a, m in out["arms"].items():
    print(f"{a} | {m['recall_at_kept_39']} | {m['items_gold_in_kept']} | {len(m['gold_enters'])} {m['gold_enters']} | "
          f"{len(m['gold_leaves'])} {m['gold_leaves']} | {m['empty_kept']} | {len(m['emptied_vs_base'])} | "
          f"{m['pack_slots']}/{m['kept_slots']} | {m['items_with_pack_chunk']}")
print("raw recall@6:", out["arms"]["base"]["recall_at_6_raw_39"], out["arms"]["peer"]["recall_at_6_raw_39"])
print("latency", out["latency_ms"]); print("gate", out["gate"])
