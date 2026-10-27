# Where the 4B loses on in-kit items: context assembly drops the answer (59% of in-kit loss)
TL;DR: On v0.1 items whose answer is in the Android kit's installed text (kit A + vital5, 21 items), the 4B loses 59% of its points on items where the retriever **did** fetch the answer-bearing article but the context-assembly stages dropped it before the prompt. 6 items: `onSubject` drops the article. 5 items: compression cuts the key sentence. Items whose key reaches the prompt already score 0.688, above Haiku-without-web's 0.65. This card is the evidence hub for the same-model pipeline direction in Sonar's lane; the techniques it points to get their own cards with frozen criteria.
Lane: Sonar (same-model pipeline, retrieval/context assembly) · Status: evidence · Priority: A (picks the next two technique cards)
Axes moved: diagnosis only. Quality on in-kit items, if assembly stops losing keys: up to the "key in context" level (0.688 vs 0.546).
Fits BOAR? n/a (analysis). Engine `upstream/main` 0cfd4a77; v0.1 public only (v0.2 held out).

Evidence (`exp/17-inkit-loss-stage/`; `run.py` → `result.txt`, `split.py` → `split.txt`):
- **Data:**
  - items: v0.1 public keyed items classed `in-kit-key` by `tools/coverage_classes.py --vital5`;
  - pipeline stages from Kiln's `g1plus/and-main-v5-s42-kic` (Android 4B profile, kit A + vital5, passage text in the sources event);
  - judge points: mean rubric over `and-main-v5-s42` + `s43`, both orders;
  - lost = ref − boar.

| Stage where the key is last seen | Items | Judge ratio | Share of in-kit points lost |
|---|---|---|---|
| R: not in the retriever's output | 2 (vit-hum-001, lan-cmp-004) | 0.580 | 10% |
| **A: retrieved, then dropped before the prompt** | **11** | **0.546** | **59%** |
| G: in the pre-answer passages | 8 | 0.688 | 31% |

- **Breakdown of A (11):**
  - **A1, the article is dropped by the topic filter or gates (6):**
    - lan-rsn-003 Cheetah (Common ostrich kept);
    - lan-rsn-005 Amazon River (Mackenzie River kept);
    - lan-ref-003 Apollo program (→ no source);
    - lan-cmp-005 Saltwater crocodile;
    - vit-hlt-002 Wikivoyage: Altitude sickness (→ no source);
    - lan-exp-003 Wikivoyage: Nairobi (→ no source).
    - All `grounding:off-topic-dropped-*`. Same mechanism as `topic-filter-answer-type-drops` / `onsubject-gold-drops-diagnosis`.
  - **A2, the article is kept but the key sentence is cut (5):**
    - vit-hum-002 Mozi (`context:238->101`);
    - lan-ref-004 Iceland (`498->242`);
    - lan-ref-002 American Civil War (`536->327`);
    - lan-cmp-003 India (`441->410`);
    - vit-trv-003 Chiang Mai (`849->415`).
    - Cause: compression budget or passage choice (`FAST_CONTEXT_TOKENS` lookup 450 / other 700 and the relative floor, sized for the iPhone 1.5B's TTFT).
- **Caveats:**
  - Stage R/A use article-level text for `raw` (upper bound). A can include "right article, wrong passage" from the pack's own passage selection, not only compression.
  - n = 21, 2 seeds.
  - The key-term proxy is loose (`key_in_context.py` caveats).
  - Ratios are means over items, not paired.

Techniques this points to (Sonar lane; each gets its own card, pre-validated locally per the replay-first rule before queueing):
1. **A2 → tier-aware assembly budget for the Android 4B:** larger `FAST_CONTEXT_TOKENS` on the 4B tier, and/or a compression rule that keeps the sentence carrying numbers/dates/entities for lookup questions. Cost: prefill tokens on the phone (Anvil's TTFT data). Pre-validation: replay `compressContext` (exp-08 harness, fidelity 356 vs 345 tokens) on these items' chunks at 450/700 vs ×1.5/×2 budgets, then on all 72 items: key kept vs prompt tokens added.
2. **A1 → 4B relevance check for sources the topic filter drops:** one short yes/no prompt to the resident 4B per dropped candidate (or per top-k raw candidate), instead of the lexical `onTopic`. Precedent: an LLM relevance judgment as the gate (RE-RAG's relevance estimator, arXiv 2406.05794; LLM listwise reranking, RankGPT, arXiv 2304.09542). Cost: ~k short prefills on the phone. Pre-validation: run Qwen3-4B (`shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf`, local) as the judge on the raw candidates of the 21 in-kit items. It must keep Cheetah / Amazon / Apollo / Saltwater crocodile / Altitude sickness / Nairobi and reject the noise kept today (Common ostrich, Mackenzie River).
