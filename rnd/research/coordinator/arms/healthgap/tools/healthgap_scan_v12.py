"""HEALTHGAP v1.2 scan (0 LLM) = the v1.1 scan (healthgap_scan_v11.py) + REVIEW-healthgap-r2.md: DOSE_INTENT quant[ao]s? /
cu[áa]nt[ao]s?, the add-detail join, and the 180 self-tests of the 9 published packs (qa-bitcoin-se, qa-ethereum-se left out),
over the public v0.1 60 + those 180 and the 64 Q2 probes, plus the review examples. Normative source for rule v1.2 §1; src/routing/healthGap.ts is their TS port (parity checked).
Usage: python3 -I healthgap_scan_v11.py <boar root> [out.json]
"""
import json, re, sys, glob, collections
root = sys.argv[1]
B = r"(?<![\w])"; E = r"(?![\w])"
def rx(s, flags=re.I): return re.compile(s, flags | re.U)
def bw(alts): return rx(B + "(?:" + alts + ")" + E)

# ---------- dose ----------
DRUG = bw(r"ibuprofen|ibuprofeno|acetaminophen|paracetamol|tylenol|advil|calpol|nurofen|motrin|aspirin|aspirina|dipirona|metamizol|novalgina|amoxicillin|amoxicilina|azithromycin|antibiotics?|antibi[óo]tico|melatonin|benadryl|diphenhydramine|loratadine|cetirizine|antihistamine|loperamide|imodium|omeprazole|ondansetron|dramamine|insulin|insulina|codeine|tramadol|morphine|oxycodone|diazepam|lorazepam|xanax|valium|zolpidem|prednisone|dexamethasone|metformin|warfarin|iron tablets?|vitamin [a-k]\d?|painkillers?|analg[ée]sic[oa]?|rem[ée]dio|medicine|medication|medicamento|medicina")
DOSE_WORD = bw(r"dose|doses|dosage|dosagem|dosis|tablets?|pills?|capsules?|drops|gotas|gotitas|comprimidos?|pastillas?|cucharadas?|colheres?|teaspoons?|spoonfuls?|ml|mg|mcg|µg")
DOSE_INTENT = bw(r"how (?:many|much)|quant[ao]s?|cu[áa]nt[ao]s?|too (?:much|many)|demais|is it (?:safe|ok|okay|too)|max(?:imum)?|m[áa]xim[oa]|can (?:i|she|he|we|they|my \w+) (?:have|take|give)|(?:what time|when) can|again|more|(?:every|per|each|a cada|cada) \d+ ?(?:h|hr|hrs|hours?|horas?|days?|dias?|d[íi]as?)"
                 r"|what dose|dose of|twice|double|by mistake|accidentally|extra|missed|next (?:one|dose)|together")  # v1.1 additions (review)
PATIENT = bw(r"\d+ ?(?:kg|kilos?|lbs?|pounds?|months?|years?|yo|anos|meses|años)|child|kid|baby|toddler|infant|son|daughter|filh[oa]|criança|bebê|hij[oa]|niñ[oa]|bebé")  # v1.1
COOKING = bw(r"recipe|bake|baking|flour|sugar|butter|dough|batter|yeast|cups?|oven|cooking")  # v1.1, no-DRUG branch only
DIGIT = rx(r"\d")
WATER_PURIFY = rx(r"(?:purif\w*|disinfect\w*|treat\w*|sanitiz\w*|make .{0,20}safe to drink|safe to drink|potable|contaminated).{0,60}water|water.{0,60}(?:purif\w*|disinfect\w*|treat\w*|safe to drink|potable|contaminated)", re.I | re.S)
def dose(q):
    if DRUG.search(q): return bool(DOSE_INTENT.search(q) or DOSE_WORD.search(q) or PATIENT.search(q))
    return bool(DOSE_WORD.search(q) and DIGIT.search(q) and DOSE_INTENT.search(q) and not COOKING.search(q) and not WATER_PURIFY.search(q))

# ---------- poison ----------
HAZARD = bw(r"death cap|destroying angel|amanita|cogumelo venenoso|hongo venenoso")  # v1.1: alone-sufficient only these
INGEST = bw(r"ate|eaten|eat|drank|drunk|drink(?:ing)?|swallow\w*|ingest\w*|licked|chewed|took|taken|sniffed|inhal\w*|engoli\w*|bebeu|comeu|tom(?:ou|ei)|trag[óo]|bebi[óo]|comi[óo]"
            r"|got into|chewing|sucked|tomó|ingirió")  # v1.1 additions
