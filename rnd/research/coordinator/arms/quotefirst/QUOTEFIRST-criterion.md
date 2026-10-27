# QUOTEFIRST criterion (frozen 2026-10-20 before any candidate generation)

## Question
If Qwen3-1.7B first copies the source sentence that answers the question (with its [n]) and then explains in one or two plain sentences, does it read the packs better and make fewer confident errors on pack set K1 (K0 + boar-simplewiki-en v3proto 99bcec30)?
Not a repeat of LITE17 arm Q (two-pass: separate quote call, then the normal answer with the quote appended; 150 pack-matched self-test contexts; NO, +0.002): this is one pass, the output format itself changes, the sources are the engine's K1 retrieval on MAIN (mostly off-pack), and the decision metric includes CE.

## Candidate (arms/quotefirst/quotefirst.patch, sha256 in quotefirst.patch.sha256; -p1 diff to the tree root of be-0cfd4a77-cut7-litepacks, src/routing/answer.ts only)
New exported constant QUOTE_FIRST_INSTRUCTION, appended to the style reminder (the "(Response style: ...)" block after the question in the user message) when: not health, not fromMemory (sources present), English (not pt), compact model (isCompactModel: the 1.7B), single-pass. Text:
"If a numbered source answers the question, start your answer with the sentence from that source that answers it, copied word for word without quotation marks, followed by its number, like [1]. Then add at most two short plain sentences that answer the question directly. If no source answers the question, ignore this and answer as usual."
No other change: system message, answer prefix (KV), retrieval, CT-1 citation check, attribution, compact decline / release rules and the warning line are untouched. "Without quotation marks" is deliberate: unit check (scratch test, 0 LLM) shows that after a closing quote (`"... ." [1]`) citations.ts sentenceBefore stops at the quote and keeps any [n] unchecked, which would silently disable CT-1 and the all-citations-removed / uncited release rules. Engine tests: src/routing (608 tests) pass except PL-1 geoWiring, which fails identically on the unpatched tree (missing asset); tsc reports no error in answer.ts.
Everything else identical (K1, seed 42, same requests, Qwen3-1.7B Q4_K_M, --reasoning off, LITEDECLINE_OFF=5, quickFirst, packHeadPass a2, packDense2 append-budget).

## Stage 1 (screen, K1)
27 K1 problems + 10 sentinels (arms/lp-screens/screen-K1.ids, sha256 c7ea13c3165c6d42c13f9866a77e936b7f11a859845cd3aeee5e1e3e270bd158) versus the mini K1 screen control (lpctl-K1-screen-s42). Gate = the frozen output of tools/screen_gate.py: GO iff fixed >= 6 (ceil(0.22 x 27)) AND sentinels worse <= 1 (worse = correctness drop >= 1.0, new decline/refusal-like, or new CE). NO-GO stops the arm.

## Stage 2 (only on GO; MAIN n 97 = v01 57 + qa-cooking-se 20 + qa-money-se 20)
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via tools/run_arm.sh; only answers whose text differs from the control are re-judged (identical answers reuse control rows); paired bootstrap B 2000 seed 11 as in tools/agg_run.py. U = Q with declined answers scored 0; CE = share of non-declined answers with correctness <= 1.5.
- PRIMARY: candidate on K1 vs the cached mini K0 MAIN control (lpctl-K0-main-s42, the shipped kit). PASS iff U change >= +0.03 with paired CI low > 0 AND CE rate change <= +0.02. Otherwise NO.
- Reported beside it (no effect on the verdict): candidate vs the mini K1 MAIN control (lpctl-K1-main-s42; reused if SHORTCTX already built it, else generated lazily by run_arm.sh), answer length (chars, generated tokens), warned rate (answers starting with the released-decline warning line), share of answers whose first sentence carries a [n].

## Budget
calls_cap: Haiku 1000
(Per piece: screen <= 160 Haiku calls; stage 2 <= 420; the K1 MAIN control, if this arm must judge it, <= 420, accounted separately; one line cap = the sum, enforced per piece by the planned-call accounting in the arm report. 0 Opus, 0 paid API.)

## Sets
Dev only (no blind/, rnd/veil/, boar-eval/bench/v0.4).
