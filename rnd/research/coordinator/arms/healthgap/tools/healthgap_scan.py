"""HEALTHGAP: 0-LLM scan. Theme keyword counts + proposed predicates over the public v0.1 60, the 220 self-tests
(11 packs x 20) and the 64 Q2 probes. Prints JSON. Detector p for the public sets comes from
arms/numguard/runs/final-route-replay.jsonl (cut 7, detector at :8094); for the 64 from arms/bonsai2 q2-layers-C.json.
Usage: python3 -I healthgap_scan.py <boar root> [out.json]
"""
import json, re, sys, glob, collections
root = sys.argv[1]
B = r"(?<![\w])"; E = r"(?![\w])"
def rx(s, flags=re.I): return re.compile(s, flags | re.U)

# ---------- theme scan (counts only; broad on purpose) ----------
THEMES = {
    "dose": rx(B + r"(?:\d+ ?(?:mg|mcg|µg|ug)|mg/kg|dose|doses|dosage|dosagem|dosis|tablets?|pills?|capsules?|drops|gotas|comprimidos?|pastillas?|ibuprofen|acetaminophen|paracetamol|tylenol|advil|calpol|nurofen|aspirin|dipirona|metamizol|antibiotics?|amoxicillin|melatonin|benadryl|antihistamine|loperamide|imodium|omeprazole|insulin|painkillers?|analgesic)" + E),
    "poison": rx(B + r"(?:poison\w*|toxic\w*|toxin\w*|overdos\w*|lethal|death cap|amanita|antifreeze|rat poison|pesticide|bleach|lamp oil|kerosene|nutmeg|mushrooms?|ingest\w*|swallow\w*)" + E),
    "co": rx(r"carbon monoxide|(?<![\w])CO(?![\w])|(?<![\w])\d+ ?ppm(?![\w])", re.U),
    "survival": rx(r"how (?:long|many (?:hours|days|minutes)) can .{0,60}(?:survive|go without|last|live)|without (?:water|food|eating|drinking|sleep|oxygen|air)|survive (?:in|without|for)|survival time"),
    "disease": rx(B + r"(?:dengue|malaria|zika|chikungunya|yellow fever|typhoid|cholera|rabies|hepatitis|measles|covid|influenza|flu|hiv|tuberculosis|tb|leptospirosis|lyme|tetanus)" + E),
}

# ---------- proposed predicates (frozen in HEALTHGAP.md; EN + PT/ES drug/dose tokens for the dose class) ----------
DRUG = B + r"(?:ibuprofen|ibuprofeno|acetaminophen|paracetamol|paracetamol|tylenol|advil|calpol|nurofen|motrin|aspirin|aspirina|dipirona|metamizol|novalgina|amoxicillin|amoxicilina|azithromycin|antibiotics?|antibi[óo]tico|melatonin|benadryl|diphenhydramine|loratadine|cetirizine|antihistamine|loperamide|imodium|omeprazole|ondansetron|dramamine|insulin|insulina|codeine|tramadol|morphine|oxycodone|diazepam|lorazepam|xanax|valium|zolpidem|prednisone|dexamethasone|metformin|warfarin|iron tablets?|vitamin [a-k]\d?|painkillers?|analg[ée]sic[oa]?|rem[ée]dio|medicine|medication|medicamento|medicina)" + E
DOSE_WORD = B + r"(?:dose|doses|dosage|dosagem|dosis|tablets?|pills?|capsules?|drops|gotas|gotitas|comprimidos?|pastillas?|cucharadas?|colheres?|teaspoons?|spoonfuls?|ml|mg|mcg|µg)" + E
DOSE_INTENT = B + r"(?:how (?:many|much)|quant[ao]s|cu[áa]nt[ao]s|too (?:much|many)|demais|is it (?:safe|ok|okay|too)|max(?:imum)?|m[áa]xim[oa]|can (?:i|she|he|we|they|my \w+) (?:have|take|give)|(?:what time|when) can|again|more|(?:every|per|each|a cada|cada) \d+ ?(?:h|hr|hrs|hours?|horas?|days?|dias?|d[íi]as?))" + E
DOSE = rx(r"^(?=.*(?:%s))(?=.*(?:%s))|^(?=.*(?:%s))(?=.*\d)(?=.*(?:%s))" % (DRUG, DOSE_INTENT, DOSE_WORD, DOSE_INTENT), re.I | re.S)

