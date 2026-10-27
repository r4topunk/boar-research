# Kiln: hypotheses for quality-per-second on the phone (sprint 1)

Date: 2026-09-30 · Author: Kiln (R&D) · Scope: research only; nothing in `boar-app/` or `wt/` was touched.

## TL;DR

- **The problem is no longer the fast tier's TTFT.** The iPhone fast tier is already at **≤5 s TTFT, score 0.48** (CI 0.42–0.56) ([06-resumo-manha](../../review/research-pipeline/06-resumo-manha-2026-09-30.md)). That summary says the corpus/search lever is exhausted on v2 and **what remains is the model's reading of the sources**. the post author's complaint is "slower **and less effective at difficult questions**" ([ADR 0001 §0](../../review/adr-moe-deep/docs_adr_0001-deep-tier.md)).
- **#1 hypothesis (K1): an in-RAM sparse MoE reader** (Ling-3.0-tiny, 7.9B total / 1.3B active, MIT, Q4_K_M 4.82 GB). It has roughly the per-token compute of the current 1.5B and the knowledge of an 8B. It is the post author's "big total, small active" thesis with no flash streaming, no 10.7 GiB prefill peak and no engine project. **Nobody has measured it anywhere in the repo.** It is still an open, unchecked task for Android ([IPHONE-MODEL-AB-rc6](../../review/IPHONE-MODEL-AB-rc6.md) line 55).
- **Precomputed passage KV (TurboRAG/CacheBlend) ranks near the bottom.** Three reasons:
  - It cannot splice per-passage state on the hybrid linear-attention models that make up the whole 2026 roster.
  - It costs 28–144 KiB of disk per corpus token.
  - The fast-tier prompts it would speed up are already 150–350 tokens, which is ~2–3 s of prefill.
- **Already measured in the repo, do not redo:**
  - k=6 experts: +20–25% decode.
  - n-gram speculation: 1.6× at temp 0, 1.06× at temp 0.7, negative on MoE.
  - Speculation on streamed MoE: negative.
  - ubatch-only chunked prefill: does **not** lower the 10.7 GiB peak.
  - LFM2.5-1.2B: faster but worse with packs.
  - Temp 0.2 vs 0.7: no quality change.
  - Sources in the user turn: reverted.
- **Proposed experiment 01 (awaiting approval): `exp-01-inram-moe-reader`.**
  - Setup: Ling-3.0-tiny vs Qwen3-4B vs Qwen2.5-1.5B on identical RAG contexts, Mac mini M4 CPU `-t 4`.
  - Measurements: TTFT, tok/s, peak RSS and blind judge vs Opus+web on 12 hard v2 questions.
  - Questions: v2 (12), plus Lantern's `vitalik-evalset` rev2 split into the a competitor team verbatim items (27) and the rest (25). Each is scored separately, plus the confident-wrong rate.
  - Cost: 4.82 GB download, 3 heavy-queue jobs of ~20 min each, ~1 day wall.
  - Candidate swap: Maple-Preview 20B-A1B (K1b). TQ1_0 is 4.98 GB and TQ2_0 is 5.90 GB (>5 GB). Either needs a llama.cpp rebuild on the mini.

## 1. What "quality per second" means here

| Term | Definition | Source of the number |
|---|---|---|
| Quality | Win score vs Opus + web (blind, both A/B orders, Claude judge) on v2 items | `wt/eval/eval/README.md` (method), `wt/eval/eval/references/v2/claude-code__opus.jsonl` |
| Time | TTFT and total seconds per answer, on the same prompt, `-t 4` CPU (phone proxy) | llama.cpp server `timings` |
| Quality per second | Quality at a fixed time budget. A change wins if it raises quality without raising p50 TTFT by >30%, or cuts p50 TTFT by ≥30% without losing quality beyond noise (±0.05, see 06 §"Ruído") | — |
| "Difficult questions" | v2 categories where the fast tier loses: `crypto-expert` (20), `math-reasoning` (6), `travel-practical` (10), `danger-situation` (5). `local-food*` is excluded because the places route answers it without an LLM (vegan 85%) | `wt/eval/eval/dataset/questions.v2.jsonl` (counted today) |

## 2. Ranked hypotheses

