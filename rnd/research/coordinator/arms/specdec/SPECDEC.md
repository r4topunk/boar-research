# SPECDEC: speculative decoding for the 4B answer path (2026-10-06, coordinator)

TL;DR: **NO-GO. Every Qwen3-0.6B configuration fails G1, G2, G3 and G4; Qwen2.5-1.5B is refused by llama.cpp (vocab check).** Best config = Qwen3-0.6B Q8_0, n_max 4, engine sampler: acceptance **31.1 %** (1.21 accepted tokens per target pass), projected A15 decode saving **8.4 % = 2.4 s of 29.5 s decode per model answer** at central c = 0.256 (**-14.8 % at c +50 %**, +31.5 % only at c -50 %). Answer text identical to non-speculative on only 21/50 (greedy) and 9/50 (engine sampling). Added RAM 1.03 GiB (weights 0.60 + f16 KV 0.44 at n_ctx 4096), measured RSS +1.2..1.4 GB. llama.rn 0.13.0-rc.4 cannot run a plain draft model at all (native path is MTP-only). The downloaded GGUF was deleted.

Criterion `SPECDEC-criterion.md`, sha256 `66361511046c0242a91dc7400b2bb4ee989025e62545b52dee564618b31b0cbd` (verified, not edited). No judge, no blind/ or rnd/veil/ reads, nothing pushed.

## 1. Prompts (step 1)
- Stored traces do not hold the prompt, so cut 5 s44 was re-run once with prompt capture: tree `be-0cfd4a77-cut5lite` (patch sha `3b7a0dfa42bddee2...`), runner be-ship `f5c50806...` (`--dump-prompts`: rendered chat messages + nPredict + enableThinking per generate call, with itemId), requests = `cut5lite-l1/arm-v01-s44.requests.jsonl` re-keyed, `--backend server` (llama-server b11010, `-t 4 -c 4096 --jinja`), detector :8094 on (stopped by port after). 60 items, 0 errors, **50 model-path items = 50 prompts** (1 generate call each; the other 10 are rules/places/health cards with no model call). Driver `tools/specdec-capture.sh`; data `data/specdec-cut5-s44.prompts.jsonl` (sha256 `f50472cb...`).
- Fidelity: answer text of this server-backend run equals the stored node-backend cut 5 arm run (`runs/kiln/cut5lite-l1/arm-v01-s44.traces.jsonl`) on 50/50 items; mean prompt 459.94 tokens, mean output 69.32 tokens (cut 4 control: 459.94 / 68.65). All 50: `enableThinking` null, nPredict 512, so max_tokens = 512 + 256 thinking budget = 768 (as the engine does, `LlamaEngine.ts` generateNow).
- Replay body = what the runner sends: `messages`, `max_tokens` 768, temperature 0.7, top_k 40, top_p 0.95, min_p 0.05, seed 44, `cache_prompt` false. "greedy" runs use temperature 0 (G1 reads these).

