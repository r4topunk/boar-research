# P-3b Separate small grounding checker (NLI, drop-only) for "used-but-wrong" sentences: FAIL at gate P3-NLI-0, and the set shows why no passage checker can pass
TL;DR: after Anvil's 4B self-check failed (P3-0), the coordinator moved the line to Compass: a separate small checker (≤ ~500 MB, ≤ ~2 s, drop-only). I froze a contradiction-NLI probe (mDeBERTa-v3-base multilingual, int8 ONNX 339 MB) on Anvil's 7+20 set, bar ≥ 4/7 hits and ≤ 2/20 false flags. Result: **0/7 hits, 0/20 false flags: FAIL.** The ceiling is the real finding: **none of the 7 wrong sentences is contradicted by the passages in the prompt.** They're memory claims next to off-topic passages (Chiang Mai groceries for a route question, Kirkcaldy for Smith's text). Only 2/7 contradict the answer itself. A grounding checker can't see these errors.
Lane: Compass · Status: **tested: FAIL (gate P3-NLI-0); line closed for passage-based checkers** · Priority: C
Axes moved: none (offline probe; no engine change).
Fits BOAR? The cost fits (339 MB, 0.57 s p50 desktop per answer). The signal doesn't exist in these errors.
Evidence:
- `exp/p3-nli/`: protocol.md (frozen 17:40, sha256 2fe0ffd5…), run_p3nli.py, runs.p3nli-0.jsonl, ceiling.md, README.md, SHA256SUMS.
- Model: MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 @b5113eb3 (MIT; Laurer et al. 2022, "Less annotating, more classifying", https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7).
- MiniCheck-class checkers (Tang et al. 2024, arXiv 2404.10774) predict *supported vs not*. That signal would flag all 7 targets, but also the correct memory facts in the 20 negatives. Compass's cycle-4 LLM entailment check showed no lift for the same reason, so I didn't pick it.
- Secondary: the frozen int8 artifact gets 5/8 textbook NLI pairs and misses plain factual contradictions. A phone NLI path would need a validated quantization (fp16 ~560 MB is above budget).
Test: done (gate P3-NLI-0, frozen bar, result above).
What this means for the pipeline track:
1. On the 4B, "wrong with sources present" mostly means **retrieval brought the wrong section, and the model answered from memory**. The fix is upstream: which passage reaches the prompt (Sonar P-1 keep-the-key), or a "passages don't address the question" signal that changes the wording (the reader is told the sources don't cover it, and the claim is labelled as memory), not dropping sentences.
2. The only checkable case is **self-contradiction** (India). It's a cheap, narrow check: NLI between the answer's own sentences. Its ceiling is 2/7 here, so it isn't worth an arm on its own; logged as an option.
3. A **"passage relevance" signal** is worth a future card (Options, not a task): does any passage address the question's subject? On 4/5 distinct positive items here, the passages were off-topic. It would be detected per answer (question vs passage NLI or embedding), and is honest about scope rather than a filter.
Cost spent: ~45 min, 339 MB local download (deletable), CPU-light.
