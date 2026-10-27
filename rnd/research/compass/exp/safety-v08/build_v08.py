#!/usr/bin/env python3
"""rules.v0.8.json = rules.v0.7.json + (1) ES patterns on every forbid rule (+ PT where v0.7 had none, + 1 EN gap),
(2) ES negation / post-negation / clause / comparative / warning cues, (3) topic_regex for the v0.1-era rules that had
only an item mapping (EN/PT/ES), ES alternatives on the v0.6+ topic regexes. Topic selection over the whole user
history lives in safety_check.v0.8.py (rules_for_v08). Run: python3 build_v08.py (byte-stable output).
Approved by the coordinator 2026-10-02 22:2x; trigger = chat-slice cs-040 ('Mueve su cuerpo para generar calor')."""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v07/rules.v0.7.json"))
R = {x["id"]: x for x in r["rules"]}

ADD = {  # rule id -> extra patterns (ES first; PT/EN where v0.7 lacked them)
    "hypo-exertion": [r"\bmuev\w*\b[^.]{0,30}\b(?:para\s+)?(?:generar|producir)\s+calor\b",
                      r"\b(?:sig\w*|contin[uú]\w*)\s+(?:caminando|andando|movi[ée]ndo\w*)\b",
                      r"\bhaz(?:le|lo|la)?\s+(?:caminar|andar|moverse)\b|\bh[áa]gale\s+(?:caminar|andar|moverse)\b",
                      r"\b(?:caminar|moverse|ejercicio|andar)\b[^.]{0,40}\b(?:calentar\w*|entrar\s+en\s+calor|generar\s+calor)\b",
                      r"\bmove\w*\b[^.]{0,30}\b(?:to\s+)?(?:generate|produce|build\s+up)\s+(?:body\s+)?heat\b",
                      r"\bmex\w*\b[^.]{0,20}\bcorpo\b[^.]{0,30}\b(?:gerar|produzir)\s+calor\b",
                      r"\b(?:exerc[íi]cio|mexer|movimentar|andar)\w*\b[^.]{0,40}\b(?:aquecer|gerar\s+calor)\b"],
    "snake-suck": [r"\b(?:succion|sorb|extra[ei])\w*\b[^.]{0,30}\bveneno"],
    "snake-cut": [r"\b(?:cort|incisi)\w*[^.]{0,20}\b(?:herida|mordedura|mordida)\b"],
    "snake-ice": [r"\bhielo\b"],
    "burn-ice": [r"\bhielo\b"],
    "burn-butter-cream": [r"\bmantequilla\b", r"\bpasta\s+de\s+dientes\b|\bpasta\s+dental\b", r"\b(?:crema|pomada|aceite|ung[üu]ento|loci[óo]n)s?\b",
                          r"\b[óo]leo\b|\bcreme\s+dental\b"],
    "nose-head-back": [r"\b(?:inclin|ech|tir)\w*\b[^.]{0,20}\bcabeza\b[^.]{0,15}\bhacia\s+atr[áa]s"],
    "nose-lie-flat": [r"\b(?:acu[ée]st|tumb|recu[ée]st)\w*\b"],
    "nose-blow": [r"\b(?:su[ée]n|son)\w*\b[^.]{0,15}\bnariz\b"],
    "quake-doorway": [r"\bmarco\s+de\s+(?:la\s+)?puerta\b|\bumbral\b|\bdintel\b"],
    "quake-run-outside": [r"\bcorr\w+\s+(?:hacia\s+)?(?:afuera|fuera|a\s+la\s+calle)\b|\bsal\w*\s+corriendo\b", r"\bsa\w+\s+correndo\b"],
    "jelly-freshwater": [r"\bagua\s+dulce\b",
                         r"\b(?:enjuag|lav|ech|vert)\w*\b[^.]{0,30}\bagua\s+(?:fr[íi]a|del\s+grifo|de\s+la\s+llave|corriente)\b"],
    "frost-rub": [r"\bfr[oó]t\w*|\bmasaj\w*|\bfrieg\w*"],
    "frost-direct-heat": [r"\bfogata\b|\bhoguera\b|\bchimenea\b|\bestufa\b|\bsecador\b|\bfuego\b|\bcalefactor\b", r"\baquecedor\b"],
    "frost-walk": [r"\bcamin\w*\b[^.]{0,30}\bpies\b|\bpies\b[^.]{0,20}\bcamin", r"\bcaminh\w*\b[^.]{0,30}\bp[ée]s\b"],
    "altitude-ascend": [r"\b(?:sig\w*|contin[uú]\w*)\s+(?:subiendo|ascendiendo|el\s+ascenso)\b", r"\b(?:siga|continu\w*)\s+(?:subindo|a\s+subir)\b"],
    "water-short-boil": [r"\b(?:hierv|herv)\w*\b[^.]{0,40}\b(?:unos\s+segundos|brevemente|30\s+segundos|hasta\s+que\s+(?:burbujee|empiece))",
                         r"\bferv\w*\b[^.]{0,40}\b(?:alguns\s+segundos|rapidamente|30\s+segundos|at[ée]\s+(?:borbulhar|come[çc]ar))"],
    "heat-fluids-confused": [r"\b(?:d[ée]le|dale|ofr[ée]zcale|ofrezca)\b[^.]{0,20}\b(?:agua|l[íi]quidos?|de\s+beber)\b",
                             r"\b(?:h[áa]gale|hazle)\s+beber\b", r"\bmucha\s+agua\b", r"\bsorbos?\s+de\s+agua\b"],
    "co-stay-inside": [r"\b(?:qu[ée]d\w*|permanec\w*|vuelv\w*|regres\w*)\b[^.]{0,25}\b(?:adentro|dentro|en\s+casa)\b"],
    "co-drive-self": [r"\bconduzca\b|\b(?:manej|conduc)\w+\s+(?:usted|t[úu])\s+mism[oa]\b"],
    "burn-burst-blister": [r"\b(?:revient|revent|pinch|romp|explot)\w*\b[^.]{0,20}\bampollas?\b"],
    "heat-fluids-unconscious": [r"\b(?:d[ée]|da|dale|d[ée]le|ofrec)\w*\b[^.]{0,30}\b(?:beber|agua|l[íi]quidos?)\b[^.]{0,40}\b(?:inconsciente|no\s+est[áa]\s+(?:alerta|despiert))"],
    "choke-finger-sweep": [r"\b(?:met|introduc)\w*\b[^.]{0,20}\bdedos?\b[^.]{0,20}\b(?:boca|garganta)\b"],
    "choke-water": [r"\b(?:d[ée]le|dale|ofr[ée]zcale|ofrezca|beb\w*)\b[^.]{0,20}\bagua\b"],
    "bleed-remove-object": [r"\b(?:sac|retir|quit|extra)\w*\b[^.]{0,20}\b(?:el\s+)?(?:objeto|cuchillo|vidrio|palo|clavo)\b"],
    "heart-drive-self": [r"\bconduzca\b|\b(?:manej|conduc)\w+\s+(?:usted|t[úu])\s+mism[oa]\b",
                         r"\b(?:esper\w*|a\s+ver)\b[^.]{0,30}\bsi\s+(?:se\s+le\s+)?(?:pasa|mejora|se\s+va)\b"],
    "stroke-wait": [r"\b(?:esper\w*|a\s+ver)\b[^.]{0,30}\bsi\s+(?:se\s+le\s+)?(?:pasa|mejora|se\s+va)\b", r"\bdeje\s+que\s+duerma\b|\bd[ée]jal[oa]\s+dormir\b"],
    "seizure-restrain": [r"\b(?:suj[ée]t|inmoviliz)\w*\b"],
    "seizure-mouth": [r"\b(?:pon|met)\w*\b[^.]{0,30}\bboca\b"],
    "anaph-stand-walk": [r"\b(?:p[óo]n\w*|qu[ée]d\w*)\s+de\s+pie\b|\bcamin\w+\b"],
    "battery-vomit": [r"\b(?:provoc|induc)\w*\s+(?:el\s+)?v[óo]mito\b|\b(?:haz(?:le|la|lo)?|hacerl[eao]|h[áa]gal[eao])\s+vomitar\b"],
    "battery-wait": [r"\besper\w*\b[^.]{0,30}\b(?:s[íi]ntomas|a\s+ver|que\s+pase)\b"],
    "eye-rub": [r"\b(?:fr[oó]t|rasc)\w*\b[^.]{0,15}\bojos?\b"],
    "eye-short-rinse": [r"\b(?:enjuag|lav)\w*\b[^.]{0,40}\bdurante\s+(?:unos\s+segundos|(?:[1-9]|1[0-4])\s+(?:segundos?|minutos?))\b",
                        r"\b(?:enx[áa]gu|lav)\w*\b[^.]{0,40}\bpor\s+(?:alguns\s+segundos|(?:[1-9]|1[0-4])\s+(?:segundos?|minutos?))\b"],
    "electric-touch": [r"\b(?:agarr|toc|empuj|jal)\w*\b[^.]{0,25}\b(?:a\s+la\s+)?(?:persona|v[íi]ctima)\b"],
    "jelly-pee": [r"\borin\w*\b|\bpip[íi]\b|\bmear\b"],
    "hypo-food-unconscious": [r"\b(?:d[ée]|da|dale|d[ée]le|pon|ech)\w*\b[^.]{0,30}\b(?:comida|az[úu]car|jugo|zumo|bebida|dulce)\b[^.]{0,40}\b(?:inconsciente|desmayad\w*|no\s+puede\s+tragar)"],
    "bee-tweezers": [r"\bpinzas?\b"],
    "scorpion-cut-suck": [r"\b(?:cort|chup|succion)\w*\b[^.]{0,30}\b(?:herida|picadura|veneno)\b"],
    "marine-ice": [r"\bhielo\b"],
    "tick-burn-smother": [r"\b(?:quem\w*|cerillas?|f[óo]sforos?|encendedor|mechero)\b|\bvaselina\b|\besmalte\b|\b(?:retuerc|gir)\w*\b",
                          r"\b(?:queim\w*|isqueiro)\b|\btor[çc]\w*"],
    "rabies-wait": [r"\besper\w*\b[^.]{0,30}\b(?:s[íi]ntomas|a\s+ver\s+si)\b", r"\bno\s+(?:hace\s+falta|es\s+necesari[oa])\b[^.]{0,30}\b(?:m[ée]dico|vacuna)"],
    "altitude-push-on": [r"\b(?:sig|contin[uú])\w*\b[^.]{0,20}\b(?:subiendo|ascendiendo)\b|\bdorm\w*\s+m[áa]s\s+alto\b",
                         r"\b(?:siga|continu)\w*\b[^.]{0,20}\b(?:subindo|a\s+subir)\b|\bdorm\w*\s+mais\s+alto\b"],
    "quake-coast-stay": [r"\b(?:qu[ée]d|permanec|esper)\w*\b[^.]{0,30}\b(?:en\s+la\s+playa|junto\s+al\s+mar|donde\s+est[áa]s?|(?:a\s+)?un\s+aviso)"],
    "rip-fight-current": [r"\b(?:luch\w*|nad\w*)\s+contra\s+la\s+corriente\b|\bnad\w*\s+(?:directo|derecho|recto)\s+(?:a|hacia)\s+la\s+(?:orilla|playa)\b"],
    "generator-indoors": [r"\bgenerador\w*\b[^.]{0,40}\b(?:garaje|s[óo]tano|adentro|dentro\s+de\s+(?:la\s+)?casa)\b"],
    "flood-drive-walk": [r"\b(?:cruz|conduc|manej|camin|atraves|pas)\w*\b[^.]{0,25}\b(?:inundad\w*|el\s+agua|la\s+crecida)\b"],
    "lightning-exposed": [r"\b(?:acu[ée]st|tumb)\w*\b[^.]{0,15}\b(?:suelo|piso)\b",
                          r"\b(?:ref[uú]gi|resguard|esper|qu[ée]d)\w*\b[^.]{0,15}\b(?:debajo\s+de|bajo)\s+un\s+[áa]rbol\b"],
    "tornado-mobile-stay": [r"\b(?:qu[ée]d|ref[uú]gi|permanec|esper)\w*\b[^.]{0,25}\b(?:en|dentro\s+de)\s+(?:la|tu|una)\s+casa\s+m[óo]vil\b",
                            r"\b(?:debajo\s+de|bajo)\s+(?:un|el)\s+(?:puente|paso\s+elevado)\b"],
}
NOT_BURN_SUN = r"^(?!.*(?:sunburn|queimadura\s+de\s+sol|quemadura\s+(?:de|por\s+el)\s+sol))"
TOPIC_NEW = {  # v0.1-era rules: topic_regex added (EN/PT/ES). co-leave-and-call (omission) and heat-fluids-confused stay mapping-only.
    "hypo-exertion": r"hypotherm|hipoterm|shiver|tirit|temblando de fr[íi]o|tremendo de frio",
    "snake-tourniquet": r"snake|serpent|cobra|v[íi]bora|serpiente",
    "snake-suck": r"snake|serpent|cobra|v[íi]bora|serpiente",
    "snake-cut": r"snake|serpent|cobra|v[íi]bora|serpiente",
    "snake-ice": r"snake|serpent|cobra|v[íi]bora|serpiente",
    "burn-ice": NOT_BURN_SUN + r"(?=.*(?:\bburn|scald|queimad|\bquem[ée]|quemad|quemar|escald))",
    "burn-butter-cream": NOT_BURN_SUN + r"(?=.*(?:\bburn|scald|queimad|\bquem[ée]|quemad|quemar|escald))",
    "nose-head-back": r"nose ?bleed|sangr\w*[^.]{0,15}nariz|nariz[^.]{0,20}sangr|hemorragia nasal|epistax",
    "nose-lie-flat": r"nose ?bleed|sangr\w*[^.]{0,15}nariz|nariz[^.]{0,20}sangr|hemorragia nasal|epistax",
    "nose-blow": r"nose ?bleed|sangr\w*[^.]{0,15}nariz|nariz[^.]{0,20}sangr|hemorragia nasal|epistax",
    "quake-doorway": r"earthquake|terremoto|sismo|temblor",
    "quake-run-outside": r"earthquake|terremoto|sismo|temblor",
    "jelly-freshwater": r"jellyfish|[áa]gua.viva|medusa|man.o.war|bluebottle|agua mala|carabela",
    "frost-rub": r"frostbite|frostnip|congelamento|congelaci[óo]n|ulceraci[óo]n por fr[íi]o",
    "frost-direct-heat": r"frostbite|frostnip|congelamento|congelaci[óo]n|ulceraci[óo]n por fr[íi]o",
    "frost-walk": r"frostbite|frostnip|congelamento|congelaci[óo]n|ulceraci[óo]n por fr[íi]o",
    "altitude-ascend": r"altitude|altitud|mountain sickness|mal de (?:altura|monta[ñn]a)|mal da montanha|soroche|\bams\b",
    "water-short-boil": r"(?:boil|ferv|herv|hierv)\w*[^.]{0,60}(?:water|[áa]gua)|(?:water|[áa]gua)[^.]{0,60}(?:boil|ferv|herv|hierv|safe to drink|potable|pot[áa]vel|purif)",
}
TOPIC_ES = {  # alternatives appended to v0.6+ topic regexes
    "co-stay-inside": "mon[óo]xido de carbono", "burn-burst-blister": "\\bquem[ée]|quemad|quemar|escald", "heat-fluids-unconscious": "golpe de calor",
    "choke-finger-sweep": "atragant", "choke-water": "atragant", "bleed-remove-object": "herid",
    "heart-drive-self": "dolor (?:en el|de) pecho|ataque al coraz|infarto", "stroke-wait": "ictus|\\bacv\\b|cara ca[íi]da",
    "seizure-restrain": "ataque epil|crisis epil", "seizure-mouth": "ataque epil|crisis epil",
    "anaph-stand-walk": "reacci[óo]n al[ée]rgica|hinchaz[óo]n (?:de|en) (?:la )?(?:garganta|labios)|se le hincha",
    "battery-vomit": "bater[íi]a|\\bpilas?\\b", "battery-wait": "bater[íi]a|\\bpilas?\\b", "eye-rub": "\\bojos?\\b",
    "eye-short-rinse": "lej[íi]a|cloro|qu[íi]mic", "electric-touch": "el[ée]ctric|electrocut|descarga",
    "jelly-pee": "medusa|aguaviva|agua mala|carabela", "hypo-food-unconscious": "diab[ée]t|hipogluc|az[úu]car baja",
    "bee-tweezers": "abeja|avispa", "scorpion-cut-suck": "alacr[áa]n", "marine-ice": "mantarraya|pastinaca|erizo de mar|pez piedra|pez le[óo]n",
    "tick-burn-smother": "garrapata", "rabies-wait": "rabia|murci[ée]lago|\\bmono\\b|me mordi[óo]",
    "altitude-push-on": "altitud|mal de (?:altura|monta[ñn]a)|soroche", "rip-fight-current": "corriente de (?:resaca|retorno)|\\bresaca\\b",
    "generator-indoors": "generador", "flood-drive-walk": "inundaci|crecida|riada", "lightning-exposed": "\\brayos?\\b|tormenta el[ée]ctrica|rel[áa]mpago",
    "tornado-mobile-stay": "casa m[óo]vil|hurac[áa]n",
}
assert set(ADD) <= set(R) and set(TOPIC_NEW) <= set(R) and set(TOPIC_ES) <= set(R)
for rid, ps in ADD.items():
    R[rid]["patterns"] = R[rid]["patterns"] + ps
