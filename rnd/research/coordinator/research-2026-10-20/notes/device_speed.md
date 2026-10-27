# Device speed: 1-2B LLM + retrieval on Pixel 8a (Tensor G3) and similar SoCs

Angle: fastest runtime and backend for a ~1.7B model on a Google Tensor G3 phone (llama.cpp CPU/GPU, LiteRT-LM, MediaPipe, ExecuTorch, MLC, NPUs, speculative decoding, prefill). Date of search: 2026-10-20.

## Bottom line (TL;DR)

- No primary, reproducible tok/s number for a 1-2B model on a Pixel 8 / 8a / Tensor G3 exists in what I could reach. Every Tensor G3 number below is either a third-party blog with no methodology or a different phone.
- The one unexplored lever with real evidence is the GPU path on the Tensor G3 (Mali-G715) via LiteRT-LM (OpenCL). On a 2025-2026 Snapdragon, the same Qwen3-1.7B LiteRT file decodes ~5x faster on GPU than on CPU (community measurement). Whether Mali behaves the same is unknown.
- llama.cpp's documented GPU OpenCL path lists only Qualcomm Adreno as verified. Mali is not listed. Treat llama.cpp GPU on the 8a as unverified.
- No public API gives third-party apps the Tensor G3 TPU. AICore serves Gemini Nano only. The NPU path is closed for BOAR.
- Speculative decoding: no on-phone evidence for llama.cpp at 1.7B. Blog claims of 2-3x are unverified. Low priority.

## Our reference point (from the task brief, not re-measured here)

- Qwen3-1.7B Q4_K_M, llama.cpp CPU on Pixel 8a: 12-16 tok/s decode (brief).

## Findings

### F1. Qwen3-1.7B LiteRT-LM community measurement, GPU vs CPU (Snapdragon 8 Elite Gen 5, not Tensor)

Source: https://huggingface.co/litert-community/Qwen3-1.7B (fetched 2026-10-20). License: apache-2.0 (per card).

- Device: Samsung Galaxy S26 (SM8850, Snapdragon 8 Elite Gen 5, Android 16). Tool: litert_lm_advanced_main from litert-lm v0.16.0 with --benchmark, 205-token prompt (202 tokens with this tokenizer). Values are ranges over two runs.
- File wi4b32 (dynamic_wi4b32_afp32, 932 MB, context 4096):
  - GPU (OpenCL): prefill 532-568 tok/s, decode 40.5-40.7 tok/s, TTFT 0.38-0.40 s, peak RSS 1036 MB. Card says decode 994/994 ops delegated to LITERT_CL.
  - CPU (XNNPACK): prefill 48-76 tok/s, decode 8.0-8.3 tok/s, TTFT 2.8-4.3 s, peak RSS 2523 MB.
- File wi8 (2.1 GB):
  - GPU: prefill 312-504, decode 14.9-18.1, TTFT 0.46-0.71 s, RSS 854 MB.
  - CPU: prefill 238-245, decode 7.7-7.8, TTFT 0.95-0.98 s, RSS 3185 MB.
- Quality (card, 100 MMLU questions): int8 72, BF16 ~70, int4 mixed 64. Card calls these community measurements, not official.
- Caveat: the card says the benchmark used litert-lm 0.16.0 but the files need 0.18.0 or newer. The card does not address that.

Meaning: for this exact model class, the GPU delegate is roughly 5x decode and ~7x prefill over the CPU path on the same device. The S26 is far faster than the 8a, so absolute numbers do not transfer. The GPU/CPU ratio is the thing to test on the 8a.

### F2. Gemma 3 1B on LiteRT / MediaPipe, Samsung S24 Ultra (Snapdragon 8 Gen 3)

Sources:
- https://huggingface.co/litert-community/Gemma3-1B-IT/blob/main/README.md (fetched)
- https://developers.googleblog.com/gemma-3-on-mobile-and-web-with-google-ai-edge/ (dated 2025-03-12, fetched)

