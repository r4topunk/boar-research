#!/usr/bin/env python3
"""COVERAGE-MAP summary (0 LLM): combine the lexical funnel (kfull-funnel.json) and the cm oracle funnel (cm-stage.json) into the K-FULL
funnel read: per arm, MAIN 92 / v0.1 52 / cm 40 stage counts (cm = best of oracle and lexical stage), v0.1 kept gained/lost vs K3, kept-slot
shares per pack. Writes aggregates/summary.json and kfull-funnel.md. Usage: python3 -I summarize.py"""
import json
C = "<workspace>/rnd/research/coordinator/arms/coverage-map/"
F = json.load(open(C + "aggregates/kfull-funnel.json")); M = json.load(open(C + "aggregates/cm-stage.json"))
ARMS = ["K3", "K3CM", "K3W", "KSE", "KFULL"]; ORD = {"S1": 0, "S2": 1, "S3": 2, "K": 3}; ST = ["S1", "S2", "S3", "K"]
def stage(i, a):
    s = F["items"][i][a]["stage"]
    if i in M[a]["items"] and ORD[M[a]["items"][i]] > ORD[s]: s = M[a]["items"][i]
    return s
out = {}
for a in ARMS:
    c = {"v0.1": {s: 0 for s in ST}, "cm": {s: 0 for s in ST}}
    for i, e in F["items"].items(): c[e["set"]][stage(i, a)] += 1
    v = c["v0.1"]; m = c["cm"]
    base = {i for i, e in F["items"].items() if e["set"] == "v0.1" and stage(i, "K3") == "K"}
    now = {i for i, e in F["items"].items() if e["set"] == "v0.1" and stage(i, a) == "K"}
    slots = F["arms"][a]["kept_slots_by_pack"]; tot = sum(slots.values())
    out[a] = dict(MAIN92={s: v[s] + m[s] for s in ST}, v01_52=v, cm40=m, v01_kept_gained=sorted(now - base), v01_kept_lost=sorted(base - now),
                  kept_slot_share={k: round(n / tot, 3) for k, n in slots.items()}, mean_kept=round(F["arms"][a]["mean_kept"], 2), wall_ms_mean=round(F["arms"][a]["wall_ms_mean"]))
json.dump(out, open(C + "aggregates/summary.json", "w"), indent=1)
L = ["# K-FULL funnel read (2026-10-22, 0 LLM): MAIN 92 keyed, replay of answer() up to generation, five kits", "",
     "Stages: S1 fact in no installed pack (lexical pool rule; cm: oracle = the item's own source article) · S2 in a pack, not retrieved (raw + wide-12) · S3 retrieved, not kept · K kept (= funnel S4+S5; no generation). cm stage = best of oracle and lexical.", "",
     "| kit | packs | MAIN 92 S1/S2/S3/K | v0.1 52 S1/S2/S3/K | cm 40 S1/S2/S3/K | v0.1 kept gained / lost vs K3 | mean kept | ms/q |", "|---|---|---|---|---|---|---|---|"]
NP = {"K3": 6, "K3CM": 8, "K3W": 7, "KSE": 17, "KFULL": 18}
for a in ARMS:
    o = out[a]; f = lambda d: "/".join(str(d[s]) for s in ST)
    L.append(f"| {a} | {NP[a]} | {f(o['MAIN92'])} | {f(o['v01_52'])} | {f(o['cm40'])} | +{len(o['v01_kept_gained'])} {o['v01_kept_gained']} / -{len(o['v01_kept_lost'])} {o['v01_kept_lost']} | {o['mean_kept']} | {o['wall_ms_mean']} |")
L += ["", "Kept-slot share by pack (top 5):"]
for a in ARMS:
    L.append(f"- {a}: " + ", ".join(f"{k} {v:.0%}" for k, v in list(out[a]['kept_slot_share'].items())[:5]))
L += ["", "Per item (v0.1 + cm): stage per kit", "", "| id | set | funnel K1 / K3 | " + " | ".join(ARMS) + " | KFULL kept packs |", "|---|---|---|" + "---|" * len(ARMS) + "---|"]
for i, e in F["items"].items():
    L.append(f"| {i} | {e['set']} | {e['funnel_K1']} / {e['funnel_K3']} | " + " | ".join(stage(i, a) for a in ARMS) + f" | {', '.join(e['KFULL']['kept_packs'])} |")
open(C + "kfull-funnel.md", "w").write("\n".join(L) + "\n")
for a in ARMS: print(a, out[a]["MAIN92"], out[a]["v01_52"], out[a]["cm40"], out[a]["v01_kept_gained"], out[a]["v01_kept_lost"])
