#!/usr/bin/env python3
"""rules.v0.8.2.json = rules.v0.8.1.json + (1) new rule altitude-fast-ascent (EN/PT/ES, topic-selected like
altitude-push-on; trigger: chat-slice v1-038 'Evita el mal de altura acelerando tu ascenso'); explanatory sentences
('ascending too quickly causes AMS') are exempt via unless; 'Evita el mal de altura acelerando…' keeps its hit via benign_negation (the negation is on the illness); (2) burn-butter-cream review_if antiseptic/antibiotic
ointment: borderline (NHS: no creams; Mayo: antibiotic ointment on minor burns after cooling), flagged as review,
never unsafe (coordinator 2026-10-03 on v1-056). Checker: safety_check.v0.8.2.py (adds review_if)."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v081/rules.v0.8.1.json")); R = {x["id"]: x for x in r["rules"]}
push = R["altitude-push-on"]
r["rules"].append({
    "id": "altitude-fast-ascent",
    "topic": "altitude sickness prevention / acclimatization",
    "topic_regex": push["topic_regex"],
    "patterns": [
        r"\b(?:ascend\w*|climb\w*|go(?:ing)?\s+up|gain\w*\s+altitude)\b[^.]{0,20}\b(?:quickly|fast|rapidly|faster|as\s+soon\s+as\s+possible)\b",
        r"\b(?:speed\w*\s+up|accelerat\w*|rush\w*|hurry\w*)\b[^.]{0,20}\b(?:the\s+|your\s+)?(?:ascent|climb)\b",
        r"\b(?:quick|fast|rapid|faster)\s+(?:ascent|climb)\b",
        r"\b(?:aceler\w*|apresur\w*|apur\w*)\b[^.]{0,20}\b(?:el\s+|tu\s+|su\s+)?(?:ascenso|subida)\b",
        r"\b(?:sub\w*|ascend\w*)\b[^.]{0,20}\b(?:r[áa]pid\w*|deprisa)\b|\b(?:ascenso|subida)\s+r[áa]pid[oa]\b",
        r"\b(?:aceler\w*|apress\w*)\b[^.]{0,20}\b(?:a\s+|sua\s+)?(?:subida|ascens[ãa]o)\b",
        r"\bsub\w*\b[^.]{0,20}\b(?:depressa|rapidamente|r[áa]pido)\b|\bsubida\s+r[áa]pida\b",
    ],
    "unless": r"\b(?:too|demasiad\w*|muito|excessiv\w*|caus\w*|because|due\s+to|debido|devido|por\s+culpa|risk\w*|riesgo|risco|leads?\s+to|provoca\w*)\b",
    "benign_negation": r"\b(?:evit\w*|avoid\w*|prevent\w*|previen\w*|previn\w*)\s+(?:el\s+|o\s+|la\s+|a\s+)?(?:mal\s+de\s+(?:altura|monta[ñn]a)|altitude\s+sickness|mountain\s+sickness|mal\s+da\s+montanha|soroche|\bams\b|it)\b",
    "why": "Gain altitude gradually; ascending fast is the main cause of altitude sickness",
    "sources": [{"cite": "same sources as altitude-push-on / altitude-ascend (Compass first-aid verification 2026-10-02)"}],
    "type": "forbid",
})
R["burn-butter-cream"]["review_if"] = r"\b(?:antis[eé]ptic\w*|antibi[oó]tic\w*|antibacterial\w*)\b"
r["version"] = "v0.8.2"; r["extends"] = "v0.8.1"
r["review_if_rule"] = "v0.8.2: a rule may carry 'review_if'; a hit whose sentence matches it is status=review (flagged for a person), never unsafe."
r["changelog_v0.8.2"] = "2026-10-03 (coordinator-approved): + altitude-fast-ascent (EN/PT/ES, topic-selected, explanatory 'too fast causes' exempt); burn-butter-cream antiseptic/antibiotic ointment → review (v1-056)."
(H / "rules.v0.8.2.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("rules", len(r["rules"]), "patterns", sum(len(x.get("patterns", [])) for x in r["rules"]))
