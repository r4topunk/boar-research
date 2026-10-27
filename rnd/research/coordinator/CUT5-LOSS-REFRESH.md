# Cut 4/5 loss refresh (bench v0.1 EN, dev, 57 judged items)

Analyst pass 2026-10-06. Read-and-compute only: no generation, no judge calls, no blind/veil reads. Per-item data: `CUT5-LOSS-REFRESH.items.csv` (57 rows; columns: ratio per seed, w, loss to ref/Haiku/Q450, cw flags, path, bucket, cause, arm class).

## TL;DR
- **Cut 4 (= cut 5 on v0.1, answers byte-identical) pooled ratio 0.5591** (s44 0.5585, s45 0.5596; judge.v1-med, 57 items x 2 seeds). Loss to the reference is **0.4409**; gross gap to Haiku no-web is **0.138** (cut 2: 0.164).
- **The mechanical buckets are mostly drained.** VG/AR/snakebite text moved lan-ref-003 0.26 to 0.75, vit-sci-002 0.47 to 0.73, vit-sci-003 0.20 to 0.87, dng-001 0.53 to 0.70. M1+M2 is down from +0.044 to +0.011 (Haiku gap). What is left is M6 thin (30 items, 0.057 to Haiku) and knowledge (M5a/b, 0.043).
- **Confident-wrong: 7 distinct items** (5 per seed; correctness <= 1.0 pooled over both orders, same rule as `analyze.py`): vit-hum-004, vit-cry-002, vit-cry-009 (both seeds), vit-cry-007, vit-cry-005 (s44), trv-002, lan-rsn-003 (s45). Together they lose **0.096** to the reference, 22% of all loss. Causes: **3 pinned or kept passages misread** (cry-002, cry-009, trv-002), **2 false "not recognized" denials** with no source (cry-005, cry-007), **1 true premise "corrected"** (hum-004), **1 regional passage overriding a right memory** (rsn-003).
- **Four general, not-killed, mechanical classes found** (table in section 3). Each is a 1 to 4 item class on dev, so **no single arm clears expected +0.01.** Best single: GEO-TABLE +0.006 to +0.010. The only combination near it is **GEO-TABLE + PLUG as one curated facts-table module: +0.012 to +0.016 on dev, about half that on held-out** (dev-motivated). The old L1 adopt bar (Delta >= +0.02) is unreachable for any of them; a non-inferiority bar plus target-item gates is the realistic frame.
- **Top 3:** (1) GEO-TABLE ceiling +0.0065 (Haiku target) / +0.016 (exact-lookup target), expected +0.006 to +0.010. (2) PLUG ceiling +0.006 / +0.011, expected +0.005 to +0.008. (3) EIPABS ceiling +0.002 (Haiku) / +0.006 (Q450), expected +0.003 to +0.005. NOREC (+0.002) and SC-water (parked, +0.005) follow.

## 1. Per-item picture (full table in the CSV)
Formula as in the anatomy: w_i = item ref-score share (mean of both seeds, about 1/56, 0.0170 to 0.0179); contribution_i = boarMean_i / sum(refMean); loss_i = w_i x (1 - ratio_i); gap_i(target) = w_i x max(0, target_i - ratio_i). Sum of contributions = 0.5591 and sum of loss = 0.4409 (verified).

Cut 4 vs cut 2 anatomy, bucket table (bucket_c4: lan-ref-003, vit-sci-002, vit-sci-003 relabelled M6 because the mechanical defect is fixed; the rest keep the cut-2 labels):

| Bucket | n | Loss to ref | Gap to Haiku | Gap to Q450 | cw item-seeds | Cut 2 gap to Haiku | Status on cut 4 |
|---|---|---|---|---|---|---|---|
| M1 verdict vs own facts | 1 (lan-cmp-003) | 0.0107 | 0.0024 | 0.000 | 0 | +0.022 (3 items) | VG fixed 2 of 3; the rank repair now drops the list (0.40). VG line CLOSED per QUEUE |
| M2 arithmetic | 2 (vit-cry-009, lan-rsn-002) | 0.0205 | 0.0086 | 0.0009 | 2 | +0.022 (3) | vit-sci-003 fixed 0.20 to 0.87; cry-009 untouched (EIP-7251 constants not in the AR pack) |
| M3 card / calc path | 6 | 0.0336 | 0.0077 | 0.0071 | 0 | +0.009 | dng-005 still 0.333 (SC water card parked after S5'' FAIL, recall 72%) |
| M4 context narrows memory | 5 | 0.0446 | 0.0194 | 0.0131 | 1 | +0.021 | open, gate nets +0.002 (anatomy) |
| M5a knowledge missing | 6 | 0.0687 | 0.0194 | 0.0229 | 4 | +0.022 | open (pack/deep) |
| M5b key fact absent or misread | 7 | 0.0800 | 0.0238 | 0.0200 | 3 | +0.020 | CRYPTOSEL/TRAVELSEL killed |
| M6 correct but thin | 30 | 0.1825 | 0.0568 | 0.0204 | 0 | +0.048 (27) | no lever (style/length killed) |
| Total | 57 | 0.4408 | 0.1381 | | 10 | 0.164 | |

