# PACKS-L2 — the pack line's three cells at L2 (Opus judge.v1 N = 4), 2026-10-13 21:10 (criterion PACKS-L2-criterion.md sha ace9dd58…; a parallel session; opus/high runner, text saved by the coordinator)

**Verdicts: S − OFF CONFIRMED (+0.042, CI low +0.024); P − S COST CONFIRMED (−0.019, CI high −0.003); X − P OPTIONAL (R49 unchanged: SE CI low −0.008).** 31 sets × 40 = 1,240 Opus calls (cap 1,300), 0 failures, 0 429/exit-3, 0 paid, 0 Haiku, no llama-server; S Opus rows reused from ST2 (not re-judged). Two lanes of N = 4 after three sets with 0 429s (8 Opus calls in flight, plus VITALADD's 4 for a while): fine.

## Cells (raw ratio Δ, 95 % CI, per-item bootstrap B 2000 seed 11, paired on queryId; b/w = items better/worse; Opus has more ties than Haiku)
| cell | Opus Δ (CI), b/w | Haiku Δ (CI), b/w |
|---|---|---|
| S − OFF pooled 180 | **+0.042 (+0.024…+0.062)**, 74/36 | +0.032 (+0.016…+0.050), 93/50 |
| S − OFF SE / topic | +0.048 (+0.022…+0.078) / +0.035 (+0.009…+0.062) | +0.041 / +0.022 (−0.004…+0.048) |
| P − S pooled 180 | **−0.019 (−0.035…−0.003)**, 41/51 | −0.016 (−0.033…−0.001), 48/74 |
| P − S SE / topic | −0.029 (−0.055…−0.004) / −0.006 (−0.023…+0.012) | −0.033 / +0.004 |
| X − P pooled 180 | **+0.004 (−0.010…+0.019)**, 59/48 | +0.005 (−0.009…+0.021), 73/63 |
| X − P SE / topic | +0.012 (−0.008…+0.034) / −0.005 (−0.024…+0.014) | +0.018 (−0.000…+0.038) / −0.010 |
| X − S pooled (extra, not a criterion cell) | −0.014 (−0.032…+0.003) | −0.011 |
| wave-3 S − OFF pooled 40 (kept separate) | +0.045 (+0.007…+0.087), 14/7 | +0.020 (−0.011…+0.054), 18/13 |

above_min (Opus): S − OFF +0.053 (+0.030…+0.078); P − S −0.024 (−0.044…−0.005); X − P +0.006 (−0.012…+0.024); wave 3 +0.057 (+0.008…+0.109). Levels: S 0.500, OFF 0.458, P 0.482, X 0.486 (Opus raw); wave 3 S 0.426, OFF 0.380.

Per-pack Opus Δ (Haiku in brackets), order travel / ethereum / bitcoin / health / outdoors / firstaid / medlineplus / factbook / simplewiki:
- S − OFF: +.015 (.029) / +.069 (.074) / +.093 (.054) / −.003 (.016) / +.066 (.035) / +.028 (.004) / −.003 (.002) / +.017 (−.018) / +.099 (.102)
- P − S: +.020 (.016) / −.037 (−.062) / −.054 (−.040) / −.015 (−.024) / −.059 (−.056) / −.022 (−.006) / −.012 (.009) / +.018 (.016) / −.006 (−.005)
- X − P: +.012 (.018) / −.000 (.026) / +.016 (.009) / +.016 (.010) / +.016 (.026) / −.002 (−.009) / −.006 (.010) / −.051 (−.033) / +.038 (−.010)
- Wave 3: cooking +0.053 (+0.010); money +0.038 (+0.030). Per-pack CIs at n 20 are wide; only factbook X − P (−0.051, −0.098…−0.008) and simplewiki X − P (+0.038, +0.001…+0.078) clear zero.

Aggregation stdout (pooled): `s_off opus pooled n=180 S 0.500 OFF 0.458 d_raw +0.042 (+0.024..+0.062) d_above_min +0.053 (+0.030..+0.078) better/worse 74/36` · `p_s opus pooled n=180 P 0.482 S 0.500 d_raw -0.019 (-0.035..-0.003) d_above_min -0.024 (-0.044..-0.005) better/worse 41/51` · `x_p opus pooled n=180 X 0.486 P 0.482 d_raw +0.004 (-0.010..+0.019) d_above_min +0.006 (-0.012..+0.024) better/worse 59/48` · `wave3_s_off opus pooled n= 40 S 0.426 OFF 0.380 d_raw +0.045 (+0.007..+0.087) d_above_min +0.057 (+0.008..+0.109) better/worse 14/7`. The tool's Haiku values match SELFTEST-SCORES, CROWDQ and STACK exactly (estimator copy faithful).

## Reading
- Opus rates the single-pack lift larger than Haiku (+0.042 vs +0.032) and the **topic half clears zero at L2** (+0.035, CI low +0.009), which it did not under Haiku: the report's "lift tracks the keep step; topic packs ≈ 0" softens to "topic packs +0.035 at L2, driven by simplewiki (+0.099), firstaid (+0.028), factbook (+0.017); medlineplus and health-SE ≈ 0".
- Crowding cost confirmed at L2 (−0.019; SE −0.029) → the product decision (user-selected packs, no automatic routing, none default) holds.
- The stack stays an optional setting: X − P +0.004 pooled, SE +0.012 (CI low −0.008). R49 unchanged. Wave-3 packs lift +0.045 at L2 (cooking +0.053 default-eligible; money +0.038).
- Report fold-in (loop session, after 01:00): REPORT-PACKS §1 headline numbers get the Opus column; the cards' "with/without" lines stay Haiku unless re-published.

## Files
tools/chain.sh, tools/l2_agg.py (estimator copied from localjudge_agg.py, original untouched); aggregates/{s_off,p_s,x_p,wave3_s_off,x_s}.json; logs/{smoke,laneA,laneB}.log; judgments `.judgments.opus.jsonl` (+ `.shards/`) next to the 31 traces: arms/packs/selftest-runs/st-<pack>-cut7-nopack-s42 (11), st-qa-{cooking,money}-se-cut7-s42 (2), arms/crowdq/runs/st-<pack>-cut7-all9-s42 (9), arms/stack/runs/st-<pack>-cut7-stack-s42 (9). Public items only; no EXPOSURES row. Audit note (PIPELINE-AUDIT-2026-10-13 F7): l2_agg's "pooled" prints over whatever packs are complete — all 31 sets were complete at the final run (n 180 / 40).
