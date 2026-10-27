#!/usr/bin/env python3
"""GEMMA-OPUS-MAIN prep (0 calls). python3 -I gemma_opus_prep.py -> ../gemma-opus-main/in/{set.json,<pair>-<arm>-<unit>.ids}
Arms (existing MAIN 97 K0 traces, no generation): s42 pair = 1.7B lpctl-K0-main-s42 (control) vs Gemma 4 E2B stage-2 eng K0 s42;
s43 pair = gemma4-e2b-confirm c43 (1.7B) vs g43 (Gemma). Unit = unique (item id, answer text); judge.mjs sees only question, reference and answer
text, so identical text across arms/seeds is judged once. Reuse = every existing Opus judge.v1 row pair on the identical unit and frame
(cv5_opus_pool.py: ok, both orders, seed 7, the unit's refs/questions sha). New units are judged on the first arm trace carrying them
(order ctl42, gem42, ctl43, gem43). Priority: s42 units first; s43 units only if 2 x (new s42 + new s43) <= cap 400 in full."""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP, cv5_per100_common as PC
A = "<workspace>/rnd/research/coordinator/arms"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/gemma-opus-main/in/"
CAP = 400
TRF = {"ctl42": f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl",
       "gem42": f"{A}/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl",
       "ctl43": f"{A}/gemma4-e2b-confirm/runs/c43/traces/gemma4-e2b-confirm-c43-K0-main-s42.traces.jsonl",
       "gem43": f"{A}/gemma4-e2b-confirm/runs/g43/traces/gemma4-e2b-confirm-g43-K0-main-s42.traces.jsonl"}
ids = [x for x in open(f"{A}/lp-screens/main-97.ids").read().split() if x]; assert len(ids) == 97
TX = {}
for a, f in TRF.items():
    T = {(j := json.loads(l)).get("itemId") or j.get("queryId"): j for l in open(f) if l.strip()}
    assert set(ids) <= set(T), a; assert not any(T[i].get("error") for i in ids), a
    TX[a] = {i: T[i]["answer"]["text"] for i in ids}
FR = {}
for u in ("v01", "qa-cooking-se", "qa-money-se"):
    r = json.loads(open(f"{A}/lp-screens/control/judgments/lpctl-K0-main-s42-{u}.judgments.jsonl").readline()); FR[u] = (r["refsSha256"], r["questionsSha256"])
P = {}
for u, (fr, fq) in FR.items(): P.update(CP.pool(fr, fq, exclude_prefix=os.path.dirname(OUT.rstrip("/"))))
units = {}
for a in ("ctl42", "gem42", "ctl43", "gem43"):
    for i in ids:
        k = CP.key(i, TX[a][i]); u = units.setdefault(k, {"id": i, "arms": [], "judge_on": a}); u["arms"].append(a)
for k, u in units.items(): u["reuse"] = P[k]["src"] if k in P else None
pair_of = lambda a: "s42" if a.endswith("42") else "s43"
new = collections.Counter(pair_of(u["judge_on"]) for u in units.values() if not u["reuse"])
do43 = 2 * (new["s42"] + new["s43"]) <= CAP
assert 2 * new["s42"] <= CAP, new
files = collections.defaultdict(list)
for k, u in units.items():
    if u["reuse"] or (pair_of(u["judge_on"]) == "s43" and not do43): continue
    files[f'{u["judge_on"]}-{PC.bench_of(u["id"])[0]}'].append(u["id"])
for f in os.listdir(OUT):
    if f.endswith(".ids"): os.remove(OUT + f)
for f, xs in files.items():
    assert len(xs) == len(set(xs)); open(OUT + f"{f}.ids", "w").write("".join(i + "\n" for i in xs))
src = collections.Counter(os.path.relpath(u["reuse"], A + "/..") for u in units.values() if u["reuse"])
nn = sum(len(v) for v in files.values())
doc = dict(traces=TRF, frames=FR, n_ids=97, units=units, n_units=len(units), reused=sum(1 for u in units.values() if u["reuse"]),
           new_units_by_pair=dict(new), do_s43=do43, new_units=nn, planned_calls=2 * nn, cap=CAP, files={k: len(v) for k, v in files.items()}, reuse_sources=dict(src))
json.dump(doc, open(OUT + "set.json", "w"), indent=1)
print(json.dumps({k: doc[k] for k in ("n_units", "reused", "new_units_by_pair", "do_s43", "new_units", "planned_calls", "files", "reuse_sources")}, indent=1))
