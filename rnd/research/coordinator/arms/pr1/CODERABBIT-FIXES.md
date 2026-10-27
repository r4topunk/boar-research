# CODERABBIT-FIXES: the five review findings on PR #85 (pr/cut7-engine), 2026-10-15

TL;DR (updated): review fixes in **570e0716** on top (see last section; identity 60/60 vs de3d97ac). All five findings fixed in **one commit de3d97ac** on pr/cut7-engine (parent 8b117738), not pushed. 9 files,
+222/−17. tsc clean, vitest **1,386/1,386** (1,378 + 8 new; each new test fails on 8b117738). Retrieval replay 60/60
identical to cut 7. Generation identity vs the cut 7 reference: tier/task/outcome/kept/reason codes 60/60, text 59/60 (lan-exp-007, the known reference-run noise from PR1-REBASE.md); vs the PR-1 run (8882b175) **60/60 on every field**. No finding left as a follow-up.

## Findings
| # | finding (verified against 8b117738) | fix | test |
|---|---|---|---|
| 1 | emergencyDetector.ts `load()`: after `canary-fail` / `no-canary` / `load-failed`, every question re-ran `loadNow()` (re-init of mmBERT next to the resident 4B). Confirmed: `load()` only short-circuited on `loaded`. | `TERMINAL_STATUSES` set; `load()` returns false without `loadNow()` for those; `absent` stays re-checkable. | emergencyDetector.test.ts "remembers a terminal load status…": 3 terminal cases → second `load()` adds no `initLlama`; absent → model added → loads. |
| 2 | context.ts `ES_ONLY` contained `está`, `se`, `grave` (also Portuguese): "Uma cobra me picou e está inchando, se piorar é grave? O que faço?" scored 3 → Spanish; answer.ts snakebite branch checked ES before PT → ES card for a PT question. Confirmed. | Removed the 3 shared words; snakebite branch now `pt = isPortugueseQuestion; es = !pt && isSpanishQuestion` (same as the other card sites). | context.test.ts: that PT question is not Spanish (and is PT); "Una serpiente mordió a mi hijo, qué hago?" and a `¿` question are Spanish. answer.test.ts: PT question → PT card, ES question → ES card. |
| 3 | answer.ts route-gate cold load discarded `LoadResult`; the answer's `ensureLoaded` then finds the model resident, so the `model_streams_from_storage` warning and `backend:cpu-fallback` were lost on the gated path. Confirmed. | Gate load handles the result like `ensureLoaded` (warning event; `backend:cpu-fallback` into the gate's reason codes). | answer.test.ts "cold start: the gate's load reports a storage-streaming warning and a CPU fallback". |
| 4 | routeGate.test.ts: `ROUTE_GATE_SYSTEM_B5_LENGTH = ROUTE_GATE_SYSTEM.length` → tautological. Confirmed. | Pinned literal **1673** (measured; prompt sha256 7708281b…, identical to coord/cut7's routeGate.ts), comment "update only with a new gate measurement". | the existing assertion now binds. |
| 5 | LlamaEngine.ts: `queue` (load/unload) and `genQueue` are independent; `unloadNow()` only waited for `inFlight` completions, so it could release the context while `loadKv`/`saveKv` awaited `loadSession`/`saveSession`, and the generation path then used the released (or a replaced) context. Confirmed (also a gap inside saveKv/loadKv between the FileSystem await and the native call). | (a) `tracked()` puts session I/O in `inFlight`; (b) `unloadNow()` waits in a **loop** until `inFlight` is empty, then clears `this.context` in the same synchronous step; (c) `assertCurrent(context)` after every await before a native call (generateNow, restoreStaticSystem, saveKv) — generate throws "LlamaEngine: model unloaded", the gate returns null (rules answer), `loadKv` returns null without deleting the session file. generateNow now uses the captured context throughout. | LlamaEngine.test.ts "unload during KV session I/O": unload during a pending `loadSession` (answer prefix restore) waits, then the answer rejects with no completion; unload during the gate's `saveSession` waits, gate → null, no gate completion; unload during the directory check → no `loadSession`, file kept. All 3 fail on 8b117738. |

Why the minimal fix is safe: JS is single-threaded, so "check `this.context === context` and start the native call (setting
`inFlight`)" and "see `inFlight` empty and null `this.context`" are each synchronous; whichever runs first, the other sees it.
Residual (not a bug): an unload that arrives while a completion is queued but not yet started still waits for that
completion (the loop stops it each round); `stop()` semantics are unchanged. The desktop runner does not use LlamaEngine.

