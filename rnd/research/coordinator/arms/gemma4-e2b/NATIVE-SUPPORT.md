# GEMMA4-E2B: does the native app / bench-app engine support it? (read-only check, 2026-10-21)

TL;DR: YES for both. The native app's llama.cpp pin and bench-app's llama.rn vendor the SAME commit 4bc272fd (= tag b11010, the build the desktop screens ran on). No engine bump needed. App-side blockers are small (catalog entry, a Gemma-sized prompt tier, bench-app BENCH_MODELS entry). Gemma 4 E4B is already in the app maintainer's catalog and documented as "loads and answers".

## Evidence: llama.cpp 4bc272fd
- 4bc272fd729bd094c0422e4b8353da8d2fec91f8 = "vulkan: work around NV bug with argsort_large.comp (#28975)", 2026-09-16. `git tag --contains` gives b11010 as the first tag containing it; `git rev-list --count 4bc272fd..b11010` = 0, so the pin IS b11010 (same as the desktop screens).
- Arch registered: src/llama-arch.cpp:59 `LLM_ARCH_GEMMA4 -> "gemma4"` (also :60 gemma4-assistant); src/llama-arch.h:64.
- Per-layer embeddings (E2B/E4B PLE): src/llama-arch.cpp:195 `embedding_length_per_layer_input`, :559-566 `per_layer_token_embd`, `per_layer_model_proj`, `per_layer_proj_norm`, `inp_gate`, `proj`, `post_norm`; src/models/gemma4.cpp:17 reads n_embd_per_layer, :57-60 creates the PLE tensors (token table loaded with TENSOR_READ_LAZY, so it is not forced resident).
- Date vs support PR: gemma-4 work in upstream log starts 2026-04-02 (5208e2d5b "fix: gemma 4 template", b069b10ab tokenizer fix 04-03, 650bf14eb softcap 04-04, b8635075f chat parser 04-04). The pin is 5.5 months after launch. (The arch-add commit itself could not be resolved in the blobless clone; not needed.)
- Later gemma4 fixes are all BEFORE the pin: e62fa13c2 shared-KV tail attn_k optional on load (04-10), d9a12c82f remove `</s>` eog (04-08), 3fc65063d template align (04-10), d7ff074c8 reasoning budget sampler (04-10), eeeaf6180 null-buffer crash in iswa attn for SWA-only models (05-21), 994118a18 per-model load_hparams (05-04), 04eb4c446 Gemma4 MTP (06-07).
- Gemma4 commits between pin and b11010: none (0 commits). Later gemma4 commits on master (after b11010) were not audited; all upstream fixes through the pin date are included.

## Evidence: native app (UPSTREAM_REPO/boar-app fullnative-dev, tip 0be84acd)
- Submodule: `git ls-tree HEAD android-native/engine/src/main/cpp/llama.cpp` = 160000 4bc272fd729bd094c0422e4b8353da8d2fec91f8.
- JNI is template-agnostic: android-native/engine/src/main/cpp/boar_jni.cpp:207 `common_chat_templates_init(model, ...)`, :246-271 formatChat uses `common_chat_templates_apply` with `enable_thinking`, returns thinking tags and `additional_stops` from llama.cpp's own per-model parser. No Qwen strings in the JNI. EOG via `llama_vocab_is_eog` (:335); n_gpu_layers = 0 (:161) so CPU only (matches our desktop CPU screens).
- Thinking handling already knows Gemma 4: engine/.../answer/AnswerText.kt:10,29 markers `<|channel>thought` ... `<channel|>`; AnswerPipeline.kt:85-90 passes enableThinking = user tweak (off by default) through formatChat, so Gemma gets no `<|think|>` in the render (same as our ONBOARDING).
- Arch allowlist: engine/.../models/HfQuery.kt:32-33 CHAT_ARCHITECTURES contains "gemma4" (and excludes gemma4-assistant, correct).
- Precedent: docs/MODELS.md:106 and src/models/manifest.ts:209-216 (RN) and app catalog.json:117-124 list Gemma 4 E4B QAT Q4_0 "loads and answers; not benchmarked yet".
- Only Qwen-specific text: Personalities.kt:50 comment (the "small model" tier is a file-size threshold, not name based) and DefaultModel.kt:25 (default-tier comment). Nothing blocks loading.

## Evidence: bench-app
- bench-app/node_modules/llama.rn 0.13.0-rc.4; vendor/VERSIONS:8-9 `LLAMA_CPP_REF=b11010`, `LLAMA_CPP_COMMIT=4bc272fd729bd094c0422e4b8353da8d2fec91f8`; vendor/llama.cpp/src/llama-arch.cpp:59 has gemma4. So the Pixel bench can load Gemma 4 E2B on the engine code path used for Qwen3-1.7B (the shim wraps llama.rn: src/llamaRnShim.ts:26-33).
- Needed in bench-app: a BENCH_MODELS entry (src/benchModels.ts:16-33, side-loaded, sizeBytes + sha256 from the unsloth file 740185b2...4b8b, `usesChatTemplate: true`). Do NOT copy `thinkingOff: true` blindly: it deletes thinking_* params and sets enable_thinking:false (benchModels.ts:50-61), which is right for Qwen3 hybrid but for Gemma 4 the verified render is "no `<|think|>`"; confirm the llama.rn request builds that prompt (check one rendered prompt in the bench log) before a scored run.

## Residual risks (not blockers, unmeasured on a phone)
1. Memory: E2B Q4_K_M has a large PLE token table (lazy-read, mmap) so RSS vs file size differs from Qwen3-1.7B; LoadGuard.kt thresholds are file-size based. Measure PSS on the Pixel 8a.
2. Gemma 4 sampling/stop behaviour: relies on llama.cpp's gemma4 chat parser (`additional_stops`), exercised by the app's own formatChat; one on-device answer needed to confirm no stray `<end_of_turn>`/channel text.
3. Our arm's retrieval/prompt patch (gemma4-e2b.patch) lives on the cut-7 TS engine; the native Kotlin port would need the same prompts (AnswerPipeline/Personalities) applied for parity, outside this check.

## What the app maintainer would need to change (minimum)
1. Add `gemma-4-e2b-it-q4_k_m` to catalog.json (unsloth GGUF, sha256 740185b2...4b8b, Apache-2.0) and set it as the 8 GB default only if the on-device PSS/latency pass.
2. Keep enableThinking=false default for it (already the app default); no engine/submodule bump.
3. Optional: mark it in DefaultModel/Personalities tier so the "small" prompt is used (size-based, probably automatic at ~3.1 GB? verify, since Gemma E2B file is larger than Qwen3-1.7B's 1.1 GB).

## Draft note to the app maintainer (NOT SENT)
Your llama.cpp pin (4bc272fd = b11010) already supports gemma4 incl. per-layer embeddings; your HfQuery allowlist and AnswerText already handle it, and E4B is in your catalog.
We would like gemma-4-E2B-it Q4_K_M (unsloth, Apache-2.0) added to catalog.json as an 8 GB candidate: no engine change, thinking stays off via enableThinking=false.
Could you run it once on a device (PSS after load, one answer with sources) and tell us if the "small model" prompt tier still applies at ~3 GB file size?
