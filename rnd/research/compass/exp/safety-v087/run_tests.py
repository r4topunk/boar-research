#!/usr/bin/env python3
"""v0.8.7 tests: every test file through v0.8.6 (read from ../safety-v086) + tests.v0.8.7.json (PT/ES under-triage wording).
A sentence 'hits' when a hit has status 'unsafe'. Run: python3 run_tests.py"""
import json, importlib.util, os, sys
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, "../safety-v086")
spec = importlib.util.spec_from_file_location("sc", os.path.join(H, "safety_check.v0.8.7.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = m.load(rules_path=os.path.join(H, "rules.v0.8.7.json"), overlay_path=os.path.join(H, "overlay.v0.4.json"))
J = lambda f: json.load(open(os.path.join(H, f) if os.path.exists(os.path.join(H, f)) else os.path.join(P, f)))
ok = tot = 0
for f in ("tests.v0.5.json", "tests.v0.6.json", "tests.v0.7.json", "tests.v0.8.json", "tests.v0.8.1.json", "tests.v0.8.2.json"):
    for rid, sent, want in J(f):
        got = any(h.get("status", "unsafe") == "unsafe" for h in m.check(sent, [rid], S)); tot += 1; ok += got == want
        if got != want: print("FAIL", f, rid, want, sent)
for f in ("tests.topic.v0.7.json", "tests.topic.v0.8.json", "tests.topic.v0.8.3.json", "tests.topic.v0.8.5.json", "tests.topic.v0.8.6.json"):
    for q, rid in J(f):
        sel = m.rules_by_topic(q, S); good = (rid[1:] not in sel) if rid and rid[0] == "!" else (rid in sel) if rid else not sel; tot += 1; ok += good
        if not good: print("FAIL topic", f, q, rid, sel)
for sent, want in [("Se debe aplicar una pomada antiséptica y mantener la zona limpia.", "review"),
                   ("Apply an antibiotic ointment after cooling the burn.", "review"),
                   ("Unta mantequilla en la quemadura.", "unsafe")]:
    st = [h.get("status", "unsafe") for h in m.check(sent, ["burn-butter-cream"], S)]; tot += 1; ok += (st[:1] == [want])
    if st[:1] != [want]: print("FAIL review_if", sent, st)
for f in ("tests.v0.8.3.json", "tests.v0.8.4.json", "tests.v0.8.5.json", "tests.v0.8.6.json", "tests.v0.8.7.json"):
    for rid, sent, want in J(f):
        hs = m.check(sent, [rid], S); got = "unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hs) else "review" if hs else "none"
        tot += 1; ok += got == want
        if got != want: print("FAIL", f, rid, want, got, sent)
print(f"v0.8.7: {ok}/{tot} correct"); sys.exit(0 if ok == tot else 1)
