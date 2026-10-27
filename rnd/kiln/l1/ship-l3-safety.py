#!/usr/bin/env python3
"""Ship L3 safety on the 10 v0.2 danger items. PRIMARY = addendum 04 (frozen): safety v0.7 (boar-eval scorers/vendor/safety, rules.v0.7)
+ overlay.v02-danger.v0.7.json explicit map; raw hits -> coordinator blind adjudication (as E3). SECONDARY = Compass v0.9.1 (rules.v0.9.1,
rules_for_v085 = the same explicit map + topic_always extras). E3 main reported beside. Prints ids, rule ids, statuses only (no text)."""
import importlib.util, json, sys
from pathlib import Path
B = Path("<workspace>"); V2 = B / "blind/bench-v02/live/v0.2"
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
sc7 = mod(B / "boar-eval/scorers/vendor/safety/safety_check.py", "sc7")
S7 = sc7.load(rules_path=B / "boar-eval/scorers/vendor/safety/rules.v0.7.json", overlay_path=B / "boar-eval/scorers/vendor/safety/overlay.v0.4.json")
MAP = json.load(open(V2 / "plan/overlay.v02-danger.v0.7.json"))["map"]
D91 = B / "rnd/research/compass/exp/safety-v091"; sc91 = mod(D91 / "safety_check.v0.9.1.py", "sc91")
S91 = sc91.load(rules_path=D91 / "rules.v0.9.1.json", overlay_path=D91 / "overlay.v0.4.json")
Q = {json.loads(l)["id"]: json.loads(l) for l in open(V2 / "questions.v02-new.jsonl")}
runs = {"ship-s42": B / "blind/bench-v02/runs-ship/ship-v02-s42.traces.jsonl", "ship-s43": B / "blind/bench-v02/runs-ship/ship-v02-s43.traces.jsonl",
        "e3-s42": B / "blind/bench-v02/runs-e3/e3-main-s42.traces.jsonl", "e3-s43": B / "blind/bench-v02/runs-e3/e3-main-s43.traces.jsonl"}
out = {}
for name, f in runs.items():
    T = {json.loads(l)["itemId"]: json.loads(l) for l in open(f)}
    r7, r91 = {}, {}
    for i, rids in MAP.items():
        a = T[i]["answer"]["text"]
        h7 = sc7.check(a, rids, S7)
        if h7: r7[i] = sorted({h["rule"] for h in h7})
        q = dict(Q[i]); q["safety_rules"] = rids
        h91 = sc91.check(a, sc91.rules_for_v085(q, S91), S91)
        st = [(h["rule"], h.get("status", "unsafe")) for h in h91]
        if st: r91[i] = sorted(set(st))
    out[name] = {"v07_raw_hits": r7, "v091": r91}
    u91 = sorted(i for i, s in r91.items() if any(x[1] == "unsafe" for x in s)); rv91 = sorted(i for i, s in r91.items() if i not in u91)
    print(f"{name}: v0.7 raw hits {len(r7)} {r7} | v0.9.1 unsafe {len(u91)} {u91} review {len(rv91)} {rv91}")
json.dump(out, open(B / "blind/bench-v02/runs-ship/ship-safety.json", "w"), indent=1)
