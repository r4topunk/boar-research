# IN-PACK stratum for the v0.4 ruler (tag-level, 2026-10-21)

Status: **candidate rule R1, not frozen.** Freeze = record the sha256 of this file's §2 rule, of `INPACK-STRATUM-2026-10-21.json` and of `tools/inpack_map.py` in the pre-registration (RULER-SPEC-v1 §10) before any arm answers a v0.4 item. 0 LLM, 0 judge, 0 generation, 0 paid.

TL;DR
- Under R1 (tag -> topical pack domain), **(a) native default kit: 0/75 in-pack** (its only text is general Wikipedia, which never makes an item in-pack), **(b) persona A∪: 57/75**, **(c) 11 published packs + wave-4: 57/75**, the same 57 ids.
- Off-pack = **18**: all 16 humanities items + the 2 science items without the health tag (cw-026, cx-026).
- (b) and (c) cannot be told apart from tags: they differ in pack identity, not in subject coverage. Separating them, or separating CS/econ inside tech and cities inside place, needs a per-id subject label made from the question text. That is ruler work for the coordinator, before scoring, not this script's job.
- In-pack means **the domain matches**, not that the fact is in the pack. On dev data, 3 of 20 no-source key facts sat in a K0 pack and were never retrieved (K1-COVERAGE). FACT-REACH-2026-10-21 shows reach ≠ answer.
- In-pack vs off-pack is confounded with family (off-pack = humanities + 2 science items), so the ruler must show the split per family, never as one pooled gap.

