# JUDGE-V1_1 criterion, addendum 1 (coordinator request 2026-10-21; frozen before any of its calls)

Base criterion: JUDGE-V1_1-criterion.md sha256 e4369cf03e2939ce36d8a9e7d48571833c4101d41d596a56bdcdb7ca990cbf19 (unchanged). Timing, stated plainly: this addendum arrived and was frozen AFTER the W1 validity run (180 calls, VALID: U 0.000 CI 0.000-0.000 for a, b, c) and BEFORE the W1 controls/retest and before any call below. It adds no rule to the ADOPT decision.

## Added measurement (runs only because W1 validity passed)
- Re-score under judge.v1_1 (W1) both FLOOR separability arms on the v0.1 57 (litepacks/data/v01-57.ids sha256 3e6183f6...): (1) Qwen2.5-1.5B closed-book traces floor-anchors/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl; (2) the 1.7B K0 control lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl. Haiku 5.5-low, both orders, N = 4 (v1_1/tools/run_rescore.sh sha256 357ae7193f6da73fe1432e929e1fe32c6be14a273530cbf3d639d08b0b1f7a7f). 114 x 2 = 228 calls.
- Estimator = FLOOR rule 2 (v1_1/tools/agg_rescore.py sha256 8405e2383f11cdde560497c122d8208de1a8cde1f7a378db7d80f96cbbfad6ea): U per arm with CI; paired dU = U(1.7B) - U(1.5B), joint item bootstrap 2000, default_rng(11). Under judge.v1 (existing rows): 0.294 vs 0.259, dU +0.035 (-0.019...+0.089), NOT SEPARABLE.
- Report: both U, dU with CI, position ABOVE (CI low > 0) / BELOW (CI high < 0) / LEVEL (else), FLOOR rule-2 SEPARABLE (dU >= 0.05 and CI low > 0), and per arm the items that went to zero (s = 1.000 under v1.1, s > 1 under v1). Context only; a research-page sentence "better than a 1B" needs ABOVE, and the FLOOR wording "separable" needs SEPARABLE.

## Budget
calls_cap: Haiku 640 total (400 + 240) / Opus 0. Planned: 300 (W1) + 228 = 528.
