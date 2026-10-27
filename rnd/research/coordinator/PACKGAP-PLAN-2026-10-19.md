# PACKGAP-PLAN 2026-10-19: which new packs could raise fact coverage for a the post author-style offline user, and what fits by 10-23

Research and plan only. 0 judge calls, 0 jev, 0 downloads, 0 builds, no uploads. Inputs are coordinator reports (VPARA-DIAGNOSIS-2026-10-19, T-K4d, T-K6b, WAVE3, WIKIFULL STAGE-A/B, PACKCOND-P2, DEEPWIKI, RATIONALEPASS (incl. CITEMAP-REF), CLOSED.md, PACK-CATALOGUE-2026-10-12, REPORT-PACKS-2026-10-13, DEEP-RESEARCH-2026-10-12, packs-research/VERIFIED.md, the pack cards), the public V-exact set (compass/exp/bounty-eval/bench-vslice/questions.jsonl), BOUNTY_31.md, and a web check of licences and sizes (§Sources). blind/ and rnd/veil were not opened. Category and count information only.
One read-only check ran on the mini: a `grep` count over the enwiki 20261001 multistream index already on disk (no download). It found **1,013 `Portal:Current events/<date>` daily pages for 2024–2026** in the dump.

## TL;DR
- **No new open corpus is likely to move V-para.** The missing facts are mostly absent from every source measured so far:
  - kit: 6/51 items (V-para), 6/34 absent items with the 9 published packs
  - full English Wikipedia: 9/34 (WIKIFULL A+B)
  - every SE / topic pack built so far: 0–1/34 each
  - CITEMAP-REF: 49/51 V-para reference lists cite Wikipedia, yet Wikipedia holds the fact for only about 1 in 4 absent items. The rest sits in the reference model's own knowledge, not in a corpus we can name.
  - For the 4B, one newly covered absent item is worth about +0.003–0.005 raw on V-para. That is 0.239 points spread over 24 absent items, times a capture rate of 0.3–0.5 (see PACKCOND-P1 buckets). Even a good new pack is a ≤ +0.01 V-para lever.
- **Top 3 candidates.** Ranked by expected coverage per GB and per build-hour, among licences PD / CC0 / CC BY / CC BY-SA:
  1. **boar-currentevents-en**: Wikipedia Portal:Current events daily pages, 2024-01 → 2026-09.
     - Source and licence: 1,013 pages in the 20261001 dump we already index, CC BY-SA 4.0.
     - Size: pack ≈ 10–20 MB (est.). Build ≈ 3 h.
     - Target: the recent-event slice. On H this is 8 V-para items and 0.153 of loss, 0.102 of it inside absent (RATIONALEPASS). It is the one named, corpus-shaped gap that no pack and no NS0 Wikipedia dataset holds.
     - Expected: 0–3/34 items, ≤ +0.01 raw.
  2. **boar-cryptostd** (or a boar-crypto re-cut): NIST FIPS 186-5/203/204/205, SP 800-208, IR 8547 and the CSRC glossary.
     - Licence: US public domain, NIST credit asked.
     - Size: ≈ 5–10 MB pack. Build ≈ 3–4 h.
     - Why: csrc.nist.gov is the third most-cited reference domain on V-para (6/51 items, CITEMAP-REF). V-exact vx-002 names these exact documents. The kit holds no NIST text today (boar-crypto card: EIPs/BIPs/ethspecs/ethereum.org/enwiki only).
     - Expected: 0–2/34 absent items; the main value is V-exact and product.
  3. **boar-travelgov-en**: US State Dept country information pages (entry/exit, visas, local laws, safety, health), about 200 countries.
     - Licence: PD "unless a copyright is indicated". Size ≈ 5–10 MB.
     - Target: travel-practical (4 absent, 4 wrong on the 4B).
     - Build ≈ 4–6 h, plus a scraping risk: travel.state.gov returns 403 to our fetcher.
     - Expected: 0–2/34 items.
- **Feasibility verdict for 10-23: YES for #1 and #2. Both can be built, self-tested, coverage-probed and crowding-probed by 10-22 on existing tooling.**
  - #3 is a stretch: it is blocked on the fetch path. Keep it as a 10-22 go/no-go.
  - None of the three changes the V-para bar call (4B stays about 0.41 raw / 0.26 floor-adj). They are product and honesty value: fresher events, correct PQ-crypto standards, travel rules.
  - The decision rule for "default kit vs user-selected" is the frozen crowding rule (D-K3d).

