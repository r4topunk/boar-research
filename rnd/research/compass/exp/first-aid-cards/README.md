# First-aid cards draft (Compass, 2026-10-03): DRAFT, NOT FOR SHIPPING
TL;DR: 10 short imperative cards in EN, PT-BR and ES, each ending with when to call emergency services. Every step cites a verbatim quote from an official source (49 rows; NHS, CDC, AAP, British Red Cross, St John UK/NSW/NZ, CAPT, healthdirect, Brazil MS/SES-SP, Saudi MOH). Every card is clean under safety rules v0.8.2: 0 unsafe and 0 review in 30 card-language texts, co-leave-and-call included, and 8/8 deliberately broken copies are caught. **Nothing ships without r4to's sign-off on the wording (REVIEW.md), a clinical review and native PT/ES review.**

```sh
python3 build_cards.py && python3 check_cards.py && python3 gen_sources.py   # cards.json, conditionCards.v1.json, REVIEW.md, SOURCES.md
node triggers.proposed.mjs     # proposed engine trigger regexes, self-test 24/24
node fp_check.mjs              # the same triggers on v0.1 + chat-slice v0/v1 (dev): 6 fires, all genuine
```

| card | covers |
|---|---|
| co | saf-011; the requested CO card |
| drowning | vit-loc1-026, vit-hm2-017 |
| jellyfish | vit-hm2-011, vit-hm3-014 |
| seizure | vit-hm3-049 |
| hypoglycemia | vit-hm2-021 |
| scorpion (child) | requested; Sonar's repro set; chat-slice v1-031 |
| choking (child over 1 year) | requested |
| chokinginfant (under 1 year) | requested; new engine key |
| battery (button battery, coin, magnet) | requested |
| beesting + anaphylaxis escalation | Sonar (b) |

Files:
- `cards.json`: the cards with cited steps.
- `conditionCards.v1.json`: Sonar's engine schema `{cards: {key: {en, pt, es, sources, status}}}`. The 10 cards here are `draft-vetted`; the other 17 keys are kept from the placeholder and marked `placeholder (unvetted)`.
- `REVIEW.md`: the sign-off sheet, with per-card decisions.
- `SOURCES.md` / `SOURCES.raw.md`: quotes, conflicts and gaps.
- `triggers.proposed.mjs`: the trigger changes for Sonar.

