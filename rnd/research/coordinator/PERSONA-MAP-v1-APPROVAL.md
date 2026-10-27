# Persona map v1: independent approval (RULER-SPEC-v1 §5.1 step 2), 2026-10-20

**Verdict: APPROVE WITH EDITS.** Every persona pack follows from its card's domain line and a blueprint r2 subject; shas, bytes and totals check out. Required edits fix three spots where card *status* or *results* appear as a justification, one licence omission, and the NIST exclusion's reliance on an item tag plus its unlogged departure from §5.3.

Approver: independent reviewer agent (not the drafter), no item access. Draft checked: PERSONA-MAP-v1-draft.md (2026-10-20 21:4x).

## 1. Rows checked
| row | verdict | reason (card domain line) |
|---|---|---|
| travel: boar-wikivoyage-en | OK | "travel guides" names the travel subject (blueprint r2: "travel (current place + travel arithmetic/logistics)"); matches spec §5.2 v0 table. sha ff8595e3…, 351,092,736 B, CC BY-SA 4.0 = card |
| travel: boar-visa-en | OK, edit 1 | "Wikipedia visa requirements and visa policies" names travel logistics. Second pack for one family has a precedent in the spec's own v0 science row (two everyday-health packs). The justification cites "card status default-eligible", which the rule does not allow for persona choice. sha d1dd0ffb…, 11,231,232 B, CC BY-SA 4.0 = card |
| travel: area tile + world-places gazetteer | OK | Spec §5.2 area-tile rule, not a topic choice. sha 215ce466…, 22,962,176 B = kit-vexact-places card. The gazetteer is CC BY 4.0 (GeoNames); ODbL + CC BY-SA apply to the tiles, which is correct for the combined row |
| tech: boar-crypto | OK, edit 2 | "Ethereum, EIPs/BIPs, crypto" names the cryptography/Ethereum part of the tech subject. sha ae9fbd2c… and 36,093,952 B = card (the valid build, not the OLD 35,962,880 B). Licence omits the card's "FSFAP variants" |
| tech: no pack for CS or mechanism design/economics | OK | No card domain names them. qa-money-se is "personal finance: credit and debt, banking, taxes…", a different subject. Agree |
| science: boar-medlineplus-en | OK | "consumer health summaries (NLM)" names everyday health. sha c9ac4dcf… is the pack file (807bd8bc… on the card is the source zip), 4,268,032 B, PD (NLM) + credit line = card |
| science: boar-firstaid-en | OK, edit 1 | "first aid / preparedness (v4)" names the practical side of everyday health; matches spec v0. The "(card status default-eligible)" justification must go. sha 8cfab0b4…, 20,987,904 B; licence matches card (CC BY-SA 4.0 + PD FM 21-76 + US federal works + ATP 4-02.11 "US government work, public release") |
| place: boar-factbook | OK | "country facts (CIA World Factbook archive, 261 entries)" names place overview. Status (user-selected only) is correctly treated as irrelevant to the persona. sha c5854353…, 11,624,448 B, CC0 = card |
| humanities: none | OK | No card domain names philosophy, history or literature. The general packs (simplewiki "Simple English Wikipedia, full text", vital5, top100k) are not default-eligible on their cards → empty general layer (§5.2). Agree |
| general layer: empty | OK | Status is used only here, as §5.2 allows |
| A∪ union | OK | = the 6 persona text packs + area tiles + B's kit, the union of the rows above. Recomputed: travel 362,323,968; science 25,255,936; A∪ text 435,298,304 B (415.1 MiB); + gazetteer 22,962,176 + B kit 3,144,809 (614,084 + 2,530,725) + embedder 36,806,944 = 498,212,233 B ≈ 498 MB. All correct. The arm-B facts (Essential → tier `full`, sizes, budget 50 GB, embedder bytes) match catalog.json and SetupViewModel.kt l.47/l.65 |
| D travel: + qa-travel-se | OK, see S2 | "visas, border rules, airlines, practical local travel". sha a85521ce…, 148,324,352 B = card |
| D tech: + qa-ethereum-se, qa-bitcoin-se | OK, edit 3 | Domain lines overlap. shas f16b258f… / 35b7a3ce… and bytes = cards. boar-nist-crypto ("NIST cryptography standards") also overlaps by §5.3's literal rule and is left out: a deviation that must be logged (edit 3) |
| D science: + qa-health-se, boar-preparedness, qa-outdoors-se, qa-cooking-se | OK | The first three = spec v0. qa-cooking-se is extra but follows its domain line ("food safety and storage"). Agree. shas and bytes = cards |
| D place / humanities: + wiki-vital5, simplewiki | OK, see S3 | Both are general encyclopedias. Spec v0 had simplewiki only for humanities; adding vital5 there is consistent |
| D all: + boar-wiki-en-top100k | OK | = §5.3. sha 9123b372…, 2,542,215,168 B = card |
| Exclusion: boar-nist-crypto | AGREE with the exclusion; edits 3-4 | Its card records a "V-exact vx-002" string check against an anchor's rubric ("every rubric fact is in the pack"). A pack checked against an anchor rubric is the case §5.1.4 guards against. The draft's "stated target" overstates the card, and the draft leans on the v0.4 `anchor_vexact` tag |
| Exclusion: boar-preparedness | AGREE | The firstaid card says v4 "Supersedes boar-preparedness (v3)". One primary pack per subject; kept in D |
| Exclusion: boar-wiki-en-07 | AGREE | "enwiki shard 07/15", not topic-curated, "reference only" |
| Exclusion: qa-money-se | AGREE | Personal finance is not a family subject, and the pack is not default-eligible, so not general |