## 1. Inventory: what exists, what was tried, why it closed
### 1a. Packs on disk / published (cards in research/packs/)
| id | size | licence | V-para coverage (absent 34 / per-item 51) | crowding / status |
|---|---|---|---|---|
| boar-crypto (kit) | 36 MB | mixed CC0/BSD/MIT/PD/CC BY/CC BY-SA | kit F0 3–4/5 crypto items; 2/2 crypto absent | IN kit |
| boar-wikivoyage-en (kit) | 351 MB | CC BY-SA 4.0 | kit F0 2–3/51 | IN kit |
| kit-vexact-places (+5 tiles) | 39 MB (+3.65 MB) | CC BY (GeoNames) + ODbL + CC BY-SA | venues 7/7 with GPS (outside ratio) | IN via --places |
| qa-travel-se | 148 MB | CC BY-SA per post | 1/34 verified (travel-practical) | user-selected (kit gold displaced) |
| qa-ethereum-se / qa-bitcoin-se | 103 / 78 MB | CC BY-SA | 0/34 (bitcoin 1 lead unverified) | user-selected |
| qa-health-se / qa-outdoors-se | 24 / 32 MB | CC BY-SA | 0/34 | default-eligible |
| boar-firstaid-en / boar-medlineplus-en | 21 / 4.3 MB | CC BY-SA + PD | 0/34 (V-para has no health category) | default-eligible |
| boar-factbook | 11.6 MB | CC0 | 1/34 (explanation, country) | user-selected (kit-slot gold −1/−3) |
| boar-simplewiki-en | 481 MB | CC BY-SA 4.0 | 0/34 (1 lead) | user-selected (share 0.83/0.71) |
| qa-cooking-se / qa-money-se | 89 / 137 MB | CC BY-SA | 0/34 each | default-eligible / user-selected |
| boar-wiki-en-00…14 (published), top-100k | 18.0 GB / 2.54 GB | CC BY-SA 4.0 | full Wikipedia 9/34 (A 7 + B 2); top-100k 4/51 per item | DEEPWIKI −0.034, top-100k takes 98 % of slots |
| boar-preparedness, wiki-vital5, shard 07 | 16.5 MB / 164 MB / 1.21 GB | CC BY-SA + PD | 0 / 1 / 0 per item | not in kit |
| boar-wiki-en-B (stage-B delta, mini only) | 834 MB | CC BY-SA 4.0 | +2/34 | measurement only |

Unions: 9 published packs + kit = **6/34** (T-K6b); 11-pack union unchanged after wave 3 (WAVE3); every pack on disk per item **10/51** (PACKCOND-P2).

### 1b. Closed lines (CLOSED.md row numbers)
| line | result | why closed |
|---|---|---|
| enwiki top-100k for the 4B (R5), DEEPWIKI (R29), wiki fallback (R32), VITALPACK (R34/R68) | gate FAIL / −0.034 / gold +1 / not detected | crowding of k = 6 slots by a general corpus; fallback rarely reaches gold |
| WIKISECTION (R39) → WIKIFULL (R45) | 9/34 MARGINAL (≤ ~12 with the unfetched delta) | Wikipedia is not where most V-para facts are; no WIKI-ALL arm |
| NOTES35 / QNOTES (R6) | 3/110 kept | model-written notes restate model knowledge |
| PACKDENSE, SECTIONHIT, GROUND-ST, PACKROUTE, STACK, MICROD2Q, H8, QWRITE, KIT-X2b (R44, R46–R49, R70, R72, R86, R93, R95) | step-0 FAIL / not decided | retrieval levers cannot add facts that are not in the store; many-pack routing ≤ 0.61 accuracy |
| CF country-facts tier (R50), FACTS (R9) | data 84 % / fires 0/58 on V-para | comparison fact types on V-para are not infobox/country numbers (RATIONALEPASS: 0 of 14 items) |
| Wave 1–3 packs (T-K4d, T-K6b, WAVE3) | 0–1/34 each | coverage sits on v0.2-style items, not V-para; the 20 no-kept absent items get 0 hits from any pack |
| Wikinews / GDELT / CC-NEWS as recency (DEEP-RESEARCH §4) | not built | Wikinews frozen since 2026-05-04; others not openly licensed |

