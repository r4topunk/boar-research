# PHIFIRST: phi_first on the LOGPROB traces (0 model calls, 0 judge calls)

## TL;DR
Verdict **NO**. Best variant AUC 0.488 (CI 0.368-0.601), recall of CE at a 30 % flag rate 0.185 (needs 0.50). On generated items only, AUC is 0.37-0.40 (direction inverted:
CE answers have a *more* peaked first token, mean phi 0.972 vs 0.913 for the rest). The paper's 0.82 does not transfer to this setup.

## Definition used (arXiv 2605.05166 Sec. 2.1, HTML)
t* = first content-bearing token; top-K probabilities renormalized; H = -sum p log p; phi_first = 1 - H/log K (high = confident). Paper K = 100; **K = 20 here** (stored top-20, renormalized).
Flag score = -phi. Criterion: PHIFIRST-criterion.md (sha256 3ff3394f...d9f6, committed before computing as b76a546f). Labels and no-generate treatment identical to LOGPROB (97 items, 27 CE,
75 with a generate, 23 CE among them; 22 deterministic-layer items never flagged).

## Caveats
- Traces sampled at temperature 0.7, not greedy; logged probabilities are the raw distribution. For P1 the first-token distribution is prefix-independent, so it equals the greedy one; the answer text, however, is a sampled one.
- K = 20, not 100. Model 1.7B, not 7-8B; LITEPACKS MAIN set with retrieved context (not closed-book); labels from Haiku-low.
- No generated warning prefix exists (engine-prepended), and every generate starts with an alphanumeric token, so P2 start = P1 start in all 75 items (P1 and P2 are identical). Many first tokens are word fragments ("Mo", "Gr") with p near 1, which mechanically inflates phi.

## AUC (CE positive, bootstrap B 2000 seed 11)
| variant | AUC all 97 | 95 % CI | AUC generated-only (n 75) |
|---|---|---|---|
| P1 phi_first | 0.488 | 0.368-0.601 | 0.395 |
| P2 phi_first_content (= P1 here) | 0.488 | 0.368-0.601 | 0.395 |
| P3 phi_first3 (mean of first 3 content tokens) | 0.475 | 0.354-0.589 | 0.374 |

(LOGPROB best was low_p 0.530.)

## Flag rate (CE total 27 of 97)
| variant | rate | flagged | CE flagged | precision | recall |
|---|---|---|---|---|---|
| P1/P2 | 10 % | 9 | 0 | 0.00 | 0.00 |
| P1/P2 | 20 % | 19 | 2 | 0.11 | 0.07 |
| P1/P2 | 30 % | 29 | 5 | 0.17 | 0.19 |
| P3 | 10 % | 9 | 2 | 0.22 | 0.07 |
| P3 | 20 % | 19 | 3 | 0.16 | 0.11 |
| P3 | 30 % | 29 | 6 | 0.21 | 0.22 |

## Verdict
NO (AUC < 0.75, CI low < 0.65, recall@30 % < 0.50). Closed: the first-token entropy signal does not separate Qwen3-1.7B's confident errors; combined with LOGPROB, token-level confidence is not a gate here.
Not tested: K = 100, greedy decode, closed-book prompts, larger model.

Script: tools/phifirst.py (reuses arms/logprob/tools/analyze.py); results: analysis.json.
