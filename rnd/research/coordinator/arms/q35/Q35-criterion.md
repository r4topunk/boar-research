# Q35 (Qwen3.5-4B as the 12 GB default reader) — screen frozen 2026-10-05 by the coordinator before any download or run

Model: unsloth/Qwen3.5-4B-GGUF, Qwen3.5-4B-Q4_K_M.gguf (2,740,937,888 B per anvil/exp/outofkit/models.md; Apache-2.0), non-thinking (enable_thinking false). Record sha256 at download.
Baseline: Qwen3-4B-Instruct-2507 Q4_K_M closed-book on v0.1 EN = 0.487 (judge.v1; judge.v1-med shown equivalent, κ 1.000). Same closed-book harness as Anvil's out-of-kit sweep (dense-9b-default-model.md).

## Screen (L0/L1-lite)
- Closed-book v0.1 EN 57 items, seed 44, judge.v1-med (both orders).
- Decode speed: llama-bench tg64 on the idle mini, Qwen3.5-4B vs Qwen3-4B, same quant class and threads.
- Memory: peak RSS at 4k context.
GO to a full-engine L1 iff: closed-book ratio ≥ 0.517 (baseline + 0.03); decode ≥ 0.8× Qwen3-4B; peak RSS ≤ Qwen3-4B + 0.5 GiB; 0 empty answers; thinking text never leaks into answers.
## Full-engine L1 (only after GO)
cut 3 with the reader swapped, v0.1 EN s44 + s45, ALL items judged (judge.v1-med) vs same-day cut 3 control; ADOPT iff Δ ≥ +0.02 with CI90 low > 0, unsafe 0, cw not up, total time ≤ 1.2× cut 3.
Stop rule: none (a screen FAIL ends Q35).