## 2. Gap map by category (34 absent items of H s42; 4B view from VPARA-DIAGNOSIS)
| category | absent n (of 34) | covered by kit + 9 packs | Wikipedia (full) | 4B main loss | what kind of fact is missing (category level) | corpus-shaped? |
|---|---|---|---|---|---|---|
| explanation | 12 | 1 (factbook) | part of 9/34 | absent, no source (11/17 items had no kept source) | long-tail topic depth (humanities, culture, science); V-exact examples: a country overview, a philosopher, a literary plot | partly: Wikipedia long tail (published, crowds); no open alternative of better fit found |
| reasoning | 5 | 1 (kit) | part of 9 | wrong (6 of 7 items) | numbers and distances the model must combine | weakly: numeric tables (OWID CC BY, routing distances) — reading is the binding limit |
| synthesis | 5 | 0 | part of 9 | absent 5 | multi-source; "other"/"mechanism" fact types (RATIONALEPASS) | no single corpus |
| travel-practical | 4 | 2 | part of 9 | wrong 4 (with on-topic Wikivoyage source) | entry rules, plugs/voltage, practical rules | **yes**: government travel pages (PD) and SE travel (already 1/34) |
| comparison | 3 | 0 | part of 9 | wrong 5 / thin 2 | "other"/"mechanism" facts, not infobox numbers | no |
| travel-local | 3 | 0 | part of 9 | wrong 2 | local specifics (venues are outside the ratio) | OSM/area tiles (ODbL, outside the allowed list; already shipped by decision) |
| crypto | 2 | 2 (kit) | — | reading-bound (3/5 F0) | already in kit; csrc.nist.gov cited on 6/51 items across categories | **yes**: NIST PQC standards (PD) |
| cross-cutting: recent events (2024+) | 8 items on H (0.153 of loss; 0.102 in absent) | not measured | NS0 Wikipedia + delta did not add much (B: +2) | — | dated events after the model cutoff | **yes**: Portal:Current events (CC BY-SA), Wikinews to 2026-05 (CC BY 2.5/4.0) |
| cross-cutting: stale facts | 2 items (0.12 of wrong loss) | — | — | — | — | no (too small) |

Reading:
- Only three gaps are corpus-shaped and not yet tried: recent events, NIST crypto standards, and government travel rules. Everything else is either already measured as absent from Wikipedia and every pack, or bound by the model (wrong from memory), which the deep tier addresses and packs do not.

