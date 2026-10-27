# K1-COVERAGE: why Simple English Wikipedia (K1) and top-100k enwiki (K4) do not fix the 1.7B's no-source confident errors

TL;DR
- Of the 20 K0 confident errors (CE) with no relevant source, only 2 have the fact in a new pack that retrieval skips (both top100k), and 2 have it retrieved yet answered wrong. 6 are absent from both packs, and 4 never reach retrieval (places/health refusal).
- The 6 "fixes" are mostly not pack wins: 2 are grounded, 2 partly grounded, 2 are memory answers at correctness 2.0-3.0. K1 also creates as many new CEs as it fixes (6 in, 6 out, see lp-screens).
- The gap is content first (10 of 20 key facts are in neither new pack; 3 of the 20 are in K0's own packs but never retrieved), then the pre-retrieval routing (4), then retrieval and reading (2 + 2). The 6 reading failures stay reading failures: 3 are still wrong with the same source kept, and 3 flip to correctness 2.0, which is within judge noise.

Method: 0 LLM calls, no judge calls. The data are the LITEPACKS MacBook traces and judgments (Haiku 5.5-low, judge.v1-low; K1/K4 reuse K0 rows when the answer bytes are identical), the references and author notes from the public bench v0.1 and the qa-cooking-se / qa-money-se self-tests, and read-only queries on the packs: simplewiki v3proto `99bcec30`, top-100k `9123b372`, wikivoyage `ff8595e3`, crypto `ae9fbd2c`, all with the full sha256 checked. Queries used FTS5 plus whole-article reads (`tools/packq.py`; the chunk text comes from the zstd blocks). Tools: `tools/dossier.py` (per-item traces/judgments → /tmp/k1-coverage-dossier.json, kept out of git) and `tools/build.py` (classification → k1-coverage.jsonl).

Caveat: traces log the kept **titles**, not the kept chunk text. "Fact in kept" therefore works at article level. A "yes" for a long article is backed by answer text that echoes the fact chunk (hum-004 "hobbit archers", hum-005 "Book IV, Chapter II") or by the fact sitting in the article lead (cooking-012). Fixes are flagged by grounding because the judge flips about 5 % of CE items on re-judging the same text (lp-screens/SCREENS.md). A fix at correctness 2.0 is weak evidence.

## Counts

| Class | No-source (20) | Reading failures (6) | Unclear label (1) |
|---|---|---|---|
| absent_from_both | 6 (2 present in K0 packs: cry-005, trv-003) | 0 | 0 |
| present_simplewiki_not_retrieved | 0 (+1 blocked: money-004) | 0 | 0 |
| present_top100k_not_retrieved | 2 (+1 blocked: cooking-002) | 0 | 0 |
| retrieved_but_wrong | 2 | 3 | 1 |
| fixed_in_K1_or_K4 (not CE in K1 or K4) | 6 (grounded 2, partial 2, weak/ungrounded 2) | 3 (all weak, correctness 2.0) | 0 |
| blocked_before_retrieval (extra class) | 4 (places route 1, health decline 3) | 0 | 0 |
| unclear | 0 | 0 | 0 |

Content view of the 20 no-source items: the key fact is absent from simplewiki and top100k for 10 (cooking-003, 013, 015, money-007, 010, 011, 020, cry-005, cry-007, trv-003; money-007 has only "member-owned", not the legal rule). It is present in at least one new pack for 8. Of those 8, 4 had it retrieved in K1/K4 (lan-cmp-005, lan-rsn-001, cooking-012, hum-004), 2 did not (cooking-008, sci-002), and 2 were blocked (cooking-002, money-004). Coverage is partial for the other 2 (cooking-020, money-009). In addition, 3 no-source items have the fact in the **K0** packs, unretrieved: lan-cmp-005 and trv-003 in Wikivoyage, cry-005 in crypto.

## Per item

Abbreviations: K1/K4 ret = whether the arm's kept context holds the fact (yes / partial / no / none = nothing retrieved). Corr = judge correctness, the mean of both orders (CE ≤ 1.5).

### No-source CEs (20)

| id | Key fact | K1 ret (corr) | K4 ret (corr) | Presence quote (≤ 25 words) | Class |
|---|---|---|---|---|---|
| lan-cmp-005 | Saltwater croc is the largest living reptile | partial (3.0) | yes (3.5) | top100k: "The saltwater crocodile is the largest living reptile." (also K0 Wikivoyage Nusa Tenggara) | fixed (grounded) |
| lan-rsn-001 | ~21,196 km; not visible from the Moon | yes (2.5) | yes (1.5) | simplewiki: "Neil Armstrong, said that on the Moon, it was very clear that the wall was not visible." | fixed (grounded); K4 mislabels km as miles |
| st-qa-cooking-se-002 | Botulism; low O2 under oil; tasteless toxin | none (1.0) | none (1.0) | top100k: "garlic or herbs stored covered in oil without acidification"; "tasteless" in neither pack | blocked (places route); top100k present |
| st-qa-cooking-se-003 | Cartouche controls evaporation | no (1.0) | no (1.0) | none ("cartouche" = Egyptian hieroglyph / map ornament only) | absent_from_both |
| st-qa-cooking-se-008 | Pineapple non-climacteric, won't sweeten | no (1.5) | no (1.5) | top100k: "A pineapple never becomes any riper than it was when harvested since it is a non-climacteric fruit." | present_top100k_not_retrieved |
| st-qa-cooking-se-012 | French oven = enamelled Dutch oven, marketing name | no (1.0) | yes (1.0) | top100k (Dutch oven lead): "Some metal varieties are enameled rather than being seasoned, and these are sometimes called French ovens." | retrieved_but_wrong (K4) |
| st-qa-cooking-se-013 | Salt scrub / burn off / lye; re-season | none (1.0) | none (1.0) | none | blocked (health decline); absent |
| st-qa-cooking-se-015 | Breast overcooked; carryover; brine | none (1.0) | none (1.0) | none (only "Breast: These are white meat and are relatively dry.") | blocked (health decline); absent |
| st-qa-cooking-se-020 | Dissolve sugar; temper yolks; 155-160 F | no (1.5) | partial (2.0) | top100k Custard: "it begins setting at 70 °C (158 °F)" | fixed (weak, memory answer) |
| st-qa-money-se-004 | Scam (money flipping); stolen money | none (1.0) | none (1.0) | simplewiki: "money flipping, whereby the mark is promised a large amount of money in exchange for sending a small amount of money." | blocked (health decline); simplewiki present |
| st-qa-money-se-007 | 12 USC 1759(b) common bond | partial (2.5) | no (1.5) | simplewiki: "owned and controlled by its members" (no common bond in either pack) | fixed (partial) |
| st-qa-money-se-009 | Taxed twice in taxable; deferral ~ Roth; match | no (1.5) | partial (2.5) | top100k 401(k): "may be matched by the employer" | fixed (partial) |
| st-qa-money-se-010 | Prior-year HSA needs HDHP eligibility that year | no (1.5) | none (1.0) | none (no HSA article) | absent_from_both |
| st-qa-money-se-011 | RSU income at vest; vest value = basis | no (2.5) | no (3.0) | none (no RSU text) | fixed (ungrounded, memory) |
| st-qa-money-se-020 | I bond rate tracks CPI-U, not the Fed | no (1.0) | no (1.0) | none (only generic inflation-indexed bonds) | absent_from_both |
| vit-cry-005 | Privacy Pools association sets vs Tornado Cash | no (1.0) | no (1.5) | none in sw/top; K0 crypto ERC-8262: "prove their withdrawal originates from a "clean" deposit set using ZK proofs" | absent_from_both (in K0, unretrieved) |
| vit-cry-007 | d/acc = defensive accelerationism (2023) | no (1.0) | no (1.0) | none (not in crypto pack either) | absent_from_both |
| vit-hum-004 | Scouring of the Shire: taunted Gríma kills Saruman | yes (1.5) | yes (1.0) | simplewiki: "After the hobbit uprising, Gríma kills Saruman; Gríma is killed by hobbit archers." | retrieved_but_wrong |
| vit-sci-002 | Japan ~330 vs Germany ~236 /km² | partial (1.0) | no (1.0) | top100k: "Density: 330/km2" (Japan); "population density stands at 236 inhabitants per square kilometre" (Germany) | present_top100k_not_retrieved |
| vit-trv-003 | Arcade minivan ~3 h, 135 km Rte 1095, winding | no (1.0) | no (1.0) | none in sw/top; K0 Wikivoyage Pai: "Chiang Mai (135 km) ... steep and winding drive, with lots of curves" | absent_from_both (in K0, unretrieved) |

### Reading failures (6) and the unclear-label item (1)

| id | Key fact | K1 ret (corr) | K4 ret (corr) | Presence quote | Class |
|---|---|---|---|---|---|
| lan-cmp-004 | Bison bull outweighs moose bull | partial (2.0) | partial (1.0) | (K0 Wikivoyage: moose "upward of 1500 lb" only) | fixed (weak, 2.0) |
| lan-exp-007 | Denmark autonomy, Nuuk, ~56k, ~80 % ice | partial (2.0) | partial (1.5) | simplewiki: "Greenland is a self-governing territory of the kingdom of Denmark." | fixed (weak, 2.0; population still wrong) |
| lan-rsn-003 | Cheetah; sprint only 20-30 s | yes (1.5) | yes (2.0) | top100k: "The fastest land animal is the cheetah." | fixed (weak, 2.0); K1 still says pronghorn |
| vit-cry-002 | FOCIL committee inclusion lists, censorship resistance | yes (1.0) | yes (1.0) | K0 crypto EIP-7805: "Allow a committee of validators to force-include a set of transactions in every block" | retrieved_but_wrong |
| vit-cry-003 | Partial expiry 2025, 300-500 GB | yes (1.0) | yes (1.5) | K0 crypto EIP-4444 (2021 draft): "more than 400GB of disk space" | retrieved_but_wrong (stale source) |
| vit-cry-006 | QF formula; collusion/Sybil weakness | yes (1.0) | no (1.0) | K0 crypto: "Using onchain voting makes quadratic funding susceptible to collusion" | retrieved_but_wrong; K4 crowds the crypto chunks out |
| vit-hum-005 (unclear) | "Invisible hand" once in WoN, Book IV ch. 2 | no (1.0) | yes (1.0) | top100k Adam Smith: "Smith used the term "the invisible hand" in "History of Astronomy" ... and once in each of his" | retrieved_but_wrong (K4) |

## What it implies

- **Content** is the largest bucket. 10 of 20 items have no key fact in simplewiki or top100k: everyday cooking technique, US personal-finance rules, recent crypto (d/acc, Privacy Pools) and a Thai road route. These are Stack Exchange and Wikivoyage-depth facts that encyclopedias leave out. A third general encyclopedia would not change this. Topic-matched packs would, and the qa-cooking/qa-money Stack Exchange packs hold exactly these answers.
- **Pre-retrieval routing** blocks 4 of 20 outright: 1 places misroute and 3 health declines, for a cast-iron pot, a roast bird and a PayPal scam. No pack can help those. For 2 of them the fact is in a pack.
- **Retrieval** misses only a small share in K1/K4: 2 present-but-unretrieved, plus 3 facts sitting unretrieved in the K0 packs. K4 also crowds out a good crypto source (cry-006).
- **Reading** is the ceiling once the source is there. With the fact kept, the 1.7B still answers wrong in 2 no-source items plus all 3 crypto reading failures plus hum-005. The 3 reading "fixes" are 2.0 flips, two of which keep the same factual error (Greenland population, the pronghorn in K1).
