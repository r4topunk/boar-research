# Retrieval failure scorecard (2026-10-06)

Deterministic, from existing traces + judgments (no engine runs, no judge calls). Generator: `rnd/research/coordinator/tools/retrieval_scorecard.py` (re-run: `python3 -I` on it, defaults = this report). Per-row data: `RETRIEVAL-SCORECARD-2026-10-06.items.csv`.

## TL;DR
- Largest bucket: **B1 coverage** = 38/78 item-runs (49%) over ctl-s44 + ctl-s45 (39 gold items each).
- Counts per run: **ctl-s44** B1=19 B2=7 B3=1 B4=2 B5=6 B6=4; **ctl-s45** B1=19 B2=7 B3=1 B4=2 B5=5 B6=5; **cut6-s42** B1=19 B2=7 B3=1 B4=2 B5=8 B6=2.
- Engine-fixable B2+B3 = 16 vs model-limited B4 = 4 (primary runs pooled): **B2+B3 exceeds B4** (14 ranking + 2 dropped vs 4 reader-fail). Per run: ctl-s44 8 vs 2, ctl-s45 8 vs 2, cut6-s42 8 vs 2 (of 39). Largest engine bucket: B2 ranking.
- recall@5 (scorer rule, raw[:5]) over the 39 gold items: ctl-s44 0.333, ctl-s45 0.333, cut6-s42 0.333.
- Coverage: 21/44 distinct gold titles exist in the loaded packs; 20/39 gold items have at least one. Gold titles are Wikipedia articles; the kit has no general Wikipedia pack (5,300 seed-corpus articles + Wikivoyage + crypto), so most "in pack" hits are the Wikivoyage namesake (scorer rule).
- Gold reached the prompt in 24/78 item-runs; when it did, the 4B answered right (B5) 11 times and wrong (B4) 4.

## Bucket table (gold items, one bucket per item per run)

| Bucket | meaning | ctl-s44 | ctl-s45 | cut6-s42 | pooled primary | mean corr (primary) |
|---|---|---|---|---|---|---|
| B1 coverage | no gold title in any loaded pack | 19 | 19 | 19 | 38 (49%) | 3.51 |
| B2 ranking | gold in pack, not in raw | 7 | 7 | 7 | 14 (18%) | 3.36 |
| B3 dropped | gold in raw, lost before prompt / not shown | 1 | 1 | 1 | 2 (3%) | 5.00 |
| B4 reader-fail | gold in prompt, correctness <= 2 | 2 | 2 | 2 | 4 (5%) | 1.62 |
| B5 reader-ok | gold in prompt, correctness >= 4 | 6 | 5 | 8 | 11 (14%) | 4.55 |
| B6 ambiguous | gold in prompt, correctness 3-band / declined | 4 | 5 | 2 | 9 (12%) | 3.17 |

Sub-reasons (pooled primary): B1 absent: 38; B2 B2-empty-raw: 2; B2 B2-not-ranked: 12; B3 B3-drop: 2; B6 correctness 3-band: 9.
Seed stability: ctl-s44 vs ctl-s45 same bucket on 36/39 items.
Cross-check cut6-s42: same bucket as ctl-s44 on 33/39 items.

## Per category (all 60 items; bucket, off-topic and corr columns pool the primary runs)

| category | items | gold items | B1 | B2 | B3 | B4 | B5 | B6 | mean corr | any off-topic source |
|---|---|---|---|---|---|---|---|---|---|---|
| comparison | 7 | 7 | 10 | 2 | 0 | 0 | 1 | 1 | 3.39 | 6/14 |
| crypto | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.14 | 4/14 |
| danger | 2 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 4.50 | 0/4 |
| danger-situation | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3.67 | 2/6 |
| explanation | 11 | 10 | 6 | 2 | 0 | 2 | 4 | 6 | 3.32 | 4/22 |
| health | 4 | 3 | 4 | 0 | 0 | 0 | 2 | 0 | 4.19 | 2/8 |
| honesty-refusal | 6 | 5 | 6 | 2 | 0 | 0 | 2 | 0 | 4.25 | 0/12 |
| local-food | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | - | 6/6 |
| reasoning | 11 | 7 | 6 | 4 | 0 | 0 | 2 | 2 | 3.59 | 4/22 |
| synthesis | 3 | 3 | 6 | 0 | 0 | 0 | 0 | 0 | 3.50 | 2/6 |
| travel-local | 1 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 3.00 | 0/2 |
| travel-practical | 2 | 2 | 0 | 2 | 0 | 2 | 0 | 0 | 1.75 | 0/4 |

