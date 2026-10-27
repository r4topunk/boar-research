# LENGTHSHARE: how much of the V-para floor-adjusted gap is reference length (criterion sha f03087ff…; 2026-10-10; coordinator)

TL;DR: against the same answers, condensing the ≈ 280-word frontier+web references to ≤ 80 words lifts the recommended deep configuration H (s42) from floor-adj **0.412 → 0.514** (paired +0.102, CI +0.068…+0.144) and the 4B K from **0.261 → 0.322** (+0.060, +0.037…+0.088). The ranking K < H holds and widens (H80 − K80 floor-adj +0.192, CI +0.131…+0.257). Correctness does not move (H 0.633 → 0.655, K 0.424 → 0.428); the whole shift is completeness (+0.14 / +0.09) and usefulness (+0.13 / +0.08), and about half of it is the capped references scoring lower themselves (ref mean 4.85 → 4.47). **Length share of H's remaining gap to the reference ≈ 17 % (0.102 / 0.588); ≈ 5/6 of the shortfall is substance** (key points missing per the item rubric). H clears the 0.50 point only against 80-word references and only as a point estimate (CI 0.456–0.578); this is not a bar reading. Wins vs the reference appear for the first time (H80 3/51, K80 2/51).

| Row (V-para, 51 ids, s42, Opus judge.v1, N = 4) | raw (CI) | floor-adj (CI) | corr / comp / usef floor-adj | useful ≥ 3 | wins | ref mean |
|---|---|---|---|---|---|---|
| K vs original refs | 0.413 (0.381–0.446) | 0.261 (0.216–0.306) | 0.424 / 0.173 / 0.184 | 2.0 % | 0 | 4.86 |
| K vs 80-word refs | 0.472 (0.423–0.523) | 0.322 (0.269–0.387) | 0.428 / 0.261 / 0.261 | 13.7 % | 2 | 4.52 |
| H vs original refs | 0.533 (0.500–0.563) | 0.412 (0.375–0.450) | 0.633 / 0.280 / 0.316 | 33.3 %* | 0 | 4.85 |
| H vs 80-word refs | 0.623 (0.572–0.672) | 0.514 (0.456–0.578) | 0.655 / 0.420 / 0.444 | 45.1 % | 3 | 4.47 |

\* two-seed figure (BAR-TABLE §2). Paired: H80 − H raw +0.090 (+0.061…+0.123), floor-adj +0.102 (+0.068…+0.144), per item 28 ↑ / 18 = / 5 ↓; K80 − K raw +0.059 (+0.038…+0.083), floor-adj +0.060 (+0.037…+0.088), 19 ↑ / 29 = / 3 ↓.

Part 1 (0 calls; aggregates/dimshare-*.opus.json, useful3.opus.jsonl): correctness-only floor-adj H 0.660 (V-para, 2 seeds) / 0.743 (v0.2); K 0.427 / 0.595. Completeness and usefulness carry the shortfall on both sets.

## Method
- Capping: `tools/cap_refs.mjs` + `tools/cap80.system.md` (sha 9bc9ef75…), Opus via `claude -p` (no tools), 51 calls; 18/51 rows exceeded 80 words after one retry and were truncated at the last sentence boundary ≤ 80 words (flag `truncated`); refs-80w words p10/p50/p90 = 67/77/80; `blind/V-para/refs-80w/MANIFEST.json` jsonl sha 61e7740c…, source refs sha 952e2c44…. Bench shim `bench-shim-80w/bench.json`.
- Judging: `deepthink/tools/shard_judge.sh` N = 4 opus, systems `lengthshare-H80` / `lengthshare-K80`; fail-closed checks ok (102/102 each). Files `runs-dt512/dh-H-vpara-s42.judgments.len80.jsonl`, `runs-cut6/cut6-vpara-s42.judgments.len80.jsonl`.
- Stats: `tools/dimshare.mjs` (per-dimension ratios), `deepvpara/tools/paired.mjs` (paired Δ, item bootstrap 2,000). Aggregates: `aggregates/dimshare-{H,H80,K,K80}-vpara-s42.opus.json`, `paired-H80vsH-s42`, `paired-K80vsK-s42`, `paired-H80vsK80-s42`.

## Reading for the research target
- The judge rubric already says "do not reward length", yet shorter references raise completeness/usefulness by ≈ +0.1 on H. Part of that is the references losing points themselves (the capped text drops caveats and detail the judge counts as key points), part is BOAR's answers reading as more complete relative to a shorter standard.
- For the bar: ≈ 17 % of H's gap to the reference is attributable to reference length/detail; the other ≈ 83 % is missing substance. Levers must add key points (coverage, follow-up retrieval), not words. Consistent with the measured walls (persona "detailed" −0.066 on the deep tier, DEEPFULL).
- Claim wording: numbers against the frozen references stay the headline; this measurement can be cited as "with references capped at 80 words the deep configuration reaches 0.51 floor-adjusted on V-para (dev, 1 seed, CI straddles 0.50)".

## Cost and exposure
Opus 51 (capping) + 204 (judge) = 255 calls; 0 generations; Haiku 0. V-para: existing H s42 and K s42 traces re-judged; reference text + question sent to Opus for capping (no BOAR answers). One EXPOSURES row.
