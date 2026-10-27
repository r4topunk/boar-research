# B-HONEST criterion (frozen 2026-10-20 before any candidate generation)

## Question
On Qwen3-1.7B with the compact declines released behind the warning line (LITEPACKS system, pack set K0 claim kit), does the D4 honest prompt cut confident errors (CE) without new refusals?
(GRILL-2026-10-20 Q5, Q6, Q13.)

## Candidate (arms/b-honest/b-honest.patch, patch -p1 from the mini tree root be-0cfd4a77-cut7-litepacks; sha256 in b-honest.patch.sha256)
Port of HONESTPROMPT D4 (the honest strings, arms/honestprompt/HONESTPROMPT.md appendix) into the path the 1.7B uses (DEFAULT_PERSONALITY_ID = "succinct", adapter reads PERSONALITIES; chat/completion assembly through src/rag/pure.ts CONTEXT_INSTRUCTION):
- src/constants/personalities.ts, succinct systemPrompt: append "State only facts you are sure of. Never invent names, numbers, dates, places or quotes. If you don't know, say so in one sentence. A shorter correct answer beats a longer one. This rule covers facts only. Always do what the user asks: write code, give examples, make tables, and calculate from numbers given in the question." (byte-equal to the S3 string of HONESTPROMPT, i.e. D4's honest clauses on the Succinct persona; D4's own edit "drop 'examples, ' from the leave-out sentence" has no counterpart in Succinct, which has no leave-out sentence). styleReminder unchanged.
- src/rag/pure.ts CONTEXT_INSTRUCTION second sentence: "If the context doesn't cover it, say so, then answer briefly from general knowledge, without specific figures or names you're unsure of." (HONEST context instruction).
Everything else identical: warning line (COMPACT_DECLINE_RELEASED_WARNING), release logic, retrieval, packs, sampler, seed 42.
Control = the MINI controls of arms/lp-screens/control (lpctl-K0-screen-s42, lpctl-K0-main-s42), never the MacBook LITEPACKS traces.

## Sets (dev only; no blind/, rnd/veil, bench/v0.4)
- Stage 1 = arms/lp-screens/screen-K0.ids (27 problems + 10 sentinels; sha256 b6ff7da735c370932e56e74a65589d9ee5b6d277426dceb01fd2e5d7b3b509e1).
- Stage 2 = arms/lp-screens/main-97.ids (MAIN n 97 = v01 57 + qa-cooking-se 20 + qa-money-se 20; sha256 9664d81fdf182603617d31d75b34eaa8fcb1eeb5f0fa87e68352e1fe09d2a462).

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via tools/run_arm.sh (identical answers reuse the control's judgments; only changed answers are re-judged). 0 Opus, 0 paid.

## Budget
calls_cap: Haiku 420 / Opus 0
(Stage 1 <= 160 Haiku calls (37 items x 2 orders = 74 maximum); stage 2 <= 420 (97 x 2 = 194 maximum for this arm). The one-time mini controls, if still missing, are judged under the same cap and are not charged to the arm.)

## Decision rule (stated before running)
- Stage 1 (screen K0): the frozen gate printed by tools/screen_gate.py: GO iff fixed >= ceil(0.22 x 27) = 6 AND sentinels worse <= 1 (worse = correctness drop >= 1.0, newly declined / refusal-like, or newly CE). NO-GO ends the arm: stage 2 is not run.
- Stage 2 (only on GO; MAIN n 97 vs the cached mini K0 MAIN control; paired item bootstrap B 2000 seed 11, as agg_run.py; computed by arms/b-honest/tools/verdict.py, committed before generation):
  PASS iff (1) CE rate change <= -0.05 with paired CI high < 0 (CE rate = CE count / non-declined answers), AND (2) decline + refusal-like rate change <= +0.03 (refusal_like count / n, which includes declined), AND (3) U change >= -0.01 (point estimate). Otherwise NO.
- Also reported: Q, warned rate, CE split warned / unwarned, CE counts.
- Judge noise caveat (SCREENS.md): a changed answer can flip CE by judge noise (~5 % per CE item); read the fixed list with that in mind. No re-run to rescue a NO.