SUBSTANCE = bw(r"bleach|detergent|dish soap|laundry pods?|cleaner|cleaning (?:fluid|product)|disinfectant|hand sanitizer|sanitizer|mouthwash|kerosene|petrol|gasoline|diesel|paint|glue|solvent|mushrooms?|wild berries|berries|lily|oleander|foxglove|nutmeg|pills|tablets|medicine|medication|cigarettes?|nicotine|vape (?:juice|liquid)|e-?liquid|alcohol|battery|magnet|coin|silica gel|moth ?balls?|cannabis|edibles?|gummies|cogumelo|alvejante|cloro|lavandina|lej[íi]a|hongos?|setas?"
               r"|antifreeze|ethylene glycol|rat poison|pesticide|insecticide|weed ?killer|paraquat|lamp oil|lighter fluid|paint thinner|turpentine|drain cleaner|oven cleaner|button battery"  # v1.1: moved from HAZARD
               r"|wine|beer|vodka|liquor|spirits|whiske?y|rum|gin|weed|gumm(?:y|ies)|pill|tablet|dishwasher (?:tablet|pod)s?|toilet cleaner|paraffin|white spirit|methanol|rubbing alcohol|isopropyl\w*|nail polish remover|acetone|ammonia|lye|caustic soda|rodenticide|fertili[sz]er|slug pellets|ant bait|essential oils?|eucalyptus oil|tea tree oil|button cell|coin cell|água sanitária|soda cáustica|querosene|gasolina|chumbinho|raticida")  # v1.1 additions
POISON_WORD = bw(r"poison(?:ed|ing|ous)?|toxic|toxicity|overdos\w*|lethal dose|deadly dose|envenen\w*|intoxica\w*|veneno|venenos[oa]|t[óo]xic[oa]")
QUANTITY = bw(r"\d+(?:[.,]\d+)? ?(?:g|mg|ml|grams?|gramas?|cups?|tablets?|pills?|drops?|bottles?|spoons?|teaspoons?|capsules?|comprimidos?|copos?|x[íi]caras?)")
ISTHIS = bw(r"(?:is|are) (?:it|that|this|\d)|how (?:much|many)")
FOOD_POISONING = rx(r"food poisoning")
LETHAL_AMOUNT = bw(r"(?:lethal|deadly|toxic|fatal) (?:dose|amount)")  # v1.1: alone-sufficient (information form)
def poison(q):
    """'event' (A: a deadly mushroom named; B: an ingestion verb + a substance), 'info' (C), or None."""
    if WATER_PURIFY.search(q): return None
    if HAZARD.search(q) or (INGEST.search(q) and SUBSTANCE.search(q)): return "event"
    if (POISON_WORD.search(q) and (INGEST.search(q) or QUANTITY.search(q) or ISTHIS.search(q)) and not FOOD_POISONING.search(q)) or LETHAL_AMOUNT.search(q): return "info"
    return None

# ---------- co ----------
CARBON_MONOXIDE = rx(r"carbon monoxide|mon[óo]xido de carbono")  # never excluded (v1.1)
PPM_HOME = rx(B + r"\d+ ?ppm" + E + r"(?=.{0,80}(?:house|home|room|cabin|garage|basement|rv|boat|tent|indoors|inside|bedroom|apartment|flat))", re.I | re.S)
CO_CS = re.compile(r"(?<![\w])CO(?![\w\d])(?=.{0,40}(?:ppm|alarm|detector|reading|level|monitor|poison|leak|exposure))|(?<![\w])(?:ppm|alarm|detector|reading|level|monitor)s?(?![\w]).{0,30}(?<![\w])CO(?![\w\d])", re.S | re.U)  # v1.1: no "in the house" alternative
CO_EXCLUDE = bw(r"co2|carbon dioxide|chlorine|tds|nitrates?|fluoride|lead|radon|pm ?2[.,]5|particulates?|humidity|colorado")  # v1.1: word-bounded, no "pool"
CO_CITY = re.compile(r",\s*CO(?![\w])", re.U)  # "Denver, CO"
def co(q):
    if CARBON_MONOXIDE.search(q): return True
    return bool((PPM_HOME.search(q) or CO_CS.search(q)) and not CO_EXCLUDE.search(q) and not CO_CITY.search(q))

