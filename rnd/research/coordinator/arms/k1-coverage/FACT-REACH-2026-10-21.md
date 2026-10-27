# FACT-REACH (B3): would any pack we have hold the key fact of the 20 no-source confident errors? (2026-10-21)

TL;DR
- Over the 20 no-source confident errors of K1-COVERAGE (bench v0.1 dev + qa-cooking/qa-money self-tests), the key fact is in: **(i) top-100k enwiki 7 yes + 2 partial; (ii) full enwiki 10 yes + 7 partial + 3 no; (iii) a published or wave-4 pack 16 yes + 4 partial; (iv) nothing we have: 0.**
- With the K0 kit packs added (boar-crypto, boar-wikivoyage-en), 18 of 20 are fully covered. The 2 left partial are cooking-020 (the 155-160 F target is covered, the reason the dairy is warmed first only partly) and sci-002 (the factbook gives area and population, so density must be computed).
- So for these 20, missing content is no longer the binding gap **if the topical packs are installed**. What remains is pre-retrieval routing (4 blocked: cooking-002, 013, 015, money-004), retrieval (3 facts already sat unretrieved in K0 packs) and reading. The content gaps K1 named have one owner pack each: cooking technique -> qa-cooking-se, US personal-finance rules -> qa-money-se, d/acc and Privacy Pools -> boar-vitalik-blog-en (+ boar-crypto's ERC-8262 entry), the Thai route -> boar-wikivoyage-en.
- **Strong caveat:** this result is partly true by construction. 13 of the 20 are self-test items that an agent wrote from the qa-cooking-se / qa-money-se text itself, and the vitalik pack was built on 10-21, the day after K1-COVERAGE named d/acc and Privacy Pools as gaps. It shows the packs hold what they were drawn from or built for. It is not evidence about unseen questions (v0.4, V-para).

Method: 0 LLM, 0 judge, 0 paid. Read-only FTS5 and whole-article reads with `tools/factq.py` (new; same reader as `packq.py`, every pack opened mode=ro) on the MacBook copies: top100k 9123b372, simplewiki (published fmt 2) c751768b, factbook c5854353, qa-cooking-se 81990fa9, qa-money-se 37411234, qa-travel-se a85521ce, qa-ethereum-se f16b258f, boar-crypto ae9fbd2c (local file, sha checked: the valid build), boar-wikivoyage-en ff8595e3. boar-vitalik-blog-en (94a7ec6e, sha checked) was copied read-only from the mini's wave4 into the scratchpad. (ii) **is not WIKIFULL**: stages A/B scored only V-para and v0.2 ids, and their shards were deleted. Here (ii) = top100k ∪ the live English Wikipedia read on 2026-10-21 (MediaWiki API plaintext extracts + search, about 30 requests with a generic UA, grepped by script). Live enwiki is 3 weeks newer than the enwiki-20261001 dump that WIKIFULL B used, so (ii) is an upper bound for "full enwiki at pack time".

## Per item
Y = key fact stated; P = partial (part of the fact, or derivable); N = absent. (iii) = 11 HF-published packs + wave-4 {vitalik, visa}; K0 = boar-crypto + boar-wikivoyage-en (kit, not on HF).

| id | key fact | (i) top100k | (ii) full enwiki | (iii) published / wave-4 | K0 kit | (iv) |
|---|---|---|---|---|---|---|
| lan-cmp-005 | saltwater croc largest living reptile | Y | Y | P simplewiki (up to 7 m, no Nile comparison) | Y Wikivoyage | — |
| lan-rsn-001 | ~21,196 km; not visible from the Moon | Y | Y | Y simplewiki | — | — |
| st-qa-cooking-se-002 | botulism; low O2 under oil; undetectable by taste | Y | Y | Y qa-cooking ("low acid and low oxygen"; "not detectable by odor or taste") | — | — |
| st-qa-cooking-se-003 | cartouche controls evaporation | N | P "Cartouche (cooking)": traps steam, lets some escape | Y qa-cooking ("Its purpose is to control the rate of evaporation") | — | — |
| st-qa-cooking-se-008 | pineapple non-climacteric | Y | Y | Y qa-cooking ("softens, but not sweeten") | — | — |
| st-qa-cooking-se-012 | French oven = enamelled Dutch oven | Y | Y | Y qa-cooking ("french oven (aka enameled dutch oven)") | — | — |
| st-qa-cooking-se-013 | salt scrub / burn off / lye; re-season | N | Y "Seasoning (cookware)": salt scrub; stripped with lye or burned off | Y qa-cooking ("Scrub ... with Kosher salt ... start all over again seasoning") | — | — |
| st-qa-cooking-se-015 | breast overcooked; carryover; brine | N | P "Carryover cooking" exists; no bird breast/thigh text | Y qa-cooking (breast "dries out beyond 150 F", thigh "170 F"; dry brine) | — | — |
| st-qa-cooking-se-020 | dissolve sugar; temper yolks; 155-160 F | P custard sets 70 °C | P same | P qa-cooking (hot milk poured slowly into yolks + sugar; no sugar-dissolving reason) | — | — |
| st-qa-money-se-004 | money-flipping scam; stolen money | N | P "Advance-fee scam" (search snippet only) | Y qa-money ("send me 1000 dollars and I have to send half back"); simplewiki "money flipping" | — | — |
| st-qa-money-se-007 | 12 USC 1759(b) common bond | N | Y "Credit unions in the United States": 1934 Act "common bond of occupation or association" | Y qa-money ("field of membership" / "common bond") | — | — |
| st-qa-money-se-009 | taxable account taxed twice; deferral ~ Roth; match | P | P | Y qa-money (several 401k vs taxable threads) | — | — |
| st-qa-money-se-010 | prior-year HSA needs HDHP eligibility that year | N | N "Health savings account" has no prior-year rule | Y qa-money (exact case: "you cannot make any HSA contributions for 2020") | — | — |
| st-qa-money-se-011 | RSU income at vest; vest value = basis | N | P "Restricted stock": vesting only, no tax/basis | Y qa-money ("taxed as compensation ... when they vest ... becomes your cost basis") | — | — |
| st-qa-money-se-020 | I-bond rate tracks CPI-U, not the Fed | N | Y "United States Savings Bonds": variable component = CPI-U | Y qa-money ("I Bond rates are linked to current inflation ... while the Fed increases") | — | — |
| vit-cry-005 | Privacy Pools association sets vs Tornado Cash | N | N (no article; 0 search hits; not in "Tornado Cash") | Y vitalik ("Why I support privacy": prove coins come from a source not on a list of hacks); qa-ethereum-se N | Y crypto ERC-8262 | — |
| vit-cry-007 | d/acc = defensive accelerationism (2023) | N | N (only a video title cited in "P(doom)") | Y vitalik ("d/acc: one year later", "My techno-optimism") | N | — |
| vit-hum-004 | taunted Gríma kills Saruman | Y | Y | Y simplewiki | — | — |
| vit-sci-002 | Japan ~330 vs Germany ~236 /km² | Y | Y | P factbook (area + population for both: 123.2 M / 377,915 km², 84.0 M / 357,022 km²; derivable) | — | — |
| vit-trv-003 | Arcade minivan ~3 h, 135 km Rte 1095, winding | N | P "Pai, Thailand" (Route 1095, 146 km) + "Highway 1095 (Thailand)" (> 2,000 curves) | P qa-travel-se (≈ 3 h, ≈ 120 km, "762 turns"; no minivan/terminal) | Y Wikivoyage Pai (minivans hourly from Arcade terminal, ≈ 3 h) | — |

Totals: (i) Y 7, P 2, N 11 · (ii) Y 10, P 7, N 3 · (iii) Y 16, P 4, N 0 · (iii) ∪ K0: Y 18, P 2 · (iv) 0.

## The "nothing" group, narrowed to named content gaps
No item is uncovered by every pack. The gaps K1 named are closed by topical packs. General encyclopedias do not close them: full Wikipedia still misses 3 (HSA rule, Privacy Pools, d/acc) and is only partial on 7.

| named gap | items | what covers it | size now | size of a covering slice (estimate) |
|---|---|---|---|---|
| everyday cooking technique / food safety | cooking-002, 003, 008, 012, 013, 015, 020 | qa-cooking-se (published) | 88,973,312 B | ≈ 17.5 MB: tags food-safety, cast-iron, ice-cream, chicken, roasting, equipment, fruit = 4,933 posts, 19.7 % of text (11.2 MB text × 1.57 file/text) |
| US personal-finance rules (HSA, RSU, I bond, credit unions, 401k) | money-004, 007, 009, 010, 011, 020 | qa-money-se (published, user-selected only) | 137,240,576 B | ≈ 58 MB for the US/tax/retirement tag slice (15,575 posts, 42.6 % of text); ≈ 1.9 MB for just the hsa/rsu/savings-bond/credit-union tags (485 posts, 1.4 %), which covers 4 of the 6 |
| recent crypto concepts (d/acc, Privacy Pools) | cry-005, cry-007 | boar-vitalik-blog-en (wave-4, user-selected only); Privacy Pools also boar-crypto ERC-8262 | 8,806,400 B | whole pack (8.8 MB); not on Wikipedia at all |
| Thai route logistics | trv-003 | boar-wikivoyage-en (kit, not on HF); partial in qa-travel-se | 351,092,736 B | Wikivoyage Thailand pages only, a few MB (not measured) |
| encyclopedic facts | lan-cmp-005, lan-rsn-001, hum-004, sci-002 | top100k / simplewiki / factbook | 2.54 GB / 480.5 MB / 11.6 MB | already covered; size not the issue |

Smallest set that covers the 15 cooking, money and crypto items ≈ 17.5 + 58 + 8.8 ≈ **84 MB** of slices, against 235 MB for the three whole packs. Slice sizes are estimates from text share; they were not built.

## What it implies
- For dev items like these, the answer to "does BOAR have the content?" is now mostly yes. The measured failures sit downstream: health/places routing blocks 4 before retrieval, K0 already held 3 facts it never retrieved, and with the fact kept the 1.7B still answered 2 of the 20 wrong, plus the 3 reading-failure items and hum-005 (K1-COVERAGE). The next lever is routing + retrieval on topical packs, not another corpus.
- That conclusion holds **only for pack-matched dev items** (see TL;DR caveat). The held-out check is the v0.4 in-pack stratum (ruler/INPACK-STRATUM-2026-10-21.md). There, "in-pack" is a domain match, so this file's lesson (reach ≠ answer) must sit next to every in-pack number.
- Installing all of these packs together is what arm D tests (crowding). Topical SE packs took few slots in the crowding probes (qa-cooking-se 2 %); top100k took 98 %.

## Side finding
- boar-vitalik-blog-en contains Chinese-language posts (e.g. chunks 2773 and 5782, CJK text), although its card says "English only" and lists only the On_Collusion translations as excluded. The card or the converter's language filter needs a fix before any publish.

## Files
- `tools/factq.py`: read-only multi-pack query (`BOAR_PACKS` overrides the root).
- Wikipedia extracts were read in the session scratchpad and are not kept (live pages, reproducible with the API calls named above).
