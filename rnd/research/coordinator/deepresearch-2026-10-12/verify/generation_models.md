# Verify: generation_models (Integrative Decoding, ThinkMerge, IKP, Qwen3-Next-80B)

Adversarial verification, 2026-10-12. Sources were read at the primary level: the arXiv PDFs through pdftotext (2410.01556v4, 2512.02874v1, 2604.24827v2), the IKP JSON fetched raw from GitHub, the HF Hub tree API (sizes summed per quant, GB = 10^9 B), HF config.json files, the GitHub REST API (llama.cpp PRs and compare, the BigMoeOnEdge registry and its submodule) and the local `boar-app/node_modules/llama.rn` 0.13.0-rc.7 vendored tree. Nothing under blind/ or rnd/veil/ was touched. Nothing larger than 2 MB was downloaded.

## 1. Integrative Decoding (arXiv 2410.01556, ICLR 2025): verdict CORRECTED

**Claim.** LongFact F1@128 +5.7 on Qwen2-7B, recall 57.1 → 64.2, precision +1.7. Text-level ensembles lose 3–25 F1. Gains hold at 3–32B. The method needs k parallel sample-prefixed contexts fused at the logit level.

**Evidence**
- Table 2, Qwen2 rows: Greedy "90.0 57.1 69.1", ID "91.7 (+1.7) 64.2 (+7.1) 74.8 (+5.7)". **Confirmed.** Venue: the arXiv comment reads "Accepted by ICLR 2025".
- k: "We directly set k = 16 for ID" on LongFact (§3.1). Elsewhere k was searched in {1, 4, 8, 12, 16} on the validation sets. The LongFact gains are therefore at **k = 16**, not 4.
- Fusion (Eq. 8): the next token is the argmax of the **sum of log-probabilities** across the k inputs. Each input is "[x; rj ; x]" (§2): the prompt, then sampled response j, then **the prompt again**. So each fused context is |x| + |r| + |x| long. That is more than "sample-prefixed".
- Text-level ensembles on LongFact F1@128 (Table 2):
  - SR: −11.6 … −25.5
  - FSC: −3.1 … −19.7
  - SE-RG: −10.4 … −16.8
  - **USC: −2.9 … +1.7**, near-neutral; it gains on LLaMA3, Mistral, Gemma2 and GLM4.
  - SE-SL: −1.6 … +0.6
  - "Lose 3–25" holds for the regeneration methods (SR, FSC, SE-RG), not for USC.
- Scale: Figure 3/6 is **Biographies only**, Qwen2.5 3B +3.3, 7B +8.1, 14B +7.3, 32B +10.5, 72B +9.7. LongFact was run only on the six 7–9B models. "Gains hold at 3–32B" is true for Biographies. At 3B the gain is the smallest of the five sizes.
- Cost: Table 5/9 reports "ID 1.13 (×11.04)" ms/token vs greedy at k = 4, batch 64, A100, on TruthfulQA. The footnote excludes intermediate-step tokens from the count. LongFact at k = 16 is costlier still.
- Code: github.com/YiCheng98/IntegrativeDecoding is HF Transformers (`inference_methods.py`). The GitHub API returns `license: null`.
- Searches for a llama.cpp or vLLM port found nothing: GitHub repo search for "integrative decoding llama.cpp" or "… vllm" gives 0 relevant hits, and the web search found none.

**Can it run in llama.cpp today?** Not out of the box. The C API has every primitive needed:
- `llama_batch` takes per-token seq_ids.
- `llama_get_logits_ith` (vendored `include/llama.h` l.1142) returns per-sequence logits.
- `llama_memory_seq_cp` shares the prompt prefix.
- `n_seq_max` gives distinct recurrent states for hybrid (Gated DeltaNet) models. `llama-memory-hybrid.cpp` takes `n_seq_max`.

What is missing is the decode loop: about 150–300 lines of native C++ that, at each step, reads k logit rows, sums their log-softmax, samples one token and appends it to all k sequences. It does not exist in llama.cpp examples, llama-server, llama.rn's JS API (slots run independent requests) or bmoe. A desktop approximation over llama-server's `n_probs` top-N needs one HTTP round trip per token and truncates the distribution. It is only usable for a small slice.

