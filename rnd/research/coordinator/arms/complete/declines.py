#!/usr/bin/env python3
"""COMPLETE (Kiln): decline flags per trace with the bench's own detector (lantern precheck.refused on norm(text)).
usage: python3 -I declines.py traces.jsonl  -> {"itemId": true|false}"""
import json, sys
sys.path.insert(0, "<workspace>/boar-eval/scorers/vendor/lantern")
import precheck
out = {}
for l in open(sys.argv[1]):
    if not l.strip(): continue
    t = json.loads(l); row = {"declined": bool(t["answer"]["declined"]), "answer": t["answer"]["text"]}
    out[t["itemId"]] = bool(precheck.refused(row, precheck.norm(row["answer"])))
print(json.dumps(out))
