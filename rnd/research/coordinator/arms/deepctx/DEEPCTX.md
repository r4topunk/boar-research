# DEEPCTX result (coordinator-run, 2026-10-10 11:57–12:3x). Criterion DEEPCTX-criterion.md sha256 b9fba1b6b435fe0b15d23a8ca61538e172f0e95a2c7a587d19fae9c86aefa1f6 (not edited); patch deepctx-on-dt512.patch 1335c2c7… (unchanged)
**Verdict: NO at the slice.** Deep tier + thinking 512 reading up to 1200 context tokens (X) vs 400 (H, the recommended configuration), 20-item V-para slice, Haiku 5.5-low N = 4 paired: X 0.513 (0.459–0.565) vs H 0.519, Δ **−0.006 (−0.036…+0.024)**, floor −0.009, h2h 4/9/7, wins 0/0 → rule NO, not a near-miss; no full set, no Opus. The lever is close to null on this set: the 400-token context cap binds on few items (prompt tokens changed by > 100 on 4/20 items, > 300 on 2/20; median prompt 302 tokens in both arms; 17/20 items kept the same sources), so most answers were produced from the same prompt and differ only by sampling. Context 400 stays.

## Identity
| item | value |
|---|---|
| tree | mini `be-0cfd4a77-deepctx` = rsync of `-dt512` (cut 6 824e0b35… + deepthink eb3f464b… + dt512 f9a1979b…) + patch 1335c2c7… (depth.ts DEEP_CONTEXT_TOKENS 400 → 1200; DEEP_MAX_TOKENS 200 kept); `diff -rq` vs dt512: ARM, DEEPCTX_PATCH_SHA256, depth.ts |
| model / runner | Qwen3.6-35B-A3B UD-Q2_K_XL sha 96b9c0af…, llama-server b11010 CPU, adapter 7a0282ae…, `tools/remote-run.sh` (= dt512's + patch/constant/ARM checks), `--deep-model`, `--places` kit-vexact, detector up throughout, `--timeout-ms 600000`, thinking 512, succinct persona, ctx 4096 |
| smoke (dx-smoke-X, 2 v0.1 items) | 2/2 `generate:deep-thinking`, reasoning 522/522, answers 82/59 words, 0 errors; prompt tokens 275 / 632 (H's smoke: 275 / 614) → PASS |
| requests | slice 781d0a47… (= H's slice requests with runId/arm rewritten; signal20-vpara 6e707734…) |

## Slice 20 (seed 42; Haiku 5.5-low N = 4, both orders, refs 952e2c44 / questions aa604be6)
| arm | ratio (CI) | floor-adj | Δ vs H (CI) | h2h >/=/< | reasoning p50 (cap hits) | answer tok p50 | prompt tok median | total p50 (p90) |
|---|---|---|---|---|---|---|---|---|
| H (400 ctx; DT512 rows) | 0.519 (0.466–0.567) | 0.384 | — | — | 522 (17/20) | 94 | 302 | 77.6 s (97.6) |
| X (1200 ctx) | 0.513 (0.459–0.565) | 0.375 | **−0.006 (−0.036…+0.024)** | 4 / 9 / 7 | 522 (17/20) | 95 | 302 | 76.7 s (103.0) |
20/20 generated, 0 errors; mini 27 min; Haiku 40 calls, Opus 0.

## Reading
- DEEPFULL's F2 (−0.013) bundled 1200 context with the "detailed" persona and cap 400; isolated here, the context change does nothing measurable because the retrieval compression already fits most V-para items in ≈ 300 prompt tokens. The deep tier's context budget is not a lever on this set; DEEPNORAG's +0.045 for the packs is about having sources at all, not about reading more of them.
- Deep-tier desktop line stays closed (model, parity, thinking, budget, persona, context, routing, retrieval, best-of-2 all measured).

## Exposures (script-only; no blind content in any context)
V-para: 1 slice generation (20 ids, seed 42) + Haiku 20 ids (40 calls); H slice rows re-read by paired.mjs. Smoke on v0.1 (dev). Outputs: `blind/V-para/runs-deepctx/`, smoke in `boar-eval/runs/kiln/deepctx/`, aggregates here. Cost: Haiku 40, Opus 0, mini ≈ 33 min (smoke 4 + slice 27 + load).
