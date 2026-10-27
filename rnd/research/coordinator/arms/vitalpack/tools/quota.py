#!/usr/bin/env python3
"""VITALPACK post-hoc hypothesis (labelled, the one allowed per arm): the pack as an ADDITIVE, QUOTA-CAPPED peer —
kept' = base kept + the first q vital-pack chunks of the vital run's kept list (never displaces a curated chunk).
Prints the three step-0 gate numbers for q in 1..3 on each set. Counts/ids only."""
import json, sys, sqlite3, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[6]
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).casefold(); bare = lambda t: _LIB.sub("", str(t or ""), count=1)
def match(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
hit = lambda g, refs: any(match(g, r) for r in refs)
CRYPTO = {norm(t) for (t,) in sqlite3.connect(f"file:{ROOT/'shared-data/crypto/boar-crypto.sqlite'}?mode=ro", uri=True).execute("select title from articles")}
VITAL = {norm(t) for (t,) in sqlite3.connect(f"file:{ROOT/'shared-data/packs/wiki-vital5.sqlite'}?mode=ro", uri=True).execute("select distinct title from chunks")}
is_pack = lambda r: (r.get("source") is None or str(r.get("source")).startswith("Wikipedia")) and norm(bare(r.get("title"))) in VITAL and norm(bare(r.get("title"))) not in CRYPTO
load = lambda f: {r["id"]: r for r in map(json.loads, open(f))}
SETS = {"v01": (ROOT/"rnd/research/coordinator/arms/deepcovfb/replay-base.jsonl", ROOT/"rnd/research/coordinator/arms/vitalpack/replay-vital-v01.jsonl", ROOT/"boar-eval/bench/v0.1/gold/sources.json"),
        "vpara": (ROOT/"blind/V-para/runs-vitalpack/replay-base.jsonl", ROOT/"blind/V-para/runs-vitalpack/replay-vital.jsonl", None),
        "v02": (ROOT/"blind/bench-v02/runs-vitalpack/replay-base.jsonl", ROOT/"blind/bench-v02/runs-vitalpack/replay-vital.jsonl", None)}
out = {}
for lab, (bf, vf, gf) in SETS.items():
    B, V = load(bf), load(vf); ids = [i for i in B if i in V]; retr = [i for i in ids if B[i]["k"] is not None]
    G = {k: v for k, v in json.loads(open(gf).read()).items() if isinstance(v, list) and v and k in B} if gf else {}
    for q in (1, 2, 3):
        kept = {i: B[i]["kept"] + [r for r in V[i]["kept"] if is_pack(r)][:q] for i in ids}
        slots = sum(len(kept[i]) for i in retr); ps = sum(is_pack(r) for i in retr for r in kept[i])
        empty_b = [i for i in retr if not B[i]["kept"]]; filled = [i for i in empty_b if kept[i]]
        row = {"pack_share": round(ps / max(1, slots), 3), "kept_slots": slots, "filled": len(filled), "empty_base": len(empty_b), "filled_share": round(len(filled) / max(1, len(empty_b)), 3), "items_with_pack": sum(1 for i in retr if any(is_pack(r) for r in kept[i]))}
        if G:
            bh = {i: bool([g for g in G[i] if hit(g, B[i]["kept"])]) for i in G}; qh = {i: bool([g for g in G[i] if hit(g, kept[i])]) for i in G}
            row["gold_enters"] = sum(1 for i in G if qh[i] and not bh[i]); row["with_gold"] = sum(qh.values()); row["recall_kept"] = round(sum(len([g for g in G[i] if hit(g, kept[i])]) / len(G[i]) for i in G) / len(G), 3)
        out[f"{lab}-q{q}"] = row
json.dump(out, open(ROOT/"rnd/research/coordinator/arms/vitalpack/aggregates/quota-hypothesis.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
