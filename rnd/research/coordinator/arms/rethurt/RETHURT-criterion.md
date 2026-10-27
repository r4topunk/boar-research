# RETHURT probe criterion (frozen 2026-10-07, overnight loop). Analysis of EXISTING judgments only; 0 model calls, 0 judge calls.
Question: does real retrieval hurt the deep tier (35B) relative to closed-book, and where?
Data (v0.1 EN 57, judge.v1 Opus, refs bd235bb9): deep35 closed-book (moescreen-deep35-v01-s42, ratio 0.596), deep35 engine with
real retrieval (ORACLE TABLE row, 0.565), deep35 R450 gold passages (DEEPREAD, 0.634), 4B closed-book (srv-qwen3-4b, 0.487), 4B
engine (ORACLE row, 0.507). Scorecard buckets per gold item: coordinator/RETRIEVAL-SCORECARD-2026-10-06.items.csv.
Measures: paired per-item Δ (engine − closed-book) for deep35 and for 4B with bootstrap CI; better/worse/equal; Δ by scorecard
bucket (coverage miss / ranking / dropped / reader-fail / reader-ok / no-gold-item); Δ by category (crypto, health, travel, …).
Caveat recorded: engine and closed-book rows differ in prompt/protocol (engine prompt + context vs anchor.v1), so Δ is indicative.
Reading rule (pre-registered): if deep35 engine − closed-book ≤ −0.02 with CI upper bound < +0.02 AND the loss concentrates in the
coverage-miss / no-gold bucket (≥ 60 % of the net loss), the finding is "real retrieval hurts the 35B where it has no gold" and
the proposed next arm is a retrieval-relevance gate for the deep tier (closed-book fallback), to be tested with a clean paired run
(same prompt with/without context) — proposed to r4to, not run tonight. Otherwise: "no retrieval harm shown", nothing proposed.