## Checks
| check | result |
|---|---|
| `npx tsc --noEmit` | exit 0 (pr1cr.tsc.log) |
| `npx vitest run` | 118 files, 1,386/1,386 (pr1cr.vitest.log) |
| retrieval replay, 60 v0.1 items, `--tasks-from` cut 7 reference traces, `--compress`, wt/pr1 at de3d97ac | **60/60 identical** to replay-cut7.jsonl; identicalRaw 60/60 (replay-pr1cr.{jsonl,log}, replay-compare-pr1cr.txt) |
| generation identity, seed 42, tree kiln-local/be-de3d97ac-pr1cr (git archive de3d97ac + adapter 8dd1faff), llama-b11010-cpu, `-t 4`, mmbert :8094, same kit | rc 0, 60 rows, 12:48–12:56. vs cut 7 reference (v01-cut7-stack-off-s42): text 59/60, tier 60/60, task 60/60, outcome 60/60, kept titles 60/60, reason codes 60/60; only DIFF = lan-exp-007 text ("its land area" vs "the territory"), identical to the PR-1 run's text and diagnosed in PR1-REBASE.md as reference-run noise. vs v01-pr1-s42 (8882b175): **60/60 identical on all fields** |

Generation setup: requests runs/v01-pr1cr-s42.requests.jsonl = v01-pr1-s42 requests with runId → v01-pr1cr-s42, commit → de3d97ac,
arm → pr1cr (item, settings, kit, seed, device unchanged). Runner tools/run_pr1cr_gen.sh (copy of run_pr1_gen.sh, tree/run names only).
Compare: `python3 tools/compare_gen.py ../stack/runs/v01-cut7-stack-off-s42.traces.jsonl runs/v01-pr1cr-s42.traces.jsonl` (gen-compare-pr1cr.txt).
Note the tip also carries the two Android wiring commits (a1d75389, 8b117738); they touch ui-android, settings and locales only.

## Expected vs observed
- ES_ONLY: v0.1 is English; no v0.1 question contains 3 of the remaining ES words, so no item should change.
- Detector fix: desktop scores through llama-server, the device detector class is not on this path.
- Gate cold-load result: the desktop adapter's load returns no warning/cpu-fallback.
- Engine race: LlamaEngine is not used by the desktop runner.

Observed: as expected, no item changed because of these fixes (60/60 identical to the 8882b175 run). Checked offline as well: no
v0.1 public question is Spanish under either the old or the new ES_ONLY.

## Review fixes (REVIEW-coderabbit-fixes-de3d97ac.md) → commit 570e0716
One commit on top of de3d97ac (not amended, so the de3d97ac evidence above stays valid), 4 files +27/−17, not pushed.
| review item | fix | test |
|---|---|---|
| S1 snakebite card PT-first sent Spanish ("Me picó una culebra, que hago?") to the PT card (192/193) | Spanish first again at answer.ts snakebite site (`esQ = isSpanishQuestion; pt = !esQ && isPortugueseQuestion`); the ES_ONLY change alone keeps the PT question PT. My earlier "same precedence as the other card sites" reasoning was wrong: isPortugueseQuestion fires on Spanish. | answer.test.ts: PT question → PT card; "Una serpiente mordió a mi hijo, qué hago?" and "Me picó una culebra, que hago?" → ES card (fails on de3d97ac). |
| S2 a "model unloaded" throw left the generate timeout armed (legacy executor path, 120 s) | timer armed right before `context.completion` (inside nothing that can throw before the try/finally). Trade-off: the timeout no longer counts the prefix/session restore time. | LlamaEngine.test.ts "an answer that fails with 'model unloaded' leaves no timeout armed" (timeoutMs 30, onTimeout not called 60 ms later; fails on de3d97ac). |
| N6 naming | `ROUTE_GATE_SYSTEM_B6_LENGTH`, title "after the B6 system prompt"; value 1673 unchanged | — |
| N5 double report when the gate cold-loads fast and the answer loads deep | partial, 1 line: `backend:cpu-fallback` is added only once. The two `model_streams_from_storage` warnings are left: each is about a model that really was loaded, and suppressing/deferring the gate's one needs ~8 lines plus a path for instant answers (more than the 1–3-line bar). | — |
Not taken: N1 (unloading flag to cancel queued generations), N2 (ES recall rule for shared words), N3 (terminal no-canary/load-failed is the stated intent), N4 (release a context created before a load-failed throw, predates this PR); the other PT-first card sites (answer.ts ~1127/1138/1176/1188, predate this PR) — follow-ups.

Checks at 570e0716: tsc exit 0 (pr1cr2.tsc.log); vitest 118 files, **1,387/1,387** (pr1cr2.vitest.log); retrieval replay **60/60** identical to cut 7 (replay-pr1cr2.*, replay-compare-pr1cr2.txt); generation identity (tree kiln-local/be-570e0716-pr1cr2, runs/v01-pr1cr2-s42.*, tools/run_pr1cr2_gen.sh, same protocol): rc 0, 60 rows; vs the de3d97ac run **60/60 identical on every field**; vs the cut 7 reference text 59/60 (lan-exp-007, as before), all other fields 60/60 (gen-compare-pr1cr2.txt).