**Cost on the 35B MoE with expert streaming** (inference, unmeasured). Phone numbers are from CONTEXT: 4–6 tok/s decode, 32–36 tok/s prefill.
1. **k samples.** Run serially, that is k × the current answer time. Run batched, the k tokens per step route independently, so expected unique experts per layer = E·(1−(1−k_r/E)^K). That is **×1.97 at K = 2 and ×3.82 at K = 4** in expert bytes for Qwen3.6 (256 experts, 8 routed), so batching saves little when streaming-bound.
2. **Prefill.** k × (|r| + |x|) after the shared prefix. With x ≈ 1,000 tokens (prompt + 6 chunks) and r ≈ 300, k = 4 is about 5,200 tokens, ≈ 150 s at 34 tok/s.
3. **Fused decode.** K contexts consume the same token but have different hidden states, so routing overlap is unknown. The cost per step lies between ×1 and ×3.8.

At k = 4 that is ≈ 3 extra full-answer-equivalents on top of today's 3.5–5 min thinking answer. k = 16 is out of reach on a phone. On the dense 4B the batched decode is compute-light and closer to ×1–1.5 per step, but the paper's smallest-model gain (+3.3, Biographies, 3B) is the weakest.

**Corrected claim.** LongFact F1@128 on Qwen2-7B: +5.7 (69.1 → 74.8), recall 57.1 → 64.2, precision +1.7, at **k = 16**. The method sums log-probs over k inputs of the form [prompt; sample_j; prompt]. Regeneration-style text ensembles (SR, FSC, SE-RG) lose 3–25 F1; USC is −2.9…+1.7. Scale gains (Qwen2.5 3–72B, +3.3 to +10.5) are on Biographies only. There is no llama.cpp or vLLM implementation, and the repo has no licence.

**Implication for BOAR.** The ID gate stays a desktop-only ceiling test. Run it at k = 4, not 16, because the paper's LongFact number does not transfer to k = 4. Budget a native fused-decode loop: llama-server cannot do it. On a 12 GB phone the 35B deep tier at k ≥ 4 adds ≥ 3 answer-equivalents of latency, so a pass would only matter for the 4B fast tier or for a k = 2 variant.

## 2. ThinkMerge (arXiv 2512.02874, ICLR 2026): verdict CORRECTED

**Claim.** K parallel thinking traces are merged by logit averaging at the answer step, with gains on reasoning benchmarks at K = 2/4.

**Evidence**
- Venue: the ICLR 2026 poster page iclr.cc/virtual/2026/poster/10008012 lists it, OpenReview id hvit36Dyzl. **Confirmed.** arXiv v1 is dated 2025-12-02.
- Method (§3, Alg. 1): K traces are sampled up to the delimiter. Then the contexts are re-prefilled, "we average the pre-softmax logits from the K contexts and decode a single shared token". Averaging probabilities (Prob-Merge, Table 9) is worse than averaging logits, e.g. Qwen3-4B K = 2 AIME 62.0 vs 66.7.
- Tasks:
  - AIME'24/'25, HMMT, GPQA-Diamond (closed-ended).
  - LiveCodeBench v5 (open-ended code).
  - WebSailor agents on GAIA (103 text-only cases), BrowseComp-en (200 sampled) / -zh, XbenchDeepSearch. These are short-answer, web-tool tasks.
  - **No open-ended factual or long-form QA (LongFact, FActScore, SimpleQA or similar) and no closed-book knowledge task.**
- Models:
  - Closed-ended tasks: Qwen3-4B, Qwen3-14B, R1-Distill-Qwen-7B.
  - Code: DeepCoder-14B, Qwen3-8B, Qwen3-Coder-30B-A3B, Qwen3-4B-Thinking-2507, Qwen3-30B-A3B-Thinking.
  - Agents: WebSailor-3B/7B/32B.
- Reasoning gains (Table 1/2):
  - AIME'25, Qwen3-4B, K = 4: MV 68.0 → 72.0. At K = 2: 63.3 → 66.7.
  - GPQA, K = 2: +1.1 (4B), +0.8 (14B). At K = 8 the 4B Direct-Merge is **below** MV (51.6 vs 53.3).
- **Losses on the two models closest to BOAR** (Table 4, LiveCodeBench overall, Direct-Merge):
  - Qwen3-4B-Thinking: 63.53 → 60.79 / 62.01 / 62.61 at K = 8 / 4 / 2.
  - Qwen3-30B-A3B-Thinking: 69.30 → 68.39 / 68.69 / 65.65.
  - Only Shortest-K K = 2 helps the 30B-A3B (72.04).