Numbers (S24 Ultra, performance governor, int4 QAT unless noted):
- MediaPipe CPU int4 block128, ctx 1280: prefill 138, decode 50, TTFT 2.33 s, CPU mem 982 MB.
- MediaPipe CPU int4 QAT, ctx 2048: prefill 322, decode 47.
- MediaPipe CPU int8, ctx 1280: prefill 177, decode 33.
- MediaPipe CPU fp32: prefill 49, decode 10.
- MediaPipe GPU int4 QAT, ctx 2048: prefill 2585, decode 56, TTFT 4.50 s.
- MediaPipe GPU int8, ctx 1280: prefill 1191, decode 24.
- LiteRT-LM CPU int4 QAT, ctx 2048: prefill 379, decode 55.
- LiteRT-LM GPU int4 QAT, ctx 2048: prefill 2531, decode 49.
- Google blog: "At only 529MB in size, Gemma 3 1B runs at up to 2585 tok/sec on prefill via Google AI Edge's LLM inference." Decode figures are in screenshots only. Device note: "at least 4GB of memory."
- The card says "All benchmark stats are from a Samsung S24 Ultra." The page says CPU uses the XNNPACK delegate with 4 threads.
- NPU (S25 Ultra, LiteRT-LM, a16w4 QAT, ctx 1280): prefill 5836, decode 85, RSS 626 MB CPU + 689 MB GPU.

Meaning: on this family, the GPU delegate lifts prefill by ~6-7x and decode is about equal (49-56 vs 47-55). Prefill speed matters for RAG context (a 1000-token knowledge chunk is about 0.4 s prefill on the GPU vs 2.6-3 s on the CPU at these rates). Decode speed is roughly the same, so the GPU path mainly helps time-to-first-token on long prompts.

Licence: Gemma terms ("License: gemma" on the card; gating requires accepting Gemma terms). Not Apache. Redistribution needs checking under the Gemma terms, not just the licence name.

### F3. Qwen3-1.7B on Qualcomm GENIE (NPU) and GENIEX llama.cpp, Snapdragon-only

Source: https://huggingface.co/qualcomm/Qwen3-1.7B (fetched). License: apache-2.0 (the original Qwen3 licence is linked from the card's LICENSE file).

Selected rows (w4a16 GENIE, 4096 context):
- Snapdragon 8 Elite Gen 5 For Galaxy: 58.30 tok/s, TTFT 0.029-0.926 s.
- Snapdragon 8 Elite For Galaxy: 56.73 tok/s.
- Snapdragon X2 Elite: 71.54 tok/s.
- GENIEX_QAIRT, Snapdragon 8 Elite Gen 5 For Galaxy: 25.14 tok/s at ctx 512; 21.22 tok/s at ctx 4096.
- GENIEX_LLAMACPP (q4_0): Snapdragon 8 Elite Gen 5 For Galaxy, ctx 4096: 22.86 tok/s, TTFT 0.058-1.868 s.

Meaning: the NPU path is roughly 2.5x decode over llama.cpp CPU/GPU on the same Qualcomm chip, but it is Qualcomm-only and the card says "Genie support will be deprecated soon." Not available to BOAR on Tensor G3. Useful only as a ceiling and to show what an NPU would buy.

### F4. Tensor G3 CPU/GPU llama.cpp estimate (third-party blog, unverified)

Source: https://www.ertas.ai/zh/blog/llm-android-benchmarks-snapdragon-tensor (dated 2026-04-01, fetched; Chinese).

Tensor G3 (Pixel 8, 8 Pro, 12 GB, Mali-G715), GGUF Q4_K_M, ctx 2048, llama.cpp, CPU (multithreaded) and Vulkan where available:
- 1B class token generation: CPU 25-32 tok/s; GPU/Vulkan 30-38 tok/s; memory ~800 MB.
- 3B class: CPU 12-16 tok/s; GPU/Vulkan 15-20 tok/s; memory ~2.2 GB.
- Same table lists Tensor G4 1B CPU 28-35, 3B CPU 14-20; Snapdragon 8 Elite 3B CPU 18-25.

Problems: no methodology, no run count, no prompt lengths, device rows labelled "representative devices" (not confirmed test units), no prompt-processing column, and the numbers look like ranges rather than measurements. The 3B CPU range (12-16) is near our own 1.7B measurement (12-16 on the 8a), so either the 8a is slower than a Pixel 8 or this table is optimistic. Do not quote it. Use it only as a hypothesis for the Vulkan vs CPU question, which is what we actually need to measure.

