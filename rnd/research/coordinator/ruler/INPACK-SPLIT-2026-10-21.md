# INPACK-SPLIT (2026-10-21): on real dev questions, in-pack items are NOT easier, and loading the matching pack does not lift them (K3-K0 on 17 matched items -0.023 [-0.081, +0.027]); the pack gain exists only on pack-written self-tests (+0.056 [+0.018, +0.096])

TL;DR (post-hoc, 0 LLM, 0 generation, 0 paid; existing Haiku 5.5-low judgments only)
- Rule: an item is IN-PACK when its domain tag is covered by a topical carded pack (table §1); general encyclopedias (simplewiki, vital5, top100k) do not count, otherwise every item is in-pack.
- MAIN 97 (72 in / 25 off): every system scores LOWER in-pack than off-pack (gap -0.04 to -0.08; only the 4B's CI excludes 0: -0.081 [-0.152, -0.005]). Cause: the 40 cooking/money SE self-test items (U about 0.35) and the 15 crypto/travel items (U 0.37-0.42) are the hardest slices.
- v0.1 57 alone (32 in / 25 off) and the phone 57: in-pack = off-pack within noise for every system (gaps -0.05 to +0.01, all CIs straddle 0, half-widths about 0.10).
- Matching pack loaded vs not (1.7B, MAIN items whose pack K0 lacks and K3 adds: health, first aid, country; n 17): -0.023 [-0.081, +0.027]; the simplewiki-only control K1 gives -0.026 on the same items. Self-tests of the same packs (topical 60): +0.056 [+0.018, +0.096] (1.7B), +0.076 [+0.025, +0.123] (Gemma). The self-test gain is an upper bound that does not transfer to the dev questions.
- Model gaps do not concentrate in-pack: 4B - 1.7B is +0.068 in-pack vs +0.099 off-pack (DiD CI -0.086...+0.024); Gemma - 1.7B +0.031 vs +0.021.

Script: tools/inpack_split.py (sha256 6a25ec73...); outputs inpack-split.json (sha256 a4f1996e...) and the per-id assignment inpack-assignment.json (sha256 **ee307470b45bd7a848904dd65dbb09ed1b8c89b685390378bd28367c50323703**, 277 ids: 57 v0.1 + 40 MAIN cooking/money + 180 self-tests). Rerun: `python3 -I tools/inpack_split.py .` from this folder.

## 1. Tag -> pack rule (candidate for freezing)
| tag | side | packs whose card domain covers it | how items get the tag |
|---|---|---|---|
| crypto | IN | boar-crypto, qa-ethereum-se, qa-bitcoin-se | v0.1 vit-cry-*; self-tests qa-ethereum-se, qa-bitcoin-se |
| travel | IN | boar-wikivoyage-en, boar-visa-en, qa-travel-se | v0.1 trv-*, vit-trv-*; self-tests qa-travel-se |
| health | IN | boar-medlineplus-en, qa-health-se | v0.1 lan-hlt-*, vit-hlt-003 (category health); self-tests medlineplus, qa-health-se |
| firstaid | IN | boar-firstaid-en, boar-preparedness, qa-outdoors-se | v0.1 category danger / danger-situation (vit-hlt-001/002, dng-*); self-tests firstaid |
| country | IN | boar-factbook | v0.1 country-level fact questions (capital, area, population, independence, languages of a sovereign state or territory): lan-exp-001/002/003/007, lan-cmp-001/003, lan-ref-004, vit-sci-002; self-tests factbook |
| cooking / money / outdoors | IN | qa-cooking-se / qa-money-se / qa-outdoors-se | id prefix st-qa-cooking-se / -money-se / -outdoors-se |
| general-encyclopedia | IN (self-tests only, reported apart) | boar-simplewiki-en | id prefix st-boar-simplewiki-en |
| place-other | OFF (alt: IN, sensitivity) | none topical (wikivoyage destination articles could match; the persona map gives wikivoyage to travel, not place overviews) | cities, landmarks, natural features: lan-exp-004/005/006, lan-rsn-001/002/005 |
| humanities | OFF | none | vit-hum-* |
| history-culture | OFF | none | lan-ref-001/002/003/005, lan-rsn-004/006/007 |
| nature | OFF | none | lan-cmp-002/004/005, lan-rsn-003 (animals) |
| science-tech | OFF | none (no carded pack names general science or CS) | vit-sci-001 (far-UVC), vit-sci-003 (phone token arithmetic) |

Order of application: self-test id prefix -> its pack's tag; v0.1 category (health, danger*, crypto, travel-*) -> tag; else id prefix (cry, trv, hlt, hum) -> tag; else the question topic (country / place-other / history-culture / nature / science-tech). The question text of v0.1 was read only to assign these last tags (21 lan-* items + vit-sci-*); nothing was tuned. Arm kits (which tags have a covering pack loaded): K0 = crypto, travel (claim kit: boar-crypto + boar-wikivoyage-en; no visa pack); K1 = K0 + simplewiki; K2 = K1 + country; K3 = K2 + health, firstaid; Gemma/4B K0 and both phone runs = the claim kit, i.e. K0.

## 2. Per set and system: in-pack vs off-pack U (ratio of sums, declined := 0; phone = raw ratio), 95 % CI (B 2000, seed 11; gap = sides resampled independently)
### MAIN 97 (in 72 = v0.1 32 + cooking 20 + money 20; off 25)
| system | U all | U in [CI] | U off [CI] | gap in - off [CI] |
|---|---|---|---|---|
| 1.7B K0 (LITEPACKS, MacBook) | 0.406 | 0.395 [0.357, 0.434] | 0.438 [0.365, 0.514] | -0.043 [-0.127, +0.040] |
| 1.7B K1 | 0.396 | 0.377 [0.340, 0.415] | 0.449 [0.377, 0.525] | -0.072 [-0.154, +0.009] |
| 1.7B K3 | 0.394 | 0.375 [0.338, 0.414] | 0.449 [0.376, 0.527] | -0.074 [-0.155, +0.009] |
| 1.7B K0 control s42 (mini) | 0.405 | 0.393 [0.353, 0.433] | 0.441 [0.376, 0.512] | -0.048 [-0.127, +0.028] |
| Gemma E2B K0 s42 | 0.434 | 0.423 [0.386, 0.463] | 0.462 [0.387, 0.538] | -0.039 [-0.122, +0.047] |
| Gemma E2B K0 s43 | 0.432 | 0.422 [0.385, 0.461] | 0.461 [0.389, 0.538] | -0.039 [-0.121, +0.040] |
| Gemma E2B K1 s42 | 0.428 | 0.414 [0.380, 0.450] | 0.465 [0.390, 0.547] | -0.051 [-0.139, +0.034] |
| 4B K0 s42 | 0.481 | 0.460 [0.421, 0.500] | 0.541 [0.475, 0.601] | **-0.081 [-0.152, -0.005]** |
Sensitivity (place-other counted IN, 78/19): gaps -0.052...+0.002, all CIs straddle 0.

### v0.1 57 alone (in 32, off 25)
| system | U in [CI] | U off [CI] | gap [CI] |
|---|---|---|---|
| 1.7B K0 | 0.445 [0.384, 0.510] | 0.438 [0.365, 0.514] | +0.007 [-0.089, +0.106] |
| 1.7B K1 | 0.417 [0.352, 0.485] | 0.449 [0.377, 0.525] | -0.032 [-0.129, +0.070] |
| 1.7B K3 | 0.428 [0.361, 0.496] | 0.449 [0.376, 0.527] | -0.021 [-0.122, +0.081] |
| Gemma K0 s42 / s43 | 0.450 / 0.437 | 0.462 / 0.461 | -0.012 / -0.024 (CIs about ±0.10) |
| Gemma K1 s42 | 0.458 [0.396, 0.520] | 0.465 [0.390, 0.547] | -0.007 [-0.108, +0.099] |
| 4B K0 s42 | 0.509 [0.443, 0.571] | 0.541 [0.475, 0.601] | -0.032 [-0.121, +0.059] |

### Phone v0.1 57 (raw ratio, agg_device.py loader; in 32, off 25)
| system | U in [CI] | U off [CI] | gap [CI] |
|---|---|---|---|
| phone Gemma E2B (Pixel 8a) | 0.451 [0.391, 0.514] | 0.453 [0.378, 0.537] | -0.002 [-0.104, +0.102] |
| phone 4B cut 7 (Pixel 8a) | 0.520 [0.457, 0.584] | 0.555 [0.485, 0.616] | -0.035 [-0.123, +0.058] |
| desktop 1.7B K0 two-seed (mini) | 0.441 [0.381, 0.510] | 0.448 [0.383, 0.518] | -0.007 [-0.097, +0.086] |
| desktop Gemma K0 two-seed | 0.444 [0.381, 0.512] | 0.461 [0.390, 0.537] | -0.017 [-0.112, +0.081] |
| desktop 4B cut 7 s42 | 0.508 [0.448, 0.566] | 0.557 [0.479, 0.627] | -0.049 [-0.141, +0.044] |
No 57-id phone 1.7B run exists (only 26 ids, cmp30-q17); the desktop 1.7B two-seed stands in.

### Self-tests 80 / 180 (all IN by construction: upper bound only)
| set | 1.7B K0 | 1.7B K3 | Gemma K0 | Gemma K3 |
|---|---|---|---|---|
| 180 (80 cand + 100 SE) | 0.377 [0.357, 0.399] | 0.407 [0.385, 0.430] | - | - |
| cand 80 | 0.393 [0.364, 0.421] | 0.462 [0.427, 0.495] | 0.395 [0.365, 0.424] | 0.497 [0.459, 0.535] |
| topical 60 (cand minus simplewiki) | 0.404 | 0.461 | 0.400 | 0.476 |
| K3 - K0 on topical 60 (own pack loaded) | | +0.056 [+0.018, +0.096] | | +0.076 [+0.025, +0.123] |
Per pack (1.7B, n 20, K0 -> K3): factbook 0.352 -> 0.456, medlineplus 0.441 -> 0.497, firstaid 0.421 -> 0.427, simplewiki 0.360 -> 0.466; SE: travel 0.336 -> 0.319, ethereum 0.336 -> 0.313, bitcoin 0.362 -> 0.351 (domain pack loaded in both arms), health 0.419 -> 0.425 (medlineplus is a domain match, not the SE pack), outdoors 0.368 -> 0.394 (no covering pack loaded).

## 3. With the matching pack loaded vs without (1.7B, MAIN, paired item bootstrap)
| contrast (items) | n | U without | U with | delta [CI] | answers changed |
|---|---|---|---|---|---|
| **K3 - K0, health + firstaid + country (pack added only in K3)** | 17 | 0.510 | 0.487 | **-0.023 [-0.081, +0.027]** | 12 |
| K3 - K0, health + firstaid (medlineplus, firstaid) | 9 | 0.542 | 0.496 | -0.046 [-0.101, +0.004] | 6 |
| K2 - K0, country (factbook) | 8 | 0.475 | 0.471 | -0.004 [-0.107, +0.069] | 6 |
| K1 - K0, same 17 (control: simplewiki only, no matching pack) | 17 | 0.510 | 0.484 | -0.026 [-0.076, +0.013] | 10 |
| K3 - K1, same 17 (matching packs beyond simplewiki) | 17 | 0.484 | 0.487 | +0.003 [-0.040, +0.049] | 7 |
| K3 - K0, off-pack (no matching pack exists) | 25 | 0.438 | 0.449 | +0.011 [-0.028, +0.059] | 17 |
| DiD: matched 17 minus off-pack 25 | | | | -0.034 [-0.104, +0.031] | |
| K3 - K0, cooking + money (in-pack, pack never loaded in any arm) | 40 | 0.353 | 0.331 | -0.023 [-0.058, +0.012] | 24 |
| K3 - K0, crypto + travel (pack loaded in both) | 15 | 0.366 | 0.357 | -0.009 [-0.042, +0.026] | 13 |
Not available: crypto/travel without their pack (every measured arm loads the claim kit), cooking/money with their pack (no arm loads qa-cooking-se / qa-money-se), Gemma or 4B with K3 on MAIN.

Within K0 (cross-sectional, MAIN): covering pack loaded (crypto + travel, 15) U 0.366 [0.283, 0.474]; in-pack but not loaded (57) 0.402; off-pack (25) 0.438. Same order for Gemma K0 (0.400 / 0.430 / 0.462) and the 4B (0.415 / 0.472 / 0.541): the items that have a loaded pack are the hardest ones, so domain coverage is a difficulty marker on this set, not an advantage.

## 4. Model deltas by side (MAIN, paired, K0 s42, mini)
| pair | in-pack (72) | off-pack (25) | DiD CI |
|---|---|---|---|
| 4B - 1.7B | +0.068 [+0.038, +0.100] | +0.099 [+0.058, +0.146] | -0.086...+0.024 |
| Gemma - 1.7B | +0.031 [+0.004, +0.059] | +0.021 [-0.025, +0.072] | -0.047...+0.061 |
| 4B - Gemma | +0.037 [+0.006, +0.069] | +0.079 [+0.030, +0.126] | -0.097...+0.013 |

## 5. Caveats
- Post-hoc split of existing sets, decided after the numbers of every run were known (not after this split's numbers: the rule in §1 was written before the first computation, and the alt variant is the only sensitivity run). Freeze the §1 table (plus the assignment sha256) before using it on any new set.
- IN-PACK = domain match on the pack card, not fact presence: an in-pack item can have its answer absent from the pack (cf. PACK coverage probes: cooking/money 0/34 V-para facts). A fact-presence split needs retrieval replay or jev F0 per item; not done here.
- Haiku 5.5-low judge (judge.v1-low, compresses gaps), one seed per run (Gemma K0 two seeds), dev sets only; the 1.7B LITEPACKS rows run on the MacBook and the Gemma/4B/control rows on the mini (cross-host pairs avoided in §3 and §4).
- Small strata: off-pack n 25 and the matched contrast n 17 give CI half-widths of 0.05-0.10; no split difference here is below that resolution except the 4B MAIN gap.
- MAIN's in-pack side is 56 % cooking/money self-tests (pack-written, never pack-loaded), so the MAIN gap mixes "in-pack" with "self-test style"; the v0.1-only table is the cleaner real-question split.
- Self-test rows are an on-topic ceiling (questions written from the pack), never a casual-traffic estimate.
- Exposure: no blind/, no rnd/veil, no v0.4 text read; v0.1 question text read only for §1 tags.
