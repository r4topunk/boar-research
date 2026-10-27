#!/usr/bin/env python3
"""v0.8.1 tests (+ tests.v0.8.1.json PT pairs): every v0.5–v0.7 sentence and topic test under v0.8, plus the ES sentence pairs (tests.v0.8.json) and the
ES / history topic tests (tests.topic.v0.8.json; a null rule = no rule may be selected; '!rule' = that rule must not be selected). A sentence 'hits' when a hit has
status 'unsafe' (review is not counted). Run: python3 run_tests.py"""
import json, importlib.util, os, sys
H = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sc8", os.path.join(H, "safety_check.v0.8.6.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = m.load(rules_path=os.path.join(H, "rules.v0.8.6.json"), overlay_path=os.path.join(H, "overlay.v0.4.json"))
ok = tot = 0
for f in ("tests.v0.5.json", "tests.v0.6.json", "tests.v0.7.json", "tests.v0.8.json", "tests.v0.8.1.json", "tests.v0.8.2.json"):
    for rid, sent, want in json.load(open(os.path.join(H, f))):
        got = any(h.get("status", "unsafe") == "unsafe" for h in m.check(sent, [rid], S)); tot += 1; ok += got == want
        if got != want: print("FAIL", f, rid, want, sent)
for f in ("tests.topic.v0.7.json", "tests.topic.v0.8.json", "tests.topic.v0.8.3.json", "tests.topic.v0.8.5.json", "tests.topic.v0.8.6.json"):
    for q, rid in json.load(open(os.path.join(H, f))):
        sel = m.rules_by_topic(q, S); good = (rid[1:] not in sel) if rid and rid[0] == "!" else (rid in sel) if rid else not sel; tot += 1; ok += good
        if not good: print("FAIL topic", f, q, rid, sel)
for sent, want in [("Se debe aplicar una pomada antiséptica y mantener la zona limpia.", "review"),
                   ("Apply an antibiotic ointment after cooling the burn.", "review"),
                   ("Unta mantequilla en la quemadura.", "unsafe")]:
    st = [h.get("status", "unsafe") for h in m.check(sent, ["burn-butter-cream"], S)]; tot += 1; ok += (st[:1] == [want])
    if st[:1] != [want]: print("FAIL review_if", sent, st)
for rid, sent, want in json.load(open(os.path.join(H, "tests.v0.8.3.json"))) + json.load(open(os.path.join(H, "tests.v0.8.4.json"))) + json.load(open(os.path.join(H, "tests.v0.8.5.json"))) + json.load(open(os.path.join(H, "tests.v0.8.6.json"))):
    hs = m.check(sent, [rid], S); got = "unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hs) else "review" if hs else "none"
    tot += 1; ok += got == want
    if got != want: print("FAIL v0.8.3", rid, want, got, sent)
print(f"v0.8.6: {ok}/{tot} correct"); sys.exit(0 if ok == tot else 1)
