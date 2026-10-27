#!/usr/bin/env python3
"""SEFIX-124 sanity + judge plan (0 LLM). python3 -I sanity_124.py -> ans-judge/sanity_124.json, ans-judge/plan.124.json, ans-judge/plan.124.<seed>.<arm>.ids
Arms: ans-traces/sefix124-main-s{42,43} (F1+F2+F4, F3 off) vs the K3 control of the same seed (s42: litepacks mini K1 traces = pool-K1 texts; s43: ans-traces/ctlk1-main-s43) and vs SEFIX-ALL of the same seed.
Sanity: 97/97 rows, 0 errors / empty / loops; deterministic items (control: 0 output tokens or no generate:user-model reason) identical to the control (F3 off => expected identical).
Judge plan (cap Haiku 200 = 100 units x 2 orders): units = (seed, id, arm) whose answer text differs between 124 and the control and has no existing judged row (cache keyed by (id, answer text):
control pool-K1, ARM-G, SEFIX-ALL s42 rows, SEFIX-ALL/control s43 judged rows). Priority (outcome-blind): cooking/money items first, then v0.1 by id; per item all needed units of both seeds together; whole items only."""
import json, glob, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
src_of = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
ctl42 = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): ctl42.update(ld(f))
TR = {42: dict(X=ld(SF + "/ans-traces/sefix124-main-s42.traces.jsonl"), C=ctl42, F=ld(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")),
      43: dict(X=ld(SF + "/ans-traces/sefix124-main-s43.traces.jsonl"), C=ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl"), F=ld(SF + "/ans-traces/sefixall-main-s43.traces.jsonl"))}
rp = {r["id"]: r for r in rd(SF + "/replays/main.F1F2F4.jsonl")}
out = {}
for s, D in TR.items():
    X, C, F = D["X"], D["C"], D["F"]
    r = dict(rows=len(X), missing=[i for i in ids if i not in X], errors=[i for i in ids if i in X and X[i].get("error")],
             empty=[i for i in ids if i in X and not (X[i]["answer"]["text"] or "").strip()], loops=[i for i in ids if i in X and loop(X[i]["answer"]["text"] or "")])
    r["kill"] = bool(r["missing"] or r["errors"] or r["empty"] or r["loops"])
    dets = [i for i in ids if det(C[i])]
    r["det_items_in_control"] = len(dets); r["det_identical_to_control"] = sum(X[i]["answer"]["text"] == C[i]["answer"]["text"] for i in dets)
    r["det_not_identical"] = [i for i in dets if X[i]["answer"]["text"] != C[i]["answer"]["text"]]
    r["det_not_identical_also_diff_vs_ALL"] = [i for i in r["det_not_identical"] if X[i]["answer"]["text"] != F[i]["answer"]["text"]]
    r["det_not_det_in_arm"] = [i for i in dets if not det(X[i])]
    r["text_differs_vs_control"] = sum(X[i]["answer"]["text"] != C[i]["answer"]["text"] for i in ids)
    r["text_identical_to_ALL"] = sum(X[i]["answer"]["text"] == F[i]["answer"]["text"] for i in ids)
    r["text_differs_vs_ALL"] = [i for i in ids if X[i]["answer"]["text"] != F[i]["answer"]["text"]]
    r["kept_identical_to_ALL"] = sum(seq(X[i]) == seq(F[i]) for i in ids)
    r["kept_titles_eq_replay_F1F2F4"] = sum([c["title"] for c in X[i]["retrieval"]["kept"]] == [c["title"] for c in rp[i]["keptFull"]] for i in ids)
    r["fallback_fired"] = [i for i in ids if any("health-fallback" in c for c in X[i]["route"]["reasonCodes"]) or "health-fallback" in json.dumps(X[i].get("grounding", ""))]
    m = lambda f: round(sum(f(X[i]) for i in ids) / len(ids), 2)
    r["mean_out_tok"] = m(lambda t: t["timing"].get("outputTokens") or 0); r["mean_totalMs"] = m(lambda t: t["timing"].get("totalMs") or 0)
    r["ALL_mean_out_tok"] = round(sum(F[i]["timing"].get("outputTokens") or 0 for i in ids) / len(ids), 2)
    out[str(s)] = r
# judge plan
r42 = json.load(open(SF + "/answers-sefixall.json")); r43 = json.load(open(SF + "/answers-sefixall-s43.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
TG = ld(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")
cache = {}
for i in ids:
    cache[(i, pool[i]["text"])] = 1; cache[(i, TG[i]["answer"]["text"])] = 1; cache[(i, TR[42]["F"][i]["answer"]["text"])] = 1
    for arm, nm in (("C", "ctl"), ("F", "ALL")):
        if r43["items"][i][nm]["judgment"] != "proxy": cache[(i, TR[43][arm][i]["answer"]["text"])] = 1
need = {}
for i in ids:
    for s in (42, 43):
        X, C = TR[s]["X"][i]["answer"]["text"], TR[s]["C"][i]["answer"]["text"]
        if X == C: continue
        for arm, txt in (("X", X), ("C", C)):
            if (i, txt) in cache: continue
            if s == 42 and arm == "C": continue   # pool-K1 holds every s42 control row
            need.setdefault(i, []).append((s, arm))
order = sorted(need, key=lambda i: (0 if src_of(i) != "v0.1" else 1, ids.index(i)))
plan, calls = [], 0
for i in order:
    c = 2 * len(set((s, a, TR[s][a][i]["answer"]["text"]) for s, a in need[i]))
    if calls + c <= 200: plan.append(i); calls += c
units = {}
for i in plan:
    seen = set()
    for s, a in need[i]:
        key = (s, a); txt = TR[s][a][i]["answer"]["text"]
        units.setdefault(f"{s}.{a}", []).append(i)
out["plan"] = dict(units_needed=sum(len(v) for v in need.values()), items_needing=len(need), plan_items=len(plan), plan_calls=calls, left_unjudged=[i for i in order if i not in plan],
                   by_unit={k: len(v) for k, v in units.items()})
json.dump(out, open(SF + "/ans-judge/sanity_124.json", "w"), indent=1)
json.dump(dict(plan=plan, need={i: need[i] for i in need}, units=units), open(SF + "/ans-judge/plan.124.json", "w"), indent=1)
for k, v in units.items(): open(SF + f"/ans-judge/plan.124.{k}.ids", "w").write("\n".join(v) + "\n")
print(json.dumps({s: {k: (v if not isinstance(v, list) or len(v) < 10 else f"[{len(v)}]") for k, v in r.items()} for s, r in out.items()}, indent=0))
