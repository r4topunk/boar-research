# Best-of-n sampling with cheap selection (self-consistency / MBR) for the 4B
TL;DR: sample n answers and keep the one the samples agree on (MBR/medoid) or the one best supported by the sources. **Tested offline on 40 captured prompts: the oracle ceiling is only +2/40 over a single sample, consensus gets +1, source-support −2.** The 4B's misses are systematic (33/40 items give the same verdict in all 4 samples), so sampling cannot find answers the model doesn't produce. Not worth the phone latency.
Lane: Anvil · Status: tested (offline, negative) · Priority: C
Axes moved:
- quality ≈: +1/40 with medoid selection; ceiling +2/40.
- truthfulness ≈: CW 2 in every sample, so selection cannot remove it.
- **latency ↓↓:** n× decode on a phone unless batched decode is nearly free (not shown), plus a possible n× prefill if llama.rn's parallel slots don't share the prompt KV (UNKNOWN).
- safety, retrieval, resources: none.
Fits BOAR? Technically: llama.rn has a parallel mode (`n_parallel`, `parallel.queueCompletion`, slot manager; `node_modules/llama.rn/src/types.ts` ~69–73, 410–420). Whether its slots share a prompt prefix is UNKNOWN. Phone 4B decode is ~4–6 tok/s (`android-4b-latency-budget`).
Evidence:
- **Method lineage:**
  - self-consistency (Wang et al., [arXiv 2203.11171](https://arxiv.org/abs/2203.11171)) and Universal Self-Consistency for free-form answers (Chen et al., [arXiv 2311.17311](https://arxiv.org/abs/2311.17311));
  - repeated sampling raises coverage only when correct answers exist in the sample distribution (Brown et al., "Large Language Monkeys", [arXiv 2407.21787](https://arxiv.org/abs/2407.21787)).
  - Accessed 2026-10-02, titles and abstracts as recalled. The mechanism is standard; the size is what matters here.
- **Offline replay (this card, `exp/best-of-n/`):** Qwen3-4B Q4_K_M, 40 captured app prompts with sources, n = 4 at temp 0.7 (the app sampler), precheck v2.2.

  | Selector | pass | CW | fail-missing |
  |---|---|---|---|
  | single sample (s1) | 27 | 2 | 11 |
  | medoid (MBR, content-word Jaccard) | **28** | 2 | 10 |
  | source support (key-term overlap) | 25 | 2 | 13 |
  | **oracle** (best of 4 by precheck; ceiling) | **29** | 2 | 9 |

  - Per-sample pass: 27 / 25 / 27 / 27. CW is 2 in each.
  - **33/40 items give the same status in all 4 samples.** The 7 that vary are mostly 3-of-4 passes (vit-cry-004/010/011, vit-fa-003/011/027, vit-hum-005).
  - So the headroom is ~2–5 pp on precheck, and the "used-but-wrong" / missing-fact errors repeat in every sample.
- **Batched decode on CPU** (`exp/batched-decode/`, Qwen3-4B, M1 Ultra CPU, 4 threads, GPU off):
  - aggregate decode stays flat: **16.0 / 17.6 / 17.3 tok/s for 1 / 2 / 4 parallel sequences**, so per-sequence speed falls as 1/n;
  - here decode is compute-bound (2.5 GB × 16 tok/s ≈ 40 GB/s, far below this machine's bandwidth), so this does **not** settle the phone case.
  - On the Dimensity 8300 the effective rate is ≈ 10 GB/s (Phi-3.5 at 4.0 tok/s, `android-4b-latency-budget`), which may be memory-bound, where batching would help. UNKNOWN.
  - It is cheap to settle on the device: llama.rn `context.bench(pp, tg, pl, nr)` with `pl` = 1 vs 4. Only worth doing if a test-time-compute card needs it.
Test in boar-eval: not proposed. A judged best-of-n arm would need n × the judge budget, and a +2/40 precheck ceiling doesn't justify it.
Cost to try: done (≈ 20 min of M1 Ultra GPU; no download).

## What this says about the new direction

- The precheck ceiling of best-of-4 is ~+5 pp, and CW never moves. **Errors are systematic per item, not stochastic.** Decoding-side compute (more samples, selection) cannot fix "used-but-wrong" or "fact missing".
- The levers left in my lane are **verification against sources** (P-3, queued: a self-check pass that drops or regenerates unsupported sentences) and anything that changes *what* the model sees or plans (P-1/P-2, Sonar/coordinator).
- Caveat: precheck grades key facts, not completeness. A judge might see more spread between samples on completeness than precheck does. The 33/40 identical verdicts suggest the spread is small even there. UNKNOWN until judged.
