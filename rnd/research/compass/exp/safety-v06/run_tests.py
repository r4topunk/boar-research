#!/usr/bin/env python3
"""v0.6 tests: (1) the 27 v0.5 sentence tests still pass under v0.6; (2) per-new-rule unsafe/negated pairs; (3) topic selection.
A sentence 'hits' when a hit has status 'unsafe' (review is not counted). Run: python3 run_tests.py"""
import json, importlib.util, os, sys
H = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sc6", os.path.join(H, "safety_check.v0.6.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = m.load(rules_path=os.path.join(H, "rules.v0.6.json"), overlay_path=os.path.join(H, "overlay.v0.4.json"))
ok = tot = 0
for f in ("tests.v0.5.json", "tests.v0.6.json"):
    for rid, sent, want in json.load(open(os.path.join(H, f))):
        got = any(h.get("status", "unsafe") == "unsafe" for h in m.check(sent, [rid], S)); tot += 1; ok += got == want
        if got != want: print("FAIL", f, rid, want, sent)
for q, rid in json.load(open(os.path.join(H, "tests.topic.v0.6.json"))):
    sel = m.rules_by_topic(q, S); good = (rid in sel) if rid else not sel; tot += 1; ok += good
    if not good: print("FAIL topic", q, rid, sel)
print(f"v0.6: {ok}/{tot} correct"); sys.exit(0 if ok == tot else 1)
