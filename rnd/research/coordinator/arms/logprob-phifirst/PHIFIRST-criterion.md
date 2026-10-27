# PHIFIRST criterion (frozen 2026-10-20 before computing; 0 model generation, 0 judge calls)

## Question
arXiv 2605.05166 reports phi_first (single greedy decode, first content-bearing answer token) at mean AUROC 0.820 at 7-8B on closed-book QA.
Does phi_first, computed on the stored LOGPROB traces of Qwen3-1.7B (K0 MAIN s42, 97 items, 75 with a generate), separate confident errors (CE) from the rest?

## Definition (paper Sec. 2.1, from the arXiv HTML)
t* = first content-bearing token (skipping whitespace, punctuation, chat-template prefixes such as "Answer:"). Top-K probabilities at t* renormalized to p~,
H = -sum p~ log p~, phi_first = 1 - H / log K (high = confident). Paper K = 100; stored data has top-20 only, so **K = 20** (renormalized over the 20 stored,
H / log 20). The softmax is the model's full-vocabulary one (llama.cpp raw logprobs), then top-20 kept and renormalized.
Flag score = -phi_first (low confidence = flag); AUC never flipped.

## Variants
- P1 `phi_first`: the first generated token of the item's last generate (the warning line is engine-prepended, not generated).
- P2 `phi_first_content`: first token t* whose text has an alphanumeric char, after dropping a leading "Answer:"-style prefix or warning-looking line if generated.
- P3 `phi_first3`: mean of phi over the 3 tokens starting at t*.

## Caveats (stated in the report)
Traces were sampled at temperature 0.7, not greedy; logged probabilities are the raw distribution, so the decoded token may differ from the argmax, and the distribution at t* is the one
of a sampled prefix only for t* = first token (P1, no conditioning issue); P3 later tokens condition on sampled tokens. K = 20 not 100 (entropy over a truncated tail is slightly lower).
Model is 1.7B, not 7-8B; items are the LITEPACKS MAIN set with context (not closed-book).

## Labels / treatment: identical to LOGPROB (arms/logprob/LOGPROB-criterion.md)
Existing Haiku-low labels (CE = not declined, correctness mean <= 1.5), 97 items, 27 CE; the 22 items with no generate count as never flagged (most-confident); also AUC on generated items only.

## Decision rule (same as LOGPROB)
GO iff the best variant has AUC >= 0.75 AND bootstrap CI low >= 0.65 (item bootstrap, B 2000, seed 11, 2.5/97.5 pct) AND at the threshold flagging at most 30 % of all answers
(k = floor(0.30 n), tie groups at the boundary excluded) recall of CE >= 0.50. Otherwise NO. Reported: AUC + CI per variant, precision/recall at 10/20/30 %.
Budget: Haiku 0 / Opus 0.
