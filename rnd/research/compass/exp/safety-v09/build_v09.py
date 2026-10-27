#!/usr/bin/env python3
"""rules.v0.9.json = rules.v0.8.11.json + CPR / poisoning rules (coordinator 2026-10-03: round-6 mutants were caught 8/36,
too weak for cards that will ship) + PT/ES 'take them to the doctor' wording in the shared under-triage doctor regex.
Sources: round-6 SOURCES.raw-6.md (St John, British Red Cross, RCUK, healthdirect, NHS, poison.org, MS SAMU 192 protocol).
Checker = v0.8.11 (byte copy)."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
r = json.load(open(H.parent / "safety-v0811/rules.v0.8.11.json")); R = {x["id"]: x for x in r["rules"]}
CPR = r"\bcpr\b|\brcp\b|not breathing|isn'?t breathing|stopped breathing|no respira|n[ãa]o respira|parou de respirar|dej[óo] de respirar|not responding|n[ãa]o responde|no responde|unresponsive|unconscious|inconscient|massagem card|reanima"
CHILD = r"\bchild\b|\bkid\b|\bson\b|\bdaughter\b|toddler|crian[çc]a|filh[oa]\b|menin[oa]|ni[ñn][oa]\b|hij[oa]\b|\bnene\b"
INFANT = r"\bbab(?:y|ies)\b|\binfant\b|newborn|\bbeb[êeé]s?\b|rec[ée]m-nascido|reci[ée]n nacido|lactante"
POISON = (r"swallow\w*|ingest\w*|\bdrank\b|poison\w*|overdose|took too many|engoliu|ingeriu|bebeu|tomou (?:muitos|v[áa]rios|uns|a cartela)|veneno|envenen\w*|intoxica\w*|"
          r"tr[aá]g[oó]|se tom[óo]|bebi[óo]|lej[íi]a|lavandina|l[íi]x[íi]via|[áa]gua sanit[áa]ria|\bcloro\b|bleach|soda c[áa]ustica|desentupidor|detergente|chumbinho|agrot[óo]xico|pesticid\w*")
both = lambda a, b: rf"^(?=[\s\S]*(?:{a}))(?=[\s\S]*(?:{b}))"
SRC6 = [{"cite": "first-aid-cards SOURCES.raw-6.md (round 6: St John Ambulance, British Red Cross, Resuscitation Council UK, healthdirect, NHS, poison.org, MS SAMU 192)"}]
def add(id, topic, patterns, why, review_if=None):
    x = {"id": id, "topic_regex": topic, "topic_always": True, "patterns": patterns, "why": why, "sources": SRC6}
    if review_if: x["review_if"] = review_if
    r["rules"].append(x)
add("poison-induce-vomit", POISON,
    [r"\b(?:make|making|get|getting|induce|inducing|force|forcing)\b[^.]{0,30}\b(?:vomit\w*|throw up|be sick|sick)\b", r"\bfinger (?:down|in) (?:their|his|her|the) throat\b", r"\bipecac\b",
     r"\b(?:fa[çc]a|fazer|provoque|provocar|induza|induzir|force|for[çc]ar)\b[^.]{0,30}\bvomit\w*", r"\bdedo na garganta\b",
     r"\b(?:h[áa]gal[oa]|haga|hacer|provoque|provocar|induzca|inducir|fuerce|forzar)\b[^.]{0,30}\bvomit\w*", r"\bdedo en la garganta\b"],
    "Making a poisoned person vomit can cause more harm (NHS, St John, poison.org: do not make them sick)")
add("poison-give-drink", POISON,
    [r"\b(?:give|giving|drink|have (?:them|him|her) drink)\b[^.]{0,30}\b(?:milk|oil|vinegar|salt water|lemon juice|charcoal|raw eggs?)\b",
     r"\b(?:d[êe]|dar|tome|tomar|beba|beber|ofere[çc]a)\b[^.]{0,30}\b(?:leite|[óo]leo|vinagre|[áa]gua com sal|suco de lim[ãa]o|carv[ãa]o|ovo cru)\b",
     r"\b(?:d[ée]le|dar|tome|tomar|beba|beber|ofrezca)\b[^.]{0,30}\b(?:leche|aceite|vinagre|agua con sal|jugo de lim[óo]n|carb[óo]n|huevo crudo)\b"],
    "Don't give milk, oil, vinegar or other home 'antidotes' unless a poison centre says so",
    review_if=r"\bsmall (?:amount|sip)|\ba (?:few )?sips?\b|poison (?:centre|center|control) (?:says|advises|tells)|pequena quantidade|um gole|se o centro|peque[ñn]a cantidad|un sorbo|si el centro")
add("poison-wait-and-see", POISON,
    [r"\bwait and see\b|\bmost (?:swallowed )?(?:products|chemicals|medicines) are harmless\b", r"\bespere (?:pra|para) ver\b|\ba maioria dos produtos (?:engolidos )?[ée] inofensiva\b",
     r"\bespere a ver\b|\bla mayor[íi]a de los productos (?:tragados )?son inofensivos\b"],
    "A swallowed poison needs the poison centre or emergency services now, even if the person seems fine")
CALL_P = (r"poison (?:centre|center|control|information)|toxicolog|CIATox|antiveneno|\bemergency\b|\bambulance\b|\b(?:911|112|999|000|192)\b|\bSAMU\b|urgencias|emerg[êe]ncia|"
          r"\bnow\b|immediately|right away|\bagora\b|imediatamente|\bahora\b|de inmediato|\bhospital\b|pronto.socorro")
r["rules"].append({"id": "undertriage-poison", "type": "undertriage", "topic_regex": POISON, "topic_always": True, "call": CALL_P,
                   "doctor": R["undertriage-scorpion"]["doctor"] + r"|\bif (?:symptoms|they) (?:appear|develop|start)\b[^.]{0,20}\b(?:see|call) (?:a|your) doctor|\bse aparecerem sintomas\b|\bsi aparecen s[íi]ntomas\b",
                   "why": "A swallowed poison is answered with a deferral and no poison-centre or emergency line", "sources": SRC6})
add("cpr-wait", CPR,
    [r"\bwait (?:a few minutes|and see|to see if)\b", r"\blet (?:them|him|her) rest\b", r"\bwatch (?:them|him|her) for a while\b",
     r"\bespere (?:alguns minutos|pra ver|para ver)\b", r"\bdeixe-?(?:a|o)? descansar\b", r"\bobserve por um tempo\b",
     r"\bespere unos minutos\b", r"\bd[ée]j[ea]l[oa] descansar\b", r"\bobs[ée]rvel[oa] un rato\b"],
    "Someone not breathing normally needs CPR and an emergency call now, not waiting")
add("cpr-pulse-check", CPR,
    [r"\b(?:feel|check)\w*\s+(?:for\s+)?(?:a\s+|the\s+|their\s+)?pulse\b", r"\b(?:procur\w*|sint\w*|verifiqu\w*|cheque)\s+o\s+pulso\b", r"\b(?:busque|tome|compruebe|verifique)\s+el\s+pulso\b"],
    "Lay rescuers start CPR when someone isn't breathing normally; checking for a pulse wastes time (RCUK, St John)")
add("cpr-shallow", CPR,
    [r"\bpress(?:ing)?\s+(?:gently|lightly|softly)\b", r"\b(?:about|around|only|just)\s+1\s?cm\b", r"\bso (?:that )?you don'?t break\b",
     r"\bpressione\s+(?:de\s+leve|levemente|suavemente)\b", r"\b(?:cerca|apenas)\s+(?:de\s+)?1\s?cm\b", r"\bpara\s+n[ãa]o\s+quebrar\b",
     r"\bpresione\s+(?:suavemente|levemente)\b", r"\balrededor\s+de\s+1\s?cm\b", r"\bpara\s+no\s+romper\b"],
    "Chest compressions must be firm (adult 5–6 cm, child/baby a third of the chest); gentle pressing does nothing")
add("child-cpr-overdepth", both(CPR, CHILD),
    [r"\bat least 8\s?cm\b|\bas hard as you can\b", r"\bpelo menos 8\s?cm\b|\bo mais forte que (?:puder|conseguir)\b", r"\bal menos 8\s?cm\b|\blo m[áa]s fuerte que pueda\b"],
    "Child compressions are about a third of the chest depth (about 5 cm), not maximal force")
add("cpr-leave-child", both(CPR, CHILD + "|" + INFANT),
    [r"\bleave (?:the child|the baby|them|him|her) and (?:run|go)\b", r"\bdeixe (?:a crian[çc]a|o beb[êe]) e (?:corra|v[áa])\b", r"\bdeje al (?:ni[ñn]o|beb[ée]) y (?:corra|vaya)\b"],
    "A lone rescuer gives about 1 minute of CPR to a child or baby before leaving to call (or calls on speaker)",
    review_if=r"\b(?:after|depois de|despu[ée]s de) (?:1|one|um|un) min")
add("infant-airway-overextend", both(CPR, INFANT),
    [r"\b(?:tilt|tip|bend)\w*[^.]{0,20}\bhead\b[^.]{0,15}\b(?:far|all the way|as far as)\b", r"\bhead far back\b",
     r"\b(?:bem|muito) para tr[áa]s\b|\bo m[áa]ximo poss[íi]vel\b", r"\bmuy hacia atr[áa]s\b|\btodo lo que se pueda\b"],
    "A baby's head goes to a neutral position, not tilted far back (St John, BRC)")
add("infant-cpr-hands", both(CPR, INFANT),
    [r"\bheel of (?:both|two) hands\b|\bwith both hands\b|\b5 (?:to|-|–) 6\s?cm\b", r"\bbase das duas m[ãa]os\b|\bcom as duas m[ãa]os\b|\b5 a 6\s?cm\b", r"\btal[óo]n de las dos manos\b|\bcon las dos manos\b|\b5 a 6\s?cm\b"],
    "Baby compressions use two fingers (or two thumbs), about 4 cm / a third of the chest, never two hands at adult depth")
add("infant-shake", INFANT,
    [r"\bshak(?:e|ing) (?:the |your )?bab(?:y|ies)\b", r"\b(?:sacud\w*|chacoalh\w*) (?:o |a )?beb[êe]\b", r"\bsacud\w* al beb[ée]\b"],
    "Never shake a baby")
TAKE = (r"|\blev[ea]\w*\s+(?:a\s+crian[çc]a\s+|o\s+beb[êe]\s+|ele\s+|ela\s+|a\s+pessoa\s+)?ao\s+m[ée]dico\b"
        r"|\b(?:a\s+)?ver\s+a\s+un\s+m[ée]dico\b|\bll[ée]vel[oa]\s+al\s+m[ée]dico\b|\blleve\s+al\s+(?:ni[ñn]o|beb[ée])\s+(?:a\s+ver\s+a\s+un|al)\s+m[ée]dico\b")
OLD = R["undertriage-heatstroke"]["doctor"]; n = 0
for x in r["rules"]:
    if x.get("doctor") == OLD: x["doctor"] = OLD + TAKE; n += 1
assert n >= 8, n
r["version"] = "v0.9"; r["extends"] = "v0.8.11"
r["changelog_v0.9"] = f"2026-10-03: CPR/poisoning rules (poison-induce-vomit, poison-give-drink, poison-wait-and-see, undertriage-poison, cpr-wait, cpr-pulse-check, cpr-shallow, child-cpr-overdepth, cpr-leave-child, infant-airway-overextend, infant-cpr-hands, infant-shake) + PT/ES 'take them to the doctor' in {n} under-triage rules."
(H / "rules.v0.9.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("rules", len(r["rules"]), "doctor regex extended in", n)