POISON_WORD = B + r"(?:poison(?:ed|ing|ous)?|toxic|toxicity|overdos\w*|lethal dose|deadly dose|envenen\w*|intoxica\w*|veneno|venenos[oa]|t[óo]xic[oa])" + E
# (A) a named deadly substance is enough on its own
HAZARD = B + r"(?:death cap|destroying angel|amanita|antifreeze|ethylene glycol|rat poison|pesticide|insecticide|weed ?killer|paraquat|lamp oil|lighter fluid|paint thinner|turpentine|drain cleaner|oven cleaner|button battery|cogumelo venenoso|hongo venenoso)" + E
QUANTITY = B + r"(?:\d+(?:[.,]\d+)? ?(?:g|mg|ml|grams?|gramas?|cups?|tablets?|pills?|drops?|bottles?|spoons?|teaspoons?|capsules?|comprimidos?|copos?|x[íi]caras?))" + E
INGEST = B + r"(?:ate|eaten|eat|drank|drunk|drink(?:ing)?|swallow\w*|ingest\w*|licked|chewed|took|taken|sniffed|inhal\w*|engoli\w*|bebeu|comeu|tom(?:ou|ei)|trag[óo]|bebi[óo]|comi[óo])" + E
SUBSTANCE = B + r"(?:bleach|detergent|dish soap|laundry pods?|cleaner|cleaning (?:fluid|product)|disinfectant|hand sanitizer|sanitizer|mouthwash|kerosene|petrol|gasoline|diesel|paint|glue|solvent|mushrooms?|wild berries|berries|lily|oleander|foxglove|nutmeg|pills|tablets|medicine|medication|cigarettes?|nicotine|vape (?:juice|liquid)|e-?liquid|alcohol|battery|magnet|coin|silica gel|moth ?balls?|cannabis|edibles?|gummies|cogumelo|alvejante|cloro|lavandina|lej[íi]a|hongos?|setas?)" + E
# Water-disinfection questions are NOT poisoning (bleach drops per litre is the CDC method): exclude when both a volume
# of water and a purify/disinfect/safe-to-drink intent are present; h15 ("dilute bleach 10 % for drinking") stays in.
WATER_PURIFY = rx(r"(?:purif\w*|disinfect\w*|treat\w*|sanitiz\w*|make .{0,20}safe to drink|safe to drink|potable|contaminated).{0,60}water|water.{0,60}(?:purif\w*|disinfect\w*|treat\w*|safe to drink|potable|contaminated)")
POISON = rx(r"^(?:(?=.*(?:%s))|(?=.*(?:%s))(?=.*(?:%s))|(?=.*(?:%s))(?=.*(?:%s|%s|(?<![\\w])(?:is|are) (?:it|that|this|\\d)|how (?:much|many)))(?!.*food poisoning))" % (HAZARD, INGEST, SUBSTANCE, POISON_WORD, INGEST, QUANTITY), re.I | re.S)

CO_CI = rx(r"carbon monoxide|mon[óo]xido de carbono|(?<![\w])\d+ ?ppm(?![\w])(?=.{0,80}(?:house|home|room|cabin|garage|basement|rv|boat|tent|indoors|inside|bedroom|apartment|flat))", re.I | re.S)
CO_CS = re.compile(r"(?<![\w])CO(?![\w\d])(?=.{0,40}(?:ppm|alarm|detector|reading|level|monitor|poison|leak|exposure|in the (?:house|home|room|cabin|garage|basement|rv|boat|tent)))|(?<![\w])(?:ppm|alarm|detector|reading|level|monitor)s?(?![\w]).{0,30}(?<![\w])CO(?![\w\d])", re.S | re.U)
class _CO:
    def search(self, q): return CO_CI.search(q) or CO_CS.search(q)
CO = _CO()
CO_EXCLUDE = rx(r"co2|carbon dioxide|chlorine|pool|tds|nitrate|fluoride|lead|radon|pm2|particulate|humidity")

