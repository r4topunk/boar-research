# Model-driven chat routing: let the loaded LLM decide when to search (Anvil, 2026-10-02 night)

**Recommendation:** on the 4B, replace the rules with **B4: a one-token label gate on the already-loaded model**. It scores 95% on Compass chat-slice v0 with 0 missed searches. It only works if the gate's fixed 258-token prompt prefix stays **cached on the device**. For the 1.5B, no model-driven variant is safe yet. Don't use native tool calling: the models answer from memory instead of calling search.

Origin: r4to's new front. A real user typed "boa noite" and BOAR ran a full search plus answer; r4to wants no greeting rules. Fast-iteration policy: no sha freeze.

## What was compared

- **C (baseline):** today's rule, `smallTalk` + `classify.ts` @ upstream/main 0cfd4a77. Scores are Compass's (`compass/chat-slice/decisions.main.jsonl`). My own 30 items use `classify.ts` copied verbatim.
- **A (native tool calling):** the chat model gets a `search(query)` tool through the GGUF's own jinja template. For Qwen this is the Hermes `<tool_call>` format, the same one llama.cpp parses on the device. It's multi-turn aware and decides 0..n calls. Decision = it emitted a tool call. Greedy decoding, up to 96 tokens.
- **B (Jev-style label gate, [featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev), Apache-2.0, read 2026-10-02):**
  - one prefill of a router prompt, then the next-token probabilities of `SEARCH` vs `ANS` (the first token of "ANSWER");
  - score = p(SEARCH) / (p(SEARCH) + p(ANS)), threshold 0.5;
  - both labels' first tokens are distinct single tokens in both Qwen tokenizers;
  - history is folded into one user message: "Conversation so far … Last message …". With history as separate chat turns, the label probability mass fell to ~0.001 on follow-ups.
  - Prompt versions:
    - **B2:** neutral definition of the two labels.
    - **B3:** "BOAR answers questions about the world only from its offline library, never from memory … SEARCH even if you think you know the answer".
    - **B4:** B3 plus 13 short examples. The examples were written before Compass's slice existed and don't overlap it.
