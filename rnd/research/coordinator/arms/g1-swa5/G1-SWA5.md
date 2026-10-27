# G1-SWA5 prep: 5-turn Gemma sessions on rc.4, swa_full arm (2026-10-21)

TL;DR: step 0 finds 0 KV/decode markers in the existing Gemma phone logs (all single-turn). dd2 APK built with two bench-only switches (swaFull, session) plus greedy/seed sampling overrides; 3 requests, the readout script and the frozen criterion are ready. Phone step = about 20 min on 10-22. 0 LLM, 0 judge, 0 paid so far.

Criterion: G1-SWA5-criterion.md, sha256 b89f1f1a... (G1-SWA5-criterion.sha256), committed in rnd 60eba22b before any phone run. Ids: ruler/ids/swa5.ids (ls03-t1..t5 + ls04-t1..t5, sha256 e259efac...).

## Step 0 (0 LLM): existing Gemma phone results, handoff/pixel8-2026-10-20/bench/results/
| dir | files grepped | 'memory slot' | 'llama_decode' | 'kv' + error/fail |
|---|---|---|---|---|
| gemma10-a | none: the dir has no logcat/bench.json/log (aborted run; only request, device, kit, meminfo, telemetry) | n/a | n/a | n/a |
| gemma10-b | logcat.txt (1474 lines), bench.json | 0 | 0 | 0 |
| gemma73-a | logcat.txt (9967), bench.json | 0 | 0 | 0 |
| gemmaa73-a | logcat.txt (9183), bench.json, results/gemmaa73-a.log | 0 | 0 | 0 |
llama/ggml lines are present in the logcats (399 in gemma73-a), so the native log is captured; 'kv' matched 3 unrelated hiddenapi lines per logcat, none with error/fail. As expected: these runs are single-turn, and the bug needs the cache to fill across turns.

## dd2 switches (bench-app commit c9c6a22; engine tree unchanged = parsearch 8ad2c4b0, Promise.all search, BLOCK_CACHE 16)
- engineOverrides.swaFull (bool) -> rc.4 ContextParams swa_full (native: JSIParams.cpp l.375). Init param, so a change reloads. Absent = the key is never set (init params JSON-identical to the engine's).
- engineOverrides.temperature / seed (added; the hypothesis needs greedy and the engine sends temperature 0.7 with the llama.rn seed -1 = random). temperature replaces the answer completions' value only (n_probs 0). The route-gate probe (n_probs > 0) keeps temperature 1 because rc.4 n_probs are post-sampling. seed goes on every completion. Not init params: no reload.
- request "session": {"groups": [[ids in turn order], ...]}. The runner reads it from pending.json (as it reads engineOverrides) and validates it: ids exist, are contiguous and in order, query texts unique, one model, no answerAnyway. src/answerServiceTap.ts (what answerEval gets for answerService) then gives turn k's answer() call ctx.history = {turns: earlier questions + the engine's own result.text from this run}. That is the chat's follow-up path (ConversationHistory -> assembleChatMessages, DETMAX window, route gate with history), as LONGSESSION run A did on desktop. Turn 1 and the warm-up keep ctx unchanged. bench.json gets sessionLog (history messages/chars per turn). Nothing existed for multi-turn on the phone before: answerEval always asks standalone.
- Deviation from the app: full earlier session (8 messages at turn 5, no summary). The app UI keeps 6 verbatim + a background summary, so turn 5 sends one turn more than the app, as in LONGSESSION. A killed/resumed request breaks history (resume skips answered turns), so the readout marks such a run INVALID.
- Check: tools/params_test.mts (tsx, 22 checks OK). Default-arm blocks leave init params byte-identical with no swa_full key; the full arm adds exactly swa_full:true and changes the config key (reload); the sampling and session shapes are covered. bench-app tsc clean. The release bundle contains swa_full, sessionLog and BENCH_VERSION 0.3.2-swa5.

## APK
bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-dd2-nonet-8ad2c4b0fae9.apk (89.7 MB, no INTERNET), sha256 57c704774829df3db1a4d7b714de231c3bc3d6ad56ca083305491c77ee04ffe9 (.sha256 file next to it). Incremental gradle :app:assembleRelease, JDK17 Homebrew, BENCH_NONET=1, same native libs / llama.rn 0.13.0-rc.4 (unchanged). bench-app/engine left on the parsearch tree.