Trace check (b). No pack choice rests on coverage, F0, self-test or crowding numbers. Three traces need fixing:
- §1 quotes a result (LITEPACKS "K3 +0.069").
- §6 uses the v0.4 `anchor_vexact` tag, although §1 says no extra tag value is used.
- Q2's recommendation cites status and size.

The per-family item counts in the headings come from item tags. They are not used for choosing, but they are not needed either (S1).

## 2. Required edits (exact text)
1. §2 status as a justification.
   - Visa row: replace `(blueprint r2: "travel arithmetic/logistics"); card status default-eligible |` with `(blueprint r2: "travel arithmetic/logistics") |`.
   - Firstaid row: replace `primary pack for the practical-safety side of everyday health (card status default-eligible) |` with `primary pack for the practical-safety side of everyday health |`.
2. §2 tech row licence: replace `mixed: CC0 1.0, BSD-2/3, PD, MIT, CC BY 4.0, CC BY-SA 4.0 (per-source map in meta)` with `mixed: CC0 1.0, BSD-2/3-Clause, PD, MIT, CC BY 4.0, FSFAP variants, CC BY-SA 4.0 (per-source map in meta)`.
3. §6 boar-nist-crypto reason: replace everything from `built 2026-10-19 with the V-exact anchor vx-002's rubric` through `§5.1 step 4's exclusion is extended to it.` with:
   `its card reports a "V-exact vx-002" check: every rubric fact of that anchor is in the pack (built 2026-10-19). A pack checked against an anchor's rubric is the case §5.1 step 4 guards against, so that exclusion is extended to it. Its domain ("NIST cryptography standards") overlaps the tech subject, so leaving it out of D(tech) departs from §5.3's literal rule. This is a logged deviation, decided in Q1.`
   - Keep the closing `Also user-selected only and shadowed by boar-crypto on its card. See Q1`.