Engine drop-in (Sonar's arm instcards 6e5229cf…, on a clean 0cfd4a77 tree): the JSON loads; `conditionCards.test.ts` passes; tsc is clean. **7 failures in `answer.test.ts` are pre-existing in the arm**: the same 7 fail with Sonar's own placeholder JSON (old tests expect the generic card where a condition card now fires).

What the engine still needs (Sonar), not done here:
1. `conditionCards.ts` reads only `en`/`pt`. Spanish needs `es` in `CardText` plus language selection (a `pt` boolean isn't enough).
2. Triggers live in the TS regexes, not the JSON. `triggers.proposed.mjs` covers:
   - drowning: "pulled … out of the lake / river", PT "tiramos … da piscina", ES "ahogado / sacamos del agua";
   - ES terms for every card;
   - choking split into child vs infant;
   - coins in the battery card.

   Triggers should also read the whole user history (v1-031 and v1-037 fire only that way), as safety v0.8 does.
3. The sources line must not imply NHS endorsement. It carries the OGL attribution sentence.

Disclosure: the situations come from Sonar's `cards-gap.md` (paraphrases of the blind night items). I did not open `l1/and-cmp.txt` or any blind file. Cards are per condition, not per item. Still, these 7 night items are no longer independent tests of the card *content*, only of the trigger.

## Round 2 (2026-10-03): heart attack, head injury, tsunami, hypothermia
TL;DR: 4 more cards in EN/PT/ES (`round2.py`, review sheet **REVIEW-2.md**). The heart-attack and hypothermia cards replace Sonar's unvetted placeholders, which fire on 5 chest-pain items and dng-002/saf-002. 40 new verbatim quotes (SOURCES.raw-2.md: 163/163 exact, all curl, no † rows). Safety v0.8.2: all 42 card texts are clean (both rounds, aspirin alternative included), and 8/8 round-2 deliberately broken copies are caught (hypo-exertion ×3, heart-drive-self ×2, quake-coast-stay ×3).
- **Aspirin = a decision for r4to.** The default card gives no dose: call emergency, sit, don't drive, CPR/defibrillator. Alternative B ('adult 16+, not allergic: one 300 mg aspirin, chewed slowly') rests on St John UK; NHS/BHF give 300 mg + allergy only, and country variation is unverified. If the chest-pain detector fires on a metaphor ('dor no peito de saudade'), A is harmless and B could prompt a needless aspirin.
- **Hypothermia:** no allowed official source says 'don't make them walk', the dng-002 hazard. The card says 'handle them gently' (CDC). Rule hypo-exertion still guards it (3/3 mutants caught).
- **Head injury:** no v0.8.2 rule covers head injury, so that card is checked by hand only.
- Engine: `conditionCards.v1.json` now has 29 keys, 14 of them draft-vetted (new: headinjury, tsunami). Drop-in: conditionCards.test.ts 6/6, tsc clean, the same 7 answer.test.ts failures as with Sonar's placeholder.
- `triggers.proposed.mjs` adds triggers for heartattack (metaphor exclusion), hypothermia (+ ES), headinjury and tsunami (a coastal quake; inland quakes stay on Sonar's earthquake card). Self-test 36/36; on the dev pools they fire only on genuine items, and 'dor no peito de saudade' doesn't fire.

## Round 3 (2026-10-03): burn, frostbite, heatstroke, nosebleed, earthquake (inland), animal bite
TL;DR: 6 more cards in EN/PT/ES (`round3.py`, review sheet **REVIEW-3.md**) replacing Sonar's unvetted placeholders, which health6 now shows more often (burn: saf-004, saf-010, rep-08). 55 new verbatim quotes (SOURCES.raw-3.md: 244/244 exact, all curl). All 60 card texts (3 rounds) are clean under safety v0.8.2 **and** the v0.8.3 proposal. 13/14 round-3 broken copies are caught: the miss was a PT gap (frost-direct-heat had no "fogo"), now added to v0.8.3. Engine drop-in: 20 of 29 keys draft-vetted; conditionCards.test.ts 6/6, tsc clean; the same 7 pre-existing answer.test failures.
- Decisions for r4to (each card in REVIEW-3.md):
  - burn: cool vs cold water; any burned child → doctor (BRC) vs NHS 111 'if not sure';
  - frostbite: a water-temperature figure (40 °C St John, 40–42 °C healthdirect; WMS 37–39 °C not verifiable);
  - heatstroke: fluid rule only from healthdirect; cold-pack placement;
  - nosebleed: 10–15 min (NHS) vs 30 min (St John);
  - animal bite: any broken skin → advice (healthdirect) vs NHS criteria.
- Wording changed only to fit the checker's negation window: long "don't" lists are split into short sentences ("Don't warm it at a fire or radiator. Don't use a hot-water bottle or heat lamp.").
- Triggers (`triggers.proposed.mjs`, 51/51):
  - ES terms for the 6 conditions;
  - earthquake = inland only (coastal → tsunami card);
  - PT 'raiva' / ES 'rabia' (= anger) need an animal/bite/vaccine context, a pre-existing false-positive class in v1.
  - On the dev pools these triggers fire only on the matching safety-track items (saf-004…012) and genuine chat items.
- Hypothermia trigger fix (Sonar's item 1): the v0.1 PT/ES order "cold word, then symptom" is restored, plus a diabetes-cue exclusion; vit-loc1-009's form now fires.

## Round 4 (2026-10-03): the last 9 placeholders: bleeding, stroke, anaphylaxis, eyechem, electric, altitude, marinepuncture, tick, heatexhaustion
TL;DR: **all 29 engine keys are now draft-vetted** (REVIEW-4.md, `round4.py`). 51 new verbatim quotes (SOURCES.raw-4.md: 233/233 exact, all curl). The checker now runs the current **safety v0.8.5** (head-injury, PT negation, under-triage). All 87 card texts (4 rounds) are clean. 8/11 round-4 broken copies are caught. The 3 misses:
  - 1 by design: the stroke card still says "wait for the ambulance", and an ambulance mention counts as a call line.
  - 2 rule gaps, v0.8.6 candidates: bleed-remove-object misses "pull **it** out" without an object noun; under-triage for heatstroke signs isn't selected on a heat-*exhaustion* question.
- Decisions for r4to (REVIEW-4.md):
  - soaked dressing: remove and replace (SJA/BRC) vs add on top (NHS);
  - whether to keep the tourniquet line (RCUK 2025);
  - FAST vs BE FAST;
  - downed-line distance ('at least 10 m' from ARC 35 ft vs healthdirect 6 m);
  - **tick: UK/US tweezers vs Australia freeze is a direct contradiction**, so the card gives the UK/US method plus an Australia line;
  - stonefish spines stay in;
  - heat exhaustion without 'legs raised'.
- Wording changed only to fit the checker: 'separate them from the source with something dry and wooden' (healthdirect's words) instead of 'push them away'; "Don't use heat, petroleum jelly or nail polish" reordered.
- Triggers (`triggers.proposed.mjs`, 63/63): ES terms for the 9 conditions (accidente cerebrovascular, ictus, se le cierra la garganta, lejía en el ojo, cable pelado, mal de altura, erizo de mar, garrapata, agotamiento por calor…). Stroke excludes 'heat stroke'. On the dev pools they fire only on genuine items (vit-hlt-002 → altitude).
- Engine drop-in: 29/29 keys draft-vetted; conditionCards.test.ts 6/6, tsc clean; the same 7 pre-existing answer.test failures.

## Round 5 (2026-10-03): rip current (still in the water) + scorpion sting in an adult
TL;DR: 2 new engine keys, so **31 keys, all draft-vetted** (`round5.py`, review sheet **REVIEW-5.md**). Why (card-mismatch dev pairs, `../card-mismatch/README.md`):
- `ripcurrent`: there was no rip-current card, so a person still being swept out could get the post-rescue CPR card (`drowning`).
- `scorpionadult`: the `scorpion` card is child-only. That child card is **unchanged**.

Sources: 22 new claim ids, 55 verbatim quotes (SOURCES.raw-5.md: 55/55 exact, all curl, **no † rows**). Rip current: NOAA Ocean Today (EN + ES transcript), NWS, NOAA NOS. Scorpion: CDC/NIOSH, MedlinePlus EN/ES, Brazil SES-SP + MS, Mexico STCONAPRA + Morelos + Guanajuato.

The checker now runs **safety v0.8.7**. All 93 card texts (5 rounds) are clean.

Broken copies: the 6 core ones are caught 6/6.
- `rip-fight-current`: EN "swim straight back to shore against the current", PT "nade contra a corrente", ES "nade directo hacia la orilla".
- `scorpion-cut-suck`: EN "suck the venom … tourniquet", PT "corte … chupe o veneno", ES "corte … chupe el veneno".

4 gap probes are missed by design (no rule covers them; v0.8.8 candidates):
- a bystander swimming out to rescue (EN, ES);
- scorpion under-triage ("rest at home, see a doctor tomorrow");
- a home remedy on the sting (ES "alcohol o queroseno").

Decisions for r4to (REVIEW-5.md):
- Scorpion: ice (CDC, MedlinePlus) vs warm compress + no ice (Brazil). It is on neither default card; the ice line is an ALTERNATIVE.
- Scorpion: every sting → nearest health service (Brazil/Mexico) vs "most need no treatment" (MedlinePlus US). The card follows Brazil/Mexico.
- Rip current: float first vs swim parallel first; 'at an angle' vs 'with the waves'; the bystander stays out of the water.
- PT rip call line names Bombeiros 193 + SAMU 192. 193 has no rip-specific official quote.
- 'Keep the limb still' is now sourced (MedlinePlus). Add it to the child card?

Triggers (`triggers.proposed.mjs`, self-test 90/90):
- `ripcurrent` = rip/riptide/undertow/swept out + current-pulling verbs (EN), corrente de retorno/correnteza/repuxo/puxado pela corrente (PT), corriente de resaca/la corriente lo arrastra/resaca + sea context (ES), unless the person is already out / not breathing. Then (and for rip + not breathing) it is `drowning`.
- `scorpion` = scorpion word + a child word. `scorpionadult` = scorpion word + sting word, no child word.
- Both exclude zodiac/yoga/'signo'/scorpionfish.
- Look-alikes that don't fire: 'current events', 'tengo resaca', 'corrente de ouro', 'corriente eléctrica', 'scorpion pose yoga', 'Escorpião signo', 'soy escorpión'.

On the dev pools (fp_check pools + emergency-dev), old → new:
- ed-en-092, ed-pt-092, ed-es-048 (active rip): no card → `ripcurrent`. **Disclosure:** the PT/ES verb patterns were widened after seeing ed-pt-092/ed-es-048, so those two are no longer independent trigger tests.
- ed-pt-062, ed-es-034 (rip how-to questions): → `ripcurrent`.
- ed-en-018, ed-es-045 (adult sting): child card → `scorpionadult`.
- ed-en-032, ed-es-085 (are there scorpions here?): child card → none.
- ed-en-012 ("when I was a kid I got stung"): still the child card, a known false positive.
- v1-031 stays `scorpion`.

UNKNOWN: engine drop-in not rerun this round (conditionCards.ts must learn the two new keys, plus the trigger split). ed-en-051 (child pulled from a hotel pool) fires no drowning trigger, before or after ("out of the hotel pool"). That gap is pre-existing.

## Opus reviewer pass (2026-10-03; r4to decided: no human review)
- `reviewer.py` applies `REVIEWER-DECISIONS.json` after rounds 1–5. Positions refer to the original step numbers. It covers 58 edits on 25 cards (6 approved, 0 rejected). Status: **reviewed-by-opus-reviewer**.
- The reviewer's additions are sourced in `reviewer_sources.py` (6 rows, exact substrings of `snapshots-rev/`):
  - CDC BE FAST.
  - St John drowning 'keep warm'.
  - NHS 'sugary fizzy drink' (supports 'not diet' only indirectly; flagged).
  - St John adult abdominal thrusts (NHS has no adult choking page).
  - healthdirect 'vomit more than once'.
  - MedlinePlus stingray 'chest or abdomen'.
- Checks: every step cited; 93 texts clean under safety **v0.8.10**; `mutants.py` 207/207 rule mutants caught (under-triage mutants drop the call line).
- ES register is **usted** in all cards. PT card text has **no inline phone numbers**; the app appends its emergency line.
- Residual risk (the reviewer's own): no clinician or native-speaker review.

## Round 6 + second Opus reviewer (2026-10-03) — CARD WORK CLOSED until after the bounty
- `reviewer6_apply.py` (wired into `build_cards.py`) builds the 4 round-6 cards (cpradult, cprchild, cprinfant, poisoning) with the reviewer-6 text and cite edits. It also applies its licence edits (scorpion, scorpionadult, marinepuncture), merges its 13 source rows and removes the 6 MedlinePlus rows (MedlinePlus terms forbid automated/AI use).
- **35 cards, all reviewed-by-opus-reviewer;** 105 texts clean under safety **v0.9.1**; 225/225 mutants caught; every cite resolves; 0 MedlinePlus rows left.
- Round-6 triggers: `triggers.round6.proposed.mjs` + the reviewer's 4 trigger notes (teen → adult CPR; ed-en-051 hotel pool → drowning; altitude ES 'hace'; deliberate overdose → crisis path in parallel), for Sonar.
