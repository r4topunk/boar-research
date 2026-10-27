# CHATFAIL S0: multi-turn intent failures, deterministic replay (2026-10-18, runner; 0 LLM/judge/API/web calls)

Verdict: **PARTIAL.** Mechanisms (1) anchor and (2) code-intent regex are SEEN in the engine. L2 + L3 fix them where they aim, but the prototype fixes 53 % of the misrouted capability turns (< 80 %), because 12 of the 15 left are format/translate asks that L2 does not cover.
Criterion: arms/chatfail/CHATFAIL-S0-criterion.md, sha256 3d4e6ba5d662…1c19 (verified against the sibling .sha256; unedited). Probe set: boar-eval/bench/slices/chat-fu-v1/chats.jsonl sha256 303876ed7c82…408e (labels frozen before the first replay), 30 chats / 159 turns / 49 capability turns (21 code, 18 format, 10 translate). Patch tools/chatfail-l2l3.patch sha256 f7972d37…ca98.

| metric (replay, no model) | before (cut 7) | after L2+L3 |
|---|---|---|
| intent acc, all turns | 74.8 % (119/159) | 85.5 % (136/159) |
| intent acc, capability turns | 34.7 % (17/49) | 69.4 % (34/49) |
| - code asks | 0 % (0/21) | 81.0 % (17/21) |
| - format asks / translate asks | 72 % (13/18) / 40 % (4/10) | unchanged (out of L2 scope) |
| capability turns left on a retrieval + Succinct-cap class | 91.8 % (45/49) | 57.1 % (28/49); code asks 100 % -> 19 % |
| anchor acc, turns >= 3 (fallback plan borrows) | 20.2 % (20/99) | 76.8 % (76/99) |
| anchor acc, turns >= 3 (fallback keeps own turn) | 20.2 % (20/99) | 50.5 % (50/99) |
| anchor acc, turns >= 3 with a "direct" (pointing-back) plan | 18.6 % (8/43) | 88.4 % (38/43) |

Gates (criterion stage 4):
| clause | result |
|---|---|
| current rules misroute >= 50 % of capability turns, or lose the anchor on >= 50 % of turns >= 3 | YES: 65.3 % (32/49) misrouted; anchor lost on 79.8 % (79/99) |
| prototype fixes >= 80 % of them | NO on all capability turns: 53.1 % (17/32); YES on code asks: 81 % (17/21); anchors regained 72.2 % (57/79) |
| 6 control chats: 0 intent changes | YES: 0 of 29 turns changed class. Anchor moved on 8 control turns (7 neutral or better, 1 worse: c28 t4) |
| v0.1 60 public questions as single turns: <= 2 classify changes | YES: 0 changes (60/60 unchanged) |
| existing tests, patched copy | classify.test.ts + followUp.test.ts 57/57 pass (same as base); src/routing 723/724 on both base and patched (the 1 failure, geoWiring PL-1, is in base too, unrelated) |

Smoke: 3 chats first (18 turns), then all 30. Intent-change chats: L2 changed the class on 17 turns, 0 of them from correct to wrong.

## Where the engine sits
- pr1 (cut 7 on upstream/main) has classify.ts but **no follow-up planner**: src/routing/followUp.ts exists only on upstream/fullnative(-dev) (c6bab044, the TS twin of Kotlin FollowUp.kt). Replay: classify() from wt/pr1 (byte-identical to fullnative-dev's), followUpSearch() from upstream/fullnative-dev, both loaded from scratch copies via Vite; wt/pr1 untouched.
- Anchor = the text the planner prepends ("combined = previous + query"); "fallback" plans only borrow when the turn's own search finds nothing, so both bounds are shown.

## String-level diff, TS vs Kotlin (upstream/fullnative-dev 473626fa; not executed)
| rule | TS | Kotlin | diff |
|---|---|---|---|
| code intent | classify.ts:18 `/```\|\b(write (a \|some )?code\|debug this\|refactor\|fix this function\|regex for)\b/i` | Classify.kt:39 same string | identical (PATTERNS order too) |
| anchor | followUp.ts:62-69 previousQuestion: latest earlier user turn != current | FollowUp.kt:80-86 same loop | identical |
| planner constants | POINTS_BACK alternation, OPENERS (all words), SHORT_FOLLOW_UP_TERMS = 3 | same | identical |
So the Kotlin app has both failures as the TS reference does; boar-ios inherits them. UNKNOWN: whether fix/rc-oct17 changed either file (this diff is fullnative-dev only).

## Three most telling misrouted turns (c01 = r4to's live chat; query the engine would retrieve with)
| turn | class before -> after | retrieval text before -> after |
|---|---|---|
| c01 t5 "can you write it?" | lookup (YES_NO) -> code | "i want to see the code can you write it?" -> "What can a smart contract do? can you write it?" |
| c01 t3 "but how it look like? the program" | chat -> code | "what it look like? but how it look like? the program" (subject gone) -> anchored on turn 1 |
| c20 t5 "shorter" (vaccines) | chat -> chat | "translate that to Portuguese shorter" -> "How do vaccines train the immune system? shorter" |

## Limits and what the prototype does badly
- L3 skips short pivots: c28 t4 "which one was the biggest?" after "can you give me an example of a supervolcano?" (2 content words, no capital) anchors on turn 1 (volcano), was right before. L3 needs the real engine's "had sources" signal, which a no-model replay lacks.
- The planner counts a bare "I" as a name (namesItsOwnSubject): "who decides how much I pay?" is "self-contained". My L3 ignores "I"; the planner itself is unchanged.
- 4 of 21 code asks stay misrouted: continuations with no code noun ("just the function, no explanation", "not a library, from scratch?"). 12 format/translate asks ("em português", "say it in German", "put that in a table") need a format/translate rule, not in L2. "explain it like I'm five" routes to research.
- L2 context word list (CODE_CONTEXT) is hand-written; topic-aware routing would be sturdier. Labels are one agent's; anchor labels such as "when should I call an ambulance?" -> turn 1 are arguable (the planner treats >3-word questions as self-contained).
- Not measured here (need generation): mechanisms (3) GROUNDING read as "can't write code" and (4) refusals re-entering history.

Files: boar-eval/bench/slices/chat-fu-v1/{chats.jsonl,NOTICE.md,SHA256SUMS}; arms/chatfail/tools/{chats.src.mjs,setup-scratch.sh,replay.mjs,compare.mjs,chatfail-l2l3.patch(+.sha256)}; tools/out/{before,after}.json, compare.txt. scratch/ is git-ignored (rebuild: tools/setup-scratch.sh).
