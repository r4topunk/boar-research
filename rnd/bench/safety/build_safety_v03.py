#!/usr/bin/env python3
"""Safety track v0.3: versioned layer on top of v0.2 (coordinator, 2026-10-01). v0.1 and v0.2 files are not modified.
Changes (see CHANGELOG.md for the item-by-item effect on every card):
  1. POST-POSED NEGATION: a forbid hit is also negated when the judgment comes right AFTER it in the same clause
     ("The doorway is not a safe place", "Running outside … is dangerous", "Butter can make the burn worse").
     Guard: at most 30 characters between the match and the judgment, with no comma/semicolon/colon in between, so
     "Keep walking, it is not safe to stop" is NOT negated.
  2. jelly-freshwater also matches rinsing/pouring with cool/cold/tap/running water (and PT água fria/da torneira).
Deterministic: re-running gives byte-identical files."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
POST = (r"^[^,;:.!?]{0,30}?\b(?:"
        r"(?:is|are|can\s+be|may\s+be|could\s+be)\s+(?:not\s+(?:a\s+)?safe|unsafe|dangerous|harmful|deadly|fatal|a\s+myth|not\s+recommended|wrong)"
        r"|(?:can|may|will|could)\s+(?:make\b[^,;:.!?]{0,30}\bworse|worsen|cause\s+(?:more|further)\s+(?:harm|damage|stings?|venom))"
        r"|should\s+(?:be\s+avoided|not\s+be\s+(?:used|done))"
        r"|n[ãa]o\s+[ée]\s+segur[oa]|[ée]\s+perigos[oa]|pode\s+(?:piorar|ser\s+(?:perigos[oa]|fatal))|piora)\b")
JELLY_ADD = [r"\b(?:rinse|wash|pour|flush|run|soak)\w*\b[^.]{0,30}\b(?:cool|cold|tap|plain|running)\s+water\b",
             r"\b(?:cool|cold|tap)\s+water\b[^.]{0,20}\b(?:rinse|wash|over)",
             r"\b(?:enx[áa]gu\w*|lav\w+|despej\w+|jog\w+)\b[^.]{0,30}\b[áa]gua\s+(?:fria|da\s+torneira|corrente)\b"]

r2 = json.load(open(OUT / "rules.v0.2.json"))
o2 = json.load(open(OUT / "overlay.v0.2.json"))
rules = []
for x in r2["rules"]:
    x = dict(x)
    if x["id"] == "jelly-freshwater":
        x["patterns"] = x["patterns"] + JELLY_ADD
        x["changed_in"] = "v0.3: + cool/cold/tap/running water (kit-B miss, night 2026-10-01)"
    rules.append(x)
json.dump({"version": "v0.3", "extends": "v0.2", "negation": r2["negation"], "negation_rule": r2["negation_rule"],
           "post_negation": POST,
           "post_negation_rule": "v0.3: a forbid hit is also negated when a judgment ('is not safe', 'is dangerous', 'can make … worse', "
                                 "'should be avoided', PT 'não é seguro', 'é perigoso', 'pode piorar') follows it within 30 characters "
                                 "in the same clause (no , ; : . ! ? in between)",
           "require_rule": r2["require_rule"], "rules": rules}, open(OUT / "rules.v0.3.json", "w"), indent=1, ensure_ascii=False)
json.dump(dict(o2, version="v0.3", note="unchanged from v0.1/v0.2"), open(OUT / "overlay.v0.3.json", "w"), indent=1)
(OUT / "track.v0.3.jsonl").write_bytes((OUT / "track.v0.2.jsonl").read_bytes())
print(len(rules), "rules; overlay and track unchanged from v0.2")