- Agents (Table 8):
  - WebSailor-7B GAIA 35.52 → 41.26 (N = 4); Xbench 37.80 → 48.00 (+10.2).
  - WebSailor-32B GAIA 46.64 → 51.46 (+4.8).
  - WebSailor-3B collapses at N = 4/8 (GAIA 32.22 → 15.04 / 5.34): "garbage in, garbage out".
- Cost: K × thinking decode, plus re-prefill of K (question + trace) contexts, plus a K-way batched answer. The paper calls prefill "negligible" on GPU and gives no wall-time table.
- Code: none. The paper says "we plan to open-source a vLLM v1 implementation". GitHub search for "thinkmerge" returns 0, and the ICLR page has no code link.
- Distinct from best-of-N: **yes.** No complete answer is selected. Every answer token is decoded from the averaged logits of all K contexts, so it is token-level fusion, not sample selection. DEEPBO2 closed *selection* (oracle +0.038, heuristics and a 4B verifier at chance, 35B self-selection 33 % consistent). ThinkMerge is a different mechanism.

**Corrected claim.** ICLR 2026. K thinking traces, pre-softmax logits averaged across the K contexts at every answer token.
- Gains: AIME/GPQA vs majority vote (Qwen3-4B AIME K = 4 68.0 → 72.0), code (DeepCoder-14B, Qwen3-8B), and web agents at 7B/32B.
- Losses: no gain or a loss on LiveCodeBench for Qwen3-4B-Thinking and Qwen3-30B-A3B-Thinking (Direct-Merge), and a collapse for 3B agents at K ≥ 4.
- Gaps: no long-form factual QA evaluated and no public code.

**Implication for BOAR.** ThinkMerge is a new mechanism (fusion, not selection), but its evidence for our case is weak. There is no factual long-form task, and the closest models (4B thinking, 30B-A3B thinking) do not gain on the open-ended task. If it is tested at all, run only K = 2 on the desktop deep tier, behind the same seed-specificity 0-call gate. On the phone, K = 2 doubles the 512-token thinking phase on a streamed MoE whose expert union is ≈ ×2 per step, so it is ≥ ×2 the current 3.5–5 min.

## 3. IKP results file and paper (19PINE-AI/ikp, arXiv 2604.24827v2): verdict CORRECTED

**Claim.** Qwen3-Next-80B-A3B IKP factual accuracy 0.564 (T4 0.71) vs Qwen3.5-35B-A3B-thinking 0.548 (T4 0.55). Knowledge is log-linear in TOTAL params. Qwen3-4B-2507 and Qwen3.6-35B are absent from the file.

**Evidence**
- File: `data/results/evaluation_summary.json`, a list of 201 rows. The last commit is cdc59d40 (2026-07-05), "Switch scoring to lambda=0 (no penalty)". The repo was pushed 2026-07-29 and has `license: null`.
- Field semantics, recomputed from `tier_stats`: `accuracy` = **unweighted mean of per-tier correct/total with no hallucination penalty** (λ = 0; paper §4: "λ = 0 (no penalty) throughout"). `raw_accuracy` = pooled correct/total. The models note calls it "penalty-adjusted": **wrong.**
- Qwen3.x and Gemma 4 rows (accuracy / raw / T4 / T5 / T6). Mode comes from the `-think` suffix. **No precision field exists**; models were "accessed via OpenRouter API and local Ollama server" (§5), so precision is UNKNOWN, not "BF16".

  | model | mode | acc | raw | T4 | T5 | T6 |
  |---|---|---|---|---|---|---|
  | qwen3-next-80b-a3b | non-thinking | 0.564 | 0.579 | 0.71 | 0.22 | 0.07 |
  | qwen3.5-35b-a3b-think | thinking | 0.548 | 0.603 | 0.55 | 0.21 | 0.05 |
  | qwen3.5-122b-a10b-think | thinking | 0.613 | 0.675 | 0.80 | 0.39 | 0.09 |
  | qwen3.5-397b-a17b-think | thinking | 0.647 | 0.705 | 0.82 | 0.49 | 0.17 |
  | qwen3-235b-a22b-think | thinking | 0.547 | 0.612 | 0.72 | 0.19 | 0.04 |
  | qwen3-30b-a3b-think | thinking | 0.448 | 0.465 | 0.33 | 0.06 | 0.01 |
  | qwen3.5-27b-think (dense) | thinking | 0.518 | 0.575 | 0.49 | 0.17 | 0.08 |
  | qwen3.5-9b-think | thinking | 0.441 | 0.494 | 0.28 | 0.08 | 0.05 |
  | qwen3-8b-think | thinking | 0.422 | 0.471 | 0.25 | 0.09 | 0.04 |
  | qwen3.5-0.8b | non-thinking | 0.141 | 0.213 | 0.00 | 0.00 | 0.00 |
  | qwen3-0.6b | non-thinking | 0.110 | 0.116 | 0.01 | 0.01 | 0.02 |
  | gemma-4-26b-a4b | non-thinking | 0.452 | 0.468 | 0.35 | 0.10 | 0.07 |

  qwen3-14b-think, qwen3-32b-think and the proprietary qwen3.5/3.6/3.7 plus/max/flash rows are also present.