4. §7 Q1: replace `including it would be the "pack shaped on the anchor" the spec forbids (§5.1.4)` with `its card records a check against anchor vx-002's rubric, the "pack shaped on the anchor" case of §5.1.4; excluding it from D departs from §5.3 and is logged as a deviation with this reason`.
5. §7 Q2: replace `Its domain is travel logistics, it is default-eligible, 11 MB, and it was built 2026-10-19 from public sources before the item freeze;` with `Its card domain (visa requirements and policies) names the travel-logistics half of the blueprint r2 travel subject, the same split §5.2's own v0 table makes for everyday health (medlineplus + firstaid);`.
6. §1 inputs table, LITEPACKS row: replace `context only (pack-matched self-test gain K3 +0.069); not used to choose` with `build identities only (v3proto shas, for Q3); no result used`.

## 3. Optional suggestions
- S1. Drop the item counts from the §2 headings ("(16 items)" etc.) and from the tag-count line in §1, or mark them "information, from tags". The rule's inputs are the five family values only (§5.1.1).
- S2. D(travel): boar-factbook ("country facts") arguably overlaps the travel subject's "current place" half under §5.3. Either add it to D(travel) or add one line saying the overlap is reported from A∪ vs A traces only, as §5 already does.
- S3. General encyclopedias in D. The draft adds simplewiki and vital5 where the family has place or humanities content. Science (general science) and tech (CS, mechanism design) also lack a topical pack. Either add both packs to D(science) and D(tech), or state the rule used. Also replace the place justification `whose entries include country articles` (a pack-content argument) with the domain-line reason: "general knowledge overlaps every subject".
- S4. Q5: delete `(it crowds the kit by its 2026-10-13 probe)`. The card status alone carries the argument; the probe is a result.
- S5. §2 general layer: the list of default-eligible non-general packs omits medlineplus, firstaid and visa. Write "e.g." or list them all.
- S6. Add Q6 for the source-code 9-12 issue (medlineplus code 10, factbook code 11). It decides whether two persona packs are effective in the APK, and it must be settled before freeze.

## 4. Questions for r4to: assessment
- Q1 (exclude nist-crypto): right question, sound recommendation. With edit 4 it also covers the D deviation.
- Q2 (visa in persona): right question. The recommendation is sound once it is argued from the domain line (edit 5).
- Q3 (format-2 vs v3proto shas): right question and sound: freeze what the submitted APK reads.
- Q4 (arm B = untouched Essential): right question and sound. It is arm definition rather than persona, but it is needed before freeze.
- Q5 (humanities empty): right question and sound. Changing a card to fit the map would invert the procedure. Apply S4.
- Missing: S6 (source codes 9-12). S2 and S3 could be folded into one D-set question.

## 5. What I read
- PERSONA-MAP-v1-draft.md (all).
- RULER-SPEC-v1-2026-10-20.md: §5 (l.112-138), the §4 arm-table rows for A∪ and D (l.98, l.102), and the arm list at l.10.
- BENCH-ITEMS-BLUEPRINT-2026-10-20.md l.1-15.
- Cards: rnd/research/packs/*.md (README table, plus sha, size, licence, status and domain lines of every card; persona cards in full) and the wave-4 cards boar-visa-en and boar-nist-crypto in full.
- Native catalog.json and SetupViewModel.kt, grep spot-checks only.

I read no v0.4 item, draft, reference, checklist, answer, trace or score. I read nothing under blind/ or rnd/veil/, and neither QUEUE.md nor any arm report or run output. The only anchor information I saw is what the NIST card itself states.

## 6. Drafter's resolution (2026-10-20, coordinator)
- Required edits 1-6: applied verbatim to PERSONA-MAP-v1-draft.md (now draft r1).
- S1 applied (counts out of headings; tag line marked information only). S2 applied (factbook/travel overlap reported from A∪ vs A traces). S3 applied as one rule: simplewiki + vital5 join all five D sets ("general knowledge overlaps every subject"); largest D restated as ≈ 3.70 GB. S4, S5 applied. S6 folded into Q3 (keeps the questions at 5).
- No row of the persona map or A∪ changed; the map stays unfrozen pending r4to's veto.
