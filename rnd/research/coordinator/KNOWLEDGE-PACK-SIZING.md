# Knowledge-pack sizing: is a web-only pack worth building for the 4B before 2026-10-31?

Analyst pass, 2026-10-04. DEV only: bench v0.1 EN (57 judged items) and the public V-exact slice. Read-and-compute only: no generation, no judge calls. The only web access was to licence pages. Baseline = **cut 3** (a67c70db…, v0.1 EN 0.566). Per-item cut-3 values come from `cut3-confirm.md` for the 5 changed items; the other 52 items are byte-identical to cut 2 (4-seed mean from `4B-LOSS-ANATOMY.items.csv`).

## TL;DR
- **Do not build a web-only pack for the bounty.** Anvil's "+0.027 web-only" survives the recount (Q450 − cut 2: web-only **+0.025**, mixed +0.014, wiki-only +0.001). The gain does not come from web content a pack could ship, though. Splitting the web-sourced Q450 gains over cut 3 by why they are out of reach:
  - only non-redistributable sources (news, commercial travel pages, SEP, Guinness): +0.022;
  - already in the kit but lost by retrieval or selection: +0.016;
  - not knowledge (M4, the gain comes from removing bad context): +0.008;
  - already fixed by cut 3's verdict guard (VG): +0.002;
  - open source exists: +0.028. Of this, **only about +0.013 is plausibly reachable**: Nobel CC0 for lan-ref-001 and the post author's WTFPL blog for vit-cry-007. dng-005 is blocked by the water-card trigger (SC parked after 3 rounds). Gríma is blocked by the 4B's denial reflex (Sonar: 15/15 denials even with the book sentence in context).
- **No single web-only pack clears the adoption bar, even at its ceiling.** Best: the post author blog + ethresear.ch, at +0.015 gains-only and **+0.007 net** of the crypto items Q450 made worse. The L1 noise half-width is ≈ 0.025 (cut-3 CI90 [+0.007, +0.058]), so +0.02 is out of reach and these packs would not be measurable.
- **vit-cry-009 is not a missing-knowledge item.** The EIP-7251 constants table is in the shipped crypto pack as its own chunk (`MIN_ACTIVATION_BALANCE … 32 ETH`, `MAX_EFFECTIVE_BALANCE_ELECTRA … 2048 ETH`; chars 3627–3841 of the article). It is also in Q450's source text. Question-similarity selection picks prose windows, not the table. This belongs to selection or the arithmetic tools (AR, constants by field regex), not to a pack.
- **The travel-practical losses are mostly in-kit retrieval misses.** Wikivoyage already holds the Lisbon airport metro line, the Pai road warning ("an average of two accidents a day") and Brazil's 110/220 V. What is missing is Brazil's plug Type N, a one-row fact.
- **Recommendation: park the web-only knowledge line for the bounty.** If one knowledge arm runs before 10-31, make it **CF, a country-facts lookup**. It is not web-only (Wikidata CC0). It is < 1 MB, about 2 agent-days, and fits V-para's comparison (7) and travel-practical (5) families plus V-exact's "Tell me about Japan" (completeness 1/5 today). Expected Δ on v0.1 is +0.005 to +0.012, so it **will probably miss +0.02**. Run L0 first, which needs no judge calls. The criterion is drafted below.
- **After the bounty:** a the post author-blog passages pack (WTFPL, 5–10 MB) is the cleanest web-only pack. It is low value on the bench and carries crypto-noise risk for non-crypto questions (the Japan and Mozi contamination).

## 1. Source split (Q450 oracle contexts vs cut 2 / cut 3)
Classes come from the `kind` field of each item's Q450 passages (`anvil/exp/oracle/ctx-Q450.jsonl`). Δ = Σ wᵢ·(Q450ᵢ − baseᵢ) with wᵢ ≈ 1/56.

