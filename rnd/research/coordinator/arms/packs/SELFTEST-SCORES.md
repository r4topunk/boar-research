# SELFTEST-SCORES — the 9 published packs' self-tests, with vs without the pack (2026-10-13)
TL;DR: 4B claim build (cut 7, claim kit) on each pack's 20 public self-test items, with the pack added vs claim kit only, Haiku 5.5-low L1 (N = 4 shards, both orders, 680 new calls + the 40 existing qa-travel-se rows). **Pooled 180 items: with 0.493 (0.470–0.516) vs without 0.460 (0.437–0.484) raw, paired Δ +0.032 (+0.016…+0.050); above_min Δ +0.042 (+0.021…+0.065); items better/worse 93/50.** Clear lifts: simplewiki +0.10, ethereum-se +0.07, bitcoin-se +0.05; ≈ 0 for firstaid, medlineplus, factbook (−0.02). Win 0/180 vs gold everywhere. Dev numbers, agent-written gold.

## Pipeline
- Wave-2 path fix: `tools/selftest_to_bench.py`, `selftest_agg.py`, `run_selftest.sh` resolve `shared-data/packs/wave2` first, then wave1.
- Generation (MacBook, `tools/gen_localjudge.sh` → `run_selftest.sh`): with-pack traces for boar-factbook / boar-simplewiki-en + 9 no-pack controls (`selftest_to_bench.py <pack> --no-pack`; kit = boar-crypto + boar-wikivoyage-en). 11 runs × 20, 0 errors, 0 declined. Bench dirs `boar-eval/bench/selftest/<pack>/` (questions/refs shas unchanged for the 7 wave-1 packs).
- Judge: `deepthink/tools/shard_judge.sh <traces> <R>.judgments.jsonl bench/selftest/<pack> <R>.ids selftest-<pack>-cut7[-nopack] 4 haiku`; 17 × 40 = 680 calls, 0 failures, ≈ 50 s wall per set. `floor_metrics.py --strict` per set → `aggregates/<R>.floor_metrics.txt`.
- Δ = per-item bootstrap of the ratio-of-sums difference (B 2000, seed 11; categories are free-form so no stratification): `tools/localjudge_agg.py` → `aggregates/selftest-scores.json`.

