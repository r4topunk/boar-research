# Upgrade the iPhone compact reader to the strongest model whose hot set fits: Qwen3.5-2B (IQ4_XS) first
TL;DR: the iPhone tier (0.379) loses after retrieval, on the 1.5B's reading. Qwen3.5-2B in non-thinking mode, the post author's own a competitor team pick, scores MMLU-Pro 55.3 / GPQA 51.6 / IFEval 61.2 against Qwen2.5-1.5B's 32.4 / 29.8 / 42.5. Its IQ4_XS file needs ~1.09 GiB hot per token, against 0.91 GiB today and a ~1.2 GB ceiling where 2B models thrash. Quality can be scored now on desktop; fit needs one iPhone probe.
Lane: Anvil · Status: ready-to-test (desktop quality arm) · Priority: B
Axes moved:
- **quality ↑, possibly large on the iPhone tier:** the vendor gap is +23 MMLU-Pro points and +22 GPQA. How much survives in RAG with the compact gate is the question.
- **latency:** decode ≈ −15–20% (hot set 1.19× and 1.30× for Q4_K_M), and Gated DeltaNet makes per-token cost flat in context length. Prefill on A15 CPU is UNKNOWN.
- **truthfulness:** UNKNOWN. Qwen3.5 small models hallucinate a lot closed-book (AA: 4B 80%), so the compact citation gate stays essential.
- resources ↑: +0.1–0.2 GiB hot.
- safety: UNKNOWN.
Fits BOAR?
- **iPhone 13: borderline.**
  - Hot sets, from my GGUF header parse (`tools/gguf_sizes.py`, 24 MB range reads):

    | Model | Hot set | Note |
    |---|---|---|
    | Qwen2.5-1.5B Q4_K_M | 0.913 GiB | runs, 14 tok/s |
    | Qwen3-1.7B Q4_K_M | 1.026 GiB | tied head |
    | **Qwen3.5-2B IQ4_XS** | ≈ 1.09 GiB | 1,172,996,352 B file; tied head, so the whole file is hot |
    | Qwen3.5-2B Q4_K_M | 1.183 GiB | |
    | MiniCPM5-2B Q4_K_M | ≈ 1.45 GiB | **thrashed at 0.35 tok/s** |
    | MiniCPM5-1B Q4_K_M | 0.531 GiB | untied: 0.105 GiB embedding lookup + 0.153 GiB head |

  - The ceiling's exact value is UNKNOWN. Step 0 of `gemma4-e2b-compact-iphone` (the Qwen2.5-1.5B quant ladder at 0.91 / 1.05 / 1.19 / 1.53 GiB) measures it for all of these.
- Android: trivially fits.
- llama.rn rc.4 has `LLM_ARCH_QWEN35` (headers). The adapter's node-llama-cpp has `qwen35.cpp`, so **no backend work**, unlike Maple.
- All files are ≤ `LOW_RAM_MAX_MODEL_BYTES` (1.6e9), so `isCompactModel` treats them as compact and the citation gate applies. Qwen3.5-2B IQ4_XS is > `AUTO_PICK_MAX_MODEL_BYTES` (1.1e9), so the arm must set the model explicitly.
- Apache-2.0 (HF cards, `unsloth/Qwen3.5-2B-GGUF` @ `f6d5376be1`, `unsloth/Qwen3-1.7B-GGUF` @ `d7f544eead`). Offline: yes.
Evidence:
- **Qwen3.5-2B non-thinking** (Qwen model card, [huggingface.co/Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B), accessed 2026-10-02): MMLU-Pro **55.3**, MMLU-Redux 69.2, GPQA **51.6**, IFEval **61.2**. Thinking mode: MMLU-Pro 66.5, IFEval 78.6. Vendor numbers.
- **Qwen2.5-1.5B-Instruct** ([Qwen2.5 blog](https://qwenlm.github.io/blog/qwen2.5-llm/)): MMLU-Pro 32.4, MMLU-redux 50.7, GPQA 29.8, IFEval 42.5. Vendor numbers.
- **the post author's own setup:** his a competitor team copy runs `qwen3.5-2b` and `minicpm5-1b` (Kiln `hypotheses.md`, verified commits 2026-09-24). That is weak evidence of quality, but strong evidence of what he will compare BOAR against.
- **In-repo:** the iPhone tier's losses are "after retrieval: declines with the gold in context (5 items), compression cutting comparison sides, and the 1.5B's use of sources". Kit + vital5 raised recall@5 0.33 → 0.63 but quality only 0.379 → 0.395 (QUEUE.md, coordinator finding 2026-10-02 01:00). A better reader is the lever left in my lane.
- **Sonar's cycle 7 (exp-08) points here too:** the "key shown but declined" bucket is generation-side, i.e. the answer is in the context and the compact model still fails. A better reader is the lever for that bucket.
- **What was already tried:** LFM2.5-1.2B (faster, worse with packs); MiniCPM5-2B and LFM2.5-2.6B (thrash). Qwen3-1.7B and Qwen3.5-2B were never measured in the repo (grep 2026-10-02).
Test in boar-eval:
- **Step 2, iPhone fit probe:** only for a model that passes step 1. Decode tok/s and RSS on s16; must be ≥ 0.7× the 1.5B's.
- **Success criterion (stated before any run), per candidate, vs main on the same seeds:**
  1. ratio Δ ≥ +0.036 (the MDE);
  2. confident-wrong not higher by more than 1 per run;
  3. unsafe on the 17 danger items ≤ main's;
  4. declines not higher by more than 10% of items (the compact gate must still pass its answers);
  5. step 2: decode ≥ 0.7× and no jetsam kill.
  - A candidate that passes 1–4 but fails 5 is recorded as "right model, wrong phone": it goes to the 6 GB-class iPhones, if BOAR ever targets them.
Cost to try: two downloads of 1.17 + 1.11 GB (coordinator OK, each > 1 GB); 4 × 72 desktop runs (~40 min at these sizes); ~300 judge calls; no engine work except the thinking-off switch already needed by Gemma/Ling/Maple.

## What would make it fail

- The fit ceiling sits below ~1.09 GiB, as MiniCPM5-2B's thrash suggests the ceiling is somewhere between 0.91 and 1.45 GiB. Step 2 catches it. **Fallback: Qwen3-1.7B at 1.03 GiB.**
- Qwen3.5's recommended sampling (temp 1.0, presence_penalty 2.0) is far from the app's (temp 0.7, top_k 40, min_p 0.05). Quality could depend on it (UNKNOWN). Run with the app's sampler, because that is what ships.
- Hybrid DeltaNet prefill on A15 CPU could be slower than dense attention. Kiln noted "hybrid models have no per-passage state to splice", which only matters for KV tricks BOAR doesn't use. UNKNOWN.

## MiniCPM5-1B note (tested offline in cycle 16: see `minicpm5-1b-compact`, C)

- 0.53 GiB hot, the lightest option by far. It is the other model in the post author's a competitor team and uses the standard `llama` arch. Its expected quality is below Qwen3.5-2B; AA phone score 45 per Kiln's answer-llms.md. Worth adding as a third arm only if step 2 shows the ceiling is below ~1.0 GiB.

Shelf: rows "Qwen3.5-2B GGUF", "Qwen3-1.7B GGUF", "MiniCPM5-1B GGUF" in `../../SHELF.md`.
