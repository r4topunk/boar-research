# X2B-OFF-MAIN result (2026-10-21 13:2x)

TL;DR
- **Verdict by the frozen rule: X2b stays on.** OFF - ON on the 77 live MAIN ids = **+0.024 U_d (CI -0.029..+0.079)**: the U clauses of "safe" pass (dU >= -0.02, CI low >= -0.05), but **CE-unwarned rises 7 -> 10 (+3 > 2)**, so neither "safe" nor "better" holds.
- The engine loses no measured U on real items with X2b off; it trades refusals for shown answers (R 46 -> 40), and some of the newly shown answers are confident errors (6 new CEu, 3 gone, net +3).
- **The cost of X2b is confirmed:** OFF cuts prompt tokens by **42 %** (729 -> 420 mean, n 75 live) and retrieval wall by 73 ms (183 -> 110 mean; p50 181 -> 108).
- Reading: X2b's appended chunks act on real items mostly as a warning/refusal trigger, not as a quality lever. Half the prompt is free in U, but not in CEu at this n. CEu +3 on 77 is about 1 item over the clause, single seed, Haiku; per-item seed noise on these ids is r 0.66 (16 CE flips of 77, s42 vs s43), so this is borderline, not a demonstrated harm.

## Setup
Criterion X2B-OFF-MAIN-criterion.md, sha256 0415e6eb..., committed 1c315378 before generation. Set main-live77.ids (77 = MAIN 97 minus the 20 reaches_model = false ids of ruler/divergence-map.json; 44 v0.1 + 33 cooking/money-se). 1.7B LITEPACKS K1, seed 42, mini (13:10-13:14, 77/77 rows, 0 errors). ON = mini K1 control (null-cal/control/pool-K1.json). OFF = x2b-off.patch (same patch as X2B-RETEST).
Judge: Haiku 5.5-low, judge.v1-low, N 4, both orders, changed answers only: **124 calls (cap 160)**, 0 Opus, 0 paid, 0 phone.
Sanity: 0 headpass:add codes in OFF; 0 items going from 0 to > 0 prompt tokens; changed answers 62, changed contexts 61. Nondeterminism check: the 37 ids shared with X2B-RETEST's OFF run are byte-identical in text and context (37/37), so the mini generation is deterministic at seed 42.

## Table (main/aggregates/x2b-off-main.json; d = OFF - ON, item bootstrap B 2000 seed 11)
| set | n | U_d ON -> OFF | d (95 % CI) | CEu | R | prompt tok (live) | retrieval ms mean / p50 |
|---|---|---|---|---|---|---|---|
| MAIN77 (decides) | 77 | 0.171 -> 0.196 | **+0.024 (-0.029..+0.079)** | **7 -> 10** | 46 -> 40 | 729 -> 420 (-42 %) | 183 -> 110 / 181 -> 108 |
| v0.1 | 44 | 0.208 -> 0.217 | +0.010 (-0.076..+0.091) | 4 -> 4 | 24 -> 22 | 863 -> 497 | 166 -> 92 |
| cooking+money-se | 33 | 0.121 -> 0.166 | +0.045 (-0.008..+0.109) | 3 -> 6 | 22 -> 18 | 558 -> 323 | 206 -> 135 |
The runner's raw-U delta (no default-mode zeroing of warned answers) is -0.005 (-0.028..+0.019); the U_d gain comes from fewer warned answers, not from better text.

CEu flips (ON -> OFF): new lan-rsn-001, lan-cmp-002, lan-cmp-004, st-qa-cooking-se-016, st-qa-money-se-007, st-qa-money-se-009; gone vit-cry-006, vit-cry-007 (now refused), lan-cmp-005 (now correct). The cm half carries the CEu rise (3 -> 6).

## Verdict by the frozen rules
1. "OFF is better": no (CI low -0.029 <= 0).
2. "OFF is safe for kit-only installs": no; dU +0.024 >= -0.02 and CI low -0.029 >= -0.05 pass, CEu +3 > 2 fails.
3. **X2b stays on.**

UNKNOWN:
- Whether CEu +3 is real or seed noise (borderline by 1 item, single seed, Haiku). A seed-43 pair on the same 77 (about 8 min mini + <= 160 Haiku) or an Opus pass on the 9 CEu-flip items (18 calls) would settle it; not run (out of scope).
- Phone prefill saving of -309 tokens per answer is unpriced on the 1.7B (4B POCO: about 6.5 s TTFT at 47.6 tok/s).

