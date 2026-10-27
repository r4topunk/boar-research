# WARNSPEC-PATCH: the unsafe-answer warning as an engine option (`deps.warn`, default off). 2026-10-16. Status: **v2 PASS** (REVIEW-warn-patch applied; counts = spec, OFF identical)

> v2 (§ at the end) supersedes the patch sha below: **tools/warn.patch v2 = 11294894c72096da9d0869b292bc1d45ce8e51f5a3a8ed6c763f2c5ba48d35d2**. The v1 sections are kept as history.

TL;DR: `tools/warn.patch` sha256 **58da177b216b750ba9eb3ea9203de0727531ebb3be364cfa6356a13cd3066940** (685 lines, diff vs wt/pr1 HEAD 8ac9eb7a = NUMGUARD r3 + HEALTHGAP r2; 7 files in src/routing, +544 −3). It ports tools/warnspec.py (v2, f2d1849a…) 1:1 to `src/routing/warn.ts`. The 676 trace goldens give the reference tier on every row. The engine replay with the live detector gives the spec counts exactly, and OFF is identical to wt/pr1 on 304/304. Calls: 0 judge, 0 paid, 0 generation. Exposure: public probes, v0.1 and published self-tests only; blind/ and rnd/veil/ were not read, so there is no EXPOSURES row.