# ---------- survival ----------
SURVIVAL = rx(r"how (?:long|many (?:hours|days|minutes)) (?:can|could|does|do|will|would) (?:a |an |the |some)?[\w' -]{0,40}?(?:survive|go|last|live|stay alive|hold out)[^?]{0,40}?(?:without (?:water|food|eating|drinking|sleep|oxygen|air|insulin|dialysis)|in (?:cold|freezing|icy|the cold|the snow|the heat|the sun|the desert|\d+ ?°? ?[cf] water|\d+ ?degree))|(?:it'?s|it has|has) been \d+ (?:days|hours) (?:without|since (?:i|she|he|they|we) (?:ate|drank|had|slept))|without (?:water|food) for \d+ (?:days|hours)"
              r"|survive \d+ (?:days|hours) without|die (?:of|from) (?:thirst|dehydration|starvation|hunger)", re.I | re.S)  # v1.1 additions
SURV_EXCLUDE = bw(r"plants?|cactus|cacti|succulents?|trees?|seedlings?|lawn|grass|batter(?:y|ies)|phones?|laptops?|cars?|engines?|startups?|business(?:es)?|compan(?:y|ies)")  # v1.1
def survival(q): return bool(SURVIVAL.search(q) and not SURV_EXCLUDE.search(q))

# ---------- class + precedence + multi-turn ----------
ORDER = ["poison-event", "co", "dose", "poison-info", "survival"]  # review MUST-FIX 4
def classes(q):
    p = poison(q); out = []
    if p == "event": out.append("poison-event")
    if co(q): out.append("co")
    if dose(q): out.append("dose")
    if p == "info": out.append("poison-info")
    if survival(q): out.append("survival")
    return out
def classify1(q):
    c = classes(q)
    if not c: return None
    top = c[0]
    return {"cls": "poison" if top.startswith("poison") else top, "event": top == "poison-event", "all": c}
ctx = open(f"{root}/kiln-local/be-0cfd4a77-cut7/src/routing/context.ts", encoding="utf8").read()
m = re.search(r'const FOLLOW_UP_WORDS = new Set\(\s*\((.*?)\)\.split', ctx, re.S)
FOLLOW_UP_WORDS = set(re.sub(r"\\u([0-9a-fA-F]{4})", lambda u: chr(int(u.group(1), 16)), " ".join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)))).split())
GUARD_EXTRA = set("more have another again dose doses much many too safe next one".split())
def follow_up_only(q):
    w = re.sub(r"[¿¡?!.,;:]", " ", q.lower()).split()
    return 0 < len(w) <= 12 and all(x in FOLLOW_UP_WORDS or x in GUARD_EXTRA for x in w)
def classify(q, turns=()):
    c = classify1(q)
    if c: return {**c, "prev": False}
    adds_detail = bool(turns) and len(re.sub(r"[¿¡?!.,;:]", " ", q.lower()).split()) <= 12 and bool(PATIENT.search(q) or QUANTITY.search(q)) and classify1(turns[-1]) is not None  # v1.2
    if turns and (follow_up_only(q) or adds_detail):
        c = classify1(f"{turns[-1]}. {q}")
        if c: return {**c, "prev": True}
    return None

# ---------- data ----------
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
pub = [(r["id"], r["question"], "v01") for r in jl(f"{root}/boar-eval/bench/v0.1/questions.public.jsonl")]
for d in sorted(d for d in glob.glob(f"{root}/boar-eval/bench/selftest/*/questions.jsonl") if d.split("/")[-2] not in ("qa-bitcoin-se", "qa-ethereum-se")):  # v1.2: published packs only
    pub += [(r["id"], r["question"], "st-" + d.split("/")[-2]) for r in jl(d)]
probes = {}
for f in ["health", "multiturn", "final-probes", "final-probes-mt"]:
    for r in jl(f"{root}/rnd/research/coordinator/arms/numguard/review/{f}.jsonl"): probes[r["id"]] = r
for r in jl(f"{root}/boar-eval/bench/v0.1/questions.public.jsonl"):
    if r["id"] in ("dng-001", "dng-002", "dng-005", "vit-hlt-001", "vit-hlt-002", "vit-hlt-003"): probes[r["id"]] = r
