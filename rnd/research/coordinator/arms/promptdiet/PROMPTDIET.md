# PROMPTDIET on cut 3 (engine engineer, 2026-10-05, DEV)

TL;DR: fixed prompt text on the 4B normal answer path cut from 272.9 to 122.7 mean tokens (-150.2, bar -150; thin margin of 0.2), passages identical. No generation, no judge, no L1. Reviewer + L1 are the coordinator's.

| item | value |
|---|---|
| branch / commit | `coord/promptdiet` acbc3cd9 (from `coord/final` c5249560 = cut 3 + VG v3) in `wt/promptdiet` (local only) |
| patch | `promptdiet-on-cut3.vs-0cfd4a77.patch`, sha256 `f5ca5df6b0b15b742b8027a1818fd0ffa704fa03918f471033583f656debdfdb` (cut 3 + promptdiet vs 0cfd4a77) |
| fresh `git archive 0cfd4a77` + patch | applies; tsc clean; vitest 1285/1285 |
| unit tests (worktree) | 1285/1285, tsc clean |
| code | `src/rag/pure.ts`, `src/constants/personalities.ts` (succinct only), `src/routing/context.ts` (NO_SOURCE_INSTRUCTION wording) |
| rule table | `prompt-diff.md` (old → new, every rule; weakest edit flagged: row 3, bullet guidance) |

## L0 numbers (4B tokenizer = Qwen3-4B-Instruct-2507-Q4_K_M.gguf, vocab only, node-llama-cpp)
Method (`tools/l0-fixed-tokens.mts`): for the 100 v0.1 EN cut3-confirm traces that generated (s44 + s45, promptTokens > 0), build `assembleChatMessages` as answer.ts does (default persona, the item's query, same number of passages and titles) with EMPTY passage bodies, so passages are identical and cost 0 in both arms. Fixed = tokens(system message) + tokens(user message) − tokens(question). Items with no kept passage get NO_SOURCE_INSTRUCTION in the reminder, as answer.ts does.

| subset | n | before | after | delta |
|---|---|---|---|---|
| all | 100 | 272.86 | 122.66 | **-150.20** |
| with sources | 72 | 282.53 | 129.53 | -153 |
| no source (fromMemory) | 28 | 248.00 | 105.00 | -143 |

Raw: `l0-before.json`, `l0-after.json`. The old runs' mean real prompt size was 458.9 tokens (`promptTokens` in the traces), so the cut is about a third of the prompt.

## Caveats and UNKNOWN
- Not counted, identical in both arms: chat-template tokens (`<|im_start|>` etc.), passage bodies, history, HEALTH/today/PT lines. Health items are measured without HEALTH_GROUNDING_INSTRUCTION (untouched, so the delta holds).
- The margin is 0.2 tokens, and it needed edits beyond rewording (rows 1-3, 9): "or a brief paragraph", the bullets-for-genuine-lists guidance and "not as a command or task" were dropped, and "[1] or [2]" became "[1]". If the reviewer restores any of them the bar is missed; the stop rule gives one revision.
- NO_SOURCE_INSTRUCTION (routing/context.ts) was reworded for ~3 tokens of the mean; revert it first if the reviewer objects (the L0 bar is then missed).
- UNKNOWN: the effect on answer quality, citation rate and the unsafe/confident-wrong counts (L1). The shorter persona may lengthen answers: the system persona no longer says "concise" or "brief paragraph".
- Style wrapper "(Response style:" → "(Style:" applies to all personas (detailed, summary too).
- Test edits (strings only, no snapshots): `src/rag/pure.test.ts` (several asserts: "cite a source you used by its number" → "Cite sources by number"; "no ability to control real-world devices…" → "can't control devices…"; "Never claim to have done something" → "never claim you did"; "(Response style:" → "(Style:"), `src/routing/citationPlaceholder.test.ts` ("like [1] or [2]" → "like [1]"), `src/routing/prompt.test.ts` (grounding substring; and the "prefix is more than half of the prompt" assertion relaxed to "< 60 % to prefill", because the prefix is now about 100 tokens).
- The KV answer prefix (`answerPromptPrefix`) shrinks with it (about 225 → about 100 tokens), so on the phone the prefilled-in-cache part is smaller; the part prefilled after the cache (sources + question) is unchanged. A first question with a cold cache gains the full cut.

## Revision 1 (2026-10-05) — L0 FAIL on the bar, ends PROMPTDIET per the coordinator's rule 3
The 4 weakened rules (reviewer: concise/brief paragraph, bullets for genuine lists, use-context/cite-used/[1] or [2], small-talk "not as a task") are restored with the reviewer's wording (see `prompt-diff.md`, Revision 1). No rule was traded for tokens.

| subset | n | before | revision 1 | delta |
|---|---|---|---|---|
| all | 100 | 272.86 | 147.14 | **-125.72** (bar -150: FAIL by 24.3) |

- Raw: `l0-rev1.json`. Same method and items as above.
- Savings searched without weakening a rule: none found. The fixed text is now about 85 tokens of instructions + about 28 of headers/titles/wrappers; remaining candidates are the "(alarms, lights)" examples (-5, reverted as unfaithful to the alarm-hallucination fix), the "Context:" label and the "(Style: …)" parentheses (about 2-3 each, which would change source headers/format for little gain) and NO_SOURCE_INSTRUCTION (already reworded).
- Best faithful number: -125.7 tokens (about 46 % of the fixed text, about 27 % of the 459-token prompt). Roughly 3.5-5 s of prefill at 25-35 tok/s on the phone. The coordinator decides whether to run L1 on this text anyway (the frozen criterion says L0 FAIL).
- Patch (cut 3 + promptdiet rev 1): `promptdiet-on-cut3.vs-0cfd4a77.patch`, sha256 `bb287ddea667d99a42cbed426013341158f6aae9c1705690f2ddda0062405cb5`, commit 127fda54 on `coord/promptdiet`; applies to a fresh `git archive 0cfd4a77`; tsc clean; vitest 1285/1285 (worktree and fresh archive).
- Test edits in rev 1: `citationPlaceholder.test.ts` back to "like [1] or [2]"; `pure.test.ts` citation asserts now match "cite those you used".
