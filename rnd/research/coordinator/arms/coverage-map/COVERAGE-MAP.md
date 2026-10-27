# COVERAGE-MAP (2026-10-22): which dev facts the packs miss, which permitted corpus holds them, what the packs on disk add

TL;DR (0 LLM, 0 judge, 0 paid, 0 phone; MacBook replays + read-only pack FTS; dev only: v0.1 57 + cooking/money self-tests 40)
- **The K1 S1 set (45) is 39 cooking/money self-tests + 6 v0.1 items.** All 39 cm facts sit in qa-cooking-se / qa-money-se, which are on disk (built, published; by construction). Of the 6 v0.1: 4 are in English Wikipedia (2 already in K3's factbook/top100k), 1 is arithmetic (no corpus needed), 1 is a route distance (no permitted corpus).
- **K-FULL (18 packs on disk: K3 + visa, nist, 7 SE qa, preparedness, vitalik blog, enwiki top100k) moves MAIN 92 S1 52 -> 4** (same-method K3 baseline; RAG-FUNNEL's own K3 S1 was 45 with dense candidates). **But kept facts move only 23 -> 28.** v0.1: S1 12 -> 4, kept 23 -> 25 (+7 / -5). cm: S1 40 -> 0, kept 0 -> 3.
- **Best kit for MAIN is K3 + qa-cooking + qa-money (K3CM): kept 23 -> 29, v0.1 untouched (0 gained / 0 lost).** In the 18-pack kit, cm kept drops 6 -> 3 (crowding).
- **Wikipedia top100k is the only on-disk pack that adds v0.1 facts K3 lacks (8 items), and it crowds:** 55 % of kept slots in K3W, +7 / -5 kept (net +2). Same failure as DEEPWIKI (-0.034).
- **The binding gap after install is retrieval, not content:** with K3CM, 21 of 40 cm items are S2 (pack installed, own article not retrieved; for 21 of the 23 oracle-S2 items the qa pack is among the candidates but another thread wins) and 13 are S3.
- Full English Wikipedia (15 FineWiki shards) is **not on disk** (only the 15 .json sidecars here; shards deleted after WIKIFULL; the mini has none), so K-FULL uses top100k. No shard grouping was needed: the engine loaded all 18 packs in one replay.

## S1 (K1) breakdown: domain x corpus type (coverage.md has every row)
| domain | n | corpus type that holds the fact | on disk? | ids |
|---|---|---|---|---|
| cooking | 20 | Stack Exchange cooking (CC BY-SA) | FOUND qa-cooking-se, 20/20 own source article (quotes verified); lexical pool rule finds 6 | st-qa-cooking-se-001..020 |
| money | 19 | Stack Exchange personal finance (CC BY-SA) | FOUND qa-money-se, 19/19 (money-012 is S3, not S1); lexical finds 8 | st-qa-money-se-* |
| humanities | 2 | English Wikipedia (Mozi/Mohism; J. S. Mill / Harm principle); Gutenberg PD On Liberty | FOUND top100k (partial for Mozi: no 'Mozi' article; 'Heaven' chunk) | vit-hum-001, vit-hum-006 |
| law/ref | 2 | Factbook (CC0) / English Wikipedia | FOUND factbook (K3: Iceland 103,000 sq km; Japan/Germany area + population, derivable), top100k 'Demographics of Japan' 336/km2 | lan-ref-004, vit-sci-002 |
| travel | 1 | route distance (OSM routing = ODbL, outside the list) | NOT FOUND; NOT COVERABLE as a stated fact | vit-trv-004 |
| science | 1 | none: arithmetic from the question | not a coverage gap | vit-sci-003 |
The 5 unkeyed v0.1 items (trv-002, trv-004, dng-001/002/005) are covered by K0/K3 packs (Wikivoyage Brazil, Lisbon Airport; firstaid ATP 4-02.11, Ready.gov; preparedness).
Lexical-only S1 that hand reads move: vit-cry-005 (boar-crypto ERC-8262 P, vitalik Y), lan-rsn-002 (simplewiki Baikal P) = in pack. Still absent in every kit: vit-hum-003 (Mozi on reciprocity; full enwiki Mohism, not on disk), vit-trv-004, vit-sci-003.

## K-FULL funnel read (replay of answer() to the stubbed generation; K3 settings a2 + append-budget; gate/detector from the RAG-FUNNEL K3 traces)
| kit | packs | MAIN 92 S1/S2/S3/K | v0.1 52 | cm 40 | v0.1 kept +/- vs K3 | top kept-slot share |
|---|---|---|---|---|---|---|
| K3 (baseline, raw titles = funnel 96/97) | 6 | 52/11/6/23 | 12/11/6/23 | 40/0/0/0 | - | simplewiki 69 % |
| K3CM = K3 + qa-cooking + qa-money | 8 | 12/32/19/**29** | 12/11/6/23 | 0/21/13/6 | +0 / -0 | simplewiki 54 %, money 14 %, cooking 10 % |
| K3W = K3 + enwiki top100k | 7 | 43/10/14/25 | **4**/10/13/25 | 39/0/1/0 | +7 / -5 | top100k 55 % |
| KSE = K3 + 11 (no top100k) | 17 | 10/33/24/25 | 10/10/10/22 | 0/23/14/3 | +2 / -3 | simplewiki 38 %, SE qa 7-9 % each |
| **KFULL = KSE + top100k** | 18 | **4/38/22/28** | 4/11/12/25 | 0/27/10/3 | +7 / -5 | top100k 47 % |
K = kept (= funnel S4+S5; no generation). cm stage = best of oracle (own source article in raw/wide/kept) and lexical. v0.1 gained under top100k: hum-001, hum-005, hum-006, cmp-004, cmp-005, cry-010, hlt-003; lost: exp-004, exp-005, rsn-006, cry-006, trv-003 (displaced by top100k chunks). Per-item table: kfull-funnel.md.

## Ranked pack-build list (corpus types covering >= 3 dev facts)
| # | corpus | licence | size | build effort | dev S1 recovery | kept effect (replay) | crowding risk |
|---|---|---|---|---|---|---|---|
| 1 | qa-cooking-se + qa-money-se (archive.org SE 2024-04 snapshot) | CC BY-SA per post (OK) | 89 + 137 MB (FACT-REACH slices ~17.5 + 58 MB) | **0: built, published** (wave3) | 39/39 cm (by construction) | MAIN kept 23 -> 29; v0.1 unchanged | low (24 % of slots, no v0.1 loss); in an 18-pack kit cm kept halves |
| 2 | English Wikipedia top100k | CC BY-SA 4.0 (OK) | 2.54 GB | 0: built 10-01 (on MacBook + mini); needs an additive quota / fallback patch (VITALPACK-ADD q = 1, untested) | v0.1 lexical S1 12 -> 4 (8 items only here) | +7 / -5 kept, net +2 | **high** (47-55 % of slots; DEEPWIKI -0.034) |
| 3 | Full English Wikipedia (15 FineWiki shards; maintainer's wiki/en plan) | CC BY-SA 4.0 (OK) | ~18 GB | script exists (packs/run-en-shards.sh, build on the mini); 18 GB download; mini has 31 GiB free (floor 25) -> one shard at a time | +1-2 on our dev over top100k (Mohism/Mozi, Harm principle article); WIKIFULL prior on v0.2 dev: 37/78 missing facts, 27 outside top100k | not measured | high (as 2, larger) |
| 4 | the post author's blog | **WTFPL: outside PD/CC0/CC BY/CC BY-SA -> flag for r4to** | 8.8 MB | 0: built (mini wave4); card fix (holds Chinese posts) | 2 crypto facts beyond the claim kit by hand (Privacy Pools, d/acc; FACT-REACH); lexical in-pack 5 v0.1, all also in boar-crypto | KSE: 3 % of slots; cry-009 kept gained | low |
| 5 | qa-ethereum-se + qa-bitcoin-se | CC BY-SA (OK) | 151 + 113 MB (v3proto) | 0: built, published | 0 S1 (3 + 2 lexical in-pack, overlap boar-crypto) | KFULL: cry-010 gained via them, cry-006 lost | medium (9 + 6 % of slots in KSE) |
Not worth a build on this evidence: Ethereum docs/EIPs re-cut (boar-crypto already holds ethereum.org (MIT: flag) + EIPs (CC0); 0 dev S1 items need it); visa, nist-crypto, preparedness, qa-health/outdoors/travel (0 dev S1 items; they only add candidates).
**NOT COVERABLE by any permitted corpus:** vit-trv-004 (walking-route distance needs OSM routing, ODbL), vit-sci-003 (arithmetic, no corpus), and the rubric depth the v0.1 humanities items cite from plato.stanford.edu (SEP: all rights reserved; Wikipedia covers the core fact, not the objections/depth).

## Caveats
- Dev items only (v0.1 public + agent-written self-tests); no blind/, rnd/veil or v0.4 read. Key facts are agent-read from gold/rubrics.
- cm coverage is true by construction (self-tests written from those packs): it shows install value, not coverage of unseen cooking/money questions.
- Lexical fact rule is noisy both ways: the pool rule found 14/40 cm facts that are verifiably in the pack (recall ~35 % here), and 3 of 8 v0.1 top100k-only hits were checked by hand (2 Y, 1 spurious top hit with a Y elsewhere). S1 counts are upper bounds, S2 lower bounds.
- The replay logs raw + wide-12 candidates, not the two-stage dense list, so S3 is lower and S1/S2 higher than RAG-FUNNEL's (kept K matches: 23 = 23).
- One replay per kit, seed-free (retrieval only). Walls are not comparable: the MacBook ran at load ~150 from other sessions' replays.
- Files: coverage.json / coverage.md (deliverable 1), kfull-funnel.md, aggregates/{coverage-pool, cm-oracle, cm-stage, kfull-funnel, summary}.json, tools/{coverage_pool, cm_oracle, cm_stage, score_kfull, summarize, build_coverage}.py, tools/{run_replay, score_all}.sh, replay/kit.*.txt (replay jsonl hold pack text: keep out of git).