## 3. Candidates (web-checked; licences at the source where reachable)
| # | candidate | licence (verified?) | raw size | pack est. | freshness | build effort | targets | prior on V-para absent 34 | crowding risk |
|---|---|---|---|---|---|---|---|---|---|
| C1 | **Portal:Current events daily pages 2024-01…2026-09** | CC BY-SA 4.0 / GFDL (Wikimedia dumps legal page) | 1,013 pages in the 20261001 dump; ≈ 9–12 KB wikitext/day → ≈ 10–12 MB | 10–20 MB | to 2026-09-30 (next dump 11-01) | ≈ 3 h: index lookup → range fetch (stageB/fetch.py) → `cleanWikivoyage`-style strip, one doc per day, chunk per event bullet with date prefix → build | recent-event slice (8 items on H) | 0–3 | medium: many entity names per page; must pass share ≤ 0.40 |
| C1b | Wikinews en, 2024-01…2026-05-04 (closed) | CC BY 2.5 (to 2024-12-16) / CC BY 4.0 (after) (Wikinews:Copyright, verified) | 47.5 MB bz2 total; 2024+ subset small | 2–5 MB | frozen 2026-05-04 | +1 h on C1's path (filter by date) | same | +0–1 | low |
| C2 | **NIST crypto standards**: FIPS 186-5, 203, 204, 205 (+ 206 draft if public), SP 800-208, IR 8547, SP 800-57 pt 1, CSRC glossary | US PD: "FIPS … not subject to copyright in the United States"; Technical Series by NIST employees not subject to US copyright, royalty-free reprint licence for foreign rights (NIST pages, verified via search excerpts) | ≈ 15–40 MB PDFs | 5–10 MB | 2023–2025 publications | 3–4 h: pdftotext → section split (the PDF path of T-K1 exists for ATP 4-02.11) → build; or append to boar-crypto (re-cut) | crypto + PQ explanation/comparison; V-exact vx-002 | 0–2 (crypto absent already kit-covered; gain is on reading-bound and cross-category NIST-cited items) | low (distinct vocabulary) |
| C3 | **US State Dept country information** (travel.state.gov) | PD "unless a copyright is indicated"; photos and Country Commercial Guides excluded (copyright page, via search excerpt; direct fetch 403) | ≈ 200 pages × 3–6k words | 5–10 MB | live | 4–6 h incl. a polite crawler; **403 to our fetcher** = blocker risk | travel-practical (4 absent + 4 wrong) | 0–2 | low–medium vs Wikivoyage (same country titles: title collision as with factbook) |
| C4 | ethereum.org full re-cut (8,527 pages; 228 used) + EIPs refresh | MIT (repo LICENSE, verified; not on the PD/CC list: needs r4to ruling, boar-crypto already ships MIT parts) | repo | +20–40 MB to boar-crypto | live | 3 h | crypto (v0.2 crypto absent 11/13; V-para ≈ 0) | 0 | low (inside kit pack) |
| C5 | the post author's blog (vbuterin/blog) | **WTFPL** (README, verified) — outside the allowed list: needs r4to ruling | small | 5–10 MB | 2026-10 | 1–2 h | crypto/explanations in the post author's own terms (product/demo value) | 0 (crypto losses are reading-bound) | low |
| C6 | Wikibooks en (cookbook, how-to, textbooks) | CC BY-SA 4.0 / GFDL | 208 MB bz2 (2026-10-01, verified) | 150–300 MB | 2026-10 | ½ day + filtering | explanation / practical how-to | unknown, low (Wikipedia-like coverage) | **high** (general corpus; simplewiki failed at 0.83) |
| C7 | Our World in Data articles + grapher data | CC BY for OWID's own data/charts/articles; third-party data keeps its own licence (FAQ, verified) | ~GB with data | 50–150 MB as text rows | live | 1–2 days (tables → text rows; format 2 leaves table chunks unindexed) | reasoning/comparison numbers | low (V-para comparison facts are not country numbers) | medium |
| C8 | Stack Exchange 2026-06-30 community dump (expatriates, law, academia; fresher travel) | CC BY-SA per post (licence file not displayed on the item page) | 91.8 GB / 362 files | 10–200 MB per site | 2026-06-30 | 2–3 h per site (wave-3 pipeline) | travel-practical, practical how-to | 0–1 (SE packs 0–1/34 so far) | medium (travel-SE displaced kit gold) |
| C9 | Wikipedia long tail (shards 00–14, already published) | CC BY-SA 4.0 | 18 GB | exists | 2025-08 + delta | 0 (exists) | explanation | 9/34 (measured) | **high** (DEEPWIKI −0.034); user-selected only, deep tier only |
| C10 | Wiktionary en | CC BY-SA 4.0 / GFDL | 1.65 GB bz2 (verified) | ≈ 1 GB | 2026-10 | 1 day | definitions | ≈ 0 (no definitional category) | high |
| — | OpenStax | **CC BY-NC-SA 4.0 for the current library** (help centre and book prefaces, verified) | — | — | — | — | — | — | excluded (NC); confirms D-K5 |
| — | UK FCDO travel advice | OGL v3 (DEEP-RESEARCH verified) — not on the allowed list | 0.7 M words | — | live | — | travel | — | excluded unless r4to extends the list |
| — | CDC Yellow Book 2026 / destination pages | unverified (print by Oxford University Press; CDC pages generally PD) | — | — | — | — | travel health | — | parked until a CDC reuse statement is read |
| — | OSM extracts / more area tiles | ODbL — not on the allowed list (already shipped by decision for venues) | per city 1–20 MB | — | — | — | venue items (outside ratio) | 0 on ratio | none (separate path) |
| — | Wikidata tables beyond facts.v1, Gutenberg reference works (1911 Britannica) | CC0 / PD | large | — | stale (Gutenberg) | — | comparison numbers / general | ≈ 0 (CF closed R50; comparison facts not infobox type) | — |

