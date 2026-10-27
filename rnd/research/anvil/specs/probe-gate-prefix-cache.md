# Route-gate prefix cache: decision + device probe spec (Anvil, 2026-10-02; frozen before any device run)

> **Scope update (r4to, 2026-10-02): no ≥ 8 GB iPhone, so leg C is dropped.** Legs kept: A (g75 1.5B), B (g75 4B, after Probe B), A′ (iPhone 13 1.5B, Metal mechanism). The 4B cost bar P3 is judged on leg B only. The iOS 4B cost (≈ 0.2–0.4 s in §3) stays a **desktop-derived estimate, labelled as such**, not a measurement.

**TL;DR:** keep the B4 gate's fixed prefix cached with **two session files on the classic (single-sequence) path**:
- `loadSession(gate)` before each gate call;
- `loadSession(answerPrefix)` before the answer that follows.

Parallel slots are unusable on rc.4. The shared-prefix variant would change every answer prompt, so it stays the fallback. Probe legs: g75 + 1.5B now (mechanism + timings), g75 + 4B after Probe B passes, iOS 4B-profile device when available. **Cost bar (4B legs): gate overhead p50 ≤ +1.0 s.**

Context: `../exp/chat-routing/README.md` (B4 = 95% on chat-slice v0, but uncached the 4B costs +15–22 s on the g75) and `../exp/chat-routing/llamarn-nprobs.md` (rc.4 probs).

## 1. The three options, checked against llama.rn 0.13.0-rc.4 source (`boar-app/node_modules/llama.rn`)

| Option | What the rc.4 code does | Verdict |
|---|---|---|
| **(a) parallel slot** (`context.parallel.enable({n_parallel: 2})`) | **n_ctx is split per slot:** `n_ctx_per_slot = n_ctx / n_parallel` (`cpp/rn-slot-manager.cpp:54`), so answers would get 2048 of the 4B's 4096. **Slot choice is LRU, not by prompt:** `get_available_slot` (`:419-440`), so the gate can't be pinned to a slot. **A slot reuses its KV prefix only when the request carries `load_state_path`:** otherwise the slot "starts fresh" and runs `llama_memory_seq_rm(kv, id, 0, -1)` (`cpp/rn-slot.cpp:192-270`). **`loadSession`/`saveSession` throw in parallel mode** (`cpp/jsi/JSISession.h:26-30,102-106`). BOAR's answer path (`completion()` + `setAnswerPrefix` warm) would have to move to the queue API. | **Rejected.** On rc.4 it is just (b) with a halved context and a rewritten answer path. |
| **(b) session swap** (`saveSession` / `loadSession`, classic path) | `loadSession` runs `llama_state_load_file` and **restores the token list into `completion->embd`** (`JSISession.h:22-60`). The next `completion()` runs `find_common_prefix_length(embd, prompt)` → `seq_rm(n_common…)` and prefills only the tail (`cpp/rn-completion.cpp` loadPrompt ~443-470). `embd` survives between completions (it is cleared only by embedding/rerank, `:1780`, `:1834`). `saveSession(path, {tokenSize})` saves the state plus the first N tokens; on load, the memory is rolled back to N (`JSISession.h:50-60`). | **Chosen.** Works on rc.4, no native change, no change to the answer prompt, the answer keeps its full n_ctx. Cost = 2 file loads per message (measured by this probe). |
| **(c) gate on the answer's shared prefix** | One sequence. The gate and the answer share only the bytes they have in common from token 0. The answer system prefix (`answerPromptPrefix`, ~225 tokens) is followed by different content, so the gate's 258-token instruction block would be re-prefilled on every message unless it moves **into the answer's system message**. That changes every answer prompt (+258 tokens of routing text the answer model reads) and the gate prompt B4 was measured with. | **Fallback**, only if (b)'s file loads miss the bar. It would need its own L1 (gate accuracy with the BOAR system prompt in front) and its own L2 (answers with routing text in the system message). |

The in-memory "prompt state cache" in rc.4 (`rn-completion.cpp:88-118`) is **recurrent/hybrid only** (`state_cache_enabled = llama_model_is_recurrent || llama_model_is_hybrid`). It is off for Qwen3-4B and Qwen2.5-1.5B and is not a 4th option.

## 2. Design (b), as implemented in the arm's `LlamaEngine` part (`../exp/chat-routing/arm/`)