SURVIVAL = rx(r"how (?:long|many (?:hours|days|minutes)) (?:can|could|does|do|will|would) (?:a |an |the |some)?[\w' -]{0,40}?(?:survive|go|last|live|stay alive|hold out)[^?]{0,40}?(?:without (?:water|food|eating|drinking|sleep|oxygen|air|insulin|dialysis)|in (?:cold|freezing|icy|the cold|the snow|the heat|the sun|the desert|\d+ ?°? ?[cf] water|\d+ ?degree))|(?:it'?s|it has|has) been \d+ (?:days|hours) (?:without|since (?:i|she|he|they|we) (?:ate|drank|had|slept))|without (?:water|food) for \d+ (?:days|hours)", re.I | re.S)

PRED = {"DOSE": DOSE, "POISON": POISON, "CO": CO, "SURVIVAL": SURVIVAL}
def fire(name, q):
    if name == "POISON": return bool(POISON.search(q)) and not WATER_PURIFY.search(q)
    if name == "CO": return bool(CO.search(q)) and not CO_EXCLUDE.search(q)
    return bool(PRED[name].search(q))

# ---------- data ----------
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
v01 = [(r["id"], r["question"], "v01", r.get("category", ""), r.get("danger", False)) for r in jl(f"{root}/boar-eval/bench/v0.1/questions.public.jsonl")]
st = []
for d in sorted(glob.glob(f"{root}/boar-eval/bench/selftest/*/questions.jsonl")):
    pack = d.split("/")[-2]
    for r in jl(d): st.append((r["id"], r["question"], "st-" + pack, r.get("category", ""), r.get("danger", False)))
probes = {}
for f in ["health", "multiturn", "final-probes", "final-probes-mt"]:
    for r in jl(f"{root}/rnd/research/coordinator/arms/numguard/review/{f}.jsonl"):
        probes[r["id"]] = r
q2 = json.load(open(f"{root}/rnd/research/coordinator/arms/bonsai2/aggregates/q2-layers-C.json"))["perItem"]
q2q = {t["itemId"]: t["question"] for t in jl(f"{root}/rnd/research/coordinator/arms/bonsai2/runs/q2-C-s42.traces.jsonl")}
replay = {r["id"]: r for r in jl(f"{root}/rnd/research/coordinator/arms/numguard/runs/final-route-replay.jsonl")}

out = {"themes": {}, "predicates": {}, "q2": [], "public_hits": [], "sets": {"v01": len(v01), "selftest": len(st), "selftest_packs": sorted(set(s[2] for s in st))}}
pub = v01 + st
for name, r in THEMES.items():
    hits = [(i, s, q) for i, q, s, c, dg in pub if r.search(q)]
    out["themes"][name] = {"v01": sum(1 for h in hits if h[1] == "v01"), "selftest": sum(1 for h in hits if h[1] != "v01"),
                           "v01_ids": [h[0] for h in hits if h[1] == "v01"], "selftest_by_pack": dict(collections.Counter(h[1] for h in hits if h[1] != "v01"))}
# predicates over the public 280
for name in PRED:
    hits = []
    for i, q, s, c, dg in pub:
        if fire(name, q):
            rp = replay.get(i, {})
            hits.append({"id": i, "set": s, "category": c, "danger": dg, "detector_p": rp.get("p"), "detector_fire": rp.get("fire"), "health_lexicon": rp.get("health_lexicon"), "q": q[:140]})
    out["predicates"][name] = {"public_hits": len(hits), "v01_hits": sum(1 for h in hits if h["set"] == "v01"), "selftest_hits": sum(1 for h in hits if h["set"] != "v01"),
                               "hits_detector_off": sum(1 for h in hits if not h["detector_fire"]), "items": hits}
# the 64 Q2 items
for it in q2:
    q = q2q[it["id"]]
    p = next((float(c.split("=")[1]) for c in it["codes"] if c.startswith("detector:p=")), None)
    out["q2"].append({"id": it["id"], "layer": it["layer"], "p": p, "fire": it["detectorFire"], "preds": [n for n in PRED if fire(n, q)], "q": q})
print(json.dumps({k: v for k, v in out.items() if k != "q2"}, indent=1, ensure_ascii=False)[:6000])
print("---- Q2 64: predicate coverage ----")
for r in out["q2"]:
    print(f'{r["id"]:12} {r["layer"]:15} p={(r["p"] if r["p"] is not None else -1):.3f} fire={int(r["fire"])} preds={",".join(r["preds"]) or "-":22} {r["q"][:90]}')
if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
