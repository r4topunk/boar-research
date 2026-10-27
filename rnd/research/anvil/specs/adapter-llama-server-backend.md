# Spec: a llama-server (b11010) backend for boar-eval's desktop-node adapter

TL;DR: add a second `AnswerEngine` implementation, `makeServerEngine`, that talks to a pinned `llama-server` build over HTTP/SSE instead of in-process node-llama-cpp. It is selected by `--backend server --server-bin <path>`, and the default path is unchanged. It is about 120 lines in `adapters/desktop-node/runner/adapter.ts`, plus one validation run. It unblocks QUEUE #15 (Maple, `maple` arch missing from node-llama-cpp's llama.cpp `v0.4.0`). It also gives the harness hidden-reasoning time and peak RSS for free.

Author: Anvil · 2026-10-02 · for Kiln (implementer) and the coordinator. Read-only sources: `boar-eval/adapters/desktop-node/runner/adapter.ts` (469 lines), `rnd/kiln/exp-01-inram-moe-reader/harness/{build-b11010.sh,serve-bench.py,run-model.sh}`, `rnd/kiln/exp-02-maple/README.md`.

## 1. Why a server backend and not a node-llama-cpp rebuild

| Option | Work | Risk |
|---|---|---|
| A. `npx node-llama-cpp source download --release b11010` (rebuild the addon at b11010) | Small if it builds | node-llama-cpp 3.21.1's addon must compile against b11010's C API (`llama_lazy_mode`, new params). UNKNOWN; it can fail on API drift, and it changes the engine for **every** arm, so all baselines would need a re-run |
| **B. llama-server backend (this spec)** | ~120 lines + 1 validation run | Sampler/template differences vs node-llama-cpp, handled by the validation in §5. The binary **already exists**: `<runner>/spikes/llama-b11010/build-cpu/bin/llama-server` (Kiln exp-02, b11010 `4bc272f`, 54 s build, CPU only, `GGML_METAL=OFF`) |

B keeps the default adapter byte-for-byte, so existing runs stay comparable. It also reuses a binary that exp-02 already validated: the 4B's answers on b11010 were byte-identical to 0e8c83e.

## 2. Where it plugs in

- `makeEngine(modelPath, fileName, seed, temp, onGeneration)` (`adapter.ts` ~204) returns the object the app's routing code calls:
  - `load`, `stop`, `getModelInfo`, `hasEmbeddedChatTemplate`, `estimateFit`, `setAnswerPrefix`;
  - `generate(o)`, where `o` has `messages | prompt`, `nPredict`, `thinkingBudget`, `enableThinking`, `stop`, `timeoutMs`, `nCtx`, `temperature`, `onToken(chunk)` and `onTimings({promptTokens, promptMs, predictedTokens, predictedMs, cachedTokens})`.
- **New:** `makeServerEngine(...)` with the same signature and the same returned shape. `main()` picks one or the other from `cli.backend` (`"node"` default | `"server"`).
- Nothing in `trace.ts` / `protocol.ts` changes, except two optional fields (§4).

## 3. `makeServerEngine` behaviour

