# Notes-first capped reasoning (Chain-of-Note style prompt) for the 12 GB reader
TL;DR: have Qwen3-4B write ≤ 40 words of source notes ("Notes: [n] says…" or "none relevant") before "Answer:", a prompt-only stand-in for capped thinking. **Tested offline: no gain**, and it delays the visible answer.
Lane: Anvil · Status: tested (offline, negative) · Priority: C
Axes moved:
- quality ≈/↓: precheck pass 26 → 24 of 40 (greedy).
- truthfulness ≈: confident-wrong 2 → 2.
- latency ↓: first answer token +0.63 s median on an M1 Ultra GPU, which is roughly +3–5 s on phone CPU (UNKNOWN). The notes are hidden tokens the user waits for.
- safety, retrieval, resources: none.
Fits BOAR? Yes, prompt-only; the app would have to hide the "Notes:" part. Offline: yes.
Evidence:
- **Chain-of-Note** (Yu et al., Tencent, [arXiv 2311.09210](https://arxiv.org/abs/2311.09210), accessed 2026-10-01): "+7.9 EM given entirely noisy retrieved documents" and "+10.5 in rejection rates" for out-of-scope questions. **But it was fine-tuned** (ChatGPT-made notes → LLaMA-2 7B), not prompted. Strength: moderate for the fine-tuned version, none for prompting.
- Kiln K4 (`rnd/kiln/hypotheses.md`): always-on thinking on LFM2.5-8B-A1B gave 85% `<think>` output, TTFT 27 s and 4/17 empty answers. Capped thinking was never tried. This card is the cheapest capped variant: the capping is in the prompt, there is no thinking model, and the reader is the same one.
- **Offline replay (this card, `exp/notes-first/`):**
  - Setup: 40 captured app prompts with sources (Kiln exp-01 `lantern52`, built for Qwen3-4B by app 3bb0a3f), Qwen3-4B-Instruct-2507 Q4_K_M, greedy, graded by precheck v2.2.

  | Arm | pass | CW | fail-missing | output tokens (median) | first answer token (median) |
  |---|---|---|---|---|---|
  | N0 as captured | 26 | 2 | 12 | 70 | 2.08 s |
  | N1 notes first | 24 | 2 | 14 | 67 (4 of them notes) | 2.71 s |

  - The two lost passes were both "notes" items where the answer got shorter. N1 never turned a fail into a pass.
  - One run per arm at temp 0. Not repeated at temp 0.7: the direction is null-to-negative, and the latency cost holds whatever the sampling seed.
Test in boar-eval: not proposed.
Cost to try: done (≈ 6 min of M1 Ultra GPU).

## Side signal for Compass: the model's own "none relevant" note

- In N1 the 4B wrote **"Notes: none relevant" on 22/40** items. It is a free, model-side read of whether the retrieved sources cover the question.
- Those 22: 13 still passed from memory, 7 fail-missing, **2 confident-wrong**.
- The 17 items with real notes: 10 pass, 7 fail-missing, **0 confident-wrong**.
- n is tiny (2 vs 0 CW), so this is a hint, not evidence. If Compass builds an answerability gate, the note is a candidate feature next to the retrieval scores (their queue #4 "calibrated abstention"). It costs ~4 output tokens, not 40, because the note is usually just "none relevant".
- It also agrees with the cycle-2 replay: **most retrieved contexts in this sample don't contain the answer**, so prompt tricks on the reader can't fix them (see `citation-exemplar-prompt`).

## What would have made it work

- A reader fine-tuned to write notes, as in the paper. That is the LoRA/distillation item on the radar, parked: > 1 day of work, and the replay shows the bottleneck is upstream (retrieval coverage), not reading.
