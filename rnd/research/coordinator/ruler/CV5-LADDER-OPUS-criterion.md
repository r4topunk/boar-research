# CV5-LADDER-OPUS criterion (round 3, hypotheses-round3-2026-10-21.json; frozen 2026-10-21 before any Opus call)

## Question (verbatim statement)
The two ladder sentences of RV2-SEP-LADDER survive an Opus re-judge on the same existing traces (v0.1 51 dev ids after the deterministic items
are removed, judge.v1 bytes, both orders). The two sentences are 'the 4B separates from the 1.7B/Gemma tier' and 'the 1.7B is level with a
closed-book Qwen2.5-1.5B'. Expected under Opus: 4B - 1.7B >= +0.05 with CI low > 0, and 1.7B - 1.5B with a CI covering 0.

## Items and rungs
- Ids: the RV2 primary 51 = arms/gemma4-e2b/phone/judge/v01-57.ids minus FLOOR's 6 nonmodel_path_items (RV24-criterion.md). Dev set; no blind/, rnd/veil, v0.4.
- Rungs = RV2's primary rungs, existing traces, no generation: L0 Qwen2.5-1.5B closed-book (FLOOR run), L1 1.7B K0 desktop control s42,
  L2 Gemma 4 E2B desktop stage2 s42, L3 Qwen3-4B cut 7 on the Pixel 8a (RV2's 4B rung; the hypothesis text says "4B K0" but the sentences under
  test are RV2's, whose 4B rung is this one).
- **Deviation, stated before the run: single seed per rung.** RV2 averaged two seeds for L1 (s42 + c43) and L2 (s42 + g43). With both seeds the
  unique (item, answer) units are 263 (25 reusable) = 476 new calls, above the 408 cap. With one seed: 186 units, 24 reused, 162 new = 324 calls.
  The Haiku comparison is recomputed on the identical single-seed frame (RV2 load semantics, s42 rows); RV2's two-seed Haiku numbers are quoted
  next to it, not re-derived.

## Judge
- judge.v1 bytes, Opus (node harness/judge.mjs --judge-model opus via arms/deepthink/tools/shard_judge.sh model opus), both orders, seed 7,
  --gap-ms 0, N = 4 shards, one pass per rung file (ruler/tools/cv5_ladder_run.sh). Unit = unique (item id, answer text): identical text across
  rungs is judged once (judge.mjs sees only question, reference and answer text). Reuse: any existing Opus judge.v1 row pair (ok, both orders,
  seed 7, refsSha256 bd235bb9..., questionsSha256 568b3ece...) on the identical unit, indexed by ruler/tools/cv5_opus_pool.py (24 units: 12 CE-OPUS-CHECK ctl-v01,
  5 g75desk, 3 and-qwen-s44, 3 WARN-OPUS K0-v01, 1 ios8; amended before any call). Unit list frozen in ruler/cv5-ladder/in/set.json (ruler/tools/cv5_ladder_prep.py).
- **calls_cap: Opus 360** (= 408 - 48 reused-unit calls; planned 324). Haiku 0, paid API 0, generation 0, phone 0, mini 0. A stopped shard
  (STOP file) is fixed and rerun, never skipped; every unit needs both orders before analysis.

## Analysis (ruler/tools/cv5_ladder.py, committed with this file)
- s, r = mean of the 3 dimensions averaged over both orders; U = sum(s-1)/sum(r-1); U_net = (U-0.058)/0.942. Item-cluster bootstrap B 2000,
  numpy default_rng(11), 2.5/97.5 pct, pairs on the same draws (identical to rv2_ladder.py). Pairs: 1.7B-1.5B, Gemma-1.7B, 4B-Gemma,
  Gemma-1.5B, 4B-1.7B, 4B-1.5B; SEPARABLE iff dU >= 0.05 and CI low > 0 (RV2 rule). Same table under Haiku single-seed.
- Per rung: Opus - Haiku U offset (bootstrap CI), offset spread across rungs, Spearman of per-item s (Opus vs Haiku), CE (corr <= 1.5) and
  correct (corr >= 4) agreement counts.

## Decision (Opus; kill rules verbatim from the hypothesis)
- **Support**: 4B - 1.7B >= +0.05 with CI low > 0 AND 1.7B - 1.5B CI covers 0.
- **Kill-sep**: the 4B - 1.7B or 4B - Gemma CI includes 0 under Opus -> the page drops 'the 4B separates' and keeps only 'the ruler did not
  separate the tiers under Opus'. If both CIs exclude 0 but a point is < 0.05: '4B ahead under Opus, below the 0.05 separability threshold'.
- **Kill-level**: 1.7B - 1.5B CI low > 0 under Opus -> the page says 'separable under Opus, not under Haiku' with both rows.
- **Kill-Haiku-rows**: any per-rung Spearman (Opus vs Haiku, per-item s) < 0.7 -> the page drops all Haiku-only ladder rows.
- Page sentences are chosen mechanically from these flags and printed in CV5-LADDER-OPUS-2026-10-21.md with the judge family named.

## Known limits (stated before the run)
One seed per rung; n 51 dev ids; the 4B rung is cut 7 + claim kit on the phone vs the K0 litepacks engine for the lower three (RV2 confound);
1.5B, not 1B; one Opus pass (two orders).
