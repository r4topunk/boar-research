# MiniCPM5-1B as the iPhone compact reader (the lightest a competitor team model)
TL;DR: MiniCPM5-1B is the other model in the post author's a competitor team copy. It needs only 0.53 GiB hot per token (vs 0.91 GiB for Qwen2.5-1.5B), so it would decode ~1.7× faster on the iPhone. **Tested offline on 40 captured prompts with the compact gate: no quality gain** (gated pass 14.3 vs 15.7 of 40) and new failure modes (runaway answers, empties). Its only plus: fewer confident-wrong answers (1.0 vs 1.3 after the gate).
Lane: Anvil · Status: tested (offline, negative) · Priority: C
Axes moved:
- quality ≈/↓: after the gate, pass 16 / 16 / 11 vs Qwen's 16 / 15 / 16 (3 runs each).
- truthfulness ↑ slightly: CW after the gate 1 / 1 / 1 vs 3 / 0 / 1; raw CW 1.0 vs 2.3 per run. It self-abstains more (raw "refused" 6 / 3 / 6 vs 0).
- latency ↑ on phone (estimated from the hot set; desktop GPU median 1.6 vs 2.1 s per answer, not representative).
- stability ↓: 8/120 answers ran to the 512-token cap (copying the context) and 2/120 were empty, against 0 and 0 for Qwen.
Fits BOAR? iPhone 13: yes, easily (0.53 GiB hot: 0.105 GiB embedding lookup, 0.153 GiB untied head). llama.rn (`llama` arch, MiniCPM5 tokenizer). Apache-2.0. Offline: yes.
Evidence:
- **Offline replay** (`exp/compact-minicpm5/`): Kiln exp-01 `lantern52` (40 prompts with sources, contexts built for the 4B by app 3bb0a3f), node-llama-cpp 3.21.1, thinking off, compact-gate port of 0cfd4a77, precheck v2.2.

  | | Qwen2.5-1.5B (t0 / s1 / s2) | MiniCPM5-1B (t0 / s1 / s2) |
  |---|---|---|
  | raw pass | 21 / 17 / 19 | 18 / 16 / 15 |
  | raw CW | 3 / 1 / 3 | 1 / 1 / 1 |
  | pass after the gate | 16 / 15 / 16 | 16 / 16 / 11 |
  | CW after the gate | 3 / 0 / 1 | 1 / 1 / 1 |
  | raw answers with [n] | 26 / 20 / 25 | 22 / 21 / 21 |
  | ran to the 512 cap / empty (all runs) | 0 / 0 | 8 / 2 |

- Vendor/AA: MiniCPM5-1B AA phone score 45 (Kiln `answer-llms.md`). MiniCPM5-2B is AA-Omniscience −12, attempting only 29% ([AA, 2026-09-07](https://artificialanalysis.ai/articles/openbmb-releases-minicpm5-2b)). The self-abstention seen here fits that family trait.
- **Harness finding:** node-llama-cpp needed `budgets: { thoughtTokens: 0 }`. With only `enable_thinking=false` in the jinja parameters (what boar-eval's adapter sets, `adapter.ts` ~243–246), MiniCPM5-1B produced hidden thoughts and empty answers after ~19 s. **Any boar-eval arm with a MiniCPM5 model needs the same fix**, or it will measure thinking-on behaviour, as happened with Gemma (#2).
Test in boar-eval: not proposed. Only reconsider it if step 0 of `gemma4-e2b-compact-iphone` shows the iPhone ceiling below ~1.0 GiB, ruling out Qwen3-1.7B and Qwen3.5-2B.
Cost to try: done (≈ 15 min M1 Ultra GPU, 0.69 GB download).

## What would change this

- A boar-eval run with real compact-tier contexts. This replay used contexts built for the 4B, which are longer than what the compact tier gets, and the runaway answers copied context. The decode speed win on the phone stays real, but quality would have to be at least equal.

Shelf: row "MiniCPM5-1B GGUF" in `../../SHELF.md` (status → tested offline).
