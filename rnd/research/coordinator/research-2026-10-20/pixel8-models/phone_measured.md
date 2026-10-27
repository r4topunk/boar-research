# Measured on-device numbers, 8 GB-class Android, 1.5B to 8B models

Date: 2026-10-20. Angle: measured tok/s, TTFT, peak RAM on phones (ideally Tensor G3/G4 or Snapdragon 8 Gen 2/3). Sources opened in this run are marked [opened]. Search-snippet-only sources are marked [snippet]. Vendor or forum claims are marked [vendor] or [forum].

## TL;DR

- No opened source gives a measured Pixel 8 (Tensor G3) llama.cpp number for any model in the 1.5B to 8B band. The only Tensor G3 row is a vendor table with no method (Ertas, [vendor], unverified). The only Pixel 8 llama.cpp datapoint is a Reddit anecdote, 7.8 tok/s for Llama-3.2-3B Q4 ([snippet]).
- The most relevant opened measurements for a phone-class CPU: SmolLM3-3B on a Galaxy S26 (LiteRT-LM CPU, decode 9.6 to 11.5 tok/s, peak 3.12 to 4.36 GB), Gemma 3n E4B on a Pixel 9 Pro XL (decode 5.72 tok/s, prefill 35.0 tok/s, TTFT 7.5 s, runtime unstated), and Gemma 3n E2B on a Galaxy S24 Ultra CPU (decode 16.1 tok/s, prefill 110.5 tok/s).
- Qualcomm AI Hub has llama.cpp-backed rows (GENIEX_LLAMACPP, q4_0) for Phi-4-mini on Snapdragon 8 Elite and 8 Elite Gen 5. These are newer chips than 8 Gen 2/3, so use them only as an upper bound.
- For the SD 865 (8 GB), the HF dataset dispatchAI/on-device-latency has llama.cpp rows for 1.5B to 3.8B models. It labels them "estimated benchmarks based on model architecture, parameter count, and quantization level", so they are not measurements despite the dataset intro saying "measured on actual phone hardware". Treat them as rough guides.
- Memory is the weakest evidence. Only two opened sources give peak RAM at all (SmolLM3 LiteRT card), and neither is llama.cpp.

## Measurement rows

