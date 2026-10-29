# SC safety cards: independent review (criterion S6)
Reviewer: Opus 5.5 (independent; did not write the cards; did not open `blind/` or `rnd/veil/`), 2026-10-04.
Reviewed: `arms/sc-cards-REVIEW.md`, `wt/cut3-dev/src/routing/safetyCardText.ts` (text), `waterSafety.ts` and `firstAidCards.ts` (wiring only). House style from `compass/exp/co-hazard/REVIEWER.md` + `SOURCES.md` and `compass/exp/first-aid-cards/REVIEWER-DECISIONS-6.md` (region-neutral wording, the more conservative source wins on conflict, every card says whom to contact, short imperative sentences, no unsourced sentences, MedlinePlus A.D.A.M. pages not cited).
Method: every source re-fetched live with WebFetch on 2026-10-04 (URL only, no personal data). Engine code not modified.

## TL;DR
| card | verdict | main changes |
|---|---|---|
| Water safety | **CHANGE** | Altitude: use the lower (EPA) threshold, 3 min above 1,000 m. Add EPA chlorine-smell check and CDC 1% bleach dose (underdosing risk with weaker bleach outside the US). Add "heavy metals, salt" (EPA) to the can't-fix list. Add the CDC "health department" contact. Cloudy → "cloudy, coloured or very cold". Settle/filter moved before the boil step. |
| Snakebite | **CHANGE** | Drop the unsourced "alone… move toward help" sentence, which contradicts WHO immobilisation; replace with "if you are alone, call right away and follow their instructions". Add an explicit early "Call emergency services now", the side position (WHO, NHS), and the CPR line (healthdirect). **Drop "wash the bite"**: Australia's government guidance says not to wash, because venom on the skin identifies the snake. "Tight tourniquet" → "tourniquet" (CDC, NHS, healthdirect). Painkillers: name aspirin/ibuprofen/naproxen only, since NHS allows paracetamol. |

Both cards were verified sentence by sentence; nothing in the proposed text is unsafe apart from the "alone" sentence. The changes close omissions and conflicts. After the edits below, both cards are **approved**, provided the unit tests are updated as noted and re-run.

## Flagged issue 1: boiling at altitude (CDC 6,500 ft vs EPA 5,000 ft)
- Live quotes: CDC "Bring clear water to a rolling boil for 1 minute (at elevations above 6,500 feet, boil for 3 minutes)." EPA "At altitudes above 5,000 feet (1,000 meters), boil water for three minutes."
- EPA's own pair is inconsistent: 5,000 ft is about 1,520 m, not 1,000 m.
- **Decision: use EPA's lowest stated threshold, 1,000 metres (about 3,300 feet).** This is the most conservative figure any official source gives. The only cost of the extra 2 minutes' boiling is fuel, and it avoids printing EPA's mismatched pair. "About 3,300 feet" is our conversion. Readers between 3,300 and 6,500 ft get a stricter instruction than CDC gives, which is safe.

## Flagged issue 2: the "alone" sentence
- "If you are alone, call for help first; if no one can reach you, move calmly and slowly toward help rather than waiting."
- No official health-agency source says this. I searched and found it only in non-agency pages, which are not usable here.
- Its second half contradicts WHO ("keep them from moving around at all") and CDC ("Lay or sit down").
- **Decision: remove it** and use the brief's option (b), supported by CDC ("get medical help right away"), NHS ([NHS quote withheld]) and healthdirect ([healthdirect quote withheld]): "if you are alone, call right away and follow their instructions." Movement decisions are left to the call handler.