Path split (s44): 50 fast-tier items (of which 9 on the no-source memory path), 2 fast + health card, 5 instant (dng-001/002/005 cards, vit-sci-003 calculator, vit-trv-004 travel calc). Seed noise: mean |s44 - s45| per-item ratio 0.057 (median 0.034, max 0.267 = lan-exp-007), so any single-item gain below about 0.15 ratio (0.003 Delta) is inside noise.

## 2. Confident-wrong items (either seed), cause from answer + trace
Context facts: trace stores titles and route codes, not passage text; passage content below comes from the CRYPTOSEL/TRAVELSEL L0 notes where marked.

| Item | cw seeds | Ratio (c4 / Haiku / Q450 / closed-book) | Path | What the 4B saw vs what it said |
|---|---|---|---|---|
| vit-hum-004 | s44+s45 | 0.20 / 0.47 / 0.67 / 0.20 | fast, research | Only an off-topic Wikivoyage "Lord of the Rings tourism" passage (1 kept, 378 to 153 tok). Says "Gríma does not kill Saruman; Gandalf does". The premise is true (Scouring of the Shire). Premise-denial from memory; not fixable by code (premise guard killed) |
| vit-cry-002 FOCIL | s44+s45 | 0.20 / 0.33 / 0.40 / 0.20 | fast, lookup, `context:pinned-1` | EIP-7805 passage pinned (+ EIP-8369). Says FOCIL "enforces inclusion of blocks / finality". Reference: committee-built transaction inclusion lists vs censorship. Misread of a correct pinned passage. CRYPTOSEL (gold sentence in context) lifted rubric 1.0 to 2.5 only |
| vit-cry-009 | s44+s45 | 0.20 / 0.43 / 0.20 / 0.20 | fast, chat, `pinned-3` | EIP-7251 pinned x3. Says "64 ETH cap, 156 validators before and after". Ref: 32 ETH, 312 (+16 ETH) before, 5 after. Wrong old cap + no arithmetic tool. CRYPTOSEL: 5 after but "before" still wrong |
| vit-cry-007 d/acc | s44 (s45 corr 1.5) | 0.22 / 0.33 / 0.47 / 0.20 | fast, memory, no-source | Retrieval returned Wikivoyage Accra x3, all dropped. Answer: "d/acc is not a recognized term, may be a typo". False denial of a real entity (the post author essay, 2023) |
| vit-cry-005 | s44 (s45 corr 2) | 0.23 / 0.57 / 0.47 / 0.20 | fast, compare | Context = Tornado Cash Wikipedia x4, no Privacy Pools text. Says Privacy Pools is "not widely recognized or documented". False denial; the Tornado half is right |
| trv-002 | s45 (s44 corr 2) | 0.27 / 0.60 / 0.50 / 0.20 | fast, lookup | Wikivoyage Brazil x2 (666 to 235 tok); TRAVELSEL notes the plug sentence is already in context. Says "Type C and F, 110 to 127 V". Ref: Type N, 127 and 220 V. Misread of a passage that was there |
| lan-rsn-003 | s45 (s44 corr 2) | 0.25 / 0.60 / 0.60 / 0.80 | fast, chat | Kept Wikivoyage Antelope Valley + North American wildlife (2 of 4 dropped off-topic). Leads with the pronghorn "fastest land animal in the Western Hemisphere", cheetah demoted. Closed-book 0.80. Regional fragment overrides a right memory |

Near-cw (correctness <= 2, not cw): vit-cry-001 (citation marker inside "e.g.": "(e [4].g., EIP-8141)"), vit-hum-002, vit-hum-006, lan-exp-002 (Montenegro "has not yet adopted the euro"), trv-004, vit-cry-003, lan-cmp-005.

