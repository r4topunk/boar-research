# CITESUP (N5, 2026-10-21): a bge-small cosine rescue for CT-1, with tau set so Qwen3-1.7B decisions do not change, leaves Ministral-3-3B vendor NO-GO on both GATE v2 screens

TL;DR: Qwen3-1.7B rarely fails the key-word check (6 pending citations in 91 answers), and its highest cosine is 0.700, so the rule puts tau at 0.701. At that tau, 3 of 10 Ministral pending citations per screen are rescued. False refusals on K1 drop from 7 to 5 out of 20 (limit 4) and U_cov goes from -0.123 to -0.073 (floor -0.071), so K1 misses on both clauses. K0 is unchanged at 3/20 false refusals (limit 2). Verdict NO-GO, no stage 2. 28 Haiku calls, 0 Opus, 0 paid.

Criterion: CITESUP-criterion.md. The first freeze 127f17db was committed in 8fe1def4 before any run. Amendment 1 (90b02601) added a Budget block before any result. Amendment 2 (2c59d374) came after the K1 calibration generation and before tau, any candidate run or any judge call. It replaced the text-identity test with a decision-level test because of decode drift (below). Final sha256 fc8e653d...

## Mechanism (citesup-log.patch b6510bff, min3v-citesup-on.patch c003c618)
- CT-1 keeps a [n] if the key-word rule keeps it, OR if the bge-small-en-v1.5 cosine between the cited sentence and the best 1000-char window of source n is at least tau. The embedder and normalisation are the ones retrieval uses.
- The default checkCitations output is identical to the base tree (tools/unit.mjs OK).
- The rescue runs inside the engine's own post-processing, so attribution, the release rules and the warning line behave exactly as in the engine. The sidecar does not hold full source bodies, so an offline replay would not have been exact.

## Calibration (1.7B, log mode, screen2 K0 + K1 = 91 ids, tools/calib.py, runs/calib.out)
- 6 pending decisions, cosines 0.544-0.700, so tau = 0.701. Log mode rescued 0 citations.
- Decode drift: 4 of 41 (K1) and 4 of 50 (K0) answer texts differ from the 180-item control run. All 8 have byte-identical retrieval and no CITESUP check record, so the drift happens before CT-1 (temperature 0.7, different preceding requests). The 1.7B identity therefore holds at the decision level: 0 of 6 1.7B decisions flip at tau.

## Candidate (Ministral-3-3B vendor sampler + CITESUP on at tau 0.701; judged = text differs from original min3v and from the control)
| screen | pending [n] | rescued (items) | changed vs min3v (rescue / drift) | judged | warned | net (bar) | false refusals (max) | U_cov (min) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| K1 | 10 (cos max 0.832, 6 >= 0.6) | 3 (3) | 7 (3 / 4) | 7 | 15 -> 11 | 13 (9) | 7 -> **5**/20 (4) | -0.123 -> **-0.073** (-0.071) | NO-GO |
| K0 | 10 (cos max 0.735, 5 >= 0.6) | 3 (3) | 7 (3 / 4) | 7 | 11 -> 10 | 17 (10) | 3 -> **3**/20 (2) | -0.032 -> -0.026 (-0.059) | NO-GO |
CE-unwarned: K1 21 -> 11 (min3v 13), K0 30 -> 16. Re-aggregating the original min3v traces with the same tools reproduces the original K1 gate line verbatim, so the aggregation path is correct.

## Reading
- A 1.7B-safe tau is close to the top of Ministral's cosine range. It recovers about a third of the dropped in-range citations and only part of the false refusals. The K0 false refusals do not move, so they come from something other than CT-1 support: no reference at all, or drift.
- The cosine measures topical closeness, not entailment. A lower tau would break the 1.7B identity on these screens and would need its own criterion and a precision check (wrong-source rescues).
- Limits: tau rests on 6 1.7B decisions from the screens themselves; one seed; drift accounts for 4 changed answers per screen, about the same size as the effect.

## Files
- Patches, criterion and plan: PLAN.md, CITESUP-criterion.md, citesup-log.patch, min3v-citesup-log.patch, min3v-citesup-on.patch.
- Tools: tools/{gen.sh, unit.mjs, calib.py, mkon.sh, judge_gate.sh, chain.sh}.
- Runs: runs/citesupctl (1.7B log), runs/citesupm3v (traces + .citesup.jsonl sidecars, judgments, aggregates/*.gate2.txt), runs/chain.log.
- The smoke (smoke-K1.ids) was cancelled while queued: the K1 calibration run got a slot first and served as the smoke.