**Start (once per run, inside `makeEngine`'s place):**
```
<server-bin> -m <gguf> -t <threads> -tb <threads> -c 4096 -ngl 0 -np 1 --jinja --no-webui \
  --cache-ram 0 --reasoning-format deepseek --port <free port>
```
- These are exactly Kiln's exp-01/02 flags (`serve-bench.py`). `--cache-ram 0` keeps RSS valid (exp-01 §5). `--reasoning-format deepseek` splits `<think>` into `reasoning_content`.
- `loadMs` = time until `GET /health` returns 200.
- `fileName`'s sha256 is already checked by the adapter.
- Record `<server-bin> --version` (build + commit) into `runtime.versions` as `"llama-server": "b11010 (4bc272f)"`. Add `backend: "llama-server"`.
- Kill the server on exit, including on SIGINT and errors (`finally`).

**`generate(o)`:**
- Request `POST /v1/chat/completions` with `stream: true` when `o.messages` exists. Otherwise use `POST /completion` with `prompt` and `stop = o.stop ?? ["\nUser:", "\nQuestion:"]`, the same fallback as today. Body:
  - `messages`;
  - `max_tokens = (o.nPredict ?? 512) + (o.enableThinking === false ? 0 : o.thinkingBudget ?? 0)`, the same arithmetic as the node path;
  - sampler identical to the node path: `temperature = temp ?? o.temperature ?? 0.7`, `top_k 40`, `top_p 0.95`, `min_p 0.05`, `seed`;
  - `cache_prompt: false`: the node path builds a fresh context per answer, and the app's prefix cache is not emulated there either;
  - `chat_template_kwargs: { enable_thinking: false }` **only when** `o.enableThinking === false`. Templates without the variable ignore it (Maple does, per exp-02).
- **Stream parsing (SSE):**
  - `choices[0].delta.reasoning_content`: hidden reasoning. Count chunks/tokens and record `firstReasoningMs`. **Do not** pass it to `o.onToken`.
  - `choices[0].delta.content`: visible text. Pass it to `o.onToken`, and set `firstTextMs` at the first chunk with `content.trim() !== ""`.
  - Final chunk `timings`: `prompt_n`, `prompt_ms`, `predicted_n`, `predicted_ms`. Map to `onTimings({promptTokens: prompt_n, promptMs: prompt_ms, predictedTokens: predicted_n, predictedMs: predicted_ms, cachedTokens: 0})` and to the `Generation` record.
- **Timeout:** an `AbortController` on `fetch`, with `o.timeoutMs ?? cli.timeoutMs` as today. `stop()` aborts the in-flight request.
- **Return** the concatenated visible `content`, which is what the app shows. Reasoning never reaches the app code, the same as llama.rn with tags.

**Thinking budget (the one semantic gap):**
- llama.rn enforces `thinking_budget_tokens` per request by forcing the end tag (LlamaEngine sets it; the fast tier uses 256).
- `llama-server` has a **server-wide** `--reasoning-budget` flag; a per-request equivalent is UNKNOWN for b11010. Verify with `llama-server --help | grep -i -e budget -e reasoning`.
- **Minimum spec:** pass the per-item `o.thinkingBudget` as a cap on hidden tokens. Count `reasoning_content` tokens while streaming (via `/tokenize` on the accumulated text, or 1 chunk ≈ 1 token). If the count reaches the budget, abort and re-issue the request with the reasoning so far plus the end tag prefilled as an assistant message, which is how llama.rn continues after forcing `</think>`.
- **If that is too much for tonight:** run without the cap. Record `reasoningTokens`, and **flag every item whose reasoning exceeds `o.thinkingBudget`** in the trace (`thinkingBudgetExceeded: true`). In exp-02 Maple's median was ~121 tokens, so the cap binds only on a tail. The flagged items are where the desktop run is not app-faithful.

**Peak RSS (bonus, the node path leaves `resources` null):**
- Sample `ps -o rss= -p <server pid>` every 250 ms during each `generate`. Write `resources.peakRssBytes` as the max over the run, and per item if the trace allows.
- This is the number criterion 6 of #15 needs, measured the way exp-01 §5 did.

## 4. Trace fields (optional, backward compatible)

- `timing.firstVisibleMs` (= `firstTextMs`) and `timing.reasoningMs` (= `firstTextMs − firstReasoningMs` when reasoning happened). Together these are the harness TTFT fix the coordinator assigned on 2026-10-02.
- `timing.reasoningTokens`, `route.thinkingBudgetExceeded` (bool).
- `runtime.versions["llama-server"]`, `runtime.backend`.

## 5. Validation before any Maple run (definition of done)

1. **Determinism and parity at temp 0.** Qwen3-4B Q4_K_M, Android profile, 72 items, `--temp 0`, both backends. Done when **≥ 68/72 answers are byte-identical**. If fewer, diff the rendered prompts first: node-llama-cpp uses its own Qwen chat wrapper, llama-server uses the GGUF jinja template, and that is the likeliest source of drift.
2. **Same instrument at temp 0.7.** Seed 42 on the server backend vs the existing `and-qwen-s42` (node). Gate mode plus judge. Done when the ratio Δ is inside the MDE (|Δ| < 0.036) and the confident-wrong / unsafe counts match ±1.
3. **Speed sanity.** Prefill and decode tok/s within ±10% of the node path for the 4B on the same host and threads. exp-02 shows b11010's 4B speed equal to 0e8c83e's.
4. Only then the #15 arm (Maple TQ2_0-head-Q4_K, 2 seeds), compared against the **server-backend** Qwen runs from steps 1–2, so the backend is held fixed.

## 6. Cost

- Code: ~120 lines TS. No new dependencies (`fetch` + `child_process` are in Node 25).
- Validation: 72 × 2 desktop runs (~30 min) plus ~70 judge calls.
- Disk: 0 extra for the binary (it exists). Maple's 5.9 GB stays blocked on the #6 enwiki build (coordinator, 2026-10-02).

## 7. Risks

- **Sampler parity:** llama-server's default sampler chain order may differ from node-llama-cpp's. At temp 0.7 the answers will differ token by token even when quality is equal. That is why step 2 compares quality, not bytes.
- **Template parity** (step 1) is the real risk. If the two backends render different prompts, the backend becomes a confound. Hold the backend fixed within any comparison (step 4).
- `--jinja` template errors on exotic templates surface as HTTP 500. Fail the item loudly and do not fall back silently.

UNKNOWN:
- per-request reasoning budget in llama-server b11010;
- whether node-llama-cpp 3.21.1 would build against b11010 (option A).
