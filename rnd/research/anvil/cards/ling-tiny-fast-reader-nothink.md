# Ling-3.0-tiny (thinking off) as the 12 GB reader, to pay for longer answers with faster decode
TL;DR: if the complete-paragraph persona (QUEUE #12) wins on the 4B but triples answer time, swap the reader for Ling-3.0-tiny with thinking forced off. It is an in-RAM MoE (7.9B total / 1.3B active) that decoded **59 vs 22 tok/s** on the same M4 CPU and read "about as well" as Qwen3-4B in exp-01. The bet: the same quality as 4B+persona at ~40% of the total time.
Lane: Anvil · Status: closed (S1 K4 fired after Maple #15 failed; the MoE-reader line is closed for this bounty) · Priority: C
Axes moved:
- **latency ↑ (better):** total time p50 5.0 vs 10.5 s with the same contexts (exp-01, M4 CPU, short answers). The gain grows with answer length, because decode dominates.
- **quality ≈/↓:** −7.9 pp pass on factual 38 vs the 4B (23 vs 26 of 38, p = 0.51, not significant). Judge ratio 0.48 vs 0.53 on 7 hard pairs. Never measured on the shared engine.
- **resources ↓ (worse):** anonymous footprint 4.58 GiB vs 3.03 GiB; peak RSS 5.93 GB, under the 6 GB bar by ~1%.
- **truthfulness:** vendor non-hallucination 69.5% (Kiln `answer-llms.md`, vendor claim); CW in exp-01 7 vs 7 of 38. ≈.
- safety: UNKNOWN.
Fits BOAR? Android 12 GB: yes. iPhone: no. llama.rn rc.4 (b11010) has `bailingmoe3` (merged 2026-08-17). The Ling chat parser [#28682](https://github.com/ggml-org/llama.cpp/pull/28682) landed after b11010, which matters only when thinking is on. MIT. 4.82 GB file. Offline: yes.
Evidence:
- **exp-01** (`rnd/kiln/exp-01-inram-moe-reader/README.md`, Kiln 2026-09-30): same app contexts, M4 CPU ×4, `enable_thinking=false`, 0 reasoning tokens in all answers. Ling TTFT p50 4.1 s, total 5.0 s, decode 59 tok/s, against Qwen3-4B 7.7 / 10.5 s and 22 tok/s. "Correct answers per minute" 6.0 vs 3.1.
- **D3** (`rnd/kiln/d3-android-reader.md`): Ling "NO-GO" under the ±5 pp rule on factual 38 (−7.9 pp, McNemar p = 0.51). D3 also flags that "it cannot run in the app the way it was measured without a code change, because the fast tier turns thinking on". Cycle 10 confirmed this on the shared engine: `gen.thinking = true` with a 256-work budget for every fast-tier model.
- **Why revisit now:**
  1. The decision instrument changed. boar-eval's judged ratio with MDE 0.036 replaced the factual-38 ±5 pp rule, and a −7.9 pp non-significant gap on 38 items is compatible with "no difference".
  2. If #12 shows that longer answers are what moves the ratio on the 4B tier, decode speed becomes the cost driver. Ling's 2.7× decode is the cheapest way to pay it.
- Off-repo: a user report has Ling-3.0-tiny at ~10 tok/s on a 2017 i5 laptop CPU at Q6 ([Ken Ashe blog, 2026-09-26](https://kenashe.ai/blog/2026-09-26-ling-3-0-tiny-makes-old-cpus-interesting-again), accessed 2026-10-02; anecdotal). No Android phone number exists for this model (UNKNOWN).
Test in boar-eval (only after #12 reports):
- Arms on the Android 12 GB profile, 2 seeds each, full mode, persona = #12's winner (or succinct if #12 fails):
  - `4B+persona` (= #12's arm, reuse its runs);
  - `ling+persona` with **`enableThinking: false` on the fast tier**. This needs a small engine/adapter option, because today the fast tier forces thinking with budget 256.
- Latency must be read as first *visible* text (the harness fix assigned 2026-10-02).
- **Success criterion (stated before any run):**
  1. ratio of `ling+persona` ≥ `4B+persona` − 0.036 (non-inferior within the MDE);
  2. total time p50 ≤ 0.6× `4B+persona` on desktop CPU ×4;
  3. first visible text p50 ≤ 1.0×;
  4. confident-wrong not higher by more than 1 per run;
  5. unsafe on the 17 danger items ≤ `4B+persona`;
  6. peak RSS ≤ 6 GB with `--cache-ram 0`.
  - Fail on any one = not adopted.
Cost to try:
- 4.82 GB download (coordinator OK; the mini is at ~19 GiB free).
- ~1 h of runs plus ~150 judge calls.
- A one-line "fast-tier thinking off for this model" option in the adapter or engine. The same switch fixes the product note on Gemma (cycle 10).

## What would make it fail

- Ling reads worse on the shared engine's longer, persona-shaped prompts than on exp-01's short ones (criterion 1).
- KDA linear attention plus MLA: prefill on ARM phone CPUs is UNKNOWN. exp-01's prefill was on M4 CPU only.
- 5.93 GB peak RSS leaves little headroom on 12 GB phones running other apps. LMK kills are a real risk; the device run must watch for them (CR-2 load marker).
- With thinking forced off, quality may drop below the vendor's thinking-mode numbers. exp-01 already measured thinking-off, so this risk is priced in.

Shelf: rows "Ling-3.0-tiny GGUF" in `../../SHELF.md`.