- **Files:** `<cacheDir>/kv/<modelFile>.<sha8(prompt prefix text)>.<llama.rn version>.gate.bin` and `….answer.bin`, one per answer tone. They are deleted with the model. Built lazily:
  - gate: the first gate call after a load prefills the gate's fixed prefix (n_predict 0, same messages format as the gate with an empty user turn) → `saveSession(file, {tokenSize: nPrefix})`;
  - answer: `warmNow()` already prefills the answer prefix → `saveSession(answerFile, …)` right after it.
- **KV owner:** the engine tracks `kvHolds: "gate" | "answer" | "other"`.
  - Gate call: if `kvHolds !== "gate"`, `loadSession(gateFile)`; then the gate completion; then `kvHolds = "gate"`.
  - `generate()` with a prompt that `sharesPrefix`: if `kvHolds !== "answer"` and the answer file exists, `loadSession(answerFile)` first.
  - Anything else leaves `kvHolds = "other"`, and the existing idle warm does the rest.
- **Sizes** (f16 KV; per token = layers × KV heads × head dim × 2 (K, V) × 2 bytes):

  | Model | Shape | Per token | Gate file (~258 tok) | Answer file (~225 tok) |
  |---|---|---|---|---|
  | 4B | 36 × 8 × 128 | 144 KiB | ≈ 36 MiB | ≈ 32 MiB |
  | 1.5B | 28 × 2 × 128 | 28 KiB | ≈ 7 MiB | ≈ 6 MiB |

  `llama_state_load_file` reads tensor by tensor through a small temp buffer, not the whole file, so the RSS cost should be small. UNKNOWN on the device: that's criterion P5.
- **rc.4 n_probs workarounds** (from `llamarn-nprobs.md`):
  - the gate reads the **last** `completion_probabilities` entry;
  - every answer `completion()` passes `n_probs: 0` (sampling params are sticky);
  - the gate sets only `n_predict: 1`, `n_probs: 20`, `temperature: 1`, never top_k / top_p / min_p / logit_bias / ignore_eos;
  - no label in the top 20 → SEARCH.

## 3. Cost model (prediction, stated before the probe)

Gate overhead per message = `loadSession(gate)` + gate prefill of the new tokens (+1 forward) + `loadSession(answer)` when the answer follows.

| Leg | Prefill rate | New tokens single-turn / short follow-up | loadSession ×2 | **Predicted overhead p50** |
|---|---|---|---|---|
| g75 1.5B | 65–90 tok/s (derived) | 13 / ~60 → 0.15–0.2 s / 0.7–0.9 s | 2 × (7 + 6 MiB): ~0.02–0.1 s | **≈ 0.2–0.3 s** |
| g75 4B (needs Probe B) | 12–18 tok/s (frozen prediction) | 13 / ~60 → 0.7–1.1 s / 3.3–5 s | 2 × (36 + 32 MiB): ~0.1–0.3 s | **≈ 0.8–1.4 s: borderline on the bar** |
| iOS 4B profile (8–12 GB iPhone) | UNKNOWN; A17/A18-class Metal prefill likely ≥ 100 tok/s | 13 / ~60 → ≤ 0.15 / ≤ 0.6 s | ~0.05–0.2 s | **≈ 0.2–0.4 s** |

The ANSWER path skips retrieval + the sources prompt: −6–13 s on the 1.5B, −20–40 s on the g75 4B. So one correctly skipped search pays for 20–40 gate calls on the 4B.

## 4. Device probe (next phone session; apply the arm's device patch through Metro, as in Probe B)

**Setup:**
- Engine tree: 0cfd4a77 + `../exp/chat-routing/arm/b5gate-engine.patch` (sha256 `50609046…`) for **legs A / A′ (1.5B)**. For **leg B (4B)**, then apply `../exp/chat-routing/arm/b5-to-b6-gate.patch` (sha256 `21211329…`; touches only `routeGate.ts` + its test; B5 + it = `b6gate-engine.patch` `17a50083…`, verified). B6 is the arm that passed desktop L1 on 2026-10-03. Why leg A stays on B5: see `why_leg_A_stays_B5` in `probe-gate-items.json` (1.5B label mass collapses under the B6 prompt). Leg A also sets `ROUTE_GATE_CONFIG.anyModel = true` in `src/routing/routeGate.ts` (a one-word Metro edit). Every gate logs one line:
  `[gate] model=… newTok=… cachedTok=… loadGateMs=… gateMs=… probsLen=… top=SEARCH:p,ANS:p,…`, plus `[gate] answer prefix restored in N ms` before the answer that follows (= loadAnswerMs). The route the engine took is in the answer receipt (`route-gate:*` reason codes).