Scale 1–5. **G** = expected gain on quality-per-second on the phone for difficult questions. **C** = cost to test *and* ship (1 = hours). **R** = risk that it fails or is not shippable before 2026-10-31. **Score = G × (6−C) × (6−R)**, max 125.

| # | Hypothesis | G | C | R | Score | Already measured in repo? |
|---|---|---:|---:|---:|---:|---|
| **K1** | **In-RAM sparse MoE reader** (Ling-3.0-tiny, 1.3B active) beats the dense 1.5B/4B on difficult questions at ≤1.5B-class latency | 5 | 2 | 3 | **60** | **No.** Paper-only ([answer-llms.md](../../review/models-research/answer-llms.md): AA index 15 vs 7 for LFM2.5-8B-A1B; 69.5% non-hallucination). The Android s16 run is still unchecked |
| K2 | **Context budget curve**: sentence compression at 1200 / 800 / 400 tokens. Measures what ≤400 tokens costs in quality | 2 | 1 | 1 | 50 | **Partly.** Compression kept (748→185, 1341→513 tokens), but "**quality effect not measured**" ([02 §3](../../review/research-pipeline/02-medicoes-existentes.md)) |
| K3 | **N-gram / prompt-lookup speculation at low temperature** on the dense fast tier | 3 | 3 | 2 | 36 | **Yes, on its own:** 1.6× at temp 0, 1.06× at 0.7 (`boar-app/docs/SPECULATIVE_DECODING.md`; mini `<runner>/spikes/results/spec-qwen15`). **New fact that reopens it:** temp 0.2 vs 0.7 is quality-neutral (0.44 vs 0.43, [06](../../review/research-pipeline/06-resumo-manha-2026-09-30.md)). Needs a llama.rn native patch (`rn-completion.cpp` ignores `ngram-*`) |
| K4 | **Short, capped thinking** (e.g. ≤128 think tokens) for difficult questions only | 3 | 2 | 3 | 36 | **Negative evidence only:** LFM2.5-8B-A1B always-thinking → 85% of output is `<think>`, TTFT 27 s, 4/17 empty ([02 §1](../../review/research-pipeline/02-medicoes-existentes.md)). A capped budget was never tried |
| K5 | **Deep tier on a 12 GB Android** with ≤400 tokens + ≤200 answer + k=6 (ADR option a) | 4 | 3 | 4 | 24 | **Projected only** (~50 s total, ADR §4.4). **Blocked:** no 12 GB Android in the lab, and the 12.3 GB model was deleted from the mini (ADR §9) |
| K6 | **Prefill-light architectures** (LFM2.5 conv hybrid) as the reader | 2 | 2 | 3 | 24 | **Yes, negative for the compact tier:** LFM2.5-1.2B is 1.6× faster but scores lower with packs (0.39 vs 0.43; crypto 25% vs 48%). The 2.6B always thinks and thrashes on 4 GB ([06](../../review/research-pipeline/06-resumo-manha-2026-09-30.md), [IPHONE-MODEL-AB-rc6](../../review/IPHONE-MODEL-AB-rc6.md)) |
| K7 | **Bounded-staging prefill** for the streamed MoE (fix the 10.7 GiB peak) | 3 | 4 | 3 | 18 | **Yes, the naive version fails:** ubatch 64 still peaks at 10.73 GiB (ADR §4.2). A real fix is an engine patch in BigMoeOnEdge. Blocked on the same >5 GB download and mini disk |
| K8 | **iqk aarch64 MoE kernels** (IQ2_XS/IQ3_XXS): 2× prefill | 3 | 4 | 3 | 18 | **Not by us.** a competitor team measured 73 s → 37 s on a 1,216-token prompt ([moe-and-speed §5](../../review/models-research/moe-and-speed.md), S13). Deep tier only |
| K9 | **Draft-model speculation** (small draft → dense 4B) | 2 | 3 | 3 | 18 | **MoE only, negative:** −3% to −60% on GPU, −18% to −29% on phone ([moe-and-speed §5](../../review/models-research/moe-and-speed.md)). Dense 4B + draft: never measured. llama.rn does not drive draft models |
| K10 | **k=6 routed experts** on the deep tier | 1 | 1 | 2 | 20 | **Yes:** +20–25% decode on the M4 (8.7 vs 7.3 tok/s, ADR §4.1). Quality effect unmeasured. Only useful if K5 passes |
| K11 | **Precomputed passage KV on disk** (TurboRAG / CacheBlend) | 2 | 5 | 4 | 4 | **No.** See §3 for why it ranks low |
| K12 | **Engram-class n-gram model** (Qwen3.8-Flash-Next) | — | — | — | 0 | **Out:** smallest file ~80–85 GB against a 50 GB total disk budget ([moe-and-speed §2](../../review/models-research/moe-and-speed.md)) |
| K13 | **LLMLingua-style learned compressor** | 1 | 3 | 3 | 9 | Reviewed, left out: "real gain ≤18%, second model" ([research-pipeline README §4](../../review/research-pipeline/README.md)) |

