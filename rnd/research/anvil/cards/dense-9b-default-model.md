# A dense 7–9B (or newer 4B-class) default model for the 12 GB tier
TL;DR: no candidate beats Qwen3-4B-Instruct-2507 on what it answers from memory. Closed-book on v0.1 EN, 57 items, judge.v1, against the 4B through the same harness:
- **Qwen3.5-9B (no-think) ties:** 0.488 vs 0.487, with more confidently-wrong answers (38 vs 30).
- **Ministral 3 8B loses:** 0.457, cw 44 vs 30.

Both cost ~2.2× the 4B's decode time and ~6 GB of RAM. **Closed: the default-model lever does not move the ratio at ≤ 9B.**

Lane: Anvil · Status: tested (L1, closed-book screen; negative) · Priority: C

Axes moved:
- quality: ±0 to −0.03;
- truthfulness: worse (cw 38–44 vs 30);
- latency: ×2.2 decode (mini CPU: 11 tok/s Ministral vs 24 tok/s 4B), est. 4–8 tok/s on a 12 GB phone;
- resources: +2.7–3.2 GB, which needs `no_extra_bufts` (with repack the load peak is ~11 GB, a low-memory kill).

Fits BOAR? It runs: `mistral3` landed in b7216 and `qwen35` in b7990, so both are in llama.rn rc.4's b11010. But the bounty pays for quality, and there's none to buy here.

Evidence:
- **Screen design** (`exp/outofkit/`):
  - same recipe as the harness's Claude anchors: `anchor.v1` system prompt, the bare question, no tools; app sampler 0.7/40/0.95/0.05, seed 42; thinking off;
  - every model through the same server or node harness, judged by judge.v1 (Opus, both orders) against the frozen v0.1 refs.
  - **Validated:** on the 24-item out-of-kit slice, closed-book 4B = 0.422 (node) / 0.418 (server) vs the real engine's 0.440 on the same items. Out of kit, the engine is a memory answer.

  | system (EN) | slice 24 | all 57 | pass / cw / fail (57) |
  |---|---|---|---|
  | Qwen3-4B-2507 (control, server b11010) | 0.418 | **0.487** | 10 / 30 / 17 |
  | current engine (4B, main, 3 seeds) | 0.440 | 0.507 | 15 / 17 / 25 |
  | **Qwen3.5-9B** no-think (5.68 GB) | 0.459 | **0.488** | 8 / 38 / 11 |
  | **Ministral 3 8B** 2512 (5.20 GB) | 0.400 | **0.457** | 3 / 44 / 10 |
  | Haiku no-web (frontier anchor) | 0.593 | 0.653 | 20 / 17 / 20 |
  | Sonnet / Opus no-web | 0.956 / 1.039 | — | — |

- **The slice's +0.04 for Qwen3.5-9B was noise.** The all-57 read is a tie. 1-rep L1 on 24 items can't resolve < ~0.08.
- **The desk evidence** (`exp/outofkit/models.md`) predicted this: AA-Omniscience accuracy 14.7% vs 12.7%. The higher TriviaQA (base 68 vs 53) did not transfer for Ministral.
- **Not tested, by the desk evidence:** Qwen3.5-4B (≈ baseline on Omniscience), Gemma 4 E4B (contradictory, not adopted before), SmolLM3, LFM2.5-8B-A1B (reasoning-only: it gave an empty answer in non-thinking use).
- **Ministral fairness check, done:** at its recommended temperature 0.1, slice 0.414 vs 0.418 (cw 20 vs 15). Still no gain; the negative holds.

What would revive it: a ≤ 9B model with a published closed-book SimpleQA / AA-Omniscience accuracy clearly above ~20%.

Next: the lever is knowledge in the kit, not the reader. See `exp/oracle/` (the 4B with gold passages).
