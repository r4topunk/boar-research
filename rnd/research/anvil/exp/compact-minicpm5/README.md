# exp compact-minicpm5 (Anvil, 2026-10-02 cycle 16)

MiniCPM5-1B Q4_K_M (`openbmb/MiniCPM5-1B-GGUF` @ `3d55fac809`, 688,065,920 B, sha256 prefix 81b64d05a23b17b3; file kept in the session scratchpad, not in this folder) vs Qwen2.5-1.5B on Kiln's 40 captured app prompts with sources, thinking off, scored by the compact-gate port (`../cite-exemplar/gate.mjs`) and precheck v2.2. Qwen rows are cycle 2's `../cite-exemplar/runs/A0-*`.
- `run.mjs <gguf> <temp> <seed> <out>`. **Thinking must be suppressed with node-llama-cpp `budgets: { thoughtTokens: 0 }`.** `enable_thinking=false` via the jinja render parameters was not enough: the first attempt returned empty text after ~19 s per item, i.e. hidden thoughts.
