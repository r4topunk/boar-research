# PR note: WARN, the health caution on model-written answers (patch arms/warnspec/tools/warn.patch v2, sha256 11294894…)

## Commit message
routing: show a health caution on health-shaped answers a model wrote (off by default)

A model answer about health can be wrong whether or not it cites a source. This change adds src/routing/warn.ts. A turn gets a caution when a model wrote its text (not a card, excerpt, fixed line, calculator, FACTS, small talk or decline) and it is health-shaped. Health-shaped means one of: the detector fires or scores p ≥ 0.05, HEALTHGAP fired, the health grounding ran, the safety or WARN lexicon matches the question, or a kept source comes from a health pack. The caution has one of three tiers by grounding. no-source: nothing was kept and the model answered from memory. beyond-source: sources were kept, but the answer cites none, its first content sentence is uncited, or under half of its content sentences are cited. sourced: cited and covered, still not clinically reviewed. A new warn event carries the tier before generation (no-source with no source, else beyond-source). The done event's new warn field settles it, and the tier may only move from beyond-source to sourced. The receipt gets warn:<tier>. On such a turn the caution is the one notice: the non-declined weak_sources warning and the uncited preface are not sent. No model-based gate; reason codes only. A stopped answer that shows model text keeps the tier it showed. A turn that ends with no caution (a decline, or the source excerpt that replaced a risky model line) gets back the notice it would have had. A late health source (a deeper answer, multi-pass) gives one notice, the caution. The detector score on a deeper answer and the HEALTHGAP class count as health evidence for the caution only, never for routing or the receipt. Off by default; on with deps.warn = true.

## Files
- src/routing/warn.ts (new): the predicate, the tier, the EN/PT-BR/ES copy
- src/routing/warn.test.ts (new) + src/routing/testing/warn-goldens.json (new, 676 finished turns from eval traces, one per line, with no answer text: the rule's inputs, the reference coverage and the expected tier)
- src/routing/answer.ts: deps.warn, the stream-start warn event, done.warn + warn:<tier>, the weak_sources/preface hold-back on a caution turn
- src/routing/events.ts: WarnTier, the warn event, done.warn
- src/routing/answerReducer.ts: state.warn (set by warn, settled or cleared by done)
- src/routing/answer.test.ts: 12 cases (the three tiers, off, a decline, a deterministic dose line, a stopped answer ×2, a late health source, a risky line swapped for the excerpt, a deeper answer, multi-pass)

## Verification
- tsc clean; vitest src/routing 31 files / 763 green; full suite 121 files / 1,538 green; `git apply --check` clean on the PR branch.
- Goldens: 676/676 rows get the reference tier. Probes 64 with HEALTHGAP on: exactly h21, n12, vit-hlt-003 (vit-hlt-003 is cited and wrong, and stays beyond-source). v0.1: 4. The 180 self-tests: 36 per model. 0 non-health WARNs on v0.1; 4 safety-adjacent ones on the 180.
- Replay with no model and the live detector, 64 + 60 + 180: off = the PR branch on 304/304 traces; on = the same counts and ids. On a caution turn the only differences are the warn event, done.warn, warn:<tier>, the held-back weak_sources and the preface.

## Off switch
deps.warn absent or false (the default): no warn event, no done.warn, no warn:* code; weak_sources and the uncited preface are byte for byte as before. Default-on waits for an out-of-sample check, because the lexicon and the p ≥ 0.05 line were fitted on the sets above. **Android: do not enable yet.** The Android chat bridge does not render the warn event yet: answerBridge drops it, and ChatAnswerOutcome has no warn field. On a caution turn the engine sends no weak_sources and no uncited preface, and on Android the preface is the only notice the user sees. Enabling deps.warn before a renderer exists therefore removes that notice, so the wiring PR must add the renderer first. A native client with a strict event decoder must also know the new `warn` event type or skip unknown types.

## Port lines (native)
1. M (known before generation, confirmed at done) = modelId ∉ NOT_A_MODEL ∪ {small-talk} ∧ no `answer:*` ∧ no `*declined*` ∧ no `instant:final` ∧ no `grounding:health-unsafe-*` ∧ success ∧ non-empty text.
2. H = `detector:fire` ∨ detector p ≥ 0.05 (compared on the receipt's 3-decimal string; Kotlin `%.3f` HALF_UP agrees; a deeper answer scores the detector for this only) ∨ the HEALTHGAP class (with or without the layer) ∨ `healthgap:*` ∨ `grounding:health-*` ∨ isSafetyQuery(q) ∨ WARN_LEX(NFC(q)) with boundaries `(?<![\p{L}\p{N}_])…(?![\p{L}\p{N}_])` (Kotlin: UNICODE_CHARACTER_CLASS) ∨ a kept chunk with packId ∈ {boar-medlineplus-en, qa-health-se, boar-firstaid-en}.
3. Tier: 0 kept → no-source; kept ∧ (0 cited ∨ first content sentence uncited ∨ < 50 % of content sentences cited) → beyond-source; else sourced. No model-based gate.
4. Emit `warn:<tier>` in reasonCodes + done.warn; render the tier copy above the answer from stream start, move only beyond-source → sourced at done (multi-pass may also leave no-source), keep the shown tier on a stopped/timed-out turn with text, and store it with the message (never recomputed); suppress uncitedPreface/weak_sources on that turn, and send the held weak_sources if the turn ends without a caution. Copy language: Spanish first (isSpanishQuestion), then Portuguese, then English.
5. Parity goldens = src/routing/testing/warn-goldens.json (probes 64 with HEALTHGAP on: exactly h21, n12, vit-hlt-003; v0.1: 4 ids; the 180: 36 ids per model); WARN_LEX is normative.
