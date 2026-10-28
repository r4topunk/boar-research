# XFAM comparison

Reporter uses an in-memory Bench compatibility subclass for the manifest-based items layout and excludes the seven venue-list items, which are outside the 51-item judge comparison. The original reporter, scorers and inputs remain unchanged. Model: `gpt-5.6-sol`; CLI: `codex-cli 0.144.3`; judge: `judge.v1-codex`. [usage detail removed]. Fixed high reasoning effort; CLI temperature control unavailable. Seed 7 for A/B start order; two generation seeds (42, 43), 51 items, both orders, 408 successful calls. Pilot rows reused. No new answer generation.

Ratios and their CIs are from unmodified `harness/report.py`, with `--repeat`, seed 11 and 2000 two-level bootstrap resamples. Both orders are combined with the unmodified vendored judge core; scores are averaged and winner disagreement becomes a tie. Two-seed point estimates use per-item seed means. Win rates average the two seed-specific combined-order outcomes; a win scores 1, tie 0.5, loss 0.

Call audit: one completed CLI attempt was discarded by an adapter false positive that scanned successful output for 429. The classifier was corrected to inspect only failed-call diagnostics (local commit 4c4d379); the missing pair was rerun with identical judging settings. The 408 stored verdicts exclude that discarded attempt. All attempts remain in the call logs.

| Arm | Judge | Raw ratio | Raw 95% CI | Floor-adjusted ratio | Floor 95% CI | Win rate | Tie rate | Loss rate | Win score |
|---|---|---|---|---|---|---|---|---|---|
| K | Codex | 0.49670024 | 0.44922098, 0.54678948 | 0.36082929 | 0.30016238, 0.42286769 | 0.00980392 | 0.01960784 | 0.97058824 | 0.01960784 |
| K | Claude | 0.41332885 | 0.37826389, 0.44698233 | 0.26112760 | 0.21736737, 0.30273692 | 0.00000000 | 0.00000000 | 1.00000000 | 0.00000000 |
| H | Codex | 0.66748252 | 0.62109609, 0.71069211 | 0.57695730 | 0.51856011, 0.63174138 | 0.00000000 | 0.04901961 | 0.95098039 | 0.02450980 |
| H | Claude | 0.55251604 | 0.52167649, 0.58431591 | 0.43593018 | 0.39638806, 0.47631644 | 0.00000000 | 0.00000000 | 1.00000000 | 0.00000000 |

Paired H − K uses shared item draws, averaging seeds within each item first; percentile bootstrap over items, 2000 resamples, seed 1. This interval represents item variation conditional on these two generation seeds.

| Judge | Raw H − K | Raw 95% CI | Floor-adjusted H − K | Floor 95% CI |
|---|---|---|---|---|
| Codex | 0.17078227 | 0.12254031, 0.21902359 | 0.21612801 | 0.15453551, 0.27716791 |
| Claude | 0.13918720 | 0.09989568, 0.17841587 | 0.17480259 | 0.12585617, 0.22384586 |

Spearman correlations use midranks for ties (12-decimal rounding removes floating-point averaging noise) across 51 items, after averaging both orders and both generation seeds. Score correlation compares BOAR mean rubric scores; ratio correlation compares BOAR/reference per-item ratios.

| Arm | Score Spearman rho | Ratio Spearman rho |
|---|---|---|
| K | 0.91770568 | 0.88308959 |
| H | 0.88455343 | 0.71860008 |

## Numeric summary key

Lines 1–2: successful verdicts, attempts, failed attempts, tool calls; then items, generation seeds, arms, order seed, reporter bootstrap seed, paired bootstrap seed, resamples.
Lines 3–6: K Codex, K Claude, H Codex, H Claude; columns raw ratio, floor-adjusted ratio, win, tie, loss.
Lines 7–8: Codex, Claude; columns raw H−K, lower CI, upper CI, floor-adjusted H−K, lower CI, upper CI.
Lines 9–10: K, H; columns score Spearman rho, ratio Spearman rho.

## Numeric summary