### R1. Gemma 3n E2B (LiteRT-LM, int4 weights) [opened]
- Source: https://huggingface.co/google/gemma-3n-E2B-it-litert-lm (LiteRT-LM table)
- Samsung S24 Ultra CPU: prefill 110.5 tok/s, decode 16.1 tok/s
- Samsung S24 Ultra GPU: prefill 816.4, decode 15.6
- Vivo X300 Pro NPU: prefill 1671.3, decode 28.4
- MacBook Pro M3 CPU: prefill 232.5, decode 27.6
- Memory: not reported. Licence metadata: `gemma` (Gemma Terms of Use; the page requires accepting Google's licence to access)
- Runtime: LiteRT-LM, not llama.cpp. Card says the numbers are preliminary.

### R2. Gemma 3n E4B [opened, plus one forum source]
- Source: https://huggingface.co/google/gemma-3n-E4B-it-litert-lm (official table): S24 Ultra CPU prefill 73.5, decode 9.2; S24 Ultra GPU prefill 548.0, decode 9.4; MacBook M3 CPU 170.1 / 20.1.
- Pixel 9 Pro XL, E4B (HN comment, runtime not named, likely Google AI Edge Gallery): decode 5.72 tok/s, prefill 35.02 tok/s, first token 7.48 s, total latency 86.88 s. Quantization and memory not reported. Source: https://hn.nuxt.dev/item/44044199 [opened, forum]
- Pixel 6 Pro, E4B (same thread): about 4.4 tok/s decode on an image prompt, over 6 tok/s on text chat. Phone RAM 12 GB per the comment. [forum]
- Pixel Fold (same thread): 2.6 to 5.8 tok/s decode, GPU switched on mid-run; model variant not stated. [forum]
- Memory: not reported in any row. Licence: `gemma`.

### R3. Gemma 3 1B (int4 QAT) [opened]
- Source: https://developers.googleblog.com/gemma-3-on-mobile-and-web-with-google-ai-edge/
- Galaxy S24 Ultra, CPU or GPU (performance governor): prefill up to 2585 tok/s. Per-backend decode numbers are only in screenshots, not readable here.
- Model file 529 MB. Google recommends at least 4 GB RAM for best performance.
- Licence: Gemma terms (not checked on the HF card in this run).

### R4. Phi-4-mini 3.8B (Qualcomm AI Hub, GENIEX_LLAMACPP, q4_0) [opened]
- Source: https://huggingface.co/qualcomm/Phi-4-Mini-Instruct
- Snapdragon 8 Elite Gen 5 For Galaxy, context 512: decode 21.4, 23.0, 23.2 tok/s; TTFT 0.09 to 4.8 s
- Snapdragon 8 Elite Gen 5 For Galaxy, context 4096: decode 7.2, 11.0, 13.1 tok/s; TTFT 0.1 to 80.5 s
- Snapdragon 8 Elite For Galaxy, context 512: decode 18.5 to 22.3; context 4096: 6.9 to 10.3
- Memory: not published. Licence metadata: `mit`.
- These are 8 Elite, not 8 Gen 2/3. Use as an upper bound. The row structure is a 4096-context slowdown of about 2.3x.

### R5. Qwen3-4B (Qualcomm AI Hub, q4_0) [snippet, conflicting]
- Search snippet from the Qualcomm page lists Snapdragon 8 Elite Mobile, 512 ctx 22.3 tok/s, 4096 ctx 7.6 tok/s (https://app.alphaneural.io/assets/qualcomm/Qwen3-4B, [snippet]).
- The Qualcomm page itself (https://aihub.qualcomm.com/mobile/models/qwen3_4b, [opened]) says the model "is currently not supported on any Mobile chipset" and gives no rows. This conflicts with the snippet. Do not quote the 22.3 figure without a fresh check.
- Qwen3-4B is already screened (reference only).

### R6. Llama-3.2-3B Q4 on Pixel-class phones [mixed]
- Pixel 9 Pro (Tensor G4), llama.cpp contributor on r/LocalLLaMA, Nov 2024: tg128 about 12 tok/s for Q4_K_M; Q4_0_4_8 pp512 78.86 ± 1.06 tok/s on a build with the Tensor G4 repacking. [snippet, Reddit thread https://redlib.hbubli.cc/r/LocalLLaMA/comments/1glx6a5/phone_llms_benchmarks; the thread itself did not load in this run]
- Pixel 8 vs Pixel 7, same model: 7.8 tok/s vs about 7.5 tok/s (anecdote, Reddit, no build or thread counts). [snippet]
- Tensor G3 (Pixel 8), CPU 3B Q4_K_M: 12 to 16 tok/s, GPU/Vulkan 15 to 20, memory about 2.2 GB (Ertas vendor table, https://www.ertas.ai/blog/llm-android-benchmarks-snapdragon-tensor, [opened, vendor]). The page gives chip ranges only, no phone names or method. Its RAM column also lists the Pixel 8 at 12 GB, which conflicts with the 8 GB Pixel 8a in our target profile.
- Snapdragon 8 Gen 2 3B CPU 12 to 18 tok/s (same vendor table, [vendor]).
- SD 865 (S20 FE), dispatchAI dataset, estimated: Llama-3.2-3B Q5 7.7 tok/s; FP16 5.5 tok/s (https://huggingface.co/datasets/dispatchAI/on-device-latency, [opened, estimated]).
- Arm SME2 page, Llama-3.2-3B Q4_0, 1 thread, Arm C1 core, unnamed Android phone: pp 12.3, tg 9.1 tok/s with SME2; pp 7.9, tg 5.9 without (https://learn.arm.com/learning-paths/mobile-graphics-and-gaming/performance_llama_cpp_sme2/, [opened]). SME2 is not in Tensor G3 as far as this run found; verify on the device.

### R7. SmolLM3-3B (LiteRT-LM) [opened]
- Source: https://huggingface.co/litert-community/SmolLM3-3B; licence `apache-2.0`.
- Samsung Galaxy S26 (SM-S942Q, Android 16, SoC not stated; 2026 flagship, not 8 GB class):
  - CPU, file `SmolLM3-3B_q4_block32_ekv4096.litertlm`, 4 threads, XNNPACK: prefill 55.6 to 76.2, decode 11.49 tok/s, TTFT (1024 prompt) 13.5 to 18.5 s, init 2.59 s, peak 3.12 GB
  - CPU, file `SmolLM3-3B.litertlm`: prefill 157.6 to 174.3, decode 9.56 to 9.83, TTFT 6.0 to 6.6 s, init 7.04 s, peak 4.36 GB
  - GPU, q4 block32 file: prefill 372.5 to 383.2, decode 19.45 to 25.09, TTFT 2.7 s, peak 1.22 GB
  - GPU, plain file: prefill 221.3 to 458.5, decode 12.48 to 17.22, peak 1.00 GB
- iPhone 18 Pro (iOS 27): CPU decode 22.5 tok/s, GPU (Metal) 43.9; memory not measured (entitlement about 3.37 GB).
- Mac M4 Max (CPU 24.5 decode). Not a phone.
- Note: this is LiteRT-LM, not llama.cpp, and the CPU path reads a 3.1 to 4.4 GB peak, which is near the practical budget.

### R8. LFM2 / LFM2.5 family (Liquid AI) [opened, no numbers]
- LFM2-1.2B and LFM2-2.6B HF cards (https://huggingface.co/LiquidAI/LFM2-1.2B, https://huggingface.co/LiquidAI/LFM2-2.6B) give no on-device tok/s, device, runtime or RAM figures. Only an uncited claim "2x faster decode and prefill on CPU compared to Qwen3", with the chart as an image.
- Licence: `lfm1.0` / "LFM Open License v1.0". The revenue and commercial-use terms were not read in this run; check them before any redistribution.
- Snippet-only: "LFM2.5-230M on a Galaxy S25 Ultra CPU up to 213 tok/s decode" (Digg, secondhand). Different size, not in band.

### R9. Phi-3.5-mini 3.8B and Gemma-2-2B (SD 865, dataset, estimated) [opened, estimated]
- https://huggingface.co/datasets/dispatchAI/on-device-latency, S20 FE, SD 865, 8 GB, llama.cpp, 4 threads:
  - Phi-3.5-mini Q5 6.3 tok/s; FP16 4.5
  - Gemma-2-2B-IT Q5 11.2 tok/s; FP16 8.0
- Dataset licence: Apache-2.0. Labelled estimated.

### R10. Qwen2.5-1.5B-Instruct and SmolLM2-1.7B (SD 865, dataset, estimated) [opened, estimated]
- Qwen2.5-1.5B-Instruct: INT4 16.8 tok/s; Q5 14.7; Q8 12.6. (Proxy for Qwen3-1.7B, which is not in this dataset.)
- SmolLM2-1.7B-Instruct: Q5 12.6 tok/s; FP16 9.0.
- Same caveats as R9.

### R11. Qwen3-4B Q4_K_M on SD 865 (forum claim) [opened, forum, unverified]
- HF discussion https://huggingface.co/Qwen/Qwen3-4B/discussions/17: "~12-14 tokens/sec per device", 40 Samsung S20 FE phones, Q4_K_M. No methodology, prompts, context length or RAM. Post is from a company selling an on-device product. Do not quote as a measurement.

### R12. PrivateLoRA appendix, 7B, flagship phone (MLC Chat, 3-bit) [opened, reference only]
- https://arxiv.org/pdf/2311.14030 (text extracted locally): "a 3-bit quantized 7B model on a flagship smartphone achieves only 58.1 and 8.1 tokens per second for prefill and decode". Device memory bandwidth assumed 42.7 GB/s, 15.8 TFLOPS (Table 2).
- Use: decode is bandwidth-bound; for a 3B Q4 model of about 1.8 GB, this bandwidth implies roughly 2.3x the 7B-3bit decode speed in the ideal case. This is a scaling argument, not a measurement.
- The Xiaomi 13 attribution in a search snippet does not appear in the PDF text; do not quote it.

### R13. Snapdragon 8 Gen 2 llama.cpp CPU, 1B and 3B (Ertas, vendor) [vendor]
- 1B Q4_K_M: CPU 25 to 35 tok/s (vendor).
- 3B Q4_K_M: CPU 12 to 18 tok/s (vendor). Memory ~2.2 GB.
- Method not stated, "measured" label with ranges only. Use only as a band.

### R14. Snippet-only sources (not opened; listed for completeness)
- Qualcomm slide (2023 baseline): LLaMA-2 decode 6.4 tok/s on 8 Gen 3, 14.2 after optimisation (MLC-style, community baseline). [snippet]
- Cambricon-LLM paper: MLC-LLM 7.58 tok/s decode on Llama2-7B, Snapdragon 8 Gen 2. [snippet]
- Phi-4-mini on MediaTek Dimensity 9400: prefill >800, decode >21 tok/s (vendor claim, MediaTek). [snippet]
- LiteRT-LM SmolLM3 on iPhone 17 Pro (Metal): decode 22.5 tok/s (earlier card, superseded by R7). [snippet]

## Candidate map (for coordinator)

| Candidate | Best phone-class evidence in this run | Device class | Speed read | Licence |
|---|---|---|---|---|
| Qwen3-1.7B (main, screened) | none direct; proxy Qwen2.5-1.5B SD865 INT4 16.8 / Q5 14.7 (estimated) | SD 865 8 GB | ~12 to 17 tok/s (estimated) | Apache-2.0 (not opened here) |
| Qwen3-4B (screened) | forum 12-14 tok/s SD865 Q4_K_M (unverified); Qualcomm 8 Elite 18-23 at 512 ctx (conflicting) | SD 865 / 8 Elite | 12-14 (forum), 7-13 at 4096 ctx | Apache-2.0 (not opened) |
| Gemma 3n E2B | S24 Ultra CPU 16.1 dec / 110.5 pre | 12 GB flagship 2024 | 16 tok/s decode | gemma (Gemma terms) |
| Gemma 3n E4B | Pixel 9 Pro XL 5.7 dec / 35 pre / TTFT 7.5 s; S24 Ultra CPU 9.2 / 73.5 | 2024 flagships | 5.7 to 9.2 tok/s decode | gemma (Gemma terms) |
| Gemma 3 1B QAT | S24 Ultra prefill up to 2585 tok/s, decode not in text | 2024 flagship | decode not published | Gemma terms |
| Gemma-2-2B-IT | SD 865 Q5 11.2 / FP16 8.0 (estimated) | SD 865 8 GB | 8 to 11 tok/s (estimated) | Gemma terms (not opened) |
| Phi-4-mini 3.8B | Qualcomm 8 Elite 18.5-23 at 512 ctx, 6.9-13 at 4096 ctx | 8 Elite (newer) | ~7-23 tok/s (upper bound) | mit |
| Phi-3.5-mini 3.8B | SD 865 Q5 6.3 / FP16 4.5 (estimated) | SD 865 8 GB | 4.5 to 6.3 tok/s (estimated) | MIT (not opened) |
| SmolLM3-3B | S26 CPU decode 9.6-11.5, peak 3.1-4.4 GB; GPU 19-25, peak 1.2 GB | 2026 flagship | 9.6 to 11.5 tok/s CPU (LiteRT) | apache-2.0 |
| Llama-3.2-3B Q4 | Pixel 9 Pro tg128 ~12 (forum); Pixel 8 7.8 (anecdote); Tensor G3 12-16 (vendor); SD 865 Q5 7.7 (estimated) | mixed | 7.8 to 12 tok/s | Llama 3.2 Community Licence (not opened here) |
| LFM2-2.6B | none (no numbers in cards) | n/a | unknown | lfm1.0 / LFM Open v1.0 |

## Gaps

- No opened Pixel 8 (Tensor G3) llama.cpp measurement for any 1.5B to 8B model. Action: run `llama-bench -p 512 -n 128 -r 5` on the Pixel 8a with Qwen3-1.7B and Qwen3-4B GGUFs; record RAM with `dumpsys meminfo`.
- No Snapdragon 8 Gen 2 or 8 Gen 3 llama.cpp measurement for a 3B or 4B model in an opened source.
- RAM: only the SmolLM3 LiteRT card reports peak memory for 3B CPU (3.12 to 4.36 GB), and it is LiteRT, not llama.cpp.
- Reddit r/LocalLLaMA thread 1glx6a5 failed to load (HTTP 502 and a 403 on reddit.com). The Pixel 9 Pro and Pixel 8 rows come from search snippets only.

## Searched (queries and sources)

- WebSearch: llama.cpp Android Pixel 8 Tensor G3 Qwen; Snapdragon 8 Gen 2 Qwen3 4B Q4_K_M; PocketPal benchmark; Gemma 3n E2B Pixel LiteRT; Qwen3-4B Snapdragon 8 Gen 3; Pixel 8 Pro benchmark; MLC LLM Snapdragon 8 Gen 3; LFM2 Galaxy S24; SmolLM3 Android; Phi-4-mini Android; Gemma 3 4B QAT Pixel; llama.cpp GitHub discussions Android; KleidiAI Pixel 8.
- Opened: ertas.ai/blog/llm-android-benchmarks-snapdragon-tensor; qualcomm blog 2026/04 (title only, no data); huggingface datasets/dispatchAI/on-device-latency; google/gemma-3n-E2B-it-litert-lm; google/gemma-3n-E4B-it-litert-lm; qualcomm/Phi-4-Mini-Instruct; aihub.qualcomm.com qwen3_4b; Qwen/Qwen3-4B discussion 17; arxiv 2311.14030 (PDF, text extracted); hn.nuxt.dev/item/44044199; developers.googleblog.com gemma-3-on-mobile; litert-community/SmolLM3-3B; LiquidAI/LFM2-1.2B; LiquidAI/LFM2-2.6B; learn.arm.com performance_llama_cpp_sme2 and voice-assistant/7-performance (Vivo X300 pp128 table, no tg, no SoC name).
- Failed: redlib.hbubli.cc Reddit thread (502); reddit.com (blocked).