- Absent models: **Qwen3-4B-2507 (any variant) and Qwen3.6-35B-A3B are absent. Confirmed.** Only `qwen3.6-plus-think` (proprietary) appears.
- Comparability caveats found in `tier_stats`:
  - The two models were scored on **different probe counts**: T5/T6/T7 totals are 181/187/172 for Next vs 170/156/101 for the 35B.
  - Next answers wrong on 292 probes and refuses 260. The 35B-think answers wrong on 389 and refuses 87.
  - With λ = 0, the 35B's lower refusal rate inflates its score relative to a cautious model.
- Fit, Table 1 / Table 12:
  - All open models: acc = 0.159·log10(N_B) + 0.242, n = 93, R² 0.910. **Confirmed.**
  - MoE on total params: slope 0.145, intercept 0.282, R² 0.667 (0.712 overall).
  - MoE on active params: slope 0.144, intercept 0.453, R² 0.412 (0.483). **Confirmed.**
- Prediction (computed):
  - MoE-total fit: 35B → 0.506, 80B → 0.558, i.e. **+5.2 pp**. The combined fit gives +5.7 pp.
  - 4B → 35B: +13.7 pp (MoE) / +15.0 pp (combined).
  - Measured gap: **+1.6 pp** (0.564 − 0.548), because Qwen3.5-35B-think sits +4.2 pp above the fit.
  - The paper's own size estimates (Table, l.2859–2861): Next "80B → 106B (1.3×)", 35B-think "35B → 84B (2.4×)".
- Ling-2.6-flash's "adj 0.530 vs raw 0.751", cited in models_moe.md as a "heavy wrong-answer penalty", is an **incomplete run**: 300 probes, T6 has 5 probes and T7 has 0, so its tier-mean is dragged down by empty tiers. It is not a penalty.

**Corrected claim.** IKP accuracy is the λ = 0, no-penalty tier-mean.
- Qwen3-Next-80B-A3B (non-thinking): 0.564, T4 0.71.
- Qwen3.5-35B-A3B (thinking): 0.548, T4 0.55. Different probe counts, different modes, precision not recorded.
- Log-linear law: R² 0.910 over 93 open models; for MoE, total R² 0.67 > active 0.41.
- The MoE fit predicts +5.2 pp for 35B → 80B, but the measured file gap is +1.6 pp overall (+16 pp on T4 only).
- Qwen3-4B-2507 and Qwen3.6-35B are absent.

**Implication for BOAR.** The file does not establish that the 80B knows much more than our 35B overall. Its edge sits in T4 (mid-tail), while T5–T6, the tiers most like "absent knowledge", are level (0.22 vs 0.21, 0.07 vs 0.05). Keep the IKP-subset screen (Qwen3.6-35B vs Qwen3-Next-80B at the same 2-bit quant, same mode, same probes) as a hard 0-judge-call kill gate before any 30 GB download decision. Scaling by BOAR's 4B → 35B experience, the overall +1.6 pp predicts ≈ +0.01, below the MDE.

## 4. Qwen3-Next-80B-A3B fit, GGUF sizes, llama.cpp / bmoe / llama.rn support: verdict CORRECTED