- **Engine:** desktop CPU, node-llama-cpp 3.21.1 (the desktop adapter's library), 4 threads, contextSize 4096, no GPU. Models from `shared-models/`: Qwen2.5-1.5B-Instruct Q4_K_M and Qwen3-4B-Instruct-2507 Q4_K_M.
- **Code:**
  - `run.mjs`: switches `ITEMS`, `B_ONLY`, `FOLD`, `B3`, `B4`;
  - `score.py` scores my 30 items, `score_slice.py` the slice;
  - `variant_c.mts` runs the baseline;
  - raw rows are in `runs-*.jsonl`.

## Results

### Compass chat-slice v0

- 64 items: PT 26 / EN 22 / ES 16; 13 multi-turn.
- Scoring follows Compass's `score.main.json`: 57 items are scored (34 "no search", 23 "search"); the 7 marked "either" are excluded.
- A **missed search** means the model answers a world question from memory, which is the hallucination risk. A **false search** costs time and adds noise.

| Variant | 1.5B | 4B |
|---|---|---|
| **C** rules (main) | 44%: false 32/34, missed 0/23 | same (model-independent) |
| **A** tool calling | 60%: false 1/34, **missed 22/23** | 65%: false 0/34, **missed 20/23** |
| **B2** gate, neutral prompt | 58%: false 14/34, missed 10/23 | n/a |
| **B3** gate, search-by-default | n/a (15/30 on my set, chance) | 81%: false 11/34, missed 0/23 |
| **B4** gate, B3 + 13 examples | 75%: false 6/34, **missed 8/23** | **95%: false 3/34, missed 0/23** |
| B4 at threshold 0.05 (search-biased) | false 20/34, missed 1/23 (*threshold picked on this slice*) | same as 0.5 (scores are near 0 or 1) |

- **4B B4's 3 false searches:** "quais assuntos você sabe?", "where do your answers come from?", "help". All three are meta or ambiguous, so they fail in the safe direction. Errors by language: en 2, pt 1, es 0.
- **Tool-call format** (all runs, my 30 items + slice):
  - 13 calls, all well-formed (valid JSON, name `search`, non-empty `query`);
  - 1 malformed: the 1.5B wrote a call-like text outside the tags.
  - The 4B's queries are good self-contained rewrites ("clima em Lisboa Portugal", "é perigoso dirigir moto de Chiang Mai para Pai?"). One query drifted to Spanish on a Portuguese message.
  - The problem with A is recall, not format.

### My 30 quick items (PT/EN; 15 search, 15 no-search; 4 multi-turn; `items.jsonl`)

The prompts were iterated on this set, so it is the dev set and the slice is the check.

| Variant | 1.5B | 4B |
|---|---|---|
| C | 18/30 (searches all chit-chat but 3) | 18/30 |
| A | 16/30 (1/15 search recall; "a capital do Cazaquistão é Almaty") | 23/30 (8/15) |
| B2 | 24/30 | 27/30 (misses capital, route, visa: "it knows") |
| B3 | 15/30 | 28/30 (15/15 recall) |
| B4 | 17/30 | 29/30 |

### Added cost per message (tokens; time on desktop is noisy, the load average was ~5 from other agents)

| Variant | Gate prompt (static, cacheable) | New tokens per message, p50 / max (with history) | Extra decode | Desktop prefill p50, uncached (1.5B / 4B) |
|---|---|---|---|---|
| C | 0 | 0 | 0 | ~0 ms |
| A | 276 (system + tool schema; part of the chat prompt) | 12–14 / 63 | SEARCH path: ~24–29 tokens for the call | 1.4 s / 4.5 s |
| B2 / B3 / B4 | 93 / 116 / 258 | 12–14 / 61–64 | 0 (one forward) | B4: 1.8 s / 4.2 s |

## Cost on the moto g75 (estimate)

Rates:

| Model | Prefill | Decode | Source |
|---|---|---|---|
| 1.5B | ≈ 65–90 tok/s | 12.2 tok/s | measured, `and-q15-r1`; prefill from time to first token minus retrieval on 6 rows. The traces' `prefillMs` field is unreliable (sometimes larger than time to first token), so `tools/e2_latency_check.py` misreads device prefill. |
| 4B | 12–18 tok/s | 2.5–3.8 tok/s | frozen prediction, `android-4b-latency-budget` §2b. The 4B doesn't load on the g75 until Probe B (`no_extra_bufts`); no-repack speed is UNKNOWN. |

| Variant | 1.5B on g75 | 4B on g75 |
|---|---|---|
| C | 0 | 0 |
| **B4, prefix cached** | **+0.2 s p50** (≤ 0.9 s with long history) | **+0.7–1.0 s p50** (≤ 3.4–5 s) |
| B4, prefix re-prefilled every message | +3–4 s | **+15–22 s** (unusable) |
| A, SEARCH path | +2 s (decoding the call) | +6–10 s |
| **Saved on the ANSWER path** (greetings, thanks, meta) | skips retrieval (2.0–5.3 s measured) + the sources prompt (300–600 tokens ≈ 4–8 s): **≈ 6–13 s faster** | larger: the sources prompt alone ≈ 20–40 s at 12–18 tok/s |

- **Keeping the prefix cached is a condition, not an option.** llama.rn reuses KV only for the prefix shared with the previous completion. The gate prompt and the answer prompt differ from the system message onward, so each answer evicts the gate prefix.
- **Ways to keep it** (one to pick and test on the device):
  - **(a)** a second slot: llama.rn `context.parallel.enable({ n_parallel: 2 })`. The KV memory cost per slot is UNKNOWN.
  - **(b)** saving the gate's KV once and reloading it before each gate call: llama.rn `saveSession` / `loadSession`. That is ~38 MB for 258 tokens on the 4B (36 layers × 8 KV heads × 256 × 2 bytes per token).
  - **(c)** shortening the gate, B3 at 116 tokens, at the measured accuracy cost on the 4B (81% vs 95%).

## Does llama.rn (rc.4) support what the variants need?

| Need | Status |
|---|---|
| jinja chat templates | yes: `jinja: true`; BOAR already uses `messages` + `jinja` (`LlamaEngine.ts` ~459/512). |
| Native tool calls | yes: completion params `tools`, `tool_choice`, `parallel_tool_calls`; result `tool_calls[{function:{name, arguments}}]`, parsed natively by the jinja `chat_parser` (`src/index.ts` 281–283, 443–483; `src/types.ts` 490). |
| Next-token probabilities | yes: `n_probs` (`src/types.ts` 290) → `completion_probabilities[].probs[{tok_str, prob}]`. The gate is `n_predict: 1, n_probs: 20`, reading `tok_str` "SEARCH" vs "ANS". Label mass was ≥ 0.93 with the folded-history prompt, so both labels are in the top 20. **UNKNOWN:** whether llama.rn's probs are pre- or post-sampling. Use temperature > 0 for that call, or verify on the device that greedy doesn't return one-hot probs. |
| KV prefix reuse | yes, automatically for the shared prefix with the last prompt; it doesn't cover alternating prompts (see above). |
| Parallel slots / session state | `parallel.enable({n_parallel})` (`src/index.ts` 637); `saveSession`/`loadSession`. Not verified for this use. |

## What would make it fail

- **Overfitting:**
  - B4's examples were written before the slice existed, but the B3 → B4 step was chosen on my 30 items;
  - the 1.5B's 0.05 threshold was picked on the slice itself;
  - both need a fresh set before any bench claim.
- **Answers in the ANSWER path:** the 4B's answers are fine for greetings, thanks and meta (see `runs-q4b.jsonl`, A text). But replying in the user's language is a separate issue, Compass's `lang_match`.
- **Device:** if the 4B's no-repack prefill on the g75 is much slower than predicted, even the cached gate costs seconds.

UNKNOWN:
- the g75 1.5B prefill rate (derived, not measured cleanly);
- the 4B's speed on the g75;
- llama.rn's `n_probs` semantics;
- the memory cost of a second slot.

## Next iteration (fast)

1. **On the device (g75, 1.5B already installed):** one gate call with `n_predict: 1, n_probs: 20` on 10 slice items. Check that the probabilities match the desktop scores (±0.1), and measure the gate time with the prefix cached via `saveSession`/`loadSession` vs uncached.
2. **For the 1.5B:** test whether a gate on the 4B's prompt style plus a shorter answer path is even needed, or whether the 1.5B tier just keeps C and fixes its PT/ES greeting coverage. That last part is r4to's call, given the "no rules" preference.
