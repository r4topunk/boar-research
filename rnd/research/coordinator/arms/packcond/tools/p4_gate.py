#!/usr/bin/env python3
"""PACKCOND P4 step 0 replay gate (0 LLM): settings.packGround off vs on (wt/packcond), deep tier, k 6.
- H32: v0.2 in-pack ids (P1 H F0 true); metric = the F0 article (P1 hit_articles, p4_diag.is_f0) in the engine's kept sources.
- R20: random20-v02 control; items whose kept list (title#section) changes, pack-labelled share of kept slots.
- v0.1 public: gold (bench/v0.1/gold/sources.json, vitalpack/tools/quota.py match rule) entering / leaving kept.
- default-off identity: off run == the pre-patch run (dt512 code), all fields but timing.
GATE: F0 article kept >= 16/32 with the setting on AND <= 4/20 control items change. Writes ids/titles/counts only."""
import json, sys, re, collections
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packcond/tools")
import p4_diag as P
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/packcond"; D = f"{ROOT}/blind/bench-v02/runs-packcond"
load = lambda f: {r["id"]: r for r in map(json.loads, open(f))}
key = lambda L: [(c["title"], c.get("section")) for c in L]
pg = lambda r: next((c for c in r["codes"] if c.startswith("packground:")), None)
def ispack(c): return P.pack_of(c["title"])[0] in ("wikivoyage", "crypto") or str(c.get("source") or "").startswith(("Wikivoyage", "Ethereum", "Bitcoin", "ethereum.org"))
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).casefold(); bare = lambda t: _LIB.sub("", str(t or ""), count=1)
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
def strip(r): r = dict(r); r.pop("ms", None); return json.dumps(r, sort_keys=True)

agg = json.load(open(f"{ARM}/aggregates/packcond-H-v02.json"))
F0 = {it["id"]: {p: {a.lower() for a in v["hit_articles"]} for p, v in it["packs"].items() if v["f0"]} for it in agg["items"] if it["F0"]}
out = {"setting": "packGround", "tree": "wt/packcond", "replay": "arms/packcond/tools/replay-pg.ts --deep --gate rules --k 6 --pool 20 --tasks-from H traces"}
for n in ("H32", "R20"):
    off, on, pre = load(f"{D}/pg-off-{n}.jsonl"), load(f"{D}/pg-on-{n}.jsonl"), load(f"{D}/pg-prepatch-{n}.jsonl")
    row = {"n": len(off), "default_off_identical_to_prepatch": all(strip(off[i]) == strip(pre[i]) for i in off),
           "kept_changed": sorted(i for i in off if key(off[i]["kept"]) != key(on[i]["kept"])),
           "packground_codes_on": dict(collections.Counter(re.sub(r"\d+", "N", pg(on[i]) or "-") for i in on)),
           "kept_slots_off": sum(len(r["kept"]) for r in off.values()), "kept_slots_on": sum(len(r["kept"]) for r in on.values()),
           "pack_share_off": round(sum(ispack(c) for r in off.values() for c in r["kept"]) / max(1, sum(len(r["kept"]) for r in off.values())), 3),
           "pack_share_on": round(sum(ispack(c) for r in on.values() for c in r["kept"]) / max(1, sum(len(r["kept"]) for r in on.values())), 3),
           "empty_kept_off": sum(1 for r in off.values() if r["k"] is not None and not r["kept"]),
           "empty_kept_on": sum(1 for r in on.values() if r["k"] is not None and not r["kept"])}
    row["kept_changed_n"] = len(row["kept_changed"])
    if n == "H32":
        ko = {i for i in off if any(P.is_f0(c, F0[i]) for c in off[i]["kept"])}; kn = {i for i in on if any(P.is_f0(c, F0[i]) for c in on[i]["kept"])}
        row.update(f0_kept_off=len(ko), f0_kept_on=len(kn), f0_enters=sorted(kn - ko), f0_leaves=sorted(ko - kn))
    out[n] = row
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
off, on = load(f"{ARM}/replay/pg-off-v01.jsonl"), load(f"{ARM}/replay/pg-on-v01.jsonl")
gi = [i for i in G if i in off]
ho = {i for i in gi if any(gmatch(g, c) for g in G[i] for c in off[i]["kept"])}; hn = {i for i in gi if any(gmatch(g, c) for g in G[i] for c in on[i]["kept"])}
out["v01"] = {"n": len(off), "gold_items": len(gi), "gold_kept_off": len(ho), "gold_kept_on": len(hn), "gold_enters": sorted(hn - ho), "gold_leaves": sorted(ho - hn),
              "kept_changed_n": sum(1 for i in off if key(off[i]["kept"]) != key(on[i]["kept"])),
              "packground_codes_on": dict(collections.Counter(re.sub(r"\d+", "N", pg(on[i]) or "-") for i in on)),
              "empty_kept_off": sum(1 for r in off.values() if r["k"] is not None and not r["kept"]), "empty_kept_on": sum(1 for r in on.values() if r["k"] is not None and not r["kept"])}
h, c = out["H32"], out["R20"]
out["gate"] = {"rule": "f0_kept_on >= 16/32 and R20 kept_changed <= 4/20", "f0_kept_on": h["f0_kept_on"], "r20_changed": c["kept_changed_n"],
               "pass": h["f0_kept_on"] >= 16 and c["kept_changed_n"] <= 4}
json.dump(out, open(f"{ARM}/aggregates/p4-gate.json", "w"), indent=1)
print(json.dumps({k: (v if k == "gate" else {x: y for x, y in v.items() if not isinstance(y, list) or len(y) < 12}) for k, v in out.items() if isinstance(v, dict)}, indent=1))
