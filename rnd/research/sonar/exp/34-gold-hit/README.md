# exp-34: gold-hit L0 — is the oracle's gold in front of the 4B? (Sonar, 2026-10-03, dev only)

TL;DR (v0.1 EN, 57 items; gold = Anvil's oracle `anvil/exp/oracle/`, 45 items have a gold Wikipedia article):
- **The +0.10 oracle gap is mostly passage choice and article retrieval. Coverage matters less.**

  | Context source | gold article in context | gold sentence in context |
  |---|---|---|
  | kit A (Android default; crypto + Wikivoyage), s44 dump / p1 kic | 0–1 / 45 | 4 / 56 |
  | kit A + vital5 (g1plus base, kic) | 17 / 45 | 11 / 56 |
  | kit A + vital5 + top100k, full search (#17 g1plus, kic) | 24 / 45 | 12 / 56 |
  | Anvil Q450 (question-chosen passages from the gold articles) | — | **50 / 56** |
  | Anvil R450 (answer-chosen, the oracle; 0.606 judged) | — | 56 / 56 |

- **Where the 45 Wikipedia-gold items are lost (g1plus):**
  - 9: right article and a gold sentence reach the model;
  - **15: right article in context, wrong passage** (passage selection);
  - **12: gold article is in top100k but not retrieved** (article retrieval);
  - **8: gold article outside top100k** (coverage; the full-EN title tier);
  - 1: a gold sentence from another article.
- **Coverage ceiling** (`ceiling.py`; offline: the local enwiki index + the pageview ranks the top-N packs were cut by):

  | Pack size | any gold article | top-passage article |
  |---|---|---|
  | top10k | 22 / 45 | 11 / 30 |
  | top100k | 33 / 45 | 20 / 30 |
  | top300k | 39 / 45 | 27 / 30 |
  | top1M | 42 / 45 | 29 / 30 |
  | full EN | 45 / 45 | 30 / 30 |

  "Top-passage article" means the article holding the oracle's best passage, for the 30 items whose best passage is Wikipedia.
- **Question-similarity passage selection works on the right articles.** Q450 = bge-small cosine to the question, 120-word passages, 340 words. Its gold-sentence hit is 50/56. Restricted to the articles the engine already retrieved, it recovers ≥ 6 of the 15 wrong-passage items. That is a lower bound: Q450 often picks a different gold article than the one the engine had.

## Metrics (`goldhit.py`)
- **art:** a gold Wikipedia title is a context source labelled Wikipedia. Unlabelled sources in traces = vital5 leads. Wikivoyage "Singapore" does not count.
- **sent (primary):** some ≥ 8-word sentence of the top-3 R450 passages has ≥ 60% of its word 4-grams in the context. This is robust to the pack's dump date and to the engine's sentence compression.
- **pas:** ≥ 50% 4-gram coverage of a whole R450 passage. Strict: compression rarely keeps 120 words.
- Inputs: `--dump-prompts` files (the Context block) or `--event-source-text` traces (the last `sources` event with text = what was placed in the prompt).
- Caveats:
  - The gold set is Opus-reference-derived, one judge's view.
  - The 4-gram match misses paraphrases, so the hits are a floor.
  - 12 items have no Wikipedia gold (crypto, dangers, web-only); `sent` covers them where R450 has a passage.

## Plan (front 2, bounty lever; each step time-boxed)
1. **PQ, question-similarity passage re-selection within the retrieved Wikipedia articles (2 h, next):**
   - **L0 on the mini** (top100k is there): for each item, take the Wikipedia titles the g1plus engine placed in context, re-chunk their pack text into ~120-word passages, rank them by bge-small cosine to the question, and fill the same budget.
   - **Gate:** gold-sentence hit ≥ 12 + 5 = 17 / 56, with no item losing its hit. Pass → engine patch (rank passages within named or retrieved articles by question embedding before compression) → L1 with Kiln.
   - **Device cost:** one bge-small embedding per candidate chunk. Cap at ~40 chunks per question (≈ 0.4–1 s on the phone; Forge to measure).
2. **Article retrieval (12 items):** the exp-33 L1 arm C (named-title tier) addresses named items. For the unnamed ones, a question-embedding check over lead vectors is already in the pack. Measure `art` on the exp-33 kic traces.
3. **Coverage (8 items): the full-EN title tier** (TIER-PLAN.md; 8.3 GB). `ceiling.py` says top300k already covers 27 / 30 top-passage articles, so a top300k–1M slim tier gets most of the gain at a fraction of the size. Decide after step 1.
4. **Every pack/retrieval arm from now on reports `art` and `sent`.** Kiln adds `--event-source-text` to the runs, and the metric runs in seconds.

## PQ L0 result (2026-10-03, ~1.2 h of the 2 h box): modest; article set, gates and coverage dominate
- **Setup** (`pq.mts`; g1plus = kit A + vital5 + top100k, s42 kic traces). For each item:
  - take the Wikipedia articles the engine placed in context;
  - take their top100k chunks and keep the top 40 by bge-small cosine to the question;
  - split those into ~45–60-word sentence windows and re-rank them by cosine;
  - fill the budget after the engine's non-Wikipedia passages (vital5 passages are kept).
  v1 used whole 1,000-character chunks, which fit only 1–2 per budget: 12/56, +4/−4.

  | Budget (mean words placed) | gold sentence | vs engine 12/56 |
  |---|---|---|
  | engine's own words per item (117) | 14 / 56 | +3 / −1 |
  | 240 words (126) | 15 / 56 | +4 / −1 |
  | 340 words (163; Q450's budget) | **17 / 56** | +5 / −0 |

- **Reading:**
  - The gate (≥ 17, none lost) passes only at 340 words, which is ~30 more words than the engine places.
  - At the same budget the net is +2 of 56: real but small, below what a judged L1 can see (MDE ≈ 0.04).
  - Q450's 50/56 comes from having the RIGHT articles, not from the selection method.
- **Raw retrieval vs placed** (`rawvsplaced.py`; gold Wikipedia article in the retrieve event vs in the prompt):

  | Run | raw | placed | dropped by gates/compression |
  |---|---|---|---|
  | kit A + vital5 | 22 / 45 | 17 | 5 |
  | + top100k | 30 / 45 | 24 | 6 |

  - Gates: `grounding:off-topic-dropped-*` / `no-good-source`.
  - Examples of dropped gold articles:
    - Apollo 11 for "astronauts on the Moon before 1970";
    - Cheetah/Pronghorn;
    - World population;
    - Amazon/Nile;
    - Dengue fever (compression 368→104).
  - Retrieval recall within top100k is close to the ceiling (raw 30 vs 33 in pack).
- **Revised loss split** (45 Wikipedia-gold items, kit A + vital5 + top100k):

  | Loss | Items | Lever |
  |---|---|---|
  | gold article not in the pack | ~12 | coverage: full-EN or top300k title tier |
  | retrieved but dropped by the gates | 6 | gate exemption for retrieved named/high-cosine articles |
  | right article placed, wrong passage | 15 | PQ: +2 to +5 |
  | works | 9 | |

## Fast replay + judged attribution + LQ (2026-10-03, gate box ~2 h; closed)
- **Fast replay harness** (`stub-server.mjs`, `replay.sh`, `rp*.requests.jsonl`):
  - The real engine tree and packs run through the desktop-node adapter with `--backend server --server-url` pointed at a stub server that answers instantly.
  - Retrieval, gates and compression are real, and `--event-source-text` captures the context.
  - 65 items in ~20 s after ~60 s of pack hashing.
  - Validated against Kiln's real exp-33 arm A: **58/65 placed contexts byte-identical**. The 7 differences are venue/travel items, because the replay had no `--places`.
  - Never for judged runs.
- **Kit sweep, same engine** (bounty1 = health13 + travel distance; s42 request set):

  | Kit | gold article placed | gold sentence | raw → placed |
  |---|---|---|---|
  | A (crypto + Wikivoyage) | 1 / 45 | 4 / 56 | 1 → 1 |
  | A + top100k (= exp-33 arm B) | 17 | 7 | 20 → 17 |
  | A + vital5 | 17 | 11 | 22 → 17 |
  | A + vital5 + top100k | 23 | 11 | 28 → 23 |

  E1(a) already judged A + vital5 = A on the Android 4B (Δ 0.000). So more gold sentences in context does not by itself move the judge.
- **Where the oracle's judged gain lives** (`where.py`; Q450 − engine s44 rubric, summed by loss category on A + vital5 + top100k; Q450 = **0.567**, R450 0.606, engine 0.498, closed-book 0.487):

  | Category | n | ΔQ450 | ΔR450 | closed-book rubric |
  |---|---|---|---|---|
  | gold sentence already in context | 11 | +2.5 | +7.0 | 2.97 |
  | right article, wrong passage | 14 | +3.0 | +4.7 | 2.61 |
  | retrieved, dropped by gates/compression | 6 | +2.5 | +1.8 | 2.86 |
  | **in pack, not retrieved** | 8 | **+7.7** | +11.2 | 2.00 |
  | outside top100k (title tier) | 7 | +2.0 | +2.2 | 2.24 |
  | no Wikipedia gold | 11 | +1.8 | +3.7 | 1.71 |
  | total | 57 | +19.5 (≈ +0.07) | +30.5 | |

  The "not retrieved" 8 are heterogeneous:
  - 2 health items (health route);
  - 2 long questions with **empty retrieval** (Mozi critique; Burj Khalifa / Lake Baikal);
  - 2 year-rule drops (Nobel 2017, Moon before 1970);
  - 1 comparison (Japan vs Germany);
  - 1 Wikivoyage outranking Wikipedia (Brazil plugs).
- **Root cause of the empty retrievals:**
  - Long questions fail every coverage rule: the pack's named-title share must be ≥ 0.5 of all content stems, and BM25 passages need coverage ≥ 0.5 of all stems.
  - `onTopic` needs termCoverage ≥ 0.75. The "before 1970" year rule also requires the year in the source.
- **LQ** (`lq-on-bounty1.DEV.patch` ad7ecc01…, DEV): coverage and named share on the top-6 idf stems for long questions; `onTopic` coverage 0.5 for ≥ 7 terms; bound years ("before/after/since/until YYYY") exempt.

  | Kit | gold article placed | gold sentence | raw |
  |---|---|---|---|
  | A + vital5 + top100k | 23 → 25 | 11 → 11 | 28 → 30 |
  | A + top100k | 17 → 18 | 7 → 7 | 20 → 22 |

  - Fixed: Mohism now retrieved for the Mozi critique, Cheetah placed, "List of river systems by length" placed.
  - Not fixed: Lake Baikal (two named entities, each under the 0.5 share) and World population (still dropped).
  - **Small: no standalone L1.**
- **Reading for front 2:**
  - The oracle's +0.07 (Q450) is spread over many small mechanisms: article choice, passage choice, the gates, named share, compression. No single retrieval fix captures it.
  - Realistic engineering estimate: +0.02–0.03, and only as one combined arm.
  - The full-EN title tier is worth ≈ +2 rubric points on v0.1 (7 items). It matters for the post author's own named long-tail questions (Mozi, Gríma), not for v0.1.

## Retrieval v2: patched arm vs CLEAN path (2026-10-03 night; the coordinator: keep whichever is higher)
All rows use the same kit: A + top100k (= exp-33 arms B/C). Gold sentence in context, v0.1 EN, of 56 items.

| Candidate | 130 words | 240 words | 340 words | candidate windows / question |
|---|---|---|---|---|
| engine B (full search; replay) | 7 | — | — | — |
| engine C2b (title tier, fixed; replay) | 8 | — | — | — |
| C2b + PQ windows (patched arm) | 12 | 12 | 13 | — |
| B + LQ + PQ windows (patched arm) | 11 | 9 | 13 | — |
| CLEAN full (named + dense 6 + BM25 4; lead + 3 chunks) | 12 | 18 | 18 | 102 |
| CLEAN lite (named + dense 4 + BM25 2; lead + 1) | — | 17 | — | 45 |
| CLEAN nodense (named + BM25 4; lead + 3) | — | 18 | — | 51 |
| CLEAN nonamed (dense 6 + BM25 4; lead + 3) | — | 17 | — | 101 |
| **CLEAN min (named + BM25 4, cap 8; lead + 1 best chunk)** | 12 | **19** | 19 | **34.5** |

- **Decision: the CLEAN path wins** (19 vs 13). Against engine B it gains 12 items and loses 0.
- Dense lead search adds nothing, so there's no 19 MB lead-vector scan on the phone.
- **The gain comes from:**
  - broad article candidates (named titles at share ≥ 0.25 + the BM25 top articles);
  - ~60-word sentence windows chosen by bge-small cosine to the question, jointly with kit A's Wikivoyage and crypto passages;
  - no term-coverage gates, only a cosine floor of 0.5 (0, 0.5 and 0.6 gave the same hits).
- **Budget:** 240 words (≈ 320 tokens, the engine's compressed context size) captures it all; 130 words is too few.
- **Device cost:** ~35 bge-small embeddings of ≤ 60 words per question, on the embedder already resident for retrieval. Forge to measure; my guess is 0.5–1.5 s.
- **Anvil's oracle, final:** engine 0.507, Q450 0.567, R450 0.606, R1500 0.626. On the 33 not-in-kit items: 0.478 → Q450 0.552.
- **Next:** implement CLEAN min as an engine arm (`rv2`):
  - replaces compressContext and the `onTopic` gate for Wikipedia/Wikivoyage/crypto passages on non-health questions;
  - keeps the health path, the crypto-source guard and the instant/calculator/places shortcuts;
  - L0 on the replay (target ≥ 17/56 in the REAL engine), then a 2-seed L1 against arm B / C2.

## Compass V-exact review checks (2026-10-03 night; VSLICE-REPORT 0105ad03)
- **vx-001 "Tell me about Japan"** (judged 0.38: crypto-kit retrieval).
  - kit A context: 3 Wikivoyage Japan passages + **"Stablecoin > Legislation > Japan"** (crypto noise).
  - rv2 + top100k: Wikivoyage Japan ×3 + the **Wikipedia "Japan" lead** ("Japan is an island country in East Asia…"); no crypto.
  - The context is fixed; the judged effect comes with the exp-35 L1.
- **vit-hum-004 Gríma** (0.20: "confident false correction": the 4B says Gríma does not kill Saruman).
  - kit A: only "Wikivoyage: Lord of the Rings tourism".
  - rv2 + top100k: 4 windows, with "**Saruman's murder by Gríma** (seen only in the Extended Edition)…" plus 3 Saruman/LOTR windows. So the KILLING is in context, which contradicts the false correction.
  - The **why** is not in context: Saruman beats and curses Wormtongue, reveals his crimes, and Wormtongue kills him. It is in top100k (Saruman chunk 1460199; LOTR plot chunk 2776068), but those passages say "Wormtongue", not "Gríma":
    - the stem-based best chunk misses them (even with 6 sections);
    - rv2 reads only the lead + 1 best chunk.
  - **rv2.1 (DEV, killed):** read the 2 named articles whole (every chunk's windows ranked). Gold sentence 18 → 16 (+1 / −3), and Gríma still gets other Wormtongue windows (Orthanc palantír scene). No.
  - Remaining options:
    - the full-EN title tier (a "Gríma Wormtongue" article, not in top100k);
    - an alias map (question name → the article's own epithet) at pack build.
  - Both are for after the L1. The judged L1 shows whether "Gríma killed Saruman" in context removes the false correction.

## Next (proposed)
- Don't L1 PQ alone. Fold it into one **"retrieval v2" arm**: top100k (or the title tier) + PQ windows at the engine's 450-work budget + a gate fix for the 6 drops. Gate it at L0 on gold-sentence ≥ 20 / 56 with ≤ 1 lost, then L1.
- Next 2 h box: why the off-topic gate drops Apollo 11 / Cheetah / World population (exp-26 saw the same gate: ≥ 0.5 topic stems or lead cos ≥ 0.70).

## Files
- `goldhit.py`: L0 metric. `python3 goldhit.py <prompts.jsonl | kic traces.jsonl> <label> [-v]` → `goldhit-<label>.json`.
- `ceiling.py`: coverage by pack size → `ceiling.json`. Offline, ~45 s.
- `pq.mts` (+ `pq-items.json`, `pq-engine-ctx.json`): the PQ L0; needs a top100k subset sqlite (built on the mini with ATTACH; not committed).
- `rawvsplaced.py`: gold article in raw retrieval vs placed.
