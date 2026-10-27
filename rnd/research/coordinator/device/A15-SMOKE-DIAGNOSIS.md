# A15 smoke (cut 3 BOAR Bench, 2026-10-05): diagnosis of 3 issues

Data: `rnd/research/coordinator/device/a15-smoke-2026-10-05/` (SM-A155M, Helio G99, 7.5 GB, Android 16, 9 items, 20:47:22Z to 20:56:47Z).
Engine paths below are `bench-app/engine/src/...`; they are byte-identical to `wt/cut3-dev/src/...` for `inference/LlamaEngine.ts`, `routing/answer.ts`, `routing/context.ts`. Nothing in the engine or the app was changed. The desktop repro used `bench-app/dry-run/run.mts` (the phone's own runner on Node, llama-server shim, same kit: crypto + Wikivoyage, no Wikipedia). It wrote 2 rows into `bench-app/dry-run/appdir/eval/diag-a15-warmup.*`, and nothing else.

## TL;DR
- **Wrong instant answer: reproduced on desktop, so it is an engine bug, not a device bug.** The same codes and the same Lyon snippet come out. Both "Paris is the capital" and "Lyon is France's gastronomic capital" score 1.0 (the page title "France" is credited to every sentence), the tie goes to the shorter sentence, and no check asks whether the sentence answers the question. Fix: one `instantFinalBlock` rule (fragment + figurative modifier).
- **Mojibake is an export artifact** (UTF-8 bytes decoded as cp1252 and re-encoded on the host, CRLF added). The em dash in the warm-up answer comes from the pack, not from the request, so input cannot be the cause. The model most likely saw clean input (desktop on the same request gives a clean "Gríma"). Not provable from the logcat (see UNKNOWN).
- **The biggest latency bug is the KV session cache: it can never work on Android.** The key contains `models/…gguf`, so the file path is `cache/kv/models/<file>.bin`, but only `cache/kv/` is created. `saveSession` fails ("Failed to save session"), `loadKv` never finds a file, and every question re-prefills the gate prefix (about 430 tokens, 35–41 s) and the answer prefix (about 260–350 tokens, 20–28 s) at about 12 tok/s. The desktop shim makes `saveSession` a no-op, so this was invisible.
- **The 15–70 s before "retrieving" is exactly that gate-prefix prefill**, plus on the first item a ~28 s model load, plus detector (1.4 s) and gate (2.5–5 s). When the previous model-path item generated nothing (cards), the gate cache survived and the same stage took 2.9–3.0 s.
- Fixing the key is a one-line change with an estimated −55 to −65 s per model-path question (about 100–147 s down to about 40–85 s). The remaining floor is decode at 2.0–2.9 tok/s (swap and threads, unverified) and retrieval at 6–15 s warm and 57 s cold.
- Cheaper-than-gate options (skip the gate, threads, repack) are secondary and need an L1 or a device A/B.

---

## 1. Wrong instant answer ("What is the capital of France?" -> Lyon)

### Root cause
Desktop reproduces it exactly: reason codes `task:lookup, route-gate:cold-load, route-gate:search, route-gate:score-1.000, retrieve:yes, instant:may-finish, …, context:598->249, instant:final`. Titles `Wikivoyage: France` x2, snippet `- — France's gastronomic capital with a history from Roman times to the Resistance`, tier instant, modelId extractive. The score and the gate are deterministic. Only the timing differs (desktop `retrieving` at 20.6 s, phone 69.8 s).

Why the instant tier accepted it (`routing/answer.ts:1044-1073`, `routing/context.ts`):
1. `plan.instant == "may-finish"` for `task:lookup`. The retrieved pool has only Wikivoyage France chunks.
2. `selectInstant` (`context.ts:155`) scores by IDF-weighted term coverage of {capital, france}. `scoreSentences` (`context.ts:114-126`) credits any title segment whose words are all in the question ("France") to **every** sentence of that page. So any sentence containing "capital" scores 1.0, whatever it says about the capital.
3. Near-ties go to the shorter sentence (`context.ts:159-162`). A synthetic check with a Paris sentence ("Paris — The capital and largest city of France, …") next to the Lyon line still picks Lyon, in either order (script in the session scratchpad: `inst.mts`).
4. The gates are lexical only: `onSubject` true, `termCoverage` = 1.0 (>= 0.75), `sentenceNamesSubject` true ("France's"), and `instantFinalBlock` (`context.ts:184`) returns null. Its anaphora test only catches pronouns. The "What is X" definition test is skipped because the term starts with "the". Pointer and title-only tests pass.
5. Nothing checks that the sentence is a statement about the *capital of France* (copula or "France's capital"), nor that it is a sentence at all. The text starts with `- —`: the Wikivoyage list entry "Lyon — France's gastronomic capital…" lost its subject (the link text "Lyon" was stripped by the pack builder), and "capital" is figurative.

### What the 126.6 s consists of (measured: stages + telemetry, and consistent with the Sahara log in §3)
| Part | s | Evidence |
|---|---|---|
| Detector (first call, loads detector) | 1.4 | `loading_model` stage at 1395 ms |
| Cold model load of the 2.5 GB GGUF (`route-gate:cold-load`, `answer.ts:762-770`) | about 28 | telemetry PSS 0.38 GB at +5 s, 4.59 GB peak at +28 s (repack), 3.6 GB at +35 s |
| Gate fixed-part prefill (430 tok at about 12 tok/s, see §3) | about 35 | derived: 69.8 − 1.4 − 28 − 5 |
| Gate call | about 5 | Sahara `gateMs=5012` |
| `retrieving` stage starts | 69.8 | stage `atMs` |
| **Retrieval, cold** (`retrievalMs`) | **56.8** | receipt; no `retrievalStages` in cut 3, so unsplit |
| Instant extractive, no generation | about 0 | `tokensGenerated 0`, total − retrieval = 69.8 |

### Proposed fix (engine, 1 rule, no quality surface elsewhere)
In `instantFinalBlock` add a new block reason, `"fragment"`, returning non-null when:
- the snippet starts with a bullet or dash fragment (`/^\s*[-–—•*]/`), or
- the question is "(what|which) is the NOUN of X" and the snippet does not contain NOUN directly adjacent to X (`X's NOUN` or `NOUN of X`, no adjective between). That rejects "France's gastronomic capital" and accepts "the capital of France".

Effect: warm-up falls to the model path (correct "Paris" is expected from the Wikivoyage France page, to be confirmed). It costs a generation (about 40–100 s on this phone today) but is right. Other instant answers should be unchanged: run Sonar's instant replay (`rnd/research/sonar/exp/34-gold-hit/replay.sh` with the stub LLM) over the dev set and count `instant:final` flips. The first rule is mostly the pack's problem: removing "- —" entries from the pack's snippet pool is cleaner but needs a pack rebuild, so it is left out of the minimal fix.

Also: the first-item cold-load plus gate (about 68 s) was spent for an answer that needed no model. An instant-final preview before the gate is not possible (the gate decides whether to search), so this stays.

---

## 2. Mojibake ("GrÃ­ma", "â€”")

### Root cause: export, not engine, not the app
- **Raw bytes of `rows.jsonl`**: the "í" is `c3 83 c2 ad` (double-encoded) and the em dash is U+00E2 U+20AC U+201D. U+20AC and U+201D are what **cp1252** gives for bytes 0x80 and 0x94, which Latin-1 would not. So: UTF-8 bytes were decoded as cp1252 and written back as UTF-8. The file also has CRLF line ends (8 of 9 rows; the device writes LF only). Both are the signature of a Windows-side text-mode step (for example Python `open()` without `encoding=`, or PowerShell redirect).
- **The em dash can't come from the request**: it is in the *warm-up answer*, a Wikivoyage pack sentence. The engine on desktop emits it correctly ("- — France's…"), and the pack has it as UTF-8. So the double encoding happens at or after the output, regardless of what the input was.
- **Desktop with the same request** (diag run, request with `í` escape): query, answer and `retrievedTitles` all show a correct "Gríma".
- **App side is clean**: rows are written by `FileSystem.writeAsStringAsync(savedPath, evalRowsToJsonl(rows))` (`eval/answerEval.ts:255,269`), UTF-8 by default and the same code that gives correct rows on desktop. `android-run.sh` pulls with `exec-out run-as … cat` (byte-safe) and builds the request with Node `JSON.stringify` (raw UTF-8, base64 on the wire, `-d` on device, byte-safe). The `request.json` in the folder is not what `android-run.sh` writes (it writes a one-line raw-UTF-8 file with `printf`); it is a 1-space-indented, `\u`-escaped file, so the tester used their own pipeline.
- **Latent hazard in the convert script**: `boar-eval/scorers/convert_device.py:146,149` uses `Path.read_text()` / `write_text()` without `encoding="utf-8"`. On Windows (cp1252) this reproduces exactly this corruption. Fix: add `encoding="utf-8"` (and `newline="\n"` on write). It is not the cause here because the damage is already in the raw `rows.jsonl`.

### Did the model see mojibake?
Most likely **no**, but not provable. An escaped `í` in the pushed file cannot be mis-decoded by `JSON.parse`; retrieval and the grounding codes on the phone (`context:378->153`, `off-topic-dropped-1`, same title) equal desktop with a clean query. If the pushed file had held raw UTF-8 and the app had read it as cp1252, the em dash in the *answer* would still be clean (it comes from the pack), and it is not. The only thing that can't be separated from the rows is the model's own echo "GrÃ­ma" (it would be equal either way after the export). The logcat has the model prompt tokens only for the last item (see §3 and UNKNOWN).

### Fix
- Tester side: pull with `adb exec-out run-as team.sopa.boarbench cat files/eval/<rid>.answer.jsonl > rows.jsonl` and no Windows text step; run `convert_device.py` with `PYTHONUTF8=1`. Check: `xxd rows.jsonl | grep -m1 "Gr"` must show `c3 ad` (the rows file stays on the phone).
- Code: the two `encoding="utf-8"` arguments above. Effect: none on scores, removes a silent corruption path on Windows. `bench-run.sh` already uses `exec-out`.

---

## 3. Latency

### Timeline per row (stages and receipts; times in s)
| item | route | start of `retrieving` (detector + gate + load) | retrieval | prefill (tokens, new) | decode (tok, tok/s) | total |
|---|---|---|---|---|---|---|
| warmup-000 | instant, cold load | 69.8 | 56.8 | none | none | 126.6 |
| vit-hum-004 | model | 36.6 | 8.3 | 27.6 (348 tok, 12.6 tok/s) | 80 tok, 2.88 | 100.5 |
| vit-trv-004 | calculator | none | none | none | none | 0.2 |
| probe-co-001 | health card (via gate) | 37.9 | 14.1 | none | none | 52.0 |
| probe-co-002 | CO rule | none | none | none | none | 0.07 |
| probe-co-alarm | health card (via gate) | **2.9** | 14.6 | none | none | 17.5 |
| dng-001 | snakebite rule | none | none | none | none | 0.07 |
| vit-cry-001 | model | **3.0** | 11.8 | 56.9 (713 tok, 12.5 tok/s) | 72 tok, 2.04 | 107.2 |
| lan-exp-005 | model | 46.8 | 5.8 | 46.9 (509 tok, 10.8 tok/s) | 105 tok, 2.23 | 146.7 |

Order of work in `answer.ts`: detector (`:633`) -> deterministic rules (`:640-700`) -> geo -> `selectAnswerModel` -> cold load if needed (`:762`) -> **route gate** `nextTokenProbs` (`:772`) -> `retrieving` (`:959`). Embedding of the query and retrieval are inside "retrieving"; the detector is the cheap part (1.4 s on the first call, under about 0.5 s later).

### What fills the 15–70 s before "retrieving"
Logcat caveat: the `main` buffer was flooded by another process (about 310k `geller_cache` error lines from pid 28992, in 17:54–17:55), so **only item 9 (Sahara, from 17:54:43) has app logs**. All the others have only stages and receipts. Item 9 gives the anchor:

| Clock (device) | Event |
|---|---|
| 17:54:18.8 | item start (end 17:56:45.5 minus 146.7 s) |
| 17:55:00.532 | `[gate] session save failed: Failed to save session` (right after the 430-token fixed-part prefill) |
| 17:55:00.577 | `loadPrompt` of the gate messages |
| 17:55:05.544 | `[gate] … newTok=30 cachedTok=460 loadGateMs=- gateMs=5012 … SEARCH:1.000` |
| 17:55:05.550 | embedding tokens of the query (BERT ids) -> retrieval starts (stage `retrieving` at +46.8 s = 17:55:05.6) |
| 17:55:11.391 | `loadPrompt` of the answer (prefill stage at +52.6 s) |

So the 46.8 s is: detector (about 1 s) + **fixed-part prefill of the gate prompt, 41 s** + gate 5 s. At the observed 10.8–12.6 tok/s, 430 tokens (`cachedTok 460 − newTok 30`) is 34–40 s, which matches. The same arithmetic explains vit-hum-004 (36.6 s), probe-co-001 (37.9 s) and the warm-up (69.8 s with the 28 s load). The two 3 s items (probe-co-alarm, vit-cry-001) are the proof: `gateCachedKey` was still set because the previous model-path item did not generate (cards), so the fixed part was reused (`LlamaEngine.ts:600-603`).

Why the gate keeps re-prefilling (`LlamaEngine.ts`):
- `generateNow` sets `gateCachedKey = null` (`:555`), and so does `warmNow` (`:479`), because the single llama context's KV now holds the answer prompt.
- Next gate: `loadKv` returns null (no file, `:606`), so it runs the 430-token warm prefill (`:608-615`) and then `saveKv` (`:616`).

### "[gate] session save failed"
`saveKv` (`:652-658`) only creates `${cacheDirectory}kv/`. The key is `${modelFilename}.${hash}.gate` (`:604`) with `modelFilename = "models/qwen3-4b-instruct-2507-q4km.gguf"` (catalog `models/manifest.ts:135`; the log line prints it). The path becomes `cache/kv/models/qwen3-…gguf.<hash>.gate.bin`, and `kv/models/` does not exist, so llama.rn's native `saveSession` fails with "Failed to save session". The answer-prefix key (`answerKvKey`, `:642`) has the same flaw. The catch only warns (`:616`, `:480`), so every item silently pays full prefill for both prefixes. The desktop shim (`dry-run/shims/llama-rn.mjs:107-108`) turns `saveSession` and `loadSession` into no-ops, which is why no desktop run could show it.

Evidence that the answer prefix is also not restored: `cachedTokens − ctxTokens` (tokens already in KV before the prompt) is only 85, 77 and 110 in the three model rows, so the answer prefix (about 260–330 tokens) is re-prefilled inside the 28–57 s "prefill" stage.

### Cheapest fixes, ranked by seconds saved (per model-path question, A15 estimates)
| # | Fix | Where | Saves | Notes |
|---|---|---|---|---|
| 1 | **Make the KV key a safe file name** (replace `/` and `.` in the model part, for example `key.replace(/[^\w.-]/g, "_")` in `kvPath`), and `makeDirectoryAsync` on `dirname(path)`. The restore replaces both prefills by a `loadSession` of about 60 MB. | `LlamaEngine.ts:647-658` (one place for gate and answer keys) | **about 35–41 s** (gate prefix) **+ about 20–28 s** (answer prefix) = about 55–65 s | Zero quality surface (same tokens). Verify first: `adb shell run-as team.sopa.boarbench ls -R cache/kv` (expected: empty or just `kv/`). After the fix, expect `[gate] … loadGateMs=<~1000>` instead of `loadGateMs=-`. The first question after a cold start still pays once. |
| 2 | Add a `[gate] answer prefix restored in N ms` check to the bench (already logged at `:551`) and put `console.log` lines in the sidecar | `bench-app` | 0 s | Observability: logcat lost all lines before 17:54:43. Use `adb logcat -b all -G 16M` and a pid filter from the start. |
| 3 | Skip the gate when the rule router is confident (`ruleTaskType` research or lookup and the detector p < floor). All 6 gates here said `SEARCH:1.000`. | `answer.ts:772-795` | about 3–5 s per question (about 0.5 s restore x2 saved too) after #1; about 40 s before #1 | **Quality surface**: the gate also turns `chat` into `conversation` / `answer` (`route-gate:chat->conversation`). It needs an L1 before use. Not recommended before #1. |
| 4 | Threads: `nThreads` defaults to 4 (`LlamaEngine.ts:227,286`) on a 2x A76 + 6x A55 SoC. Test 2 / 3 / 4 / 6 on the same 3 items. | request hook (the BENCH-APP "bench-hooks" arm is not built) or a temporary one-line change in the app's `load` options | unknown; decode is 2.0–2.9 tok/s and prefill 11–13 tok/s | UNKNOWN until measured; thermal status rose to 1 at +211 s and to 2 in the last 11 samples (about 55 s), which explains part of the decode slowdown (2.88 -> 2.0–2.2 tok/s) but not the baseline. |
| 5 | Avoid repack (`no_extra_bufts`, the Probe B line, not in cut 3 per DEVICE-DAY §6). PSS 3.55 GB with **1.6 GB in swap after item 1** (0.73 GB at the end). | engine load options | maybe −10 s load, and less page-fault stall in decode: unknown | Memory pressure: MemTotal 7.5 GB on an A15 with the Samsung stack. |
| 6 | Keep the detector before the model | already the case (`answer.ts:633`) | 0 | Not a source of delay: 1.4 s cold, small later. |
| 7 | Keep the context resident | already: `loadMs 0` on all model rows after the first | 0 | The one load (about 28 s) is a one-time cost; gate cold-load happens inside `loading_model`. |

Retrieval is a second block that stays: 5.8–14.6 s warm (desktop about 1 s) and 56.8 s cold. Cut 3 has no perf flags (`perf: null` in `bench.json`; `grep` for `sqlBatch|nativeZstd|vectorCache` in `engine/src` finds nothing), so there is nothing to switch on without carrying forge-ship. The next step is to log `retrievalStages` (sql / zstd / embed split) before choosing a fix.

Expected result of #1 alone, on the same 9 items (arithmetic from the table, not measured): vit-hum-004 about 100 -> about 40 s, lan-exp-005 about 147 -> about 85 s, vit-cry-001 107 -> about 80 s (its gate was already cached), probe-co-001 52 -> about 17 s. Warm-up unchanged (it is the cold start). Decode (30–50 s per answer at 2–3 tok/s) then dominates.

---

## UNKNOWN
- Whether `cache/kv/models/` is really missing and the failure is exactly ENOENT. The line-level reading of `kvPath` + `saveKv` makes it certain that the directory is not created; the native error text is only "Failed to save session". A second cause (for example an empty-token state) would be invisible until #1 is applied and `ls -R cache/kv` is run.
- Whether the Paris sentence was in the phone's retrieved chunks. The synthetic check (Lyon wins over Paris in both orders) shows the mechanism but not the real chunk list. Only the titles are in the rows.
- Which host step double-encoded the rows (Windows Python, PowerShell, or something else). The tester should say how `rows.jsonl` and `request.json` were produced; `request.json` in the folder is not an `android-run.sh` output.
- What the model saw for the "Gríma" prompt: the logcat only holds prompt tokens for item 9. Evidence is indirect (retrieval and grounding codes equal desktop). Check by `adb exec-out run-as team.sopa.boarbench cat files/eval/dev-cut3-smoke.answer.jsonl | xxd | grep -m1 Gr` (raw device bytes) and by re-running the Gríma item with the `[gate]` and prompt logs captured from the start.
- The cold-load split (28 s load vs repack vs embedding init) and the cold retrieval split (56.8 s): derived from the PSS curve and the stage times, no explicit log lines (the logcat lost them).
- Prefill and decode speed under thermal status 0 (the run was at status 0 for 37 of 102 samples, 1 for 54, 2 for 11) and with swap (1.6 GB after item 1). Decode 2.0–2.9 tok/s is much lower than expected for a 4B Q4_K_M, and the cause (threads, little cores, swap, thermal) is unmeasured.
- Whether the fragment rule in §1 flips other instant answers (needs the Sonar replay on the dev set; no blind or v0.2 material was used).

## Correction (2026-10-05, coordinator, after peer review)
The KV session-save code (saveSession/loadSession, `<cache>/kv/<key>.bin`) is not in upstream 0cfd4a77 or upstream main 38f996d1 (`git grep` returns nothing). It was introduced by our ship-stack patch (rnd/research/forge/arms/shipcut/shipcut2-norv2.vs-0cfd4a77.patch, ~l.69 and 200–208) and inherited by cut 3 and BOAR Bench. The bug is therefore our own regression: the session-file design never worked on device. KVFIX must travel with that design in any PR. If q8_0 KV (upstream PR 72) is adopted, the session key must include the KV cache type.
