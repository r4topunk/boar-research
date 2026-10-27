# Engine: measured "cut 7" answer pipeline (FACTS cards, emergency detector routing, grounding and health rules)

## Summary

This PR brings the answer engine (`src/routing`, `src/rag`, `src/inference`) to the build we measured as "cut 7" in the
BOAR research loop. It is the cut 7 change set (40 files, about +4.9k lines, almost all new modules and tests) rebased
onto current `main` (8fdb665f). Every maintainer change since 0cfd4a77 is kept. The engine's answers on our desktop
reference run are byte-identical before and after the rebase (see Verification).

Two further commits wire the Android chat screen to this engine by default (see "Chat wiring"), and the last two fix the CodeRabbit findings. Kept together at the app maintainer's request.

## What cut 7 adds

**Instant answers that never reach the model**
- **FACTS r6** (`src/rag/facts.ts`, `facts.v1.json`): a compact offline table of 4,233 Wikidata entities (CC0): cities,
  countries, mountains, buildings and towers, rivers, lakes, dams. The asset is 761 KB, cold load is about 110 ms and a warm
  lookup about 0.1 ms. It fires only when the question names a table entity and its wording matches exactly one property
  template, for example "What is the population of X?" or "What continent is Nairobi in?". On the 8 public v0.1 items it
  targets, the answers moved from the 4B to instant. It fired 0 times on 110 held-out and 58 paraphrase items, and had 0 false
  positives on a 100-question blind set.
- **Calculators** (`arithmetic.ts`, `travelDistance.ts`): rate × quantity → time, ceil-division word problems, and
  city-to-city travel distance from a bundled GeoNames table (`worldCities.v1.json`). English only.
- **Instant snippet guards** (INSTANT-FRAG, INSTANT-SUBJ): an extractive snippet is final only if it is not a list or heading
  fragment and not a figurative match ("gastronomic capital"), and only if the question's entity is its subject.

**Safety and health routing**
- **Learned emergency detector** (`emergencyDetector.ts`, `emergencyHead.ts`): an mmBERT-small encoder on llama.rn plus a
  JS head, with a gated lexical floor. It decides when a message goes to the health path. **DETMAX**: when there is chat
  history, the detector scores both the window and the current turn alone and keeps the maximum, so an emergency typed
  after small talk is not diluted (0/240 probe mismatches, 1 added route on 192 normal chat messages).
- **Per-condition first-aid cards** (`conditionCards.ts`, v1 JSON) and a reviewed English **snakebite card text**
  (`snakebiteCardText.ts`): a question naming exactly one condition gets that condition's card (the must-do line, the
  key don'ts, sources, the emergency line) in place of the generic no-source card.
- **CO hazard** (`coHazard.ts`): planning questions about fuel-burning devices in enclosed spaces get a fixed safety answer
  before any model runs. Sources: CDC, CPSC and NHS.
- **Health grounding rules** (`context.ts`): risky-instruction checks on model health answers (for example exertion advice
  for hypothermia), safe source excerpts, and off-topic source dropping. Your `exertion-hypothermia` rule from main is kept
  and runs after cut 7's narrower `hypo-exertion` rule.

**Answer quality guards (English model answers only)**
- **Verdict guard** (`verdictGuard.ts`, v3): repairs a first-sentence yes/no or comparison verdict that contradicts the
  facts in the same answer. It abstains on ambiguous attribution, ranges and list/count mismatches.
- Citation decimal fix (`citations.ts`), POI pack hooks for nearest-place answers (`rag/pois*.ts`, `poiPack.ts`).

**Speed (`LlamaEngine.ts`, `routeGate.ts`)**
- **Route gate**: the loaded 4B decides SEARCH vs ANSWER from one prefill and next-token probabilities, with no text
  generated. It is skipped when the rules already decide (CUT5-SPEED 3).
- **KV prefix caching**: the gate prompt, the answer prefix and the static no-source system message each have their own
  saved session file, restored instead of re-prefilled. The prompts are token-identical. Session keys are flattened,
  with no path separators (KVFIX).

## Verification

| check | main (8fdb665f) | this branch |
|---|---|---|
| `tsc --noEmit` | 0 errors | 0 errors |
| `vitest run` | 105 files, 1,178/1,178 | 117 files, 1,360/1,360 |
| retrieval replay, 60 public v0.1 items (real `answer()`, LLM stubbed) | — | 60/60 identical to the cut 7 build |
| desktop generation, 60 public v0.1 items, seed 42, llama-server CPU | — | answers 59/60 byte-identical to the cut 7 reference run; tier, kept sources and reason codes 60/60. The one difference (lan-exp-007, one clause) is sampling noise in the reference run: re-run now, the cut 7 tree and this branch give the same prompt and the same answer |

Two of main's tests were adjusted to cut 7's behaviour. No engine code was changed for them:
- `context.test.ts`: two blocks accept either `hypo-exertion` or `exertion-hypothermia`. Cut 7's rule matches first, and the
  answer is replaced by a safe excerpt either way.
- `ptQuery.test.ts`: under cut 7's modifier-only rule, "Os bebês podem tomar sol?" translates to `child` alone, so it falls
  back to its own words (null). The plural `bebês` is now checked as "Os bebês estão com febre".

**On a phone.** Cut 7 ran on a POCO X6 Pro (MT6897, 10.7 GiB, Android 16, airplane mode) through our bench app with the
same engine code. It answered 72/72 with 0 crashes. Fast-tier p50 was 31 s and app PSS stayed at or below 4.2 GB after
load. On 57 public v0.1 items it scored the same as the desktop run: 0.529 vs 0.529, paired Δ −0.000 (−0.026…+0.028).

