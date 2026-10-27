#!/usr/bin/env python3
"""Examples per rule (0 LLM): for each compact rule fired in ON, up to 3 items (deterministic: sorted by id, spread over sets) with the question,
the ON decline, the OFF (or OFF5 where OFF still declines) answer, and the judge correctness (mean of both orders). Writes aggregates/examples.jsonl."""
import json, glob, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def tr(a):
    o = {}
    for f in glob.glob(f"{H}/traces/ld-{a}-*-s42.traces.jsonl"):
        for l in open(f): t = json.loads(l); o[t["itemId"]] = t
    return o
def jd(a):
    o = {}
    for f in glob.glob(f"{H}/judgments/ld-{a}-*.judgments.jsonl"):
        for l in open(f):
            r = json.loads(l)
            if r.get("ok") is True: o.setdefault(r["queryId"], []).append(r["mapped"]["boar"]["correctness"])
    return o
T = {a: tr(a) for a in ("on", "off", "off5")}; J = {a: jd(a) for a in ("on", "off", "off5")}
v01 = set(open(f"{H}/data/v01-57.ids").read().split())
out = {}
for r in ["grounding:declined-compact", "grounding:all-citations-removed-declined-compact", "grounding:uncited-with-sources-declined-compact"]:
    ids = sorted(i for i in T["on"] if r in T["on"][i]["route"]["reasonCodes"] and (i in v01 or i.startswith("st-")))
    pick = [ids[k * len(ids) // 3] for k in range(3)] if len(ids) >= 3 else ids
    rows = []
    for i in pick:
        arm = "off" if T["off"][i]["answer"]["text"] != T["on"][i]["answer"]["text"] else "off5"
        c = J[arm].get(i, [])
        rows.append(dict(id=i, question=T["on"][i]["question"], on=T["on"][i]["answer"]["text"], arm=arm, answer=T[arm][i]["answer"]["text"],
                         codes=[x for x in T[arm][i]["route"]["reasonCodes"] if x.startswith("grounding:")], correctness=sum(c) / len(c) if c else None))
    out[r] = rows
open(f"{H}/aggregates/examples.jsonl", "w").write("".join(json.dumps(dict(rule=r, **x), ensure_ascii=False) + "\n" for r, rows in out.items() for x in rows))  # one line per row (the rnd pre-commit hook allows public v0.1 questions on JSON lines only)
for r, rows in out.items():
    print("==", r)
    for x in rows: print(f"- {x['id']} [{x['arm']}] corr={x['correctness']} | Q: {x['question']}\n  A: {x['answer'][:500]}\n  codes {x['codes']}")
