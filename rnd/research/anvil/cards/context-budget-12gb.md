# Bigger context budget on the 12 GB tier (more passages for the 4B), to raise completeness without hallucination
TL;DR: after #12 showed that the 4B's completeness gap is knowledge, not length, the natural next lever in my lane was giving it more source text: retrieveK 4 → 6–10 and contextTokens 700 → 1,200+. **Tested offline: answer-key coverage barely moves** (17 → 17 of 52 keys on the night kit; 16 → 17 on the full-article sample pack) while the prompt doubles. Not worth an arm.
Lane: Anvil · Status: tested (offline, negative) · Priority: C
Axes moved:
- quality ≈: keys in the prompt are flat with k. Sonar's exchange rate is ≈ +0.003 ratio per key moved in, so the expected effect is ≈ 0.
- latency ↓: k = 10 doubles the passage text (~690 → ~1,420 tokens). At the 4B's desktop prefill of ~77 tok/s that is +9 s TTFT; on a phone, more.
- truthfulness: more distractors (UNKNOWN sign).
- safety, retrieval, resources: none.
Fits BOAR? Config only (`quickBudget` in `src/routing/depth.ts`, 0cfd4a77: `retrieveK: 4, contextTokens: 700` for non-lookup tasks). It just doesn't pay.
Evidence:
- **#12 result** (QUEUE.md, coordinator 2026-10-02 ~04:00): asking the 4B for longer answers gave quality Δ −0.044 (CI −0.076 to −0.014), correctness 3.12 → 2.26, confident-wrong 10 → 20. The judge's length slope was **negative**. "The 4B's completeness gap is knowledge, not style." So completeness can only come from more *grounded* content.
- **Sonar** (`sonar/RADAR.md`, cycles 6–9):
  - 19 of 21 answer-key misses are knowledge coverage (intro-only or missing articles).
  - Compression cuts the key in only 3 of 13 items.
  - "Right article, wrong passage" in 10 of 52 keyed items at k = 4.
  - The exchange rate is ≈ +0.003 ratio per key moved into the prompt.
  - **The Android 4B runs have no vital5 arm yet** (kit = crypto + Wikivoyage only).
- **This card's k-sweep** (`exp/context-budget/`, engine `WikiPack.searchDetailed` @0cfd4a77, 52 keyed bench-v0.1 items):

  | Packs | k | passage text (median) | keys in returned passages | keys in the same articles' full text |
  |---|---|---|---|---|
  | Wikivoyage + crypto (night kit) | 4 | ~693 tok | 17 | 27 |
  | | 6 | ~1,010 tok | 17 | 27 |
  | | 8 | ~1,253 tok | 17 | 28 |
  | | 10 | ~1,418 tok | 17 | 28 |
  | boar-wiki-sample (full articles, 1 shard) | 4 | ~575 tok | 16 | 25 |
  | | 6 | ~827 tok | 17 | 26 |
  | | 8 | ~1,105 tok | 17 | 27 |
  | | 10 | ~1,414 tok | 17 | 27 |

  The extra passages come from the same articles or from distractors; the ~10 "right article, wrong passage" keys stay out at any k. **The bottleneck is which articles are in the packs, not how much of them the model sees.**
Test in boar-eval: not proposed.
Cost to try: done (~5 min CPU locally, no download).

## What does raise completeness without hallucination (pointing out of my lane)

- **Pack coverage on the Android tier.** This is the lever with the most items behind it, and it is Sonar's / the coordinator's:
  1. the Android 4B has never run with vital5 (the iPhone kit has it);
  2. the full-enwiki / top-100k pack (#6, Sonar `full-enwiki-pack-arm`, predicted +8 to +10 keys).
  - At ≈ +0.003 per key, only #6 is in MDE range on its own. But the 4B's per-key rate is UNKNOWN and may be higher than the 1.5B's, because the 4B reads sources better (Kiln D3: 68% vs 45% on factual 38).
- **In my lane, after #6 lands:** re-run the k-sweep on the full pack. Long full articles are where "right article, wrong passage" lives, and a per-article section budget (more sections from the top article instead of more articles) is the variant this sweep did not test. Then, and only then, revisit answer length (`complete-paragraph-persona`).

UNKNOWN:
- the k-sweep with vital5 (format 1; `WikiPack` reads format 2 only, so the format-1 path needs a different harness);
- the 4B's per-key exchange rate.
