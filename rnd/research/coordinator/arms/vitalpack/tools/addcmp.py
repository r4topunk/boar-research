#!/usr/bin/env python3
"""VITALPACK-ADD replay fidelity (bench v0.1 only): patched engine (wt/vitaladd, --add-pack wiki-vital5:1) vs the q = 1
simulation of tools/quota.py (kept' = replay-base kept + first vital chunk of replay-vital-v01 kept), plus the default-off
identity check (replay-off-v01 vs deepcovfb/replay-base). Same attribution and gold-match rules as quota.py (copied, so
this never touches the blind runs quota.py also loads). Counts/ids only -> aggregates/replay-add-v01.json."""
import json, sqlite3, re, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[6]; A = ROOT/"rnd/research/coordinator/arms"
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
B, V = load(A/"deepcovfb/replay-base.jsonl"), load(A/"vitalpack/replay-vital-v01.jsonl")
import sys
TAG = sys.argv[1] if len(sys.argv) > 1 else "replay-add-v01"
P, O = load(A/f"vitalpack/{TAG}.jsonl"), load(A/"vitalpack/replay-off-v01.jsonl")
G = {k: v for k, v in json.loads((ROOT/"boar-eval/bench/v0.1/gold/sources.json").read_text()).items() if isinstance(v, list) and v and k in B}
key = lambda r: (r["title"], r.get("section"))  # source differs by design (patched carries the pack's source column)
strip = lambda r: {k: v for k, v in r.items() if k not in ("ms", "addMs")}
off_same = [i for i in B if json.dumps(strip(B[i])) == json.dumps(strip(O[i]))]
ids = list(B); retr = [i for i in ids if B[i]["k"] is not None]
sim = {i: B[i]["kept"] + [r for r in V[i]["kept"] if is_pack(r)][:1] for i in ids}
same = [i for i in ids if [key(r) for r in P[i]["kept"]] == [key(r) for r in sim[i]]]
diff = {}
for i in ids:
    if i in same: continue
    cur_same = [key(r) for r in P[i]["kept"][:len(B[i]["kept"])]] == [key(r) for r in B[i]["kept"]]
    pk = P[i]["kept"][len(B[i]["kept"]):]; sk = sim[i][len(B[i]["kept"]):]
    why = ("curated-changed" if not cur_same else
           "sim-has-pack/patched-none:" + ("dropped-by-grounding" if any(c.startswith("addpack:dropped") for c in P[i]["codes"]) else "other-top1" if P[i].get("add") else "pack-retrieve-empty") if sk and not pk else
           "patched-has-pack/sim-none" if pk and not sk else "different-pack-chunk")
    diff[i] = why
slots = sum(len(P[i]["kept"]) for i in retr); ps = sum(is_pack(r) for i in retr for r in P[i]["kept"])
bh = {i: any(hit(g, B[i]["kept"]) for g in G[i]) for i in G}; ph = {i: any(hit(g, P[i]["kept"]) for g in G[i]) for i in G}
sh = {i: any(hit(g, sim[i]) for g in G[i]) for i in G}
ms_main = [P[i]["ms"] for i in retr]; ms_add = [P[i]["addMs"] for i in retr if P[i].get("addMs") is not None]
ms_tot = [P[i]["ms"] + (P[i].get("addMs") or 0) for i in retr]
out = {"n": len(ids), "retrieving": len(retr),
       "default_off": {"identical_lines_excl_ms": len(off_same), "of": len(ids), "kept_identical": sum(json.dumps(B[i]["kept"]) == json.dumps(O[i]["kept"]) for i in ids)},
       "fidelity": {"identical": len(same), "differing": diff},
       "patched": {"kept_slots": slots, "pack_slots": ps, "pack_share": round(ps / max(1, slots), 3),
                   "items_with_pack": sum(1 for i in retr if any(is_pack(r) for r in P[i]["kept"])),
                   "empty_kept": sum(1 for i in retr if not P[i]["kept"]), "empty_base": sum(1 for i in retr if not B[i]["kept"]),
                   "gold_enters": sorted(i for i in G if ph[i] and not bh[i]), "gold_leaves": sorted(i for i in G if bh[i] and not ph[i]),
                   "with_gold": sum(ph.values()), "addpack_codes": {c: sum(c in P[i]["codes"] for i in ids) for c in sorted({c for i in ids for c in P[i]["codes"] if c.startswith("addpack:")})}},
       "simulation_q1": {"gold_enters": sorted(i for i in G if sh[i] and not bh[i]), "pack_share": round(sum(is_pack(r) for i in retr for r in sim[i]) / max(1, sum(len(sim[i]) for i in retr)), 3)},
       "retrieve_ms_p50": {"curated": round(statistics.median(ms_main), 1), "add_call": round(statistics.median(ms_add), 1), "total": round(statistics.median(ms_tot), 1),
                           "base_replay": round(statistics.median([B[i]["ms"] for i in retr]), 1)}}
out["patched"]["gold_enters_n"] = len(out["patched"]["gold_enters"]); out["simulation_q1"]["gold_enters_n"] = len(out["simulation_q1"]["gold_enters"])
(A/f"vitalpack/aggregates/{TAG}.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