## 3. Candidate failure classes (mechanical, deterministic or structured-data fix, not on the killed list)
Items touched are on dev only. Targets: Haiku no-web (anatomy convention) and a "hi" target (exact lookup answer, 0.85 to 0.90; Q450 for EIPABS). Expected = P(fire and correct, 0.8) x gap to a mid target, discounted by what CRYPTOSEL actually realised for EIPABS.

| Class / arm | Items touched (c4 ratio) | Ceiling (Haiku / hi) | Expected Delta | False-fire risk outside the bench | Generalises? |
|---|---|---|---|---|---|
| **GEO-TABLE**: curated country area, population (with year), density, plus top-N rank lists; modes: rank list ("which countries are bigger than X"), 2-entity compare with values and difference, single slot. Source: UN/CIA area, UN population; one lookup table, ~200 rows x 3 fields, no 4B facts-call | lan-cmp-003 (0.40), lan-cmp-001 (0.67), vit-sci-002 (0.73), lan-ref-004 (0.88) | +0.0065 / +0.0164 | **+0.006 to +0.010** (0.0098 with cmp-003 at 0.85) | Medium: country-name collisions (Georgia, Turkey, Jordan, Guinea, Chad, Brazil nut), "bigger than India" about non-countries, population vintage. Needs the CF-style blind trigger set + FF set. CF's own trigger FF was 0/100, recall 80% | Yes as data: area/population rank and compare questions are common trivia and travel prep; table is public data, built without the bench. Dev Delta is partly circular (the 4 items are why it was spotted); held-out transfer about 0.5x |
| **PLUG**: mains electricity lookup (plug types, voltage, frequency) by country, from the Wikipedia/IEC mains table (CC BY-SA), trigger = plug/voltage/outlet/adapter + country | trv-002 (0.27, cw) | +0.0059 / +0.0113 | **+0.005 to +0.008** | Low: needs a country entity plus an electricity cue; "voltage of a car battery" has none | Yes: "what plug/voltage in X" is a core offline-traveller question (bounty framing). 1 dev item only. CF failed this field on raw Wikidata (7/30 disagree); a curated table is the stated fix (QUEUE CF lesson) |
| **EIPABS**: card for "EIP-N / ERC-N" in the question when the pinned in-kit EIP passage exists: title, status, abstract sentences verbatim, 4B bypassed | vit-cry-002 (0.20, cw), vit-cry-003 (0.43); cry-009 excluded (needs 312 to 5 arithmetic) | +0.0024 / +0.0057 (Q450) | **+0.003 to +0.005** (CRYPTOSEL realised +0.0033 with gold in context, so the card adds only the 4B-misread margin) | Low: explicit EIP number only; wrong card if passage is a related EIP (EIP-8369 vs 7805: match the number) | Moderate: EIP-number questions are plausible for a the post author-themed bench; no data build (corpus already in kit). Adjacent to CRYPTOSEL (killed) but a different answer mode |
| **NOREC**: when the answer asserts a user-named entity is "not recognized / no clear definition / may be a typo / not documented" and the context has no passage on it, replace the assertion with "I could not find X in the offline library" and keep any supported text | vit-cry-005 (0.23, cw), vit-cry-007 (0.22, cw) | +0.0080 / +0.0086 (Q450) | **+0.002 to +0.003** (honest-decline floor 0.31 is the realistic target: +0.0030) | Low-medium: a truly fictional entity gets a correct decline either way; risk is stripping a true negative ("No such law exists") on real traffic | Yes, as a rule; gain per fire is small because the answer stays content-free. Does not touch vit-hum-004 (premise guard is killed) |
| SC-water (parked, SC v3 S5'' FAIL: water recall 18/25 = 72% < 80%) | dng-005 (0.33) | +0.0077 | +0.005 if trigger recall were 72% | Known real FFs in v2 (5/50) | Yes, but trigger not solved |
| Citation marker inside abbreviations ("e [4].g.") | vit-cry-001 | ~0 | ~0 | none | cosmetic; 2/2 seeds on one item, fix is a 1-line guard in the citation injector |

Considered and not proposed: **lan-rsn-003 regional-passage drop** (anatomy gate nets +0.002, off-topic context also helps other items); **lan-rsn-002** (fact slip, not mechanical); **hum-004/exp-002/hum-002 premise or fact denials** (premise guard killed, knowledge missing); **M6 thin** (30 items; style/length/diet killed; SPEEDPACK/PROMPTDIET raised cw 5 to 9); **card situational fit** (dng-001/002, vit-hlt-001/002 judged on tailoring to Thailand/solo hiker/Andes, which needs the 4B or per-scenario cards; ceiling 4 items x ~0.15 = +0.011 but content-heavy and reviewer-gated, no general rule).