## 2. Setup (step 2)
- Mac mini (M4, 10 cores, 16 GB, shared: load average 3-6 during the runs), heavy lock (`<runner>/bin/run-heavy Kiln`, class normal), llama-server b11010 CPU (same binary as the SPEEDPACK/CUT5 server runs), `-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --cache-ram 0`, one server per config, killed by pid in `finally`; ports 8187/8188/8094 verified free at the end. Disk 38 GiB before, 37 GiB after.
- Target: Qwen3-4B-Instruct-2507 Q4_K_M, sha256 `3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597` (= the traces' `model.sha256`).
- Draft 1: **Qwen3-0.6B-Q8_0.gguf**, official `Qwen/Qwen3-0.6B-GGUF` (the repo has only Q8_0; no Q4_K_M), 639,446,688 bytes, sha256 `9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031` (= the HF LFS oid in the repo tree API). Downloaded to `<runner>/kiln/specdec/` with curl, **deleted after the runs** (all configs fail).
- Draft 2: kit Qwen2.5-1.5B-Instruct Q4_K_M, sha256 `1adf0b11065d8ad2e8123ea110d1ec956dab4ab038eab665614adba04b6c3370`. **llama-server refuses it**: `the target and draft vocabs are not compatible` / `failed to initialize speculative decoding context: draft model vocab type must match target model to use speculation` (both n_vocab 151936, both BPE; the failing sub-check is a debug-level line not emitted at `-lv 4`, so UNKNOWN whether it is a token text or a BOS/EOS difference). The server then keeps running WITHOUT speculation; those 4 runs (q15n4/q15n8, samp + greedy) have draft_n null and are excluded from every number below (the analysis flags them `refused`). 0 extra bytes would have been the draft's only advantage, so the kit model is out as a draft.
- Flags in this build: `-md FILE --spec-type draft-simple --spec-draft-n-max N --spec-draft-n-min 0` (`--draft-max` was removed in b11010; p_min default 0.0 in both llama-server and llama.rn's vendored common.h).
- Measures: llama-server `timings.draft_n / draft_n_accepted`, passes = predicted_n - accepted (each target pass yields accepted+1 tokens), RSS = `ps` every 250 ms on the server pid. Driver `tools/specdec_replay.py` (+ `specdec-run.sh`), analysis `tools/specdec_analyze.py`, projection `tools/specdec_project.py`. Results in `data/res/` (per-config jsonl + server logs + `summary.jsonl`, `analysis.json`, `projection.json`).

## 3. Results per draft x n_max (50 model-path prompts)
Acceptance = accepted / drafted. Tok/s = Mac mini decode, descriptive only (baseline 25.2 tok/s, same for both control runs 25.2 / 25.1). RSS added = idle server RSS minus the same-mode baseline (baseline idle 5.19-5.38 GB; peak delta in brackets).

| draft | n_max | sampler | acceptance | accepted / target pass | drafted / pass | text identical to non-spec | Mac tok/s | RSS added (peak) |
|---|---|---|---|---|---|---|---|---|
| Qwen3-0.6B Q8_0 | 4 | engine (T 0.7, seed 44) | **31.1 %** | **1.209** | 3.89 | 9/50 | 14.4 | +1352 MB (+1242) |
| Qwen3-0.6B Q8_0 | 8 | engine | 18.4 % | 1.423 | 7.74 | 14/50 | 9.5 | +1179 MB (+1144) |
| Qwen3-0.6B Q8_0 | 4 | greedy | 32.1 % | 1.247 | 3.89 | **21/50** | 14.6 | +1372 MB (+1388) |
| Qwen3-0.6B Q8_0 | 8 | greedy | 18.3 % | 1.423 | 7.76 | **26/50** | 9.4 | +1362 MB (+1376) |
| Qwen2.5-1.5B Q4_K_M | 4, 8 | both | refused by llama-server (no speculation ran) | | | | | |

Exploratory, outside the criterion (Qwen3-0.6B with `--spec-draft-p-min 0.75`, engine / greedy): n_max 4 acceptance 72.9 % / 72.8 %, 0.696 / 0.684 accepted per pass, 0.95 drafted per pass, identical text 14/50 / 19/50, Mac 18.5 / 18.4 tok/s, RSS +1504 / +1275 MB; n_max 8 acceptance 66.9 % / 68.3 %, 0.720 / 0.733 per pass, 1.08 drafted, identical 8/50 / 19/50, 17.8 / 17.9 tok/s, RSS +1593 / +1464 MB.

Reading: acceptance of a Qwen3-0.6B (hybrid-thinking, original release) against the 2507 instruct 4B is low (about 1.2 of 4 drafted tokens accepted per pass); n_max 8 only adds wasted drafts. On the Mac, speculation is 0.57x (n_max 4) and 0.38x (n_max 8) of the baseline tok/s: the CPU verify batch is not free and the draft adds overhead, so the formula below is, if anything, optimistic for the A15 (4 threads, 2xA76 + 6xA55).

## 4. A15 projection (criterion formula)
speedup per target pass = (accepted + 1) / (1 + n_max * c), c = draft / target per-token cost. A15 decode is memory-bandwidth bound (2.33 tok/s), so **c = weight-byte ratio** = 639.4 MB / 2497.3 MB = **0.256** (Qwen2.5-1.5B would be 0.395). Check on the Mac, each model decoding alone (10 prompts, greedy): 4B 25.4 tok/s, 0.6B 91.0 (c = 0.280), 1.5B 65.6 (c = 0.388), consistent with the byte ratios. Range c +-50 % = 0.128 / 0.256 / 0.384.
Budget model: `device/tools/a15_budget.py`, cut 5 = cut 4 + gate skip + nosrc KV (warm, central: gen-item p50 **62.0 s**, mean decode **29.5 s** = 68.7 tokens / 2.33 tok/s). Each of the 100 generating items' decode time is divided by its own speedup (accepted/pass of the same item id in the s44 replay; s45 items reuse that id); pooled speedups below.

| config (engine sampler) | c | pooled speedup | decode saving | decode s saved (mean / item) | gen-item p50 total |
|---|---|---|---|---|---|
| 0.6B, n_max 4 | 0.128 (c -50 %) | 1.461 | 31.5 % | 9.2 s | 62.0 -> 53.5 s |
| 0.6B, n_max 4 | **0.256 (central)** | **1.091** | **8.4 %** | **2.4 s** | **62.0 -> 59.7 s (-2.3 s)** |
| 0.6B, n_max 4 | 0.384 (c +50 %) | 0.871 | **-14.8 %** | -4.5 s | 62.0 -> 65.5 s |
| 0.6B, n_max 8 | 0.128 | 1.197 | 16.4 % | 5.0 s | 56.8 s |
| 0.6B, n_max 8 | **0.256** | **0.795** | **-25.8 %** | -7.4 s | 68.5 s |
| 0.6B, n_max 8 | 0.384 | 0.595 | -68.1 % | -19.8 s | 81.6 s |
Greedy-run acceptance gives 9.9 % (n_max 4, central) and -25.8 % (n_max 8), same picture (`data/res/projection.json`).
Not in the criterion formula, but real: the draft has to prefill the whole prompt (460 tokens on average; there is no restored KV for it). At c_pf = non-embedding parameter ratio 0.44/3.6 = 0.122 and the A15 prefill rate 11.94 tok/s that is **+4.7 s per model answer**, which turns the n_max 4 central saving into **-2.5 s** (p50) even before the c +50 % case.
Exploratory p_min 0.75 (n_max 4, central c): generalising the draft cost to the drafted tokens per pass gives 1.36x (26.6 % decode saving) only if the failed-p_min draft forwards are free; counting them (drafted + 1 forwards) it is **1.13x (11.5 %)**, 0.97x at c +50 %; then the draft prefill (+4.7 s) cancels it. It also fails G1 (19/50 greedy). Not a candidate.

## 5. Gates
| gate | bar | result | verdict |
|---|---|---|---|
| G1 identity | >= 58/60 greedy (the 10 non-model items are trivially identical, so >= 48/50 model items) | **21/50 (n_max 4), 26/50 (n_max 8)** greedy = 31/60, 36/60; engine sampling 9/50, 14/50. Control-vs-control rerun: **50/50** identical (the sampler is deterministic with a seed), so the diffs are NOT sampling nondeterminism. Explained, not excused: every first divergence sits at a low-margin token of the non-speculative greedy run (top1-top2 logprob gap median 0.12-0.18 nats, 83-92 % <= 0.5, all <= 1.0, while only 6.5 % of all tokens have a gap <= 0.5; `data/ties-output.txt`), i.e. argmax flips between a 5-token verify batch and single-token decode. Under engine sampling the speculative sampler consumes the RNG differently, so identity is not expected there at all. | **FAIL** |
| G2 projected A15 decode saving | >= 20 % at central c and >= 0 at c +50 % | n_max 4: **8.4 %** central, **-14.8 %** at c +50 % (greedy acceptance: 9.9 % / -12.9 %); n_max 8: -25.8 % / -68.1 % | **FAIL** (both clauses) |
| G3 added RAM | <= 1.0 GiB (draft weights + draft KV) | weights 0.595 GiB + draft KV (28 layers x 8 KV heads x 128 x 2 (K,V) x 2 B = 114,688 B/token, n_ctx = target's 4096) 0.4375 GiB = **1.033 GiB** at f16 (0.924 GiB at n_ctx 3072; 0.828 GiB with `spec_draft_cache_type_k/v: 'q8_0'`). Measured server RSS +1.14..1.39 GB (includes the draft compute buffers). | **FAIL** as built (marginal on the formula, clear on RSS) |
| G4 llama.rn path | separate draft works with our init path, params listed, no engine code change beyond passing them | **No.** See below. | **FAIL** |

### G4: llama.rn 0.13.0-rc.4 (`wt/cut5lite/node_modules/llama.rn`, vendored llama.cpp b11010, same as the server build)
- JS (`src/types.ts`, `src/index.ts`): `NativeSpeculativeType = 'none' | 'draft-mtp' | 'mtp'`. `initLlama` forwards `model_draft` / `draft_model` (file path, `is_model_draft_asset` on iOS) and `speculative` (bool | type | object) / `spec_type` / `spec_draft_n_max|n_min|p_min|p_split|n_gpu_layers|cache_type_k|cache_type_v`; per completion `speculative` / `spec_type` / `spec_draft_n_max|n_min|p_min|p_split`; the completion result has `draft_tokens`, `draft_tokens_accepted`. Our `LlamaEngine.load` calls `initLlama({model, use_mmap, use_mlock:false, n_ctx, n_threads, n_gpu_layers:0})` through `initWithCpuFallback`, so passing the params is a trivial JS change.
- Native (`cpp/jsi/JSIParams.cpp`, `cpp/rn-llama.cpp:574`, `cpp/rn-completion.cpp:640-900`, `cpp/rn-slot.cpp:334`): **the only speculative path is `COMMON_SPECULATIVE_TYPE_DRAFT_MTP`**. The draft model is loaded only when the type list contains draft-mtp; `shouldUseMTP()` is the only switch into the draft/verify loop; `createMTPDraftContext` builds the draft context with `ctx_type = LLAMA_CONTEXT_TYPE_MTP`, `ctx_other = target ctx`, and `llama_init_from_model` returns null for a model without MTP layers (`llama-context.cpp:3773`: "context type MTP requested but model doesn't contain MTP layers"). So:
  - `spec_type: 'draft-mtp'` + `model_draft: Qwen3-0.6B`: model loads, then **every completion throws** "failed to create MTP draft context".
  - `spec_type: 'draft-simple'` (accepted by the native name parser, rejected by the TS type): `shouldUseMTP()` is false, `model_draft` is ignored, **speculation silently never runs**.
- The vendored common code does contain `draft-simple` (`common_speculative_state_draft`), and `refillMTPTokens` is generic draft/verify/accept code, but nothing in rn selects it. Making it work = a native patch: load the draft model and create a plain `llama_context` (no MTP type, no `ctx_other`, n_ctx = target's) for `draft-simple`, route `shouldUseMTP`/`initMTP` in rn-completion.cpp and rn-slot.cpp to it, check vocab compatibility, decide how the draft context is primed when the target prefix comes from `loadSession` (BOAR's gate / answer / `.nosrc` KV restores do not restore the draft, so the draft would prefill ~460 tokens, +4.7 s above), then rebuild the 7 arm64 `jniLibs` variants with the NDK (and iOS). That is a llama.rn fork, not "pass the params".
- The params that would be needed (what the server ran): `model_draft: <Qwen3-0.6B-Q8_0 path>`, `spec_type: 'draft-simple'`, `spec_draft_n_max: 4`, `spec_draft_n_min: 0`, `spec_draft_p_min: 0`, optional `spec_draft_cache_type_k/v: 'q8_0'` (cuts the draft KV to 0.23 GiB), `n_gpu_layers: 0`.

## 6. Decision
- **Do not run a device day for speculative decoding with these drafts.** G1 fails by a wide margin (identity 31/60 vs 58/60), the central saving is 8 % (bar 20 %) and negative at c +50 %, the draft prefill costs more than the decode it saves, and llama.rn cannot run a plain draft without a fork. Qwen2.5-1.5B is incompatible with the 2507 vocab in llama.cpp's check.
- What would have to change for this lever to come back: a draft with acceptance >= ~60 % at n_max 4 (a Qwen3-4B-2507-distilled 0.5B-1B, or the 4B's own MTP head if one is ever released: that is the one path llama.rn already supports, and it needs no second model), and an identity budget that allows near-tie flips (a quality-neutral but not text-identical arm would need the judge). Untested here: ngram / prompt-lookup types (`ngram-*` exist in b11010; llama.rn exposes none of them), they would not add RAM.
- Cleanup: Qwen3-0.6B GGUF deleted on the mini; no llama-server of ours left (ports 8187, 8188, 8094 checked); Qwen2.5-1.5B (kit) untouched.

## 7. Deviations and notes
1. Replay through the server backend (gate-less) rather than the node backend; prompt text is backend-independent and the answers match the stored node run 50/50.
2. 50 model-path prompts, not 60; the G1 bar is translated (>= 48/50 model-path items = >= 58/60 with the 10 non-model items identical by construction).
3. Only Q8_0 exists in the official Qwen3-0.6B-GGUF repo; Q4_K_M not tested (it would cut c to about 0.16 and weights to about 0.35 GiB, but acceptance is a property of the model, not the quant, so the 31 % stands; I did not requantize: not an official download).
4. `--draft-max` of the task text is `--spec-draft-n-max` in b11010.
5. Qwen2.5-1.5B: refused, the 4 runs executed without speculation (kept in `data/res/q15*` for the record, excluded).
6. Added beyond the criterion (descriptive): greedy twin runs, p_min 0.75 runs (exploratory), measured c, logprob tie analysis (`res_lp`), draft-prefill caveat. None of them changes a verdict.
7. Mac timings are descriptive only (shared host, load 3-6). A15 numbers are projections with the cut 4 desktop trace lengths and the A15 smoke rates (prefill 11.94, decode 2.33 tok/s); nothing was measured on a phone.
8. Housekeeping: my first matrix launch lost its configs after the first newline (fish) and was killed after 2 minutes; the one orphaned llama-server it left was stopped by port, and the matrix was relaunched. A first `extra.sh` `timeout` call failed (not on macOS); the q15 verbose start was re-run by `tools/q15-verbose.sh`.

Files: `tools/` (dl.sh, specdec-capture.sh, specdec-run.sh, specdec-extra.sh, specdec-lp.sh, q15-verbose.sh, specdec_replay.py, specdec_analyze.py, specdec_project.py, specdec_ties.py), `data/` (prompts, requests, traces, `res/`, `res_c/`, `res_lp/`, `analysis-output.txt`, `projection-output.txt`, `ties-output.txt`).
