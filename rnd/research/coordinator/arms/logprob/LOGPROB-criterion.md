# LOGPROB criterion (frozen 2026-10-20 before the generation)

## Question
Qwen3-1.7B with compact declines released behind the warning line (LITEPACKS system, pack set K0) makes confident errors (CE) on 27/97 MAIN items
(mini control lpctl-K0-main-s42). Does the model's own token-level confidence separate its CE answers from the rest well enough to drive a gate
(stronger warning or "I don't know")? Diagnostic arm: no system change is proposed here.

## Run
- Regenerate the mini K0 MAIN control (arms/lp-screens/main-97.ids, sha256 9664d81fdf182603617d31d75b34eaa8fcb1eeb5f0fa87e68352e1fe09d2a462;
  same LITEPACKS requests via lp-screens/tools/mkreq.py, seed 42, mini tree be-0cfd4a77-cut7-litepacks, lp-screens/tools/mini_gen.sh slot lock)
  with arms/logprob/logprob.patch (sha256 in logprob.patch.sha256): the llama-server request adds `logprobs: true, top_logprobs: 20`
  (`n_probs: 20` on /completion); the stream's per-token logprobs are written to `<traces>.logprobs.jsonl` (one row per generate). Sampler unchanged.
- Byte-identity check: answer.text of every item vs lpctl-K0-main-s42. Labels are valid only on identical text; non-identical items are excluded
  and listed. If fewer than 90 of 97 are identical, the verdict is VOID (requesting logprobs changed decoding) and no gate conclusion is drawn.

## Labels (0 new judge calls)
The existing Haiku 5.5-low judgments of the control (lp-screens/control/aggregates/lpctl-K0-main-s42.json): CE (not declined, correctness mean
over both orders <= 1.5), corr, warned. Never Opus, never paid APIs.

## Features (answer body = the visible generated tokens of the item's last generate; the warning line is prepended by the engine, not generated)
mean_lp (mean sampled-token logprob), min_lp, ent20 (mean entropy over the first 20 tokens from the top-20 probabilities + one residual bucket),
low_p (share of tokens with p < 0.5). Direction pre-declared: lower confidence = flag (scores -mean_lp, -min_lp, +ent20, +low_p); AUC never flipped.
Items with no generate (deterministic layers: 22 of 97 in the control, 4 of them CE) have no features and count as never flagged
(most-confident score) in the primary analysis. Also reported: AUC on generated items only.

## Decision rule (tools/analyze.py, committed with this file)
GO (design a confidence-gate arm next) iff the best single feature (highest AUC on the identical items, all of them) has
AUC >= 0.75 for CE vs non-CE AND bootstrap CI low >= 0.65 (item bootstrap, B 2000, seed 11, 2.5 / 97.5 percentiles)
AND, at the threshold that flags at most 30 % of all answers (k = floor(0.30 x n), tie groups at the boundary excluded), recall of CE >= 50 %.
Otherwise NO. Reported: every feature's AUC + CI, precision/recall at flag rates 10 / 20 / 30 %, the same on warned-only answers (not part of the rule).

## Budget
calls_cap: Haiku 0 / Opus 0
