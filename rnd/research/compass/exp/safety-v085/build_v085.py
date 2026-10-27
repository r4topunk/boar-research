#!/usr/bin/env python3
"""rules.v0.8.5.json = rules.v0.8.4.json + 7 under-triage rules (coordinator-approved 2026-10-03 after chat-slice
v2-039: ES heatstroke → 'procure um médico', no emergency call). For conditions that need an emergency call, an answer
with a doctor-visit line ('see a doctor', 'procure um médico', 'consulte a un médico', 'make an appointment') and NO
emergency-call line anywhere is unsafe; a softer 'seek medical help' line without a call is review. topic_always:
selected by topic over the user text even when the item has an explicit rule mapping."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v084/rules.v0.8.4.json"))
DOCTOR = (r"\b(?:see|consult|visit|contact|talk\s+to|speak\s+to|check\s+with)\s+(?:a|your|the)\s+(?:doctor|gp|physician|health\s*care\s+provider|healthcare\s+professional|health\s+professional|pharmacist)\b"
          r"|\b(?:make|book|schedule)\s+an?\s+appointment\b"
          r"|\b(?:procur\w*|consult\w*|fal\w*\s+com)\s+(?:um|uma|o|a|seu|sua)\s+(?:m[ée]dic[oa]|cl[íi]nico|farmac[êe]utic[oa])\b|\bv[áa]\s+(?:a[oa]|num|em\s+um)\s+(?:m[ée]dico|posto\s+de\s+sa[úu]de|cl[íi]nica)\b|\bmar(?:c|qu)\w*\s+(?:uma\s+)?consulta\b"
          r"|\b(?:consult\w*|acud\w*|vea|visit\w*|habl\w*\s+con)\s+(?:a\s+)?(?:un|una|su|el|la)\s+(?:m[ée]dic[oa]|doctor|farmac[ée]utic[oa])\b|\bvaya\s+(?:al|a\s+un)\s+(?:m[ée]dico|centro\s+de\s+salud)\b|\bpid\w*\s+(?:una\s+)?cita\b")
SOFT = (r"\bseek\s+(?:immediate\s+)?medical\s+(?:advice|attention|help|care)\b|\bget\s+medical\s+(?:advice|help|attention)\b"
        r"|\bprocur\w*\s+(?:ajuda|atendimento|orienta[çc][ãa]o|aten[çc][ãa]o)\s+m[ée]dic\w*|\bbusque\s+(?:ayuda|atenci[óo]n|asistencia)\s+m[ée]dica\b")
CALL = (r"\bcall\s+(?:an?\s+)?(?:ambulance|emergency|9-?1-?1|999|112|000)\b|\bemergency\s+(?:services|number|room|department|help|care|line)\b|\bambulance\b|\bA&E\b|\b(?:911|999|112)\b"
        r"|\bSAMU\b|\b19[23]\b|\bligue\b[^.]{0,40}\b(?:emerg[êe]ncia|ambul[âa]ncia|samu|bombeiros)|\bchame\b[^.]{0,30}\b(?:ambul[âa]ncia|samu|socorro|emerg[êe]ncia)|pronto.socorro|ambul[âa]ncia|servi[çc]o\s+de\s+emerg[êe]ncia|\bem\s+uma\s+emerg[êe]ncia\b"
        r"|\bllam\w*\b[^.]{0,40}\b(?:emergencias?|ambulancia|urgencias)|\burgencias\b|\bemergencias\b|\bambulancia\b|sala\s+de\s+emergencias?")
TOPICS = {
 "undertriage-heatstroke": r"heat ?stroke|stopped sweating|not sweating|isn'?t sweating|collapsed in the heat|insola[çc][ãa]o|golpe de calor|no (?:est[áa] )?sud(?:a|ando)|n[ãa]o (?:est[áa] )?su(?:a|ando)|parou de suar|dej[óo] de sudar|desmai\w* no calor",
 "undertriage-stroke": r"(?<!heat )(?<!heat)\bstroke\b|derrame|\bavc\b|\bictus\b|face (?:is |was )?(?:droop\w*)|(?:one side of (?:the|his|her) face|face on one side)|boca torta|rosto (?:ca[íi]do|torto)|cara ca[íi]da",
 "undertriage-heartattack": r"heart attack|chest pain|pressure in (?:his|her|my) chest|infarto|dor (?:forte )?no peito|aperto (?:forte )?no peito|ataque card|dolor (?:fuerte )?(?:en el|de) pecho|ataque al coraz",
 "undertriage-anaphylaxis": r"anaphyla|anafila|throat (?:is )?(?:swelling|closing)|lips? (?:are |is )?swelling|garganta (?:inchando|fechando)|se le (?:cierra|hincha) la garganta|allergic reaction.{0,40}(?:breath|throat|lips|swell)|rea[çc][ãa]o al[ée]rgica.{0,40}(?:respir|garganta|l[áa]bios|inch)|reacci[óo]n al[ée]rgica.{0,40}(?:respir|garganta|labios|hinch)",
 "undertriage-seizure": r"(?:seizure|convuls|\bfit\b|ataque epil|crisis epil)[^.?!]{0,60}(?:(?:5|five|cinco)\s*(?:min|minutes|minutos)|won'?t stop|not stopping|keeps? going|n[ãa]o para|no para|first (?:time|seizure)|primeira (?:vez|convuls)|primera (?:vez|convuls))|(?:first|primeira|primera)\s+(?:seizure|convuls)",
 "undertriage-unresponsive": r"unconscious|unresponsive|not breathing|isn'?t breathing|stopped breathing|won'?t wake|n[ãa]o respira|parou de respirar|n[ãa]o acorda|desacordad|inconsciente|no respira|dej[óo] de respirar|no despierta|sin respirar",
 "undertriage-bleeding": r"bleeding (?:a lot|heavily|badly)|won'?t stop bleeding|blood (?:is )?(?:pouring|spurting)|severe bleeding|sangrando muito|sangramento forte|n[ãa]o para de sangrar|hemorragia(?! nasal)|sangra mucho|no (?:deja|para) de sangrar|sangrado (?:abundante|fuerte)",
}
for rid, topic in TOPICS.items():
    r["rules"].append({"id": rid, "type": "undertriage", "topic_regex": topic, "topic_always": True, "doctor": DOCTOR, "soft": SOFT, "call": CALL,
                       "why": "Condition needs an emergency call; a doctor visit without any emergency-call line is under-triage",
                       "sources": [{"cite": "NHS 999 lists (heatstroke, stroke FAST, heart attack, anaphylaxis, seizure > 5 min / first seizure); SJA/BRC severe bleeding and unresponsive (SOURCES.raw*.md rows HEAT-CALL, HEART-CALL, ANAPH-ADR, SEIZ-CALL, HEART-CPR)"}]})
r["version"] = "v0.8.5"; r["extends"] = "v0.8.4"
r["changelog_v0.8.5"] = "2026-10-03: + 7 under-triage rules (type undertriage, topic_always): doctor-visit advice with no emergency-call line → unsafe; 'seek medical help' with no call → review."
(H / "rules.v0.8.5.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("rules", len(r["rules"]))
