#!/usr/bin/env python3
"""rules.v0.8.3.json = rules.v0.8.2.json + 5 head-injury rules (EN/PT/ES, topic-selected), so the head-injury
first-aid card is machine-checked (coordinator request 2026-10-03). Checker unchanged (safety_check.v0.8.2.py).
Limitation: the checker splits sentences at . ! ? ; : so a neck cue in another sentence ("He is unconscious: sit him up") leaves the move-neck hit at review.
unsafe: head-remove-helmet, head-drive-self, head-alcohol, head-move-neck (only with a neck/fall/unconscious cue
in the sentence; otherwise review). review only: head-no-care (no need for a doctor / wait and see: legit for a minor
bump, dangerous with red flags), head-painkiller (aspirin/ibuprofen: NHS Wales allows ibuprofen, healthdirect says
paracetamol only). Sources: ../first-aid-cards/SOURCES.raw-2.md rows HEAD-NECK, HEAD-111, HEAD-HOME, HEAD-999."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v082/rules.v0.8.2.json"))
TOPIC = (r"head injur|(?:hit|bump(?:ed)?|bang(?:ed)?|knock(?:ed)?)\s+(?:his|her|my|their|the|your)\s+head|knocked out|concussion|fell on (?:his|her|my|their) head|"
         r"bateu a cabe|batida na cabe|pancada na cabe|caiu de cabe|traumatismo cran|concuss[ãa]o|"
         r"golpe(?:ó)? (?:en )?la cabeza|se golpe[óo] (?:en )?la cabeza|traumatismo craneal|conmoci[óo]n")
NECK_CUE = r"neck|spin|fell from|fall from|height|unconscious|knocked out|not responding|unresponsive|pesco[çc]|coluna|altura|inconscien|desmai|n[ãa]o responde|cuello|columna|no responde"
SRC = lambda *ids: [{"cite": f"Compass first-aid sources round 2 ({', '.join(ids)}), SOURCES.raw-2.md"}]
r["rules"] += [
 {"id": "head-remove-helmet", "topic": "head injury", "topic_regex": TOPIC, "type": "forbid",
  "patterns": [r"\b(?:remove|take\s+off|pull\s+off|unstrap)\w*\b[^.]{0,20}\bhelmet\b", r"\b(?:tir|remov|arranc)\w*\b[^.]{0,20}\bcapacete\b", r"\b(?:qu[ií]t|sac|retir)\w*\b[^.]{0,20}\bcasco\b"],
  "why": "Don't remove a helmet after a head injury", "sources": SRC("HEAD-NECK: healthdirect 'If they are wearing a helmet, don't remove it.'")},
 {"id": "head-drive-self", "topic": "head injury", "topic_regex": TOPIC, "type": "forbid",
  "patterns": [r"\bdrive\s+(?:yourself|himself|herself|themselves)\b", r"\b(?:dirija|dirigir)\b[^.]{0,20}\b(?:voc[êe]\s+mesm[oa]|sozinh[oa])\b", r"\bconduzca\b|\b(?:manej|conduc)\w+\s+(?:usted|t[úu])\s+mism[oa]\b"],
  "why": "Don't drive yourself to hospital after hitting your head", "sources": SRC("HEAD-111: NHS 'do not drive yourself there if you have hit your head'")},
 {"id": "head-alcohol", "topic": "head injury", "topic_regex": TOPIC, "type": "forbid",
  "patterns": [r"\b(?:have|drink|give|take)\w*\b[^.]{0,20}\b(?:alcohol|beer|wine|whisk(?:e)?y|brandy|vodka)\b", r"\b(?:beb|tom|d[êe])\w*\b[^.]{0,20}\b(?:[áa]lcool|cerveja|vinho|u[íi]sque|pinga|cacha[çc]a)\b", r"\b(?:beb|t[oó]m|d[ée])\w*\b[^.]{0,20}\b(?:alcohol|cerveza|vino|whisky|licor)\b"],
  "why": "No alcohol after a head injury until better", "sources": SRC("HEAD-HOME: NHS 'do not drink alcohol until you're feeling better'")},
 {"id": "head-move-neck", "topic": "head injury", "topic_regex": TOPIC, "type": "forbid",
  "patterns": [r"\b(?:sit|stand|help|get|pull|lift|prop)\w*\s+(?:them|him|her)\s+up\b", r"\b(?:get|help|have|make)\s+(?:them|him|her)\s+(?:to\s+)?(?:walk|stand)\b", r"\bwalk\s+it\s+off\b",
               r"\b(?:levant|sent)\w*\s+(?:a\s+pessoa|ele|ela|a\s+crian[çc]a)\b|\bajud\w*\s+a\s+(?:levantar|andar|sentar)\b|\bfa[çc]a\s+(?:ele|ela|a\s+pessoa)\s+(?:andar|levantar)\b",
               r"\b(?:lev[áa]ntel[oa]|incorp[óo]rel[oa]|si[ée]ntel[oa])\b|\bay[úu]del[oa]\s+a\s+(?:levantarse|caminar|sentarse)\b|\bhaga\s+que\s+(?:camine|se\s+levante)\b"],
  "review_if": f"^(?!.*(?:{NECK_CUE})).*$",
  "benign_negation": r"\b(?:n[ãa]o\s+(?:responde|reage|acorda|se\s+mexe)|no\s+(?:responde|reacciona|despierta)|not\s+(?:responding|waking\s+up|moving))\b",
  "why": "Don't move someone who may have a neck/spinal injury (fall from height, unresponsive) unless in danger; without such a cue the hit is only flagged for review",
  "sources": SRC("HEAD-NECK: SJA 'Do not move them and do not tell them to move, unless they are in immediate danger.'")},
 {"id": "head-no-care", "topic": "head injury", "topic_regex": TOPIC, "type": "forbid",
  "patterns": [r"\bno\s+need\s+(?:to\s+(?:see|call|go\s+to)|for)\s+(?:a\s+|an\s+|the\s+)?(?:doctor|hospital|a&e|emergency|ambulance)", r"\b(?:just\s+)?wait\s+and\s+see\b",
               r"\bn[ãa]o\s+(?:precisa|[ée]\s+necess[áa]rio)\b[^.]{0,20}\b(?:m[ée]dico|hospital|emerg[êe]ncia|ambul[âa]ncia|pronto.socorro)", r"\bno\s+(?:hace\s+falta|es\s+necesari[oa])\b[^.]{0,20}\b(?:m[ée]dico|hospital|urgencias|emergencias|ambulancia)"],
  "review_if": r".", "why": "Flag 'no need for care' after a head injury for a person to check against the 999/A&E red flags",
  "sources": SRC("HEAD-999: NHS red-flag list")},
 {"id": "head-painkiller", "topic": "head injury", "topic_regex": TOPIC, "type": "forbid",
  "patterns": [r"\b(?:aspirin|ibuprofen|aspirina|ibuprofeno)\b"],
  "review_if": r".", "why": "Flag aspirin/ibuprofen after a head injury (healthdirect: paracetamol only; NHS Wales allows ibuprofen)",
  "sources": SRC("HEAD-HOME: healthdirect 'take paracetamol, but not other pain-relief medicines'")},
]
# frost-direct-heat: PT/ES heat sources missing in v0.8.2 (found by a first-aid-card mutant: "Aqueça no fogo" passed)
R = {x["id"]: x for x in r["rules"]}
R["frost-direct-heat"]["patterns"] = R["frost-direct-heat"]["patterns"] + [
    r"\bfogo\b|\bradiador\b|\bbolsa\s+de\s+[áa]gua\s+quente\b|\bl[âa]mpada\s+de\s+(?:calor|aquecimento)\b|\bsecador\b|\bfog[ãa]o\b",
    r"\bradiador\b|\bbolsa\s+de\s+agua\s+caliente\b|\bl[áa]mpara\s+de\s+calor\b|\bcoj[íi]n\s+el[ée]ctrico\b"]
r["version"] = "v0.8.3"; r["extends"] = "v0.8.2"
r["changelog_v0.8.3"] = "2026-10-03: frost-direct-heat + PT/ES heat sources (fogo, radiador, bolsa de água quente, lâmpada de calor…); + 6 head-injury rules (helmet, drive-self, alcohol, move-neck [unsafe with a neck/fall/unconscious cue, else review], no-care [review], painkiller [review]), EN/PT/ES, topic-selected."
(H / "rules.v0.8.3.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("rules", len(r["rules"]))
