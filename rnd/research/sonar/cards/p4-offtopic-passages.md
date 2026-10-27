# P-4: off-topic passages in the 4B's prompt. Measured; the cheap drop rule is safe but weak → recommend NOT running it
TL;DR: In `and-qwen-s44`'s real prompts, 33 of 53 passages (62%) don't address what the question asks (31 same-subject, 2 off-topic). The best cheap signal, question ↔ passage cosine (AUC 0.77), can drop 5 of them at no cost to helpful or key-bearing passages, never emptying the context. But it touches only 1 of Compass's confident-wrong target items: their passages are same-subject and score 0.60–0.74, inside the helpful band. The lever for those items is recall (retrieving the passage that holds the fact), not removal. Criterion frozen as requested; recommendation: don't spend an arm.
Lane: Sonar (same-model pipeline, context assembly) · Status: evidence + frozen criterion, **recommend not run** · Priority: C
Axes moved, if run:
- truthfulness: confident-wrong on target items likely unchanged (1 target passage dropped);
- quality ≈ 0 (5 unhelpful passages removed bench-wide);
- latency **+**: passage cosine for format-2 passages needs query-time embeddings (≈ 2.3 passages per question; bge-small ~15–20 ms per ~250-token passage on desktop, ~17× on the iPhone, Android UNKNOWN). Not ~0.

Evidence (`exp/19-offtopic-passages/`):
- **Data:** 53 (question, passage) pairs: every passage in the 59 prompts of Kiln's `and-qwen-s44.prompts.jsonl` (Android 4B, kit A; exact prompt text). s42/s43 retrieval is identical (deterministic).
- **Labels** (`labels.json`): an independent Opus rater (clean subagent, no other files) labelled each pair helpful / same-subject-unhelpful / off-topic, judging only whether the passage addresses what the question asks.
  - Result: **20 helpful, 31 same-subject-unhelpful, 2 off-topic.** 19 of the 30 items with passages carry at least one unhelpful passage.
- **Signals** (`signals.json`, `analysis.txt`), AUC helpful > unhelpful:

  | Signal | AUC |
  |---|---|
  | question ↔ passage cosine (bge-small) | **0.773** |
  | question ↔ "title > section" cosine | 0.694 |
  | question ↔ article lead cosine (pack lead vectors) | 0.526 |
  | compression's best-sentence score | 0.542 |
  | prompt position | 0.511 |

- **Never-empty drop rule** (drop passages below τ, but always keep the item's best one), over 53 passages:

  | τ (passage cos) | unhelpful dropped | helpful dropped | key-bearing dropped |
  |---|---|---|---|
  | 0.60 | **5/33** | **0/20** | **0** |
  | 0.65 | 8/33 | 1/20 (Volcanoes) | 0 |
  | 0.70 | 11/33 | 2/20 | 1 |

- **Compass's target items** (`targets.txt`; confident-wrong memory claims beside unhelpful passages, from `compass/exp/p3-nli/ceiling.md`):
  - vit-trv-003: Chiang Mai 0.667 / 0.597; only the second drops at 0.60, and the first stays;
  - vit-cry-002: EIP-8369 0.631;
  - lan-cmp-003: India 0.703;
  - lan-exp-002: Montenegro 0.743, labelled helpful;
  - vit-hum-005: Kirkcaldy, not in the s44 prompts.
  - So at 0.60 the rule removes 1 target passage on 1 item and leaves the item with an unhelpful passage. The model writes its memory claim either way.
- **Why the targets can't be separated cheaply:** they are same-subject passages (the right city, the right protocol family, the right country) that lack the asked fact. Lexical and embedding similarity both rate them as on-topic. Only reading for the asked aspect separates them, and the 4B can't do that reliably (P3-0: 8/20 false flags).
- **The lever that does reach some of them is recall.** CORRECTED 2026-10-02 evening: P-1b does *not* bring the Mae Hong Son Loop passage (its vit-trv-003 gain was a key-term false positive; P-1b withdrawn). The genuine recall fix for vit-trv-003 is `p5-travel-from-to`: the "get from X to Y" travel detector puts Pai §Get in > By bus first.

Frozen criterion (arm `p4-drop060`, in case the coordinator wants the measurement anyway; Android 4B, kit A, vs `and-qwen`, 0cfd4a77):
1. Confident-wrong on the target items (vit-trv-003, vit-cry-002, lan-cmp-003, lan-exp-002, vit-hum-005), summed over 3 seeds: **down by ≥ 2** vs base.
2. **0 items emptied** (by construction) and **0 shown sources lost** among passages labelled helpful in `labels.json`, and 0 key-bearing passages lost.
3. Whole-bench paired Δratio ≥ −MDE.
4. Gate PASS v0.5; 0 new safety hits.
5. Retrieval + assembly p50 ≤ 1.2× base (the query-time passage embeddings count here).
- Predicted outcome (stated now): 1 FAILS (≤ 1 target passage removed), and 5 is at risk. Hence the recommendation not to run.

## Details
- The rule only drops passages already in the prompt: it never removes the last one (the #5/#17 lesson), and with τ = 0.60 it never removed a helpful or key-bearing passage on this data.
- If Kiln ever adds query-time passage embeddings for another reason, the 0.60 drop is a free +5 unhelpful passages removed. Revisit then.
- Labels are one rater's. The 31 "same-subject-unhelpful" are the important class, and the rubric was given verbatim (`pairs-for-rater.json` + the prompt in LOG).