## What the patch does
- **warn.ts** (pure): M (`isModelGenerated`), H (`healthReasons`: detector fire, p ≥ 0.05 read from the receipt's rounded `detector:p=`, `healthgap:*`, `grounding:health-*`, isSafetyQuery, WARN_LEX, a kept chunk whose packId ∈ {boar-medlineplus-en, qa-health-se, boar-firstaid-en} or whose source matches the health-pack hosts), the tier (0 kept → no-source; 0 cited, first content sentence uncited or < 50 % cited → beyond-source; otherwise sourced), and the nine reviewed copy strings. WARN_LEX uses `[\p{L}\p{N}_]` boundaries and `\p{Nd}`; the "8 characters after the sentence" tail is counted in code points, as in Python.
- **answer.ts hook**: before generation, if `deps.warn` is on and the turn is H, a new `warn` event carries the stream-start tier (no-source with 0 kept, else beyond-source). On that turn the caution is the one notice: the non-declined `weak_sources` event is held back (it counts as sent, so the reason codes match OFF) and `uncitedPreface` is not added. At `done`, `warnOf` runs over the final codes, kept, cited and text, and `settleTier` lets the tier move only beyond → sourced. A turn that is not M at done (declined, error, stopped) gets no caution. The receipt gets `warn:<tier>`, and done gets the new field `warn: {tier, message}`.
- **events.ts**: the `WarnTier` type, the `warn` event and `done.warn`. **answerReducer.ts**: `state.warn`, set by the `warn` event and settled or cleared by done.
- **Adapter (eval side, not in the patch)**: `patch/warn-adapter.diff` adds `HEALTHGAP=1` / `WARN=1` env switches to the tree's be/adapter.ts. The engine reads only deps.

## Counts vs spec (aggregates/warnspec.json)
| check | set | got | spec |
|---|---|---|---|
| goldens (warn.test.ts, TS port over the trace rows) | 676 rows / 7 groups | 676/676 same tier | — |
| | probes 64 · 4B cut 7 + HG r2 | 3 = h21 beyond, n12 no-source, vit-hlt-003 beyond | 3 (1/2/0) |
| | probes 64 · 2B+HG / 4B cut 7 / 2B cut 7 | 3 / 15 / 15; the 6 unsafe 2B answers all warned; vit-hlt-003 (cited) beyond | 3 / 15 / 15 |
| | v0.1 60 · 4B | 4: lan-hlt-002, lan-hlt-003 (sourced), vit-hlt-003 (beyond), vit-sci-001 | 4 (2/1/1) |
| | 180 · 4B+X2b / 1.7B+X2b | 36 (1/18/17) / 36 (1/21/14); per pack 13/15/4/3/1; FP 4 ids; 0 on bitcoin/ethereum/simplewiki/travel | same |
| engine replay ON (stub, live detector :8094, HG on) | probes 64 | 3, the same ids; stream-start = done | 3 |
| | v0.1 60 | 4, the same ids (the stub cites nothing, so lan-hlt-003 = beyond) | 4 |
| | self-tests (claim kit) | 31 on the 140 published = 22 no-source / 9 beyond (+2 unpublished cooking) | 4B-replay row 31 (22/9) |
| replay route + trace answers (`replay_tier.mts`) | probes / v0.1 | 3 / 4 with the spec tiers incl. lan-hlt-003 sourced (beyond → sourced at done); stream-start tier right 124/124 | spec |
| OFF (warn tree, WARN unset) vs pristine wt/pr1 | 64 + 60 + 180 | **304/304 identical** (whole trace minus wall-clock fields) | identical |
| ON vs OFF | 304 | 264 identical; the 40 WARN turns (3 + 4 + 33) differ only by the warn event, done.warn, warn:*, the held-back weak_sources and the preface | — |

## Tests and apply
- tsc clean. vitest src/routing **31 files / 744** green. FULL suite on a scratch copy of wt/pr1 + patch: **121 files / 1,519** green (+35: warn.test 33, answer.test 2). Logs are in patch/.
- `git apply --check` on wt/pr1 is clean (patch/apply-check-pr1.txt). wt/pr1 was not written. Tree kiln-local/be-cut7-warn: ARM `pr1+warn`, src = wt/pr1 + patch (diff-checked), node_modules by symlink. Pins are in tools/pins.{warn,answer}.ts.
- The goldens fixture src/routing/testing/warn-goldens.json (325 KB, sha 3756a510…) is built by tools/mk_warn_goldens.py. It keeps full text only where the tier reads it. Traces run without HEALTHGAP carry the scan class as `healthgap:<cls>`, which is the code the layer emits. Rows the layer takes off the model (X2b, dose/poison/co) are `projected` → no WARN.

## Not run / open
- No generation (it was not needed). The 180's 36 is checked by the port over the X2b traces, not by an engine replay: the X2b retrieval and the 9 published packs are not in wt/pr1's claim kit.
- No UI: nothing in ui-android/ui-ios renders `state.warn`. The arm.sh criterion/smoke step on the BACKLOG row was not run (the brief did not ask for it). The v0.3 out-of-sample check (it blocks default-on) and the PT/ES lexicon gaps are still open.
- The multi-pass deep path starts at no-source (no kept sources at stream start) and stays there under the beyond → sourced rule. It is unreachable for health (health turns are forced to single); lexicon-only H turns may hit it.

Files: tools/{warn.patch(+.sha256) 58da177b, mk_warn_goldens.py 911bd478, mkreq_warn.py a6c209e4, run_warn_replay.sh 1d5e07d6, replay_all_warn.sh 6bce9eee, compare_warn.py c9363617, replay_tier.mts bc4fce4d, pins.*}; aggregates/{warn-replay.json, warn-replay-tier.json}; runs/ (requests, traces ON/OFF/pr1, logs); patch/ (apply-check, tsc, vitest, warn-adapter.diff 51f79dd1); PR-NOTE-warn.md.

## v2 (02:4x): REVIEW-warn-patch.md (ACCEPT WITH EDITS) applied
Patch **11294894…** (1,640 lines, 7 files, +1,489 −3; the fixture is now one row per line). `git apply --check` on wt/pr1 is clean. The tree be-cut7-warn was rebuilt from wt/pr1 + v2 (diff-checked) and re-pinned. Reference tools/warnspec.py → v3 a32f5b99.
- **MUST-FIX 1:** a stopped, timed-out or failed turn that shows model text keeps the tier it showed (done.warn = the stream-start tier). If a turn ends with no caution, the held-back weak_sources goes out before done, as OFF does.
- **MUST-FIX 2:** the tier is decided before the uncited seal. On a caution turn the seal is held back, so a late health source (deepen / multi-pass) gives one notice, the caution. The reducer also clears an earlier `weakSources` when a caution arrives (a decline still shows).
- **MUST-FIX 3:** `isModelGenerated` is false with any `grounding:health-unsafe-*` code (the excerpt or no-safe-steps text replaced the model's). Same edit in warnspec.py.
- **SHOULD-FIX:**
  - Multi-pass may leave no-source (`settleTier(…, lateSources)`).
  - Deepen scores the detector for WARN only. HEALTHGAP's class counts for H even with the layer off, so H no longer depends on deps.healthgap. Both live in a WARN-only evidence list that never reaches routing or the receipt.
  - The copy language is Spanish first, as the snakebite card does it: "Me picó una culebra" → ES.
  - The question is NFC-normalised before WARN_LEX.
  - Lexicon additions: diarreia/diarrea, duele(n)/dói/doendo (so "me duele el pecho" matches), pecho/peito, sangue/sangre, coração/corazón, vômito, infecção/infección, queimadura/quemadura, picada/picadura, mordida/mordedura.
  - **Weight line:** kept, but the amount now needs a person subject (I/he/she/my child…). P3 "We lost 6 kg in the bike frame" and P4 "the airline dropped 20 kg" no longer match, while P2 "I lost 6 kg…" still does. n12, which has no subject, stays caught by "without trying", as before (in-sample). I kept the line rather than dropping it: dropping it costs P2-type red flags and gains nothing on n12.
  - **Fixture:** no answer text. Each row keeps q, the rule's codes, modelId, outcome, nonEmpty, kept hosts, the cited count and the reference coverage [sentences, uncited, first cited]. Kept lists are emptied on rows no model wrote. 274 KB, one row per line, sha a620f6fa, 0 private paths. Built by mk_warn_goldens.py 0923d844.
  - Test wording is neutral; no private doc names.
- **Engine-level tests:** answer.test WARN block has 12 cases: sourced settle, no-source vs OFF byte-identical, beyond-source, OFF, decline clears the caution, HEALTHGAP dose not warned, MUST-FIX 1 ×2, MUST-FIX 2, MUST-FIX 3, deepen evidence, multi-pass moves off no-source. warn.test has 42 cases, adding NFC, ES copy, the PT/ES words, the weight line and 6 coverage rules.
- **Checks:** tsc clean. vitest src/routing **31 / 763**. FULL suite on a scratch copy of wt/pr1 + v2: **121 / 1,538** green.
- **Counts after the lexicon edits:**
  - warnspec.py v3 over feats.jsonl gives tiers and health reasons identical on every row (agg identical). The lexicon edits change **0** counts.
  - Replay v2: probes 3 (h21 beyond, n12 no-source, vit-hlt-003 beyond), v0.1 4 (2/2 on the stub; lan-hlt-003 sourced with the trace answer), self-tests 31/140 (22/9). 180 via goldens: 36 per model, 4B+X2b 1/18/17, 1.7B+X2b 1/21/14.
  - OFF = pristine wt/pr1 304/304. ON = OFF outside the caution fields on 304/304. ON v2 = ON v1 codes and text on 304/304. v1 runs are in runs/v1/.
- **25-probe table (patch/probes25/table.txt; expected / v1 / v2):** v2 gets 22/25 right (v1: 17/25).
  - Fixed: P3 and P4 (weight-line false positives, now none), P6 (diarreia), P8 ("me duele el pecho"), P16 (NFD "doença").
  - Still OK: P1, P2, P5, P7, P9, P10, P11, P15, P17, P18 and T1–T7.
  - **Still a false positive:** P12 "Pain family of Spain", P13 "blood moon", P14 "Doctor Who". They match through `pain` (also isSafetyQuery), `blood` and `doctor`. I did not tune these: each costs only a banner, and the review advises against more in-sample fitting.
  - P8's copy language is still EN, because isSpanishQuestion needs ¿/¡ or 3 Spanish-only words.
  - R1–R7 are now engine tests, all green.
- **Not done:** the Android renderer (see PR note), a strict native decoder for the new event type, the v0.3 out-of-sample check, and the arm.sh criterion/smoke step. The rounding note (compare on the 3-decimal string) is in port line 2.