Files: X2B-OFF-MAIN-criterion.md(.sha256), main-live77.ids(.sha256), tools/report_main.py, main/x2boffmain/ (traces, judgments, aggregates), main/aggregates/x2b-off-main.json, main/logs/, PLAN.md.

## Addendum 1 (2026-10-21 13:3x): Opus on the 9 CEu flips + seed 43 → frozen verdict **"OFF is safe for kit-only installs" (at the edge)**
Criterion X2B-OFF-MAIN-criterion-addendum1.md (sha256 af0235a6..., commit 031cf1b9, frozen before any Opus call or seed-43 generation) + addendum 2 (eaaf1a14..., commit 3733c3d9, format only: restates the Opus clause in the Precheck block the preflight reads). Report tools/report43.py -> main/aggregates/x2b-off-main-addendum1.json. Calls: **Opus 36** (cap 36; 18 requested, +18 for ON because no Opus rows exist on the K1 control traces, declared in addendum 1), **Haiku 160** (cap 160), 0 paid.

TL;DR
- **Pooled two-seed (135 item-seed rows): dU +0.026 (CI -0.020..+0.073); CEu ON 12 -> OFF 14 = +2 (Opus labels on the 9 at s42; Haiku-only also 13 -> 15 = +2).** All three clauses hold, CEu exactly at the limit -> **"OFF is safe for kit-only installs"**. Not "better" (CI low < 0).
- **Opus does not remove the s42 CEu rise:** with Opus on the 9 flip items, s42 CEu is 6 -> 9 (Haiku 7 -> 10). Opus confirms 5 of the 6 new OFF errors (lan-rsn-001, lan-cmp-004, cooking-016, money-007, money-009; lan-cmp-002 is corr 2.0 under Opus) and moves vit-cry-006 off CE on ON. dU s42 with Opus on the 9: +0.022.
- **Seed 43 alone (58 ids): dU +0.028 (-0.030..+0.086), CEu 6 -> 5, R 31 -> 28.** The s42 CEu rise does not repeat on these ids.
- **Caveat (load-bearing):** the cap bound. 19 ids were dropped from seed 43 by the frozen order rule (3 cooking + 16 money). These include all 3 of the s42 cm CEu-new items, and the cm half carried the s42 rise (3 -> 6). So the second seed does not test the region where the rise happened. "Safe" holds by the frozen rule at the edge (+2 of a +2 allowance). It is not a demonstration that OFF adds no confident errors on cooking/money questions. Same-ids sensitivity (both seeds on the 58 only): dU +0.018 (-0.036..+0.069).

| | n | U_d ON -> OFF | dU (95 % CI) | CEu ON -> OFF | R ON -> OFF | prompt tok | retrieval ms mean |
|---|---|---|---|---|---|---|---|
| s42 Haiku | 77 | 0.171 -> 0.196 | +0.024 (-0.029..+0.079) | 7 -> 10 | 46 -> 40 | 729 -> 420 | 183 -> 110 |
| s42 Opus on the 9 | 77 | | +0.022 | 6 -> 9 | | | |
| s43 Haiku | 58 | 0.197 -> 0.225 | +0.028 (-0.030..+0.086) | 6 -> 5 | 31 -> 28 | 729 -> 420 (all 77; prompts are seed-independent) | 204 -> 136 |
| **pooled (decides)** | 135 rows | | **+0.026 (-0.020..+0.073)** | **12 -> 14 (+2)** | | | |
| pooled Haiku-only | 135 rows | | +0.026 (-0.020..+0.073) | 13 -> 15 (+2) | | | |
Pooling: ratio of sums over item-seed rows; s42 77 ids + s43 58 ids; item bootstrap keeps both seeds of an id together, B 2000 seed 11. Decision uses Haiku dU (the base metric) and CEu with Opus on the 9 at s42. The Opus mix dU is +0.025 (-0.020..+0.071), the same verdict.
Sanity: ON43/OFF43 77/77 rows, 0 errors; headpass:add ON43 38, OFF43 0; ON43 text differs from ON42 on 70/77 (seed patch applied). Judgment reuse: ON43 18 and OFF43 13 texts reused from earlier Haiku judgments; 16 items had ON43 = OFF43 text (judged once). Run names keep the runner's "-s42" suffix (hard-coded); the seed is set by null-s43.patch.

UNKNOWN:
- The CEu clause on cooking/money at seed 43 is untested (19 ids dropped). Closing it takes about 76 Haiku calls (the 19 ids, both arms, less any reuse) under a new cap.
- Phone TTFT saving of about 309 prompt tokens per answer on the 1.7B is unpriced.
