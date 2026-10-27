#!/usr/bin/env python3
"""PIN2-SCREEN judge plan (0 LLM): divergent ids per unit (byte-identical texts = tie, 0 calls) + the h2h bench (questions + base t27 texts as refs). -> judge/{v01,cooking,h2h}.ids, judge/h2h-bench/, judge/plan.json"""
import json, os
D = "<workspace>/rnd/research/coordinator/arms/coverage-map/pin2"; J = D + "/judge"
ld = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
T = {(a, s): ld(f"{D}/traces/pin2screen-{a}-{s}-s42.traces.jsonl") for a in ("base", "pin2") for s in ("main", "t27")}
for k, v in T.items(): assert len(v) == (5 if k[1] == "main" else 2), k
for v in T.values():
    for t in v.values(): assert not t.get("error") and (t["answer"]["text"] or "").strip(), t["itemId"]
div = {s: [i for i in T[("base", s)] if T[("base", s)][i]["answer"]["text"] != T[("pin2", s)][i]["answer"]["text"]] for s in ("main", "t27")}
v01 = [i for i in div["main"] if not i.startswith("st-")]; ck = [i for i in div["main"] if i.startswith("st-qa-cooking-se-")]; h2h = div["t27"]
os.makedirs(J + "/h2h-bench/refs", exist_ok=True)
for n, x in (("v01", v01), ("cooking", ck), ("h2h", h2h)): open(f"{J}/{n}.ids", "w").write("".join(i + "\n" for i in x))
q = [json.loads(l) for l in open("<workspace>/rnd/research/coordinator/arms/topics27/in/t27-succinct-s42.requests.jsonl")]
q = {r["item"]["id"]: r["item"]["question"] for r in q}
open(J + "/h2h-bench/questions.jsonl", "w").write("".join(json.dumps(dict(id=i, question=q[i], lang="en"), ensure_ascii=False) + "\n" for i in ("b15", "b18")))
open(J + "/h2h-bench/refs/refs.jsonl", "w").write("".join(json.dumps(dict(id=i, question=q[i], ok=True, answer=T[("base", "t27")][i]["answer"]["text"]), ensure_ascii=False) + "\n" for i in ("b15", "b18")))
json.dump(dict(bench="pin2-screen-h2h", questions="questions.jsonl", refs="refs/refs.jsonl", _note="PIN2-SCREEN head-to-head: refs = SEFIX-124 base answers (bench engine, 1.7B succinct s42), not a reference answer"), open(J + "/h2h-bench/bench.json", "w"), indent=1)
plan = dict(divergent=div, identical=[i for s in div for i in T[("base", s)] if i not in div[s]], calls=2 * 2 * (len(v01) + len(ck)) + 2 * len(h2h))
json.dump(plan, open(J + "/plan.json", "w"), indent=1); print(json.dumps(plan)); assert plan["calls"] <= 60