Research write-ups: [research record](https://github.com/r4topunk/boar-research), [FACTS r6](https://github.com/r4topunk/boar-research/tree/main/arms/facts),
[DETMAX](https://github.com/r4topunk/boar-research/tree/main/arms/detfu), [device run](https://github.com/r4topunk/boar-research/tree/main/arms/device-x6), [this rebase](https://github.com/r4topunk/boar-research/tree/main/arms/pr1).

## Wiring note (background for the chat-wiring commits)

Before the chat-wiring commits, the Android chat screen's fixed-model path did not go through this engine. In `src/ui-android/ChatScreen.tsx`,
`runFixedModelChat` (around lines 620–645 on main) runs its own `classifyTask` → `retrieve` → `compressForAnswer` →
`llamaEngine.generate`. None of the instant answers, cards, detector routing, grounding rules or guards above run on that
path.

Suggested follow-up: replace the body of `runFixedModelChat` with one call to `answer()` from
`src/routing/answerService.ts`, passing `{ query, answerAnyway }`, an event handler, and
`{ systemPrompt, styleReminder, maxTokens, history }`. Then map the events to the existing UI state:
- `stage` → `setProcessing` (`retrieving` or `thinking`)
- `token` → `onToken`
- `instant` → show the instant answer
- `sources` → the citation chunks
- `warning` → a notice
- `done` → the final text and receipt

`src/eval/answerEval.ts` (`askOnce`) already calls `answer()` the same way, with stop handling through `handle.stop()`. It
is the existing mapping to copy. `src/services/adaptiveChat.ts` already marks itself as superseded by `answerService.ts`.

## Chat wiring (separate commit, droppable)

Commit `a1d75389` ("ui-android: chat answers through the measured answerService path by default") on top of `8882b175`
implements the wiring note above. It is one commit and touches no engine file (`src/routing`, `src/rag`, `src/inference`
are byte-identical to `8882b175`), so it can be dropped without touching the engine commits.

**What changes for the user.** In ordinary chat (Deep Research off), questions are answered by `answer()` from
`src/routing/answerService.ts`, the same pipeline the in-app evaluation and BOAR Bench measure. The user gets that
pipeline's instant answers and cards, grounding guards (health excerpts, "not in this phone's library" declines,
current-event answer), citation check, and its model choice (low-RAM and crashed-load rules). Sources show under an
answer only when the final text cites them. Streaming, Stop, the stopped / timed-out / backgrounded badges, copy, rating,
titles and summaries work as before.

**The setting.** `measuredAnswerPath` in `src/models/settings.ts` (`getMeasuredAnswerPathEnabled` /
`setMeasuredAnswerPathEnabled`, default on), with a "Measured answer path" switch in Settings → tone and response style,
under Adaptive Routing (EN + PT strings).

**What stays legacy.** With the switch off, the chat runs exactly the previous code: `runAdaptiveChat` when Adaptive
Routing is on (its default), else the inline `runFixedModelChat`. Deep Research Mode (`runDeepResearch`) is untouched
in both cases. Note: before this commit the default chat path was `runAdaptiveChat` (`adaptiveRoutingEnabled` defaults
to true), not `runFixedModelChat`.

**How it was tested.** `src/ui-android/chat/answerBridge.ts` is pure (answer() is injected). 14 vitest cases drive it with
scripted event streams: fast answer with cited sources, finalText replacing streamed text, declined weak sources,
instant snippet then tokens, instant-final, error, stop before the handle exists, stop while streaming, timeout with
multi-pass labels, safety and deep_available, places, late or foreign events, the history window and the stats mapping.
`npx tsc --noEmit` exits 0. `npx vitest run`: 118 files, 1,374/1,374 (baseline 117 / 1,360 + the new file).

**What could not be tested.** No Android build and no device run were done for this commit, and the ChatScreen wiring
itself has no component test (the screen has none). The known behaviour differences between the two paths are listed in
WIRING.md; the main ones a reviewer should know: weak-source / "answer anyway", "deeper answer", the emergency-services line
and the location prompt have no UI on Android yet (the engine still declines or answers; the chat only shows the text).

**Review fixes (commit `8b117738`, on top of `a1d75389`).** An independent review (0 blockers) asked for three fixes, now applied:
the Android app shell registers the offline places providers (before, every places question answered "places pack not
installed" on the new path); an answer that fails after streaming some text now ends with "Error: …", fires the warning
haptic and is not saved or reused as history; and `runChatAnswer` takes the rest of the answer() request (`answerAnyway`,
`tier` + `reuseSources`, `place`). The settings notes now say that the Adaptive Routing switch still toggles instant
snippets, and usage stats carry the engine's task type. tsc exits 0; vitest 118 files, 1,378/1,378.

**Tracked follow-up: "Answer anyway" / "Deeper answer" / city chooser UI.** The engine's declines, deep_available and
needs_place events have no buttons on Android yet. The bridge already passes the request fields they need, so the
follow-up is UI only. Until then a compact-model decline can only be rephrased, or the setting turned off. "Near me" places
also need a location permission flow, which the Android UI does not have yet; a named city works from the installed pack.

## Known follow-ups (from the independent re-review of 8b117738)
- A failed answer is dropped from history but its question stays, so the next prompt can carry two user turns in a row (strict chat templates may reject it); stopped empty answers already behave this way today. Fix: drop the question together with the failed answer.
- The question of a failed answer stays saved with no answer; "Error: the answer failed." is English-only (add the pt string).
- UI for "Answer anyway" / "Deeper answer" / city chooser (the bridge already passes the options).