## Per pack (Haiku 5.5-low; raw ratio with CI; Δ = with − without, paired)
| pack | with raw (CI) / above_min | without raw (CI) / above_min | Δ raw (CI) | Δ above_min (CI) | better/worse | items with pack kept (kept from pack/kept) | fact article kept / in raw |
|---|---|---|---|---|---|---|---|
| qa-travel-se | 0.423 (0.360–0.484) / 0.262 | 0.394 (0.327–0.462) / 0.222 | +0.029 (−0.022…+0.077) | +0.040 (−0.026…+0.100) | 11/2 | 9 (15/28) | 6 / 13 |
| qa-ethereum-se | 0.516 (0.454–0.577) / 0.375 | 0.442 (0.375–0.512) / 0.278 | **+0.074 (+0.016…+0.133)** | +0.097 (+0.018…+0.176) | 12/5 | 16 (31/36) | 7 / 11 |
| qa-bitcoin-se | 0.469 (0.382–0.556) / 0.318 | 0.415 (0.337–0.500) / 0.248 | **+0.054 (+0.017…+0.094)** | +0.070 (+0.020…+0.125) | 10/4 | 16 (32/34) | 2 / 3 |
| qa-health-se | 0.525 (0.463–0.586) / 0.390 | 0.509 (0.450–0.564) / 0.371 | +0.016 (−0.014…+0.046) | +0.019 (−0.019…+0.057) | 9/7 | 10 (19/23) | 5 / 12 |
| qa-outdoors-se | 0.518 (0.464–0.575) / 0.383 | 0.483 (0.424–0.541) / 0.337 | +0.035 (−0.021…+0.099) | +0.045 (−0.028…+0.128) | 10/6 | 11 (23/25) | 9 / 15 |
| boar-firstaid-en | 0.471 (0.414–0.529) / 0.322 | 0.468 (0.419–0.518) / 0.316 | +0.004 (−0.027…+0.036) | +0.006 (−0.033…+0.046) | 8/9 | 3 (3/16) | 0 / 2 |
| boar-medlineplus-en | 0.508 (0.442–0.574) / 0.378 | 0.506 (0.441–0.574) / 0.376 | +0.002 (−0.055…+0.044) | +0.002 (−0.069…+0.055) | 10/7 | 12 (25/33) | 11 / 14 |
| boar-factbook | 0.438 (0.378–0.501) / 0.287 | 0.456 (0.393–0.521) / 0.309 | −0.018 (−0.079…+0.026) | −0.022 (−0.099…+0.032) | 8/8 | 5 (7/35) | 5 / 7 |
| boar-simplewiki-en | 0.566 (0.483–0.640) / 0.445 | 0.465 (0.386–0.542) / 0.312 | **+0.102 (+0.054…+0.157)** | +0.133 (+0.071…+0.204) | 15/2 | 15 (38/43) | 12 / 14 |
| **pooled 180** | 0.493 (0.470–0.516) / 0.351 | 0.460 (0.437–0.484) / 0.308 | **+0.032 (+0.016…+0.050)** | +0.042 (+0.021…+0.065) | 93/50 | 97 | 57 / 91 |
- Win/tie/loss vs gold: 0/0/20 in all 18 sets. No-pack controls keep 0 pack passages (simplewiki 1 title coincidence).
- Reading: the lift follows the keep step. Packs whose passages are kept on 15–16/20 items (simplewiki, ethereum-se, bitcoin-se) gain; firstaid (kept on 3/20) and factbook (5/20, crowded out by the claim kit's peers) show none. medlineplus is kept on 12/20 and the fact article on 11/20, yet Δ ≈ 0: the 4B's ≈ 50-word answer does not use it (or the closed-book answer was already as good on these consumer-health items).

## Side measurement: local judge (Qwen3.6-35B-A3B UD-Q2_K_XL, mini, 0 paid calls)
- Shim `arms/judge2/shim-qwen/` (judge-core.mjs = judge.v1 bytes 521f7ad3…; runClaude → llama-server b11010 CPU `-t 8 -c 4096 -np 1 --jinja`, json_schema grammar, thinking off, temp 0 seed 7, cache_prompt, 240 s cap, 3 attempts). Grammar caps `rationale` at 40/160 chars: rationale is the last schema field, so scores/winner are unchanged (checked: 8/8 calls identical with cap 160 vs 40 vs none). `-t 8` reproduced `-t 4` verdicts 4/4; `-t 10` did not, so it was dropped. ≈ 34 s/call; 118 calls, 0 failures.
- Calibration on qa-travel-se with pack (20 items, both orders) vs the Haiku rows: **same winner 19/20 (0.95 ≥ 0.75: trusted for the sign)**; Pearson r (BOAR mean) 0.915; position consistency 0.95 (Haiku 1.00); ratio raw 0.482 vs 0.423, above_min 0.352 vs 0.262 (local ≈ +0.06 lenient); BOAR C/Cm/U 2.30/2.40/2.50 vs 2.27/1.75/1.80, ref 4.95/5.00/4.97 vs 4.67/4.42/4.67.
- qa-travel-se with vs without, local judge: 0.482 vs 0.441, Δ +0.042 (+0.005…+0.087) — same sign as Haiku (+0.029). Stopped at that point on the coordinator's change of plan (Haiku = primary); 19 + 19 factbook rows left partial and unused. Server stopped 10:2x, mini free 31 GiB. Files: `selftest-runs/localjudge/`, `aggregates/selftest-localjudge.json`.

## Caveats
- Dev numbers on agent-written (Claude-family) gold written from the very pack text, so the self-test favours the pack; never pool with v0.1/v0.2/V-para or claim rows. Haiku L1 compresses gaps vs Opus (L1-PROTOCOL). One seed (42); per-pack n = 20 (per-pack CIs ≈ ±0.05).
- Cut 7 predates the source-code fix (SE rows labelled "enwiki"); pack membership counted by title / stackexchange URL.
- Qwen judges a Qwen 4B (self-family); used only as a side check.

## Addendum: wave 3 (2026-10-13; qa-cooking-se, qa-money-se)
Same pipeline (4B cut 7 + claim kit, seed 42; Haiku 5.5-low, N = 4 shards, both orders; `localjudge_agg.py --packs qa-cooking-se,qa-money-se` → `aggregates/selftest-scores-wave3.json`). Tools now resolve `shared-data/packs/wave3` first. 162 Haiku rows logged: 160 ok + 2 refusals (cooking item 003 as first drafted, Bacillus cereus in baked goods, refused by the judge's bio usage filter in the no-pack run; replaced by the drawn candidate 1022 "parchment lid" before any with-pack run, its no-pack trace regenerated and judged; draw file `replacements` field).

| pack | with raw (CI) / above_min | without raw (CI) / above_min | Δ raw (CI) | Δ above_min (CI) | better/worse | items with pack kept (kept from pack/kept) | fact article kept / in raw |
|---|---|---|---|---|---|---|---|
| qa-cooking-se | 0.464 (0.391–0.531) / 0.315 | 0.454 (0.386–0.520) / 0.302 | +0.010 (−0.039…+0.065) | +0.013 (−0.050…+0.086) | 8/8 | 11 (30/32) | 5 / 9 |
| qa-money-se | 0.456 (0.394–0.516) / 0.302 | 0.425 (0.378–0.471) / 0.262 | +0.030 (−0.007…+0.072) | +0.039 (−0.009…+0.095) | 10/5 | 11 (30/31) | 0 / 0 |
| pooled 40 (wave 3) | 0.460 / — | 0.440 / — | +0.020 (−0.011…+0.054) | +0.026 (−0.014…+0.070) | 18/13 | 22 | 5 / 9 |
- Win/tie/loss vs gold 0/0/20 in all four sets; 0 errors, 0 declines; p50 8.1 / 9.1 s with pack vs 5.2 / 5.6 s without. No-pack controls keep 0 pack passages.
- Reading: neither pack shows a lift that clears zero at n = 20. Money keeps pack passages on 11/20 items but never the fact's own thread (other threads on the same topic win the keyword race); cooking reaches the fact thread on 9/20 and keeps it on 5/20 — the keep-step loss again. Pooled 220 (11 packs) not recomputed here; the 180-item table above stands.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
