# WIRING: Android chat → measured answerService path (2026-10-14)

TL;DR: commit **a1d7538922d563370025e13bb8435855f16b993b** on `pr/cut7-engine` (parent 8882b175, not pushed). The Android
chat's ordinary path calls `answer()` (src/routing/answerService.ts) through a pure bridge, behind a new setting
`measuredAnswerPath` (default **on**). Off = the previous code, unchanged. Deep Research untouched. Engine files
byte-identical (`git diff 8882b175 a1d75389 -- src/routing src/rag src/inference` = 0 lines). tsc 0 errors; vitest
118 files, **1,374/1,374** (wiring.tsc.log, wiring.vitest.log). No Android build, no device run.

**Update (review fixes):** commit **8b1177386600290b5c6fad57b6507d4ef16dfddb** (parent a1d75389) applies REVIEW-wiring-a1d75389.md S1–S3 and nits N1,
N2, N3, N5; see "Review fixes" below. tsc 0 errors; vitest 118 files, **1,378/1,378** (wiring2.tsc.log, wiring2.vitest.log);
engine diff vs 8882b175 still 0 lines.

## Diff summary of a1d75389 (7 files, +756 / −16)
| file | change |
|---|---|
| src/ui-android/chat/answerBridge.ts (new, 254) | `runChatAnswer()` maps answer() events → sink (setStatus / setText / appendText / setLiveTokPerSec) and returns text, citations, outcome, receipt, warnings, declined, safety, deepAvailable. `buildChatHistory()` = the legacy history window, moved here. `queryStatsFromAnswer()` = receipt → QueryStats. Pure: answer() injected. |
| src/ui-android/chat/answerBridge.test.ts (new, 374) | 14 tests (event sequences, declined, error, stop ×2, timeout/labels/safety, places, late events, history, stats) |
| src/ui-android/ChatScreen.tsx (+74/−16) | `measuredAnswerPath` on → `runChatAnswer({ answer, query, ctx: { systemPrompt, styleReminder, history, maxTokens } })`; off → old adaptive/fixed branch verbatim. `activeAnswerRef` so Stop / backgrounding / session switch call `handle.stop()` as well as `llamaEngine.stop()`. Measured path: stats from the receipt, **no** chat-side `recordExecution` (answer() writes it). Header model updated when the receipt names another model. History via `buildChatHistory` for every path. |
| src/models/settings.ts (+23) | `measuredAnswerPath?: boolean`, `getMeasuredAnswerPathEnabled()` (default true), `setMeasuredAnswerPathEnabled()` |
| src/ui-android/PersonalitySettings.tsx (+23) | "🎯 Measured answer path" switch, after Adaptive Routing |
| src/i18n/locales/en.json, pt.json (+2 each) | `personalitySettings.measuredPathTitle` / `measuredPathNote` |

## Event → UI mapping
| answer() event | chat UI |
|---|---|
| stage retrieving | status retrieving (multi-pass: "Researching sub-question i/n") |
| stage loading_model | status thinking, label "Mounting local GGUF weights…" |
| stage prefill / verifying | status thinking |
| stage synthesizing | status thinking, label "Synthesizing offline findings…" |
| stage generating, first token | status generating |
| instant | message text = snippet (preview); the first model token clears it and streaming starts |
| token | appended to the message; live tok/s as in the legacy onToken |
| sources | kept; shown under the answer **only if** done.cited is non-empty (contract CT-2) |
| warning (weak_sources, declined, model_streams_from_storage) | collected; logged; **no UI** (none exists on Android) |
| places | the engine's places text (formatPlacesAnswer) as is, its records as sources; a list only when the engine gave no text (8b117738) |
| done | final text = finalText ?? streamed ?? result.text ?? snippet; outcome error → "Error: <message>" (appended after any streamed text, 8b117738), warning haptic, message not persisted and kept out of history; outcome stopped → stopped badge; timeout → timed-out badge |
| deep_available, location | ignored (no UI) |