**K1b (added 2026-09-30, from Lantern's radar): Maple-Preview 20B-A1B.** It is closer to the post author's shape than Ling: 20B total, ~1B active, 256 experts with 8 routed, 24 layers ([deepgrove/maple-preview](https://huggingface.co/deepgrove/maple-preview) config, MIT).

| Check | Result (verified today) |
|---|---|
| GGUF size | `maple-preview-TQ1_0-head-Q4_K.gguf` is 4,984,016,416 B (<5 GB). TQ2_0 variants are 5.9–6.3 GB ([GGUF repo](https://huggingface.co/deepgrove/maple-preview-GGUF)) |
| GGUF architecture | `maple` (read from the file header over an HTTP range request) |
| In llama.rn b11010 | Yes: `vendor/llama.cpp/src/llama-arch.cpp:65` |
| In the mini's llama.cpp `0e8c83e` (2026-08-28) | **No.** Testing it needs a fresh llama.cpp build (≥ b11010) on the mini |

Scores: G 5, C 3, R 4, total 30. Ternary (TQ1_0) kernel speed on ARM CPU and quality are UNKNOWN, and no Kiln run exists.

Lantern's radar ([rnd/lantern/radar.md](../lantern/radar.md), 2026-09-30) adds four items. None has a Kiln run.

| # | Item | G | C | R | Score | Note |
|---|---|---:|---:|---:|---:|---|
| K14 | 8→4 active experts on Qwen3.6-35B-A3B with renormalization, −0.35 MMLU ([arXiv 2609.04575](https://arxiv.org/abs/2609.04575)) | 3 | 1 | 3 | 45 | Supersedes K10 (8→6), and roughly doubles decode by arithmetic. **Deep tier only**, so it inherits K5's blockers (no 12 GB Android, 12.3 GB re-download) |
| K15 | Spark-X2.5-4B Q4_K_M 2.6 GB (Apache-2.0), arch `spark2_5` in llama.rn rc.4 | 3 | 2 | 3 | 36 | Dense 4B, so its prefill cost is the same as Qwen3-4B. It only wins on quality |
| K16 | DSpark drafter: 2.3–2.5× on dense 1–3B, 1.18× on an 8B-A1B MoE | 3 | 4 | 3 | 18 | llama.rn drives only `draft-mtp` (`shouldUseMTP`, verified by Lantern), so this needs a native patch |
| K17 | RAZOR-pruned Qwen3.6 at 19.4B total | 3 | 4 | 4 | 12 | The source download is ~70 GB and needs an OK |

Known risk for K1b: low-bit quantization loses factual knowledge ([arXiv 2609.32902](https://arxiv.org/abs/2609.32902)). A ternary Maple has to pass the knowledge items in the eval set, not just be fast.

### Why K1 is first (and K2, the cheapest, is second)

K2 is cheaper and safer, but its ceiling is lower:
- The fast-tier prompts after compression are already **150–350 tokens** on the iPhone ([02 §1](../../review/research-pipeline/02-medicoes-existentes.md), v12 receipts).
- A 400-token cap therefore changes little on the tier people use.
- It only matters for the deep tier, which is blocked (K5).

K1 attacks the stated failure, "less effective at difficult questions", at the latency the product already has:
- Active parameters drive per-token compute, both prefill and decode. Ling's 1.3B active is about the size of the current 1.5B dense.
- Its 7.9B total gives it an 8B-class knowledge store. It fits in RAM on a 12 GB Android (4.8 GB file), so there is no streaming, no expert-union peak and no llama.rn patch.
- The runtime is ready: `bailingmoe3` is in the mini's llama.cpp build (`0e8c83e`, 2026-08-28; `grep -c bailingmoe3 src/llama-arch.cpp` = 1, checked today) and in llama.rn's b11010 (answer-llms.md).

Main risks:
- Every published Ling number is in thinking mode ([answer-llms.md](../../review/models-research/answer-llms.md)).
- The KDA (linear attention) + MLA kernels are new, and their ARM CPU speed is UNKNOWN.
- The chat parser (#28682) landed after b11010.

K1 answers all three on the mini in one day. The iPhone 13 is out of scope: the file is 4.8 GB against 4 GB of RAM, so this is the Android fast tier or the "go deeper" button.

## 3. Precomputed passage KV (TurboRAG / CacheBlend): why it ranks low

What the papers claim (not reproduced):
- [TurboRAG, arXiv 2410.07590](https://arxiv.org/abs/2410.07590): precomputes and stores the document KV offline, so TTFT drops "by up to 9.4× (8.6× on average)". It **fine-tunes the model** to keep accuracy with independent per-chunk attention.
- [CacheBlend, arXiv 2405.16444](https://arxiv.org/abs/2405.16444): reuses non-prefix chunk KV and "selectively recomputes the KV values of a small subset of tokens" to recover cross-chunk attention.

Why it does not fit BOAR before 2026-10-31:

| Blocker | Evidence |
|---|---|
| **Hybrid models have no per-passage state to splice.** Qwen3.5/3.6 (Gated DeltaNet), LFM2/2.5 (conv) and Ling-3.0 (KDA) all have recurrent state that depends on every earlier token, so a passage's state computed alone is wrong once the passage sits after other text. Only pure-attention models qualify: Qwen2.5-1.5B, Qwen3-4B, MiniCPM5 (`llama`) | Architectures in [answer-llms.md](../../review/models-research/answer-llms.md) table A; Ling `model_type: bailing_hybrid` (HF config, fetched today) |
| **Disk cost per corpus token** (fp16 K+V): Qwen2.5-1.5B = 28 layers × 2 KV heads × 128 × 2 × 2 B = **28 KiB/token**. Qwen3-4B = 36 × 8 × 128 × 2 × 2 B = **144 KiB/token**. For example, 10k passages × 150 tokens = 1.5M tokens = **42 GB** (1.5B) or **216 GB** (4B), against a 50 GB total budget | HF `config.json` of both models (fetched today); arithmetic here |
| **Little TTFT left to save on the fast tier.** 150–350 prompt tokens at ~100 tok/s is ~1.5–3.5 s, and the fixed-prefix KV is already reused (answer-prefix prefill −65% on M1) | [02 §1, §3](../../review/research-pipeline/02-medicoes-existentes.md) |
| **Quality risk without a fine-tune.** TurboRAG needs one. CacheBlend's selective recompute is not in llama.cpp/llama.rn (UNKNOWN: no upstream PR found; not searched exhaustively) | Abstracts above |
| **Engine work.** It needs per-sequence state load, `seq_cp` and a position shift in llama.rn. llama.rn exposes `saveSession`/`loadSession` for the whole context only | [moe-and-speed §5](../../review/models-research/moe-and-speed.md) row "Prompt / KV prefix reuse" |

The one narrow variant worth keeping on the watchlist: **session KV for a small, fixed hot set**. Examples are the instant-answer topic docs, or a per-city Wikivoyage lead. A few MB on a pure-attention model, loaded with `loadSession`, with no splicing because the doc is the prefix. It only pays off if a later receipt shows those prompts repeating.

## 3b. Kill rule for every experiment (coordinator, 2026-09-30, after exp-02)

Paired, with the same instrument on both sides (blind hand labels or the judge, not precheck alone):
- **kill** if the candidate's pass% is more than **5 pp below** the baseline's,
- **or** its confident-wrong% is more than **5 pp above** the baseline's.

The old rule had no equivalence margin, and it killed Maple over a 1-item tie ([exp-02 §5a](exp-02-maple/README.md)).

## 4. Decisions / Options / Tasks

**Decisions (proposed, reversible)**
- D1. Kiln's first experiment is **K1** (in-RAM sparse MoE reader). It is the only top-3 item that targets "less effective at difficult questions" and needs no engine patch.
- D2. Kiln does **not** reopen the streamed deep tier (K5, K7, K8, K10) in this sprint. ADR 0001 §9 triggers T1 and T2 have not fired.
- D3. K11 (precomputed KV) is not pursued before 2026-10-31. It stays on the watchlist in its narrow "fixed hot set" variant only.

**Options (exploration, no commitment)**
- O1. After K1, run K2 (budget curve) on the winning reader. It is cheap: the same harness with a different budget.
- O2. K3 (n-gram at temp 0.2) as a second quick experiment on the mini with the existing `spec-bench.sh`, before anyone patches llama.rn.
- O3. K4 (capped thinking) on Ling, if Ling in no-think mode loses on `math-reasoning`.

**Tasks**
- [ ] T1. Coordinator approves exp-01 (machine, 4.82 GB download, mini disk). **Blocking.**
- [ ] T2. Build `rnd/kiln/exp-01-inram-moe-reader/` (plan in §5). Done when the README has TTFT/tok/s/peak RSS/quality for 3 models × 12 questions.
- [ ] T3. Go/no-go recommendation (deliverable 3) with success criterion and rollback.
- [ ] T4. **exp-02: Maple-Preview 20B-A1B.** Queued by the coordinator, and the 5.5 GiB download is approved.
  - File: `maple-preview-TQ2_0-head-Q4_K.gguf`, 5,901,782,560 B, sha256 `221f792c…477a9e`, HF `deepgrove/maple-preview-GGUF` @ `f5466f9`.
  - Blocked on the runtime: the mini's llama.cpp `0e8c83e` has no `maple` arch. The arch landed in PR [#27000](https://github.com/ggml-org/llama.cpp/pull/27000), merged 2026-09-14 as `3d10bcd`. Tag `b11010` (`4bc272f`) is 53 commits ahead of it, so it contains `maple`.
  - Fix: a separate CPU build at `b11010` in `<runner>/spikes/llama-b11010`, which matches llama.rn rc.4.
  - Order: after the Ling GGUF from exp-01 is deleted.
  - Comparison: Maple vs Qwen3-4B, with Ling's exp-01 numbers alongside, on the factual + crypto + vegan ids from `rnd/lantern/handoff-eval.md`.
  - **Kill criterion:** Maple's % factual correct is below Qwen3-4B's.

## 5. Proposed experiment 01 (for approval, not started)

| Item | Value |
|---|---|
| Name | `exp-01-inram-moe-reader` |
| Question | At the same RAG context, does Ling-3.0-tiny (1.3B active) beat Qwen2.5-1.5B and Qwen3-4B on difficult questions, and at what TTFT / tok/s / peak RSS? |
| Machine | Mac mini M4 16 GB (`<on the mini>`), CPU only, `-t 4`, through `<runner>/bin/run-heavy Kiln …` (one job). llama.cpp `0e8c83e` `build-cpu/bin/llama-server`, already built. Record `loadavg` per request (the mini showed load 35–57 today) |
| Models | Qwen2.5-1.5B Q4_K_M, Qwen3-4B-2507 Q4_K_M (already on the mini). **Ling-3.0-tiny Q4_K_M, 4,823,894,944 B, sha256 `246d67d4…51d7be9`**, HF `inclusionAI/Ling-3.0-tiny-GGUF` @ `01b850e`, MIT (new download) |
| Questions | **Two sets, scored separately** (Lantern's recommendation): (a) 12 from v2 (6 `crypto-expert`, 4 `math-reasoning`, 2 `travel-practical`), scored pairwise against the Opus+web references; (b) [`rnd/lantern/vitalik-evalset.jsonl`](../lantern/vitalik-evalset.jsonl) rev2: 58 items, 54 unique. It is reported in two slices:
- (b1) **a competitor team verbatim**: `source=a competitor repo`, 27 unique. These are the post author's own test cases, so this is the primary number.
- (b2) the other BOAR-style items: 25 unique.

`vit-trv-001/002` are left out because "near me" places answers go through the no-LLM route. Duplicates (`duplicate_of`) are dropped, which leaves 52 items to run. Set (b) has no Opus references, so it is scored by the deterministic pre-check (`grading.must_any`/`forbid`/`refuse_ok`) plus a judge grading against the item `rubric`. Items to watch: `vit-sci-003` (prefill+decode arithmetic), `vit-hum-001..006` (long synthesis a 1B gets wrong) and `vit-fa-001/002` ("Tell me about X") |
| Extra metric | **Confident-wrong rate:** the share of answers that fail `must_any`/`forbid` without refusing |
| Context | Identical for all models: the fast-tier RAG context (compressed sources + system prompt) dumped once per question. Answers ≤300 tokens, temp 0.2, `enable_thinking=false` where the template allows it |
| Metrics | TTFT (prompt_ms), prefill tok/s, decode tok/s, total s (server `timings`), peak RSS (`/usr/bin/time -l`), quality = blind win score vs Opus+web references v2 (existing judge method, both orders, `claude -p` [usage detail removed], no paid API) |
| Success (for a "go" to deliverable 3) | Ling ≥ Qwen3-4B on quality (Δ ≥ 0, n=12) **and** TTFT p50 ≤ 1.5× Qwen2.5-1.5B **and** peak RSS ≤ 6 GB |

Input from Lantern (2026-09-30), which changes how exp-01 reports its results:
- **the post author looks at prefill separately.** His 2026-09-17 post ([x.com/VitalikButerin/status/2100388909410885974](https://x.com/VitalikButerin/status/2100388909410885974)) reports input tok/s and output tok/s as two numbers: 110–373 t/s prefill and 28–33 t/s decode on a Strix Halo. So exp-01 reports **prefill tok/s as its own metric**, not only TTFT. UNKNOWN: this figure comes from Lantern, not from reading the post myself.
- **His own a competitor team copy uses small dense models:** `minicpm5-1b` (think on and off) and `qwen3.5-2b`. The copy is [a competitor repo]([competitor repo link removed]). I verified the commits `337d334545`, `87bb6e9abd` and `769e85d162` exist, all dated 2026-09-24, two days before his test. Those two models are the natural baseline to add at n≥30. They are not in exp-01 because the approval allows no second download on the mini this round.
- His retrieval changes, for Lantern and P3 rather than Kiln: int8 vector top-k ranked above BM25, LLM keyword expansion with 2 seeds, and a title boost.

Estimated cost:
- Download: **4.82 GB**, once, under the 5 GB rule.
- Mini disk: **UNKNOWN whether it is allowed.** The mini has 24 GiB free today, and Caldera's floor is 20 GB, so after the download it would sit at ~19.5 GiB. It needs an OK, or a place to put the file.
- Heavy compute: 64 questions (12 + 52) × 3 models = 192 answers, estimated at **~60–65 min**. The per-answer estimate is ~12 s for the 1.5B, ~30 s for the 4B and ~18 s for Ling (UNKNOWN), all on M4 CPU `-t 4` with ≤300 tokens. That is over the 30 min rule, so the plan is 3 heavy jobs of about 20 min each (v2, b1, b2).
- Judge: 12 × 3 × 2 orders = 72 pairwise calls, plus 52 × 3 = 156 rubric calls. That is ~230 `claude -p` calls, ~2.5 h at a 5 s gap, [usage detail removed] only. The deterministic pre-check is instant.
- Wall time: ~1 day including the harness.

## UNKNOWN

- Ling-3.0-tiny's no-think quality and ARM/M4 CPU speed. That is the point of the experiment.
- Whether the mini's `llama-server` `--jinja` renders Ling-3.0's chat template correctly without the #28682 parser. The plan falls back to a raw prompt plus a manual template if it does not.
- M4 CPU → phone transfer: tok/s is an upper bound only (ADR §4.4). The quality numbers transfer.
- Mini load during the run. The contamination risk is noted, and `loadavg` is logged per request.
- Whether CacheBlend-style selective recompute exists in any llama.cpp fork (not searched exhaustively).

**Metric of this deliverable:** 13 techniques ranked. 8 of them have a prior measurement or a hard blocker in the repo, so only 5 are genuinely untested (K1, K2, K4, K9-dense, K11).
**Next step:** coordinator approval for exp-01 (download + mini disk).
