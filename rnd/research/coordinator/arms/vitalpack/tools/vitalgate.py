#!/usr/bin/env python3
"""VITALPACK step 0 gate: metrics over base vs vital deep-tier replays (no LLM, no judge). Prints counts/ids only.
usage: vitalgate.py --base b.jsonl --vital v.jsonl --label v01 [--gold sources.json] [--ref-nokept ids.txt] --out agg.json"""
import argparse, json, re, sqlite3, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[6]
_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).casefold()
bare = lambda t: _LIB.sub("", str(t or ""), count=1)
def match(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
hit = lambda g, refs: any(match(g, r) for r in refs)
con = sqlite3.connect(f"file:{ROOT / 'shared-data/crypto/boar-crypto.sqlite'}?mode=ro", uri=True)
CRYPTO = {norm(t) for (t,) in con.execute("select title from articles")}
# The engine reports formatVersion-1 pack chunks with source None (base run: 1 such chunk, the seed corpus). Attribution:
# source None or "Wikipedia…" AND the title is an article of wiki-vital5 AND not a Wikipedia article of the crypto pack.
vcon = sqlite3.connect(f"file:{ROOT / 'shared-data/packs/wiki-vital5.sqlite'}?mode=ro", uri=True)
VITAL = {norm(t) for (t,) in vcon.execute("select distinct title from chunks")}
is_pack = lambda r: (r.get("source") is None or str(r.get("source")).startswith("Wikipedia")) and norm(bare(r.get("title"))) in VITAL and norm(bare(r.get("title"))) not in CRYPTO
ap = argparse.ArgumentParser(); ap.add_argument("--base", required=True); ap.add_argument("--vital", required=True); ap.add_argument("--label", required=True)
ap.add_argument("--gold"); ap.add_argument("--ref-nokept"); ap.add_argument("--out", required=True); a = ap.parse_args()
load = lambda f: {r["id"]: r for r in map(json.loads, open(f))}
B, V = load(a.base), load(a.vital)
ids = [i for i in B if i in V]
retr = [i for i in ids if B[i]["k"] is not None]
empty_b = [i for i in retr if not B[i]["kept"]]; empty_v = [i for i in retr if not V[i]["kept"]]
filled = [i for i in empty_b if V[i]["kept"]]; emptied = [i for i in retr if B[i]["kept"] and not V[i]["kept"]]
slots = sum(len(V[i]["kept"]) for i in retr); pack_slots = sum(is_pack(r) for i in retr for r in V[i]["kept"])
base_slots = sum(len(B[i]["kept"]) for i in retr)
items_pack = [i for i in retr if any(is_pack(r) for r in V[i]["kept"])]
displaced = sum(1 for i in retr if B[i]["kept"] and any(is_pack(r) for r in V[i]["kept"]))
ms = lambda D: statistics.median([D[i]["ms"] for i in retr]) if retr else None
collide = sum(1 for i in retr for r in B[i]["kept"] if is_pack(r))  # base kept chunks the rule would attribute to the pack (seed-corpus title collisions)
out = {"label": a.label, "base_kept_attributed_to_pack": collide, "n": len(ids), "retrieving": len(retr), "empty_kept_base": len(empty_b), "empty_kept_vital": len(empty_v),
       "filled_ids": filled, "filled_share_of_empty": round(len(filled) / max(1, len(empty_b)), 3), "emptied_ids": emptied,
       "kept_slots_base": base_slots, "kept_slots_vital": slots, "pack_slots": pack_slots, "pack_share": round(pack_slots / max(1, slots), 3),
       "items_with_pack_chunk": len(items_pack), "items_base_kept_and_pack_chunk": displaced,
       "retrieve_ms_p50": {"base": ms(B), "vital": ms(V)}, "raw_pack_share": round(sum(is_pack(r) for i in retr for r in V[i]["raw"]) / max(1, sum(len(V[i]["raw"]) for i in retr)), 3)}
if a.gold:
    G = {k: v for k, v in json.loads(open(a.gold).read()).items() if isinstance(v, list) and v and k in B}
    bh = {i: [g for g in G[i] if hit(g, B[i]["kept"])] for i in G}; vh = {i: [g for g in G[i] if hit(g, V[i]["kept"])] for i in G}
    out["gold"] = {"items": len(G), "recall_kept_base": round(sum(len(bh[i]) / len(G[i]) for i in G) / len(G), 3), "recall_kept_vital": round(sum(len(vh[i]) / len(G[i]) for i in G) / len(G), 3),
                   "with_gold_base": sum(1 for i in G if bh[i]), "with_gold_vital": sum(1 for i in G if vh[i]),
                   "enters": [i for i in G if vh[i] and not bh[i]], "leaves": [i for i in G if bh[i] and not vh[i]],
                   "raw_recall6_base": round(sum(len([g for g in G[i] if hit(g, B[i]["raw"])]) / len(G[i]) for i in G) / len(G), 3),
                   "raw_recall6_vital": round(sum(len([g for g in G[i] if hit(g, V[i]["raw"])]) / len(G[i]) for i in G) / len(G), 3)}
if a.ref_nokept:
    R = {l.strip() for l in open(a.ref_nokept) if l.strip()}
    out["ref_nokept"] = {"n": len(R), "also_empty_in_base_replay": len(R & set(empty_b)), "filled_by_vital": len(R & set(filled)), "kept_in_base_replay": len(R & set(i for i in retr if B[i]["kept"]))}
json.dump(out, open(a.out, "w"), indent=1); print(json.dumps(out))
