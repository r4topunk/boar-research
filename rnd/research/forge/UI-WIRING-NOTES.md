# Android chat → answerService wiring: notes for the PR phase (parked 2026-10-03)

TL;DR
- The Android chat UI (`src/ui-android/ChatScreen.tsx`) runs the **legacy** `runAdaptiveChat` path: `services/adaptiveChat.ts` → `planRoute` / `executeRoutingPlan`.
  - `routing/answer.ts` (B6 gate, health stack + detector, cards, instant preview) is reached only by `eval/answerEval.ts` (device eval) and the iOS UI (`ui-ios/chat/answerApi.ts`, branch `upstream/ios_android`).
  - Verified on upstream/main `a6633f8d` and `38f996d1`.
- **r4to already knew this.** The loop is: harness/benchmark → device runs via answerEval → improvement PRs to the app **later**.
- Parked; not a current blocker.

## Already done (kept, local only, nothing pushed)
- Branch **`forge/android-ship`** in worktree `wt/forge-android`, on upstream/main `38f996d1`:

  | Commit | Contents | Applied |
  |---|---|---|
  | `18505b35` | `b6-on-health12final` 68f9868d | conflict resolved (below) |
  | `51f4cc01` | Compass `hotfix-usa-franca` 9b5b7614 | clean |
  | `0f8e872a` | `forge-ship` cbca8efc | clean via 3-way |

  - vitest 1223/1223, tsc clean.
- **One real conflict**, `src/routing/context.ts` `riskyHealthInstruction`:
  - main added the app maintainer's clause-aware `exertion-hypothermia` check;
  - the stack adds health5's `hypo-exertion` rule plus the "not only is not a negation" fix.
  - Resolved as a **union**: main's check runs first (its ids; main's tests expect them), then the rule table. Sonar should review before the PR.
- Re-check at PR time: main moves on, and health13 needs stacking.

## Wiring plan (when the PR phase opens; ~1–1.5 working days)
1. **`src/ui-android/chat/answerBridge.ts`**, a pure reducer from `AnswerEvent` (`routing/events.ts`) to the Android message:

   | Event | Effect on the message |
   |---|---|
   | `sources` | citations shown **immediately** (today Android attaches them only at the end, `ChatScreen.tsx:739`) |
   | `instant` | preview text |
   | `token` | streamed text |
   | `done` | the **authoritative** final text from the result: cards, declines and instant answers emit no tokens |
   | `error` / `warning` | existing UI strings |
   | `location` | "which city?" prompt; the reply re-asks with `place` |
   | `deep_available` | the deepen button (phase 2) |

2. A **`runChatAnswer()`** used by ChatScreen:
   - `answer()` from `routing/answerService`;
   - history = summary + verbatim turns, as today;
   - stop → `handle.stop()`;
   - events flushed every ~50 ms, the iOS pattern. Today Android calls `setMessages` once per token, re-rendering the whole list each time.
   - Receipt reason codes go into `recordQueryStats`.
   - `runAdaptiveChat` stays behind a dev-only setting (`legacyChatPipeline`, default off). Deep Research mode is untouched.
3. **Tests:**
   - bridge unit tests, covering every event type and the out-of-order guard;
   - a desktop check: a node script on the boar-eval desktop-node shims runs 20 items through `runChatAnswer` and through answerEval, and asserts identical route/reason codes/sources/answer text at the same seed.
4. **Device acceptance:** an adb script types 10 items into the real chat (uiautomator dump → `input text` → tap send) and reads one `[CHAT]` receipt line per answer from logcat, gated by `DEVICE_EVAL_ON`. ~20 min of device time.
5. **Push:** only to `origin` (r4to's fork), never to `UPSTREAM_REPO/boar-app`. r4to decides the PR.

## Template
- iOS: `upstream/ios_android` `src/ui-ios/ChatScreen.tsx`:
  - `runInto()` at ~l.482;
  - event batching via `pendingEvents` / `flushTimer` at ~l.260–300;
  - `historyTurns()` in `chat/chatItems.ts`;
  - `answerApi.ts`, which is a 3-line re-export of `routing/answerService`.
- The engine contract: `AnswerRequest {query, tier?, reuseSources?, place?, answerAnyway?}` + `AnswerContext {systemPrompt?, styleReminder?, history?, maxTokens}`.
