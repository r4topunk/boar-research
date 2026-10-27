# A15 latency budget, cut 4 (2026-10-06)

TL;DR
- **Model (calibrated on the 9 A15 smoke rows, cut 3): a cut 4 model-path answer on the A15 takes p50 68.7 s / p90 88.9 s with KVFIX working (warm), versus 116.8 s / 141.7 s cold (no KV restore, today's cut 3 behaviour). TTFT p50 39 s warm vs 90 s cold.** Ranges (fast..slow parameter sets): warm 55..84 s p50, cold 103..134 s p50.
- Warm share of a model-path answer: **decode 42% (29.5 s), answer prefill 35% (24.5 s), retrieval 17% (11.8 s)**, gate 6% (4.0 s), KV restores + detector 1%. After KVFIX the A15 is token-rate bound (77% prefill+decode at 11.9 and 2.3 tok/s). Cold: gate prefix prefill 32%, answer prefill 32%, decode 25%, retrieval 10%.
- Best engine changes (warm, p50 per model-path answer): **(1) retrieval speed-up (Forge perf arms) -7.7 s, (2) second KV prefix for no-source prompts -3.9 s (-15 s on 28% of items), (3) skip the route gate when rules decide -3.7 s** (-27.7 s mean if KVFIX fails). All three: 68.7 to 54.4 s. Shorter context and answer caps save under 1 s on this bench.
- A bigger lever than any of them is the device rate (threads, KV type, repack): prefill+decode x1.25 would give -10.5 s, unmeasured (UNKNOWN 6).
- Correction to A15-SMOKE-DIAGNOSIS §3: `cachedTokens - ctxTokens` (85/77/110) are the generated tokens (80/72/105), not reused prefix. Only 5 tokens (ChatML head) were reused. The answer prefix was never restored, as predicted by the save bug.
- Desktop traces contain NO gate call (the boar-eval adapter has no `nextTokenProbs`: `grep -c nextTokenProbs boar-eval/adapters/desktop-node/runner/adapter.ts` = 0; no `route-gate:` code in 120 traces). All desktop quality numbers were measured without the gate.

Helper: `tools/a15_budget.py` (model, writes `tools/a15_budget.out.json`, `tools/a15_budget.items.csv`), `tools/tokcounts.mts` (tokenizer counts, `tools/tokcounts.json`). Engine = `wt/instsubj` (cut 4) read-only; line numbers below are `src/...` there.

## 1. Steps before the first answer token (cut 4, phone)
| # | Step | Where | LLM / embedding | Evidence of cost (A15) |
|---|---|---|---|---|
| 0 | Learned emergency detector: mmBERT-small encoder, 126 tokens, 2 threads, on EVERY question | `routing/answer.ts:633`, `routing/emergencyDetector.ts` | embedding model | 1.4 s first call (`stages` loading_model at 1395 ms), 0.07 s later (rule rows 0.067-0.22 s total, `rows.jsonl`) |
| 1 | Deterministic rules: snakebite, CO, emergency numbers, small talk, calculator, arithmetic, travel distance | `answer.ts:641-712` | none | 0.07-0.22 s total (vit-trv-004, probe-co-002, dng-001) |
| 2 | Places (SQLite POI) | `answer.ts:714-722` | none | desktop 14-69 ms; no phone row |
| 3 | Model selection, `estimateFit` | `answer.ts:724-743` | none | UNKNOWN (small) |
| 4 | Cold model load (first gated message only) | `answer.ts:762` | - | about 28 s once (diag §1 PSS curve, derived) |
| 5 | **Route gate**: one forward pass, n_predict 1, n_probs 20 | `answer.ts:745-795`, `routing/routeGate.ts`, `LlamaEngine.ts:596-640` | **LLM** | fixed 429-token system prefill + 29 new tokens + 1 step; 2.9-5.0 s when the prefix is resident |
| 6 | Query embedding (bge-small via llama.rn, 2 threads) | `rag/retrieve.ts:167`, `rag/embed.ts` | embedding model | inside retrieval |
| 7 | Retrieval: FTS5 BM25 + brute-force cosine + pack + wiki-pack search, fuse, dedupe (no reranker anywhere: `grep -ri rerank src` empty) | `rag/retrieve.ts:168-212` | none | 5.8, 8.3, 11.8, 14.1, 14.6 s warm (5 rows), 56.8 s cold |
| 8 | compressContext, grounding filters, instant snippet (JS) | `answer.ts:995-1073` | none | not separable in logs (UNKNOWN, desktop 0.1-0.2 s total retrieval) |
| 9 | Prompt build (`assembleChatMessages`: system = persona + sources, user = question) | `rag/pure.ts:370-400` | none | negligible |
| 10 | **Answer prefill** (1 LLM call; `n_predict = maxTokens + 256` thinking budget, unused by the non-thinking 4B) | `answer.ts:1323`, `LlamaEngine.ts:520-570` | **LLM** | 348/713/509 new tokens in 27.6/56.9/46.9 s = 12.6/12.5/10.8 tok/s |
Then decode (2.0-2.9 tok/s) and the citation checks (JS). Phone LLM calls per question: 2 for 100 of 120 trace rows (gate + answer), 1 for 8 (health cards pass the gate, then answer without the model), 0 for 12 (rules, places). Embedding calls: detector x120, query x108 (English; PT adds a second search).

### The 15-70 s "pre-retrieval phase" (best evidence)
Item 9 (lan-exp-005) is the only row with app logs (`logcat.txt.gz`, 17:54:43 onward; rest flooded by `geller_cache`). Item start = 17:56:45.53 minus 146.66 s = 17:54:18.87.
- 17:55:00.532 `[gate] session save failed` = end of the gate-prefix prefill: **41.7 s after start**. Minus detector (0.1 s) = 41.6 s for 429 tokens = 10.3 tok/s.
- 17:55:00.577 to 17:55:05.544 gate step: `newTok=30 cachedTok=460 gateMs=5012` (5.0 s).
- 17:55:05.550 query tokens (BERT ids) = retrieval starts (`retrieving` stage at 46.8 s); 17:55:11.391 answer `loadPrompt` (retrieval 5.8 s).
Other rows, same arithmetic (pre = `retrieving` stage time; gate step 3.0 s; detector 0.07 s): vit-hum-004 36.6 s -> 33.5 s prefix = 12.7 tok/s; probe-co-001 37.9 s -> 34.8 s = 12.3 tok/s. Mean of the three: 36.7 s = 11.7 tok/s, equal to the answer prefill rate (11.9). The two 3 s rows (probe-co-alarm 2.9, vit-cry-001 3.0) had the previous item generate nothing (cards), so `gateCachedKey` was still set (`LlamaEngine.ts:619-620`, reset at `:387,479,555`). So the phase is **gate-prefix prefill (about 35-42 s) + gate step (3-5 s) + detector**, plus 28 s load on item 1. Cause of the prefill: the KV save path bug (fixed by KVFIX 3b9f09de). Remaining UNKNOWN: the exact detector/gate split on rows without logs.

## 2. Cut 4 desktop traces: per-item tokens and calls
Source: `boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44.traces.jsonl`, `...s45...` (control = instsubj4 = cut 4 final, PATCH d51e844c, 60 items x 2 seeds; `SPEEDPACK-L1.md` Identity). Fields: `route.task/tier/reasonCodes`, `retrieval.kept`, `timing.promptTokens/outputTokens/retrievalMs`; `cache_prompt:false` on the server, so promptTokens is the whole prompt (runner/server.ts:42). The traces have one `generation` event per answer (100 rows) and no gate event, no per-call split; the gate call is added from the phone. Per-item rows: `tools/a15_budget.items.csv`.
Check: desktop promptTokens 353/718/514 for vit-hum-004/vit-cry-001/lan-exp-005 = phone `ctxTokens` + 5 (348/713/509). Same tokens on both.
| Per generating call (n=100 of 120) | p50 | p90 | mean |
|---|---|---|---|
| prompt tokens | 474.5 | 630.8 | 459.9 |
| (a) cacheable by KVFIX (answer prefix, 230 tok, `tokcounts.json`) | 230 | 230 | 72 items with sources |
| (b) new tokens (warm) | 272.5 | 400.8 | 292.9 |
| generated tokens | 70 | 92.3 | 68.7 |
Tiers: fast 104 (100 generate + 4 health cards), instant 16 (6 rules, 6 places, 4 health extractive). Tasks: lookup 42, chat 34, research 26, compare 2. **28 of 100 generating prompts have no source** (`kept=[]`): their system message (190 tok, static) does NOT start with the cached prefix (no CONTEXT_INSTRUCTION, `rag/pure.ts:370-385`), so KVFIX gives them nothing (`sharesPrefix`, `LlamaEngine.ts:446`). Gate tokens: 429 fixed (phone log; our tokenizer 427) + 29-30 new.

## 3. Calibration and projection
Parameters (script `P`; fast / central / slow), all from `a15-smoke-2026-10-05/rows.jsonl` unless noted:
| Parameter | fast | central | slow | Derivation |
|---|---|---|---|---|
| prefill tok/s | 12.6 | 11.94 | 10.8 | sum ctxTokens / sum prefillMs, 3 model rows (min, pooled, min) |
| decode tok/s | 2.88 | 2.33 | 2.04 | sum tokens / sum (total-ttft), 3 rows |
| retrieval s (warm) | 5.8 | 11.8 | 14.6 | 5 warm gated rows (min, median, max); cold 56.8 excluded |
| gate step s (prefix resident) | 2.9 | 3.0 | 5.0 | stage starts 2.9/3.0 (cards), logcat 5.0 |
| detector s | 0.05 | 0.07 | 0.3 | rule rows |
| KV restore s (each of gate, answer prefix) | 0.5 | 1.0 | 3.0 | **assumed, never measured** (60 MB and 33 MB files) |
State model: one llama context. Gate sets KV=gate (restore, or 429-token prefill when cold). A generation with sources needs the answer prefix (restore when warm; prefix already resident only if no gate ran since the last answer). Items run in trace (bench) order.
Validation, cut 3 cold replay of the smoke rows (predicted / measured total): vit-hum-004 110.8 / 100.5 s (+10%), probe-co-001 53.1 / 52.0, probe-co-alarm 17.7 / 17.5, vit-cry-001 105.5 / 107.2 (-2%), lan-exp-005 132.5 / 146.7 (-10%, thermal). Pre-retrieval 39.0 vs measured 36.6/37.9/46.8.
Projection, 100 model-path items (120 trace rows, same seeds; cut 4 on A15; one run, thermal not simulated beyond the slow set):
| Scenario | total p50 | total p90 | TTFT p50 | TTFT p90 | all 120 rows p50 / p90 |
|---|---|---|---|---|---|
| **warm (KVFIX), central** | **68.7** | **88.9** | 39.1 | 50.4 | 66.2 / 87.6 |
| warm, fast / slow | 54.8 / 83.5 | 72.7 / 107.3 | 31.0 / 49.0 | 41.5 / 63.0 | |
| warm, restore 3 s each | 72.0 | 92.9 | 41.6 | 54.4 | |
| **cold (no restore), central** | **116.8** | **141.7** | 89.9 | 103.2 | 113.3 / 140.4 |
| cold, fast / slow | 102.8 / 133.5 | 123.6 / 161.8 | 79.8 / 102.8 | 92.4 / 117.6 | |
Share of mean time per model-path answer (central): 
| Component | warm s (%) | cold s (%) |
|---|---|---|
| detector | 0.1 (0) | 0.1 (0) |
| gate (restore or 429-tok prefill, + step) | 4.0 (6) | 37.9 (32) |
| retrieval | 11.8 (17) | 11.8 (10) |
| answer KV restore | 0.7 (1) | 0 |
| answer prefill (new tokens / 11.94) | 24.5 (35) | 38.1 (32) |
| decode (68.7 tok / 2.33) | 29.5 (42) | 29.5 (25) |
| total | 70.6 | 117.3 |
Excluded: the first question after launch (model load 28 s, cold retrieval 56.8 s, first detector 1.4 s, one-time prefix creation; smoke warm-up 126.6 s).

## 4. Candidate engine changes (warm, central; savings per model-path answer, p50 / mean over all 120 rows)
| Rank | Change | Saves | How computed | Quality risk |
|---|---|---|---|---|
| 1 | **Retrieval speed-up**: Forge perf arms (native zstd, vector cache, sqlBatch; `forge/SHIP-SPEED.md`, patch `forge/arms/ship/forge-ship.patch`, not landed, never run on a phone) | **-7.7 s** / -6.9 | retrieval x0.35: D8300 measured 1.2-1.8 s to 0.35-0.6 s; applied to the A15's 11.8 s | None by design (same results; desktop identity 72/72 is still a landing check). Effect on A15 is an extrapolation: first log `retrievalStages` |
| 2 | **Second KV prefix for the no-source prompt** (static 190-token system message gets its own session key and restore; same tokens) | **-3.9 s** / -3.4; **-14.9 s on each of the 28% no-source items** (190/11.94 - 1.0) | `nosrc_cache` in script | None (token-identical). Matters in real use only if no-source questions are common on the A15 kit (UNKNOWN 5) |
| 3 | **Skip the route gate** when `ruleTaskType` is lookup/research/compare, no detector fire, no history, not about BOAR (70 of 108 gated rows) | **-3.7 s** / -2.9 (all gated rows: -5.1 / -4.7). **If KVFIX fails: -27.7 s mean** (gate prefix) | `skip_gate` in script; also drops the answer-prefix restore when gate is skipped on consecutive items | Low. All desktop v0.1 numbers (control 0.559, `SPEEDPACK-L1.md`) were measured without a gate, so for these types the route is identical to what was measured. Gate said SEARCH 1.000 on 6/6 phone rows; gate's own record: false search 3/34, missed search 0/23 (`routeGate.ts` header). Residual risk: a question the gate would divert to conversation (not in v0.1; needs a chat-like probe set) |
Combined 1+2+3: **p50 68.7 to 54.4 s (-14.4), p90 88.9 to 79.9**.
Alternative to 3 with zero quality risk: start retrieval while the gate runs (speculative): -4.0 s ideal, -2.0 s at 50% hidden (CPU contention UNKNOWN); not additive with 3.
Checked and not worth it: non-lookup context cap 450 (-0.4 s, 12 rows touched); context cap 300 for all tasks (-2.5 s p50, -3.4 mean, **high** risk: evidence cut; SPEEDPACK L1 showed even a faithful prompt diet raised confident-wrong 5 to 9); answer cap 120 tokens (-0.0 s, 1 row above 120; the 96-token cap was mid-sentence on 7-8 answers/seed and failed L1); k=4 to 3 (-19 tokens, `QUEUE.md` k3-on-cut2).
Not an engine change, larger: device rate. Prefill+decode x1.25 (threads pinned to the 2 A76 cores, KV q8_0 [KVQ8 PASS], repack off) gives p50 58.2 s (-10.5 s). No A15 measurement exists (UNKNOWN 6).

## UNKNOWN
1. KV restore time (`loadSession`, about 60 MB gate + 33 MB answer prefix) and whether llama.rn reuses the restored tokens: no cut 3 log (restore never succeeded). Assumed 1.0 s each; 3 s each moves warm p50 to 72.0 s. Check after KVFIX: `[gate] loadGateMs=<n>`, `cachedTok`, `[gate] answer prefix restored in N ms`, and `ctxTokens` near `prompt - 230`.
2. Retrieval split (query embed vs FTS vs scan vs packs vs zstd): cut 3 has no `retrievalStages`; only 5 warm samples; the two slowest (14.1/14.6 s) are health rows.
3. Idle prefix warm (`LlamaEngine.ts:427,433-470`): after a no-source generation `prefixCached` is false and a 750 ms timer starts a 230-token prefill (about 19 s) that can queue behind the next gate or compete with retrieval. Not modelled; it could add time in back-to-back runs.
4. Thermal and swap: smoke ran at thermal status 0-2 with 0.7-1.6 GB swapped; the slow set approximates this. Sustained 73-item run (`a15-v01-2026-10-05`, partial) was not used.
5. A15 kit differs from the desktop kit (no Wikipedia pack on the phone per diag): the share of no-source prompts and passage counts on the phone may differ from the 28% / 292.9 new tokens here. The 3 items checked have identical token counts.
6. Why decode is 2.0-2.9 tok/s and prefill 11-13 tok/s (threads 4 on 2xA76+6xA55, swap, thermal): unmeasured.
7. Detector warm cost (0.07 s) is inferred from the rule rows, not logged. Cut 4 itself has not run on the phone: the model is validated only against cut 3 (+10%/-2%/-10% on the 3 model rows).
