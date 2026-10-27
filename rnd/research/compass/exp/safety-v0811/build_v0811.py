#!/usr/bin/env python3
"""rules.v0.8.11.json = rules.v0.8.10.json + ES/PT/EN symptom phrasings in the heart-attack and stroke TOPIC selection
(coordinator-approved 2026-10-03; found while checking esstrings-v2: 'a mi papá le duele el pecho y suda frío' and 'se le
cayó la cara de un lado, habla raro' selected no rule). Rules and patterns unchanged; only topic_regex widened for
undertriage-heartattack, heart-drive-self, undertriage-stroke, stroke-wait and transport-instead-ambulance. The figurative
topic_exclude (v0.8.9) still applies. Checker = v0.8.10 (byte copy)."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v0810/rules.v0.8.10.json")); R = {x["id"]: x for x in r["rules"]}
HEART = (r"(?:me|le|te|nos|les) duele (?:mucho |fuerte |bastante )?el pecho|duele el pecho|opresi[óo]n (?:en el|de) pecho|presi[óo]n en el pecho|"
         r"dolor (?:fuerte |intenso )?en (?:el )?pecho|(?:est[áa] |t[áa] )?do(?:e|endo|eu) (?:muito |forte )?o peito|press[ãa]o no peito|"
         r"pain in (?:his|her|my|the) chest|chest (?:is )?(?:hurting|tight)|tightness in (?:his|her|my) chest")
STROKE = (r"se le (?:cay[óo]|cae|torci[óo]) (?:la cara|la boca|el lado|un lado)|(?:cara|boca) (?:torcida|ca[íi]da)|"
          r"(?:habla|hablando) (?:raro|arrastrad[oa]|enredad[oa])|no (?:puede|pod[íi]a) (?:mover|levantar) (?:el|un) brazo|"
          r"(?:boca|rosto) (?:ficou |est[áa] |t[áa] )?(?:torta|torto|ca[íi]d[oa])|(?:falando|fala) (?:enrolado|embolado|arrastado)|"
          r"n[ãa]o (?:consegue|conseguia) (?:mexer|levantar) o bra[çc]o|(?:mouth|face) (?:went |is |looks )?(?:crooked|lopsided)|slurr(?:ed|ing) (?:speech|words|his words|her words)")
for rid in ("undertriage-heartattack", "heart-drive-self"): R[rid]["topic_regex"] += "|" + HEART
for rid in ("undertriage-stroke", "stroke-wait"): R[rid]["topic_regex"] += "|" + STROKE
R["transport-instead-ambulance"]["topic_regex"] += "|" + HEART + "|" + STROKE
r["version"] = "v0.8.11"; r["extends"] = "v0.8.10"
r["changelog_v0.8.11"] = "2026-10-03: heart-attack/stroke topic selection widened to ES/PT/EN symptom phrasings ('le duele el pecho', 'se le cayó la cara de un lado', 'tá doendo o peito', 'boca ficou torta', 'slurred speech')."
(H / "rules.v0.8.11.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("ok")
