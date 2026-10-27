# LITEREADERS: knowledge held constant (ORACLE-ST ADD contexts), which small reader reads best? Qwen3-1.7B vs LFM2-1.2B vs Gemma-3-1B-it, 4B as reference (frozen 2026-10-16 ≈ 09:55 by the LITEREADERS agent; Haiku, dev)

Frozen before any judged run (after the 3-item smoke, 0 judge calls). READERSWEEP stage 0 applied to the lite tier. Tree kiln-local/be-0cfd4a77-cut7-oracle (PATCH_SHA256 0fba26b8…, ORACLE_PATCH = oracle-st/oracle.vs-cut7.patch), adapter be/adapter-litereaders.ts sha 0fc76e138c75891990e62a87bb66378988f431be207ff695582d4f567115cf0c (= ORACLE-ST adapter 6298e5d3 + the LITE5 hunks (1.7B entry + BOAR_SERVER_EXTRA_ARGS) + LFM2/Gemma entries; tools/adapter-litereaders.vs-6298e5d3.patch), BOAR_ORACLE_FILE = oracle-st/tools/oracle-add.json, b11010 llama-server `--reasoning off` (+ engine enable_thinking false), -t 4, ctx 4096, seed 42, MacBook M1 Pro, mmbert detector :8094. Runner tools/run_lr.sh, driver tools/gen.sh.

## Tags
Tags: none
Ruleset: 30

## Question
ORACLE-ST showed the 4B gains +0.090 (Haiku) when the fact chunk is in context. With the same ADD contexts (identical prompt text), which lite reader converts the present fact best: the lite candidate Qwen3-1.7B Q4_K_M (1.11 GB), LFM2-1.2B Q4_K_M (0.73 GB, LFM Open License v1.0) or Gemma-3-1B-it Q4_K_M (0.81 GB, Gemma terms)? Use: pick the lite-tier reader; READERSWEEP stage 0 for the lite tier.

## Fixed inputs
- Slice random20 = random.Random(777).sample(sorted 180 self-test ids, 20) (random20.ids sha f31c3863…; same ids for all readers); 4 of the 20 are answered without an LLM call in the 4B ADD trace (health-extractive / instant): identical across readers by construction, kept in the pooled number (as ORACLE-ST did) and also reported excluded.
- Requests (tools/mkreq.py) = ORACLE-ST ADD requests byte-equal apart from config.modelId and runId; one file per pack.
- Readers: qwen3-1.7b-q4km (b139949c…), lfm2-1.2b-q4km (55175400…, LiquidAI/LFM2-1.2B-GGUF @ 5399e76c), gemma-3-1b-it-q4km (8270790f…, unsloth/gemma-3-1b-it-GGUF @ f0b45be0). All three generated fresh on the MacBook.
- Reference (reused, not regenerated, not re-judged): 4B ADD Haiku 5.5-low rows oracle-st/runs/st-<pack>-cut7-oracleadd-s42.judgments.jsonl (same bench boar-eval/bench/selftest/<pack>, same judge model/effort, same gold).

## Power
expected_delta: reader − 1.7B within ±0.05 raw (priors: 1.7B − 4B −0.088 on selftest20 (LITE2), smaller readers usually weaker)
n: 20; seeds: 1
mde: ≈ 0.05 raw at n = 20, Haiku (LITE5 selftest20 CI half-width ≈ ±0.05)
slice: random20 (seed 777); l1_futility: n/a (measurement arm; Opus 0)
reopen: n/a (new arm; READERSWEEP stage 0, LITE-TIER row)
split (declared): SE vs topic; LLM items only (16) vs pooled 20.

## Ceiling (RULE 29; 0 calls)
ceiling: the 4B ADD reads at 0.583 Haiku on the 180; a lite reader can at most match it on this slice (the reader is the only change)
bar_ceiling: n/a (pack self-tests, lite tier)
launch: coordinator brief 2026-10-16 (LITE-READERS)
transfer: product-only (lite-tier reader choice)

