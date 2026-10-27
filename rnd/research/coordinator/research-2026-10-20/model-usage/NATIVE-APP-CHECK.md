# NATIVE-APP-CHECK: how the native Kotlin app calls llama.cpp (thinking, sampling, model)

TL;DR: thinking is OFF by default in the native app (enable_thinking=false passed to the embedded GGUF's jinja template). Auto = off. Default 8 GB model is Qwen3-4B-Instruct-2507 (non-thinking), and Qwen3-1.7B is not in the catalog.

Source: github.com/UPSTREAM_REPO/boar-app, branch `fullnative-dev`, shallow clone at `<scratch>/fullnative`.
Commit: **0be84acd28c8715a45223735879c57ac108f89f1** (2026-10-19 17:58 -0300).
All paths below are relative to `android-native/`. Read-only check, nothing sent.

## Settings table

| Item | Value | file:line |
|---|---|---|
| Template application | Embedded GGUF template via llama.cpp `common_chat_templates_init(model, "")` + `common_chat_templates_apply`, `use_jinja = true`, `add_generation_prompt = true` (no hand-built template when the GGUF has one) | engine/src/main/cpp/boar_jni.cpp:207, :252-266 |
| enable_thinking | `in.enable_thinking = enableThinking` (JNI arg) | boar_jni.cpp:263 |
| enableThinking source (main answer) | `AnswerRequest(..., enableThinking = settings.engineTweaks.thinkingEnabled)`; `AnswerRequest.enableThinking` defaults false | app/.../chat/ChatViewModel.kt:571; engine/.../answer/AnswerPipeline.kt:22-23, :89 |
| thinkingEnabled resolution | `thinking ?: false` (Auto = off); user can set On in Settings → Advanced | engine/.../EngineTweaks.kt:48-51; app/.../ui/settings/SettingsScreen.kt:414 |
| Presets | FORAGE and COOL set `thinking = false` explicitly | engine/.../TweakPresets.kt:21, :23 |
| Deep Research / chat-about-conversation path | `SessionEngine(session, thinkingEnabled)`, same flag | ChatViewModel.kt:549; SessionEngine.kt:17, :23 |
| Adaptive routing path (off by default) | `adaptiveRoutingEnabled` default false; PlanExecutor goes through `SessionEngine(session, tweaks.thinkingEnabled)` | AppSettings.kt:132; BoarServices.kt:261 |
| Bench activity | `formatChat(..., enableThinking = false)` hard-coded | app/.../bench/BenchActivity.kt:157 |
| /no_think or hand-written empty `<think></think>` | None found (grep for no_think, `<think>`, enable_thinking over all .kt/.cpp/.json). Suppression relies entirely on the template's `enable_thinking` kwarg. | grep result |
| Reasoning budget | None. No thinking-budget parameter exists in JNI or Kotlin; the only bound is nPredict (and the stage timeout) | boar_jni.cpp:289, :331; EngineTweaks.kt:57-67 |
| nPredict (answer) | `req.maxTokens`; Auto = 1024 for style "detailed" (the app default), 512 other styles, 2048 Deep Research, clipped to `openedContext - 1500` (min 256) | AppSettings.kt:76, :97-123; AnswerPipeline.kt:97; ChatViewModel.kt:536-537 |
| Small talk cap | `min(budget, 512)` | ChatViewModel.kt:538-541 |
| Temperature | 0.7 (hard-coded in the answer pipeline; `Sampling` default 0.7) | AnswerPipeline.kt:97; Engine.kt:60 (Sampling defaults) |
| top_k / top_p / min_p | 40 / 0.95 / 0.05 (Sampling defaults, never overridden) | Engine.kt:61-63; boar_jni.cpp:320-322 |
| Repeat penalty | 1.0 (penalties sampler added with last-n 64, freq/presence 0) | Engine.kt:64; boar_jni.cpp:319 |
| Sampler chain order | penalties, top_k, top_p, min_p, temp, dist (temp <= 0 = greedy) | boar_jni.cpp:314-324 |
| Seed | random (`seed = -1` is not sent; LLAMA_DEFAULT_SEED) | Engine.kt:65, :56; boar_jni.cpp:324 |
| Stop tokens | `cp.additional_stops` from the template + EOG tokens (`llama_vocab_is_eog`); the hand-built prompt (no template) uses "\nUser:", "\nQuestion:" etc. | boar_jni.cpp:271, :335; AnswerPipeline.kt:85-92, :114 |
| `<think>` stripped from display | Yes, in the UI: `AnswerText.splitThinking` handles `<think>...</think>` and `<\|channel>thought...<channel\|>`; the answer part is shown, reasoning is behind a 💭 toggle (unfinished reasoning shows "reasoning unfinished" note) | AnswerText.kt:10-35; ChatScreen.kt:503-515, :553 |
| `<think>` stripped from history/copy | Yes, `stripThinking` on assistant turns sent back as history | ChatViewModel.kt:491, :505, :664; AnswerText.kt:39 |
| Stored text | Full text with thinking kept (as the TS engine) | AnswerPipeline.kt:34 |
| Context | Auto: 2048 up to 4.5 GB RAM, 3072 up to 6.5 GB, else 4096; KV F16 | EngineTweaks.kt:117-122, :32 |
| llama.cpp | Submodule, pinned commit 4bc272fd729bd094c0422e4b8353da8d2fec91f8 (directory empty in the shallow clone, so upstream template/`enable_thinking` code was not inspected here) | .gitmodules; git ls-tree HEAD |

## Models shipped (catalog)

| Model | Quant | Role | file:line |
|---|---|---|---|
| Qwen3-4B-Instruct-2507 (non-thinking instruct; `answerTier: default`, sha256 3605803b...) | Q4_K_M, 2,497,281,120 B | default answer model (DefaultModel picks it when RAM > 4.5 GiB, resident, >= 6 tok/s) | app/src/main/assets/boar-data/catalog.json:41-60; engine/.../routing/DefaultModel.kt:27-30 |
| Qwen2.5-1.5B-Instruct | Q4_K_M, 986,048,768 B | `compact` tier (<= 4.5 GiB RAM) | catalog.json:62-80 |
| Qwen2.5-7B, Phi-3.5-mini (hidden), LFM2.5-8B-A1B (thinks first), Gemma 4 E4B (QAT Q4_0) | Q4_K_M / Q4_0 | optional | catalog.json:3-20, :82-130 |
| **Qwen3-1.7B** | none | **not in the catalog**; grep for 1.7b / qwen3-1 over .kt/.json/.md finds nothing | grep result |

A user could add Qwen3-1.7B through the in-app Hugging Face browser (models/HfBrowser.kt exists); the behavior then follows the same path as above.

## Verdict: thinking OFF (by default)

- The native app passes `enable_thinking=false` to llama.cpp's jinja template for every answer path unless the user sets Advanced → Thinking = On (EngineTweaks.kt:51; boar_jni.cpp:263). Auto = off, with a comment saying so ("so the answer's token cap isn't spent on reasoning", EngineTweaks.kt:48; AnswerPipeline.kt:87-88).
- Caveat (UNKNOWN): whether a Qwen3-1.7B GGUF template with `enable_thinking=false` renders an empty `<think></think>` at the pinned llama.cpp commit 4bc272fd was not verified here (submodule not fetched). The TS engine's llama.rn left it at the template default (on), per the comment at AnswerPipeline.kt:87, which is the difference to the TS path.
- No 1.7B ships by default anyway: the 8 GB default is the Qwen3-4B-Instruct-2507 non-thinking model, whose template has no think block.
- If thinking text did leak, it would be hidden behind the 💭 toggle, but it would still cost tokens (nPredict 1024 Auto).

## Differences from the TS engine

| Aspect | TS engine (per audit) | Native app |
|---|---|---|
| Thinking | planned ON for Qwen3-1.7B fast tier (depth.ts:259), budget 256 | OFF by default, no budget concept, bounded only by nPredict |
| Main/8 GB model | Qwen3-1.7B (fast tier) | Qwen3-4B-Instruct-2507 Q4_K_M (default tier) / Qwen2.5-1.5B (compact, <= 4.5 GiB RAM) |
| Sampling | see sampling.md | fixed 0.7 / 40 / 0.95 / 0.05, repeat 1.0, random seed |
| Answer cap | thinkingBudget 256 + answer | 1024 (detailed, default) or 512, 2048 Deep Research |
| Routing | depth-based | `adaptiveRoutingEnabled` default false (single model path) |

## Draft note for the app maintainer (NOT SENT)

```
Checked fullnative-dev @ 0be84acd: answers call the GGUF jinja template with enable_thinking=false (boar_jni.cpp:263, EngineTweaks.kt:51), so Auto = thinking off, and the catalog's 8 GB default is Qwen3-4B-Instruct-2507 Q4_K_M (non-thinking).
Qwen3-1.7B is not in catalog.json; if you add it as the fast model, keep thinking off (there is no reasoning budget in the JNI, only nPredict 1024/512).
Sampling is 0.7/40/0.95/0.05, repeat 1.0, random seed; ChatScreen hides <think> blocks behind the 💭 toggle (ChatScreen.kt:503-515).
```