| Q450 context class | n | Q450 − cut 2 (net) | gains-only ceiling vs cut 3 | items Q450 > cut 3 |
|---|---|---|---|---|
| web-only | 24 | **+0.025** | +0.046 | 12 |
| mixed (wiki + web) | 24 | +0.014 | +0.031 | 16 |
| wiki-only | 8 | +0.001 | +0.008 | 2 |
| none (dng-002) | 1 | −0.005 | 0 | 0 |
| all | 57 | +0.034 | +0.085 | — |

This reproduces Anvil LOG l.111 (vs bounty1: +0.027 / +0.012 / +0.005) within noise.

Why the web-sourced gains over cut 3 are out of reach (web-only + mixed items, gains-only):

| Reason | Δ | Items |
|---|---|---|
| Only non-redistributable sources won | +0.022 | trv-002 (checkmyplug), vit-cry-005 (forklog, The Block), lan-hlt-001 (PMC), vit-hum-006 (SEP), vit-hum-005 (adamsmithworks), lan-rsn-005 (NatGeo), lan-ref-005, lan-ref-004 (Britannica), vit-cry-010/011, lan-rsn-001/004/007, lan-hlt-002, lan-cmp-004, vit-hlt-003 |
| In kit, lost by retrieval or selection | +0.016 | trv-004, vit-trv-003 (Wikivoyage), vit-cry-002/003 (EIP-7805/4444 in the crypto pack), lan-rsn-002 |
| Not knowledge (M4: context narrows memory) | +0.008 | lan-rsn-003 (closed-book 0.80 > Q450 0.60), lan-hlt-003 |
| Already fixed by cut 3 (VG) | +0.002 | lan-ref-003 (0.26 → 0.78) |
| Open, redistributable source exists | +0.028 | lan-ref-001 (Nobel, +0.009), vit-hum-004 (+0.008; denial reflex), dng-005 (+0.007; card trigger parked), vit-cry-007 (+0.004) |

## 2. Per-item winners (Q450 > cut 3), with source and family

| id | family | cut 3 → Q450 | winning source(s) in Q450 | open alternative |
|---|---|---|---|---|
| lan-ref-001 Nobel Lit 2017 | reference / honesty | 0.51 → 1.00 | nobelprize.org press release + summary | Nobel API (CC0) |
| vit-hum-004 Gríma | humanities (fiction) | 0.20 → 0.67 | Wikipedia "Gríma Wormtongue" + Tolkien Gateway | TG CC BY-SA 4.0; 4B denies 15/15 regardless (Sonar exp-40) |
| dng-005 flood water | health / danger | 0.33 → 0.73 | epa.gov emergency disinfection | EPA/CDC public domain; SC card parked |
| lan-rsn-003 cheetah | reasoning | 0.26 → 0.60 | biologyinsights, marathonhandbook, nature.com | none needed: closed-book 0.80 (M4) |
| vit-cry-005 Privacy Pools | crypto | 0.22 → 0.47 | forklog, The Block + Wikipedia Tornado Cash | the post author blog (WTFPL); Privacy Pools paper (licence UNKNOWN) |
| trv-004 Lisbon airport | travel-practical | 0.38 → 0.64 | lisboacard.city, lisbontourism.org | **Wikivoyage Lisbon already has it** (metro red line, ~16 min) |
| trv-002 Brazil plugs | travel-practical | 0.27 → 0.50 | checkmyplug, power-plugs-sockets | Wikidata plug/voltage (CC0); Wikivoyage has 110/220 V, no Type N |
| vit-cry-007 d/acc | crypto | 0.24 → 0.47 | vitalik.eth.limo dacc2 + aiforhumanity.eu | the post author blog (WTFPL) |
| lan-hlt-001 raw vegan | health | 0.46 → 0.67 | PMC review + Wikipedia Raw foodism | PMC OA subset (per-article licence) |
| vit-trv-003 Chiang Mai→Pai | travel-local | 0.49 → 0.71 | smartenplus, madmonkeyhostels, visitthailandtoday | **Wikivoyage Pai already has it** (winding road, accident rate) |
| vit-cry-002 FOCIL | crypto | 0.21 → 0.40 | The Block, EIP-7805, EF blog | EIP-7805 in kit (CC0); EF blog has no licence statement |
| lan-hlt-003 mosquitoes/HIV | health | 0.58 → 0.73 | WHO fact sheet, napacounty.gov + Wikipedia | CDC (PD); WHO is CC BY-NC-SA 3.0 IGO |
| lan-rsn-002 Burj/Baikal | reasoning | 0.55 → 0.70 | Guinness + Wikipedia Lake Baikal | Wikidata depth/elevation (CC0) |
| vit-cry-003 EIP-4444 | crypto | 0.42 → 0.55 | The Block, EF blog | EIP-4444 in kit; the post author "The Purge" (WTFPL) |
| lan-cmp-001 Brazil vs Russia | comparison | 0.74 → 0.87 | Wikipedia Demographics ×2 (wiki-only) | Wikidata population (CC0) |
| vit-hum-006 harm principle | humanities | 0.42 → 0.53 | SEP + Wikipedia | Gutenberg *On Liberty* (PD; Sonar card, priority C) |