## Behavioural differences, legacy chat vs measured path (all present when the switch is on)
1. **Default legacy path was adaptive, not fixed.** `adaptiveRoutingEnabled ?? true` means today's default chat runs `runAdaptiveChat` (role-based model pick, executor), with `runFixedModelChat` only as fallback. The measured path replaces both.
2. **Model choice.** Legacy fixed: the model ChatScreen loaded at mount; legacy adaptive: a model per role. answer(): the user's pick filtered by CR-1 (low RAM), CR-2 (crashed loads) and the device default (`selectAnswerModel`); may load another model mid-chat, and the deep tier when `answerAlwaysComplete` is set or the router offers it. The header now follows `receipt.modelId`.
3. **Adaptive Routing switch still matters.** `getAnswerSettings().quickFirst = answerQuickFirst ?? adaptiveRoutingEnabled ?? true`: a user who turned Adaptive Routing off also turns quick-first (instant snippets, instant-final answers) off on the measured path. Measured runs used quickFirst = true.
4. **Retrieval.** Legacy: `classifyTask` → skip for chit-chat → `retrieve(query, ANSWER_CONTEXT_CHUNKS)` → `compressForAnswer`. answer(): its own router, PT→EN search terms, health canonical terms, on-topic filter, keep/quota step, k per tier, today-in-history date search. Neither uses history for the search query.
5. **Prompt assembly.** Same `assembleChatMessages`/`assemblePrompt` and the same `systemPrompt`, `styleReminder` and `history` inputs, but answer() appends to `styleReminder`: the health grounding instruction, the no-source instruction, today's date line, the PT answer-language line; and uses `staticSystem` when there are no sources and no summary. It also sets the KV answer prefix from the system prompt (`setAnswerPrefix`).
6. **History is used beyond the prompt.** answer() also feeds `ctx.history` to the route gate (`routeGateMessages`), the emergency detector window (DETMAX: max of window and turn alone) and the health condition cards (user turns). The legacy path only put it in the prompt. **The measured numbers were all single-turn (no history)**: multi-turn chat is the least-measured part of this path.
7. **Generation limits.** answer(): `nPredict = min(maxTokens, tier maxTokens)` and a thinking budget for reasoning models (FAST 256 / DEEP 1024); legacy: `nPredict = maxTokens`, no thinking cap.
8. **Answers with no model.** answer() can answer with no LLM: instant-final source sentences, chat/calculator/arithmetic/travel/fact cards, current-event fixed answer, health excerpts and first-aid cards, places lists. Legacy always generated.
9. **Declines.** On a weak-source question the compact model declines ("I didn't find this in this phone's library."). The engine expects an "Answer anyway" button (`answerAnyway: true`); the Android chat has none, so the user can only rephrase or switch the setting off. Same for phrase/translation questions with no source.
10. **Citations and sources card.** Legacy showed every retrieved (compressed) chunk under the answer and stripped out-of-range `[n]` in the UI. answer() checks citations (CT-1, may rewrite the text via finalText), strips model reference lists (CT-A) and the chat shows sources only when the final text cites one; uncited answers get a weak_sources warning that has no UI.
11. **Instant preview.** The snippet appears as the message text and is replaced by the first model token (the eval uses the snippet only as fallback text). A user may see the text "jump" once.
12. **No UI for:** weak_sources notice, declined/"Answer anyway", deep_available / "Deeper answer" (`deepen`), the emergency-services line (`done.safety`), location permission / "which city?" (`location`, `needs_place`), places cards with attribution (rendered as the engine's text), `model_streams_from_storage`, load-error kind card. These are product gaps, not crashes. Since 8b117738 `runChatAnswer` accepts `request` (answerAnyway, tier + reuseSources, place), so the buttons are a UI-only follow-up.
13. **Telemetry.** Measured path: usage stats from the receipt (ttft from answer() start, tok/s, load ms, reason codes); the persisted execution record is written by answer() and **only when a model generated** (instant/card/guard answers leave no record; legacy wrote one per turn). Chat-side failure record still written if the bridge throws.
14. **Stop.** Both `handle.stop()` and `llamaEngine.stop()` are called (the engine stop runs twice; harmless in tests, untested on device). answer() also stops a still-running previous answer before starting (double send).
15. **Persisted text** is the final text (after CT-1 / declines), not the raw stream. Titles and summaries use it.
16. **Errors.** answer() never throws; an error ends with `done.outcome = error` and the chat shows "Error: <message>" (e.g. "No language model is installed."). Legacy adaptive fell back to the fixed path on an empty answer; the measured path has no fallback to legacy.
17. **Personality / max tokens.** Chat passes the user's tone and Max Output Tokens; measured runs used succinct + 512 (the app defaults), so a default install matches on the first turn; other tones or 1024/2048 tokens are unmeasured.
18. **Timeouts.** answer() reports `timeout` on its own generation cap; legacy fixed had none (adaptive had the executor's).
19. **Places providers.** The app never called `registerGeoProviders`, so on the measured path (a1d75389) every places question answered "The offline places pack is not installed…" even with a pack installed (the legacy path answered from Wikivoyage retrieval). Fixed in 8b117738: src/ui-android/App.tsx registers `geoProvidersFrom({ installedPoiPacks, getCurrentPoint, getLocationFix, resolvePlace, searchPois, cities })` at module load, as BOAR Bench's runner does but with the app's real location service. That service never prompts and the Android UI has no permission flow, so until location is granted "near me" gets the engine's no-location answer ("which city?" text, no city chooser UI); a named city ("vegan food in Lisbon") works from the installed pack without GPS. The in-app EvaluationScreen shares the registration, so device venue items are no longer no_pack answers there either. Not run on a device.

## Review fixes (8b117738)
| item | now |
|---|---|
| S1 places | providers registered in src/ui-android/App.tsx (difference 19); bridge tests for a places sequence (engine text kept, records as sources) and for an empty-text places answer |
| S2 mid-stream error | bridge appends "\n\nError: <message>" after streamed text; ChatScreen: Warning haptic, `failed` flag, not persisted, filtered out of `buildChatHistory`, no title/summary; test added |
| S3 plumbing | `RunChatAnswerOptions.request?: Omit<AnswerRequest, "query">` passed to answer(); test covers answerAnyway, tier deep + reuseSources, place; no buttons (tracked follow-up) |
| N1 | `measuredPathNote` and `adaptiveRoutingNote` (en/pt) say the Adaptive Routing switch still toggles instant snippets on the measured path |
| N2 | an "Error: …" bubble is not persisted and not fed to history/summary |
| N3 | places text not listed twice; places records shown as sources |
| N5 | usage stats: `taskType` from the engine's `task:<type>` code; `adaptiveRoutingUsed` left unset |

Known, not fixed (documented): N4 (a Stop during the instant preview persists the source sentence as the answer, same as what the user saw); N6 (engine: a Stop during streaming can end as a decline with outcome success, because the wrong-script/false-claim guards run before the stop check in answer.ts; engine PR, out of scope).

## Risks
- Untested on device: React state ordering of setText/appendText under fast streams, Stop latency during prefill, the double `llamaEngine.stop()`.
- Multi-turn behaviour (difference 6) is unmeasured.
- Difference 3 couples an unrelated switch to quick-first (now stated in the settings notes).
- Difference 19: places wiring is untested on a device; "near me" depends on a permission the Android UI never asks for.
- Declines without "Answer anyway" (difference 9) may read as a dead end to a hand tester.

## Manual test list for a device
1. Fresh install, switch on (default): a lookup ("What is the capital of Mongolia?"), a health question ("How do I treat a minor burn?"), a PT question, a greeting ("hi"), a current-event question, a no-source question with the compact model (expect the decline text).
2. Stop during prefill and during streaming; background the app mid-answer; switch session mid-answer.
3. Three-turn follow-up conversation (history + summary after the threshold).
4. Settings → turn the switch off: the old behaviour (adaptive) returns; turn Adaptive Routing off too: fixed path.
5. Usage stats / Execution telemetry screens after a few answers (one record per generated answer, none for cards).
6. With a places area installed: "vegan restaurants in <that city>" (expect the list, not "pack not installed"); "restaurants near me" without location permission (expect the no-location answer).
