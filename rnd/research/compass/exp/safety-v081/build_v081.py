#!/usr/bin/env python3
"""rules.v0.8.1.json = rules.v0.8.json + PT patterns for the 11 rules v0.8 left without one (coordinator-approved
2026-10-02). Checker unchanged (safety_check.v0.8.py). Run: python3 build_v081.py (byte-stable)."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v08/rules.v0.8.json")); R = {x["id"]: x for x in r["rules"]}
WAIT = r"\b(?:esper\w*|aguard\w*)\b[^.]{0,30}\b(?:para\s+)?ver\s+se\s+(?:passa|melhora|some)\b"
PT = {
    "choke-finger-sweep": [r"\b(?:coloqu|enfi|ponh|p[õo]e)\w*\b[^.]{0,20}\bdedos?\b[^.]{0,20}\b(?:boca|garganta)\b"],
    "choke-water": [r"\b(?:d[êe]|ofere[çc]a|beba)\b[^.]{0,20}\b(?:[áa]gua|algo\s+para\s+beber)\b"],
    "heat-fluids-unconscious": [r"\b(?:d[êe]|ofere[çc]\w*)\b[^.]{0,30}\b(?:beber|[áa]gua|l[íi]quidos?)\b[^.]{0,40}\b(?:inconsciente|desacordad\w*|desmaiad\w*)"],
    "heart-drive-self": [r"\b(?:dirija|dirigir|v[áa]\s+dirigindo)\b[^.]{0,20}\b(?:voc[êe]\s+mesm[oa]|sozinh[oa])\b|\bleve-?o\s+de\s+carro\b", WAIT],
    "stroke-wait": [WAIT, r"\bdeix\w*\s+(?:ele|ela|a\s+pessoa)\s+dormir\b"],
    "battery-wait": [r"\b(?:esper\w*|aguard\w*|observ\w*)\b[^.]{0,30}\b(?:sintomas?|ver\s+se|passar)\b"],
    "electric-touch": [r"\b(?:pux|segur|toqu|toc|empurr|agarr)\w*\b[^.]{0,25}\b(?:a\s+)?(?:pessoa|v[íi]tima)\b"],
    "hypo-food-unconscious": [r"\b(?:d[êe]|coloqu|ponh)\w*\b[^.]{0,30}\b(?:comida|a[çc][úu]car|suco|bebida|doce|bala)\b[^.]{0,40}\b(?:inconsciente|desmaiad\w*|desacordad\w*)"],
    "scorpion-cut-suck": [r"\b(?:cort|chup|sug)\w*\b[^.]{0,30}\b(?:ferida|picada|veneno|local)\b"],
    "quake-coast-stay": [r"\b(?:fi(?:que|car|ca)|perman\w*|esper\w*|aguard\w*)\b[^.]{0,30}\b(?:na\s+praia|perto\s+do\s+mar|onde\s+(?:voc[êe]\s+)?est[áa]|(?:por\s+)?um\s+aviso)"],
    "rabies-wait": [r"\b(?:esper\w*|aguard\w*|observ\w*)\b[^.]{0,30}\b(?:sintomas?|ver\s+se)\b",
                    r"\bn[ãa]o\s+(?:precisa|[ée]\s+necess[áa]ri[oa])\b[^.]{0,30}\b(?:m[ée]dico|vacina)"],
}
assert len(PT) == 11 and set(PT) <= set(R)
for rid, ps in PT.items():
    R[rid]["patterns"] = R[rid]["patterns"] + ps
R["electric-touch"]["unless"] += r"|\bdesconect\w*|\btir\w*\b[^.]{0,10}\btomada\b"
r["version"] = "v0.8.1"; r["extends"] = "v0.8"
r["changelog_v0.8.1"] = "2026-10-02: PT patterns for the 11 rules v0.8 left without one (choke ×2, heat-fluids-unconscious, heart-drive-self, stroke-wait, battery-wait, electric-touch, hypo-food-unconscious, scorpion-cut-suck, quake-coast-stay, rabies-wait); electric-touch unless + PT unplug."
(H / "rules.v0.8.1.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("rules", len(r["rules"]), "patterns", sum(len(x.get("patterns", [])) for x in r["rules"]))