Crypto items where Q450's web passages made things worse: vit-cry-001 −0.11, even with the canonical ethresear.ch quantum post; vit-cry-006 −0.17; vit-cry-008 −0.17; vit-cry-004 −0.05.

**V-exact (cut 3, byte-identical to cut 2):**
- **vx-001 Japan, 0.36.** The reference cites only Wikipedia. The loss is completeness 1/5 (a 2-sentence culture blurb) plus crypto-passage noise. No web source is needed; a country card fits.
- **vx-002 PQ signatures, 0.53.** The reference cites NIST CSRC. The crypto pack already has the NIST PQC article (ML-DSA, SLH-DSA, FIPS 204/205). Missing: the FIPS texts (public domain) and the post author's quantum-emergency post.
- **vit-hum-001 Mozi, 0.55.** Wikipedia body; a coverage miss (rank ~176k, not in top100k). Q450's wiki passages scored lower (0.47).
- **vit-hum-004 Gríma, 0.20.** See the table above: this is the denial reflex, not a missing pack.

## 3. Candidate packs

The Δ columns are whole-bench ratio on v0.1 EN vs cut 3. "Q450 net" counts the items the pack's passages would also hurt. "To Haiku" is the target if the pack lifts its items to Haiku no-web.

| Pack | v0.1 items (+V-exact) | Δ ceiling: Q450 net / gains-only / to Haiku | Bounty fit (V-para: expl 17, cmp 7, synth 7, rsn 7, crypto 5, food 7, trv-local 3, trv-pract 5) | Licence (checked) | Size | Effort | Answer mode | Misuse risk |
|---|---|---|---|---|---|---|---|---|
| **A. the post author blog + ethresear.ch** (web-only) | 10 crypto (cry-001…011) + vx-002 | +0.007 / +0.015 / +0.025 | crypto 5 (+ part of synthesis) | blog: **WTFPL** (repo README); ethresear.ch: **CC BY-NC-SA 3.0** (forum ToS §2); EF blog: none stated, so excluded | blog: 176 posts, median 25 KB md, ≈ 5–10 MB pack; ethresear.ch: tens to hundreds of MB (UNKNOWN) | 1.5–2 d (crypto-pack builder reuse, strip embedded data) | passages | **High.** Long opinionated essays, numbers buried; crypto passages already leak into Japan/Mozi; Q450 lost on 4 crypto items |
| **B. Official health/safety agencies** (CDC, EPA, NIST; WHO) | 8 health/danger | +0.001 / +0.015 / +0.015 | small (no health family in V-para) | CDC/EPA/NIST: US public domain (CDC asks for attribution, no endorsement, no alteration); WHO: **CC BY-NC-SA 3.0 IGO** | 5–20 MB curated | 2+ d plus safety review | card | **High.** Passages beat cards on 0 card items (dng-001/002, vit-hlt-001/002 all lose under Q450); SC water card failed 3 trigger rounds |
| **C. Travel practicalities** (web-only) | trv-002, trv-004, vit-trv-003 | +0.012 / +0.012 / +0.008 | trv-pract 5 + trv-local 3 | winners proprietary (lisboacard, checkmyplug, hostel blogs); the open equivalent is Wikivoyage (CC BY-SA, **already in kit**) | 0 new (retrieval fix) | 1–2 d (section targeting; Sonar's lane) | passages (section-targeted) | Medium. A retrieval fix, not a pack |
| **D. Reference facts** (Nobel + records) | lan-ref-001, lan-rsn-002 (+lan-ref-003, lan-rsn-003 not pack-driven) | +0.019 / +0.019 / +0.019 (real: ≈ +0.009 from lan-ref-001) | low (honesty/reference is not a V-para family) | Nobel API: **CC0** (terms page); Guinness proprietary; Wikidata CC0 | < 1 MB | 0.5–1 d | lookup | Low. Exact rows; fires on narrow cues |
| **E. Country facts (CF)** (not web-only) | trv-002, lan-exp-001/002/003/007, lan-ref-004, lan-cmp-001/003, vit-sci-002 (+vx-001) | **−0.007** (as passages) / +0.007 / **+0.028** | cmp 7, trv-pract 5, part of expl 17; V-exact Japan | Wikidata **CC0**; GeoNames countryInfo CC BY 4.0 (local, already in kit provenance); Wikipedia mains-electricity table CC BY-SA 4.0 as a check | < 1 MB (≈ 250 rows × ~20 fields) | 2–2.5 d | **lookup** (one fact per line, units explicit, deterministic two-country ratio) + card for "tell me about X" | Low-medium. Stale or disputed values (population date, Greenland/Taiwan/Kosovo); wrong-entity fires ("Georgia", "Jordan", "Turkey", "Chad") |
| **F. Wikipedia bodies, top-N by pageviews** | broad | measured: top100k Δ −0.005; wiki-only Q450 +0.001 | broad | CC BY-SA 4.0 | 2.5 GB (100k) / 7.3 GB (300k) / 18.4 GB (full) | done | passages | **High** (rv2 diagnosis: numbers misread, fragments override memory, off-topic windows) |
| **G. Humanities/fiction** (Tolkien Gateway, Gutenberg) | vit-hum-004/005/006 | +0.007 / +0.012 / +0.014 | expl/synth (small share) | Tolkien Gateway **CC BY-SA 4.0** since 2025-01-01; Gutenberg PD (US); SEP proprietary | TG UNKNOWN (≈ tens of MB); Gutenberg subset tens of MB | 1–1.5 d | passages | High. Gríma denial reflex is model-side |

Passages hurt CF's items under Q450 (net −0.007: Kenya languages, Greenland, Japan/Germany density). That is the rv2 mechanism, and it is why CF has to be a **lookup** and not more text.

## 4. Recommendation

**Decision: park the web-only knowledge-pack line for the bounty.** Every web-only candidate's realistic Δ is ≤ +0.01, below the +0.02 bar and below L1 noise. The two cleanest are the post author blog (WTFPL) and Nobel (CC0); each touches 1–2 items.

**Option (at most one MVP, only if a slot is free): CF, the country-facts lookup.** Why this one:
- **Clean licence** (Wikidata CC0).
- **Tiny:** < 1 MB, no vectors.
- **Targets the measured 4B weakness.** The 4B misreads numbers in long context; a lookup puts one number per line and does the two-country arithmetic in code.
- **Fits the bounty families:** V-para comparison 7 + travel-practical 5, and the demo-visible "Tell me about Japan".
- **Same pattern as the arms that worked:** cards, travel calculator, AR. Code takes the answer, or the numbers, away from the 4B.

What it is not: web-only. Its v0.1 ceiling (+0.028 to Haiku) is gross. Forecast: **Δ +0.005 to +0.012 → likely FAIL at +0.02.** The case for running it is the vx-001 Japan demo item and travel-practical robustness, not the v0.1 number.

**Tasks (if CF runs):**
1. Freeze a Wikidata SPARQL snapshot (sovereign states + ISO-coded territories): capital, area, population with point-in-time, official languages, currency, calling code, driving side, emergency number, plug types, voltage, frequency, independence/inception, government type. Store the query text plus the result sha256.
2. Build the trigger from a country-name/alias gazetteer (reuse the GeoNames/places matcher) plus a slot cue (capital, currency, plug, voltage, population, area, density, language, independence, driving, emergency) or an overview cue ("tell me about / overview of / essentials on <country>").
3. Render: a "Facts:" block first (one fact per line, units, source "Wikidata, <date>"). For two-country numeric comparisons, add a computed verdict line (ratio and difference). The 4B then writes ≤ 2 sentences constrained to those facts, as the travel calculator does. Never on health, danger or card paths.

## 5. Draft criterion: CF on cut 3 (freeze its sha256 before any build output exists)

**L0: deterministic, dev only, no judge**
1. **Data check.** Row count ≥ 190 sovereign states. A fresh Opus reviewer checks 30 random rows × 5 fields against the live Wikipedia infobox. Pass: ≥ 98% agreement, 0 errors on capital, currency or plug type.
2. **Trigger.** A blind writer (sees neither v0.1 nor V-para) writes 100 positives: 60 country-slot, 20 overview, 20 two-country comparisons. They also write 100 lookalikes: Georgia (US state), Jordan (person), Turkey (food), Chad (name), Guinea pig, "China" (porcelain), country plus history or "why" questions with no slot.
   - Pass: recall ≥ 90%, false fires ≤ 2/100.
   - 0 fires on Sonar's 1,328 EN dev messages, except listed true country-slot messages, which a reviewer must label correct.
3. **v0.1 + V-exact replay** (cut 3 requests):
   - CF fires on ≥ 6 of the 9 target items and on vx-001;
   - ≤ 3 other v0.1 items change;
   - 0 changes on health, danger, card, calculator or venue items;
   - V-exact venues 6/6 and GPS city 3/3 unchanged.
4. **Arithmetic.** 20 unit tests pass: density ratio, population difference, area rank ("countries bigger than India" = 6 named).
5. **Latency.** Lookup p50 ≤ 5 ms; retrieval p50 ≤ 1.5× cut 3 on the replay.
- **Stop rule:** one revision allowed after a trigger FAIL; a second FAIL kills CF.

**L1: v0.1 EN, s44 + s45, desktop-node, Android 12 GB 4B profile**
- Arm = cut 3 + CF; control = cut 3 traces and verdicts.
- **Byte identity first.** Unchanged items must be byte-identical. If they are, judge only the changed items (judge.v1-med, both orders) and reuse the control verdicts. Log this as the reuse protocol (cut3-confirm precedent).
- **V-exact vx-001**, s42 + s43, judge.v1: report it. Pre-registered expectation: ≥ +0.10. It is not an adoption gate on its own.
- **Adopt if all hold:**
  - Δ ≥ +0.02 on the 57-item paired ratio (two-level bootstrap CI reported);
  - confident-wrong not up;
  - unsafe 0 (safety v0.9.1);
  - no changed item down ≥ 1.0 rubric;
  - retrieval p50 ≤ 1.5× cut 3;
  - first-token p50 ≤ +1 s.
- **Pre-registered forecast:** Δ +0.005 to +0.012, so the expected outcome is NOT ADOPTED. If Δ ∈ [0, +0.02) with 0 drops, record it as "neutral-positive, not adopted". No re-tuning on the same items.
- **Disclosure:** motivated by v0.1 and V-exact dev items. No v0.2 or V-para claim follows from this.

## Sources
- `rnd/research/anvil/LOG.md` l.107 (oracle), l.111 (reachable-gain split vs bounty1), l.110 (rv2 diagnosis).
- `rnd/research/anvil/exp/oracle/{README.md, ctx-Q450.jsonl, articles.jsonl, fetch_sources.py, rv2-diag.md}`.
- `rnd/research/coordinator/{4B-LOSS-ANATOMY.md, 4B-LOSS-ANATOMY.items.csv, cut3-confirm.md, cut3-vgar-L1.md, tf2-on-cut2.md, KNOWLEDGE-PACKS.md}`.
- `rnd/research/QUEUE.md` l.547 (tf2 NO-GO, Japan), l.556/562 (SC water card parked), l.578 (state).
- `rnd/research/sonar/exp/31-vitalik-coverage/A-pack-coverage.md` (the post author writing "nowhere offline"; Brazil 127/220 partial); `…/32-pqc-retrieval/README.md`; `…/40-grima/README.md` (15/15 denial); `sonar/cards/primary-texts-pack.md`.
- Kit content checks (read-only):
  - `shared-data/crypto/boar-crypto.sqlite`: EIP-7251/7805/4444/7594 present; EIP-7251 table chunk at 3627–3841; no Privacy Pools or the post author-blog docs.
  - `shared-data/crypto/build/eips.jsonl`.
  - `shared-data/packs/boar-wikivoyage-en.sqlite`: Lisbon, Pai and Brazil sections.
  - `shared-data/poi/countryInfo.txt` (GeoNames, 252 rows).
- `boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s44.traces.jsonl` (vit-cry-009: pinned-3 EIP-7251 passages, answer "64 ETH… 156").
- V-exact refs: `rnd/research/compass/exp/bounty-eval/bench-vslice/refs/refs.jsonl` (source domains only).
- Licence pages (fetched 2026-10-04):
  - github.com/vbuterin/blog README: WTFPL;
  - ethresear.ch/tos §2: CC BY-NC-SA 3.0;
  - nobelprize.org API terms: CC0 (via search snippet; page returned 403);
  - Tolkien Gateway: CC BY-SA 4.0 since 2025-01-01 (via search snippet; page returned 403);
  - who.int copyright: CC BY-NC-SA 3.0 IGO;
  - cdc.gov/other/agencymaterials: public domain with attribution/no-alteration conditions;
  - blog.ethereum.org: no licence statement in the footer.

## UNKNOWN
- **Single runs and mixed judges.** Q450 is 1 run judged with judge.v1; cut 3 uses judge.v1-med. Per-item gaps < ~0.15 are noise, so every per-pack ceiling here is ±0.01.
- **the post author blog text size.** The repo has 58 MB of markdown, inflated by a few posts with embedded data (max 17.8 MB). Clean text of 5–10 MB is an estimate. The ethresear.ch corpus size is not measured.
- **ethresear.ch NC-SA.** Whether NC-SA is acceptable for a bounty-funded app (non-commercial, but prize money), and whether it can sit next to CC BY-SA packs. The EF blog licence is unknown (none stated).
- **Wikidata coverage.** Exact property IDs and completeness for plug type, voltage, frequency and emergency number must be checked at build time. Population values need a point-in-time choice.
- **V-para fit.** How many of V-para's 17 explanation and 7 comparison items are country-shaped is not known; it was not opened by design. The fit claim rests on the family names only.
- **CF's real effect.** CF's effect on vx-001 (Japan) completeness is untested; no lookup or card has been judged on an overview question.
- **Nobel quote risk.** A Nobel lookup would replace lan-ref-001's made-up quote with the real motivation. The model may still add quotes from memory (see the quote-strip lever in 4B-LOSS-ANATOMY).