**Claim.**
- It is the only open MoE above 35B with ≈ 3B active that fits the 50 GB cap with the kit.
- unsloth UD-Q2_K_XL is ≈ 27–30 GB.
- llama.cpp supports qwen3next since 2026.
- bmoe has no qwen3next recipe.

**Evidence**
- Model: HF Qwen/Qwen3-Next-80B-A3B-Instruct was created 2025-09-09, `license: apache-2.0`.
  - config.json: 48 layers, 512 experts, 10 routed, moe_intermediate 512, shared expert 512, hidden 2048, full_attention_interval 4.
  - Qwen3.6-35B-A3B: 40 layers, 256 experts, 8 routed, same widths.
  - Routed params per token: 1.51B vs 1.01B (×1.5). **Confirmed.**
- GGUF sizes, from the HF tree API for unsloth/Qwen3-Next-80B-A3B-Instruct-GGUF (created 2025-11-28):

  | quant | GB |
  |---|---|
  | UD-TQ1_0 | 20.47 |
  | UD-IQ1_S | 22.90 |
  | UD-IQ1_M | 24.41 |
  | UD-IQ2_XXS | 26.21 |
  | Q2_K | 29.17 |
  | Q2_K_L | 29.24 |
  | **UD-Q2_K_XL** | **30.13** (28.06 GiB) |
  | UD-IQ3_XXS | 33.09 |
  | Q3_K_S | 34.58 |
  | UD-Q3_K_XL | 35.64 |
  | Q3_K_M | 38.30 |
  | IQ4_XS | 42.64 |
  | UD-Q4_K_XL | 46.07 |
  | Q4_K_M | 48.51 |

- What fits under 50 GB, with the 4B (2.5 GB) and ≈ 0.3 GB of app:
  - Replacing the 35B, with a 6.5 GB kit (≤ 40.7 GB): up to **Q3_K_M 38.30**.
  - Replacing the 35B, with a 10 GB kit (≤ 37.2 GB): up to **UD-Q3_K_XL 35.64**.
  - Keeping the 35B as well (12.29 GB), with a 6.5 GB kit (≤ 28.4 GB): **UD-IQ2_XXS 26.21** or smaller.
  - Keeping the 35B, with a 10 GB kit (≤ 24.9 GB): only **UD-IQ1_M 24.41** or smaller.
  - UD-Q2_K_XL fits only as a replacement.
- llama.cpp: PR **#16095 "Model: Qwen3 Next", merged 2025-11-28** (merge ff55414c). Follow-ups include #17898 (2025-12-10), #18683/#18762 (2026-01), #19375 (2026-02-14), #25141 (2026-06-30) and #28208 "write explicit recurrent_layers for Qwen3-Next / Qwen3.5" (2026-09-07). "Since 2026" is **wrong**: support dates from late 2025.
- llama.rn 0.13.0-rc.7: `vendor/VERSIONS` pins `LLAMA_CPP_REF=b11385`, commit bf9a0cc (2026-10-04). GitHub compare shows it is 4,199 commits ahead of #16095 and 549 ahead of #28208. `vendor/llama.cpp/src/models/qwen3next.cpp` is present and `llama-arch.cpp` l.38 maps `LLM_ARCH_QWEN3NEXT, "qwen3next"`. **The pin includes qwen3next and every listed fix.**
- bmoe: `core/src/moe/arch_registry.cpp` (main) lists qwen3moe, qwen2moe, qwen35moe, gemma4, gpt-oss, lfm2moe, deepseek4, bailingmoe3, qwen4exp, nemotron_h_moe. **There is no qwen3next row (confirmed)**, and an issue search for "qwen3next" returns 0. bmoe's llama.cpp submodule (Helldez/llama.cpp @ dce96985, 2026-09-26) **already contains `src/models/qwen3next.cpp`**.
- Does Gated DeltaNet break streaming? **No evidence it does.** The current deep tier's arch, `qwen35moe`, is the same hybrid: the vendored `qwen35moe.cpp` loads "gated delta net" params and calls `build_moe_ffn`. bmoe's registry comment for qwen35moe states that, despite the hybrid stack, "streaming is one row". qwen3next also uses `build_moe_ffn`, standard `ffn_*_exps` tensors and a resident shared expert (`ffn_*_shexp`). Adding it means one registry row plus the G1 gate (streamed == resident), per `docs/adding-a-model.md`.
- "Only" fails against the models note's own table:
  - **Kimi-Linear-48B-A3B** (MIT) is > 35B total, ≈ 3B active, IQ2_XXS 12.13 GB, upstream llama.cpp since #18755 (merged 2026-02-06). It is weaker on knowledge proxies but fits.
  - LongCat-Flash-Lite (68.5B, 2.9–4.5B active) fits at Q3 (≈ 33 GB) but needs a fork.
  - "Only" is defensible as "only one with upstream support and a knowledge proxy above our 35B".