## Card 1: water safety. Verdict **CHANGE**
Sentence check of the proposed text: every sentence is supported (CDC-W/EPA-W quotes re-verified verbatim). Gaps found:
- **Underdosing outside the US.** Only the 5–9% bleach dose is given. Household bleach elsewhere is often weaker. CDC's table also has a 1% row ("1 quart/liter: Add 10 drops"; "1 gallon: Add 40 drops"). EPA's smell check ("slight chlorine odor. If it doesn't, repeat the dosage and let stand for another 15 minutes") is a safety net for any strength. Add both.
- **Can't-fix list incomplete.** EPA adds "heavy metals, salts, and most other chemicals". Salt matters after storm-surge flooding of wells.
- **No contact line.** House style says every card says whom to contact. CDC: "Contact your health department for specific advice." No emergency-numbers line is needed (not an acute-harm card); I agree with the engineer.
- **Cloudy-water trigger.** CDC: "cloudy, murky, colored, or very cold"; EPA: "cloudy, colored, or very cold". Use "cloudy, coloured or very cold".
- **Order for a stressed reader.** Settle or filter first, then boil, so the steps read in the order they are done.
- Optional: the fast-path label "Safety facts (CDC)" → "Safety facts (CDC, EPA)", since half the lines are EPA.

**Replacement text for `WATER_SAFETY_EN`** (`WATER_SAFETY_SOURCES_EN` unchanged):
> Use bottled water, or water you stored safely before the emergency, if you have it. If your local water authority has issued a notice, follow its instructions; your local health department can also advise you. Otherwise, boil the water. If it is cloudy, first let it settle or filter it through a clean cloth, paper towel or coffee filter. Bring the clear water to a rolling boil for 1 minute (3 minutes if you are above 1,000 metres, about 3,300 feet), let it cool, and store it in clean containers with tight covers. If you can't boil it, use regular unscented household chlorine bleach. For bleach labelled 5–9% sodium hypochlorite, add 2 drops per litre or 8 drops per gallon; for 1% bleach, add 10 drops per litre or 40 drops per gallon. Use double the amount if the water is cloudy, coloured or very cold. Stir and let it stand for at least 30 minutes before you drink it. It should smell slightly of chlorine; if it doesn't, add the same amount again and wait another 15 minutes. Bleach doesn't work as well as boiling against some germs, such as the parasites Cryptosporidium and Giardia. Boiling and bleach don't remove fuel, toxic chemicals, heavy metals, salt or radioactive material: if the water might contain any of these, don't drink it, and use bottled water instead. Don't drink from a private well that was flooded until it has been disinfected and tested.

| new or changed text | official quote (live 2026-10-04) | source |
|---|---|---|
| "your local health department can also advise you" | "Contact your health department for specific advice." | CDC-W |
| "3 minutes if you are above 1,000 metres, about 3,300 feet" | "At altitudes above 5,000 feet (1,000 meters), boil water for three minutes." | EPA-W (lowest threshold; ft is our conversion) |
| "for 1% bleach, add 10 drops per litre or 40 drops per gallon" | 1% table: "1 quart/liter: Add 10 drops of bleach" · "1 gallon: Add 40 drops of bleach" | CDC-W |
| "cloudy, coloured or very cold" | "If the water is cloudy, murky, colored, or very cold, add double the amount of bleach." · "Double the amount of bleach if the water is cloudy, colored, or very cold." | CDC-W · EPA-W |
| "It should smell slightly of chlorine; if it doesn't, add the same amount again and wait another 15 minutes" | "The water should have a slight chlorine odor. If it doesn't, repeat the dosage and let stand for another 15 minutes before use." | EPA-W |
| "heavy metals, salt" | "Boiling or disinfection will not destroy other contaminants, such as heavy metals, salts, and most other chemicals." | EPA-W |
| "Don't drink from a private well that was flooded until it has been disinfected and tested" | "If you have a well on your property that has been flooded, make sure to disinfect and test the well water after the flood." | EPA-W (the "don't drink until" consequence is our wording, as in the draft) |
| unchanged sentences | as quoted in `sc-cards-REVIEW.md`, re-verified verbatim | CDC-W · EPA-W |

Tests: update any assertion on "6,500" / "2,000 metres" to "1,000 metres". Add asserts for "health department", "1% bleach" and "smell slightly of chlorine".

