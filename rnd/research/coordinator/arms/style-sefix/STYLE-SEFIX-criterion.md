# STYLE-SEFIX criterion (frozen 2026-10-23 before any generation or judge call; never edited after)
Question (r4to): every answer-style test of 2026-10-23 (TOPICS27, SUCCINCT, PARA135, DEEPMODE) ran on the base K1 tree. Under the adopted search advances (gidf + SEFIX F1/F2/F4 = SEFIX-124, chunk-level delivered facts 28 -> 42 on MAIN 92 keyed), does "Succinct beats Detailed on Qwen3-1.7B" still hold, and does Detailed use a delivered fact better than Succinct?

## Arms (seed 42, MAIN 97 = lp-screens/main-97.ids)
- S = SEFIX-124 Succinct (default persona): EXISTING answers coverage-map/sefix/ans-traces/sefix124-main-s42.traces.jsonl and EXISTING Haiku rows as built by coverage-map/sefix/ans-tools/agg_124.py (answers-sefix124.json items[42][id].X: s, sref, corr, declined, warned). Not regenerated, not re-judged.
- D = SEFIX-124 Detailed (new): requests = coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl with only runId (style-sefix-D-s42), config.arm (+detailed) and config.settings.personalityId = "detailed" changed (the TOPICS27 / style17-detailed Detailed persona, adapter persona sha expected be0e6710...). Same base tree be-0cfd4a77-cut7-litepacks + H4-MERGE.patch + SEFIX-ALL.patch, same env (RS_MERGE=gidf, RS_SE_LEAD=0.78, RS_SE_MAXDF=0.25, RS_KEEP_NOPROPER=1, F3 unset), same 13-pack kit (compose/packs-k13), same mini_gen.sh (2-slot lock, disk >= 25 GiB, detector :8094 used only). Only extra tree change: adapter maxTokens 512 -> 1024 by sed in the per-run clone (= PARA135 / style17-detailed Detailed cap). Per-run job dir; kiln-local/rs-SEFIX and other rs-* trees untouched.

## Judge
Haiku 5.5-low judge.v1-low, deepthink/tools/shard_judge.sh N 4, both orders, units v01 (bench/v0.1) / qa-cooking-se / qa-money-se (bench/selftest), the same references the S rows used (night-1023 judge_b.sh recipe). Every D item whose (id, text) has no existing judged row in the agg_124 cache (pool-K1, ARM-G, SEFIX-ALL s42/s43, SEFIX-124 new rows, control s43) is judged; identical (id, text) reuses the cached row (stated count). Cap 400 calls: 97 x 2 = 194 fits, so all 97 are covered. (Fallback only if > 400 were needed: the 42 delivered + 30 of the rest by random.Random(23).sample(sorted(rest), 30). Not expected to fire.) Opus 0, paid 0.

## Splits
Delivered = chunk flag True for "sefix F1F2F4" in coverage-map/chunklevel.json per_item (42 of the 92 keyed). Not delivered = the other 50 keyed. Overall = all 97 (incl. 5 unkeyed). Health = ids containing "-hlt-" or starting "dng-".

## Metrics (S rows and D rows on the same ids; aggregation as agg_124.py)
- U = ratio of sums (declined -> 0) per arm; paired dU = U(D) - U(S), item bootstrap B 2000, random.Random(11), paired on the same draws; overall / delivered / not delivered.
- better / tie / worse per item on s (D > S, equal, D < S).
- CE = answered and mean corr <= 1.5 (LITEPACKS / agg_124 rule), per 100 items, plus CE-unwarned (no engine warning line first); per arm and split.
- Output tokens p50 and totalMs p50 per arm (traces timing).
- Health items worse (D s < S s) count.
- Interaction: dU(delivered) - dU(not delivered) with paired bootstrap (same seed 11).

## Predictions (written before any run)
- P1: overall dU (D - S) < 0, about -0.04 to -0.10.
- P2: on delivered items the gap shrinks vs not delivered (dU delivered > dU not delivered) but stays <= 0.
- P3: CE per 100 D > S in both splits (delivered and not delivered).
- P4 (secondary): D output tokens p50 >= 5x S; ms p50 >= 2.5x S.

## What changes the recommendation
- Default stays Succinct unless overall dU >= 0 with CE per 100 D <= S and 0 health items worse.
- A conditional "Detailed when the fact is delivered" is worth proposing only if on the delivered 42: dU >= 0 (point) with CI low > -0.03, CE per 100 D <= S, and 0 health items worse among delivered. Otherwise: Succinct holds under SEFIX-124 too.
- Caveats to be printed: one seed, Haiku judge (compresses gaps), dev items (cm questions written from the packs), 1.7B only, delivered-vs-not is observational (item difficulty confounds the split; the within-item paired D-S per split is the read).
