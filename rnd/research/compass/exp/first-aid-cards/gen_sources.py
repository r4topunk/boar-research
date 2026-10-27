#!/usr/bin/env python3
"""SOURCES.md from cards.json (which source each card cites, verbatim quotes, flags). Run after build_cards.py."""
import json
D = json.load(open("cards.json")); S = D["sources"]; use = {}
for c in D["cards"]:
    for s in c["langs"]["en"]["steps"] + [c["langs"]["en"]["call"]]:
        for cid in s["cites"]: use.setdefault(cid, set()).add(c["id"])
L = ["# First-aid cards: sources (Compass, 2026-10-03)",
     f"TL;DR: {len(S)} source rows; the cards cite {len(use)} of them. Every quote is verbatim from the official page. New rows were fetched 2026-10-03 and checked as exact substrings of the saved page text, except † (CDC blocks direct download; quote via a summarising fetch, recheck by eye); round 5 has no † rows. FA-* rows were fetched 2026-10-02 the same way (../fa-cards/sources.md). The full verification log, with alternatives and conflicts, is SOURCES.raw.md. A '…' inside a quote marks words left out of the page text; nothing a card relies on is left out.",
     "", "Licences: NHS = OGL v3.0 (our own wording; the card must not present itself as NHS content; the attribution line is in the engine 'sources' string). CDC, NOAA/NWS = US public domain. MedlinePlus encyclopedia (A.D.A.M.), Mexico Secretaría de Salud/STCONAPRA/Morelos/Guanajuato = copyright: facts only. All others (St John, British Red Cross, AAP, CAPT, healthdirect, Saudi MOH, Brazil MS/SES-SP, St John NZ) = copyright: facts only, no copied wording.",
     "", "| id | used by | source | quote | flag |", "|---|---|---|---|---|"]
for k, v in S.items():
    L.append(f"| {k} | {', '.join(sorted(use.get(k, []))) or '(not cited)'} | [{v['org']}]({v['url']}) | \"{v['quote']}\" | {v['flag']} |")