## 4. Ranking (coverage per GB and per build-hour; crowding noted)
Score = prior V-para items covered (midpoint) ÷ pack GB, and ÷ build hours. Priors are this report's estimates, not measurements.

| rank | candidate | midpoint items | pack GB | items/GB | build h | items/h | crowding | 8 GB phone storage cost | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C1 (+C1b) current events | 1.5 | 0.02 | ≈ 75 | 3–4 | 0.4 | medium | ≈ 0 | **build 10-20** |
| 2 | C2 NIST crypto standards | 1 | 0.01 | ≈ 100 | 3–4 | 0.3 | low | ≈ 0 | **build 10-20/21** |
| 3 | C3 State Dept country info | 1 | 0.01 | ≈ 100 | 4–6 + fetch risk | 0.2 | low–medium | ≈ 0 | go/no-go 10-21 on fetch |
| 4 | C4 ethereum.org re-cut | 0 (V-para) | 0.03 | 0 | 3 | 0 | low | ≈ 0 | post-deadline unless MIT ruled OK (v0.2/product value) |
| 5 | C5 the post author blog | 0 | 0.01 | 0 | 1–2 | 0 | low | ≈ 0 | needs WTFPL ruling; demo value |
| 6 | C8 SE 2026 sites | 0.5 | 0.1–0.2 | ≈ 3 | 3 | 0.15 | medium | small | post-deadline |
| 7 | C9 Wikipedia long tail | 9 (measured) | 18 | 0.5 | 0 | — | high | 18 GB of the 50 GB cap | user-selected toggle, not default |
| 8 | C6 Wikibooks / C7 OWID / C10 Wiktionary | ≈ 0–0.5 | 0.15–1 | < 3 | 4–16 | < 0.1 | high | 0.2–1 GB | post-deadline / skip |

Storage: an 8 GB-RAM phone is limited by RAM, not by disk. Packs are mmap-read SQLite. The bounty cap is 50 GB total, so the three small packs add under 50 MB. Crowding, not storage, is the binding cost. CROWDQ measured −0.019 (Opus) with 9 peer packs, so every new peer pack has to pass the frozen share rule or stay user-selected.

## 5. Plan
### Decisions (fixed for this plan; reversible)
| # | decision | why |
|---|---|---|
| D-G1 | Build only C1 and C2 by 10-21; C3 only if a fetch path works by 10-21 12:00 | highest items/GB and items/h; both reuse existing tooling (stageB fetch + cleaner; T-K1 PDF path) |
| D-G2 | No new pack enters the default kit before the claim; new packs are user-selected unless the frozen crowding rule passes on v0.1 + v0.2 **and** a kit no-harm replay shows 0 lost gold | claim kit is frozen at cut 7; CROWDQ cost |
| D-G3 | No V-para generation or judging for packs; V-para is touched only by the coverage probe (script-only, coordinator-run, T-K4d precedent, EXPOSURES row) | blind discipline; V-para is dev-style but the plan does not need answers on it |
| D-G4 | Each pack ships the D-K3 artefacts: card, 20 public self-tests, coverage probe, crowding probe | PACK-CATALOGUE rule |
| D-G5 | Freeze one criterion (sha256) before the coverage probes: per pack "new verified items not in the 6/34 union ≥ 2 → candidate for a kit no-harm test; 1 → user-selected; 0 → user-selected, product value only" | decide before seeing numbers |

### Options (open)
- O-G1: fold C2 into boar-crypto (re-cut, kit pack, no new peer) vs a separate boar-cryptostd pack. A re-cut avoids crowding but changes the claim kit hash, so it needs a kit no-harm replay on v0.1/v0.2 and V-exact. Default: separate pack by 10-23; re-cut after.
- O-G2: C1 as a peer pack vs routed by a lexical date trigger (year ≥ 2024, "latest", "recent", "this year"). The trigger is a narrow routing mechanism, not the closed top-1 router (R48). It needs its own step-0 gate. Default: peer, user-selected.
- O-G3: add C1b (Wikinews 2024–2026-05) into C1 or keep it separate (licence CC BY vs CC BY-SA: keep per-row licence either way).
- O-G4: ask r4to to rule on MIT (C4) and WTFPL (C5). Both are permissive, but neither is on this task's allowed list. boar-crypto already ships MIT parts.
- O-G5: C9 (full Wikipedia shards) as an advertised user-selected toggle for the 12 GB deep tier: a product statement, not a measurement.

