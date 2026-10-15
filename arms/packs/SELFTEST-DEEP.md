# SELFTEST-DEEP — the deep tier (Qwen3.6-35B-A3B + thinking 512) on the 180 public self-test items, with vs without the pack (2026-10-13; 18 runs on the mini 10:45 → 19:07; Haiku 5.5-low N=4 both orders, 720 calls; 0 paid)

> Health and first-aid content here is AI-reviewed, not clinically reviewed; nothing in this file is medical advice.
TL;DR: **the deep tier gains nothing measurable from any pack: pooled 180 with 0.546 (0.523–0.569) vs without 0.548 (0.525–0.569), paired Δ −0.002 (−0.020…+0.016)**, above_min −0.002 (−0.025…+0.020), better/worse 76/70, win 0/180 with (1 tie) and 1/180 without. Pre-declared split (H11, BACKLOG META 10-13, declared at 6/18): SE packs (n 100) Δ **−0.003 (−0.030…+0.026)** — as predicted; topic packs (n 80) Δ **−0.000 (−0.024…+0.023)** — the "topic > 0" half is NOT confirmed. Deep with pack vs 4B with the same pack: **+0.054 (+0.034…+0.073)** pooled (SE +0.063 (+0.037…+0.090), topic +0.043 (+0.013…+0.074)). The 4B gains +0.032 from the same packs (SELFTEST-SCORES); the 35B does not. Dev numbers, agent-written gold.

## Per pack (raw; Δ = with − without, paired; vs 4B = deep with − 4B with; pack passages kept / fact article kept, of 20; p50 s desktop)
| pack | with | without | Δ (CI) | vs 4B (CI) | pack kept / fact kept | p50 s |
|---|---|---|---|---|---|---|
| qa-travel-se | 0.548 | 0.555 | −0.007 (−0.071…+0.048) | +0.125 (+0.058…+0.197) | 12 / 7 | 86 |
| qa-ethereum-se | 0.582 | 0.575 | +0.007 (−0.067…+0.089) | +0.066 (−0.009…+0.135) | 15 / 9 | 102 |
| qa-bitcoin-se | 0.545 | 0.578 | −0.034 (−0.083…+0.009) | +0.076 (+0.028…+0.131) | 18 / 4 | 100 |
| qa-health-se | 0.526 | 0.541 | −0.016 (−0.058…+0.026) | +0.001 (−0.034…+0.039) | 10 / 6 | 90 |
| qa-outdoors-se | 0.565 | 0.528 | +0.036 (−0.018…+0.096) | +0.046 (+0.002…+0.088) | 13 / 10 | 96 |
| boar-firstaid-en | 0.479 | 0.466 | +0.013 (−0.028…+0.051) | +0.007 (−0.022…+0.039) | 3 / 0 | 0.6 (health-strict path: no deep prompt, RULE 23) |
| boar-medlineplus-en | 0.523 | 0.572 | **−0.049 (−0.104…−0.002)** | +0.016 (−0.032…+0.068) | 13 / 12 | 97 |
| boar-factbook | 0.554 | 0.550 | +0.004 (−0.015…+0.023) | +0.116 (+0.045…+0.192) | 9 / 9 | 105 |
| boar-simplewiki-en | 0.599 | 0.567 | +0.032 (−0.020…+0.090) | +0.032 (−0.023…+0.100) | 16 / 13 | 115 |
| **pooled 180** | **0.546** | **0.548** | **−0.002 (−0.020…+0.016)** | **+0.054 (+0.034…+0.073)** | 109 / 70 | — |

## Reading
- The deep tier keeps the pack passages (109/180 items; the fact article on 70) and its answers do not improve: on these items the 35B's closed-book answer is already as good as the pack-grounded one. MedlinePlus is the one pack with a CI excluding 0, and it is negative (−0.049): the consumer-health summaries displace the model's own, fuller answer (per-pack n 20; one seed; descriptive).
- The pack value measured on the 4B (+0.032 pooled; simplewiki +0.10, ethereum +0.07, bitcoin +0.05) is therefore a fast-tier value. For the deep tier the product rule is the opposite of crowding mitigation: packs add latency (p50 +4…+14 s) and no quality on the pack's own questions.
- The deep tier's own advantage is the reader: +0.054 over the 4B with the same passages, largest on travel (+0.125) and factbook (+0.116), ≈ 0 on health-SE and first aid (health path).
- First aid is not a deep-tier measurement: its items take the health-strict path (p50 0.6 s, no thinking), so both arms are the canned/fast answers.

## Files and caveats
aggregates/selftest-deep.json (all 18), selftest-deep.SE.json, selftest-deep.topic.json, selftest-deep.partial-se.json (10/18 snapshot); runs under selftest-runs/deep/ (traces, Haiku judgments, floor_metrics); chain tools/stdeep-chain.sh + stdeep-remote-run.sh (mini, the maintainer's heavy queue), watcher tools/selftest_deep_watch.sh. Criterion c144f751… (measurement, no verdict rule). Haiku compresses gaps vs Opus (L1-PROTOCOL); one seed (deep-tier determinism not probed, SEEDGEN); n 20 per pack (CI ≈ ±0.05); desktop p50, not device.
