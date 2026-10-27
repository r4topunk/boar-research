# REVIEW: WARN engine patch (tools/warn.patch 58da177b…, vs wt/pr1 8ac9eb7a). Independent code review, 2026-10-16

**Verdict: ACCEPT WITH EDITS** for a PR #85 commit. Port fidelity is clean and OFF is byte-identical. Three answer.ts/warn.ts edge paths break the spec's own invariants once `deps.warn` is on: no notice at all, a double notice, or a caution on a deterministic text. The fixes are small. 0 LLM, 0 paid. I did not read blind/ or rnd/veil/, and nothing was written to wt/pr1. Engine probes ran on a scratch copy (wt/pr1 + patch; scratchpad `warnrev/pr1w/src/routing/review-warn.test.ts`). warn.test + answer.test there: 208/208 green.

## Checked and OK
- **Port** warn.ts vs warnspec.py: same predicate, NOT_A_MODEL ∪ small-talk, p ≥ 0.05 on the rounded `detector:p=`, tiers, and coverage (first content sentence cited AND ≥ 50 %, the 8-code-point tail, PREFACE/ENGINE_TAIL order). WARN_LEX matches the same span on 28/28 adversarial strings in Python and TS. Python's Unicode `\w` = `[\p{L}\p{N}_]` and `\d` = `\p{Nd}`, so fullwidth "６ kg" matches in both. The regexes carry no `g` flag, so `.test` keeps no state.
- **OFF path**: hook, hold-back, preface and done spread are all gated on `deps.warn === true` / `warnShown`. The done key order is unchanged, and the reducer returns the same state object when both are undefined.
- **Order**: warn → token → done (R4, R6). The hook sits after the phrase/compact declines, and declines after generation clear `state.warn`. NUMGUARD calculator and HEALTHGAP dose/poison/CO turns get no warn (R5). HEALTHGAP/NUMGUARD codes are pushed before the hook.

## MUST-FIX
1. **Stopped/timeout/error with visible model text loses every notice (R1).** At done the turn is not M, so `settleTier(start, null)` = null and the reducer clears the banner. The weak_sources seal was already swallowed, so the partial answer shows nothing; with OFF it showed weak_sources. In `finish`:
   `const final = warnOf({...}); const warnTier = deps.warn === true ? (final === null && warnShown && outcome !== "success" && text.trim() ? warnShown : settleTier(warnShown, final)) : null;`
   Add an answer.test case (stop at the first token) and update port line 4 ("a stopped or timed-out turn with text keeps the shown tier").
2. **Double notice when H appears only at done (R3).** deepen() → multipass returns a `pack:boar-medlineplus-en` citation. No warn event fires at stream start because H is false then. `finish` emits weak_sources and then done.warn beyond-source, so the reducer holds weakSources + warn. Fix: compute `warnTier` before the uncited block and send only the code there: `reasonCodes.push("grounding:uncited-warning"); if (!warnTier) emit({type:"warning",…weak_sources…});`.
3. **A deterministic text gets warned (R2).** On the model path, `riskyHealthInstruction` replaces the text with the source excerpt ("From the offline source:\nPinch the soft part…") or noSafeStepsAnswer, but the receipt keeps the LLM modelId. So M is true and the banner says "this AI answer may go beyond its offline source" over a verbatim excerpt. This contradicts §4.5 "no deterministic answer by construction". In `isModelGenerated` (and warnspec.py + port line 1), add `&& !has(t.codes, "grounding:health-unsafe-")`. Goldens are unchanged: the only rows with that code (dng-002 ×5) are grounding-guard → null either way.

