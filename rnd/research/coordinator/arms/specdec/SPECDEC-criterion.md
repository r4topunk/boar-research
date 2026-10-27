# SPECDEC criterion (frozen 2026-10-06, before any run): speculative decoding for the 4B answer path

Why: decode is 42% of a warm A15 model answer (29.5 s p50; A15-LATENCY-BUDGET.md); A15 decode 2.3 tok/s is memory-bandwidth bound, the regime where a small draft model pays. llama.rn 0.13.0-rc.4 (our lock) exposes `speculative` with a separate draft model (`types.ts`: type 'draft-mtp', draft.model, n_max/n_min/p_min). Draft acceptance rate depends on the models and prompts, not on the hardware, so the Mac mini can measure it.

Candidates: draft = Qwen3-0.6B (Q8_0 or Q4_K_M, official Qwen GGUF) and, if vocab-compatible, the kit's Qwen2.5-1.5B-Instruct (already shipped, 0 extra bytes). Target = Qwen3-4B-Instruct-2507 Q4_K_M (kit). Draft n_max ∈ {4, 8}.
Prompts: the exact cut 5 answer prompts of v0.1 EN s44 (60 items; model-path items only), replayed through llama-server (same build as recent runs) with and without `-md`, temperature/sampling exactly as the engine.

Measures (per draft × n_max): acceptance rate, mean accepted tokens per target pass, answer text identity vs non-speculative, Mac mini decode tok/s (descriptive), draft RSS.
Projection to A15: speedup = (accepted+1)/(1 + n_max·c) per target pass with c = draft/target per-token cost ratio from parameter+bandwidth ratio (state the c used; give c ±50%); projected decode s saved at warm p50 using A15-LATENCY-BUDGET's model; memory: draft weights + KV must keep the 4B path under the 12 GB profile (state the RSS added).

Gates (to become a device-day candidate):
G1 Identity: answer text identical to non-speculative on ≥ 58/60 (greedy); any diff explained (sampling nondeterminism shown by a control-vs-control rerun).
G2 Projected A15 decode saving ≥ 20% at the central c, and ≥ 0 at c +50%.
G3 Added RAM ≤ 1.0 GiB (draft weights + draft KV).
G4 llama.rn path: confirm in the llama.rn 0.13.0-rc.4 sources (JS + native) that a separate draft model works with our init path; list the exact params; no engine code change needed beyond passing them (else describe the change).
No judge (identity gate). No blind sets. Downloads only from the official Qwen Hugging Face org; record sha256; delete if it fails.
