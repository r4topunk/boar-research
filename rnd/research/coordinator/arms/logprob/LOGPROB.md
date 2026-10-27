# LOGPROB: does Qwen3-1.7B's token confidence flag its confident errors? (K0 MAIN n 97, diagnostic)

TL;DR: **NO.** Token-level confidence does not separate confident errors (CE) from other answers. All four features sit at AUC 0.52-0.53
(CI about 0.40-0.65), and at a 30 % flag rate they catch 8-9 of 27 CE, the same precision as random flagging (CE base rate 0.28).
On warned-only answers they do no better (AUC 0.47-0.50). The CE answers are as fluent as the correct ones. A typical CE is a short, smooth
false claim: "The Nile crocodile is larger than the saltwater crocodile" has mean logprob -0.018 and no token below p 0.5.
No confidence-gate arm follows from this.
Cost: one 97-item generation on the mini (4 min), 0 judge calls, 0 Opus, 0 paid.

- Criterion: `LOGPROB-criterion.md` sha256 `c80540f91470e261819e3c1eba80417a01558bb4aa2512ddb296343b68f2cea0`, committed with the patch and tools before generation (e52253f8).
- Patch: `logprob.patch` (sha256 `82de860a…`). It adds `logprobs: true, top_logprobs: 20` to the llama-server request and writes `<traces>.logprobs.jsonl`, one row per generate. The sampler is unchanged.
- Run: `tools/gen.sh` (LP-SCREENS mini job, slot gen1, 19:46-19:50, llama-server on an OS-assigned port started and stopped by the adapter, detector :8094 untouched). Analysis: `tools/analyze.py` -> `analysis.json`.
- Labels: the existing Haiku 5.5-low judgments of the mini control `lpctl-K0-main-s42` (CE, corr, warned).

## Byte-identity check
**97/97 answer texts are byte-identical to lpctl-K0-main-s42.** Requesting logprobs did not change decoding, so the control labels apply unchanged.
75 items have one generate each; 22 are answered by the deterministic layers with no LLM call (4 of them CE). Those 22 have no features and are never flagged.
On all 75 rows the concatenated tokens equal the generated content. On 17 items the generated content is not a literal substring of answer.text,
because the engine strips citation markers such as " [1]". Features are computed on the generated tokens, so those marker tokens (a handful per answer) are included.

## AUC, CE vs non-CE (pre-declared direction: lower confidence = flag; bootstrap B 2000 seed 11)
| Feature | All 97 (CE 27) | CI | Generated items only (75) | Warned only (39, CE 16) | CI |
|---|---|---|---|---|---|
| mean_lp (mean token logprob) | 0.525 | 0.398-0.651 | 0.453 | 0.497 | 0.311-0.680 |
| min_lp | 0.524 | 0.401-0.653 | 0.452 | 0.503 | 0.314-0.684 |
| ent20 (entropy, first 20 tokens) | 0.526 | 0.393-0.646 | 0.455 | 0.465 | 0.274-0.666 |
| low_p (share of tokens p < 0.5) | **0.530** (best) | 0.400-0.657 | 0.462 | 0.490 | 0.303-0.672 |

Medians on generated items, CE vs non-CE: mean_lp -0.183 vs -0.183, low_p 0.085 vs 0.088, ent20 0.148 vs 0.182 (CE answers are slightly *less* uncertain), tokens 46 vs 46.

## Flag-rate table (CE flagged / flagged; recall = of 27 CE; all 97)
| Feature | 10 % (k 9) | 20 % (k 19) | 30 % (k 29) | recall @30 % | mean corr flagged / unflagged @30 % |
|---|---|---|---|---|---|
| mean_lp | 3/9 | 6/19 | 9/29 (P 0.31) | 0.33 | 2.16 / 2.73 |
| min_lp | 3/9 | 6/19 | 9/29 (P 0.31) | 0.33 | 2.16 / 2.73 |
| ent20 | 2/9 | 7/19 | 8/29 (P 0.28) | 0.30 | 2.34 / 2.65 |
| low_p | 3/9 | 6/19 | 8/28 (P 0.29) | 0.30 | 2.25 / 2.68 |

Warned only (39 answers, 16 CE; k 3 / 7 / 11): at 30 % mean_lp 4/11, min_lp 5/11, ent20 5/11, low_p 3/11 (recall 0.19-0.31; CE base rate 0.41).

## Verdict (frozen rule)
**NO.** Best feature low_p: AUC 0.530 < 0.75, CI low 0.400 < 0.65, recall at 30 % 0.30 < 0.50. All three clauses fail.
Even an oracle gate on the 75 generated items could reach at most 23 of 27 CE; the features reach 8-9, which is chance level.

## Examples
High-confidence CE:
- `lan-cmp-005` "Which grows bigger, the saltwater crocodile or the Nile crocodile?" -> "The Nile crocodile is larger than the saltwater crocodile." (wrong, corr 1.0, no warning). mean_lp -0.018, min_lp -0.09, low_p 0.00.
- `vit-cry-009` (EIP-7251 validators for 10,000 ETH) -> "...after EIP-7251, the minimum remains 32 ETH but validators can stake in more flexible increments" (CE, corr 1.5). mean_lp -0.029, low_p 0.00.

Low-confidence correct:
- `lan-ref-002` "Which side won the American Civil War?" -> "The Union side won the American Civil War. The Confederacy was ultimately defeated..." (corr 5.0). mean_lp -0.184, min_lp -1.42, low_p 0.115, ent20 0.30. It is less confident than both CE examples.

## Deviations / notes
- Generation used a dedicated runner (`tools/gen.sh`, step 3 of lp-screens `run_arm.sh` only, same mini_gen.sh and slot lock), so no judge stage ran.
- Logprobs are the raw-logit probabilities that llama-server reports (post_sampling_probs off), not the sampler's temperature-0.7 distribution. Entropy uses the top 20 plus one residual bucket, so it is a lower bound.
- Labels come from a single Haiku judge run, whose noise on CE is about 5 % per item (SCREENS.md). That noise cannot explain a separation this close to 0.5.
