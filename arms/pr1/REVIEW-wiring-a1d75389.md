# Review: a1d75389 "ui-android: chat answers through the measured answerService path by default"

Reviewer: independent (read-only), 2026-10-14. Worktree wt/pr1 @ a1d7538922d5 (parent 8882b175).
Checks re-run: `npx tsc --noEmit` exit 0 (clean). `npx vitest run src/ui-android/chat` 2 files / 24 tests pass, of which answerBridge.test.ts has **14/14** (author's number confirmed). Full suite not re-run.
Scope check: `git diff 8882b175 a1d75389 -- src/routing src/rag src/inference` is empty. Locales: only en/pt exist, and both have the 2 new keys. The status labels reuse existing keys.

**Verdict: MERGEABLE AFTER FIXES (S1, S2. S3 can be a tracked follow-up if the PR text states it).** Blockers 0 · should-fix 3 · nits 6.

## Should-fix

### S1. Places questions now get a false "places pack not installed" answer (not in WIRING's 18 differences)
- Where: src/routing/answerService.ts:40 `registerGeoProviders` and answer.ts:459-464. No caller exists anywhere in src (`grep registerGeoProviders|geoProvidersFrom` matches only the definitions). answerBridge.ts:203 assumes places lists arrive.
- What happens: with the switch on (the default), any query that `detectGeoIntent` matches ("vegan restaurants near me", "where to eat in Lisbon") takes `runGeo` → `geo == null` → `finishPlaces("no_pack")`. The bubble then says "The offline places pack is not installed. Install it from Knowledge Base to search restaurants." This happens even when the user has installed a places pack, so the instruction is false. The legacy path retrieved (Wikivoyage) and answered. WIRING #12 ("places cards ... rendered as plain list") implies places work. On Android they never do.
- Fix (smallest): call `registerGeoProviders(geoProvidersFrom({...pois.ts, location.ts}))` once in the Android app shell. If that is out of scope for this PR, add it as difference #19 in WIRING/PR-DESCRIPTION and open a follow-up.

### S2. A generation error after some tokens looks like a finished, successful answer
- Where: answerBridge.ts:205 (`if (!text.trim() && outcome === "error" && error)`), ChatScreen.tsx:686/799/841.
- What happens: answer.ts:1386-1391 finishes `outcome:"error"` with the partial `text` when `engine.generate` throws mid-stream. The bridge keeps the partial text and adds no error marker. ChatScreen then fires the Success haptic (`wasStopped` false), persists the truncated text as the assistant answer and generates the title/summary. Legacy: the throw reached the catch block, which replaced the bubble with "Error: …". Only `console.log` and the stats (`outcome: failure`) record the error.
- Fix: in the bridge, `if (outcome === "error" && error) text = text.trim() ? \`${text}\n\nError: ${error.message}\` : \`Error: ${error.message}\``. Or return `error` and let ChatScreen set a badge plus the Warning haptic when `r.outcome === "error"`.

### S3. Declines are a dead end, and the bridge API cannot fix that without changing
- Where: answerBridge.ts:188 `opts.answer({ query: opts.query }, …)`. RunChatAnswerOptions has no way to pass `answerAnyway`, `tier`, `reuseSources` or `place`.
- What happens: the default is now ON. A compact-model user who asks a no-source or weak-source knowledge question gets "I didn't find this in this phone's library." The text is shown, so the bubble is not empty. The answer.ts guards at 1208, 1439, 1450, 1488, 1506 and 1526 all decline on the compact model. The only way out is to rephrase or to find the Settings switch. WIRING #9 lists this. What is new here: even a follow-up "Answer anyway" button cannot be built on this bridge, because the request is hard-coded. The same applies to "Deeper answer" (deepen) and "Use <city>" (place).
- Fix: change the option to `request?: Partial<AnswerRequest>` (merged into `{ query }`) now, and add the one-button "Answer anyway" when `r.declined`. At minimum, state the gap in the PR text as a maintainer decision for the default.

## Nits
- **N1. Settings copy says the opposite of the code.** en/pt `measuredPathNote` (en.json:259) says "the Adaptive Routing switch picks the model only then". But `getAnswerSettings().quickFirst = answerQuickFirst ?? adaptiveRoutingEnabled ?? true` (settings.ts:521), so the Adaptive switch still turns instant snippets on or off on the measured path (WIRING #3). `adaptiveRoutingNote` ("On by default … picks which downloaded model answers") is now wrong under the default. Fix: one sentence in each note.
- **N2. "Error: …" is now persisted.** ChatScreen.tsx:686→841: on the measured path `assistantText = r.text = "Error: No language model is installed."` is saved to SQLite and then fed into history and the summary. Legacy only showed it in memory. Fix: skip `persistMessage` when `r.outcome === "error" && r.streamedTokens === 0`.
- **N3. Places text is duplicated and its [n] have no sources card (latent until S1 is fixed).** `formatPlacesAnswer` (geo.ts:315) already lists every place as "1. Name — … [n]". The bridge (answerBridge.ts:203) appends "- Name (address)" for each place again. The places `done` and result carry no `cited`, so `citations = []` and the [n] markers point at nothing. Fix: append `placesList` only when the primary text is empty, and use `cited = all` for `receipt.modelId === "places"`. The eval's `answerTextOf` has the same duplication.
- **N4. Stopped during the instant preview.** The raw source sentence is persisted as the assistant answer. It has no sources card (`cited` is [] on a stopped finish) and it goes back to the model as an "assistant" turn next time (answerBridge.ts:202). This is defensible, since it is what the user saw. Possible fix: don't persist when `outcome === "stopped" && streamedTokens === 0`.
- **N5. Stats on the measured path.** `queryStatsFromAnswer` sets `adaptiveRoutingUsed: true` for every answer, including cards, guards and extractive answers, and leaves out `taskType` (answerBridge.ts:247). The Usage screen will report adaptive routing on every turn.
- **N6. Engine, out of scope.** A Stop during streaming can turn into a decline with `outcome:"success"`. The wrong-script and false-claim guards (answer.ts:1439, 1450) run before the `if (stopRequested)` at 1487, so the chat shows the "stopped" badge on "I didn't find this…". Rare. Move the stop check above the guards in a later engine PR.

## Refuted / dropped (re-read the path, claim did not survive)
1. **History includes the current question** (messagesRef is synced in a useEffect, ChatScreen.tsx:234). Dropped. Between `setMessages` and `buildChatHistory` the only awaits are the settings getters, which resolve from the in-memory cache (`cached`, settings.ts:134). That is microtasks only, so React has not committed and `messagesRef` still holds the prior messages. The code is identical to legacy. `historyTurns` is 0 on a first turn, so CUT5-SPEED's skip still applies.
2. **Double stop race** (`llamaEngine.stop()` + `handle.stop()`). Harmless. `stop()` is `stopEpoch++; stopCompletion()`, and doing it twice is idempotent. `handle.stop()` sets `stopRequested` synchronously before its engine stop, so a stop during retrieval or the GPS wait still reaches answer().
3. **Token after decline / status stuck / late events.** Declines are emitted right before `finish`, and no token follows. Events after `done` are dropped (`settled`). `send()`'s finally clears processing and tok/s. The `setStatus` guard keeps the "Stopping…" label.
4. **Sources from the wrong event.** The bridge keeps the last `sources` event, as `buildAnswerEvalRow` does. `cited` is computed by `finish` against the same list on the single-pass path. Cards appear only when `cited` is non-empty.
5. **The final text replaces the stream wrongly.** `setText` runs only when `text !== shown`, which is the case for finalText (CT-1, CT-A, declines, guards). Health answers are buffered (`onToken` suppressed) and emitted as one token. Multipass streams only the synthesis (orchestrator.ts:231). The instant→token swap uses ordered functional updates.
6. **Setting does not reach the first launch / no migration.** `measuredAnswerPath ?? true` survives `parseSettings` (spread). It is read on every send, so a toggle applies at the next message without a restart. Existing users get ON (intended, WIRING #1).
7. **Unhandled rejections.** `handle.done` resolves on every engine path (run() is wrapped). The one exception is `previous.stop()` throwing, which `runChatAnswer` propagates to send()'s catch, giving "Error:" plus a failure record. The non-awaited `stopGeneration` / AppState `.then` without catch predate this commit (same for `llamaEngine.stop()`).
8. **Out-of-scope edits.** None. The legacy branch is verbatim. `buildChatHistory` is byte-equivalent to the removed inline code. `VERBATIM_MESSAGE_COUNT` is still used by the summary block through the import.
9. **Stopped answer saved as complete.** Same as legacy: the partial text is persisted, and the `stopped` flag lives only in memory on both paths.

---

# Re-review of 8b117738 (parent a1d75389, 6 files +156/−24)

Checks: `npx tsc --noEmit` exit 0. `npx vitest run src/ui-android/chat` gives 28/28, of which answerBridge.test.ts has **18/18**. `git diff 8882b175 8b117738 -- src/routing src/rag src/inference` is **empty**. Worktree clean at 8b117738.

| Item | Verdict | Evidence |
|---|---|---|
| S1 places providers | **OK** | App.tsx:14-34 calls `registerGeoProviders(geoProvidersFrom(...))` synchronously at module load. There is no await and no permission call. location.ts only reads the permission status (`permissionBlock`) and never requests it, and offline-location uses `requireOptionalNativeModule`, so importing it on a build without the module is safe. pois.ts opens its SQLite connections lazily. Failure paths are all caught in the engine: `hasPlaces` failure → no_pack (geoWiring.ts:28), `resolvePlace` failure → unknown-place answer, `searchPois` failure → no_data (answer.ts:486, 553). For "near me" without permission, `getLocationFix` returns denied/prompt → `needs_place` text, i.e. the "which city?" answer. A named city goes resolvePlace → searchPois with no GPS, and the device fix is read only if it has already arrived (answer.ts:500-504). |
| N3 places render | **OK** | answerBridge.ts:212 adds the list only when the engine gave no text, so formatPlacesAnswer's list is not duplicated. answerBridge.ts:224 sets `citations = finalSources` when `receipt.modelId === "places"`, and those are the records from the `sources` event emitted before `places` (answer.ts:596), so the [n] markers resolve. Empty places answers carry sources [] and therefore show no card. |
| S2 error marker | **OK** | answerBridge.ts:215-216 appends "Error: <message>" after partial text (or "Error: the answer failed." with no error object). ChatScreen.tsx:696 sets `measuredFailed = outcome === "error"`. At :805 the message is marked `failed`, :808 fires the Warning haptic, :849 skips the persist, :856 skips title and summary, and :571 keeps `failed` messages out of the history. A Stop is not misreported: `llamaEngine.stop()` makes generate resolve (stopEpoch → "" or the partial completion) rather than throw, so answer.ts ends `outcome: "stopped"` (1276/1487). That path never reaches `outcome === "error"`. |
| S3 request plumbing | **OK** | answerBridge.ts:195 `opts.answer({ ...opts.request, query: opts.query }, …)`. The type is `Omit<AnswerRequest, "query">`, so answerAnyway, tier, reuseSources and place pass through unchanged, and the query cannot be overridden. No caller sets it yet, which is stated in the doc comment. |
| N1 / N5 | **OK** | Both locale notes are corrected. `adaptiveRoutingUsed` is no longer set, and `taskType` is parsed from "task:<type>" and checked against the TaskType list. |
| Refuted list (R1–R9) | **No regression** | The history window is unchanged except for the `failed` filter. Stop, the event mapping and the setting default are untouched. The commit changes no engine file. |

New findings (nits only, not blocking):
- **R-N1.** Filtering the failed assistant message keeps its user question in the history, so the next prompt carries two consecutive user turns. `assembleChatMessages` (rag/pure.ts) does not merge roles, and a strict-alternation Jinja template can reject that. Stopped-empty answers already produce this on the shipped path, so it is not a new class of problem. Fix: when filtering a `failed` assistant, also drop the user message before it.
- **R-N2.** The failed answer's user question is persisted but its answer is not, so reopening the session shows an unanswered question. This is arguably fine.
- **R-N3.** The new string "Error: the answer failed." is English-only. The existing "Error:" prefix was already English-only too.

**Final verdict: MERGEABLE AS IS.** S1–S3 and N1/N3/N5 are resolved. The remaining items are nits (R-N1 is the only one worth a follow-up) plus the unaddressed nits N2 (partly superseded: errors are no longer persisted), N4 and N6 from the first pass.