Off-topic heuristic (pre-answer source title shares no content word with the question or gold titles): 30/120 item-runs carry at least one; mean pre-answer sources 2.05, raw 2.72, prompt tokens 459.

## 10 most instructive items

- `vit-hlt-002` [danger] B3/B3, corr 5/5: gold `Altitude sickness` -> raw: Altitude sickness, North Sikkim; prompt: (nothing). (B3-drop (raw -> not in pre-answer sources))
- `lan-ref-004` [honesty-refusal] B2/B2, corr 5/4: gold `Iceland` -> raw: Driving in Iceland, South Iceland, North Iceland, European quick refe…; prompt: South Iceland, North Iceland. (B2-not-ranked (in pack: Iceland))
- `trv-004` [travel-practical] B2/B2, corr 2/2: gold `Lisbon` -> raw: Lisbon Airport; prompt: Lisbon Airport. (B2-not-ranked (in pack: Lisbon))
- `lan-exp-003` [explanation] B2/B2, corr 5/4: gold `Kenya` -> raw: Angola, Mexico, Bangladesh, Nairobi; prompt: (nothing). (B2-not-ranked (in pack: Kenya))
- `lan-exp-002` [explanation] B4/B4, corr 1.5/2: gold `Montenegro` -> raw: Montenegro, Bitcoin, Algorithmic Contract Types Unified Standards; prompt: Montenegro.
- `trv-002` [travel-practical] B4/B4, corr 2/1: gold `Brazil` -> raw: Brazil; prompt: Brazil.
- `lan-cmp-002` [comparison] B1/B1, corr 5/4: gold `Polar bear|Grizzly bear` -> raw: Dalton Highway, Deadhorse, Biomes and ecosystems; prompt: Dalton Highway, Biomes and ecosystems, Deadhorse. (absent)
- `vit-cry-011` [synthesis] B1/B1, corr 4/4: gold `Terra (blockchain)` -> raw: History of bitcoin, Stablecoin, Cryptocurrency; prompt: History of bitcoin, Cryptocurrency, Stablecoin. (absent)
- `lan-exp-001` [explanation] B6/B6, corr 3/3.5: gold `Singapore` -> raw: Singapore, Narva, Tajikistan; prompt: Singapore. (correctness 3-band)
- `lan-rsn-003` [reasoning] B1/B1, corr 2/1: gold `Cheetah` -> raw: Antelope Valley, North American wildlife, Tips for rail travel, Rail …; prompt: Antelope Valley, North American wildlife. (absent)

## Packs used and where "gold exists in pack" was checked

Desktop-node adapter (`boar-eval/adapters/desktop-node/runner/adapter.ts`, `resolveKit` + `setupAppRetrieval`) loads the request's `config.kit` packs (`<id>.sqlite` in BOAR_EVAL_PACK_DIRS, sha256-pinned) plus, with `--corpus essential` (all three runs), the engine tree's seed corpora `assets/corpus/{corpus,corpus-standard,corpus-full}.json`. Kit in the traces: `boar-crypto` ae9fbd2c7a46, `boar-wikivoyage-en` ff8595e32f56.

