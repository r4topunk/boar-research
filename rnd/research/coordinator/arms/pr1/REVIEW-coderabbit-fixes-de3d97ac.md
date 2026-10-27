# REVIEW: commit de3d97ac "CodeRabbit fixes" (pr/cut7-engine, parent 8b117738), 2026-10-15

TL;DR: **0 blockers, 2 should-fix, 6 nits. Verdict: PUSHABLE AFTER FIXES** (both fixes are 1–5 lines; neither touches the
English bounty path). The engine race fix is sound: no deadlock, no busy-spin, `inFlight` always clears, and every
native call after an await is preceded by a synchronous context check. Its one regression is a timer leak on the new throw
path. The ES_ONLY change is clean (0 flips on 500 public questions), but the **snakebite precedence swap** sends
ordinary Spanish snakebite questions to the Portuguese card. The swap was not needed, because the ES_ONLY change alone fixes the reported PT question.

Read-only review: no edits to wt/pr1. Blind sets not read. No paid API.

## Checks run
| check | result |
|---|---|
| `npx tsc --noEmit` (wt/pr1 @ de3d97ac) | exit 0 |
| `npx vitest run src/inference src/routing` | 683/683 passed |
| ROUTE_GATE_SYSTEM.length, computed with node from the source text (de3d97ac and wt/cut7 HEAD) | **1673**, sha256 7708281b3f8bb2bf…0cba in both, so the pinned literal is correct |
| old vs new ES_ONLY + card-language decision on bench v0.1 public + boar-eval/bench/selftest/* + rnd/research/packs/selftest/* (500 questions) | 0 Spanish under either regex, 0 flips in isSpanishQuestion, 0 flips in the card language |
| hand-written ES/PT snakebite probes (scratch, not from any blind set) | 4 of 5 Spanish snakebite probes now get the PT card (see S1) |

## Should-fix

**S1 · src/routing/answer.ts:651-653: snakebite card precedence (PT first) gives Spanish questions the Portuguese card.**
`isPortugueseQuestion` is true when one PT_ONLY word appears together with any accented lowercase word, or when any PT_QUESTION word appears. Spanish
shares `que`, `para`, `está`, `como` (unaccented) and uses accents all the time. Verified (`isSnakebiteFirstAid` true for all 4):
- "Me picó una culebra, que hago?" → ES before, **PT now**
- "Una serpiente me mordió en la mano, que hago?" → ES before, **PT now**
- "Una serpiente mordió a mi hijo, qué hago para ayudarlo?" → ES before, **PT now**
- "Me mordió una serpiente y está hinchado, es grave?" → ES before, **PT now** (this one is not an AID match, so it is only relevant at the other sites)
The PT card's emergency line leads with "192 SAMU, 193 Bombeiros no Brasil" for a Spanish speaker. The author's test
uses "qué hago?" with no PT_ONLY word, so it passes.
Refutation attempt: is PT-first needed for the reported PT question? No. Under the new ES_ONLY,
"Uma cobra me picou e está inchando, se piorar é grave? O que faço?" scores 0 ES words, so ES-first is safe for it.
Could a PT question reach 3 of the remaining ES words (mi, una, es, muy, tiene, hacer, …)? That is implausible in Portuguese. **Survives.**
Fix (smallest): restore the old order at this site and keep the new regex:
`const esQ = isSpanishQuestion(q); card = snakebiteFirstAidCard(q, !esQ && isPortugueseQuestion(q), esQ)`. Then change the
answer.test case to "…que hago?" so the test can catch this. Follow-up, out of scope for this commit: the other
card sites (answer.ts:1127/1138/1176/1188) have the same PT-first bias, which predates this commit.

**S2 · src/inference/LlamaEngine.ts:545 vs 586/601/612: the new `assertCurrent` throws leak the generate timeout timer.**
`timer` is armed at line 545. The `try { … } finally { clearTimeout(timer) }` starts at line 612. Before this commit, nothing between them
could throw (loadKv catches its own errors, and restoreStaticSystem is wrapped in `.catch`). Now `assertCurrent` at 586/601 throws
"model unloaded" with the timer still armed. Scenario: the legacy `runAdaptiveChat` → executor.ts path (`timeoutMs` 120 s; still
reachable from ChatScreen.tsx:719) has an answer waiting on prefix I/O. The model is switched or appReset unloads, so generate throws. Within 120 s the
stale timer fires `onTimeout()` (markTimedOut on a finished step) and `this.context?.stopCompletion()`, which **truncates whatever
answer is running then on the new model**. answer.ts passes no `timeoutMs`, so the measured path is unaffected.
Refutation attempt: is it reachable? It needs the legacy path, an unload during the KV I/O window, and a second answer within 120 s. That is narrow,
but the commit introduced it and the result is a silently cut answer. **Survives (low).**
Fix: create the timer right before `context.completion(...)` (line ~606), or wrap lines 584-610 in the same try/finally.

## Nits
- **N1 · LlamaEngine.ts:406-415: the unload loop drains queued generations instead of cancelling them.** A generate() queued on genQueue when
  unload starts still runs on the old context: it does the full prompt prefill (stop only lands between tokens), then stops and resolves with
  ~1 token of text instead of rejecting. This is bounded (one round per queued op), with no deadlock or spin. It is a large improvement on 8b117738, which
  released the context under the op. The author already noted it as a residual. Cheap improvement: an `unloading` flag (or `stopEpoch++`) at loop entry so
  `generate`/`warmNow`/`nextTokenProbsNow` bail before their native call.
- **N2 · context.ts:1450: dropping "se/está/grave" lowers Spanish recall.** Example: "Mi perro fue mordido por una serpiente, se puede morir?" goes from
  ES to EN (2 words left), so the English-only guards (answer.ts:661/700/711/723/1483: co-hazard, arithmetic, travel, FACTS,
  verdict guard) now apply to it. There are no such items in any public set (0/500). Option: count a shared word only when 2 ES-only words are present.
- **N3 · emergencyDetector.ts:27/78: `no-canary` and `load-failed` are terminal for the session.** The app has no detector download path
  (git grep: only sideload/kit), so the only runtime change is an adb push. If the push is partial (gguf + head before the canary) and a question arrives in between,
  the detector stays off until restart. This is acceptable, because it is the stated intent (no re-init next to the 4B). `absent` is still re-checked (verified),
  and `load()` still returns `false` (not undefined), so `deviceEmergencyScore` gives null and the lexical path answers.
- **N4 · emergencyDetector.ts:128-133 (predates this commit): the `load-failed` catch does not release a context that `initLlama` already created** (a throw in the canary
  loop or the canary JSON parse). The terminal status now caps this at one leaked mmBERT context per session instead of one per question. That is an improvement.
  Fix: hoist `context` and `await context?.release().catch(()=>{})` in the catch.
- **N5 · answer.ts:799-803: two load reports when the gate cold-loads fast and the plan then picks deep.** `ensureLoaded` loads a different file, so you can get
  2 `model_streams_from_storage` warnings (the first is about a model the answer does not use) and `backend:cpu-fallback` twice in
  reasonCodes. There is no double emission for the same model: ensureLoaded returns early when the file is resident (verified at 1253). A deep auto
  route after a gate pass is rare on 8 GB devices.
- **N6 · routeGate.test.ts:5/8:** the constant is named `B5_LENGTH` and the test title says "B4" for the B6 prompt. These are naming only, and the value is correct.

## Points verified with no finding
- Engine: there is no deadlock, because no genQueue task awaits `queue` and every `inFlight` op is a native promise. There is no busy-spin, because each loop round awaits `op.catch()`, and a
  settled op that is still in the slot gets cleared by the loop itself. `inFlight` clears on throw everywhere (the `tracked` finally, and the completion/warm finally blocks).
  Every native call after an await has a synchronous check right before it: generateNow 586/601, restoreStaticSystem 703/715,
  saveKv 735, loadKv's pre-check, nextTokenProbsNow (the loadKv result plus the post-save check), and warmNow (existing `this.context === context`).
  When the gate path's saveKv throws "model unloaded", the error is caught, logged and returns null. That is cosmetic: the log reads "session save failed: model unloaded".
- `loadKv` returns null without deleting the file when the context changed. A thrown generate sets `prefixCached` in `settled()`, but loadNow resets it afterwards (line 339).
- context.ts regex diff: exactly 3 alternatives were removed (está, se, grave), and there are no accidental edits (diffed).