## 4. Ranking
1. **GEO-TABLE**: highest item count (4) and the only class with a clear data lineage; expected +0.006 to +0.010 on dev, **does not clear +0.01 with confidence**, half that on held-out. Risks: it is CF-lineage (QUEUE: CF country-facts failed data review, 84% vs 98% bar; your brief names CF "context-free fallback", so confirm this is not covered by that kill). Scope here is area/population/density only, curated per field, which was the exact lesson recorded after CF.
2. **PLUG**: one dev item but the cleanest module (one public table, low FF) and a cw item; +0.005 to +0.008.
3. **EIPABS**: no new data, cheap to build; +0.003 to +0.005 because CRYPTOSEL already measured the ceiling of "right passage in context".

**Plain answer: nothing clears expected +0.01 as a single arm.** GEO-TABLE + PLUG built as one curated facts-table module (two tables, one L1) reaches +0.012 to +0.016 on dev, but it is 5 dev items and dev-motivated; treat the transfer to v0.2 as +0.005 to +0.008. EIPABS and NOREC add +0.005 to +0.008 on dev if stacked. If the next move must show a >= +0.02 paired gain on v0.1, no remaining mechanical lever on this evidence reaches it; the open levers are non-mechanical (M6 thin 0.057, M5 knowledge 0.043).

Suggested funnel if run (frozen criterion + sha first): per-module L0 = trigger recall/FF on a fresh blind writer set, data review of 30 rows per table vs source (bar 98%, no revision clause, as CF), byte identity on non-target v0.1 items (60/60), then one stacked L1 judging only changed items with a non-inferiority bar (no changed item down >= 1.0 rubric, cw not up, unsafe 0).

## UNKNOWN
- **Real-traffic share** of country area/population compare, plug/voltage and EIP-number questions (dev: 4/57, 1/57, 2/57; v0.2 held-out share not read).
- **Whether a lookup answer reaches 0.85 to 0.90**: assumed from Haiku/Q450 and the reference text; no generated card exists. The judge penalised thin-but-correct answers (M6), so GEO answers must include the compare numbers and difference.
- **CF kill scope**: QUEUE's CF is the country-facts lookup pack (data review FAIL, set #2 kept unopened); the brief's "context-free fallback" is read as a different or the same item. GEO-TABLE/PLUG are only valid if country-facts-by-field is open.
- **Trace gaps**: passage text is not stored in v0.1 traces; passage-level claims for trv-002/vit-cry-002/-009 rest on CRYPTOSEL/TRAVELSEL L0 notes, not on a re-read of the kit.
- **Ratios mix judges and runs**: cut 4 is judge.v1-med with verdicts reused for identical text (57/57 s44, 56/57 s45); Haiku, Q450, closed-book are single runs under judge.v1 (anatomy caveat). Per-item gap to a single-run target is noisy (+-0.15).
- **Desktop vs phone**: all numbers are desktop-node (llama-server, M4). Latency impact of the arms: lookup and cards are 0 s model time; not measured on a device.
- **Cut 5 = cut 4 on v0.1** by the CUT5-LITE G2 gate (120/120 identical text/tier/passages), so these numbers describe both.

## Sources (read-only)
- Judgments/traces: `boar-eval/runs/kiln/speedpack-l1/spctl-v01-s{44,45}.{traces,judgments.v1-med}.jsonl` (control = cut 4, d51e844c; 57/60 judged, 3 venue items OSM-scored); `analysis-output.txt` there: pooled 0.5591, cw lists s44 {cry-002, 005, 007, 009, hum-004}, s45 {rsn-003, trv-002, cry-002, 009, hum-004}.
- Per-item scoring: `boar-eval/scorers/score.py` pairs (boarMean, refMean, correctness); script in session scratchpad `build.py` (output = the CSV). Cut-2 comparison columns (C2, CB, HAIKU, Q450) from `4B-LOSS-ANATOMY.items.csv`.
- Closed/parked evidence: `rnd/research/QUEUE.md` (VG closed ~l.577, SC v3 FAIL ~l.562, CRYPTOSEL L1 ~l.608, TRAVELSEL ~l.616, CF data review ~l.623, CALC SKIP); `arms/cryptosel/cryptosel-L1.md`; `coordinator/KNOWLEDGE-PACKS.md`.
