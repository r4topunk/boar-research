#!/usr/bin/env python3
"""COVERAGE-MAP deliverable 1 (0 LLM): coverage.json/.md = every MAIN 97 item with its RAG-FUNNEL K1/K3 stage, domain, and for the K1-S1 items
(fact in no installed K1 pack; 45) + the 5 unkeyed v0.1 items: question, key fact (<= 12 words), corpus type, FOUND/NOT FOUND per pack on disk.
Evidence: coverage-pool.json (lexical pack rule over 20 pack files), cm-oracle.json (self-test quote in its own source article), hand reads (HAND below).
Usage: python3 -I build_coverage.py"""
import json, glob
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; C = A + "coverage-map/"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
FUN = json.load(open(CO + "ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
POOL = json.load(open(C + "aggregates/coverage-pool.json"))["items"]
CMO = json.load(open(C + "aggregates/cm-oracle.json"))
DOM = {"crypto": "crypto/ethereum", "humanities": "humanities", "history-culture": "humanities", "science-tech": "science", "nature": "science",
       "health": "health", "firstaid": "health", "country": "law/ref", "place-other": "law/ref", "travel": "travel", "cooking": "cooking", "money": "money"}
K1 = {"boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en"}
# hand reads of the v0.1 S1 items and the unkeyed v0.1 items (pack FTS read-only, 2026-10-22; FACT-REACH-2026-10-21 where cited)
HAND = {
 "vit-hum-001": ("Mozi's jian ai: impartial care for all, grounded in mutual benefit", "humanities", "full English Wikipedia (Mozi, Mohism)",
                 "FOUND top100k ('Heaven' chunk: Mohist 'universal love', jian'ai; no 'Mozi' article in top100k) = partial; full enwiki has 'Mozi' + 'Mohism' (not on disk)"),
 "vit-hum-006": ("Harm principle: power over others only to prevent harm to others", "humanities", "full English Wikipedia (Harm principle, J. S. Mill); Gutenberg PD 'On Liberty'",
                 "FOUND top100k ('John Stuart Mill': On Liberty, harm/opinion passage); objections need 'Harm principle' article (full enwiki, not on disk)"),
 "vit-sci-002": ("Japan ~336/km2 vs Germany ~235/km2; Japan ~40 % denser", "law/ref", "Factbook (CC0) + English Wikipedia",
                 "FOUND top100k ('Demographics of Japan': 336/km2; lexical top hit was a spurious S. Korea chunk); factbook K3 = area + population only (derivable)"),
 "vit-sci-003": ("83 s = 1300/30 prefill + 400/10 decode (arithmetic)", "science", "none: computation from the question's own numbers",
                 "NOT A COVERAGE GAP (no fact to store; reasoning item)"),
 "vit-trv-004": ("Paris-Rome round trip on foot ~2,700-2,900 km", "travel", "route distance (OSM routing, ODbL: not in the permitted list) / derivable from Via Francigena",
                 "NOT FOUND in any pack on disk (all lexical hits spurious; no 'Via Francigena' in top100k or Wikivoyage) -> NOT COVERABLE as a stated fact"),
 "lan-ref-004": ("Iceland area ~103,000 km2", "law/ref", "Factbook (CC0)", "FOUND factbook (K3; chunk 7032 'Area 103,000 sq km', hand label Y); top100k 'Iceland' (100,000 km2)"),
 "trv-002": ("Brazil: 127/220 V, type N (and C) plugs", "travel", "Wikivoyage (K0)", "FOUND boar-wikivoyage-en 'Brazil' (volts + plug, FTS)"),
 "trv-004": ("Lisbon airport -> centre: Metro Red Line, Aerobus, taxi", "travel", "Wikivoyage (K0)", "FOUND boar-wikivoyage-en 'Lisbon Airport' (Metro Red Line terminates at the airport)"),
 "dng-001": ("Snakebite: immobilise, keep calm, evacuate; no cutting/suction/tourniquet", "health", "first-aid manuals PD (K3 firstaid)", "FOUND boar-firstaid-en (Wilderness First Aid; ATP 4-02.11 ch. 16)"),
 "dng-002": ("Hypothermia: warm gradually, dry, insulate, evacuate", "health", "first-aid manuals PD (K3 firstaid) / MedlinePlus", "FOUND boar-firstaid-en (ATP 4-02.11 ch. 8; 'Hypothermia'), boar-medlineplus-en"),
 "dng-005": ("Boil 1 min (rolling) or 2 drops unscented bleach per litre", "health", "Ready.gov PD (K3 firstaid) / preparedness", "FOUND boar-firstaid-en 'Water (Ready.gov)'; boar-preparedness-en 'Portable water purification'"),
}
def short(s, n=12):
    w = s.split(); return " ".join(w[:n]) + (" ..." if len(w) > n else "")
items = {}
for i in MAIN:
    q = Q[i]; f = FUN.get(i); p = POOL.get(i)
    e = dict(set="v0.1" if not i.startswith("st-") else "cm", question=q["question"], tag=f["tag"] if f else None,
             domain=DOM.get(f["tag"]) if f else HAND[i][1], keyed=f is not None, K1=f["K1"]["vstage"] if f else None, K3=f["K3"]["vstage"] if f else None,
             packs_lexical=sorted(p["packs"]) if p else [])
    s1 = f is not None and f["K1"]["vstage"] == "S1"
    if i in HAND:
        kf, dom, ct, fnd = HAND[i]; e.update(key_fact=kf, domain=dom, corpus_type=ct, found=fnd, s1_K1=s1)
    elif i in CMO:
        o = CMO[i]; pk = o["pack"]
        e.update(key_fact=short(o["facts"][0]), corpus_type=f"Stack Exchange {pk[3:-3]} (CC BY-SA; built: {pk})", s1_K1=s1,
                 found=f"FOUND {pk} (own source article {o['article_id']}, quotes {sum(o['quote_found'])}/{len(o['quote_found'])}); lexical pool rule " + ("FOUND" if pk in p["packs"] else "missed"))
    else: e["s1_K1"] = s1
    items[i] = e
S1 = [i for i in MAIN if items[i]["s1_K1"]]
json.dump(dict(note=__doc__, n_main=len(MAIN), s1_K1=S1, items=items), open(C + "coverage.json", "w"), indent=1)
L = ["# COVERAGE (2026-10-22): the 45 MAIN items whose key fact is in no installed K1 pack (RAG-FUNNEL K1 S1), + the 5 unkeyed v0.1 items", "",
     "0 LLM. Key fact from the gold/rubric (v0.1) or in_pack_facts (self-tests), agent-read. FOUND = hand read of pack FTS (v0.1) or quote in the item's own source article (cm). Full per-item JSON: coverage.json (all 97).", "",
     "| id | domain | question (dev) | key fact (<= 12 words) | corpus type | on disk |", "|---|---|---|---|---|---|"]
for i in S1 + [x for x in MAIN if not items[x]["keyed"]]:
    e = items[i]; L.append(f"| {i} | {e['domain']} | {short(e['question'], 18)} | {e.get('key_fact','')} | {e.get('corpus_type','')} | {e.get('found','')} |")
open(C + "coverage.md", "w").write("\n".join(L) + "\n")
print(len(S1), sum(1 for i in MAIN if not items[i]["keyed"]))
