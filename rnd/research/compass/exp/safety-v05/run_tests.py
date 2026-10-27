#!/usr/bin/env python3
"""Unit tests for safety rules v0.5 vs v0.4. A test sentence "hits" when the checker returns at least one hit with
status "unsafe" (v0.5 adds status "review" for warning sentences; those are NOT counted as unsafe until adjudicated).
v0.4 hits have no status field and all count. Run from this directory: python3 run_tests.py"""
import json, importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def load(mod, rules):
    spec = importlib.util.spec_from_file_location("sc_" + mod.replace(".", "_"), os.path.join(HERE, mod))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m, m.load(rules_path=os.path.join(HERE, rules), overlay_path=os.path.join(HERE, "overlay.v0.4.json"))
T = json.load(open(os.path.join(HERE, "tests.v0.5.json")))
status = 0
for name, mod, rules in [("v0.4", "safety_check.py", "rules.v0.4.json"), ("v0.5", "safety_check.v0.5.py", "rules.v0.5.json")]:
    m, S = load(mod, rules); ok = 0; fails = []
    for rid, sent, want in T:
        hits = m.check(sent, [rid], S)
        got = any(h.get("status", "unsafe") == "unsafe" for h in hits)
        ok += got == want
        if got != want: fails.append((rid, want, [h.get("status", "unsafe") for h in hits], sent[:70]))
    print(f"{name}: {ok}/{len(T)} correct"); [print("   FAIL", f) for f in fails]
    if name == "v0.5" and ok != len(T): status = 1
sys.exit(status)
