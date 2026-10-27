#!/usr/bin/env python3
"""Mutant check (under-triage rules: call line removed + deferral added, since they fire only without a call line) for every card text (Compass, 2026-10-03, after the Opus reviewer pass): for each card × language, the
rules the checker selects for that card (its own rule list ∪ topic selection on the card's topic) must catch an unsafe
sentence appended to the clean card text. Mutant sentences come from each rule's own unsafe tests (v0.5–v0.8.9 test
files), preferring the card's language. Prints per-card catches and any rule whose mutant is NOT caught on the card.
Run: python3 mutants.py"""
import importlib.util, json, re
from pathlib import Path
H = Path(__file__).resolve().parent; SV = H.parent / "safety-v091"
spec = importlib.util.spec_from_file_location("sc", SV / "safety_check.v0.9.1.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = m.load(rules_path=SV / "rules.v0.9.1.json", overlay_path=SV / "overlay.v0.4.json")
tests = {}
for d, names in ((H.parent / "safety-v086", ["tests.v0.5.json", "tests.v0.6.json", "tests.v0.7.json", "tests.v0.8.json", "tests.v0.8.1.json", "tests.v0.8.2.json",
                                              "tests.v0.8.3.json", "tests.v0.8.4.json", "tests.v0.8.5.json", "tests.v0.8.6.json"]), (H.parent / "safety-v087", ["tests.v0.8.7.json"])):
    for n in names:
        for rid, sent, want in json.load(open(d / n)):
            if want is True or want == "unsafe": tests.setdefault(rid, []).append(sent)
T9 = json.load(open(SV.parent / "safety-v089" / "tests.v0.8.9.json"))
for rid, sent, want in T9["sentences"] + T9["answers"]:
    if want == "unsafe": tests.setdefault(rid, []).append(sent)
D = json.load(open(H / "cards.json"))
caught = missed = 0; misses = []
for c in D["cards"]:
    for lang, L in c["langs"].items():
        text = "\n".join([L["title"]] + [s["text"] for s in L["steps"]] + [L["call"]["text"]])
        rules = sorted(set(c.get("rules", [])) | set(m.rules_by_topic(c["topic"][lang], S)))
        assert not [h for h in m.check(text, rules, S) if h.get("status", "unsafe") == "unsafe"], (c["id"], lang)
        for rid in rules:
            cand = tests.get(rid, [])
            if not cand: continue
            sent = sorted(cand, key=lambda s: 0 if m.lang_of(s) == lang else 1)[0]
            if rid in S.get("undertriage", {}):
                # under-triage fires only when NO call line exists: the mutant drops the card's call line (and any step that
                # carries an emergency call) and adds the deferral sentence.
                U = S["undertriage"][rid]
                body = [x for x in [L["title"]] + [s["text"] for s in L["steps"]] if not U["call"].search(x)]
                mutant = "\n".join(body + [sent])
            else:
                mutant = text + "\n" + sent
            hs = m.check(mutant, rules, S)
            if any(h["rule"] == rid and h.get("status", "unsafe") == "unsafe" for h in hs): caught += 1
            else: missed += 1; misses.append((c["id"], lang, rid, sent[:90]))
print(f"mutants: caught {caught}, missed {missed}")
for x in misses: print("  MISS", x)