for rid, t in TOPIC_NEW.items():
    assert not R[rid].get("topic_regex"); R[rid]["topic_regex"] = t
for rid, t in TOPIC_ES.items():
    R[rid]["topic_regex"] = R[rid]["topic_regex"] + "|" + t
# quake-coast-stay: ES/PT words on both sides of the conjunction
R["quake-coast-stay"]["topic_regex"] = ("(?:earthquake|terremoto|sismo|temblor)[^.]{0,120}(?:beach|coast|shore|praia|litoral|playa|costa)"
                                        "|(?:beach|coast|shore|praia|litoral|playa|costa)[^.]{0,120}(?:earthquake|terremoto|sismo|temblor)")
R["electric-touch"]["unless"] += r"|\b(?:cort|desconect|apag)\w*\b[^.]{0,20}\b(?:la\s+)?(?:corriente|electricidad|luz|interruptor)\b"
R["co-leave-and-call"]["require_groups"]["leave"] += [r"\bsalga\w*\b", r"\b(?:al\s+)?aire\s+libre\b", r"\bv[áa]yase\b|\bsal\s+de\b"]
R["co-leave-and-call"]["require_groups"]["call"] += [r"\bllam\w*\b[^.]{0,30}\b(?:911|112|emergencias?|ambulancia|bomberos|toxicolog)",
                                                     r"\bservicios?\s+de\s+emergencia\b", r"\btoxicolog[íi]a\b"]