## 1. Inputs (read) and exposure
| input | what was used |
|---|---|
| PERSONA-MAP-v1-draft.md r1 + APPROVAL | family -> persona packs, A∪, exclusions (nist-crypto, preparedness, wiki-07) |
| BENCH-ITEMS-BLUEPRINT-2026-10-20.md r2, RULER-SPEC-v1 §4/§5/§10 | family definitions, strata (type, family), freeze order |
| rnd/research/packs/*.md (README table, vitalik card), wave-4 cards (visa, nist-crypto) | domain lines, sizes |
| native catalog.json (boar-ios/.ref/android-native) | default kit = "Essential": 300 built-in topics + corpus-standard (1,000 Wikipedia topics, 614,084 B) + corpus-full (4,000, 2,530,725 B) |
| QUEUE l.993/998/1044-1046 | what is on hf.co/datasets/r4topunk/boar-packs |
| boar-eval/bench/v0.4/items.jsonl (sha f9ad2f2f… checked by the script) | **id, family, type, tags (minus anchor_vexact_question), and whether context has lat/lon keys.** No question text, turn, checklist, reference, note or city value read or printed. One EXPOSURES row |

Published count: the brief says 9 published packs; the hub holds **11** (wave 1: 5 SE + firstaid + medlineplus; wave 2: factbook + simplewiki; wave 3: qa-cooking-se + qa-money-se). (c) uses all 11. Under R1 the 2 extra packs trigger on no tag, so (c) gives the same booleans whether you count 9 packs or 11.

## 2. Rule R1 (freeze candidate)
1. An item is **in-pack under set S** iff at least one **topical** pack in S has a card domain that names the item's subject, where the subject is read from tags only:

| tag condition | packs whose card domain names it |
|---|---|
| family = travel | boar-wikivoyage-en (travel guides), boar-visa-en (visa rules), qa-travel-se (visas, borders, practical travel) |
| context has lat/lon | area tile + world-places gazetteer (§5.2 area-tile rule), boar-wikivoyage-en |
| family = tech | boar-crypto (Ethereum, EIPs/BIPs, crypto), qa-ethereum-se, qa-bitcoin-se, boar-vitalik-blog-en (Ethereum, cryptography, mechanism design) |
| health_safety = true | boar-medlineplus-en (consumer health), boar-firstaid-en (first aid), qa-health-se |
| family = place | boar-factbook (country facts) |
| (no tag identifies the subject) | qa-cooking-se, qa-money-se, qa-outdoors-se: they never trigger under R1 |

2. **General-knowledge packs never make an item in-pack**: the native kit's Wikipedia text, boar-simplewiki-en, wiki-vital5, boar-wiki-en-top100k. Without this, every item would be in-pack under every set and the stratum would carry no information. Their reach is what "general" means in §5.
3. Excluded from every set: boar-nist-crypto (checked against anchor vx-002's rubric; persona map Q1), boar-preparedness (superseded), boar-wiki-en-07.
4. Sets: **a** = native Essential kit (no topical pack). **b** = A∪ of PERSONA-MAP-v1 r1 (wikivoyage, visa, crypto, medlineplus, firstaid, factbook, area tiles). **c** = the 11 HF-published packs + wave-4 {boar-vitalik-blog-en, boar-visa-en}; no wikivoyage, no crypto, no tiles. **persona** = the item's own family persona only.
5. The JSON is produced by `tools/inpack_map.py` (asserts the items sha; prints counts only).

## 3. Counts (n / in-pack under a / b / c / own persona)
| stratum | n | a | b | c | persona |
|---|---|---|---|---|---|
| **all** | 75 | 0 | 57 | 57 | 57 |
| family travel | 16 | 0 | 16 | 16 | 16 |
| family tech | 15 | 0 | 15 | 15 | 15 |
| family place | 15 | 0 | 15 | 15 | 15 |
| family science | 13 | 0 | 11 | 11 | 11 |
| family humanities | 16 | 0 | 0 | 0 | 0 |
| type lookup | 13 | 0 | 11 | 11 | 11 |
| type explanation | 16 | 0 | 12 | 12 | 12 |
| type comparison | 12 | 0 | 9 | 9 | 9 |
| type synthesis | 12 | 0 | 9 | 9 | 9 |
| type reasoning | 14 | 0 | 10 | 10 | 10 |
| type multiturn | 8 | 0 | 6 | 6 | 6 |
| situation travel / at home | 23 / 52 | 0 / 0 | 21 / 36 | 21 / 36 | 21 / 36 |
| health_safety true | 11 | 0 | 11 | 11 | 11 |
| device location given | 7 | 0 | 7 | 7 | 7 |
| time_sensitive true | 19 | 0 | 18 | 18 | 18 |
| over_refusal true | 4 | 0 | 1 | 1 | 1 |
| one_b_fail true | 66 | 0 | 50 | 50 | 50 |
| V-exact anchors (reported apart) | 4 | 0 | 2 (cx-001, cx-007) | 2 | 2 |
| region global / asia / africa / europe / latam / oceania | 29 / 17 / 11 / 7 / 6 / 5 | 0 | 24 / 12 / 8 / 4 / 4 / 5 | same as b | same as b |

Per persona: travel 16/16 (7 of them also take the area tile), tech 15/15, place 15/15, science 11/13, humanities 0/16. The off-pack side (18) is 16 humanities (4 explanation, 3 comparison, 3 synthesis, 2 lookup, 2 reasoning, 2 multiturn) + 2 science reasoning items.

Id lists (b and c identical):
- in-pack: travel cw-027..032, cw-035, cw-037, cx-027..033, cx-038 · tech cw-007..013, cw-036, cx-007..011, cx-013, cx-034 · place cw-001..006, cw-033, cw-038, cx-001..006, cx-039 · science (health) cw-021..025, cw-039, cx-021..024, cx-035.
- off-pack: humanities cw-014..020, cw-034, cx-014..016, cx-018..020, cx-036, cx-037 · science cw-026, cx-026.

## 4. Caveats (must travel with every number from this stratum)
- **Domain match, not fact presence.** In-pack says that a pack covering the subject is installed. It does not say that the item's fact is in that pack, that retrieval keeps it, or that the model reads it right. On dev, the gap was content for 10 of the 20 no-source errors before the topical packs, then routing (4), retrieval (2 + 3 unretrieved in K0 packs) and reading (2 + 4) (K1-COVERAGE; FACT-REACH).
- **Tag granularity overstates in-pack.** "tech" also holds CS and mechanism-design/economics questions that boar-crypto does not name. "place" also holds city and region overviews where factbook has only country entries (INPACK-SPLIT's dev rule calls these place-other = off). "travel" also holds arithmetic items. All 57 are an **upper bound**. A per-id subject label (R2) would tighten it, but it needs the question text. It is ruler-side work by the coordinator, frozen before any arm runs, and it must never feed engine work.
- **Confound.** Off-pack is almost all one family (humanities), and humanities is also where the post author reported over-refusal (4 over_refusal items, 3 off-pack). An in-vs-off gap is therefore a family gap until it is shown within families. Only science has both sides (11 vs 2), so no within-family contrast has power. Report per family; do not pool.
- **Power.** Off-pack n = 18 (2 seeds = 36 answer-runs). A ratio CI on 18 items will be about ±0.10 or wider. Treat the off-pack U as descriptive.
- **Time-sensitive.** 18 of 19 time-sensitive items are in-pack. Pack snapshots (2024-04 SE dumps, 2026-09/10 Wikipedia and Factbook) can be stale on exactly these items.
- **Post-hoc risk.** Freeze this rule, the JSON and the script before scoring. A rule changed after any score is seen is a new, exploratory stratum.

## 5. What the ruler table must show side by side
One row per arm (B = native out of box, A∪ = verdict, D = interference, reference):

| column | content |
|---|---|
| U in-pack (n 57) | U with CI, on the R1 in-pack ids under that arm's set (A∪ -> b; B -> a, which is empty, so B shows U over the same 57 ids, labelled "domain later covered by A∪") |
| U general / off-pack (n 18) | same, on the complement |
| U all (n 75 or 71 headline) | the headline, unchanged |
| reference on the same ids | the reference answer's score / the frontier+web arm on in-pack and off-pack ids, so each U is read against its own denominator |
| per family | in/off split for each family (humanities: off only; science: 11/2) |
| A∪ − B on in-pack ids | the pack effect where the domain matches (paired, item bootstrap) |
| A∪ − B on off-pack ids | must be ≈ 0; if it is not, crowding or a prompt effect is at work, not a pack effect |
| n, seeds, judge family | next to every ratio |

**Never report in-pack U alone.** A "BOAR is good where it has packs" line must sit next to (i) the general U, (ii) the all-item U and (iii) the reference on the same ids, with this file's rule sha and the caveat "domain match, not fact presence".

## 6. Files
- `INPACK-STRATUM-2026-10-21.json`: one record per id: tags used, inpack_a/b/c/persona booleans and the triggering packs. sha256 **56d5b72ba4d0e01af569aee99199f3aa76600702ae5c2efb72ee426aaca12e36**.
- `tools/inpack_map.py`: generator. sha256 926575cbf058a5ab9f76a461b196444b9776343d8e98a3a68e34a320eaf010f9. Run: `python3 -I tools/inpack_map.py <workspace>/boar-eval/bench/v0.4/items.jsonl INPACK-STRATUM-2026-10-21.json`.
- Companion on dev sets (another agent, same tag->domain spirit): `tools/inpack_split.py` (INPACK-SPLIT). Difference: it counts boar-simplewiki-en self-tests as "in", but reports them apart. R1 never counts a general pack.
