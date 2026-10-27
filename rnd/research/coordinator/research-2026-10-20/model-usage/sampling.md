# Model-usage audit: sampling and decoding (2026-10-20)

TL;DR: no sampling or decoding misuse explains today's 1.7B NOs. Desktop and phone use the same sampler (T 0.7 / top_k 40 / top_p 0.95 / min_p 0.05, no penalties). The token cap and the stop handling never bind on the 1.7B: across today's arms the answers average 40 tokens, the longest is 105 tokens against a cap of 512, 0 end mid-sentence and 0 loop. The vendor card values were tested today (VENDORSAMP), and so was greedy (GREEDY). Both moved CE by less than the gate's bar. Findings are medium or low: an app-fidelity gap on 1.7B thinking, greedy loops and format breaks in OCC-RAG on Q4_K_M, a false-positive `thinkingBudgetExceeded` flag, and sampler fields missing from traces.

Tools: `model-usage/sampling-tools/capscan.py` and `capscan2.py` (stats over all non-blind `*.traces.jsonl`, 1119 files). These were reads only, with 0 generations and 0 judge calls.

## Configuration per path (as executed)
| Path | Where | temp | top_k / top_p / min_p | penalties | seed | n_predict | stop |
|---|---|---|---|---|---|---|---|
| Fast/compact answer, desktop server | be/server.ts:26-28 `samplerFor` | engine value (0.7; health 0) | 40 / 0.95 / 0.05 | none (llama.cpp default repeat 1.0) | 42 per request | answer.ts:1455 min(512, gen.maxTokens) + thinking budget unless enable_thinking false | template EOG; `stop` [] |
| Same, desktop node path | be/adapter-litedecline.ts:357-359 | same | 40 / 0.95 / 0.05 | none passed | 42 | same | — |
| Phone (llama.rn 0.13.0-rc.4) | src/inference/LlamaEngine.ts:536-558; llama.rn cpp/jsi/JSIParams.cpp:427-449 | passed per call | not passed, so vendored common.h:230-232 defaults 40 / 0.95 / 0.05 | default 1.0 | **-1 (random per call)**, JSIParams.cpp:428 | same | template EOG |
| Deep (Qwen3.6-35B) | depth.ts:102-104, 243 | 0.7 | 40 / 0.95 / 0.05 (DEEPSAMP tested the card values: NO) | none | 42 | 200 answer + 512 think | — |
| Health T0 | answer.ts:1460 | 0 | — | — | — | 512 | — |
| OCC-RAG (arm only) | occrag.patch:85,125 | 0, top_k 1 (card: greedy) | — | none | 42 | 512 + 512 trace + forced 8 + 64 | `--special` |
| Route gate (phone) | LlamaEngine.ts:647 | 1, n_predict 1, n_probs 20 | defaults (post-sampler probs) | — | — | 1 | — |
None of the GGUFs embed `general.sampling.*` metadata (Qwen3-1.7B, 4B-2507, Qwen2.5-1.5B and bge were checked), so the llama.cpp defaults above apply.

Vendor cards: Qwen3 non-thinking and Qwen3-2507 instruct recommend T 0.7 / top_p 0.8 / top_k 20 / min_p 0 / presence 0-2. Qwen3 thinking recommends T 0.6 / 0.95 / 20 / 0. Qwen2.5 recommends T 0.7 / 0.8 / 20 / repetition 1.05. OCC-RAG recommends greedy (`do_sample=False`), `enable_thinking=False`, `max_new_tokens` 2048 in the quickstart.

## Measured from traces (non-blind only)
| model, tier, backend | n | mean answer tok | max | at cap | mid-sentence | 4-gram x4 |
|---|---|---|---|---|---|---|
| qwen3-1.7b fast server, today's arms (lp K0-K4, b-honest, shortctx, quotefirst, greedy, logprob, vendorsamp) | ~1,500 | 39-48 | 105 | 0 | 0 | 1 (natural repetition) |
| qwen3-1.7b fast server, all runs | 3275 | 53 | (OCC smokes 1536) | 8, all OCC smokes | 8 | 0 |
| qwen3-4b-2507 fast server | 7856 | 51 | 552 | 4 | 0.6 % | 96, inspected: natural repetition, not loops |
| qwen3-4b-2507 fast node | 9433 | 71 | 768 | 101, all persona-detailed + vxa | 2.4 %, chat emoji endings | 17 |
| deep35 deep | 57 | 72 | 115 | 0 of 200 | 0 | 0 |
| qwen2.5-1.5b fast node | 5728 | 48 | 768 | 3 = one item looping "[1] [1] ..." at T0 (10-01 iOS runs) | 0.3 % | 3 |

Decoding noise vs the screen bar: VENDORSAMP changed 15/37 answers and gave 1 fix and 1 worse sentinel. GREEDY changed 24/37 and gave 4 fixes. A pure decoding perturbation therefore produces about 1-4 "fixes", below the bar of 6. Sampling noise does not hide a real lever, and it does not manufacture the NOs.