### Tasks
| # | date | task | owner / model | cost | done when |
|---|---|---|---|---|---|
| G1 | 10-20 AM | Freeze D-G5 criterion (sha) + EXPOSURES pre-row | coordinator | 0 | sha in arms/packgap/ |
| G2 | 10-20 | C1 build: list `Portal:Current events/2024…2026` titles from the local 20261001 index (1,013 found), range-fetch their streams with stageB/fetch.py (est. < 0.5 GB), strip wikitext (the stage-B converter), one doc per day, date in the title and chunk header, add C1b Wikinews 2024+ if ≤ 1 h; build on the mini (disk free 33 GiB ≥ 25 policy) | sonnet/medium (runnable check: builder validate + sha + chunk count) | downloads < 0.5 GB (r4to rules allow CC BY-SA corpora); 0 LLM | pack + manifest + sha in DISK-LOG |
| G3 | 10-20/21 | C2 build: fetch the NIST PDFs (≈ 10 files) → pdftotext → section split (T-K1 PDF path) → build; credit line "Source: NIST (US public domain)" | sonnet/medium | < 50 MB download; 0 LLM | pack + card draft |
| G4 | 10-21 | Self-tests: 20 public items per pack (agent-written from pack text, seed-11 draw; selftest_draw.py), Haiku L1 with/without (80 calls per pack) | sonnet (writer), Haiku judge | 160 Haiku | SELFTEST-SCORES addendum |
| G5 | 10-21 | Coverage probe on V-para 34 absent items + v0.2 78 (dev): `arms/packs/tools/coverage_vpara.py --pack <sqlite>` (CAPC 20, TOPK 20), also reported on the 8 RATIONALEPASS recent-event ids (ids only) | **coordinator** (script-only on blind) | jev [usage detail removed]–0.05 per pack | counts per category; EXPOSURES row; D-G5 verdict |
| G6 | 10-21/22 | Crowding probe as peer to the claim kit (crowding.sh, v0.1 + v0.2 replays; share ≤ 0.40, kit gold not lower) | opus/medium | 0 LLM | status default-eligible / user-selected |
| G7 | 10-22 | V-exact check (public): 0-LLM retrieval replay of the 11 items with each pack; C2 must put a NIST source in kept for vx-002 (its rubric names FIPS 204/205 and SP 800-208); C1 must not displace kit gold on vx-001/vit-* | opus/medium | 0 LLM | pass/fail per pack |
| G8 | 10-22 | C3 go/no-go: if a fetch path works (no 403, robots allow), build + G4–G7 at reduced scope; else post-deadline | sonnet/medium | — | decision row in QUEUE |
| G9 | 10-23 | Cards (card wording rule), QUEUE rows; publication on r4topunk/boar-packs per the standing pack rule only for packs passing D-K3 (not part of this task) | coordinator | 0 | cards committed |

Minimum that closes the loop: G2 → G5 → G6 for C1 alone (one pack, one coverage metric, one crowding status). Next iteration: C2.

### Post-deadline (after 10-23)
- C4 ethereum.org re-cut + C5 the post author blog (after a licence ruling). Product value for crypto; v0.2 crypto absent 11/13.
- C8 SE 2026-06-30 sites: expatriates, law, fresher travel. Check the item's LICENSE.txt first.
- C7 OWID numeric rows. This needs a table → text row path (format 2 does not index table chunks).
- Monthly C1 refresh from each new dump (11-01). Per HoH (DEEP-RESEARCH B11), replace the old pages; never keep two revisions.
- A non-Claude v0.3 set (bench/v0.3) with pack-matched items is the only way to get a claim-grade number for any pack.

