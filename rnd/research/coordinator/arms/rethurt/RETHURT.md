# RETHURT: does real retrieval hurt deep35 vs closed-book? (v0.1 EN 57, judge.v1 Opus, refs bd235bb9; 0 model/judge calls)
**Result (pre-registered rule, criterion `RETHURT-criterion.md` sha ce950ece…, unchanged): "no retrieval harm shown", nothing proposed.** deep35 engine − closed-book = **−0.031 (CI −0.072…+0.011)** meets the size and CI conditions, but coverage-miss + no-gold carry **0.4 %** of the net loss (bar ≥ 60 %).
## Data (judge.v1 claude-opus-5-5, both orders, refs bd235bb9, all 114 rows ok per seed; sha256 first 12)
| row | judgments | sha256 | prompt / context | max tokens | gen seeds | median words |
|---|---|---|---|---|---|---|
| deep35 engine (0cfd4a77 main~deep35, kit A) | `boar-eval/runs/night-2026-10-01/deep35/and-deep35-s{42,43}.judgments.jsonl` | 65611af004a2 / f2cff05d8b92 | engine deep-tier prompt, k 6, ~400 ctx tok, no-think | 200 | 42, 43 | 52 / 54 |
| deep35 closed-book | `boar-eval/runs/kiln/moescreen/moescreen-deep35-v01-s42.judgments.jsonl` | e57a3618de0a | anchor.v1 (ea2f484e), bare question | 450 | 42 | 213 |
| deep35 R450 gold | `rnd/research/coordinator/arms/deepread/deep35-R450.judgments.jsonl` | b40265bf921b | engine fast-tier prompt + ~450 tok oracle passages | 512 | 42 | – |
| 4B engine (0cfd4a77 main, kit A) | `boar-eval/runs/night-2026-10-01/and-qwen-s{42,43}…`, `boar-eval/runs/and-qwen-s44/and-qwen-s44.judgments.jsonl` | 1a9e8a7d72da / 27dd92b77317 / 363b156bba70 | engine fast-tier prompt + retrieval | 512 | 42, 43, 44 | – |
| 4B closed-book | `rnd/research/anvil/exp/outofkit/runs/srv-qwen3-4b.judgments.jsonl` | 6b2a71001c60 | anchor.v1, bare question | 450 | 42 | – |
Buckets: `coordinator/RETRIEVAL-SCORECARD-2026-10-06.items.csv` (sha 4afb630f907e…), run **ctl-s44**; no scorecard row = no-gold. Script `rethurt.mjs` (3362d623e305…), outputs `analysis-ctl-s44.json`, `analysis-ctl-s45.json`, `rethurt-items.csv`.
**Caveat (protocol):** engine vs closed-book differ in prompt (engine prompt + context vs anchor.v1), answer cap (200 vs 450 for deep35; 512 vs 450 for 4B), seeds (2–3 vs 1) and length (deep35 engine median 52 words vs 213). Rubric shift deep35 engine vs closed: correctness 3.46 vs 2.72, completeness 2.36 vs 3.18, usefulness 2.46 vs 2.87. Δ is indicative, not a clean retrieval effect. Scorecard buckets come from 4B cut-4 control traces (ctl-s44), not from the deep35/0cfd4a77 runs; only B1 coverage and no-gold are run-independent.
Convention: per item, order-combined rubric averaged over seeds; item ratio = mean BOAR rubric / mean ref rubric; aggregate Δ = Σ/Σ ratio difference, 2000 joint item boots (seed 5); better/worse on item ratio; converted = engine corr ≥ 4 & closed ≤ 2; cw = corr ≤ 2.
## 1–2. Paired Δ, n = 57
| pair | ratios | Δratio (95% CI) | better / worse / equal | converted / regressed | cw (a vs b) | pass (a vs b) |
|---|---|---|---|---|---|---|
| deep35 engine − closed | 0.565 vs 0.596 | **−0.031 (−0.072…+0.011)** | 23 / 30 / 4 | 7 / 0 | 9 vs 27 | 26 vs 15 |
| 4B engine − closed | 0.507 vs 0.487 | +0.020 (−0.022…+0.061) | 30 / 19 / 8 | 2 / 1 (lan-rsn-003) | 17 vs 30 | 15 vs 10 |
| deep35 R450 gold − closed | 0.634 vs 0.596 | +0.039 (−0.015…+0.091) | 29 / 24 / 4 | 15 / 1 (lan-rsn-001) | 7 vs 27 | 38 vs 15 |
deep35 engine converted: dng-001, lan-cmp-002, lan-cmp-003, lan-exp-006, lan-ref-001, vit-cry-004, vit-cry-011.
## 3. Δ item ratio by bucket (sum of item Δ; share = bucket sum / net sum; deep35 net −1.700, 4B net +1.232, R450 net +2.160)
| bucket | n | deep35 mean Δ | deep35 share of loss | 4B mean Δ | 4B share of gain | R450 mean Δ |
|---|---|---|---|---|---|---|
| coverage (B1) | 19 | +0.005 | −5.7 % | +0.024 | 37.0 % | +0.071 |
| no-gold | 18 | −0.006 | 6.1 % | +0.027 | 38.7 % | +0.036 |
| ranking (B2) | 7 | −0.017 | 7.0 % | +0.124 | 70.2 % | +0.132 |
| dropped (B3) | 1 | −0.350 | 20.6 % | +0.022 | 1.8 % | −0.233 |
| reader-fail (B4) | 2 | −0.183 | 21.6 % | +0.028 | 4.5 % | 0.000 |
| reader-ok (B5) | 6 | −0.156 | 54.9 % | −0.026 | −12.6 % | −0.061 |
| ambiguous (B6) | 4 | +0.019 | −4.4 % | −0.122 | −39.7 % | −0.038 |
Coverage + no-gold: deep35 −0.007 of −1.700 = **0.4 %**; same with ctl-s45 buckets (0.4 %). Gold-in-prompt buckets B3–B6 (n 13): 92.6 % of deep35's net loss.
By category, deep35 mean Δ (n): honesty-refusal +0.169 (6), crypto +0.062 (7), synthesis 0.000 (3), comparison −0.003 (7), travel-local −0.054 (1), explanation −0.065 (11), reasoning −0.072 (11), travel-practical −0.077 (2), health −0.125 (4), danger-situation −0.172 (3), danger −0.200 (2). 4B: honesty-refusal +0.191, crypto +0.124, travel-practical +0.113, comparison +0.094, travel-local +0.063, synthesis +0.009, reasoning −0.027, explanation −0.043, danger-situation −0.074, health −0.125, danger −0.128.
## 4. deep35 engine vs closed, largest item moves (id, bucket, Δ item ratio, corr closed → engine)
Losses: lan-rsn-003 coverage −0.350 (2→1.5); vit-hlt-002 dropped −0.350 (4.5→3); dng-002 no-gold −0.317 (4→2.75); lan-cmp-001 reader-ok −0.283 (4→2.75); lan-exp-002 reader-fail −0.267 (3.5→4.25); vit-hlt-003 reader-ok −0.233 (4→4); dng-005 no-gold −0.200 (2→3); vit-trv-004 no-gold −0.197 (2→1.5); lan-rsn-007 reader-ok −0.183 (4.5→3.5); vit-hum-001 coverage −0.181 (3.5→4).
Gains: vit-cry-008 no-gold +0.412 (1→3.75); lan-ref-001 coverage +0.333 (2→5); lan-cmp-004 coverage +0.267 (1→3); vit-cry-002 no-gold +0.233 (1→2.5); vit-cry-011 coverage +0.151 (2→4); vit-cry-004 no-gold +0.133 (2→4); lan-ref-003 coverage +0.133 (2→3.5); lan-rsn-002 ranking +0.117 (2→3.5); lan-ref-005 coverage +0.104 (3→5); lan-ref-004 ranking +0.096 (3→3.75).
## Rule, literally
Δ −0.031 ≤ −0.02 ✓; CI upper +0.011 < +0.02 ✓; coverage/no-gold share 0.4 % ≥ 60 % ✗ → **"no retrieval harm shown", nothing proposed.**
## UNKNOWN
- How much of −0.031 is retrieval vs the 200-token cap / engine prompt: the rubric shift (correctness up, completeness down) fits a length effect; no clean same-prompt pair exists.
- Buckets for deep35's own retrieval: the scorecard covers 4B cut-4/cut-6 runs only; B2–B6 membership for 0cfd4a77 kit A may differ. n per gold bucket is 1–7.
- 1 seed for both closed-book rows; README noise floor ≈ 0.05.