## Budget (RULE 29)
wall_cap: 1 h (60 generations ≈ 5 s + 27 server loads; judge ≈ 10 min)
calls_cap: Haiku 120 / Opus 0 / paid 0
smoke: smoke3 (3 ids outside random20 whose 4B ADD trace reaches the LLM; smoke3.ids sha 8f586ca6…) × 3 readers = 9 generations, gate PASS (smoke.verdict.json): 0 errors, 0 empty, 0 reasoning tokens, prompt identical to the 4B ADD dump 3/3 per reader, kept identical, `--reasoning off` in every server log. Speeds (p50 total / ttft / decode, peak RSS of llama-server): 1.7B 3.67 s / 2.87 s / 52.5 tok/s / 2665 MB; LFM2 2.62 / 2.08 / 95.0 / 1537 MB; Gemma 3.04 / 1.56 / 64.5 / 1446 MB; output tokens p50 42 / 48 / 98.
kill_if: any error/empty answer, reasoning tokens > 0 or `<think>`, prompt-identity failure (gate)
subset_step0: n/a

## Precheck (S2; 0 calls)
token_projection: 609 (smoke mean promptTokens across readers) / token_budget: 1222 (4B ADD 180 p50 622 + 600)
disk_peak_gib: 1.6 (two new GGUFs, downloaded; MacBook free 4.9 GiB, floor 4)
off_baseline: 4B ADD rows (ORACLE-ST, MacBook); 0-call identity anchor = prompt dumps byte-equal to the 4B ADD dumps
call_pattern: Haiku 5.5-low N=4 shards, both orders, each reader vs gold on random20 (3 × 40 = 120 calls); preflight probe off (PREFLIGHT_PROBE_IDS=0); 0 Opus; 0 paid
lane: mac-gen; opus_clause: none; wall_cap_h: 1; parallelism: 1; run_type: measurement

## Stages and rules
1. Generate random20 per reader on the MacBook (busy.sh; one llama-server at a time). 0-call gate (tools/gate.py r20): G0 0 errors, non-empty, 0 reasoning tokens, no `<think>`, receipt model = the reader; G1 prompt dump byte-equal (json) to the 4B ADD dump on every LLM item, the same no-LLM items as the 4B, kept list identical. FAIL -> stop, 0 Haiku.
2. Haiku 5.5-low N=4 both orders, each reader vs gold, per pack (deepthink/tools/shard_judge.sh; check_judgments.py fail-closed; 120 calls).
3. Estimator = packs-l2/tools/l2_agg.py load/setstats/paired (per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId), tools/agg.py. Report per reader: raw ratio (CI), above-min, W/T/L vs gold; paired Δ vs the 4B-ADD rows with CI and head-to-head better/tie/worse; Δ LFM2 − 1.7B and Gemma − 1.7B; ranking by raw; speed/RSS table (p50 total, ttft, decode tok/s, prompt/output tokens, words, peak RSS).
4. **Verdict (frozen; Haiku, dev random20): LEVER-shaped** only if a reader ≤ 1.2 GB (LFM2 or Gemma) beats the 1.7B by Δ raw ≥ +0.03 with CI low > 0. Otherwise **MEASUREMENT** (ranking + speed table only; no adoption). No adoption from this arm in any case (a LEVER-shaped result licenses a 180 confirmation, a coordinator call).
- One generation per reader and pack. No rerun, except after an infrastructure error before the first token.

## Stop rules
MacBook disk ≥ 4 GiB; never stop :8094, Docker or ollama; no server left running. Haiku ≤ 120, Opus 0, paid 0. No git push; `git -C rnd commit` of the arm files allowed. Delete the two new GGUFs at the end unless LEVER-shaped (DISK-LOG).

## Outputs and exposure
LITEREADERS.md (≤ 50 lines, cites this sha), aggregates/{litereaders.json, gate-*.json}, tools/*, runs/* (public self-test traces + judgments). Self-tests are public (bench/selftest); no blind/ read; rnd/veil/ never read → no EXPOSURES row. QUEUE row (tools/qrow.sh, tag main), BACKLOG rows 8 (READERSWEEP stage 0, lite tier) and LITE-TIER.
