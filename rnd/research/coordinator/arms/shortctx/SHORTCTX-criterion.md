# SHORTCTX criterion (frozen 2026-10-20 before any candidate generation)

## Question
Does a short, focused context (at most 2 retrieved chunks, about 350 context tokens) let Qwen3-1.7B use the Simple Wikipedia pack (pack set K1 = K0 + boar-simplewiki-en v3proto 99bcec30)? LITEPACKS found K1 raised mean prompt tokens 384 -> 729 and changed 61/97 answers with no gain.

## Candidate (arms/shortctx/shortctx.patch, sha256 in shortctx.patch.sha256; -p1 diff to the tree root of be-0cfd4a77-cut7-litepacks, src/routing/answer.ts only)
After the whole source assembly (compression, grounding, X2b append-budget) and before the sources event: unless the question is health or the mode is multi-pass, keep the first 2 sources in their current order, with a total of about 350 tokens (approxTokens = chars/4, 1400 chars incl. titles); a chunk body over its allowance is cut at the last sentence end in the second half of the allowance (else hard cut); a second chunk with less than 240 chars of body room is dropped. No env override exists for k or the context budget (planAnswer sets retrieveK/contextTokens), hence the patch. Reason code shortctx:<n>-><m> marks changed items. Everything else identical (K1, seed 42, same requests, Qwen3-1.7B Q4_K_M, --reasoning off, LITEDECLINE_OFF=5, quickFirst, packHeadPass a2, packDense2 append-budget).

## Stage 1 (screen, K1)
27 K1 problems + 10 sentinels (arms/lp-screens/screen-K1.ids, sha256 c7ea13c3165c6d42c13f9866a77e936b7f11a859845cd3aeee5e1e3e270bd158) versus the mini K1 screen control (lpctl-K1-screen-s42). Gate = the frozen output of tools/screen_gate.py: GO iff fixed >= 6 (ceil(0.22 x 27)) AND sentinels worse <= 1 (worse = correctness drop >= 1.0, new decline/refusal-like, or new CE). NO-GO stops the arm.

## Stage 2 (only on GO; MAIN n 97 = v01 57 + qa-cooking-se 20 + qa-money-se 20)
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via tools/run_arm.sh; only answers whose text differs from the control are re-judged (identical answers reuse control rows); paired bootstrap B 2000 seed 11 as in tools/agg_run.py. U = Q with declined answers scored 0; CE = share of non-declined answers with correctness <= 1.5.
- PRIMARY: candidate on K1 vs the cached mini K0 MAIN control (lpctl-K0-main-s42, the shipped kit). PASS iff U change >= +0.03 with paired CI low > 0 AND CE rate change <= +0.02 (the LITEPACKS rule). Otherwise NO.
- Reported beside it (no effect on the verdict): candidate vs the mini K1 MAIN control (generated lazily by run_arm.sh), prompt tokens (mean, p50), retrieval ms and TTFT ms p50 from the traces.

## Budget
calls_cap: Haiku 840
(Per piece: screen <= 160 Haiku calls; stage 2 <= 420; the K1 MAIN control, if it must be judged, <= 420, accounted separately; one line cap = the sum, enforced per piece by the planned-call accounting in the arm report. 0 Opus, 0 paid API.)

## Sets
Dev only (no blind/, rnd/veil/, boar-eval/bench/v0.4).
