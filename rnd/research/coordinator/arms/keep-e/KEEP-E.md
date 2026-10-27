# KEEP-E (2026-10-21): empty-lexical dense append, one Haiku screen on the changed MAIN rows. Verdict: **KILL** (net U -0.010)

Criterion frozen before any replay/generation/judge: `KEEP-E-criterion.md` (sha256 4421544c..., rnd commit 3b30b8da).
Cost: **55 Haiku 5.5-low calls** (28 judge.v1-low + 27 DECLINE2STAGE stage 1; cap 60), 0 Opus, 0 paid, 28 generations on the Mac mini, 0 phone. Dev sets only.

## TL;DR
- Replay (0 LLM, stub server, MacBook): KEEP_E=1 changes **exactly the 14 MAIN rows** K1 listed (12 cooking/money self-tests + vit-hum-003, vit-sci-001); every one goes from 0 kept chunks to 1-2 dense chunks. Prompt tokens **+8.2 %** over the 75 prompted MAIN rows (781 -> 845), **+118 %** on the 14 changed rows.
- Judge (Haiku N=4 both orders + stage 1): **net U -0.010** on MAIN 97 (sum delta -4.50 / sum s_ref 451.17); 3 rows better, 9 worse, 2 equal.
- CE-unwarned new: **0**. New refusals: **0** (stage 1 said "attempted" on all 27 texts). But the corr <= 1.5 answers go 0 -> 3 (money-005, money-013, cooking-014), all carrying the CMP30OFF warning line, so they are CE-warned, not CE-unwarned.
- The 2 S3 fact items do not move: vit-hum-003 corr 2.0 -> 2.0, vit-sci-001 2.5 -> 3.0 (+0.17 s). The fact chunk reaches the prompt, but the 1.7B does not read it (both answers still start with the "Not found ... from memory" warning).
- Warned answers rise 6 -> 12 of 14: the appended dense chunks are apparently off-topic enough that the model does not use them, so the warning line stays or appears. Only 2/14 E answers cite a source (money-016, money-019).
- **Verdict: KILL** (frozen rule: net U >= +0.010 fails; CE and refusal clauses pass).

## Per-row table (E on the mini vs LITEPACKS K1 baseline; s = mean of 3 dims over both orders, D2S zeroing applied; tokens = replay prompt)
| id | corr base -> E | s base -> E | delta | warned base -> E | E cites | CE-unw new | tok base -> E |
|---|---|---|---|---|---|---|---|
| st-qa-cooking-se-004 | 3.0 -> 2.5 | 2.50 -> 1.83 | -0.67 | 1 -> 1 | 0 | 0 | 318 -> 560 |
| st-qa-cooking-se-006 | 2.5 -> 2.0 | 1.83 -> 1.33 | -0.50 | 1 -> 1 | 0 | 0 | 311 -> 777 |
| st-qa-cooking-se-007 | 2.0 -> 3.0 | 1.33 -> 2.17 | +0.83 | 0 -> 1 | 0 | 0 | 260 -> 545 |
| st-qa-cooking-se-014 | 3.0 -> 1.5 | 2.00 -> 1.17 | -0.83 | 0 -> 1 | 0 | 0 | 257 -> 570 |
| st-qa-money-se-003 | 2.5 -> 2.5 | 1.50 -> 1.83 | +0.33 | 1 -> 1 | 0 | 0 | 318 -> 454 |
| st-qa-money-se-005 | 3.0 -> 1.0 | 2.33 -> 1.00 | -1.33 | 0 -> 1 | 0 | 0 | 278 -> 726 |
| st-qa-money-se-012 (S3) | 2.0 -> 2.0 | 1.50 -> 1.33 | -0.17 | 0 -> 1 | 0 | 0 | 261 -> 744 |
| st-qa-money-se-013 | 3.5 -> 1.0 | 2.50 -> 1.00 | -1.50 | 0 -> 1 | 0 | 0 | 267 -> 748 |
| st-qa-money-se-015 | 2.0 -> 2.0 | 2.00 -> 1.83 | -0.17 | 1 -> 1 | 0 | 0 | 328 -> 569 |
| st-qa-money-se-016 | 2.5 -> 2.5 | 1.50 -> 1.50 | 0.00 | 1 -> 0 | 1 | 0 | 324 -> 568 |
| st-qa-money-se-018 | 3.0 -> 2.0 | 2.00 -> 1.50 | -0.50 | 0 -> 1 | 0 | 0 | 266 -> 644 |
| st-qa-money-se-019 | 3.5 -> 3.0 | 2.50 -> 2.33 | -0.17 | 0 -> 0 | 1 | 0 | 260 -> 753 |
| vit-hum-003 (S3) | 2.0 -> 2.0 | 1.33 -> 1.33 | 0.00 | 1 -> 1 | 0 | 0 | 327 -> 541 |
| vit-sci-001 (S3) | 2.5 -> 3.0 | 1.50 -> 1.67 | +0.17 | 1 -> 1 | 0 | 0 | 307 -> 700 |
| **sum** | | | **-4.50** | 6 -> 12 | 2 | **0** | +118 % |
Stage 1 (DECLINE2STAGE): "attempted" on all 14 E and all 14 baseline texts (13 new calls + vit-sci-001 baseline label reused by text sha); no refusal-neutral rows.
st-qa-money-se-012 is a K1 S3 item that E's replay did not mark as fact-reached (fact at dense rank 3); it changed anyway.

