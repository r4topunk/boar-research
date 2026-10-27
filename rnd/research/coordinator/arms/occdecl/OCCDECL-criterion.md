# OCCDECL criterion (frozen 2026-10-20 before any candidate generation)

## Question
On the LITEPACKS system (Qwen3-1.7B, LITEDECLINE_OFF=5, refuse-by-default product read through the corrected labels), does the OCCRAG hybrid
with OCC abstentions turned into the engine's refusal (instead of a Qwen fallback) cut default-mode confident errors (CE-unwarned) beyond the
measured null, without false refusals, and at what latency? Variant A = OCC-RAG-1.7B Q4_K_M, variant B = OCC-RAG-0.6B Q4_K_M (latency question).

## Candidates (be/adapter-litedecline.ts only; engine source untouched)
- occdecl-A.patch (sha256 in occdecl-A.patch.sha256): occ-ai/OCC-RAG-1.7B-GGUF @ 57938bfa, OCC-RAG-1.7B-Q4_K_M.gguf, sha256 5ff807a9...412a51 (MIT).
- occdecl-B.patch (sha256 in occdecl-B.patch.sha256): occ-ai/OCC-RAG-0.6B-GGUF @ 53da9f5d2c18eb685a9752c6473c59b4b186ca63, OCC-RAG-0.6B-Q4_K_M.gguf,
  396,701,824 B, sha256 2b0bf248d0cdd60ea37c0fa092134acea35ee4bca0ee11ee031b91bf04281d17 (= HF LFS oid; MIT). The two patches differ only in OCC_FILE.
- Both = arms/occrag/occrag.patch (hybrid: OCC answers only generations with >= 1 engine context chunk; native format, documents via
  chat_template_kwargs, greedy, answer section only, trace cap 512 + forced close 8 + 64; second llama-server b11010 with --special) with:
  - status read case-insensitively ("unanswerable" = UNANSWERABLE);
  - route `occ-decline`: status UNANSWERABLE, or a valid status with an empty / "Not enough information" answer -> the adapter returns the engine's
    refusal string "I didn't find this in this phone's library." (answer.ts); NO Qwen call;
  - route `occ-decline-malformed`: malformed trace (status not ANSWERABLE/UNANSWERABLE or missing) whose answer section matches
    /not enough information|(sources?|context|passages?|documents?|text) (do|does) not (contain|provide|mention|include)|unanswerable/i -> the same refusal;
  - other malformed (`occ-malformed-fallback-qwen`) and looped traces (`occ-looped-fallback-qwen`) fall back to Qwen3-1.7B with the original request, as before;
  - sidecar adds OCC prompt/predicted tokens and ms (for the tg rate).
  The refusal string then goes through the engine's post-processing like any model text (with LITEDECLINE_OFF=5 the uncited-with-sources release may
  prepend the warning line); labels.py counts it as a decline either way (ENGINE_DECLINE).
- Classifier check on the OCCRAG sidecars (0 LLM, before freezing): K0 8 decline + 2 decline-malformed (= REREAD's 10), K1 15 + 2 (= REREAD's 17).

## Sets and controls (dev only)
- Stage 1: GATE v2 screens arms/null-cal/pool/screen2-K0.ids (sha 891b67e2..., 30 problems + 20 sentinels) and screen2-K1.ids (sha 2d45ca83...,
  21 + 20), vs the merged mini controls null-cal/control/pool-K0.json / pool-K1.json, via null-cal/tools/run_pool.sh (SCREEN_JSON set).
- Gate: arms/null-cal/GATE-V2.md, sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982 (screen_gate_v2.py sha256 fa726fc0...):
  GO iff net >= 10 (K0) / 9 (K1), false refusals <= 2/20 (K0) / 4/20 (K1), U_cov delta >= -0.059 (K0) / -0.071 (K1).
- Stage 2: arms/lp-screens/main-97.ids (MAIN n 97) on K0 vs the mini K0 MAIN control (lpctl-K0-main-s42, inside pool-K0.json).

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders (run_pool.sh); answers byte-identical to the control reuse control judgments.
0 Opus, 0 paid APIs. calls_cap: Haiku 400 for stage 1 (4 screens), 400 for stage 2.

## Decision rule (stated before running)
- Stage 1, per variant and pack set: the GATE v2 line printed by screen_gate_v2.py (GO/NO-GO as above). Reported with it, not gated:
  CE-unwarned count on the screen (control -> candidate), false refusals, U_cov delta, sentinels worse; OCC route counts (answered / decline /
  decline-malformed / malformed->Qwen / looped->Qwen / qwen-nosource); OCC generated tokens per OCC call (median, p90, max; all OCC calls and answered
  only); mini wall time per answer (trace timing.totalMs), median over the screen items and over the OCC-eligible items, candidate vs control.
- Latency clause: median mini wall per answer over all screen items (timing.totalMs) <= 1.5x the control's median on the same items.
- Projected Pixel decode time per OCC call: A = median OCC tokens / 12 and / 16 tok/s; B = median OCC tokens / (12-16 tok/s x r), r = median mini tg
  rate of B / median mini tg rate of A (occPredictedTokens / occPredictedMs per OCC call, both runs of each variant pooled). Report only.
- Stage 2 runs only for a variant that is GO on K0 AND meets the latency clause on K0 (if both variants qualify, A first; B only if A fails).
  MAIN n 97 on K0. Metrics with labels.py (default mode: refused items, R, score 0): U = sum s / sum sref over the 97; CEu rate = CE-unwarned / 97.
  Paired item bootstrap B 2000 seed 11. PASS iff U change >= +0.03 with CI low > 0 AND CEu rate change <= +0.02. Otherwise NO.
- No re-run to rescue a NO. Judge-noise caveat per SCREENS.md; the false-refusal proxy (judge corr on the control answer) never saw the sources.

## Cleanup
NO-GO (or stage-2 NO) -> recipe lines for both GGUFs in rnd/kiln/MODELS.md, delete them from the mini, log in rnd/kiln/DISK-LOG.md.
