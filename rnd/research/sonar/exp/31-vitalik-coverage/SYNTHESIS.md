# the post author's example questions: coverage, ≤ 50 GB pack plan, places/GPS (Sonar, 2026-10-03)

TL;DR (from A-pack-coverage.md, B-pack-budget.md, C-places-gps.md; Sonar's re-checks are noted inline):
- **"Vegan restaurants near me" does not work on Android today.** Re-checked on current boar-app `origin/main` 7aa67d5a:
  - `registerGeoProviders` is defined (`src/routing/answerService.ts:39`) but never called, so `getGeoProviders()` is null and the places path ends in "places pack not installed".
  - The engine and data work on desktop: 18 questions, Berlin/Lisbon/São Paulo give 10 real OSM vegan venues in 12–130 ms. The world data is built (8,374 tiles, 980 MB, 51,840 vegan-tagged venues).
  - **Correction to C:** current main DOES declare FINE/COARSE location (`plugins/withBuildVariant.js:43-45,142`, loaded by `app.config.js`). C audited 38f996d1, which is not on main.
- **The default kit misses most humanities and country answers.** Of 23 the post author-style items, 11 are answerable in kit A, 3 more with wiki-vital5, 6 only in built-but-unshipped Wikipedia packs, 3 nowhere. vital5 has lead sections only (Japan: 1.7k characters vs 54k).
- **When the answer IS installed, retrieval loses it** (5 of 14 reach the model):
  - compression or the wrong section loses 6 (Mozi comparison, PQC/ECDSA, FOCIL, DAO, Chiang Mai→Pai, Lisbon airport);
  - gates drop 2 (altitude, Kenya);
  - crypto noise fills all slots for 1 ("Explain Mozi's views…" → TrueCrypt).
- **the post author's two weak exact items:**
  - **Gríma/Saruman:** a coverage gap; the 4B is confidently wrong, not over-refusing. The sentence exists only in top100k.
  - **Paris–Rome:** no text anywhere states the distance. Fix it with a local distance tool (gazetteer coordinates + `distanceMeters`: 1,107 km great-circle), not a pack.
- **Storage is not the constraint; retrieval precision is.** Catalog with everything ≈ 41 GB; recommended plan S1 ≈ 24.6 GB (B). Every past "bigger pack" arm failed the gate on noise (#6, #6b, #17), so any added text needs tiered or filtered retrieval.

> **Board alignment (BOUNTY-BOARD.md, 2026-10-03):** English only. No work inside the app maintainer's app: task 1 (Android places wiring) is a finding for the end-of-bounty PR, measured through boar-eval / BOAR Bench. Sonar's front = #2 (V-exact, V-para); 2-hour time box per idea.

## Decisions / Options / Tasks
**Decisions (reversible, Sonar's lane):**
- Licenses rejected: Stanford Encyclopedia of Philosophy (no redistribution), ethresear.ch (CC BY-NC-SA), the post author's blog repo (no license), WorldClim.
- the post author's own posts can't be packed; cover their topics via Wikipedia, EIPs and the crypto pack.

**Ranked tasks** (impact on a the post author demo ÷ effort):
| # | Task | Owner (proposed) | Effort | Evidence |
|---|---|---|---|---|
| 1 | Android places wiring: call `registerGeoProviders(geoProvidersFrom(…))` at app start (10 lines exist on `ios_android` `src/ui-ios/App.tsx:25-35`); add the gazetteer + tiles to the downloadable catalog; "Use my location / Type a city" for the prompt, denied and stale cases; GPS wait 10 s → ~30 s (no A-GPS offline) | PR to the app maintainer at the end (board rule: no app work now) | S–M | C §2, §5; re-check above |
| 2 | Places quality: restaurant filter when asked for "restaurants" (2–4 of 10 are gelaterias/bars); "near <landmark>", "plant-based/veggie", "why are there so many vegan…" (not a list), "groceries", "open now" | Sonar (geo.ts intent) | S | C §4 (24 intent probes) |
| 3 | Travel arithmetic tool: "how far / how long from X to Y (and back)": gazetteer coordinates → great-circle + a stated road/rail factor, with an explicit "approximate, straight-line ×1.25" line | Sonar (engine calculators) | S | A §3b (Paris–Rome 0.29 vs 0.65) |
| 4 | Keep the key through compression for named entities/acronyms: the PQC answer names ML-DSA/SLH-DSA/FIPS 204/205 but they are dropped; same class for Mozi, FOCIL, DAO | Sonar (P-1 style) | M | A §3 |
| 5 | Domain gate for crypto-pack noise on non-crypto questions (Mozi → TrueCrypt). The translated-PT guard from health11 generalised by a topic check | Sonar | S | A §3 |
| 6 | Tiered Wikipedia: top-100k always + long tail (full EN 18.4 GB, built and hosted) via exact title lookup or when the first pass is thin. the post author's titles: 14/32 in the top-100k, 25 in the top-300k, 30 in the top-1M | Sonar + Kiln | L | B §1–3; past failures #6/#6b/#17 |
| 7 | Cheap packs (~1.9 GB): NIST FIPS 203/204/205 + RFCs + IACR/arXiv abstracts; Stack Exchange 8 sites; public-domain Mozi/Chinese classics; country facts + visa tables; GeoNames cities500; Overture vegetarian | Sonar (build) | M | B §3 |

**Options (not decided):**
- S1 ≈ 24.6 GB (4B + full-EN tiered + cheap packs + world places).
- S2 ≈ 45.8 GB (S1 + Qwen3.6-35B-A3B 12.3 GB + Maple). Anvil owns the model tier.

## UNKNOWN
- What the Android chat answers today for "vegan near me" (likely model text with possibly invented venues): no device run.
- Search speed and RAM with 15+ packs open on the phone; whether the 4B uses longer passages; true sizes of the new packs; whether Overture and OSM data can be combined (licences).
