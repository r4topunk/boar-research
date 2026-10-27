#!/usr/bin/env python3
"""MIN3CITE-OPUS prep (0 calls). python3 -I min3cite_opus_prep.py -> ../min3cite-opus-main/in/{set.json,m3c-<unit>.ids}
Arms (existing MAIN 97 K0 seed-42 traces, no generation): ctl = 1.7B lpctl-K0-main-s42 (control), m3c = MIN3CITE stage 2
(arms/min3cite/traces/min3cite-K0-main-s42.traces.jsonl); report-only: v4b = Qwen3-4B VS4B (gemma4-e2b-vs4b), never judged in this pass.
Unit = unique (item id, answer text). Reuse = every existing Opus judge.v1 row pair on the identical unit and frame (cv5_opus_pool.py).
New units are judged on the m3c traces only (ctl must be fully reused, asserted). Cap 150 new calls (2 per unit)."""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP, cv5_per100_common as PC
A = "<workspace>/rnd/research/coordinator/arms"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/min3cite-opus-main/in/"
CAP = 150
TRF = {"ctl": f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl",
       "m3c": f"{A}/min3cite/traces/min3cite-K0-main-s42.traces.jsonl",
       "v4b": f"{A}/gemma4-e2b-vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl"}
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
cov = {a: sum(CP.key(i, TX[a][i]) in P for i in ids) for a in TRF}
assert cov["ctl"] == 97, cov
files = collections.defaultdict(list); units = {}
for i in ids:
    k = CP.key(i, TX["m3c"][i]); units[k] = {"id": i, "reuse": P[k]["src"] if k in P else None, "same_as_ctl": TX["m3c"][i] == TX["ctl"][i]}
    if not units[k]["reuse"]: files[f'm3c-{PC.bench_of(i)[0]}'].append(i)
nn = sum(len(v) for v in files.values()); assert 2 * nn <= CAP, nn
for f in os.listdir(OUT):
    if f.endswith(".ids"): os.remove(OUT + f)
for f, xs in files.items(): open(OUT + f"{f}.ids", "w").write("".join(i + "\n" for i in xs))
src = collections.Counter(os.path.relpath(u["reuse"], A + "/..") for u in units.values() if u["reuse"])
doc = dict(traces=TRF, frames=FR, n_ids=97, units=units, opus_coverage_existing=cov, reused_m3c=97 - nn, new_units=nn, planned_calls=2 * nn,
           cap=CAP, files={k: len(v) for k, v in files.items()}, reuse_sources=dict(src))
json.dump(doc, open(OUT + "set.json", "w"), indent=1)
print(json.dumps({k: doc[k] for k in ("opus_coverage_existing", "reused_m3c", "new_units", "planned_calls", "files", "reuse_sources")}, indent=1))
