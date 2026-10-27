# CHATROUTE: CHATFAIL L2+L3 shipped without L1 (2026-10-19, 0 LLM/API/web calls)

TL;DR: the L2 (code intent in a chat) and L3 (follow-up anchor) routing from CHATFAIL S0/S1 is now one engine commit. It has no L1 prompt line and nothing from L4. The replay reproduces S0 exactly: intent accuracy 74.8 % -> 85.5 % and code asks 0/21 -> 17/21. Guards: 0 route changes on 144 single-turn items (v0.1 60, safepack 30, packread-v1 54) and 0 class changes on the 30 first-aid chat turns. The commit also adds a health-conversation exclusion that S1 did not have, so first-aid chats keep exactly pr1's route and search. vitest is 122 files / 1521 tests green with and without HEALTHGAP=1, and tsc is clean. Decision: project owner, 2026-10-19 (the audit traced the first-aid harm to the L1 prompt line).

- Commit `303e4561` on the stack 8ac9eb7a + longdigit, cocar, facts-r7, facts-r8, saferoute (worktree `<scratch>/wt-chatroute`, kept; wt/pr1 untouched; nothing pushed).
- Patch: `arms/chatfail/chatroute.patch`, sha256 `9adcb4f33f50244415b4b30f4d5456d14d749506b749137dacd0a90645246df4`.
- Apply: `git am` after `saferoute.patch`.

## What was ported (and how S1 applied it)
In S0/S1, L2+L3 was `tools/chatfail-l2l3.patch` (f7972d37) on scratch trees, but the engine never called it. `contexts.ts` called `classifyTaskInContext` outside answer.ts. It wrapped `deps.retrieve` with fullnative-dev's `searchWithFollowUp`, and it skipped answer.ts for code turns, so the route gate never saw them. pr1 has no follow-up planner (`followUp.ts` exists only on upstream/fullnative-dev). The engine port therefore:

| piece | change |
|---|---|
| `classify.ts` | `CODE_CONTEXT`, `CODE_EXPLICIT`, `CODE_NEEDS_CONTEXT`, `classifyTaskInContext`: byte-identical to the S0 patch (only comment wording changed) |
| `followUp.ts` (+ test) | fullnative-dev's planner (c6bab044 / 750fdcf4 / 11d19d68), with L3 `previousQuestion` + `selfContained` byte-identical to the S0 patch |
| `answer.ts` rule type | `ruleTaskType = classifyTaskInContext(query, userTurns)` |
| `answer.ts` route gate | skipped when the in-context rule turned a turn into code (`route-gate:skip-code-request`). S1 never gated code turns. A SEARCH verdict would map code -> chat and undo L2 |
| `answer.ts` retrieval | `deps.retrieve(searchQuery, k)` goes through `searchWithFollowUp(searchQuery, history, ...)`, the same wrapper and arguments S1 used. Reason codes: `retrieve:follow-up-direct` / `retrieve:follow-up-fallback` |
| **new vs S1: health exclusion** | Neither L2 nor the planner runs in a health conversation. The conversation counts as health when the detector fires, when this turn or any earlier user turn matches `isHealthQuestion`, `isSafetyQuery` or `isCardEmergency`, or when `isHealthFollowUp` matches. Those turns keep pr1's rule type and pr1's search (`isHealthFollowUp` / `conversationCondition` path). S1 ran the planner on first-aid chats in both C0 and A2, so it never measured that against pr1 (which has no planner) |
| not ported | L1 (GROUNDING / styleReminder strings), L4 (history refusal filter), format/translate rules |

## (a) Probe set replay, chat-fu-v1 (30 chats, 159 turns, 49 capability asks)
"Before" is pr1 + this stack + fullnative-dev's unpatched planner, the same baseline as S0. "Classifier" is `tools/replay.mjs` on the new tree. "Engine rule" is `tools/chatroute/engine-replay.mjs`, which adds the health exclusion. The exclusion uses the lexical part only: the learned detector is not replayed, and it can only add exclusions.

