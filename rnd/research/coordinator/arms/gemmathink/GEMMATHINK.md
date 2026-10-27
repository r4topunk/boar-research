# GEMMATHINK result (coordinator-run, 2026-10-09 02:32–06:35). Criterion GEMMATHINK-criterion.md sha256 46e058d3802b9cba1c701d6f7794e11184a7bda1baaab46ebc72f64050a91bef (not edited); adapter.ts ccf8cd19…, server.ts 0d069273… (boar-eval 80a16cc)
**Verdict: NO.** Gemma 4 26B-A4B + thinking 1024 (G) is **27 % faster** than Qwen3.6-35B-A3B + thinking (T) on the desktop proxy (p50 106–109 s vs 143–146 s, ratio 0.743) but **not at parity**: two-seed paired Δ raw **−0.028 (−0.057…+0.003)**, floor-adj −0.034 (−0.071…+0.004); seed 42 was level (−0.002), seed 43 clearly worse (−0.054, CI −0.082…−0.028). The PARITY-FASTER clause needs CI low ≥ −0.03 → FAIL; BETTER needs CI low > 0 → FAIL. The Qwen deep tier + thinking stays the best measured configuration; G would still be the second-best rung (vs deep without thinking +0.047 raw, +0.013…+0.077).

## Identity / gates
| item | value |
|---|---|
| tree | mini `be-0cfd4a77-gemmathink` = rsync of `-deepthink` (cut 6 PATCH_SHA256 824e0b35… + deepthink patch eb3f464b…; `diff -rq` vs deepthink: only ARM, be-repo/adapter.ts, be-repo/server.ts) with be-repo from boar-eval 80a16cc: Gemma model entry (roles ["reasoning"]) + `BOAR_THINK_KWARG=1` → `chat_template_kwargs {enable_thinking: true}` only on requests carrying a thinking budget (22/22 adapter tests, tsc 0; Qwen request bodies unchanged) |
| model | `gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf` 10,546,934,240 B, sha256 2a1d26df… verified after download (02:32–02:38); the Qwen GGUF was deleted first (disk 34 → 45 → 35 GiB; MODELS.md, DISK-LOG) |
| runner | tools/remote-run.sh (= deepthink's + adapter/server sha checks, `--deep-model gemma-4-26b-a4b-ud-q2kxl`, env BOAR_THINK_KWARG=1), `--places` kit-vexact, detector v3b up throughout, llama-server b11010 CPU `-t 4 -c 4096 --reasoning-format deepseek`, `--timeout-ms 600000`, heavy lock |
| smoke (v0.1 vit-hum-001, lan-exp-001; aggregates/smoke-G.txt) | 2/2 `generate:deep-thinking`, reasoning 576 / 1033 tokens (thinking reachable), 1033 = 1024 + budget message with `thinkingBudgetExceeded` (budget enforced on Gemma's tags), answers 390 / 323 chars, decode ≈ 12 / 9.4 tok/s, peak RSS 7.2 GB, free 35 GiB, swap 1.1 GB → **all gates PASS** |

## Stage 1: slice 20 (signal20-vpara, s42; triage only)
G 0.499 (0.455–0.539) vs T 0.489 (0.441–0.535) Haiku; paired Δ +0.010 (−0.043…+0.070), h2h 7/4/9, wins vs ref 0/0; p50 104.5 s vs 143.6 s (0.728) → clause (b) parity-faster → CONTINUE. Mini 34 min (20 items), 40 Haiku.

## Stage 2: generation (V-para 58 items; 51 judged ids; desktop proxy)
| run | n / errors | deep-thinking | reasoning tok p50 (p10) | budget hits /51 | answer tok p50 | total p50 (p90) | ttft p50 | T total p50 | mini wall |
|---|---|---|---|---|---|---|---|---|---|
| gt-G-vpara-s42 | 58 / 0 | 51/51 (7 venue `task:places`) | 995 (590) | 25 | 65 (T 89) | **106.2 s** (145.3) | 96.8 s | 142.9 s | 1.56 h |
| gt-G-vpara-s43 | 58 / 0 | 51/51 | 1033 (594) | 29 | 65 (T 91) | **108.5 s** (133.7) | 101.1 s | 146.0 s | 1.55 h |
Gemma thinks ≈ 30 % faster (reasoning ≈ 12–16 tok/s vs ≈ 9.5) and answers shorter (65 vs 89–91 tokens); budget hit on 49–57 % of items (T 61–71 %). Peak RSS 7.7 GB (T ≈ 10 GiB). Traces sha 8325deee… (s42), 40e636c8… (s43); requests 6300c728… / 41a4be5b….

## L1 (Haiku 5.5-low N = 4, both orders, 51 ids, refs 952e2c44d978 / questions aa604be6aa3f, s42)
G 0.500 (0.472–0.529) vs T 0.512 (0.486–0.539); paired Δ −0.012 (−0.043…+0.022), floor-adj −0.016, h2h 17/9/25, wins vs ref 0/0. Clause (a) FAIL; clause (b) Δ ≥ −0.03 PASS and p50 106.2 ≤ 0.75 × 142.9 = 107.2 s PASS (ratio 0.743) → CONTINUE to L2 (frozen rule, marginal on speed).

## L2 (Opus judge.v1 sharded N = 4, `--system gemmathink-G-opus`, 102 calls per seed; scales as DEEPTHINK: floor_metrics stratified by items.jsonl, D_decl 0.306; aggregates/L2-G-2seed.opus.json, paired_gap-GvsT-2seed.json, paired_gap-GvsD-2seed.json)
| arm | raw (CI) | floor-adj (CI) | above-decline (CI) | win-rate |
|---|---|---|---|---|
| **G** Gemma 4 26B + think (s42+s43) | **0.514 (0.487–0.540)** | **0.388 (0.354–0.421)** | 0.299 (0.261–0.337) | 0/51 ×2 |
| T Qwen3.6-35B + think (DEEPTHINK) | 0.542 (0.513–0.571) | 0.422 (0.385–0.459) | 0.340 (0.298–0.382) | 0/51 ×2 |
| D Qwen3.6-35B, no think (DEEPVPARA) | 0.467 (0.439–0.494) | 0.329 (0.294–0.362) | 0.232 (0.192–0.271) | 0/51 ×2 |
Per seed G − T (paired.mjs, items jointly resampled): s42 −0.002 (−0.034…+0.033), h2h 18/11/22; s43 **−0.054 (−0.082…−0.028)**, h2h 10/6/35. Two-level paired gap G − T: raw **−0.028 (−0.057…+0.003)**, floor-adj −0.034 (−0.071…+0.004), above-decl −0.040 (−0.082…+0.004). G − D: raw +0.047 (+0.013…+0.077), floor-adj +0.059 (+0.017…+0.097).
Per category G vs T (2 seeds, descriptive, aggregates/cat-GvsT-2seed.opus.json): explanation −0.030 (3/2/12 better/same/worse), comparison −0.034 (2/0/5), synthesis −0.027 (3/0/4), reasoning +0.037 (4/0/3), crypto −0.100 (1/0/4), travel-practical 0.000 (2/0/3), travel-local −0.087 (1/0/2); overall 16/2/33. Judge correctness mean is **higher** for G (3.77 vs 3.51; every category but crypto/travel-local), so the ratio loss sits in completeness/usefulness: Gemma's answers are shorter (65 vs 89 tokens) under the same 200-token answer cap.

## Reading
- Bar: G floor-adj 0.388, below 0.50 by 0.112 (CI low short by 0.146), win-rate 0. The V-para ladder stays 4B 0.26 → deep 0.33 → Gemma+think 0.39 → Qwen+think 0.42.
- Product trade: Gemma 4 26B is 1.7 GB smaller, 2.3 GB lighter in RSS and 27 % faster per answer, at ≈ −0.03 raw vs the Qwen thinking tier on this set (not resolved at parity by 2 seeds). Under the frozen rule that is NO; a product could still prefer it on memory (7.7 GB peak fits an 8 GB-class budget worse than it sounds, but better than 10 GiB) if the quality gap is accepted. Not a claim decision.
- Observation (not tested, no rescue): higher correctness with lower completeness suggests an answer-length/format lever on the Gemma deep tier (e.g. the deep answer prompt or cap); it would need its own frozen criterion.
- Cost: Haiku 142 (slice 40 + full 102; cap 160), Opus 204 (cap 204), mini ≈ 4.5 h (download 6 min, smoke 4 min, slice 34 min, s42 94 min, s43 93 min).

## Exposures (script-only; no blind content in any context)
V-para (blind/V-para): generation gt-G-vpara-s42-slice (20 ids), gt-G-vpara-s42 (58), gt-G-vpara-s43 (58); Haiku 20 ids (40) + 51 ids s42 (102); Opus 51 ids s42 + s43 (204). T Haiku/Opus rows and D Opus rows re-read by scripts. Smoke on v0.1 (dev). Outputs: `blind/V-para/runs-gemmathink/` (traces, judgments + shards, think per-item, paired JSON, paired-1seed/2seed symlink dirs); smoke in `boar-eval/runs/kiln/gemmathink/`; aggregates in `aggregates/` (no per-item). Mini run dirs kept under the gemmathink tree; the Gemma GGUF kept on the mini (35 GiB free).