### F5. Tensor G3 GPU identity and llama.cpp GPU support

Sources:
- https://github.com/ggml-org/llama.cpp/blob/master/docs/backend/OPENCL.md (fetched). Verified GPUs listed are Adreno only: 750, 810, 830, 840, X1-85, X2-90. Mali is not mentioned. "A6x GPUs in phones are likely not supported." Every quant type (Q4_0, Q4_K, Q6_K, ...) is marked as supported in the DataType table. No Android performance numbers. Known issue: "Flash attention does not always improve performance." TODO: "Improve OpenCL C kernels performance."
- Tensor G3 GPU per search snippets (not fetched): Notebookcheck says Mali-G715 MP7, OpenCL 2.0, Vulkan 1.1 (https://www.notebookcheck.net/ARM-Mali-G715-MP7-GPU-Benchmarks-and-Specs.762528.0.html). CPU-Monkey says Immortalis-G715 MP10, Vulkan 1.3 (https://www.cpu-monkey.com/en/igpu-arm_immortalis_g715_mp10). Sources disagree on core count.
- Notebookcheck places the G715 MP7 between Adreno 725 and Adreno 730 in synthetic tests.

Meaning: llama.cpp's OpenCL backend is not validated on Mali. A Vulkan build of llama.cpp exists but I found no Mali/Tensor llama.cpp Vulkan result. The LiteRT-LM GPU (OpenCL/ML Drift) path is the only GPU route with Android numbers, and none were found on a Mali device.

### F6. llama.cpp Android build docs: CPU-only acceleration

Source: https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md (fetched). Note: this page covers the Android binding. It names CPU acceleration only: "hardware acceleration up to SME2 for Arm and AMX for x86-64 CPUs"; KleidiAI optional for arm64-v8a. No OpenCL, Vulkan, or Hexagon notes. Recommended thread count not given. Build flag: GGML_NATIVE=OFF for cross-compilation. Do not add a global -march flag unless you want to raise the baseline.

Meaning: the Tensor G3 cores (Cortex-X3 / A715 / A510, from my own knowledge, not verified in this session) do not include SME2, so the KleidiAI SME2 kernels will not apply. Only the NEON/SVE2 CPU path applies. Test 4 vs 5 threads (the earlier LocalLLaMA hint, next item).

### F7. Thread count and repacked quants on Tensor G4 (community, anecdotal)

Source: search snippet from r/LocalLLaMA via a search result; primary URL not opened. Commenter on Pixel 9 Pro (Tensor G4), Llama-3.2-3B Q4_K_M: about 12 tok/s generation, about 9 without SVE compilation. Notes that Q4_0_4_8 repacking beat Q4_K_M on pp512 and that the G3 may do better with 5 threads than 4 (more performance cores on the G3). Anecdotal; the G4 is a different chip.

Meaning: our Pixel 8a sweep should include 4 vs 5 threads and an SVE-compiled build. Treat as a cheap hypothesis, not a finding.

### F8. "Is Your NPU Ready for LLMs?" measurement study (2026)

Source: https://arxiv.org/abs/2607.05475 (abstract fetched). Authors: Cai, Tian, Yang, Ren, Yuan, Li, Wang. ACM MACO vol. 10 no. 3 (DOI 10.1145/3857370). Licence: CC BY 4.0 (per PDF metadata). The PDF text was unreadable in the fetch, so device, SoC, and model details are unverified.

Abstract claims (quoted paraphrase):
- Cross-layer study of five frameworks on three backends (CPU, GPU, NPU), with a profiler called PowerBench. Names llama.cpp and GENIE as examples.
- Framework gaps "reaching up to 10x" on NPUs.
- NPUs best for compute-bound prefill; CPUs outperform the other backends for memory-bound decode.
- CPU frequency tuning cuts energy by up to 39.7%; an energy-oriented NPU configuration by up to 53.2%.

Meaning: supports the decode-is-bandwidth-bound view. For BOAR, the decode speed of a 1.7B model on CPU is close to the memory-bandwidth ceiling, so faster decode from the CPU alone is unlikely. Prefill (RAG context ingestion) is where a GPU or NPU delegate would matter. Needs the full text to use numbers.

### F9. mllm-NPU: NPU offload for prefill (2024, older)

Source: https://arxiv.org/abs/2407.05858 (abstract fetched). Title "Fast On-device LLM Inference with NPUs", Xu et al., v1 2024-07-08, v2 2024-12-15. Claims 22.4x faster prefill and 30.7x energy saving on average; "more than 1,000 tokens/sec prefilling for a billion-sized model"; end-to-end up to 32.8x in one app. The page does not list devices or models in the abstract (Gemma-2B named only as an example). Hardware not verified. Two years old and not on Tensor. Useful as background only.

### F10. PELM: speculative decoding with DVFS on-device (2026)

Source: https://arxiv.org/abs/2609.09662 (abstract fetched). Submitted 2026-09-09, SenSys'26. Claims "up to 23.1% speedup" and "52.4% reduction in energy consumption" with "comparable task performance." Uses self-speculative decoding (a truncated target model as draft) rather than a separate draft model. Device, SoC, model sizes not in the abstract; not verified.

Meaning: the only on-device speculative decoding number I found, and it is modest (+23%) and unverified on a phone like ours. Lower priority than the GPU path.

### F11. Speculative decoding in llama.cpp and mobile (weak evidence)

- llama.cpp examples/speculative README (fetched): only says "Demonstration of speculative decoding and tree-based speculative decoding techniques" and links PRs #2926, #3624, #5625. No speedups, no draft-vocabulary rule, no mobile mention.
- Search snippets: an Android tutorial pairs Qwen 0.5B draft with a 7B target and reports "40+ tokens/sec on a Pixel 9" and "2-3x" speedup (dev.to, not verified). Blog posts repeat 2-3x without data.
- arXiv 2403.00858 (Direct Alignment of Draft Model, 2024): argues small draft models for edge devices are missing. Not a phone benchmark.

Meaning: no credible number for a 1.7B target with a sub-1B draft on a Tensor phone. Only worth testing after the GPU path, and it would need a draft with the same vocabulary.

### F12. Qwen3-1.7B on other phones (anecdotal, for scale only)

- DakeQQ Native-LLM-for-Android (project page; fetched only as a search snippet): Qwen3-1.7B q4f32 ~37 tok/s on a Vivo X200 Pro (MediaTek Dimensity 9400), CPU. Speed varies with device, backend, quantisation.
- Qualcomm GENIEX_LLAMACPP row above (F3).

### F13. Google Tensor TPU / NPU access

Source: search results only (AICore docs at d.android.com/ai/aicore not fetched; GrapheneOS forum thread at discuss.grapheneos.org/d/41853 not fetched).
- AICore: system service giving apps access to Gemini Nano only, text only. Listed devices included Pixel 8 Pro, and the search did not show a Tensor G3 or Pixel 10 entry.
- The GrapheneOS thread (anecdotal) says apps on Pixel 10 Pro Fold fall back to CPU for local LLMs; the TPU path is limited to privileged Google apps.
- No public SDK for third-party LLM inference on the Tensor G3 TPU was found.

Meaning: the Tensor G3 NPU is closed for BOAR. The only fast paths are CPU (llama.cpp / LiteRT XNNPACK) and GPU (LiteRT OpenCL, Mali, untested).

### F14. LiteRT-LM runtime: platform and licence

Source: https://github.com/google-ai-edge/LiteRT-LM (fetched). Licence: Apache-2.0 (sidebar). Platforms: Android, iOS, Web, Desktop, IoT. GPU and NPU acceleration; CPU is not named as a backend in the README. Model format .litertlm. No benchmark table in the README; points to a technical overview.

Also from the blog (https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/, dated 2026-05-19): Gemma 4 E2B on Android GPU (OpenCL): decode 52 tok/s (device not named). Samsung S26 Ultra GPU: up to 2.2x decode with MTP. Pixel and Tensor are not mentioned in the post. Licence: "fully open-source iOS Swift API"; no licence name given in the text.

### F15. Gemma 4 E2B on Samsung S26 Ultra (LiteRT-LM, from search snippet)

Official-looking figures (secondary, via a search snippet of the Hugging Face card): CPU prefill 557 / decode 46.9; GPU prefill 3808 / decode 52.1 tok/s. Newer model and newer SoC; not usable for the 8a directly. Snippet not fetched; treat as secondary.

## Searched and not found

- Any Pixel 8 / 8a / Tensor G3 LiteRT-LM or MediaPipe benchmark with prefill, decode, or TTFT.
- Any Pixel 8 / 8a llama.cpp Vulkan or OpenCL benchmark (Mali-G715).
- Any Qwen3-1.7B measurement on a Tensor chip, on any backend.
- A Tensor G3 TPU or NPU route for third-party LLMs (AICore is Gemini Nano only).
- A 2025-2026 llama.cpp speculative-decoding phone benchmark with a 1-2B target.
- A readable table of the 2607.05475 study (PDF text did not extract).
- ExecuTorch, MLC-LLM, and Qualcomm/MediaTek NPU phone numbers for 1-2B models were not searched in depth (only the Qualcomm card and the 2607 abstract). MLC-LLM and ExecuTorch were not checked at all; this is a gap.

Search depth: 13 WebSearch standard queries, about 25 WebFetch calls. No extended searches run.

## What this means for BOAR

1. Test the LiteRT-LM GPU path on the 8a first. Concrete check: Qwen3-1.7B LiteRT file (dynamic_wi4b32_afp32, 932 MB, Apache-2.0 card) on the Pixel 8a with --benchmark (or Google AI Edge Gallery), CPU vs GPU, 205-token prompt, 5 runs, report prefill, decode, TTFT, RSS. Expected from the S26 ratio: a GPU speedup, but the Mali-G715 may fall far short of the Adreno 830. Pin the litert-lm version (the card needs 0.18.0 or newer).
2. Test llama.cpp CPU thread counts 4 vs 5 and Q4_K_M vs Q4_0_4_8 (if SVE build works on Tensor G3) before changing the engine. Cheap, no new dependency.
3. Do not spend on llama.cpp OpenCL for the 8a. It is not verified for Mali. A Vulkan build is possible but has no Mali data; test only after step 1 if GPU helps.
4. Do not pursue the Tensor NPU, speculative decoding, or GENIE. No access, no evidence, or Qualcomm-only.
5. Speed is not the reading wall. The brief says the 1.7B does not use retrieved text (dU -0.004 to -0.012). A 2x faster decode does not fix that; only prefill matters if it lets more context fit in the time budget. So the GPU test buys latency and maybe a larger context, not accuracy. Be explicit about that in any plan.
6. Licence check for the Gemma family (if BOAR ever moves to Gemma 3 1B / 4 E2B for speed): Gemma terms, not Apache. Qwen3-1.7B is Apache-2.0, which allows redistribution.

## Load-bearing (for the structured output)

- F1 (LiteRT-LM GPU vs CPU for Qwen3-1.7B): could change the next engine test.
- F2 (Gemma 3 1B LiteRT: GPU prefill ~6-7x CPU, decode equal): changes how we weigh prefill vs decode.
- F8 (2607.05475: CPU best at decode, NPU at prefill): explains why decode is stuck near bandwidth limits.

Not load-bearing: F4 (unverified blog), F5/F6 (llama.cpp GPU/CPU facts, useful but do not change the plan by themselves), F7-F13 (anecdotal or closed paths).

## Sources opened (URL list)

- https://huggingface.co/litert-community/Qwen3-1.7B
- https://huggingface.co/litert-community/Gemma3-1B-IT/blob/main/README.md
- https://developers.googleblog.com/gemma-3-on-mobile-and-web-with-google-ai-edge/
- https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/
- https://huggingface.co/qualcomm/Qwen3-1.7B
- https://www.ertas.ai/zh/blog/llm-android-benchmarks-snapdragon-tensor
- https://github.com/ggml-org/llama.cpp/blob/master/docs/backend/OPENCL.md
- https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md
- https://github.com/ggml-org/llama.cpp/blob/master/examples/speculative/README.md
- https://github.com/google-ai-edge/LiteRT-LM
- https://arxiv.org/abs/2607.05475 (abstract only; PDF unreadable)
- https://arxiv.org/abs/2407.05858
- https://arxiv.org/abs/2609.09662
- Search-snippet sources (not opened): notebookcheck and cpu-monkey Mali pages, the GrapheneOS thread, the AICore docs, the r/LocalLLaMA Pixel 9 Pro thread, the dev.to speculative tutorial.
