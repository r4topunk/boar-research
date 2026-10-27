#!/usr/bin/env python3
"""LITE5 fact-in-context (0 LLM), precheck_x2b.py's rule on selftest20: present = a fact chunk kept under S (headpass-st/runs-x2/split-x2b.jsonl S_present,
= LITE3's replay rule) OR an oracle fact chunk of the item's own pack among the appended ids (headpass:add: / headpass:dense:add: codes) of the given traces.
Usage: fic.py <traces.jsonl> [--out f.json]   Prints counts + per-item; also LITE3's OFF flag for comparison."""
import json, re, sys
A = "<workspace>/rnd/research/coordinator/arms"
FACTS = json.load(open(f"{A}/oracle-st/tools/oracle-facts.json")); CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
split = {d["id"]: d for d in map(json.loads, open(f"{A}/headpass-st/runs-x2/split-x2b.jsonl"))}
l3 = {r["id"]: r["fact_in_context"] for r in json.load(open(f"{A}/lite3/aggregates/lite3.json"))["slices"]["st20"]["items"]}
ids = [l.strip() for l in open(f"{A}/lite2/selftest20.ids") if l.strip()]
T = {(t := json.loads(l))["itemId"]: t for l in open(sys.argv[1]) if l.strip()}
rows = {}
for i in ids:
    p = FACTS[i]["pack"]; cs = T[i]["route"]["reasonCodes"]
    app = [x.split(":add:")[1] for x in cs if x.startswith(("headpass:add:", "headpass:dense:add:"))]
    fc = {int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]}
    own = {int(m.group(2)) for x in app for m in [CID.match(x)] if m and m.group(1) == p}
    rows[i] = {"off": split[i]["S_present"], "lite3_off": l3[i], "appended_fact": bool(fc & own), "on": split[i]["S_present"] or bool(fc & own),
               "n_appended": len(app), "budget_dropped": sum(x.startswith("headpass:budget:dropped:") for x in cs)}
out = {"n": len(ids), "off_present": sum(r["off"] for r in rows.values()), "lite3_off_present": sum(r["lite3_off"] for r in rows.values()),
       "off_agrees_lite3": sum(r["off"] == r["lite3_off"] for r in rows.values()), "on_present": sum(r["on"] for r in rows.values()),
       "newly_present": sorted(i for i, r in rows.items() if r["on"] and not r["off"]), "fired": sum(r["n_appended"] > 0 for r in rows.values()),
       "appended_chunks": sum(r["n_appended"] for r in rows.values()), "items": rows}
print(json.dumps({k: v for k, v in out.items() if k != "items"}))
if "--out" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