## SHOULD-FIX
1. **Multipass sticks at no-source (R7, the report's edge, reachable).** "Compare the caffeine in coffee and tea", tier deep, no deep model → multipass. The banner says "no offline source covers this" while the answer cites [2]. Fix: `settleTier(start, final, lateSources = gen.mode === "multipass")`, which may leave no-source when sources arrive mid-turn.
2. **deepen() drops the detector/HEALTHGAP evidence** (`reuseSources` skips both). In R6 the fast answer ends `warn:sourced` (p 0.08), and the deepened answer to the same question gets no caution. Carry H into deepen (an AnswerRequest flag set from the earlier turn) or score the detector for WARN only.
3. **H depends on `deps.healthgap`.** The goldens inject `healthgap:<cls>` into traces run without HEALTHGAP (`hgScan`). Removing those codes, the engine with warn on and HG off warns 11/15 probes, not 15, and drops h10, h15, h21 and h28 (h10 is one of the 6 unsafe 2B answers). Either compute `classifyHealthGap(q)` as an H reason regardless of the layer, or write "deps.warn assumes deps.healthgap" in the deps doc and PR note, and mark "6/6 unsafe without HG" as reference-only.
4. **Android chat**: `answerBridge` drops `warn` (switch with no default), and `ChatAnswerOutcome` has no warn field. ChatScreen only logs warnings, so the uncited preface in the text is Android's only visible notice, and WARN removes it. Turning it on before a renderer exists = a from-memory health answer with no notice. Add `warn: d?.warn` to ChatAnswerOutcome in this PR, plus a "do not enable until rendered" line. Native: `warn` is a new event type; a strict Kotlin sealed decoder must know it or skip unknown types.
5. **Engine tests**: only 2 cases (sourced; no-source + OFF). Port R1–R4/R7 plus "a decline after warn clears state.warn". The 676 goldens test warn.ts, not the answer.ts hook.
6. **Fixture**: 30 rows keep full text the tier never reads (cited 0). They include wrong 2B health answers (h08 "200 ppm … not a standard…", h10 "a 2-year-old can … go without water for a few days", n06), which would land in a public repo; use the placeholder. 325 KB on one line: write one row per line; 266 KB of it is the kept lists of non-WARN rows (trim them). Scope is fine: probes, v0.1, published-pack self-tests; no v0.2/V-para ids; a grep finds 0 private paths (/Users, rnd/, arms/, kiln, blind, veil).

## NITS
- warn.test.ts names a private doc ("WARNSPEC §2", "WARNSPEC §1 v2, reviewed"): use neutral words. The events.ts comment "absent = the model did not write the text after all" needs rewording after MUST-FIX 1.
- warnLang copies the cards' `!pt && es` precedence. "Me picó una culebra, que hago?" is pt and es at once → PT copy (the snakebite card is Spanish-first). This is inherited; fix both together later.
- NFD input ("doença") misses `doen[çc]a` in both Python and TS: run `query.normalize("NFC")` before WARN_LEX. Known PT/ES gaps were confirmed (diarreia, "me duele el pecho", "perdi 6 kg").
- Rounding: p 0.0495 → "0.050" → H. Port line 2 should say to compare on the 3-decimal string (Kotlin `%.3f` HALF_UP agrees).

## Probes (0 LLM; tsx over the tree's warn.ts, model turn with no source unless stated; R = engine via vitest on the scratch copy)
| id | input | expected | got |
|---|---|---|---|
| P1/P17 | ibuprofen with beer / melatonin mg for a 10-year-old | no-source | no-source ✓ |
| P2 | "I lost 6 kg in two weeks without dieting" | no-source | no-source ✓ |
| P3/P4 | "We lost 6 kg in the bike frame redesign" / "airline dropped 20 kg over the allowance" | none | **no-source (FP, red-flag line)** |
| P5 | "lost 6 kg of luggage weight" | none | none ✓ |
| P12–14 | Pain family of Spain / blood moon / Doctor Who | none | **no-source (FP: pain/blood via isSafetyQuery too; doctor)** |
| P15 | "um cão adorável na porta do dormitório" | none | none ✓ |
| P6/P8 | "Estou com diarreia há 3 dias…" / "Me duele el pecho y el brazo izquierdo" | warn | **none (miss; P8 copy lang = en)** |
| P7/P11/P9/P18 | febre / sintomas da dengue / paracetamol embarazada / sangre en la orina | warn | no-source ✓ (pt/pt/es/es) |
| P10 | "Fui picado por uma abelha…" | warn | no-source ✓ (isSafetyQuery only) |
| P16 | NFD "doença de pele" | warn | **none (miss)** |
| T1–T7 | [1][2] after the stop / first uncited / "Dr." split / emergency tail / "No. [1]" + uncited / PT cited / "Yes [1]." | spec tiers | 7/7 ✓ |
| R1 | stop at the first token, from memory, "symptoms" | a notice stays | **ON: none (warn cleared, weak held); OFF: weak_sources** |
| R2 | deep nosebleed, model says "blow your nose" → excerpt | no warn | **beyond-source over the excerpt** |
| R3 | deepen, multipass cites a medlineplus chunk, uncited | one notice | **weak_sources + done.warn** |
| R4/R5/R6 | beyond engine path / NUMGUARD calc + HG dose / deepen of a p 0.08 turn | beyond / none / warned | ✓ / ✓ / **deepen: none** |
| R7 | "Compare the caffeine in coffee and tea", deep → multipass, cites [2] | beyond or sourced | **no-source** |

UNKNOWN: whether the 64 probes (h*, n*, m*, nm*) are already public (WARNSPEC says so; not verified against boar-bench). tsc was not rerun. Timeout was reasoned from code (only multipass sets timedOut), not probed.
