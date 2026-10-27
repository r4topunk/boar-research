#!/usr/bin/env python3
"""CV5-PER100-OPUS prep (0 calls). python3 -I cv5_per100_prep.py -> ../cv5-per100/in/{set.json,<tier>-<unit>.ids}
Population: hon67.py desktop MAIN 97 K0 rows D (4B vs4b s42, Gemma stage2 s42, 1.7B lpctl control s42), unchanged.
(a) census: every row SHOWN under refuse-by-default (not r["hidden"]);
(b) hidden sample: per tier, rows hidden and not engine declines (text exists), stratified by the Haiku label (CE corr<=1.5 / correct corr>=4 /
    partial), 20 per tier, proportional allocation (largest remainder, >= 1 per non-empty stratum), random.Random(f"cv5p100-{tier}-{stratum}").
Unit = unique (item, answer text); existing Opus judge.v1 rows of the identical unit and frame (refs/questions sha of that bench unit, seed 7,
both orders) are reused, including CV5-LADDER-OPUS outputs. New units are judged on the first tier trace carrying them (order 4B, Gemma, 1.7B)."""
import json, sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP, cv5_per100_common as PC
G, TRF, TX, H67SHA = PC.load(); D = G["D"]; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/cv5-per100/in/"
TIERS = ("4B", "Gemma", "1.7B"); NH = 20
cls = lambda r: "CE" if r["corr"] <= 1.5 else ("correct" if r["corr"] >= 4 else "partial")
shown = {t: sorted(i for i, r in D[t].items() if not r["hidden"]) for t in TIERS}
hidpop = {t: sorted(i for i, r in D[t].items() if r["hidden"] and not r["dec"]) for t in TIERS}
sample, strata = {}, {}
for t in TIERS:
    by = collections.defaultdict(list)
    for i in hidpop[t]: by[cls(D[t][i])].append(i)
    N = len(hidpop[t]); ks = sorted(by); quota = {k: NH * len(by[k]) / N for k in ks}; alloc = {k: max(1, int(quota[k])) for k in ks}
    for k in sorted(ks, key=lambda k: -(quota[k] - int(quota[k]))):
        if sum(alloc.values()) >= NH: break
        if alloc[k] < len(by[k]): alloc[k] += 1
    while sum(alloc.values()) > NH: k = max(ks, key=lambda k: alloc[k]); alloc[k] -= 1
    sample[t] = {}
    for k in ks:
        ids = sorted(by[k]); random.Random(f"cv5p100-{t}-{k}").shuffle(ids); sample[t][k] = sorted(ids[:min(alloc[k], len(ids))])
    strata[t] = {k: len(by[k]) for k in ks}
FR = {}
for u in ("v01", "qa-cooking-se", "qa-money-se"):
    f = {"v01": f"{G['A']}/lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"}.get(u, f"{G['A']}/lp-screens/control/judgments/lpctl-K0-main-s42-{u}.judgments.jsonl")
    r = json.loads(open(f).readline()); FR[u] = (r["refsSha256"], r["questionsSha256"])
P = {}
for u, (fr, fq) in FR.items(): P.update(CP.pool(fr, fq, exclude_prefix=os.path.dirname(OUT.rstrip("/"))))
units = {}
def add(t, i, why):
    k = CP.key(i, TX[t][i]); u = units.setdefault(k, {"id": i, "rows": [], "judge_on": t}); u["rows"].append([t, why])
for t in TIERS:
    for i in shown[t]: add(t, i, "shown")
    for k, ids in sample[t].items():
        for i in ids: add(t, i, f"hidden-{k}")
for k, u in units.items(): u["reuse"] = P[k]["src"] if k in P else None
files = collections.defaultdict(list)
for k, u in units.items():
    if not u["reuse"]: files[f'{u["judge_on"]}-{PC.bench_of(u["id"])[0]}'].append(u["id"])
for f in os.listdir(OUT):
    if f.endswith(".ids"): os.remove(OUT + f)
for f, ids in files.items():
    assert len(ids) == len(set(ids)); open(OUT + f"{f}.ids", "w").write("".join(i + "\n" for i in ids))
new = sum(len(v) for v in files.values())
doc = dict(hon67_sha256=H67SHA, traces=TRF, frames=FR, shown={t: len(v) for t, v in shown.items()}, hidden_text_pop=strata, hidden_sample=sample,
           units=units, n_units=len(units), reused=sum(1 for u in units.values() if u["reuse"]), new_units=new, planned_calls=2 * new, files={k: len(v) for k, v in files.items()})
json.dump(doc, open(OUT + "set.json", "w"), indent=1)
print(json.dumps({k: doc[k] for k in ("shown", "hidden_text_pop", "n_units", "reused", "new_units", "planned_calls", "files")}))