```
408 409 1 0
51 2 2 7 11 1 2000
0.49670024 0.36082929 0.00980392 0.01960784 0.97058824
0.41332885 0.26112760 0.00000000 0.00000000 1.00000000
0.66748252 0.57695730 0.00000000 0.04901961 0.95098039
0.55251604 0.43593018 0.00000000 0.00000000 1.00000000
0.17078227 0.12254031 0.21902359 0.21612801 0.15453551 0.27716791
0.13918720 0.09989568 0.17841587 0.17480259 0.12585617 0.22384586
0.91770568 0.88308959
0.88455343 0.71860008
```

## Per-item scores

| Id | K Codex score | K Claude score | H Codex score | H Claude score |
|---|---|---|---|---|
| vpara-001 | 2.83333333 | 2.16666667 | 2.91666667 | 2.08333333 |
| vpara-002 | 2.41666667 | 2.33333333 | 2.66666667 | 2.33333333 |
| vpara-003 | 2.41666667 | 1.66666667 | 2.58333333 | 2.16666667 |
| vpara-004 | 4.16666667 | 3.41666667 | 4.33333333 | 3.41666667 |
| vpara-005 | 2.75000000 | 2.33333333 | 2.66666667 | 2.25000000 |
| vpara-006 | 2.66666667 | 2.58333333 | 2.00000000 | 2.16666667 |
| vpara-007 | 1.50000000 | 1.41666667 | 2.75000000 | 2.50000000 |
| vpara-008 | 1.50000000 | 1.33333333 | 3.00000000 | 2.75000000 |
| vpara-009 | 2.16666667 | 2.41666667 | 4.00000000 | 3.41666667 |
| vpara-010 | 1.25000000 | 1.00000000 | 1.91666667 | 1.33333333 |
| vpara-011 | 3.41666667 | 2.50000000 | 3.91666667 | 2.58333333 |
| vpara-012 | 2.33333333 | 2.00000000 | 4.00000000 | 3.00000000 |
| vpara-013 | 3.33333333 | 2.66666667 | 4.08333333 | 2.66666667 |
| vpara-014 | 2.33333333 | 1.75000000 | 3.08333333 | 2.58333333 |
| vpara-015 | 2.91666667 | 2.41666667 | 3.41666667 | 3.08333333 |
| vpara-021 | 2.41666667 | 2.00000000 | 2.83333333 | 2.66666667 |
| vpara-022 | 1.91666667 | 1.91666667 | 2.33333333 | 2.25000000 |
| vpara-023 | 3.33333333 | 2.83333333 | 4.08333333 | 3.00000000 |
| vpara-024 | 3.33333333 | 2.41666667 | 3.83333333 | 2.83333333 |
| vpara-025 | 3.00000000 | 2.58333333 | 3.00000000 | 2.50000000 |
| vpara-026 | 2.75000000 | 2.33333333 | 2.08333333 | 2.16666667 |
| vpara-027 | 2.08333333 | 2.00000000 | 3.25000000 | 3.00000000 |
| vpara-028 | 1.66666667 | 1.33333333 | 4.25000000 | 3.33333333 |
| vpara-029 | 1.66666667 | 1.33333333 | 2.00000000 | 1.66666667 |
| vpara-030 | 2.66666667 | 2.16666667 | 2.58333333 | 2.00000000 |
| vpara-031 | 3.08333333 | 2.58333333 | 3.66666667 | 2.83333333 |
| vpara-032 | 4.00000000 | 2.91666667 | 4.33333333 | 3.08333333 |
| vpara-033 | 2.33333333 | 2.00000000 | 2.41666667 | 2.16666667 |
| vpara-034 | 2.16666667 | 2.16666667 | 2.83333333 | 2.58333333 |
| vpara-035 | 2.41666667 | 2.25000000 | 2.33333333 | 2.50000000 |
| vpara-036 | 1.33333333 | 1.33333333 | 2.08333333 | 1.91666667 |
| vpara-037 | 3.16666667 | 2.66666667 | 3.58333333 | 3.08333333 |
| vpara-038 | 2.41666667 | 1.50000000 | 2.91666667 | 2.66666667 |
| vpara-039 | 2.66666667 | 1.91666667 | 2.16666667 | 2.08333333 |
| vpara-040 | 2.83333333 | 2.50000000 | 2.75000000 | 2.50000000 |
| vpara-041 | 1.16666667 | 1.16666667 | 2.25000000 | 2.41666667 |
| vpara-042 | 1.33333333 | 1.33333333 | 4.58333333 | 4.16666667 |
| vpara-043 | 2.00000000 | 1.58333333 | 3.33333333 | 2.83333333 |
| vpara-044 | 1.91666667 | 1.83333333 | 2.00000000 | 2.33333333 |
| vpara-045 | 2.08333333 | 2.00000000 | 3.00000000 | 2.50000000 |
| vpara-046 | 2.08333333 | 1.75000000 | 3.83333333 | 3.00000000 |
| vpara-047 | 3.58333333 | 2.66666667 | 4.50000000 | 3.83333333 |
| vpara-048 | 1.08333333 | 1.08333333 | 2.33333333 | 2.00000000 |
| vpara-051 | 3.08333333 | 2.75000000 | 3.33333333 | 2.75000000 |
| vpara-052 | 1.00000000 | 1.00000000 | 2.66666667 | 2.83333333 |
| vpara-053 | 1.50000000 | 1.50000000 | 3.50000000 | 3.16666667 |
| vpara-054 | 2.25000000 | 2.00000000 | 4.25000000 | 3.58333333 |
| vpara-055 | 2.00000000 | 2.16666667 | 3.00000000 | 2.83333333 |
| vpara-056 | 2.83333333 | 2.75000000 | 2.50000000 | 2.66666667 |
| vpara-057 | 1.00000000 | 1.00000000 | 4.16666667 | 3.58333333 |
| vpara-058 | 1.00000000 | 1.00000000 | 3.16666667 | 2.66666667 |

