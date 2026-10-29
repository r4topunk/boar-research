# DEEPPAR-L1 result: judged parity bmoe v0.28.0 vs llama-server b11010, deep35 R450 (D4 step c): **TRANSFER**

Criterion: `DEEPPAR-L1-criterion.md` sha256 `1d9745879102cc891deb11f14c5b641403a76a4f3edd30da5102dc5ae3d69be5` (verified 21:47 before start, not edited). Previous step: `DEEPPAR-criterion.md` sha256 `98028c0dcd84e4c63abbdb61d280c92fe866b52b8ddef9526ed7d4c08322ce18` (FAIL, see DEEPPAR.md). Runner: Kiln, 2026-10-07 21:47–22:50.

**Pre-checks (mini 21:47):** free 34 GiB, swap used 2600 MB / 4096, load 1.68, no llama/bmoe process (ollama serve idle only). GGUF sha256 `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` = expected. `bmoe-cli` sha256 `7d5f12e8021d5ebc18a6589ab32b1a94c16dafaf3f3e128e71c70800d04df94e` = DEEPPAR.md. Controls: A traces `05710eee2f92`, A judgments `b40265bf921b`, B judgments `d51e87775b38` (all = criterion). `requests.jsonl` sha256 `a7c2cbe435e6baa46ef0c71a7282a73e499fb8fbd5782c3253568823812c0b69` (57 rows).
**Render:** llama-server b11010, DEEPPAR flags, port 18094, healthy 14 s; 57 × `/apply-template` (enable_thinking false); SIGTERM rc 0, `pgrep llama-server` = none before bmoe started. Rendered sha256 list: `raw/l1/rendered-sha256.txt`.
**Generation:** one `bmoe-cli --session` process under `<runner>/bin/run-heavy` (waited 0 s) and `/usr/bin/time -l`: `--temp 0.7 --top-k 40 --top-p 0.95 --seed 42 -n 512 -c 4096 -t 4 --ubatch 512 --moe-stream --overlap --dense-weights anon --cache-mb 1500 --io-threads 4 --csv`; requests `{"cmd":"generate","id":k,"n_predict":512,"think":false,"clear_kv":true,"prompt":<rendered>}` (raw, no `--chatml`/`--no-think`). Source check (cli/main.cpp, session.cpp): session requests use the process sampler flags; `clear_kv:true` calls `llama_sampler_reset` → seed 42 per item, like the control's per-request seed. Model load 9.8 s, 21:49:13–22:23:13, 57/57 answers, 0 errors, 0 `<think>` blocks, 0 hit 512 tokens. **Prompt tokens bmoe = control A on 57/57** (n_prompt vs llama-server prompt_n).

## Quality (Opus judge.v1, combined orders, 57 items each)
| arm | ratio [95 % CI] | floor-adjusted [CI] | win / tie / loss vs ref | pos. consistency | C / Cm / U (answer) |
|---|---|---|---|---|---|
| **bmoe R450** | **0.623** [0.576, 0.672] | 0.526 [0.464, 0.584] | 1 / 4 / 52 | 0.947 | 3.80 / 2.60 / 2.75 |
| A: deep35 llama-server | 0.634 [0.590, 0.683] | 0.541 [0.479, 0.597] | 1 / 3 / 53 | 0.965 | 3.89 / 2.66 / 2.78 |
| B: 4B llama.rn | 0.606 [0.558, 0.658] | 0.505 [0.440, 0.567] | 1 / 2 / 54 | 0.982 | 3.58 / 2.58 / 2.76 |

| paired Δ (n = 57, bootstrap 2000, items jointly) | Δ ratio [95 % CI] | Δ floor-adjusted [CI] |
|---|---|---|
| **bmoe − A** | **−0.012** [−0.045, +0.020] | −0.015 [−0.055, +0.024] |
| bmoe − B | +0.017 [−0.026, +0.060] | +0.021 [−0.032, +0.079] |

Per-item bmoe vs A (combined-order mean score of each answer vs the same ref; equal = tie): **bmoe 15 / tie 20 / A 22**. `bmoe-R450.items.csv` has per-item means.

## Verdict rule (quoted) and application
"TRANSFER: paired Δ(bmoe − A) point ≥ −0.030 AND its 95 % CI includes 0." → Δ = −0.012 ≥ −0.030, CI [−0.045, +0.020] contains 0 → **TRANSFER**. The llama-server deep-tier numbers may be quoted for the bmoe device plan with the caveat "judged parity on 57 dev items, 1 seed, temperature 0.7 (noise floor ≈ 0.05)". D4 closed. (Context, not part of the rule: bmoe's ratio 0.623 is also ≥ 0.606, B's ratio; the paired CI vs A is wide enough that a ≈ 0.04 loss is not excluded.)

## Speed (mini M4, CPU, median over 57; descriptive)
| engine | prefill s | decode tok/s | total s | output tokens |
|---|---|---|---|---|
| bmoe session (`--moe-stream`, cache 1500 MiB) | 25.7 | 8.57 | 35.3 | 76 |
| A: llama-server b11010 (control traces) | 41.1 | 9.43 | 48.7 | — |
bmoe peak memory footprint (`time -l`, whole 57-item session) 11.72 GiB (12,587,599,968 B), max RSS 9.13 GiB; whole run 2029 s generation.

## Deviations from the criterion
1. Judge command: added `--bench bench/v0.1`. The bare command resolves `harness/config.json` → `../rnd/bench/questions/v0` (dry-run: refs `cfb8ceccd500`, questions `dc859ebd91b0`, 30 items), which would have tripped the criterion's first-line check. With `--bench bench/v0.1` the first log line is `judge: 57 items, 114 calls to do (0 done), refs bd235bb9811f, questions 568b3ececd8a` = the criterion's pins and the control's judge log (DEEPREAD used the same bench). Judged material unchanged.
2. No `min_p` in bmoe (pre-accepted in the criterion).
3. Runner bug, fixed before splicing: `results.jsonl` rows had the item id overwritten by bmoe's session `id` (0..56). `raw/l1/results.items.jsonl` re-maps by request order; checked against `run.log` (logs the item id per request, 57/57 in order) and the n_prompt match (57/57 equal to A position by position). Raw file kept as written.
4. Trace `timing` uses bmoe fields (`prefillS`, `decodeTokPerSec`, `totalS`, `promptTokens`, `outputTokens`, `loadS`); `resources.peakFootprintGiB` is the session-wide `time -l` value (one process for all items), not per item.

## Stop-rule events
None. Watchdog every 5 s: free disk min 30.5 GiB (≥ 25), swap used peak 7061 MB (< 8192). Never both engines resident. Docker untouched. Mini after (22:47): free 36 GiB, swap used 1150 MB, no llama/bmoe process. GGUF kept (free ≥ 25 GiB).

## Spend and wall

## Files
`bmoe-R450.traces.jsonl` (sha256 `088b44325d70b73fd6d6c472964474dfaf95f058d1023388b6b82fcf6302f7d0`), `bmoe-R450.judgments.jsonl`, `bmoe-R450.items.csv`, `tools/run_l1.py` (mini driver), `tools/splice.py`, `tools/analyze_l1.mjs`, `raw/l1/` (rendered sha list, results(.items).jsonl, session.stdout without per-token lines, session.csv, bmoe stderr head/tail, run/driver/server/judge logs, analysis.json; 0.9 MB). Mini copy: `<runner>/kiln/deeppar-l1/`. Not committed; QUEUE entry by the coordinator.
