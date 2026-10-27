# LITEREACH2-180: the wider X2b append budget (1200/4/8) on the lite 1.7B is NO on the 180 self-tests: Δ vs X2b 600/2/4 +0.005 (−0.014…+0.025); fact in context 97 → 119 converts only where the fact arrives (2026-10-16 11:1x; Haiku 360, Opus 0, 0 paid)

Criterion LITEREACH2-180-criterion.md sha 0f51560601e3… (Ruleset 30), frozen and committed (rnd cb108d84) before any run. Smoke = LITEREACH2's 3-item b20 smoke re-scored for this sha: PASS (projected 0.39 h). LITEREACH2's own smoke verdict is kept as smoke.verdict.litereach2-v2.json.

## Setup
- Arm B20: the 180 LITE5-180 ON request rows with only runId changed (tools/mkreq.py asserts it). Env BOAR_LR2 1200/4/8. Tree kiln-local/be-0cfd4a77-cut7-litereach2. Adapter-lite5, Qwen3-1.7B Q4_K_M, b11010 --reasoning off, seed 42, -t 4.
- Host: MacBook, the same host as the control rows. The mini's QUANTLITE X2b tree has the v3proto sidecars but not the env patch, and a cross-host run re-samples answers (LITE5 hostid: 5/20 identical cross-host vs 18/20 same-host). So the MacBook lane was used: one server, busy.sh, disk 5–6 GiB, floor 5 held.
- Control: the LITE5-180 ON rows (X2b 600/2/4), Haiku rows reused and not re-judged. Estimator l2_agg.py (B 2000, seed 11).

## Gates (0 calls)
- Per-pack gates 9/9 PASS. 0 errors, 0 empty, 0 reasoning, no <think>. Kept + appended = step-0 b20 replay on 180/180.
- Checkpoint after 3 packs (60 items): fact in context 26 → 33 (+7 ≥ +4), Δprompt p50 +424 (≤ +600). Result: CONTINUE.
- Gate on the 180: PASS. Fact in context (trace rule) **97 → 119 (+22) = step-0 119**. Paired Δprompt p50 +437.5 (max +1133) on 152 LLM items.
- Same-host anchor: on the 20 LITEREACH2 r20 ids, answer text and promptTokens are identical in 20/20.

## Δ (Haiku 5.5-low N=4 both orders, 360 calls, 0 failures; ratio of sums)
| comparison (180) | ratio a / b | Δ raw (CI) | b/w |
|---|---|---|---|
| **B20 − X2b 600/2/4 (LITE5-180 ON)** | 0.491 / 0.486 | **+0.005 (−0.014…+0.025)**; above-min +0.005 (−0.020…+0.030) | 78 / 62 |
| B20 − 1.7B OFF | 0.491 / 0.415 | +0.076 (+0.051…+0.101) | 101 / 45 |
| B20 − 4B plain | 0.491 / 0.493 | −0.001 (−0.025…+0.022) | 67 / 88 |
| B20 − 4B X2b | 0.491 / 0.549 | −0.057 (−0.080…−0.035) | 45 / 106 |
| (ref) X2b − OFF | 0.486 / 0.415 | +0.071 (+0.048…+0.094) | 92 / 51 |

## Splits (declared)
| cell | n | B20 − X2b |
|---|---|---|
| newly gain the fact (step 0) | 22 | **+0.056 (−0.004…+0.108)**, b/w 14/4 |
| rest | 158 | −0.001 (−0.021…+0.019), b/w 64/58 |
| SE / topic | 100 / 80 | +0.003 (−0.018…+0.024) / +0.008 (−0.027…+0.043) |
Per pack: travel −0.032, ethereum −0.021, bitcoin +0.034, health-se +0.003, outdoors +0.032, firstaid +0.033 (+0.006…+0.061), medlineplus −0.009, factbook −0.008, simplewiki +0.019. 5 of 9 packs are positive and every CI except firstaid's crosses 0.

## Cost (MacBook M1 Pro, 152 LLM items, paired vs the ON traces)
p50: prompt tokens 876 → 1303.5 (+437.5); ttft 5.99 → 8.91 s (+2.86 s); total 7.40 → 10.35 s (+3.12 s); decode 39.4 → 33.3 tok/s; words 34.5 → 37. Wall: generation 29 min, judge 9 min.

## Verdict (frozen rule)
**NO (Haiku, dev 180)**: Δ +0.005, CI low −0.014 ≤ 0. The extra reach is real: 22 more items get the fact, and the replay matches 180/180. Those 22 gain +0.056, which is about a third of LITE5-180's +0.173 newly-present gain, and the CI touches 0. That gives about +0.007 pooled, which the remaining 158 items (−0.001) neither add to nor take from. The random20's +0.032 was mostly noise on the rest cell (+0.018 at n 16). The price is a ≈ 50 % longer prompt (+2.9 s ttft desktop; phone estimate ≤ +6 s from LITE6) and −15 % decode.
Decision input: keep X2b at 600/2/4 for the lite tier. The 1.7B does not convert the extra dense chunks well, consistent with LITE6, where "thin" (fact present, not used) is 53 % of the gap. Caveats: dev self-tests with agent-written gold; Haiku only; one seed.

## Files
LITEREACH2-180-criterion.md + .sha256, arm-180.conf, smoke.verdict.json (this sha), smoke.verdict.litereach2-v2.json; tools/{gen_180.sh, gate_180.py, judge_180.sh, agg_180.py} (+ mkreq.py, run_gen.sh reused); aggregates/{checkpoint-180.json, gate-180.json, lr2-180.json}; runs/180/ (9 requests, traces, judgments, logs). No blind/ read; rnd/veil/ not read. No servers left running; the :8094 detector was untouched.