## 6. UNKNOWN
1. Whether the recent-event facts on V-para are in Portal:Current events at all. The 8 recent-event items are an H-arm count (RATIONALEPASS); the 4B's recent-event count was not measured. G5 answers this.
2. How many of the 6 NIST-citing V-para items are in the 34 absent set. CITEMAP-REF gives domains per item, not buckets. G5 answers this.
3. Whether `Portal:` pages fetched from the multistream dump strip cleanly. Daily pages are built from bulleted lists with templates (`{{Current events header}}` etc.); the stage-B cleaner drops non-listing templates.
4. travel.state.gov reachability for a crawler (WebFetch got 403 there and on state.gov), and the live wording of its copyright page. That wording was read only via a search excerpt of the primary page.
5. NIST: FIPS and Technical Series PD status is from NIST's general pages, read via search excerpts. Each PDF's front matter should be checked at build time (contractor-authored parts can carry copyright).
6. The licence text of the archive.org stackexchange_20260630 item (LICENSE.txt not displayed).
7. CDC Yellow Book reuse terms (print edition by OUP).
8. The capture rate (0.3–0.5) for newly covered items on the 4B. It comes from PACKCOND-P1 buckets (n = 6) and the DEEP-RESEARCH design arithmetic, not from a judged run.
9. Whether C1 crowds. Event pages are dense with entity names, so BM25 may hit them on non-news questions. G6 measures it.

## Sources
- Internal (rnd/research/coordinator/): VPARA-DIAGNOSIS-2026-10-19.md; arms/packs/T-K4d.md, T-K6b.md, WAVE3.md; arms/wikifull/STAGE-A.md, STAGE-B.md; arms/packcond/PACKCOND-P2.md; arms/deepwiki/DEEPWIKI.md; arms/rationalepass/RATIONALEPASS.md (CITEMAP-REF); CLOSED.md (R5, R6, R9, R29, R32, R34, R39, R44–R50, R68, R70, R72, R86, R93, R95); PACK-CATALOGUE-2026-10-12.md; REPORT-PACKS-2026-10-13.md; DEEP-RESEARCH-2026-10-12.md §2A, §4; packs-research/VERIFIED.md; EXPOSURES.md rows 145, 147, 157; ../packs/README.md and cards; compass/exp/bounty-eval/bench-vslice/questions.jsonl (vx-001, vx-002, vit-*); ../../../BOUNTY_31.md.
- Mini (read-only): enwiki-20261001-pages-articles-multistream-index.txt.bz2, `Portal:Current events/202[456]*` = 1,013 entries; disk free 33 GiB.
- Web (checked 2026-10-19):
  - Wikipedia Current events portal (daily subpage scheme): https://en.wikipedia.org/wiki/Portal:Current_events
  - Wikimedia dump licence (CC BY-SA 4.0 + GFDL): https://dumps.wikimedia.org/legal.html (VERIFIED.md 3b)
  - Wikibooks dump 207,777,448 B multistream, 2026-10-01: https://dumps.wikimedia.org/enwikibooks/latest/
  - Wiktionary dump 1,647,823,823 B, 2026-10-01: https://dumps.wikimedia.org/enwiktionary/latest/
  - Wikinews dump 47,537,899 B, 2026-10-01: https://dumps.wikimedia.org/enwikinews/latest/ ; licence CC BY 2.5 → CC BY 4.0 after 2024-12-16: https://en.wikinews.org/wiki/Wikinews:Copyright ; closure read-only 2026-05-04: https://meta.wikimedia.org/wiki/Wikimedia_News , https://heise.de/-11249432
  - NIST: https://www.nist.gov/oism/copyrights ; https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications ; https://www.nist.gov/itl/fips-general-information
  - US State Dept Consular Affairs copyright (PD unless marked; direct fetch 403): https://www.travel.state.gov/content/travel/en/copyright-disclaimer.html
  - OpenStax (CC BY-NC-SA): https://help.openstax.org/s/article/Licensing-information-of-OpenStax-textbooks
  - Our World in Data licence (CC BY, third-party data excepted): https://ourworldindata.org/faqs
  - ethereum.org repository licence (MIT): https://github.com/ethereum/ethereum-org-website/blob/dev/LICENSE
  - the post author's blog (WTFPL): https://github.com/vbuterin/blog
  - Stack Exchange 2026-06-30 community dump (91.8 GB, uploaded 2026-08-17): https://archive.org/details/stackexchange_20260630
  - CDC Yellow Book (print via OUP; reuse unverified): https://www.cdc.gov/yellow-book/hcp/about/index.html