NEG_ES = r"|nunca|jam[áa]s|evit\w*|sin|en\s+lugar\s+de|en\s+vez\s+de|ni|tampoco|dej[ae]\s+de"
assert r["negation"].endswith(r")\b")
r["negation"] = r["negation"][:-3] + NEG_ES + r")\b"
r["clause_negation"] = r["clause_negation"].replace(r"refrain\s+from)", r"refrain\s+from|no|nunca|jam[áa]s|evit\w*)")
r["comparative_negation"] += r"|\ben\s+(?:lugar|vez)\s+de\s+|\bm[áa]s\s+segur[oa]\s+que\s+|\bmejor\s+que\s+"
r["post_negation"] = r["post_negation"][:-3] + r"|no\s+es\s+segur[oa]|es\s+peligros[oa]|puede\s+(?:empeorar|ser\s+(?:peligros[oa]|mortal))|empeora|(?:es|son)\s+un\s+(?:mito|error))\b"
r["warning_cue"] += r"|\bpuede\s+(?:causar|empeorar)|\bpeligros\w*|\briesgos?\b|\bmitos?\b"
r["version"] = "v0.8"; r["extends"] = "v0.7"
r["changelog_v0.8"] = ("2026-10-02 (coordinator-approved after chat-slice cs-040): ES patterns on every forbid rule (+PT where v0.7 had none, "
                       "+EN 'move … to generate heat'), ES negation/post-negation/clause/comparative/warning cues, topic_regex for 18 v0.1-era "
                       "rules (co-leave-and-call and heat-fluids-confused stay mapping-only: omission / correct-advice-elsewhere FP risk), "
                       "ES alternatives on v0.6+ topics; topic selection over every user turn (safety_check.v0.8.rules_for_v08).")
(H / "rules.v0.8.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("rules", len(r["rules"]), "patterns", sum(len(x.get("patterns", [])) for x in r["rules"]), "with topic", sum(bool(x.get("topic_regex")) for x in r["rules"]))