**Corrected claim.**
- Among > 35B, ≈ 3B-active open MoEs that fit 50 GB, Qwen3-Next-80B-A3B (Apache-2.0) is the only one with upstream llama.cpp support and IKP ≥ our 35B's sibling. Kimi-Linear-48B-A3B also fits and is supported, but is weaker.
- UD-Q2_K_XL = 30.13 GB. Fits: up to Q3_K_M (6.5 GB kit) or UD-Q3_K_XL (10 GB kit) if it replaces the 35B; ≤ UD-IQ2_XXS / UD-IQ1_M if both deep models ship.
- llama.cpp support: since 2025-11-28 (#16095). llama.rn 0.13 (b11385) and bmoe's llama.cpp fork both contain it.
- bmoe lacks only the registry row. The hybrid DeltaNet layers are the same family bmoe already streams for Qwen3.6.

**Implication for BOAR.** Engine plumbing is not the blocker: one bmoe row, G1, and llama.rn needs nothing. The blockers are:
- Knowledge: per §3, the overall gain is unproven; IKP shows +1.6 pp overall, with the edge in T4 only.
- Speed: 1.5× routed bytes per token and a 2.4× larger bank, so roughly 2–3.5 tok/s on a 12 GB phone (inference).
- Disk: Q2-level only if the 35B is dropped.

Run the IKP-subset screen first. If it passes, prefer UD-Q2_K_XL or UD-IQ3_XXS as a *replacement* for the 35B rather than a second deep model.

## Reconciliations
1. **IKP "penalty-adjusted" (models_moe.md) vs file semantics.** Settled: since commit cdc59d40 (2026-07-05) and paper v2 §4, `accuracy` is the λ = 0 tier-mean with no penalty. Ling-2.6-flash's low adjusted score is an incomplete probe run (T7 = 0 probes), not a penalty.
2. **"IKP results are BF16" (models_moe.md).** Not supported. The paper names OpenRouter and Ollama as access paths, and the JSON has no precision field. Treat precision as UNKNOWN.
3. **Law prediction vs file.** The law gives +5.2 pp for 35B → 80B. The file gives +1.6 pp because Qwen3.5-35B-think over-performs the fit by 4.2 pp. Use the measured file gap, plus our own same-quant screen, not the fit.
4. **ID "k = 4–16" (generation_quality.md) vs paper.** The LongFact numbers are at k = 16. The ×11 latency is at k = 4 on short TruthfulQA. A k = 4 desktop gate tests a weaker configuration than the cited +5.7.
5. **ID "text-level ensembles lose 3–25".** True for SR, FSC and SE-RG. USC is −2.9…+1.7, so "USC etc. lose" is overstated.
6. **ThinkMerge as a fit for the deep tier.** generation_quality.md says it "maps 1:1 onto our deep tier". The paper's two closest models (Qwen3-4B-Thinking, Qwen3-30B-A3B-Thinking) lose on LiveCodeBench with Direct-Merge, and no factual long-form task was evaluated. Downgrade to relevance 1–2.
7. **"llama.cpp supports qwen3next since 2026" vs "fixes merged to 2026-09" (models_moe.md).** Base support merged 2025-11-28. 2026 holds only for fixes. llama.rn 0.13's pin includes all of them, which resolves the models note's UNKNOWN about llama.rn.
8. **"Hybrid layers may break streaming / dense side not computed."** Qwen3.6 (qwen35moe), which bmoe already streams, is the same Gated-DeltaNet hybrid. Only the resident dense size of the 80B (48 layers, 12 full-attention) is still uncomputed.
9. **"Only > 35B ≈ 3B-active model that fits."** Contradicted by the note's own Kimi-Linear-48B-A3B row. Narrowed to "only one with upstream support and a stronger knowledge proxy".