assert len(probes) == 64, len(probes)

# review examples (REVIEW-healthgap.md word-list edits + multi-turn): (text, turns, expected class or None)
REVIEW = [
    ("What dose of amoxicillin for a 10 kg child?", [], "dose"), ("Ibuprofen dose for my 4 year old", [], "dose"),
    ("My son took two doses of Calpol by mistake", [], "dose"), ("She took her warfarin twice today", [], "dose"),
    ("How many teaspoons of baking soda for 2 cups of flour?", [], None), ("How many ml in 3 cups?", [], None),
    ("How many drops of bleach per 1 liter of water to purify it?", [], None),
    ("How much weed killer should I mix per liter?", [], None), ("Best rat poison for the attic?", [], None),
    ("Drain cleaner for a clogged sink?", [], None), ("Is the paint thinner smell bad?", [], None), ("Is there pesticide on strawberries?", [], None),
    ("My toddler drank some wine", [], "poison"), ("My kid got into my weed edibles", [], "poison"),
    ("My son swallowed a dishwasher tablet", [], "poison"), ("Mi hijo tomó lejía", [], "poison"), ("Meu filho bebeu água sanitária", [], "poison"),
    ("What's the lethal dose of caffeine?", [], "poison"), ("Dad took 10 of his heart pills by mistake", [], "poison"),
    ("Took 2 Tylenol PM and a beer, too much?", [], "poison"),
    ("Carbon monoxide alarm by the pool heater is beeping", [], "co"), ("Is the misleading CO reading on my monitor real?", [], "co"),
    ("Moving to CO next month, how is the market in the house segment?", [], None), ("Denver, CO in the house market", [], None),
    ("How long can a car battery last in the cold?", [], None), ("How long can a cactus go without water?", [], None),
    ("Can a person survive 5 days without water?", [], "survival"), ("Can you die of thirst in a day?", [], "survival"),
    ("poison ivy rash on my arm", [], None), ("Are there poison weeds in the garden?", [], None),
    ("What exposure dose for night photography?", [], None), ("What is the CO population of Colorado?", [], None),
    ("Can a startup survive without funding?", [], None),
    ("when can she have more?", ["I gave her Calpol at 9."], "dose"),
    ("when can I visit Lisbon again?", ["I gave her Calpol at 9."], None),
]

out = {"rule": "HEALTHGAP-rule-v1.2", "sets": {"v01": sum(1 for p in pub if p[2] == "v01"), "selftest": sum(1 for p in pub if p[2] != "v01")}, "public_hits": [], "q2": [], "review": []}
for i, q, s in pub:
    c = classify(q)
    if c: out["public_hits"].append({"id": i, "set": s, **c, "q": q[:140]})
for pid, r in probes.items():
    c = classify(r["question"], r.get("turns", []))
    out["q2"].append({"id": pid, "cls": c and c["cls"], "event": bool(c and c["event"]), "prev": bool(c and c["prev"]), "all": c["all"] if c else [], "q": r["question"]})
bad = 0
for t, turns, exp in REVIEW:
    c = classify(t, turns); got = c and c["cls"]; ok = got == exp; bad += not ok
    out["review"].append({"q": t, "turns": turns, "expected": exp, "got": got, "ok": ok})
fires = [r for r in out["q2"] if r["cls"]]
out["counts"] = {"public": len(out["public_hits"]), "v01": sum(1 for h in out["public_hits"] if h["set"] == "v01"), "selftest": sum(1 for h in out["public_hits"] if h["set"] != "v01"),
                 "q2_fires": len(fires), "q2_by_class": dict(collections.Counter(r["cls"] for r in fires)), "q2_event": [r["id"] for r in fires if r["event"]],
                 "review_ok": len(REVIEW) - bad, "review_n": len(REVIEW), "follow_up_words": len(FOLLOW_UP_WORDS)}
print(json.dumps(out["counts"], ensure_ascii=False))
for h in out["public_hits"]: print("PUBLIC", h["id"], h["cls"], h["all"], h["q"][:100])
for r in out["q2"]:
    if r["cls"]: print(f'Q2 {r["id"]:12} {r["cls"]:9} event={int(r["event"])} prev={int(r["prev"])} all={",".join(r["all"])}  {r["q"][:80]}')
for r in out["review"]:
    if not r["ok"]: print("REVIEW-MISMATCH", r)
if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
