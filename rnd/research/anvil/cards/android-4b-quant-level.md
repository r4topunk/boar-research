# Higher-precision quant (Q5_K_M / Q6_K) for the 12 GB Android reader
TL;DR: the 12 GB tier has RAM to spare, so Qwen3-4B-2507 could ship as Q6_K (3.31 GB) instead of Q4_K_M (2.50 GB). The literature points to a modest factual-recall gain that probably won't clear boar-eval's MDE, at a ~25% decode cost. **Not worth an arm now.**
Lane: Anvil · Status: evidence · Priority: C
Axes moved:
- quality: ↑ small, likely below the harness MDE of 0.036.
- truthfulness: ↑ small (fewer recall slips), UNKNOWN size.
- latency ↓: decode is memory-bound, so ≈ −24% tok/s for Q6_K (3.31/2.50 GB read per token) and ≈ −14% for Q5_K_M. Prefill is roughly unchanged; rc.4 has repack GEMMs for q5_K/q6_K.
- resources ↑: +0.4–0.8 GB RAM and disk.
Fits BOAR? Android ≤ 12 GB: yes. iPhone: no (the resident ceiling). Catalog-only change (same `unsloth/Qwen3-4B-Instruct-2507-GGUF` revision `a06e946bb6`; sizes on SHELF). Offline: yes.
Evidence:
- **Factual recall under quantization:** degradation is "particularly amplified in smaller models", but "models quantized at reduced bit precision do not consistently exhibit inferior performance" and the overall effect is "modest" ([Through a Compressed Lens, arXiv 2505.13963 / TrustNLP 2026](https://arxiv.org/abs/2505.13963), accessed 2026-10-02; abstract only). Strength: moderate. It does not test GGUF K-quants.
- **Accuracy is non-monotonic in bits and hides divergence;** mixed-precision Q4_K has lower divergence than Q4_0 at the same size ([arXiv 2609.07664, 2026-09-07](https://arxiv.org/abs/2609.07664); abstract only). So any small accuracy delta between Q4_K_M and Q6_K would itself be noisy.
- **In-repo scale of effects:** boar-eval's minimum detectable Δratio at 2 runs × ~57 items is **0.036** (QUEUE.md rule #7). Gemma 4 E4B, a whole different model, moved the ratio by only −0.016. A within-model quant step is very unlikely to exceed 0.036.
- **The 4B tier's losses are mostly completeness and usefulness** (2.18 / 2.25), not correctness (3.05). Quant precision acts on correctness. See `complete-paragraph-persona` (QUEUE #12).
Test in boar-eval (only if #12 lands the 4B just under the bar and correctness becomes the gap):
- Arm Q6_K vs Q4_K_M, Android profile, 2 seeds, gate + judge.
- Success criterion (stated before any run): Δratio ≥ +0.036 (the MDE), confident-wrong not higher, decode tok/s ≥ 0.75× on desktop CPU ×4.
Cost to try: one 3.31 GB download (coordinator OK) plus ~1 h on the mini. Risk: low.

## What would change this to B

- A judged result where the 4B tier's correctness rubric, not completeness, is the main gap after #12.
- Or a GGUF KLD table for Qwen3-4B-2507 showing Q4_K_M top-1 token agreement below ~95% (UNKNOWN; none found this cycle).

Shelf: row "Qwen3-4B-Instruct-2507 GGUF quant ladder" in `../../SHELF.md`.
