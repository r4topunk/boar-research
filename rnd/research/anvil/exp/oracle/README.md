# Oracle: what the 4B does when the right passage is in its context (Anvil, 2026-10-03, DEV: v0.1 EN, 57 judged items)

**TL;DR:** the knowledge lever is large and the 4B can use it. Through the engine's own fast-tier prompt, the 4B scores **0.567** with passages chosen by the question from the gold articles, and **0.606 / 0.626** with oracle passages at a 450 / 1,500-work budget. The current engine scores **0.507** and closed-book **0.487**; Haiku no-web is 0.653.
- **The reader is not the bottleneck; getting the right passage in front of it is.** Sonar's gold-hit L0 agrees: a gold sentence is in context for 12/56 items with engine + top100k, vs 50/56 for Q450.
- **What packs can buy, at best:**
  - **≈ +0.06** ratio if the article exists and today's style of retrieval picks within it (Q450);
  - **≈ +0.10 to +0.12** with ideal passages.
  - On the 33 out-of-kit items: 0.478 → 0.552 (Q) → 0.595 (R).

| system (4B Qwen3-4B-2507 unless noted) | ratio | pass / cw / fail |
|---|---|---|
| closed-book (anchor.v1, server b11010) | 0.487 | 10 / 30 / 17 |
| **current engine** (main 0cfd4a77, and-qwen, 3 seeds) | **0.507** | 15 / 17 / 25 |
| **Q450**: gold articles, passages chosen by the **question**, ~450-work budget | **0.567** | 27 / 15 / 15 |
| **R450**: gold articles, passages chosen by the **reference answer** (oracle), ~450 tokens | **0.606** | 35 / 12 / 10 |
| **R1500**: same, ~1,500 tokens | **0.626** | 32 / 8 / 17 |
| Qwen3.5-9B closed-book (no-think) | 0.488 | 8 / 38 / 11 |
| Haiku no-web (frontier anchor) | 0.653 | 20 / 17 / 20 |

**By coverage class** (Compass `l1-items.tsv`):

| class | n | engine | closed | Q450 | R450 |
|---|---|---|---|---|---|
| not-in-kit | 33 | 0.478 | 0.447 | 0.552 | 0.595 |
| in-kit-key | 11 | 0.626 | 0.599 | 0.654 | 0.701 |
| in-kit-no-key | 8 | 0.527 | 0.546 | 0.519 | 0.604 |
| unkeyed | 5 | 0.404 | 0.405 | 0.547 | 0.466 |

- **In-kit items gain too** (0.626 → 0.701 with ideal passages): better passage selection inside the existing kit is also worth something.

## Method (`fetch_sources.py`, `build_ctx.mts`, `gen_oracle.mts`)
- **Sources:**
  - every Wikipedia article cited by the item's `reference_sources`, by the Opus+web reference's sources/answer, or by `gold/sources.json`: 45/57 items, via the API's plain-text extracts;
  - the other reference URLs, HTML → text, best effort: all 57 items, 203 documents.
  - User-Agent: `boar-research/0.1 (offline-research-bench)`. Raw page cache deleted after extraction.
- **Passages:** ~120-word windows, embedded with the engine's bge-small (`bge-small-en-v1.5-q8_0`).
  - **Q** = cosine to the question; **R** = cosine to the Opus reference answer (the oracle).
  - Greedy fill up to 340 words (≈ 450 tokens; engine traces show `context:452->320`) or 1,150 words.
- **Prompt:** the engine's fast-tier prompt, byte-for-byte from `boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl` (main 0cfd4a77): the same system text, the `Context:` block formatted `[n] Wikipedia: <title>\n<text>`, and the user message with the same response-style suffix ("2-3 sentences").
- **Generation:** app sampler (0.7/40/0.95/0.05, seed 42), nPredict 512, node-llama-cpp CPU.
- **Judging:** judge.v1 (Opus, both orders) vs the frozen v0.1 refs; ratio = Σ mean-rubric(system) / Σ mean-rubric(ref), as judge-core.

## Caveats
- Dev, 1 rep (the engine row is 3 seeds). Differences < ~0.05 are within noise.
- **R is an upper bound:** passages were chosen with knowledge of the reference answer.
- **Q is closer to reachable**, but its candidates are only the gold articles. A real pack has many more distractors (Sonar's L0 measures the gap).
- The engine's post-processing (citation gates, uncited preface, health path) is not applied to the oracle answers. Closed-book and the anchors weren't post-processed either.
- Items with no fetchable passage (e.g. dng-002) run without a context.

## Implications
1. Sonar's packs + retrieval front is the lever. Its realistic ceiling is ≈ +0.06 (Q450) if the article is present **and** retrieval picks the right part.
2. **A bigger context budget helps a little:** R450 → R1500 +0.02, cw 12 → 8. It costs prefill on the phone, ~1,000 more tokens ≈ +8–12 s at 4B speeds. Not first.
3. The 4B is a capable reader. No reader swap is needed for the knowledge lever (`../../cards/dense-9b-default-model.md`).