## Card 2: snakebite (EN). Verdict **CHANGE**
Sentence check of the proposed text:
- CDC-S quotes re-verified verbatim: rings/watches, wash, dressing, mark, ice/water, alcohol/pain relievers, don't wait.
- WHO-S quotes re-verified: immobilise, stretcher, narrow tourniquet/incision/chemicals/suction. WHO-S also says "If possible place them on their side to help protect their airway and breathing."

Issues:
| # | issue | resolution |
|---|---|---|
| 1 | "Alone" sentence is unsourced and contradicts immobilisation. | Replaced (flagged issue 2). |
| 2 | **No explicit "call" in the card body.** The emergency line comes only at the very end, after about ten sentences. | Add "Call emergency services now." as sentence 2 (NHS [NHS quote withheld]; healthdirect [healthdirect quote withheld]; CDC "Seek emergency medical attention as soon as possible"). |
| 3 | **"Wash the bite with soap and water" conflicts by region.** healthdirect (Australian Government) says not to wash the bite area, because venom left on the skin and clothing can help identify the snake ([healthdirect quote withheld]). | Region-neutral rule: drop washing. It has no acute benefit, and the clean dry dressing stays (CDC). |
| 4 | "and anything tight": WHO is silent. | Now sourced by NHS: [NHS quote withheld]. Use "loosen clothing near the bite". Don't say "anything tight", which could be read as removing an Australian pressure bandage. |
| 5 | "tight tourniquet" implies a loose one is fine. | CDC "Do not apply a tourniquet", NHS [NHS quote withheld], healthdirect [healthdirect quote withheld]: use "Do NOT use a tourniquet". |
| 6 | "painkillers such as aspirin or ibuprofen" reads as all painkillers; NHS says [NHS quote withheld]. | Name only the agreed drugs: "don't take aspirin, ibuprofen or naproxen" (CDC list). |
| 7 | No airway or collapse step (dangerous omission). | Add the side position ("on their side if possible", WHO + NHS "recovery position"; compatible with CDC "Lay or sit down"). Add "If the person stops responding or stops breathing normally, start CPR" (healthdirect). This answers brief points 2 and 3. |
| 8 | Brief point 4, photo | Add, distance-guarded: CDC "Take a photograph from a safe distance to identify the snake if possible"; NHS [NHS quote withheld]. The first sentence already says to move away. |
| 9 | Pressure-immobilisation bandage (healthdirect; WHO: neurotoxic snakes only) | Not added. It is region- and species-dependent and needs a technique the card can't teach. "Do NOT use a tourniquet" does not forbid it. |

**Replacement text for `SNAKEBITE_EN`:**
> Snakebite, first aid: move away from the snake and don't try to catch or kill it. Call emergency services now; if you are alone, call right away and follow their instructions. Keep the person still and calm, lying down, on their side if possible, and stop them from moving around at all; carry them on a makeshift stretcher if you can, and get them to medical care without delay, for antivenom: don't wait for symptoms. Take off rings, watches and bracelets, and loosen clothing near the bite, before swelling starts. Cover the bite with a clean, dry dressing. Mark the edge of the swelling on the skin and write down the time. Do NOT use a tourniquet, do NOT cut the wound, and do NOT suck the venom or put chemicals on it. Don't put ice on it or soak it in water. Don't drink alcohol, and don't take aspirin, ibuprofen or naproxen. If you can do it safely from a distance, take a photo of the snake to help identify it. If the person stops responding or stops breathing normally, start CPR.

**Replacement text for `SNAKEBITE_SOURCES_EN`:**
> Sources: WHO, questions and answers on snakebite envenoming (2019); CDC NIOSH, Venomous Snakes at Work; NHS, Snake bites; healthdirect Australia, Snake bites.

The emergency-numbers line stays appended after it.

