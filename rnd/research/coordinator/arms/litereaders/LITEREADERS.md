# LITEREADERS: with the fact chunk in context, the Qwen3-1.7B is the best lite reader; LFM2-1.2B and Gemma-3-1B read worse by ≈ 0.06 (2026-10-16 09:45–10:10; 120 Haiku, 0 Opus, 0 paid)

READERSWEEP stage 0 for the lite tier. Knowledge was held constant: ORACLE-ST's ADD contexts (the known fact chunk appended to the kept list), the same prompt text for every reader, and only the model swapped. Criterion `LITEREADERS-criterion.md` v2 sha `1d033198…` (Ruleset 30, frozen before any judge call; v1 `f0e5e130…` failed its 0-call gate on a device-date line only, see below). **Verdict: MEASUREMENT**. No reader of 1.2 GB or less beats the 1.7B; both are *worse*, with CIs below 0.

## Δ ratio (Haiku 5.5-low N=4, both orders, vs gold; random20 of the 180, seed 777; paired per-item bootstrap B 2000 seed 11)
| reader (Q4_K_M) | file | raw (CI) | above-min | Δ vs 4B-ADD (CI) | h2h b/t/w vs 4B | Δ vs 1.7B (CI) | h2h b/t/w vs 1.7B |
|---|---|---|---|---|---|---|---|
| Qwen3-4B-2507 (ref, ORACLE-ST rows) | 2.5 GB | 0.543 (0.479–0.600) | 0.412 | – | – | – | – |
| **Qwen3-1.7B** | 1.11 GB | **0.511** (0.448–0.575) | 0.372 | **−0.032 (−0.070…+0.005)** | 6/5/9 | – | – |
| LFM2-1.2B | 0.73 GB | 0.451 (0.390–0.510) | 0.297 | −0.092 (−0.142…−0.043) | 5/1/14 | **−0.060 (−0.118…−0.006)** | 7/1/12 |
| Gemma-3-1B-it | 0.81 GB | 0.446 (0.386–0.503) | 0.289 | −0.097 (−0.151…−0.046) | 2/4/14 | **−0.065 (−0.125…−0.009)** | 3/3/14 |
- Ranking: 4B > 1.7B > LFM2 ≈ Gemma. W/T/L vs gold is 0/0/20 for every reader, including the 4B. Position consistency 1.0.
- Splits (declared). SE (12): LFM2 − 1.7B −0.104, Gemma − 1.7B −0.097, 1.7B − 4B −0.017. Topic (8): LFM2 − 1.7B +0.002, Gemma −0.020, 1.7B − 4B −0.052. The small readers lose on the long SE answers. LLM items only (17): 1.7B − 4B −0.043 (−0.088…−0.001). Sensitivity without the 2 date-line items (n 18): 1.7B − 4B −0.029 (−0.074…+0.014), with the same ranking.
- **Side finding:** with the fact present, the 1.7B is only −0.032 behind the 4B. Without it (LITE2, selftest20, plain retrieval) the gap is −0.088. The lite tier's gap is mostly a knowledge gap, not a reading gap (consistent with LITE5: X2b closes 1.7B to the 4B plain).

## Speed and memory (MacBook M1 Pro, b11010 llama-server -t 4, ctx 4096, `--reasoning off`; 17 LLM items of random20)
| reader | p50 total s | p50 ttft s | decode tok/s | prompt tok mean | output tok p50 | words p50 | llama-server RSS median / peak |
|---|---|---|---|---|---|---|---|
| Qwen3-1.7B | 4.42 | 3.50 | 49.8 | 650 | 47 | 36 | 2484 / 2671 MB |
| LFM2-1.2B | 3.10 | 2.52 | 91.2 | 667 | 48 | 38 | 1518 / 1539 MB |
| Gemma-3-1B-it | 2.56 | 1.71 | 67.3 | 654 | 59 | 46 | 1432 / 1452 MB |
- LFM2 decodes 1.8× faster and Gemma prefills 2× faster. Both use ≈ 40 % less RSS. On quality they lose ≈ 0.06 to the 1.7B. The speed is real, but it does not pay for the lost quality on these items.

## Frozen inputs and gates
- Tree kiln-local/be-0cfd4a77-cut7-oracle with adapter `be/adapter-litereaders.ts` 0fc76e13… (`tools/adapter-litereaders.vs-6298e5d3.patch` 2924b852… = ORACLE-ST adapter + the LITE5 hunks + the LFM2/Gemma entries). BOAR_ORACLE_FILE = oracle-st/tools/oracle-add.json. Runner `tools/run_lr.sh` (2 s RSS sampler), driver `tools/gen.sh`, requests `tools/mkreq.py` (= the ORACLE-ST ADD requests apart from modelId/runId). random20.ids f31c3863…, smoke3.ids 8f586ca6….
- Models: LiquidAI/LFM2-1.2B-GGUF @ 5399e76c, sha 55175400… (LFM Open License v1.0: free below USD 10M revenue, not OSI). unsloth/gemma-3-1b-it-GGUF @ f0b45be0, sha 8270790f… (Gemma terms). 1.7B b139949c…. Neither new model has a thinking mode. Reasoning tokens 0 on all 69 traces. `--reasoning off` appears in every server log.
- Smoke (smoke.verdict.json): 3 × 3 PASS. r20 gate v1 FAIL: on 2/20 items (factbook-011, travel-se-012) the only prompt difference was the engine's device-date line, "Today is Tuesday, 13 October" (4B, 10-13) vs "Friday, 16 October". It was identical for all three readers. Clock artefact: there is no date override in the engine and no faketime on the host. v2 normalises that line, adds the n 18 sensitivity and keeps the rule otherwise unchanged. Gate v2 PASS: prompts identical 17/17 LLM items per reader, kept identical 20/20, 0 errors / empty.
- Reference rows reused: oracle-st/runs/st-<pack>-cut7-oracleadd-s42.judgments.jsonl (Haiku). Judge `tools/judge.sh` (shard_judge N=4, preflight OK 27/27, check_judgments fail-closed), 120 rows. Aggregation `tools/agg.py` → aggregates/litereaders.json (+ .stdout.txt), gate-{smoke,r20}.json, gate-r20.v1-FAIL.json.

## Reading for the programme
- READERSWEEP stage 0 (lite tier) is done. Among stock-runtime lite readers, the Qwen3-1.7B stays the lite candidate. A smaller reader buys speed/RAM at about −0.06. Reader swaps are not the lite lever; knowledge reach is (X2b, packs).
- Caveats: dev gold from pack text; n 20, one seed; Haiku compresses gaps. The 4B rows were generated 3 days earlier (date line only).
- Exposure: public self-tests only; no blind/ read; rnd/veil/ never read → no EXPOSURES row. Both new GGUFs deleted from the MacBook after the run (DISK-LOG); nothing downloaded on the mini.