## Requests (handoff/pixel8-2026-10-20/bench/requests/, made by tools/mkreq_swa5.py)
| request | model | engineOverrides | sha256 |
|---|---|---|---|
| swa5-g-default | gemma-4-e2b-it-q4km | reload, temperature 0, seed 42 | bd0727ae... |
| swa5-g-full | gemma-4-e2b-it-q4km | + swaFull true | 41556048... |
| swa5-q17-default | qwen3-1.7b-q4km | reload, temperature 0, seed 42 | 7db97cdc... |
Each request: warmup-000 + ls03-t1..t5 + ls04-t1..t5 (11 questions), session groups [ls03], [ls04], quickFirst true, A-union kit as on the phone.

## Run (r4to, phone, about 20 min, no thermal gate; this is not a speed run)
1. adb install -r <the dd2 apk path above> (keeps files/ and the kit).
2. Run these in the bench folder, one at a time: python3 boar_bench.py run swa5-g-default, then swa5-g-full, then swa5-q17-default. Each takes about 3-5 min. Before each run, note the temperature from adb shell dumpsys battery | grep temperature; telemetry.csv logs it too.
3. Reinstall the APK that the next device-day step names.

## Evaluate (0 LLM)
python3 -I tools/compare_swa5.py --json readout.json -> per-turn tier, history wiring, error/empty/garbled flags, logcat markers, 32-word identity default vs full, divergence onsets, and the verdict under the frozen criterion (KILLED / CONFIRMED / INCONCLUSIVE / INVALID). Smoke-tested on synthetic dirs.
UNKNOWN: whether the epinephrine turn (ls03-t4) reaches the LLM on Gemma or ends on a card (LONGSESSION saw fa-card-from-history on ls03); turns that skip the LLM are trivially identical and reduce the test's power. The per-turn tier column shows this.

## Addendum 2026-10-21 16:3x: phone run (device runner, 0 LLM readout)
Verdict under the frozen criterion: **KILLED** ("5-turn sessions clean on rc.4"). Identity clause VOID (turn 1 differs: ls04-t1 30 vs 34 tokens at temperature 0 / seed 42), so markers decided: Gemma default 0 error rows, 0 empty, 0 garbled, 0 logcat markers (memory slot / llama_decode / kv error / decode failed) over 10 turns; swa_full arm the same; Qwen3-1.7B control 0/10. Wiring valid: historyMessages = 2 x (turn - 1) on 10/10 turns in all three arms; swa_full true in the full arm's init. Descriptive: turns 2-5 identical at 32 words 4/8, divergence onsets with identical history 1; only 5 of the 8 Gemma follow-up turns reach the LLM (ls03-t2, t3, t5 end on the card / source path with 0 tokens), so the test's power is 5 LLM follow-ups per arm.
Deviations: (1) BOAR Bench was found NOT installed at session start (pm path empty; fresh uid after install, files/ empty), so dd2 was a fresh install and the A-union kit was rebuilt from local files (bench-app/kits/persona-a-union.kit.txt + embedding, detector, Qwen3-1.7B, Gemma 4 E2B, Qwen2.5-1.5B, Qwen3-4B; every pack and the gazetteer sha-matched shared-data/packs/persona-a-union/SHA256SUMS on the device; model sizes equal the gemmaa73-a kit.txt). The first swa5-g-default attempt timed out (app had no kit, request not picked up; no rows, discarded). (2) Arm order: swa5-g-full ran first (its pending.json from the killed driver was picked up as soon as the app opened; a fresh request, not a resume; pulled with --pull-only; its telemetry.csv is from the killed driver and is renamed STALE), then g-default, then q17-default. Each arm reloads the model (reload true), so order does not enter the criterion. (3) Battery 28.8 C at the g-full start, 30.9 / 33.3 C before/after g-default, 33.7 C after q17; thermal status 0 throughout (results/swa5-*/temps-swa5-all-arms.txt). Readout: readout.json (compare_swa5.py needs the results dir as first argument when --json is given; otherwise it treats the json path as the results dir).