- Airplane mode, unplugged, force-stop + cold start; verify the `[gate]` lines appear before measuring.
- **Items:** 10 from Compass chat-slice v0 (frozen list, all already run on the desktop):
  - 5 that should answer directly: cs-001-type greetings / thanks / meta;
  - 5 that should search, 2 of them multi-turn.
  - Pinned in `probe-gate-items.json`: 10 items + 2 spares. **References re-pinned to B5 on 2026-10-03, before any device run** (B4 columns kept as `*_b4`). Leg A compares against the B5 1.5B column; the pre-registered reading for its near-threshold items (cs-021 0.423, cs-028 0.433) is in the file.
- **Control and ordering (decided 2026-10-03 for Forge): ABAB blocks, not per-item interleave.**
  - Gate on = `ROUTE_GATE_CONFIG.off = false` (A), gate off = `true` (B).
  - The toggle is a Metro source edit, so switching per item means a JS reload before every item. A reload resets the engine's JS state (`gateCachedKey`, `prefixCached`, warm timer) and may re-init the context. Every gate would then be a "first gate after load": the cold path that P2/P3 must NOT measure.
  - **Order:**
    - **A1:** items 1–5, **B1:** 1–5, **A2:** 6–10, **B2:** 6–10;
    - each block starts with a force-stop + cold start, then **1 unmeasured warm-up message** (spare cs-010) so the session files exist and the KV is in steady state;
    - then the 5 measured items, sent back to back.
  - **Thermal / drift guard (replaces per-item interleave for this probe):**
    - log `adb shell dumpsys battery | grep temperature` and the time at each block start;
    - P3 uses the gate-on blocks only (`loadGateMs + gateMs + loadAnswerMs` from the `[gate]` lines). The A − B answer totals are reported, not gated;
    - if the battery temperature rises > 5 °C between A1 and A2 → note it next to P3.

**Legs:**
- **A:** moto g75 + 1.5B (installed today);
- **B:** moto g75 + 4B, only after Probe B passes (`no_extra_bufts`);
- **C:** an iOS device on the 4B profile (≥ 8 GB iPhone), when one is available. Plus **A′:** iPhone 13 + 1.5B for the Metal mechanism only.

**Frozen criteria:**

| # | Criterion | Applies to |
|---|---|---|
| P1 | **Decision parity:** device decision = desktop decision on 10/10 items. Desktop = node-llama-cpp raw softmax, `runs-slice-q4b-b4.jsonl` / the 1.5B rerun with the same prompt. A mismatch is allowed only where the desktop score is within 0.45–0.55. | all legs |
| P2 | **Cache works:** gate completions report `tokens_cached ≥ nPrefix − 1` on ≥ 9/10 calls, and the answer after it reports cached ≥ answer prefix − 1. | all legs |
| P3 | **Cost:** gate overhead p50 ≤ **1.0 s** (`loadGateMs + gateMs + loadAnswerMs`, over the 10 items). p95 is reported. | **4B legs (B, C)**; leg A reported only |
| P4 | **No answer side effects:** after a gate call, `completion_probabilities` grows by exactly 1 per gate (answers add none, so `n_probs: 0` holds), and 10/10 answers succeed. | all legs |
| P5 | **Memory:** peak TOTAL RSS with the gate ≤ control peak + 100 MB (`dumpsys meminfo` every 1 s on Android; Xcode memory gauge on iOS); 0 LMK / jetsam kills. | all legs |

- **Failure handling:** if P3 fails on leg B but passes on leg C → the gate ships on the iOS 4B profile only; the g75 4B is r4to's call. If P2 fails (no cache hit after `loadSession`) → switch to option (c) and run its L1. If P1 fails → stop: the decision is runtime-dependent and the desktop L1/L2 doesn't transfer.

UNKNOWN:
- g75 4B prefill rate (Probe B gives it);
- `loadSession` ms on UFS / iOS NVMe for 7–36 MiB;
- whether an ≥ 8 GB iPhone is available for leg C (the "iOS 12 GB profile" device);
- the gate's accuracy on long real chats (the fold caps history, see the arm README).
