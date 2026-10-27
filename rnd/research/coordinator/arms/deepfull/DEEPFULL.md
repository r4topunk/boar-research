# DEEPFULL result (coordinator, 2026-10-09 06:37–08:20). Criterion DEEPFULL-criterion.md sha256 c13b5679a3aec50dc765a2f72ed69fd32b3fb540b43fca9f86fce4a9131c99e5; patch deepfull-on-deepthink.patch 63159edf… (both unchanged)
**Verdict: NO at the slice (both arms).** On the 20-item V-para slice (Haiku 5.5-low, paired vs T = deep + thinking with the succinct persona): **F1** (persona "detailed", cap 200) Δ **−0.066** (−0.134…+0.014), h2h 5/2/13; **F2** (persona "detailed" + context 1200 / cap 400) Δ **−0.013** (−0.069…+0.048), h2h 6/3/11; wins vs ref 0/0 everywhere. Neither meets "wins + 3 or Δ ≥ +0.03" → stop after stage 2, no full set, no Opus. Longer, "thorough" deep answers do not score better against the frontier reference on this set; the succinct persona and the 400/200 budgets stay.

## Identity
| item | value |
|---|---|
| trees | F1: mini `be-0cfd4a77-deepthink` (cut 6 + deepthink patch eb3f464b…), config only (`settings.personalityId = "detailed"`, persona sha recorded by the adapter). F2: `be-0cfd4a77-deepfull` = rsync of deepthink + patch 63159edf… (depth.ts DEEP_CONTEXT_TOKENS 400 → 1200, DEEP_MAX_TOKENS 200 → 400; `diff -rq` vs deepthink: ARM, DEEPFULL_PATCH_SHA256, depth.ts); tsc rc 0 on a MacBook copy |
| model / runner | Qwen3.6-35B-A3B UD-Q2_K_XL sha 96b9c0af… (re-downloaded 06:37–06:43 after deleting the Gemma GGUF; free 33 GiB), llama-server b11010 CPU, adapter 7a0282ae…, `--deep-model`, `--places` kit-vexact, detector up, `--timeout-ms 600000`, budget 1024 |
| smoke F2 (aggregates/smoke-F2.txt) | try 1 ran without `--deep-model` (driver passed arm "F2" to a runner that adds the flag only for "D"; 0 generations, infra error before the first token, archived); try 2: 2/2 deep-thinking, answers 326 / 304 words (T 87 / 65), output 1424 tokens (1034 + 390: the 400 cap nearly bound), context 684→419 / 976→397 (T 368 / 380), RSS 8.5 GB → gates PASS |
| requests | slice ids = signal20-vpara (sha 6e707734…); F1 requests 8a456815…, F2 387d7f00…; items identical to T's |

## Stage 2: slice 20 (seed 42; Haiku 5.5-low N = 4, both orders, refs 952e2c44d978 / questions aa604be6aa3f)
| arm | ratio (CI) | floor-adj | Δ vs T (CI) | Δ floor-adj | h2h >/=/< | reasoning tok p50 | budget hits /20 | answer tok p50 | total p50 (p90) | mini wall |
|---|---|---|---|---|---|---|---|---|---|---|
| T (succinct; DEEPTHINK rows) | 0.489 (0.441–0.535) | 0.347 | — | — | — | 1034 | 15 | 90 | 143.6 s | — |
| F1 persona detailed, cap 200 | 0.423 (0.376–0.472) | 0.259 | **−0.066 (−0.134…+0.014)** | −0.088 | 5 / 2 / 13 | 1034 | **20** | **190** (cap bound 20/20) | 107.0 s (117.0) | 39 min |
| F2 persona detailed, ctx 1200, cap 400 | 0.477 (0.435–0.520) | 0.325 | **−0.013 (−0.069…+0.048)** | −0.023 | 6 / 3 / 11 | 1034 | **20** | **390** (cap bound) | 125.9 s (170.2) | 46 min |
Rule: F1 NO, F2 NO (aggregates/L1-rule-F*-slice.txt). 20/20 generated, 0 errors in both. Haiku 80 calls, Opus 0.

## Reading
- The "detailed" persona makes the deep model think to the full budget on every item (20/20 vs 15/20) and write to the answer cap: at 200 tokens the answers are cut mid-text (F1, −0.066); at 400 tokens they are complete but still score slightly below the succinct answers (F2, −0.013, CI straddling 0). The judge's completeness/usefulness gain from length does not show up; the slice is 20 items (triage only).
- The context lever could not be isolated: F2 bundles it with the persona (the smoke showed the compression is relevance-driven and the 400 cap binds on ≈ 10 % of V-para items, so the expected effect was small). Not pursued further under this criterion.
- Time: F2 answers cost +40 % decode (p90 170 s); F1 is faster than T only because its answers are truncated.
- Product reading: keep the succinct persona for the deep tier; the 4B COMPLETE result (−0.80 correctness) and this one agree in direction, at a smaller size on the 35B.

## Exposures (script-only; no blind content in any context)
V-para: 2 slice generations of 20 ids (F1, F2, seed 42) + Haiku 20 ids × 2 (80 calls); T Haiku rows re-read by paired.mjs. Smoke on v0.1 (dev). Outputs: `blind/V-para/runs-deepfull/`, smoke in `boar-eval/runs/kiln/deepfull/`, aggregates in `aggregates/` (no per-item). Mini run dirs kept under the trees. Cost: Haiku 80, Opus 0, mini ≈ 1.6 h (+ 6 min download, 10 min smoke).
