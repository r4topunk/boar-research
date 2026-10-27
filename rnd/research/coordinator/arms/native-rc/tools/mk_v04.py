#!/usr/bin/env python3
"""NATIVE-RC R3 inputs from the frozen v0.4 items (0 LLM). NEVER prints item text: only counts and shas.
Writes (all under work/v04/, gitignored):
  native-items.jsonl                 {id, turns, context} for the JVM harness 'conv' mode (NATIVE-RC; no location input in the native app)
  engine/<seed>/turn1.requests.jsonl ENGINE-RC adapter requests (config = validation night v2-s ON config: RC kit, RC settings), turn 1 of every item,
                                     item.context {lat, lon} for the 7 location items (the adapter hands it to the engine as the device fix)
  engine/<seed>/turns.template.jsonl later turns (k >= 2) with prevId, filled with history on the mini (stage script)
  bench/questions.jsonl              judge.mjs input: question = the single turn, or the numbered user turns + "Judge the assistant's whole conversation,
                                     all turns." (spec 6.3); rubric = checklist points (no errata exist yet: original notes) + the time-sensitive line /
                                     the location line (spec 6.1)
usage: python3 -I mk_v04.py"""
import json, os, hashlib
B = "<workspace>"; A = B + "/rnd/research/coordinator/arms/native-rc"; W = A + "/work/v04"
ITEMS = B + "/boar-eval/bench/v0.4/items.jsonl"; SHA = "f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594"
b = open(ITEMS, "rb").read(); assert hashlib.sha256(b).hexdigest() == SHA, "items sha mismatch"
its = [json.loads(l) for l in b.decode().splitlines() if l.strip()]
os.makedirs(W + "/bench", exist_ok=True)
with open(W + "/native-items.jsonl", "w") as o:
    for i in its: o.write(json.dumps(dict(id=i["id"], turns=i["turns"], context=i.get("context")), ensure_ascii=False) + "\n")
tmpl = json.loads(open(A + "/../validation-1024/night/jobs/v2-s/req/" + sorted(os.listdir(A + "/../validation-1024/night/jobs/v2-s/req"))[-1]).readline())
for seed in (42, 43):
    d = f"{W}/engine/s{seed}"; os.makedirs(d, exist_ok=True)
    with open(d + "/turn1.requests.jsonl", "w") as o1, open(d + "/turns.template.jsonl", "w") as ot:
        for i in its:
            for k, t in enumerate(i["turns"]):
                r = json.loads(json.dumps(tmpl)); r["config"]["arm"] = "ENGINE-RC+native-rc-v04"; r["seed"] = seed
                r["runId"] = f"nrc-v04-engine-s{seed}-t{k + 1}"
                it = dict(id=i["id"], question=t, lang="en")
                if i.get("context") and i["context"].get("lat") is not None: it["context"] = dict(lat=i["context"]["lat"], lon=i["context"]["lon"])
                if k: it["prevTurn"] = k; ot.write(json.dumps(dict(r, item=it), ensure_ascii=False) + "\n")
                else: r["item"] = it; o1.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(W + "/bench/questions.jsonl", "w") as o:
    for i in its:
        q = i["turns"][0] if len(i["turns"]) == 1 else "\n".join(f"[Turn {k + 1}] {t}" for k, t in enumerate(i["turns"])) + "\n\nJudge the assistant's whole conversation, all turns."
        notes = list(i["checklist"])
        if i["tags"].get("time_sensitive"): notes.append("Time-sensitive points are stated as of 2026-10-20.")
        if i.get("context") and i["context"].get("city"): notes.append(f"The user is in {i['context']['city']} ({i['context']['lat']}, {i['context']['lon']}).")
        o.write(json.dumps(dict(id=i["id"], question=q, rubric=notes, weight=0.5 if i["tags"].get("health_safety") else 1.0,
                                anchor=bool(i["tags"].get("anchor_vexact")), multiTurn=len(i["turns"]) > 1, family=i["family"], type=i["type"]), ensure_ascii=False) + "\n")
n1 = sum(1 for _ in open(f"{W}/engine/s42/turn1.requests.jsonl")); nt = sum(1 for _ in open(f"{W}/engine/s42/turns.template.jsonl"))
print(f"items {len(its)} (multi-turn {sum(len(i['turns']) > 1 for i in its)}, location {sum(bool(i.get('context')) for i in its)}); engine turn1 {n1}, later turns {nt} per seed; "
      f"bench questions sha {hashlib.sha256(open(W + '/bench/questions.jsonl', 'rb').read()).hexdigest()[:12]}")
