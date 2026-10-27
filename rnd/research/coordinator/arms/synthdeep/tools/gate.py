#!/usr/bin/env python3
"""SYNTHDEEP replay gate (B7): per comparison item, sides represented in the engine's kept sources, cmpSplit on vs off.
Item set = v0.1 ids lan-cmp-* + items whose route task is compare + any item whose searched query yields two sides.
A kept ref counts for a side if it is the pinned side article (ref.side) or its title names the side (titleNamesSide
port) or contains the side phrase. Gold match = arms/vitalpack/tools/quota.py rule. Output: counts/ids only."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[6]; A = ROOT / "rnd/research/coordinator/arms/synthdeep"
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).casefold(); bare = lambda t: _LIB.sub("", str(t or ""), count=1)
def match(gold, ref):  # quota.py
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
sing = lambda s: re.sub(r"(?<=\w{3})(es|s)$", "", s.lower())
def names_side(title, side):  # src/rag/comparison.ts titleNamesSide + library prefix + phrase containment
    t = re.sub(r"\s*\(.*\)$", "", re.sub(r"^Wikivoyage:\s*", "", bare(title), flags=re.I)).strip()
    ws = side.split()
    if any(sing(" ".join(ws[i:])) == sing(t) for i in range(len(ws))): return True
    return re.search(r"\b" + re.escape(sing(side)) + r"", t.lower()) is not None
def per_side(kept, sides): return [sum(1 for r in kept if r.get("side") == s or names_side(r["title"], s)) for s in sides]
load = lambda f: {r["id"]: r for r in map(json.loads, open(f))}
ON, OFF = load(A / "replay-on-v01.jsonl"), load(A / "replay-off-v01.jsonl")
G = {k: v for k, v in json.load(open(ROOT / "boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list)}
task = lambda r: next((c[5:] for c in r["codes"] if c.startswith("task:")), None)
ids = [i for i in ON if i.startswith("lan-cmp-") or task(ON[i]) == "compare" or task(OFF[i]) == "compare" or ON[i].get("sides")]
rows = []
for i in ids:
    on, off = ON[i], OFF[i]; sides = on.get("sides") or []
    g = G.get(i, []); gh = lambda r: sorted(x for x in g if any(match(x, k) for k in r["kept"]))
    kon, koff = per_side(on["kept"], sides), per_side(off["kept"], sides)
    rows.append({"id": i, "task": task(on), "sides": len(sides), "fired": any(c.startswith("cmpsplit:sides-2") for c in on["codes"]),
                 "kept_per_side_off": koff, "kept_per_side_on": kon, "both_off": len(sides) == 2 and min(koff) >= 1, "both_on": len(sides) == 2 and min(kon) >= 1,
                 "kept_off": len(off["kept"]), "kept_on": len(on["kept"]), "gold_n": len(g), "gold_off": len(gh(off)), "gold_on": len(gh(on)),
                 "gold_lost": sorted(set(gh(off)) - set(gh(on))) != [], "codes_on": [c for c in on["codes"] if c.startswith("cmpsplit:")]})
gained = [r["id"] for r in rows if r["both_on"] and not r["both_off"]]; lost_both = [r["id"] for r in rows if r["both_off"] and not r["both_on"]]
gold_lost = [r["id"] for r in rows if r["gold_lost"]]
# whole-set gold check (the setting could move any item, not just these)
gold_lost_all = [i for i in G if i in ON and set(x for x in G[i] if any(match(x, k) for k in OFF[i]["kept"])) - set(x for x in G[i] if any(match(x, k) for k in ON[i]["kept"]))]
gold_gain_all = [i for i in G if i in ON and set(x for x in G[i] if any(match(x, k) for k in ON[i]["kept"])) - set(x for x in G[i] if any(match(x, k) for k in OFF[i]["kept"]))]
changed_kept = [i for i in ON if json.dumps([{k: v for k, v in x.items() if k != "side"} for x in ON[i]["kept"]]) != json.dumps(OFF[i]["kept"])]
ref = load(ROOT / "rnd/research/coordinator/arms/vitalpack/replay-base-dt512-v01.jsonl"); cut7 = load(ROOT / "rnd/research/coordinator/arms/deepcovfb/replay-base.jsonl")
ident = lambda B, f: sum(1 for i in OFF if i in B and json.dumps(OFF[i][f]) == json.dumps(B[i][f]))
out = {"items": rows, "n_items": len(rows), "fired_items": sum(r["fired"] for r in rows), "both_off": sum(r["both_off"] for r in rows), "both_on": sum(r["both_on"] for r in rows),
       "gained_both": gained, "lost_both": lost_both, "gold_lost_cmp": gold_lost, "gold_lost_all": gold_lost_all, "gold_gain_all": gold_gain_all,
       "items_kept_changed_on_vs_off": changed_kept, "fires_outside_cmp_set": [i for i in ON if any(c == "cmpsplit:sides-2" for c in ON[i]["codes"]) and i not in ids],
       "off_identity": {"vs_dt512_replay_kept": ident(ref, "kept"), "vs_dt512_replay_raw": ident(ref, "raw"), "vs_dt512_replay_codes": ident(ref, "codes"), "vs_deepcovfb_cut7_base_kept": ident(cut7, "kept"), "n": len(OFF)},
       "verdict": "PASS" if len(gained) >= 5 and not gold_lost_all else "FAIL"}
(A / "aggregates").mkdir(exist_ok=True); json.dump(out, open(A / "aggregates/replay-v01.json", "w"), indent=1)
for r in rows: print(r["id"], r["task"], "sides", r["sides"], "fired", r["fired"], "off", r["kept_per_side_off"], r["kept_off"], "on", r["kept_per_side_on"], r["kept_on"], "gold", f'{r["gold_off"]}->{r["gold_on"]}/{r["gold_n"]}', r["codes_on"])
for k in ("n_items", "fired_items", "both_off", "both_on", "gained_both", "lost_both", "gold_lost_all", "gold_gain_all", "items_kept_changed_on_vs_off", "fires_outside_cmp_set", "off_identity", "verdict"): print(k, out[k])