L += ["", "## Conflicts and gaps (each one is a decision in REVIEW.md)",
      "- Honey for a swallowed button battery (poison.org yes; UK no) → left out.",
      "- Scorpion: ice (CDC) vs warm compress, no ice (Brazil) → left out; 'keep still' has no official source → left out.",
      "- Drowning: 5 initial breaths (UK) vs 2 (Saudi MOH) → 5; 'don't hold upside down' has no official drowning source → 'don't try to get water out' instead; hospital is required only after rescue breaths/CPR (AAP).",
      "- Infant chest thrusts: two fingers (NHS, BRC) vs two thumbs (St John UK) → two fingers.",
      "- 'Don't give insulin': single source (St John NZ).",
      "- Coin: the regional NHS page sends every swallowed coin to A&E; no national nhs.uk page exists.",
      "- Jellyfish vinegar only in tropical box-jellyfish areas; not on bluebottles (healthdirect).",
      "- † CDC rows (hypoglycemia 15-15, seizure hold-down, CO call) need a by-eye recheck.",
      "", "## Round 2 conflicts and gaps (REVIEW-2.md; full log SOURCES.raw-2.md, 163/163 quotes exact, no † rows)",
      "- Aspirin: 'chew' + 'not under 16' only on St John UK (BRC: chew); NHS/BHF: 300 mg + allergy only; country variation not verified (AHA blocked) → default card gives NO dose; dosing is alternative B for r4to.",
      "- Head injury vomiting tier: NHS England 111 vs healthdirect/CDC emergency (repeated) vs BRC 999 (any).",
      "- Unresponsive + possible neck injury: St John (side only if the airway can't be kept open) vs BRC (always side) → card follows St John.",
      "- Tsunami: leave after any quake on the beach (NWS) vs 'strong or long' vs 'hard to stand' (Chile); vertical evacuation = upper floors of a sturdy building (NSW) vs ≥ 8 floors, second option (Chile).",
      "- Hypothermia: 'don't make them walk' NOT in any allowed source (NOLS/Mayo only) → 'handle them gently' (CDC); CDC allows an electric blanket on the core (left out); CPR line only from CDC.",
      "", "## Round 3 conflicts and gaps (REVIEW-3.md; full log SOURCES.raw-3.md, 244/244 quotes exact, no † rows)",
      "- Burn: cool (NHS, SJA, healthdirect) vs cold (BRC) water; any burned child → doctor (BRC, PBB) vs NHS 111 'if not sure'; no cling film on the face (healthdirect only).",
      "- Frostbite: water temperature figure: SJA ~40 °C, healthdirect 40–42 °C; WMS 37–39 °C not fetchable → card says 'warm, not hot'. Refreezing: healthdirect only.",
      "- Heatstroke: fluids only by healthdirect ('sips … if conscious'); cold packs armpits/neck (NHS, SJA) vs cheeks/palms/soles (healthdirect); NHS heat exhaustion no longer has 'feet raised'.",
      "- Nosebleed: A&E after 10–15 min (NHS) vs 999 after 30 min (SJA); blood thinners = GP tier (NHS); ice on the nose: weak evidence (NHS) → left out.",
      "- Earthquake: 'stay in the car' = CDC/ARC (not Ready.gov); 'don't move about if trapped' not found → left out; USGS 403.",
      "- Animal bite: any broken skin → medical advice (healthdirect) vs NHS criteria; face bite = ED (healthdirect) vs 111 (NHS); monkeys only in the CDC Yellow Book (clinician text).",
      "", "## Round 4 conflicts and gaps (REVIEW-4.md; full log SOURCES.raw-4.md, 233/233 quotes exact, no † rows)",
      "- Bleeding: soaked dressing remove-and-replace (SJA, BRC) vs add on top (NHS); raise the wound (NHS only); tourniquet per RCUK 2025, improvised only on the 999 handler's instruction (SJA).",
      "- Stroke: FAST (UK) vs BE FAST (CDC) vs RÁPIDO (CDC ES); signs that stopped: 999 (NHS) vs tell a health care team (CDC, TIA); no food/drink = SJA only; 'no aspirin' in no source.",
      "- Anaphylaxis: legs raised optional (NHS) vs raised (SJA); CPR line only healthdirect; NHS page review overdue.",
      "- Chemical in the eye: tier = strong chemicals only (NHS) vs any chemical splash (SJA); lenses out unless the eye is badly damaged (healthdirect).",
      "- Electric: downed-line distance 6 m (healthdirect) vs 35 ft ≈ 10.7 m (American Red Cross); the old 18 m is in no source → card says 'at least 10 metres'.",
      "- Altitude: descend if worse or not better after 1 day (NHS) vs worse despite rest (CDC Yellow Book, clinician text).",
      "- Sea creatures: hot water ≥ 30 min (NHS) vs 45 °C up to 90 min (healthdirect fish/stingray); stonefish spine stays in (healthdirect) vs remove spines (NHS).",
      "- Tick: DIRECT CONTRADICTION: tweezers, never freeze (CDC, NHS, SJA) vs freeze with ether, never tweezers (healthdirect, ASCIA) → UK/US method + an Australia line.",
      "- Heat exhaustion: 'lie down, legs raised' only SJA (not NHS) → left out.",
      "", "## Round 5 conflicts and gaps (REVIEW-5.md; full log SOURCES.raw-5.md, 55/55 quotes exact, no † rows)",
      "- Rip current: float first (NOAA Ocean Today; parallel only 'if you're a good swimmer') vs swim out first (NWS); back to shore at an angle (NWS, NOS) vs with the waves (NOAA OT); bystander never enters (NOAA OT) vs only with a flotation device (NWS) → card: don't swim out yourself.",
      "- Rip current: RNLI/USLA/SLSA blocked or 404 → NOAA/NWS only; no PT official rip page fetchable; Bombeiros 193 only on the MS scorpion page's general emergency line; CPR line only via the drowning card's BRC row.",
      "- Scorpion (adult): ice (CDC/NIOSH, MedlinePlus) vs warm compress + no ice (SES-SP) → neither on the default card; ice = ALTERNATIVE for r4to.",
      "- Scorpion (adult): every sting → nearest health service quickly (SES-SP, MS, Morelos, Guanajuato) vs 'most North American stings need no treatment' (MedlinePlus) → card follows Brazil/Mexico.",
      "- Scorpion (adult): diphenhydramine (MedlinePlus) and the antivenom table (MS) left out; CONAPRA's 'no frío local' is snakebite-only; Mayo Clinic 403."]
open("SOURCES.md", "w").write("\n".join(L) + "\n")
print(len(S), "sources;", len(use), "cited")
