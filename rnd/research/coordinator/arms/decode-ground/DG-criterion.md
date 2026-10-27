# DG-criterion (FROZEN 2026-10-21 21:1x, after the 5-item smoke, before any judged run)

Question: does moving the knowledge pack into the decoder (SELECT under grammar → AMPLIFY → closed-book FALLBACK) lift Qwen3-1.7B + K1 packs above the same-host K1 baseline by more than the measured null?

## Fixed before generation
- Model Qwen3-1.7B Q4_K_M, llama-server b11010, mini, -t 4, seed 42, engine sampler 0.7/40/0.95/0.05, reasoning off, enable_thinking false, default repack, LITEDECLINE_OFF=5, tree be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d) + the DG adapter patch (tools/dg.patch sha c81ba53106c16d49). Baseline B = MINI-BASELINE K1 traces (same host, same tree without the patch).
- Arms: S (grammar SELECT, one-chunk context, closed-book on NO_EVIDENCE), SB (S + logit_bias b = 4.0 (smoke b 2.0 changed 1 of 3 model answers vs S, b 4.0 changed 2 of 3, text clean) on the selected chunk's content tokens), SC (S + CAD α = 1.0 with plausibility cut DG_PLAUS 0.1 (tokens with p_ctx below 0.1 x top p_ctx are excluded from the CAD argmax; the pure −30 imputation produced non-words on 4 of 4 smoke CAD answers)), C1 (CAD α = 1.0 with plausibility cut DG_PLAUS 0.1 (tokens with p_ctx below 0.1 x top p_ctx are excluded from the CAD argmax; the pure −30 imputation produced non-words on 4 of 4 smoke CAD answers) on the baseline kept context, no SELECT). α and b come from the smoke only (no judge was run) and are written here at freeze.
- SELECT menu: raw candidates cap 12 by score, ≤ 3 sentences per chunk (≥ 40 chars), ≤ 30 alternatives, plus NO_EVIDENCE. Deterministic layers (FACTS, calculators, refusals, emergency) untouched: those items must be byte-identical to B (checked, 0 tolerance; a difference = bug, run invalid).
- Items: stage 1 = screen-K1.ids (lp-screens; 21 problems + 20 sentinels); stage 2 = main-97.ids; confirm = CV5 51 (cb17/in/opus.ids). Fact-in-pack subset = RAG-FUNNEL S2–S5 ids (fact-in-pack.ids, 47 ids = K1 vstage S2-S5, sha 3fcee0f2; S1 = 45, unkeyed 5). No blind, no v0.4 text.

## Rules
1. Stage 1 (per arm, order S → SB → SC → C1): GATE v2 K1 params via tools/screen_gate_v2.py: GO iff net ≥ 9, false refusals ≤ 4 of 20, U_cov Δ ≥ −0.071. Judge Haiku 5.5-low judge.v1 N 4 both orders on changed answers only (identical texts reuse B's rows). A child arm (SB, SC) is skipped if S is NO-GO with net ≤ 5 and the child's smoke changed < 3 of 5 answers vs S.
2. Stage 2 (GO arms only): MAIN 97 paired ΔU vs B (item bootstrap B 2000, seed 11), CE-unwarned counts, output tokens and totalMs. PASS-SCREEN iff ΔU ≥ +0.02 with CI low > −0.01.
3. Confirm (PASS-SCREEN arms only): CV5 51 under Opus judge.v1 paired against the K0 and CB Opus rows of CB17 (identical units reuse rows). LEVER iff ΔU vs K0 ≥ +0.03 with CI low > 0; CE claims only from this Opus run.
4. Kill before judging: > 5 % empty or repetition-loop answers; mean totalMs > 4× B (set from the smoke; CAD arms expected ≈ 2×); grammar rejection or token-id mismatch on any item.
5. Reported, no rule: NO_EVIDENCE rate and agreement with the S1 label; selected-in-dropped count; ΔU on the fact-in-pack subset vs S1; time split (select / answer).

## Caps and exposure
Haiku ≤ 700 total, Opus ≤ 110, paid 0, phone 0 min. Dev items only (EXPOSURES row: v0.1/MAIN dev, status unchanged).

## Prediction (written before any result)
S alone: net 6–9 (around the null; the gain, if any, comes from keep-dropped chunks and the fallback). SC: the highest net if reading is the wall (+3…+6 over S). SB: between S and SC. C1: positive on fact-present items, negative on off-topic ones (no gate) → net ≈ S. Aggregate MAIN 97 ΔU for the best arm +0.00…+0.04; the coverage ceiling (S1 45/97) caps it.