| source | articles | sha256 (12) | kit pin ok | checked file |
|---|---|---|---|---|
| boar-crypto.sqlite (Ethereum and cryptography) | 3141 | ae9fbd2c7a46 | yes | `shared-data/crypto/boar-crypto.sqlite` |
| boar-wikivoyage-en.sqlite (English Wikivoyage) | 34002 | ff8595e32f56 | yes | `shared-data/packs/boar-wikivoyage-en.sqlite` |
| corpus.json (seed corpus (Wikipedia)) | 300 | c677b2e39df1 | n/a (engine 0cfd4a77 blob) | `wt/cryptotruth/assets/corpus/corpus.json` |
| corpus-standard.json (seed corpus (Wikipedia)) | 1000 | 2aeff76db480 | n/a (engine 0cfd4a77 blob) | `wt/cryptotruth/assets/corpus/corpus-standard.json` |
| corpus-full.json (seed corpus (Wikipedia)) | 4000 | 6d602003bb9d | n/a (engine 0cfd4a77 blob) | `wt/cryptotruth/assets/corpus/corpus-full.json` |

Lookup: `articles.title` (exact, then NOCASE + whitespace normalisation = the scorer's rule) on each SQLite pack, read-only; titles of each JSON corpus. Near-misses (not counted as present): `Gold (qualifier)` titles, punctuation-only differences, and `redirects` rows pointing to a differently titled article.

Gold title status (44 distinct): absent 21, exact 21, near-miss 2.
- `Amazon River`: near-miss (boar-wikivoyage-en.sqlite:redirect Amazon River -> Voyaging along the Amazon River)
- `Burj Khalifa`: near-miss (boar-wikivoyage-en.sqlite:redirect Burj Khalifa -> Dubai/Jumeirah)

## What engine work would move which bucket

- **B1 coverage (38) -> packs, not engine.** Only a Wikipedia pack (or adding the gold articles to the seed corpora) moves it. Near-miss B1s are title-format gaps (Wikivoyage destination vs the Wikipedia article), still pack work.
- **B2 ranking (14) -> retrieval engine.** Title/lead boost for an exact entity match (the gold title is a query n-gram in most of these), FTS+vector fusion weights, raising k, per-article dedup so one article cannot fill all k slots (see repeated `Lisbon Airport` x4).
- **B3 dropped (2: 2 drop, 0 hidden) -> gates/context packing.** Off-topic/grounding gates (`grounding:off-topic-dropped-N`), context budget (`context:A->B`), citation pruning (`citations:removed-N`). Cheapest engine lever when non-zero: the right passage was already retrieved.
- **B4 reader-fail (4) -> model / prompt.** Gold was in the prompt and the 4B still scored <= 2: bigger/deep tier, better passage selection inside the article (section-level chunks), or answer prompt.
- **B5/B6 (11/9)** are not retrieval losses; B6 is mostly the correctness-3 band.
- Upside check: mean correctness is already B2 3.36, B3 5.00 (the 4B answers many of these from parametric memory). B3 items and their gate codes: `vit-hlt-002` grounding:health-off-topic-dropped-1,grounding:fa-card-altitude.
- Ceiling arithmetic: engine work (B2+B3) can at most promote 16 of 78 gold item-runs into the prompt; B1 (38) is unreachable without packs.

## UNKNOWN / caveats
- Gold exists for 39/60 items only; the 21 others (crypto, honesty, danger, food, travel-local…) have no bucket, only the descriptive fields in the CSV.
- The ctl judgments are `judge.v1-med` reused from text-identical speedpack answers (prep.json); treated as the judgments of these traces.
- Correctness = mean of both orders; 3-band includes 3.5 and 2.5 is B4 only if <= 2 (2.5 -> B6).
- Section-level gold is not used (no gold entry has `#section`); a hit on the gold article counts even if the retrieved chunk is an irrelevant section.
- Off-topic is a lexical heuristic on titles; it flags `Wikivoyage: Narva` for Singapore correctly but also flags legit titles that share no word with the question.
- UNKNOWN: whether the seed corpora were fully indexed on the runner (we assume seedKnowledgeBaseIfEmpty indexed all 5,300 titles); pack presence is title-level, not chunk-level.