## Findings
- **M1. App-fidelity gap on 1.7B thinking.** The engine's fast plan always requests thinking (depth.ts:255,259 `thinking: true`, which sends FAST_THINKING_BUDGET 256 and no enable_thinking=false, answer.ts:1457-1458). On the desktop the 1.7B stays thinking-off only because the server runs with `--reasoning off` (traces `server.extra_args`). A TS-engine phone build on llama.rn would let the Qwen3-1.7B think for up to 256 tokens, with n_predict 768. The desktop 1.7B numbers are therefore "thinking off by server flag", not the engine's behaviour. LITETHINK shows thinking on is flat or negative, so the measured NOs stand. The gap is in product parity: the native Kotlin app must disable thinking explicitly. Test: 1 render via `/apply-template` without `--reasoning off` and the engine's body, then check whether `<think>` is open.
- **M2. OCC-RAG greedy on Q4_K_M loops and breaks format.** Greedy decoding follows the card, but there is no repetition or presence guard. The sidecar shows 1 status loop ("hidden\nTrue" repeated ~400 times, K0), 2 invented status strings ("ANSWER_SOURCE", "HAS_ANSWER"), and 8 of 40 OCC calls malformed or looped (OCCRAG.md). Even if all 3 malformed calls on K1 had become fixes, K1 would reach 6 only in the best case, so the verdict probably holds. It is untested whether a Q8_0 quant or presence_penalty 0.5-1.0 cuts the breaks. False-UNANSWERABLE at 47-60 % is the dominant cause, and that is model behaviour, not sampling.
- **L1. Engine sampler is not any vendor's card.** It uses llama.cpp defaults (40 / 0.95 / 0.05) on all Qwen paths. The card values were tested on the 1.7B (VENDORSAMP NO, 22/37 identical) and on the 35B (DEEPSAMP Q -0.029, P -0.017). They were never tested on the 4B-2507 (same family, expected to be a no-op).
- **L2. `thinkingBudgetExceeded` is a false positive** (be/server.ts `budgetExceeded`). Every flagged dt512 item has exactly 522 reasoning tokens: 512 plus the ~10-token THINKING_BUDGET_MESSAGE, which the server streams as reasoning_content. Maple at budget 256 shows 264. 381/527 deep traces are flagged "not app-faithful" when the budget was in fact enforced. The fix is to subtract the message length or use `>`, budget + 16.
- **L3. Trace sampler fields are incomplete.** `runtime.sampler` records only temperature and seed. top_k/top_p/min_p are hard-coded and appear only via `versions["sampler.override"]`. Deep-tier traces also label `runtime.model` with the fast model id (e.g. qwen3-4b-instruct-2507 on dt512 deep generations).
- **L4. Phone vs desktop seed.** The phone passes no seed, so it is random per call. The desktop uses seed 42, a single draw. Device numbers carry sampling variance that desktop screens do not show. All of today's screens are single-seed, T 0.7.
- **L5. Phone gate probabilities are post-sampler.** llama.rn rn-completion.cpp:1637-1642 reads `common_sampler_get_candidates` after top_k 40 / top_p 0.95 / min_p 0.05 at T 1. The desktop gate (be/gate.ts) uses the raw softmax. The SEARCH/ANS ratio keeps its sign, but a label below 0.05·p_max becomes 0, and if both are pruned the result is null (fallback).
- **L6. LITETHINK (10-16) did not use the card's thinking sampler.** It ran at T 0.7 / top_k 40 / min_p 0.05 instead of the thinking card's 0.6 / 20 / 0. The arm is closed.
- **L7. Qwen2.5-1.5B at T0 has no repetition_penalty** (the card says 1.05). vit-hlt-003 looped "[1] [1] ..." to the 768 cap in 3 iOS runs (boar-eval/runs/night-2026-10-01). This applies only if Qwen2.5 is still shipped anywhere (UNKNOWN for boar-ios, where no sampler code was found in Swift).

## Checked OK
- BOAR_SAMPLER_JSON was applied and recorded (VENDORSAMP changed 15/37 answers; GREEDY changed 24/37 with temperature 0 in the traces). Requests carry no `temperature`, so the engine's per-call value (health 0) is honoured.
- No n_predict truncation and no broken stop on the 1.7B: 0 cap hits and 0 mid-sentence endings in today's arms. The EOG from the chat template ends every answer.
- No repetition loops on the 1.7B or the 4B outside OCC. The 96 4-gram flags on the 4B are natural repetition ("people per square kilometer").
- The deep answer cap of 200 is not binding (max 115). The thinking budget is enforced at 512 (+ message).
- The LOGPROB arm left decoding unchanged (97/97 byte-identical) and read raw (pre-sampler) probabilities.
- Desktop/phone sampler parity: both use 40 / 0.95 / 0.05, and the llama.rn param persistence (JSIParams falls back to the previous value) is reset by an explicit temperature and n_probs on every answer call.
- No GGUF ships `general.sampling.*` metadata that could silently override the defaults.

UNKNOWN: the sampler of the native Kotlin app and of boar-ios (not in this tree); whether Q8_0 reduces OCC format breaks; the seed-to-seed CE flip rate of the 1.7B control (a second-seed control screen would calibrate the "fixed ≥ 6" bar directly).