| new or changed text | official quote (live 2026-10-04) | source |
|---|---|---|
| "Call emergency services now" | [NHS quote withheld] · [healthdirect quote withheld] · "Seek emergency medical attention as soon as possible" | NHS-S · HD-S · CDC-S |
| "if you are alone, call right away and follow their instructions" | "Do not wait for symptoms to appear; get medical help right away" | CDC-S (brief option b) |
| "lying down, on their side if possible" | "If possible place them on their side to help protect their airway and breathing." · "lie in the recovery position if you can" · "Lay or sit down with the bite in a neutral position of comfort." | WHO-S · NHS-S · CDC-S |
| "Take off rings, watches and bracelets, and loosen clothing near the bite, before swelling starts" | "Remove rings and watches before swelling starts" · "take off any jewellery and loosen clothes near the bite" | CDC-S · NHS-S |
| "Do NOT use a tourniquet" | "Do not apply a tourniquet, electric shock, or folk therapies." · [healthdirect quote withheld] | CDC-S · HD-S |
| "don't take aspirin, ibuprofen or naproxen" | "Do not drink alcohol as a painkiller or take pain relievers (such as, aspirin, ibuprofen, naproxen)." · "do not take aspirin or ibuprofen, as they can make bleeding worse" | CDC-S · NHS-S |
| "take a photo of the snake…" | "Take a photograph from a safe distance to identify the snake if possible" | CDC-S |
| "start CPR" | [healthdirect quote withheld] | HD-S |
| (removed) "Wash the bite with soap and water" | [healthdirect quote withheld] | HD-S (conflicts with CDC-S; dropped as region-neutral) |
| unchanged sentences | WHO-S immobilise/stretcher/incision/suction/chemicals; CDC-S dressing, mark and time, ice/water, don't wait | WHO-S · CDC-S |

**Brief point 1 (unit-test guard):** confirmed. "Rings", "watch" and "ice" are now sourced, so the EN test can drop them from the forbidden list. Keep forbidding "immobiliz…" and "heart" (heart-level positioning is contested). Add forbidden "wash" (region conflict) and "tight tourniquet". Add required "Call emergency services", "on their side" and "CPR". PT/ES cards are out of scope and unchanged. Note for later: their "torniquete apertado" has the same "tight tourniquet" issue as row 5.

## Sources (all fetched live with WebFetch on 2026-10-04; official health agencies only)
| key | page | URL | page date shown | retrieved |
|---|---|---|---|---|
| CDC-W | CDC, How to Make Water Safe in an Emergency | https://www.cdc.gov/water-emergency/about/index.html | last updated Sept. 19, 2024 | 2026-10-04 |
| EPA-W | US EPA, Emergency Disinfection of Drinking Water | https://www.epa.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water | last updated February 24, 2026 | 2026-10-04 |
| WHO-S | WHO, Questions and answers: Snakebite envenoming | https://www.who.int/news-room/questions-and-answers/item/snakebite-envenoming | 20 November 2019 | 2026-10-04 |
| CDC-S | CDC NIOSH, Venomous Snakes at Work | https://www.cdc.gov/niosh/outdoor-workers/about/venomous-snakes.html | updated/reviewed September 23, 2026 | 2026-10-04 |
| NHS-S | NHS, Snake bites | https://www.nhs.uk/conditions/snake-bites/ | last reviewed 17 July 2026 | 2026-10-04 |
| HD-S | healthdirect (Australian Government), Snake bites | https://www.healthdirect.gov.au/snake-bites | last reviewed October 2024 | 2026-10-04 |

Not used:
- MedlinePlus: the snakebite first-aid article is A.D.A.M.-licensed. Under REVIEWER-DECISIONS-6 `r6-medlineplus`, those rows can't be cited, so the page was not fetched.
- https://medlineplus.gov/snakebites.html returned 404 on 2026-10-04.
- Non-agency pages (Mayo Clinic, Red Cross, commercial sites) surfaced by a search for the "alone" sentence; none was used.

Licence: CDC, EPA and NIOSH texts are US federal works (public domain). NHS text is under the Open Government Licence v3.0, but NHS wording is not redistributed in this release. healthdirect content is © Healthdirect Australia; it is used only as the basis for one paraphrased instruction and one omission, with no text reproduced in the card, and its wording is withheld from this review (v1.1.2).

AI-reviewed, not clinically reviewed.