| metric | before | classifier (= S0 after) | engine rule |
|---|---|---|---|
| intent acc, all turns | 74.8 % (119/159) | **85.5 % (136/159)** | 85.5 % (136/159) |
| intent acc, capability turns | 34.7 % (17/49) | 69.4 % (34/49) | 69.4 % (34/49) |
| code asks routed to code | 0 % (0/21) | **81.0 % (17/21)** | 81.0 % (17/21) |
| format / translate asks | 13/18, 4/10 | unchanged | unchanged |
| capability asks left on a retrieval + 2-3 sentence class | 45/49 | 28/49 | 28/49 |
| anchor acc, turns >= 3 (fallback borrows) | 20.2 % (20/99) | 76.8 % (76/99) | 64.6 % (64/99) |
| anchor acc, direct-plan turns >= 3 | 8/43 | 38/43 | 32/43 |
| control chats (29 turns): class changes | - | 0 | 0 |
| class changes ok -> wrong | - | 0 | 0 |

`compare.txt` is identical to S0's `tools/out/compare.txt`. The engine-rule anchor drop (76.8 -> 64.6) comes entirely from the 19 first-aid follow-up turns (c13-c17, c27) that now keep their own search, which is the intended exclusion. All 17 changed classes are crypto/science code asks (c01 t2-t6, c02 t4-t5, c03 t5-t6, c04 t4-t5, c06 t3-t4, c21 t3-t4, c24 t3-t4).

## (b) Guards (single turn; route = rule task type, gate, planner)
| set | n | danger / lexical health | class changed (raw `classifyTaskInContext`, no health guard) | engine route changed |
|---|---|---|---|---|
| v0.1 questions.public | 60 | 5 / 5 | 0 | 0 |
| safepack (emergency self-test) | 30 | 25 / 20 | 0 | 0 |
| packread-v1 | 54 | 0 / 8 | 0 | 0 |
| chat-fu-v1 first-aid turns (6 chats) | 30 | - | 0 | 0 (planner off on all 19 follow-ups) |

**Changed guard items: none.** No health, danger or first-aid item changes route. The hard-fail clause passes. The planner needs an earlier turn, so on single-turn items the search text is unchanged by construction. Raw output: `tools/chatroute/out/guards.json` and `firstaid-turns.txt`.

## (c) Tests
- `vitest run`: 122 files, **1521/1521** (base stack 1513, plus 8 new). `HEALTHGAP=1`: 1521/1521. `tsc --noEmit -p .`: clean.
- New tests:
  - classify.test.ts (3): code follow-ups; explicit code nouns; supervolcano, road, "write it down", table and translate left alone.
  - followUp.test.ts (1): L3 anchor.
  - answer.test.ts (4): "can you write it?" gives `task:code` with no search and no gate call; the code forms; the anchored follow-up search; and 5 first-aid follow-ups (choking baby, compare table, burn cooling, nosebleed head-tilt, "write it as a program" in a CPR chat) that keep `task:` = `classifyTask`, with no `retrieve:follow-up` and no search on the first question.
- The last test fails if the health exclusion is removed (mutation checked).

## Expected effect and limits
- S1 M4 measured A2 - C0 = +0.122 (CI 0.000..+0.256) on fulfilled capability turns. That figure includes L1, which alone gave +0.041. The audit puts the real L1+L2+L3 gain near +0.10. This commit therefore carries roughly the routing share, about +0.06..+0.08 on M4, but **routing without L1 was not generated or measured**. M1 (1.5B) showed no gain in S1 and still refused at c21-t3.
- UNKNOWN:
  - Generation numbers for L2+L3 alone. The next run would be a cheap S1 arm "A2 minus L1" on M4 (49 turns, 0 judge).
  - How the real route gate would have treated these turns. The commit skips the gate for the in-context code rule only; explicit single-turn code asks still go through the gate as before.
  - The anchor change on non-health chats against pr1 itself. pr1 had no planner, so every non-health follow-up now searches with an anchor. S1 measured that only against the unpatched planner.
- Remaining misroutes: 4/21 code asks ("just the function, no explanation", "not a library, from scratch?") and all 12 format/translate asks (out of scope).

Files: `arms/chatfail/{chatroute.patch, CHATROUTE.md}` and `arms/chatfail/tools/chatroute/{engine-replay.mjs, guards.mjs, fa.mjs, out/*}`.
