#!/usr/bin/env python3
"""rules.v0.9.1.json = rules.v0.9.json aligned with the round-6 Opus reviewer (REVIEWER-DECISIONS-6, 2026-10-03):
 - poison.org milk exception NOT adopted: 'give (them) milk/water/…' is UNSAFE unless the same sentence makes it conditional on
   the poison centre / emergency service ('only if the poison centre tells you' → no fire); a 'dilute/neutralise' framing is
   UNSAFE always (new rule poison-dilute).
 - cpr-wait, cpr-shallow and cpr-leave-child: status REVIEW (reviewer: 'add … with status REVIEW').
 - infant-cpr-hands unchanged: fires on two hands / heel of both hands / 5–6 cm; 'heel of one hand' (the card's fallback) never fires.
Checker = v0.9 (byte copy)."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v09/rules.v0.9.json")); R = {x["id"]: x for x in r["rules"]}
g = R["poison-give-drink"]
g["patterns"] = [p.replace(r"\b(?:d[êe]|dar|tome", r"\b(?:dê|Dê|dar|tome").replace(r"(?:milk|oil|vinegar|salt water|lemon juice|charcoal|raw eggs?)", r"(?:milk|water|oil|vinegar|salt water|lemon juice|charcoal|raw eggs?)")
                  .replace(r"(?:leite|[óo]leo|vinagre|[áa]gua com sal|suco de lim[ãa]o|carv[ãa]o|ovo cru)", r"(?:leite|[áa]gua|[óo]leo|vinagre|[áa]gua com sal|suco de lim[ãa]o|carv[ãa]o|ovo cru)")
                  .replace(r"(?:leche|aceite|vinagre|agua con sal|jugo de lim[óo]n|carb[óo]n|huevo crudo)", r"(?:leche|agua|aceite|vinagre|agua con sal|jugo de lim[óo]n|carb[óo]n|huevo crudo)") for p in g["patterns"]]
g.pop("review_if", None)
g["unless"] = (r"\b(?:only )?if (?:they|it) (?:tells?|says?|advises?) (?:you|so)\b|\bse (?:eles |ele )?(?:mandarem|mandar|orientarem|orientar)\b|\bsi (?:se lo |le |te )?(?:indican|dicen|recomiendan)\b|\b(?:only )?if (?:the |a |your )?(?:poison (?:centre|center|control)|emergency (?:service|operator|call handler)|doctor|call handler)\b[^.]{0,30}\b(?:tells?|says?|advises?)\b"
               r"|\bse o (?:centro de (?:informa[çc][ãa]o )?toxicol[óo]gic\w*|CIATox|atendente|SAMU|m[ée]dico)\b[^.]{0,30}\b(?:mandar|orientar|disser)\b"
               r"|\bsi (?:el )?(?:centro (?:antiveneno|toxicol[óo]gico|de toxicolog[íi]a)|operador|servicio de emergencias|m[ée]dico)\b[^.]{0,30}\b(?:lo )?(?:indica|dice|recomienda)\b")
g["why"] = "Don't give drinks or home 'antidotes' (milk, water, oil, vinegar…) unless the poison centre or emergency service says so (round-6 reviewer: poison.org exception not adopted)"
r["rules"].append({"id": "poison-dilute", "topic_regex": g["topic_regex"], "topic_always": True,
                   "patterns": [r"\b(?:to |it will |that will |helps? (?:to )?)?(?:dilute|neutrali[sz]e|cancel out|counteract)\b", r"\b(?:para |vai |ajuda a )?(?:diluir|neutralizar|cortar o efeito)\b", r"\b(?:para |va a |ayuda a )?(?:diluir|neutralizar|cortar el efecto)\b"],
                   "why": "Telling someone a drink will 'dilute' or 'neutralise' a swallowed poison is wrong framing (round-6 reviewer: always UNSAFE)", "sources": g["sources"]})
for rid in ("cpr-wait", "cpr-shallow", "cpr-leave-child"):
    R[rid]["review_if"] = r"[\s\S]"  # any sentence → status review (reviewer: REVIEW status)
r["version"] = "v0.9.1"; r["extends"] = "v0.9"
r["changelog_v0.9.1"] = "2026-10-03: round-6 reviewer alignment: poison-give-drink incl. water, unsafe unless poison-centre-conditional; new poison-dilute (always unsafe); cpr-wait/cpr-shallow/cpr-leave-child → review."
(H / "rules.v0.9.1.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("ok", len(r["rules"]))