## Input fingerprints

| Input | SHA256 |
|---|---|
| runs-cut6/cut6-vpara-s42.traces.jsonl | f3d3e49ef693efa686d12d628e044b25f8646072a6544843d50d7203b225e6ba |
| runs-cut6/cut6-vpara-s43.traces.jsonl | af7d4d7c0118cc7dc45991dde17ddb68c374cf6141e8a0b9ac7a01c98c8774fe |
| runs-xfam/cut6-vpara-s42.codex.judgments.jsonl | 6b7f75de905169f5a5afb4b72c21ceae12487658d85d5f734468a997169b8e76 |
| runs-xfam/cut6-vpara-s43.codex.judgments.jsonl | e73b062c99cae0c6cad32f620e0538d1779e18127fa42673d0d4113c3ff50e59 |
| items.jsonl | aa604be6aa3f2e5de6af72478f9059a0ec478e61882846e3360a7cb53c74bebd |
| refs/refs.jsonl | 2cbc0e080fc0c474c5f4571dd28fe2462758fbeea1bf0e4e1b9ce9b74525fab2 |
| runs-cut6/cut6-vpara-s42.judgments.jsonl | 9186fe89a50ff857b1efe48c5ce4d4eb11b7e91c2e1d20d4595b51263fa66e3b |
| runs-cut6/cut6-vpara-s43.judgments.jsonl | 127059075ee5cf610f20d031afb11c06fe2369944386d0039d1997682b027b6e |
| runs-dt512/dh-H-vpara-s42.traces.jsonl | 2eb423cdfd08c37953fc6682661c3e647a8e31a148f7898db00d012db49539eb |
| runs-dt512/dh-H-vpara-s43.traces.jsonl | 30ed158d41c4b86c610bbe756f42f27d5668453dfe4e9f50f612b9db5dce3f25 |
| runs-xfam/dh-H-vpara-s42.codex.judgments.jsonl | 34b2bc2fcb6527d81bff0d825f1fea32a2cbf632f5312cde55ab8f0c908a252c |
| runs-xfam/dh-H-vpara-s43.codex.judgments.jsonl | 267d7f299a8efc026ccf07c43e8c15604a716a4e4cba0ff9119c5177540ca216 |
| runs-dt512/dh-H-vpara-s42.judgments.jsonl | 6ed395d6f38e6933fa2f43f5a5d30a6c8c668af119a6fdf1726a69c269db345e |
| runs-dt512/dh-H-vpara-s43.judgments.jsonl | 6698e7710acddf2546afa8a1546041e7fc47f6edd0acabf961f9cbd96aa91d78 |