## Deviations
- **Host parity fails.** The base-control run (KEEP_E unset, same 14 rows, same mini) gives texts different from the MacBook LITEPACKS baseline on 14/14 rows (similarity 0.06-0.95). The mini llama-server build (build-cpu) and the MacBook one (llama-b11010-cpu) do not reproduce each other at seed 42. So each delta mixes the E effect with host noise of about the same size. The frozen pairing (E vs the LITEPACKS baseline, as in ROUTING-R1) was kept. Judging the control as well would need 28 more calls, over the cap. The direction is still clear enough for a screen: 9 of 14 rows are worse, and the 3 new corr <= 1.5 answers are all E rows with off-topic appended chunks.
- No shard_judge --preflight: the frozen criterion states the cap in its Judge block, but the preflight wants a "## Budget" calls_cap line. Same as routing-r1/tools/judge.sh. Cap enforced by hand (55/60) and by the stage-1 ledger (cap 32).
- The request rows' runId was unified to ke-MAIN14-s42 (the adapter refuses mixed runIds). Configs are identical apart from ramGb 12 vs 12.0.

## Reading
- With an empty lexical list, the dense candidates are the pack's nearest vectors to a question the pack does not cover. They add 250-480 tokens of near-miss text, and the 1.7B then answers worse (money-005 invents an IRS-refund path, money-013 flips to "charged on top"). This fits the CTX/dilution history: on the 1.7B, extra loosely related context costs more than it adds.
- The 2 S3 items E was meant to recover stay unread. Reaching the fact is not enough at this model size (ORACLE-REAL +0.015 with the fact at slot 1).
- So the empty-raw skip in the engine is a useful guard, not a bug. Keep it. The K1 gap closes here; no Opus confirmation is queued.

## Files
- tools/apply_keepe.py (env-gated patch, KEEP_E=1), tools/keep-e.answer.diff (answer.ts 0d1ac07d -> 9a52b8a1), tools/replay.sh, tools/compare.py, tools/gen_mini.sh, tools/judge.sh, tools/analyze.py, tools/baseline.py, tools/stub_server.py (copy of the K1 stub).
- Tree: kiln-local/be-0cfd4a77-cut7-litepacks-keepe (MacBook) and <runner>/kiln/be-0cfd4a77-cut7-litepacks-keepe (mini), both answer.ts 9a52b8a1.
- req/ke-MAIN14-s42.requests.jsonl (LITEPACKS K1 request rows), traces/ke-{E,base}-MAIN14-s42.traces.jsonl (mini), judgments/ke-E-*.judgments.jsonl, judgments/stage1/.
- aggregates/replay.json (changed rows, tokens), aggregates/baseline.json (LITEPACKS K1 texts + judgments, from arms/litepacks/traces/lp-K1-{cm,v01}-s42 and judgments/lp-K{0,1}-*), aggregates/keep-e.json (per-row metrics, verdict).
