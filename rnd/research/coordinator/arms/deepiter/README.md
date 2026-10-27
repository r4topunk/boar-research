# DEEPITER — planner-driven second retrieval pass on the deep thinking tier

TL;DR: on the dt512 deep path (Qwen3.6-35B + thinking 512), the deep model first names up to 2 follow-up searches for facts the first pass's sources lack; their on-topic passages join the sources (budget 800) before the unchanged thinking answer. `deepIterFollowups: 0` = dt512 exactly.

| What | Value |
|---|---|
| Worktree / branch | `wt/deepiter`, `coord/deepiter`: 979187fa (= dt512: 0cfd4a77 + repro/deep-dt512.vs-0cfd4a77.patch, git tree e216bc90, content 8ce8b0fc) → fb6d7b3a (DEEPITER) |
| Content hash (repro/tree-hash.mjs) | `040be888cd1001fceccea87a7ec2d0cb4aaad76e390ca9bde0ff928541026489` (git tree 8db44abb) |
| Patches | `deepiter.vs-dt512.patch` (sha a83bead8…), `deepiter.vs-0cfd4a77.patch` (sha ad86e920…, rebuilds 040be888 on 0cfd4a77) |
| Runner | `deepiter-remote-run.sh` = dt512 mini runner + tree path, adapter pin 6298e5d3 (boar-eval 4a22a4e), DEEPITER_PATCH_SHA256 / constants / ARM checks |

```bash
# rebuild + check (same method as repro/verify-trees.sh)
git -C boar-app worktree add --detach /tmp/di 0cfd4a77 && (cd /tmp/di && git apply --index <arms>/deepiter/deepiter.vs-0cfd4a77.patch && node <repro>/tree-hash.mjs .)  # 040be888…
# disable: settings {"deepIterFollowups":0}  (or DEEP_ITER_FOLLOWUPS = 0 in src/routing/answer.ts)
```

## Mechanism (src/routing/answer.ts at fb6d7b3a)
1. Gate (:1004): `gen.modelId === deepModel.id`, tier deep, mode single, `gen.thinking`, not health, `plan.retrieve`. Count = `settings.deepIterFollowups ?? DEEP_ITER_FOLLOWUPS` (:272, default 2). Health, the fast tier, and the no-deep-model fallback (multi-pass / single on the fast model) are untouched.
2. Budget (:1014): source budget `DEEP_ITER_CONTEXT_TOKENS` 800 (:274) when the count > 0; else the plan's 400.
3. After the first retrieval's isSubstantive drop (:1037): the deep model is loaded here if needed (same load call, stage, warnings; its load time and residency are carried to the later load site :1315/:1334). Planner: `deps.engine.generate` with `src/routing/deepIter.ts` system + `deepIterPlannerInput` (question, first-pass on-subject sources as `title — first 160 chars`, the spec's instruction), nPredict 64, temperature 0, `enableThinking: false`, timeoutMs 20 000, no onToken.
4. `parseDeepIterQueries` (:1071): `Q:` lines, trimmed, case-insensitive dedupe, drop the search query / the question / NONE, ≤ count.
5. Each follow-up: `deps.retrieve(q, 6)`; keep isSubstantive and (onSubject(c) or, not crypto-blocked, onTopic(followup, c)); merge after the first pass with `mergeSources([raw, extra])` (dedupe by chunkId), cap 12 (:1090).
6. Compression (:1099): against the question **plus the follow-up queries that added passages** (only then). Deviation from "compression unchanged": against the question alone, compressContext's half-relevance floor drops follow-up passages by construction (unit test: GRIFFIN passage dropped, `context:159->96`). Subject filter (:1110) keeps follow-up passages accepted in step 5. Then unchanged: sources event, instant preview, assembleChatMessages, thinking generation.

Reason codes: `deepiter:planner-none` | `deepiter:followups-N`, `deepiter:added-M` (M = merged − first pass, after the cap; only when N > 0); `deepiter:planner-error`, `deepiter:planner-load-failed`.
Adapter (boar-eval 4a22a4e): the planner is one `other/generation` event (reasoningTokens 0); each follow-up is a `retrieve` event; `timing.retrievalMs2` = sum of every `deps.retrieve` after the first (only follow-ups exist on this path: answer.ts has 2 call sites, :995 and :1076); `timing.retrievalMs` stays the first search. `outputTokens` includes the planner's ≤ 64 tokens; `prefillMs`/`decodeTokPerSec` stay the last (answer) generation's.

## followups = 0 reproduces dt512
- Code path: count 0 → budget term = plan's 400 (:1014); the block at :1037 is skipped (iterResidentBefore undefined, iterLoadMs 0, iterQueries [], iterAccepted empty) → compress query = matchQuery, subject filter = onSubject, loadMs = gateLoadMs, residentBefore = getModelInfo() at the same point as dt512. No deps call is added (no extra `now()`).
- Differential test (scratch script, fake deps, both trees' real createAnswerer): dt512 979187fa vs deepiter followups 0 on 6 scenarios (deep thinking cold / resident, deep no on-topic source, deep PT, deep health, fast tier): events + every generate/load/retrieve call + result + receipt **6/6 byte-identical**; with followups 2 the 4 deep non-health scenarios differ, health and fast stay identical.
- Unit tests `src/routing/deepIter.test.ts` (7): parser, prompt, followups 0 (no planner, 1 retrieval, no codes), planner NONE, follow-ups added (retrieve k 6, codes, merged source in the prompt), health / fast untouched.

Checks: `tsc --noEmit` 0 errors; vitest 1317/1319 (the 2 failures are dt512's own, present before this change: `depth.test` / `answer.test` "deep model … thinking false" expectations vs the DEEPTHINK `thinking: true` patch; dt512 baseline 1310/1312).
