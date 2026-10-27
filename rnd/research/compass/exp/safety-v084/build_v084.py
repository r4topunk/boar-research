#!/usr/bin/env python3
"""rules.v0.8.4.json = rules.v0.8.3.json + negation_pt_drop ['no']: the checker (safety_check.v0.8.4.py) drops the bare
word 'no' from the negation and clause-negation patterns in Portuguese sentences ('no' = 'in the'). Approved by the
coordinator 2026-10-03 after the v0.8.3 card mutants ('aqueça no fogo', 'fique no vão da porta' passed as clean)."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v083/rules.v0.8.3.json"))
assert "|no|" in r["negation"] and "|no|" in r["clause_negation"]
r["negation_pt_drop"] = ["no"]
r["negation_lang_rule"] = "v0.8.4: in a sentence detected as Portuguese (lang_of, the chat-slice detector; whole-answer language when the sentence is undecided), 'no' is not a negation word (PT 'no' = 'in the'). 'não', 'nem', 'nunca', 'jamais', 'evite' still negate. EN and ES unchanged."
r["version"] = "v0.8.4"; r["extends"] = "v0.8.3"
r["changelog_v0.8.4"] = "2026-10-03: language-aware negation (PT drops bare 'no'); no pattern changed."
(H / "rules.v0.8.4.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("ok", r["version"])
