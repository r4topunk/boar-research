# Persona map v1, DRAFT for the ruler (RULER-SPEC-v1 §5), 2026-10-20 21:4x

Status: **DRAFT r1, not frozen, not hashed** (r1 = the six required edits of PERSONA-MAP-v1-APPROVAL.md plus S1-S6 applied: counts out of headings, factbook/travel overlap line, encyclopedias in every D set, Q5 without the probe result, general-layer wording, source codes folded into Q3). It waits for r4to's veto (§5.1 step 2: a veto needs a logged written reason and is published with the map). After the veto window the frozen form is `persona-map-v1.json` (family -> pack id + pack file sha256 + bytes; the A∪ union; the D sets), hashed into the pre-registration (§10.3). Independent approval: PERSONA-MAP-v1-APPROVAL.md.

TL;DR
- 5 families -> packs, chosen only from the pack cards' domain lines and the blueprint r2 family definitions (rule §5.2: one primary topical pack per subject; general layer = default-eligible general-knowledge packs, of which there are none).
- travel: boar-wikivoyage-en + boar-visa-en (+ area tile when a location is given); tech: boar-crypto; science: boar-medlineplus-en + boar-firstaid-en; place: boar-factbook; humanities: none (B's kit only).
- **A∪ = 6 text packs, 435,298,304 B (≈ 435 MB)**, + places gazetteer 22,962,176 B + per-location tiles. Fits a phone install easily (assumption below).
- Arm B (out of the box) on the native APK = the setup's default package "Essential" (catalog tier `full`: built-in 300-topic base + corpus-standard + corpus-full, ≈ 3.1 MB of text); the default answer model and whether the submitted APK is this build are UNKNOWN.
- Excluded: boar-nist-crypto (built against a V-exact anchor's rubric, see §6), boar-preparedness (superseded by boar-firstaid-en; kept for D), boar-wiki-en-07 (reference shard).

## 1. Inputs used (and nothing else)
| input | what was read |
|---|---|
| RULER-SPEC-v1-2026-10-20.md §5, §4 arm table, §12 U1-U4 | persona procedure and rule |
| RULER-SPEC-v1-REVIEW.md F1, F3, F21 | A∪ as verdict arm; independent approver; storage gate on the union |
| BENCH-ITEMS-BLUEPRINT-2026-10-20.md, revision r2 "Changes" (family definitions) | the five subjects |
| PACK-CATALOGUE-2026-10-12.md; rnd/research/packs/*.md; wave-4 cards (shared-data/packs/wave4/boar-visa-en.card.md, boar-nist-crypto.card.md) | domain line, licence, size, sha256, status |
| native app source, read-only (android-native catalog.json + SetupViewModel.kt, commit 0be84ac 2026-10-19) | default install for arm B |
| arms/litepacks/LITEPACKS.md | build identities only (v3proto shas, for Q3); no result used |
| boar-eval/bench/v0.4/items.jsonl (sha f9ad2f2f…) | **tag values and counts only**, via a script printing no text fields |

Family tag values (information only, not used to choose): place, tech, humanities, science, travel; 75 items in total. Exposure note, stated honestly: the counting script also printed the counts of the other tag fields (type, region, situation, time_sensitive, health_safety, over_refusal, multiturn_shape, anchor_vexact) and the four `anchor_vexact_question` strings. Those four strings are the post author's public questions, already listed verbatim in blueprint r2 and the ruler spec; no question text, checklist, reference, answer, trace or score of a v0.4 item was read. None of these extra values is used below.

No v0.4 the post author-blog pack exists (searched arms/ and shared-data/packs/); §5.1 step 4 would exclude one anyway.

## 2. Family -> persona packs
Persona(family) = B's kit ∪ the packs below (§5.2). Sizes = pack file bytes from the card. "Card domain" quotes the card's domain line (packs/README.md `domain` column, or the card's own "Domain:"/title line for wave-4 cards).

### travel: "a traveller who installed the travel-guide pack and the visa-rules pack, with the area tile for where they are"
| pack | sha256 (card) | bytes | licence | card domain (justification) |
|---|---|---|---|---|
| boar-wikivoyage-en | ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e | 351,092,736 | CC BY-SA 4.0 | "travel guides": the primary pack for the travel / current-place subject |
| boar-visa-en | d1dd0ffb58a8e4f9b50a6a21cb164bdb314a7181eb2803c952db21e21359ad20 | 11,231,232 | CC BY-SA 4.0 | "Wikipedia visa requirements and visa policies": the primary pack for the travel-logistics subject (blueprint r2: "travel arithmetic/logistics") |
| area tile (items with a device location only) | built at freeze per §5.2 (APK flow, else 25 km places/POI tile); gazetteer world-places 215ce4663b2f79dbf25e9cacab90cd8aa0a8711721663a733cb53bc49d972892 | 22,962,176 + tile(s) | CC BY 4.0 (GeoNames) + ODbL 1.0 + CC BY-SA 4.0 | kit-vexact-places: "places + OSM venues"; the spec's rule, not a topic choice |
Total (text packs): 362,323,968 B (≈ 362 MB), + gazetteer and tiles.

### tech: "a crypto/tech researcher who installed the Ethereum and cryptography pack"
| pack | sha256 | bytes | licence | card domain |
|---|---|---|---|---|
| boar-crypto | ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb | 36,093,952 | mixed: CC0 1.0, BSD-2/3-Clause, PD, MIT, CC BY 4.0, FSFAP variants, CC BY-SA 4.0 (per-source map in meta) | "Ethereum, EIPs/BIPs, crypto": the only carded pack naming the cryptography/Ethereum subject of the tech family (blueprint r2: "cryptography, Ethereum, CS, mechanism design/economics") |
Total: 36,093,952 B (≈ 36 MB). No carded pack names CS or mechanism design/economics (qa-money-se's domain is personal finance, a different subject).

### science, incl. everyday health: "a health-minded reader who installed the consumer-health and first-aid packs"
| pack | sha256 | bytes | licence | card domain |
|---|---|---|---|---|
| boar-medlineplus-en | c9ac4dcfdae367d4502c3360bf0ffc9596d55290c0a49e0835aeedf990ba227a | 4,268,032 | PD (NLM), credit line "Courtesy of MedlinePlus from the National Library of Medicine" | "consumer health summaries (NLM)": primary pack for the everyday-health subject |
| boar-firstaid-en | 8cfab0b47ec8c5cb32840b24df1054c4df1a08d600d063c95c022c58eb5bf558 | 20,987,904 | CC BY-SA 4.0 + US PD (FM 21-76, federal works, ATP 4-02.11) | "first aid / preparedness (v4)": primary pack for the practical-safety side of everyday health |
Total: 25,255,936 B (≈ 25 MB). No carded pack names general science (physics, biology, etc.); that subject runs on B's kit.

### place: "a curious reader who installed the country-facts pack"
| pack | sha256 | bytes | licence | card domain |
|---|---|---|---|---|
| boar-factbook | c585435354a413d04790882c4e2263f725b1024c067febad3f2a99783e663447 | 11,624,448 | CC0 (archive of a US government work; snapshot 2026-09-11) | "country facts (CIA World Factbook archive, 261 entries)": the only carded pack whose domain is place overviews |
Total: 11,624,448 B (≈ 12 MB). Card status: user-selected only; persona choice follows the domain line, the status only governs the general layer (§5.2).

### humanities: "a reader of philosophy, history and literature who installed nothing beyond the default"
- Persona = B's kit only. No carded pack's domain names philosophy, history or literature; the general-knowledge packs (boar-simplewiki-en "Simple English Wikipedia", wiki-vital5 "Wikipedia intros (vital L5)", boar-wiki-en-top100k "enwiki top 100k full text") are not default-eligible on their cards, so the general layer is empty (§5.2, U4). Total: 0 B.

### General layer (all families)
Empty: no general-knowledge pack has card status default-eligible (simplewiki and qa-money-se user-selected only; top100k and vital5 not in kit). Default-eligible packs that are not general-knowledge (e.g. qa-health-se, qa-outdoors-se, qa-cooking-se, and the persona packs boar-medlineplus-en, boar-firstaid-en, boar-visa-en) are topical: they enter a persona or D by domain, never the general layer.

## 3. A∪ (verdict arm)
A∪ = B's kit ∪ {boar-wikivoyage-en, boar-visa-en, boar-crypto, boar-medlineplus-en, boar-firstaid-en, boar-factbook} ∪ area tiles (per item location, §5.2), installed once, identical for every item.

| part | bytes |
|---|---|
| 6 text packs | 435,298,304 (≈ 435 MB / 415 MiB) |
| places gazetteer (world-places) | 22,962,176 |
| area tiles | UNKNOWN until built at freeze (the 4 existing city tiles are 0.66-9.9 MB each) |
| B's kit (native "Essential": corpus-standard 614,084 + corpus-full 2,530,725) | 3,144,809 |
| embedding model bge-small-en-v1.5 q8 (required) | 36,806,944 |
| **total without the answer model and tiles** | **≈ 498 MB** |

Fit: yes. Assumption: a ≤ 12 GB-RAM phone with ≥ 128 GB storage and ≥ 10 GB free; the native catalog's own storage budget is 50 GB (`storageBudgetBytes` 50,000,000,000), the ruler's storage gate is 50 GB (§7.1). With the largest catalog answer model (5.16 GB) the install stays < 6 GB. Download time on the install path is the §7.3 gate's business, not this map's.

## 4. Out-of-box kit (arm B)
| what | value | source |
|---|---|---|
| default setup package | "Essential" (`SetupPackage.ESSENTIAL` -> catalog tier `full`) | SetupViewModel.kt l.47, l.65 (commit 0be84ac) |
| text in that tier | built-in 300-topic base + corpus-standard (2aeff76d…, 614,084 B) + corpus-full (6d602003…, 2,530,725 B), CC BY-SA 4.0 (Wikipedia) | catalog.json tiers |
| optional tier offered | "Encyclopedia" = Essential + wiki-vital5 (d3b87d56…, 163,647,488 B) | catalog.json |
| default answer model | UNKNOWN (the catalog lists 7 LLMs, none flagged default; setup offers "the default and the compact tier") | catalog.json, SetupViewModel.kt l.59 |
| boar-crypto / boar-wikivoyage-en | NOT in the native catalog (they are the TS claim kit) -> they enter only via persona packs | catalog.json |
| area tile in B | only if the README instructs it (§5.2, F8); UNKNOWN | README of the submitted APK not read |
| whether the submitted APK = this build | UNKNOWN (U1) | — |
| format support | native engine reads format 2 (`WikiPack.kt`); its `PackSource` enum stops at BIPS (codes 0-8): packs with source codes 9-12 (stackexchange, medlineplus, factbook, simplewiki) may be mislabelled or dropped. UNKNOWN until checked on the APK | WikiPack.kt l.20, l.691 |
| side-loading | the app opens any `.sqlite` in its pack dir as `local-<name>`; this is the install path for A∪ if the README documents it | BoarServices.kt l.170 |

Consequence for the map: medlineplus (code 10) and factbook (code 11) need the source-code check before freeze; if the APK drops their rows, the frozen map must say so or the APK must carry the patch (no map edit after freeze, §5.1).

## 5. Interference sets (arm D) and the overlapping pairs to test
D(family) = Persona(family) ∪ every other carded pack whose card domain overlaps the same subject ∪ boar-wiki-en-top100k (§5.3).

| family | added in D (beyond the persona) | overlap, by card domain |
|---|---|---|
| travel | qa-travel-se (a85521ce…, 148,324,352 B) | "visas, border rules, airlines, practical local travel" |
| tech | qa-ethereum-se (f16b258f…, 102,473,728 B), qa-bitcoin-se (35b7a3ce…, 77,889,536 B) | "Ethereum development…, EIPs, wallets"; "Bitcoin protocol, wallets, mining, Lightning" |
| science | qa-health-se (687e4994…, 23,797,760 B), boar-preparedness (53d8bcef…, 16,490,496 B), qa-outdoors-se (ff733e4f…, 31,555,584 B), qa-cooking-se (81990fa9…, 88,973,312 B) | "health / medical explanation questions"; "emergency / survival"; "hiking, camping, wilderness skills and safety"; "home cooking technique, food safety and storage…" |
| every family | wiki-vital5 (d3b87d56…, 163,647,488 B), boar-simplewiki-en (c751768b…, 480,534,528 B) | general knowledge ("Wikipedia intros (vital L5)", "Simple English Wikipedia, full text") overlaps every subject; added to all five D sets by one rule |
| all | boar-wiki-en-top100k (9123b372…, 2,542,215,168 B) | "enwiki top 100k full text" |

Pairs D should report (displacement list, §3.5), one row each:
1. boar-wikivoyage-en × qa-travel-se (practical travel advice)
2. boar-visa-en × qa-travel-se (visa and border rules)
3. boar-crypto × qa-ethereum-se, boar-crypto × qa-bitcoin-se
4. boar-firstaid-en × boar-preparedness (near-duplicate: v4 contains v3's 1,754 docs; a pure duplication test)
5. boar-medlineplus-en × qa-health-se
6. boar-firstaid-en × qa-outdoors-se (outdoor safety)
7. boar-medlineplus-en × qa-cooking-se (food safety)
8. boar-factbook × wiki-vital5 / boar-simplewiki-en (country entries)
9. every persona pack × boar-wiki-en-top100k
boar-factbook ("country facts") also overlaps travel's current-place half; that overlap is reported from A∪ vs A traces, not from a D set. Inside A∪ itself (no D needed, report from A∪ vs A traces): boar-wikivoyage-en × boar-visa-en and boar-wikivoyage-en × boar-factbook share destination/country titles.

D bytes are information only (largest D = travel persona + qa-travel-se + simplewiki + vital5 + top100k ≈ 3.70 GB); the storage gate applies to the submission (§5.3, F21).

## 6. Excluded packs and why
| pack | reason |
|---|---|
| boar-nist-crypto (e45b16d5…, 1,761,280 B; domain "NIST cryptography standards") | its card reports a "V-exact vx-002" check: every rubric fact of that anchor is in the pack (built 2026-10-19). A pack checked against an anchor's rubric is the case §5.1 step 4 guards against, so that exclusion is extended to it. Its domain ("NIST cryptography standards") overlaps the tech subject, so leaving it out of D(tech) departs from §5.3's literal rule. This is a logged deviation, decided in Q1. Also user-selected only and shadowed by boar-crypto on its card. See Q1 |
| boar-preparedness | superseded by boar-firstaid-en (v4 = v3 docs + ATP 4-02.11); one primary pack per subject; kept in D as the duplicate test |
| boar-wiki-en-07 | "enwiki shard 07/15", not topic-curated, reference only |
| qa-money-se | "personal finance": no family subject names it; not default-eligible so not general |
| v3proto rebuilds of simplewiki/factbook/medlineplus/firstaid (LITEPACKS K1-K3) | different shas, format not on the cards; see Q3 |

## 7. Questions for r4to (veto window; each with a recommended answer)
1. **Exclude boar-nist-crypto from every scored arm (A, A∪, D)?** Recommended: yes. It was built against anchor vx-002's rubric; its card records a check against anchor vx-002's rubric, the "pack shaped on the anchor" case of §5.1.4; excluding it from D departs from §5.3 and is logged as a deviation with this reason; the tech persona keeps boar-crypto.
2. **boar-visa-en as a second travel pack in the persona (and so in A∪)?** Recommended: yes. Its card domain (visa requirements and policies) names the travel-logistics half of the blueprint r2 travel subject, the same split §5.2's own v0 table makes for everyday health (medlineplus + firstaid); the alternative (visa only in D) leaves the logistics subject without a pack. Veto if you read "one primary pack per subject" as one per family.
3. **Which builds are frozen: the format-2 files on the cards, or the v3proto rebuilds used by LITEPACKS (other shas)?** Recommended: the files the submitted APK reads. The native engine reads format 2, so the card shas above, unless the 1.7B app ships v3proto packs; decide before freeze, because a map edit after it opens a new (APK, map) pair (§9.3). Same decision covers source codes 9-12: confirm on the APK that boar-medlineplus-en (code 10) and boar-factbook (code 11) rows are kept; if not, ship the label patch in the APK or record in the frozen map that those two packs are inert.
4. **Arm B = the native setup's untouched default ("Essential" tier + its default model)?** Recommended: yes, B = whatever the README's first-run flow selects with no changes; confirm the submitted APK commit (≥ 0be84ac?) and its default answer model, and whether the README tells the user to download the area tile (U1, F8).
5. **Humanities persona stays empty (B's kit only), with boar-simplewiki-en only in D?** Recommended: yes. Adding simplewiki would need its card status changed; changing a card to fit the map is the kind of choice the procedure forbids. The verdict arm still covers humanities through B's kit.

## 8. UNKNOWN
- Default answer model of the native APK, and whether the submitted APK is commit 0be84ac or later (arm B).
- Whether the native engine keeps or drops rows with source codes 9-12 (affects boar-medlineplus-en and boar-factbook in the persona).
- Area-tile sizes and count (built at freeze from item locations; the APK's own flow if it has one).
- Whether the README offers all six persona packs (the storage and install gates assume it does, §7.1/§7.3).
