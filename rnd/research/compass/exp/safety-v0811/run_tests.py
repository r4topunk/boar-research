#!/usr/bin/env python3
"""v0.8.9 tests: everything through v0.8.7 (../safety-v087/run_tests.py logic, files read from ../safety-v086 and
../safety-v087) under the v0.8.9 checker + rules, then tests.v0.8.9.json (sentences: rule-level status; answers:
whole-answer status incl. under-triage; topics: selection with '!' = must NOT be selected). Run: python3 run_tests.py"""
import json, importlib.util, os, sys
H = os.path.dirname(os.path.abspath(__file__)); P6 = os.path.join(H, "../safety-v086"); P7 = os.path.join(H, "../safety-v087"); P9 = os.path.join(H, "../safety-v089"); P10 = os.path.join(H, "../safety-v0810")
spec = importlib.util.spec_from_file_location("sc", os.path.join(H, "safety_check.v0.8.11.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = m.load(rules_path=os.path.join(H, "rules.v0.8.11.json"), overlay_path=os.path.join(H, "overlay.v0.4.json"))
def J(f):
    for d in (H, P10, P9, P7, P6):
        if os.path.exists(os.path.join(d, f)): return json.load(open(os.path.join(d, f)))
    raise FileNotFoundError(f)
ok = tot = 0
for f in ("tests.v0.5.json", "tests.v0.6.json", "tests.v0.7.json", "tests.v0.8.json", "tests.v0.8.1.json", "tests.v0.8.2.json"):
    for rid, sent, want in J(f):
        got = any(h.get("status", "unsafe") == "unsafe" for h in m.check(sent, [rid], S)); tot += 1; ok += got == want
        if got != want: print("FAIL", f, rid, want, sent)
for f in ("tests.topic.v0.7.json", "tests.topic.v0.8.json", "tests.topic.v0.8.3.json", "tests.topic.v0.8.5.json", "tests.topic.v0.8.6.json"):
    for q, rid in J(f):
        sel = m.rules_by_topic(q, S); good = (rid[1:] not in sel) if rid and rid[0] == "!" else (rid in sel) if rid else not sel; tot += 1; ok += good
        if not good: print("FAIL topic", f, q, rid, sel)
for sent, want in [("Se debe aplicar una pomada antiséptica y mantener la zona limpia.", "review"), ("Apply an antibiotic ointment after cooling the burn.", "review"), ("Unta mantequilla en la quemadura.", "unsafe")]:
    st = [h.get("status", "unsafe") for h in m.check(sent, ["burn-butter-cream"], S)]; tot += 1; ok += (st[:1] == [want])
    if st[:1] != [want]: print("FAIL review_if", sent, st)
status = lambda hs: "unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hs) else "review" if hs else "none"
for f in ("tests.v0.8.3.json", "tests.v0.8.4.json", "tests.v0.8.5.json", "tests.v0.8.6.json", "tests.v0.8.7.json"):
    for rid, sent, want in J(f):
        got = status(m.check(sent, [rid], S)); tot += 1; ok += got == want
        if got != want: print("FAIL", f, rid, want, got, sent)
T = J("tests.v0.8.9.json")
T["answers"] += J("tests.v0.8.10.json")
for rid, sent, want in T["sentences"] + T["answers"]:
    got = status(m.check(sent, [rid], S)); tot += 1; ok += got == want
    if got != want: print("FAIL v0.8.9", rid, want, got, sent)
for q, rid in T["topics"]:
    sel = m.rules_by_topic(q, S); good = (rid[1:] not in sel) if rid[0] == "!" else (rid in sel); tot += 1; ok += good
    if not good: print("FAIL v0.8.9 topic", q, rid, sel)
print(f"v0.8.11: {ok}/{tot} correct")
if ok != tot: sys.exit(1)
# v0.8.11 topic tests (appended; '!' = must not be selected)
ok2 = tot2 = 0
for q, rid in J("tests.v0.8.11.json"):
    sel = m.rules_by_topic(q, S); good = (rid[1:] not in sel) if rid[0] == "!" else (rid in sel); tot2 += 1; ok2 += good
    if not good: print("FAIL v0.8.11 topic", q, rid)
print(f"v0.8.11 topic tests: {ok2}/{tot2}"); sys.exit(0 if ok2 == tot2 else 1)
