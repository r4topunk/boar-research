# QUANT17 criterion (frozen before any measurement; 2026-10-20)

Question (RT-1, model-usage/runtime.md): is Qwen3-1.7B Q4_K_M (the lite file) numerically adequate vs the full-precision model, or is a Q8_0 gate-v2 K0 screen warranted? Zero judge calls, zero paid API.

## Inputs
- Prompts: the first 30 records, in file order, of arms/gate17/traces/gate17dump-K0-main-s42.prompts.jsonl (the exact messages the 1.7B saw in K0 MAIN; enableThinking null = `--reasoning off`, so the assistant turn opens with the empty think block). The app's "Not found in this phone's offline library..." label is added after generation (not model input), so there is no answer prefix to include.
- Rendering: Qwen3 ChatML, `<|im_start|>role\ncontent<|im_end|>\n` per message, then `<|im_start|>assistant\n<think>\n\n</think>\n\n`.
- Models (unsloth/Qwen3-1.7B-GGUF @ d7f544ee, same revision for all): Q4_K_M (sha b139949c, the lite file), Q8_0 (sha 0becaa82), BF16 (reference, sha recorded in QUANT17.md).
- Binaries: llama.cpp b11010 CPU build on the mini (the engine build), 4 threads. Slot lock gen1/gen2 for every inference job; free disk >= 25 GiB.

## Measurement A: teacher-forced KLD on the answer tokens
- Sequence per item = rendered prompt + answer text + `<|im_end|>`. Answers come from step B (Q4_K_M greedy, the production file) = primary set; the Q8_0 greedy answers = secondary set (removes the bias of scoring on Q4's own text).
- Tool: tools/kld3.cpp (libllama b11010). llama-perplexity --kl-divergence was not used for the verdict because it scores only the second half of each chunk (prompt tail + answer mixed); the metric definitions are the same (KLD(ref||test) over the full vocab; top-token agreement = argmax equal; delta-p = p_test(actual token) - p_ref(actual token)), scored on answer tokens only.
- Outputs per model vs BF16: mean KLD (+- s.e. over tokens), top-token agreement %, mean delta-p.

## Measurement B: greedy generations (no judge)
- 30 prompts x {Q4_K_M, Q8_0}, llama-server b11010, temperature 0, seed 42, n_predict 512, raw rendered prompt. Report: items whose text differs, and token-level differences (length of common prefix, token count difference, first divergence position, count of differing items).

## Rule (decides, single pass, no re-runs)
- Q4 adequate (no Q8 screen) iff Q4_K_M top-token agreement vs BF16 >= 95 % AND mean KLD <= 0.05, on the primary set.
- Otherwise: queue a gate-v2 K0 screen of Q8_0 (not run here).
- The secondary set is reported only; if it disagrees with the primary verdict that is stated, but the verdict follows the primary set.
