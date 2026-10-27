# Citation rule + one-shot cited exemplar in the cached answer prefix (compact 1.5B)
TL;DR: tell the 1.5B to end every sourced sentence with [n] in the source's own words, plus a one-shot cited example in the KV-cached prefix, so fewer answers die at the compact citation gate — **tested offline: no measurable effect; the gate's declines come from retrieval misses, not from missing [n]**.
Lane: Anvil · Status: tested (offline replay, negative) · Priority: C
Axes moved: quality ≈ (gated pass 15.7 → 16.7 of 40, mean of 3 runs per arm, inside seed noise of ±4) · truthfulness ≈ (confident-wrong after gate 1.3 → 2.0 of 40) · latency ≈ (the exemplar is in the prefix BOAR keeps prefilled, `answerPromptPrefix` + `setAnswerPrefix`; ~90 extra prefix tokens, paid once per model load) · retrieval/safety/resources/stability: none.
Fits BOAR? Yes, prompt-only (`src/rag/pure.ts` CONTEXT_INSTRUCTION + exemplar before `Context:`), any device, offline. It just doesn't help.
Evidence:
- ALCE (Gao et al., EMNLP 2023, [arXiv 2305.14627](https://arxiv.org/abs/2305.14627)), App. G.3 / Table 16, ASQA, ChatGPT: citation recall **69.3 (0 demos) → 74.6 (1 demo) → 73.6 (2 demos)**, precision ~73 flat, correctness 41.9 → 39.8 → 40.4. "Using at least one demonstration ensures high citation recall"; for original LLaMA "more demonstrations lead to better performance" (numbers not legible in the PDF text). Strength: moderate for "≥ 1 demo helps recall"; nothing on 1–2B models.
- MAM-AI (withdrawn, [arXiv 2606.29580](https://arxiv.org/abs/2606.29580)): prompt redesign "cuts deflection from 33% to 3%" with Gemma 4 E4B. Abstract only; weak.
- **In-repo diagnosis (this card, 2026-10-01):** the night D10 run (iPhone 13, 611a4b9, kit A, `rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0.jsonl`) has 24/60 declines: **12 `all-citations-removed`** (the 1.5B wrote [n] but the cited source lacks ≥ 50% of the sentence's key words), **6 `uncited-with-sources`** (no [n] at all), 5 no-source, 1 false-claim. So "the model doesn't cite" is the minority; "it cites a source that doesn't say it" is the majority.
- **Offline replay (this card):** `exp/cite-exemplar/` — 40 captured app prompts with sources (Kiln exp-01 `capture/lantern52.jsonl`, app 3bb0a3f contexts), Qwen2.5-1.5B Q4_K_M via node-llama-cpp 3.21.1 (Metal, M1 Ultra), scored by a JS port of the shared engine's gate (`0cfd4a77` `citations.ts` + the compact branches of `answer.ts`), graded by Lantern's precheck v2.2.

  | Arm (temp/seed) | raw pass | raw CW | gate declines | pass after gate | CW after gate |
  |---|---|---|---|---|---|
  | A0 baseline (0/42) | 21 | 3 | 16 | 16 | 3 |
  | A0 (0.7/1) | 17 | 1 | 18 | 15 | 0 |
  | A0 (0.7/2) | 19 | 3 | 18 | 16 | 1 |
  | A1 rule only (0/42) | 21 | 3 | 16 | 15 | 3 |
  | A2 rule + exemplar (0/42) | 23 | 3 | 17 | 18 | 3 |
  | A2 (0.7/1) | 16 | 2 | 16 | 13 | 2 |
  | A2 (0.7/2) | 24 | 3 | 20 | 19 | 1 |

  (pass after gate counts precheck's `refuse_ok` items.) The raw [n] rate does not rise: 26/40 (A0), 28 (A1), **20 (A2)** at temp 0 — the exemplar made the 1.5B cite *less*. Same-arm seed spread (A2: 16 vs 24 raw pass) is bigger than any arm difference.
Test in boar-eval: not proposed. If someone wants it anyway: gate mode, arm = `CONTEXT_INSTRUCTION` swap + exemplar (text in `exp/cite-exemplar/run.mjs`), success = gate declines on bench public −5 or more with CW not up, ≥ 2 runs per arm.
Cost to try: done (≈ 15 min of M1 Ultra GPU, no download).

## What the replay says about the gate (hand-off to Compass, not my lane)

- In A0 at temp 0, the gate's 16 declines were **5 correct raw answers** (Japan ~126 M, giraffe, Mill's harm principle, healthy-life advice, most populous countries — memory answers with a reflexive "[1]" after an off-topic source), **10 incomplete** (fail-missing), **0 confident-wrong**. All 3 confident-wrong answers passed the gate because their [n] had lexical support.
- Across the 3 A0 runs: correct answers lost per run 5 / 2 / 3, confident-wrong caught 0 / 1 / 2. That is ~3 right answers lost per wrong answer caught — the same ratio the code comment in `answer.ts` records for the 4B's uncited-line ("cost the 4B 4 right answers per wrong one caught").
- Why prompting can't fix it: these answers are memory answers to questions the retrieved passages don't cover (e.g. "Why does Gríma kill Saruman?" against four *Lord of the Rings tourism* passages). No instruction makes a source support a fact it doesn't contain. The levers are retrieval (Sonar) or gate calibration (Compass: calibrated abstention / NLI support check instead of key-word overlap).

## What would have made it work (and didn't happen)

- If most declines had been `uncited-with-sources` with a supporting source present, a stronger cite rule would convert them. Only 6/24 (device) and 1–5/40 (replay) were of that kind, and `attributeCitations` already rescues uncited sentences with ≥ 75% support.

## Caveats

- Contexts were built for the 4B by app 3bb0a3f, not by 0cfd4a77 for the 1.5B (the compact tier may compress differently). node-llama-cpp's Qwen chat wrapper ≠ llama.rn's jinja path byte-for-byte. Gate port omits health, wrong-script, false-claim and topic-guard paths (none of the 40 are health items). n = 40, 3 runs per arm.
- UNKNOWN: whether a *fine-tuned* citer (Pleias-RAG-1B, literal-quote `<ref>` syntax, [arXiv 2504.18225](https://arxiv.org/abs/2504.18225)) would pass the lexical gate more often — it quotes sources verbatim, which this gate rewards — but it can't add facts the sources lack either, and its multi-section reasoning output would cost seconds on the iPhone.

Shelf: row "Pleias-RAG-1B GGUF" in `../../SHELF.md`.
