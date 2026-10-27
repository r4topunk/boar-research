# Android chat → answerService wiring on cut 7: report (2026-10-11)

TL;DR: branch `forge/android-ship-cut7` (worktree `wt/forge-android`, local only, nothing pushed). Final commit **ee447c61** (tree **f462f062**), pre-wiring restack **2450636e**. The Android chat now runs `routing/answer.ts` through `answerService`; `runAdaptiveChat` only behind the dev-only `legacyChatPipeline` setting (default off). tsc clean, vitest **1403/1403** (122 files). Identity check chat vs device eval: **20/20 identical on every field**, on GPU and again on CPU.

## A. Restack (pre-wiring hash 2450636e; `forge/android-ship` untouched at 0f8e872a)
- Cut 7 (6d0b93b1) sits on main 0cfd4a77, not on 38f996d1, so `git rebase 6d0b93b1` replayed main's 19 non-merge commits (0cfd4a77..38f996d1: Android setup wizard, iOS UI moved off main, the app maintainer's hypothermia-exertion fix, "Answer anyway" fix, docs) plus the 3 ship commits. Kept that way so the branch stays mergeable on main (call for the PR phase).
- Conflicts and resolutions:
  - `src/routing/context.ts` `riskyHealthInstruction` (3 steps, 6ed58044 / ff481155 / 010d0c38): union, main's clause-aware `exertion-hypothermia` check first (with SEVERE), then cut 7's rule table (hypo-exertion; "not only" is not a negation). Final text = forge/android-ship's resolution. The replayed 6ed58044 commit alone has a regex typo (`\b` lost) that the next two steps overwrite; only the tip is meant to build.
  - `src/routing/answer.test.ts` (3f5e6c9e): kept both tests (INSTANT-FRAG + "Answer anyway").
  - `package.json` / `package-lock.json` (0e68e269, 0a5343ab): main's version; `src/ui-ios/navigation/RootNavigator.tsx` deleted as main does.
  - Ship 1/3 (18505b35, b6-on-health12final): 9 conflicts, all content already in cut 7 (cut 7 is newer: routeGate skip, conditionCards v1, firstAidCards). Took cut 7's side everywhere → empty commit, **dropped**.
  - Ship 3/3 (forge-ship): `answer.ts` import block, union (retrievalStages/perfFlags/zstd + cut 7's SBt card wrappers).
- Engine on the branch ≠ cut 7 byte for byte: `git diff 6d0b93b1 HEAD -- src/routing src/rag src/inference src/eval` = 17 files (+686/−53): main's exertion check (context.ts), answerAnyway turns instant off (answer.ts), Compass emergencyNumbers hotfix, forge-ship retrieval perf (zstd, vector cache, sqlBatch, stage timers). Before restack: tsc clean, vitest 1377/1377.

## B–C. Files (2450636e..ee447c61: 15 files, +1087/−17)
- Added `src/ui-android/chat/answerBridge.ts` (+test): pure reducer for every AnswerEvent type; guard drops other answerIds, freezes after done (except deep_available); `finalizeBridge` = result text/sources authoritative; `showsSafetyNote`.
- Added `chat/runChatAnswer.ts` (+test): answer() + bridge, tokens flushed every 50 ms, other events at once, `handle.stop()`, `chatQueryStats` (receipt reason codes → recordQueryStats). Added `chat/chatContext.ts`: tone, max tokens, summary + 6 verbatim turns (unchanged rule).
- `ChatScreen.tsx`: answerService by default; Stop / background / session switch stop through the handle; renders notice, error, SafetyNote. `settings.ts`: `getLegacyChatPipeline()` (false in release whatever the file says) + setter. Deep Research untouched.
- Caveat: Android had no card component. Added `components/SafetyNote.tsx`, shown when `done.safety` or a card receipt code (`grounding:(fa|health)-card*`, `answer:first-aid-card*`, `answer:safety-fact*`): emergency line (en/pt i18n) + "AI-reviewed, not clinically reviewed" verbatim. The test renders the component and greps for the phrase, plus a source check that ChatScreen renders it for `item.safety`.
- Added `scripts/dev/identity-check.mjs` + `scripts/dev/identity/` (desktop answerService stand-in, 2 inert native stubs).

## D. Identity check
- Command (app repo root): `node scripts/dev/identity-check.mjs --gpu --out <file>` (CPU: drop `--gpu`). Default 20 ids: vit-hum-001/002/003/004/006, lan-rsn-001, lan-cmp-001, lan-ref-001, lan-hlt-001/002, vit-trv-003, vit-cry-001/002/008, vit-hlt-001, food-001, trv-002, trv-004, dng-001, dng-002.
- Setup: boar-eval desktop-node shims (read, not modified); Qwen3-4B-Instruct-2507 Q4_K_M from `shared-models/`, seed 42, engine sampler; route gate on (node-llama-cpp forward, boar-eval `runner/gate.ts`); lexical emergency detector; android, 8 GB; packs boar-crypto, boar-wikivoyage-en, boar-preparedness (v3), wiki-vital5; fresh app dir; no measured speeds or execution records, so neither path can change the other's routing.
- Path A = `runChatAnswer` with `loadChatAnswerContext([], null)` (the chat's own settings read). Path B = `runAnswerEvaluation` from `eval/answerEval.ts`, unchanged. Both import the same `answer()`.
- Result: **20/20** both runs (GPU 2.9 min, CPU 5.9 min). Per field 20/20: tier, outcome, reasonCodes, sourceIds (kept), shownIds (listed), shownTitles, cited, text, rowAnswer (eval row text rebuilt from the chat's events). 26 generations; 6 items end instant (facts, card, places), 14 fast.
- The first run gave 19/20: dng-002 (hypothermia card) differed on sourceIds. That was a wiring bug: the bridge kept the listed sources when the result kept none. Fixed in 8ae53c84 (sources = result's kept; listed → `shownSources`, still shown under cards and declines). No inherent differences left.

## Open items for the PR phase
- Places/location UI (`places`, `location` → "which city?" + `place` re-ask), "Answer anyway" button, deepen button: the bridge carries them, ChatScreen does not show them yet (food-001 answers with the text only).
- No UI toggle for `legacyChatPipeline` (dev builds set it in settings.json). The safety note and notice are not persisted with the message (gone after a session reload).
- Sonar review of the context.ts union; decide whether main's 19 commits stay on the branch (they do now) or the PR targets main with cut 7 as a merge.
- Device acceptance (notes step 4) and push (step 5) are out of scope here. Learned detector and KV prefix reuse are not exercised on the desktop.

## Strict branch (product APK): `forge/android-ui-cut7`, engine byte-identical to cut 7
- Commit **d7b8ba84**, tree **8cf18cc0** = 6d0b93b1 + the wiring commits cherry-picked (be85a510, d0e79ed7, 2f00427d, all clean) + d7b8ba84. None of main's 19 commits and none of the ship stack. `forge/android-ship-cut7` is untouched at ee447c61.
- Local edits instead of shared files (d7b8ba84): the `legacyChatPipeline` getter moves to `src/ui-android/chat/legacyPipeline.ts` (reads settings.json, dev builds only, no setter); the emergency line moves from the locale files to `SafetyNote.tsx` (`emergencyLineFor`, en/pt). `src/models/settings.ts` and `src/i18n/locales/*` are back to 6d0b93b1.
- Proof 1: `git diff --stat 6d0b93b1 HEAD -- . ':(exclude)src/ui-android' ':(exclude)src/components/SafetyNote*' ':(exclude)scripts/dev' ':(exclude)**/*.test.ts' ':(exclude)**/*.test.tsx'` → empty. SafetyNote lives in `src/ui-android/components/`, which the first exclude already covers.
- Proof 2: `git diff --quiet 6d0b93b1 HEAD -- package.json package-lock.json && echo PKG-IDENTICAL` → PKG-IDENTICAL.
- Proof 3: `git diff --stat 6d0b93b1 HEAD` → 14 files (+1122/−17): 4 under `scripts/dev/`, 10 under `src/ui-android/` (ChatScreen.tsx, chat/{answerBridge,chatContext,legacyPipeline,runChatAnswer}.ts + 3 tests, components/SafetyNote.tsx + test).
- tsc clean; vitest 1374/1374 (122 files; 28 of them are the new UI tests).
- Identity check `node scripts/dev/identity-check.mjs --gpu`: **20/20** on every field (exit 0, 2.9 min). The 20 text hashes equal those of `forge/android-ship-cut7`.
- Not in the strict branch: main's 19 commits (setup-wizard model choice, the exertion-hypothermia clause check, "Answer anyway" turning instant off, docs) and the ship stack. That means no Compass emergency-numbers hotfix and none of the forge-ship speedups: no native zstd, no vector cache, no P-8 sqlBatch, no stage timers.
