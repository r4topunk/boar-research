# JUDGE2: Gemma 4 26B-A4B UD-Q2_K_XL as a local judge.v1 (Kiln, 2026-10-07): full run, both legs (Addendum 1 rerun 16:04–18:41)
**TL;DR:** 228/228 calls, 0 JSON failures, 0 thinking tokens, **41–43 s/call**. Gemma keeps Opus's **ranking** (deep35 − 4B **+0.026**, CI −0.001…+0.058, vs Opus **+0.029**, CI −0.004…+0.063). It picks the same winner as Opus on **86–88 %** of items. It is **not** a drop-in ratio judge: it scores **+0.11 above Opus** on both legs (CI excludes 0) and is lenient on BOAR correctness (κ ≥ 4 only 0.32 / 0.55). Use it for triage and ranking, never as the headline number. Criterion 4e825da3… (sha OK), 0 Opus calls.
## Inputs (sha256 first 12, recorded before the first call; full list in `inputs.sha256`, all re-verified OK at 18:45)
| input | sha |
|---|---|
| deep35-R450 traces / Opus judge.v1 / Sonnet-low / Sonnet-med | 05710eee2f92 / b40265bf921b / c4d5400d6054 / fa40dcd451ea |
| qwen3-4b-R450 traces / Opus judge.v1 | 21a761a3ca1a / d51e87775b38 |
| refs / questions (v0.1) | bd235bb9811f / 568b3ececd8a |
| judge-core.mjs (boar-eval = shim copy) / judge.mjs / shim claude-cli.mjs | 521f7ad33a13 / b3c3cd160dab / 11e50a6e22e8 |
| llama-server b11010 (0.4.1-dev 4bc272f) / GGUF | 7fe62554ccd0 / 2a1d26dfe6ea (verified after download) |
## Setup (unchanged from the frozen method)
- `harness/judge.mjs` ran on the MacBook with `BOAR_EVAL_LIB=arms/judge2/shim`. The shim POSTs to the mini's llama-server (`<runner>/bin/run-heavy`, `-t 4 -c 4096 -np 1 --jinja --no-webui`, default mmap) through `ssh -T -N -L 18091`. The driver `judge2-run.mjs` ran leg A then leg B (`--bench bench/v0.1 --effort gemma4q2 --gap-ms 0 --seed 7`, judgeVersion `judge.v1-gemma4q2`) and checked disk and swap every 10 calls.
- Request settings: temp 0, seed 7, max_tokens 400, enable_thinking false, json_schema = VERDICT_SCHEMA, judge.v1 bytes unchanged.
- Gates (`gates.txt`): free 37.5 GiB ≥ 35 GiB before load PASS; model loads PASS; smoke2 3/3 valid, verdicts byte-identical to run-1 smoke PASS.
## Results (orders combined per item; 57 items per leg; Δ = Gemma − ref judge, 2000 joint boots seed 5)
| measure | leg A deep35-R450 | leg B qwen3-4b-R450 |
|---|---|---|
| same winner as Opus | **49/57 (86.0 %)** | **50/57 (87.7 %)** |
| same winner as Sonnet-low | 50/57 (87.7 %) | n/a (no Sonnet-low judgments of 4B in the frozen inputs) |
| κ, BOAR correctness ≥ 4, vs Opus (vs Sonnet-low) | 0.32 (0.18) | 0.55 |
| Pearson r, BOAR mean rubric, vs Opus | 0.86 | 0.85 |
| ratio Gemma vs Opus | 0.745 vs 0.634 | 0.718 vs 0.606 |
| Δratio vs Opus | **+0.110 (+0.085…+0.134)** | **+0.112 (+0.082…+0.142)** |
| Δratio vs Sonnet-low | +0.147 (+0.120…+0.174) | n/a |
| position consistency Gemma / Opus | 86.0 % / 96.5 % (≥ 80 %, not noise) | 93.0 % / 98.2 % |
| win / tie / loss (Gemma) | 0 / 15.8 / 84.2 % | 3.5 / 8.8 / 87.7 % |
| BOAR C / Cm / U, Gemma (Opus) | 4.65 / 3.16 / 3.34 (3.89 / 2.66 / 2.78) | 4.39 / 3.05 / 3.28 (3.58 / 2.58 / 2.76) |
| ref C / Cm / U, Gemma (Opus) | 4.97 / 5.00 / 5.00 (4.80 / 4.94 / 4.97) | 4.94 / 5.00 / 5.00 (4.83 / 4.93 / 4.96) |
| JSON failures / reruns / think leaks | 0/114 / 0 / 0 | 0/114 / 0 / 0 |
| s/call median (mean, max); wall | 41.0 (40.6, 60.1) s; 77 min | 42.6 (42.1, 56.6) s; 80 min |
| tokens median: prompt / cached / output; prefill / decode tok/s | 866 / 265 / 141; 23.4 / 9.6 | 859 / 265 / 141; 23.2 / 9.5 |
- Sonnet-low vs Opus on leg A (reference): 54/57, κ 0.68, r 0.93, Δ −0.037 (reproduces JUDGE-TRIAGE).
- Winner disagreements with Opus. Leg A: lan-cmp-001, lan-rsn-002, vit-sci-002, lan-ref-003, lan-exp-003, lan-exp-007 (Gemma tie, Opus ref), lan-ref-004 (ref/tie), lan-ref-005 (tie/boar). Leg B: lan-cmp-001 and lan-exp-007 (Gemma boar, Opus ref), lan-rsn-002, lan-exp-003, lan-rsn-007 (tie/ref), lan-ref-004 (ref/tie), lan-ref-005 (tie/boar). These are mostly the long-form `lan-*` items.
## Cross-leg ranking (deep35 − 4B, paired on 57 items)
| judge | Δratio (CI) | items deep35 better / worse |
|---|---|---|
| Gemma 4 Q2 | **+0.026 (−0.001…+0.058)** | 25 / 10 |
| Opus judge.v1 | +0.029 (−0.004…+0.063) | 26 / 18 |
- **Ranking preserved: YES.** The sign and size match, within 0.003. Neither CI excludes 0 under either judge, so Gemma says what Opus says: a small, unproven deep35 edge.
## Disk and swap (Addendum 1 monitor, `legA|legB/disk.jsonl`)
- Free disk 27.47–30.46 GiB over the run (floor 25 held), swap 7.0–12.1 GB, server RSS 3.3–5.3 GB. After cleanup (18:42): llama-server stopped, Gemma GGUF deleted, **free 46.2 GiB, swap 3.0/4 GB**. deep35 GGUF stays deleted (re-downloadable; MODELS.md and DISK-LOG.md updated).
## History: run 1 (15:00–15:52, criterion 2c3ff0eb…), STOPPED by the disk rule
- Swap grew 2 → 10.4 GB and free disk fell to 19.0 GiB at leg A 56/114 calls. On those 28 items: same winner 26/28, κ 0.36, r 0.87, Δ +0.116 (+0.084…+0.149), 44 s/call. The verdicts are kept in `run1-stopped/` and `analysis-legA-partial.json` and were not merged. The full leg A reproduces them: Δ +0.110, with winner agreement lower on the second half (86 %).
## Deviations
1. Run 1 was stopped by the frozen disk rule. Addendum 1 reran both legs from scratch, with a disk gate that counts swap and the deep35 GGUF deleted first.
2. judge.mjs ran on the MacBook through a port-forward, not on the mini (boar-eval is not there). The model call is unchanged.
4. **Supervisor hand-over:** the supervising Kiln agent died when the coordinator session restarted, around leg B 13/114 (17:30). The driver process (caffeinate → judge2-run.mjs → judge.mjs + tunnel) kept running untouched and was **never restarted**. A new Kiln agent took over at 17:31, monitored it every ~10 min until it ended (18:41, exit 0), then ran the analysis and the cleanup. The 228 rows have unique (queryId, order) keys, all ok.
5. Leg B has no Sonnet-low comparison, because the frozen inputs list Sonnet-low only for deep35.
## Files
- `boar-eval/runs/kiln/judge2/`: `deep35-R450.judgments.gemma4q2.jsonl` (114), `qwen3-4b-R450.judgments.gemma4q2.jsonl` (114), `legA/` and `legB/` (`calls.jsonl`, `disk.jsonl`, `driver.log`, `judge.log`), `smoke/`, `smoke2/`, `run1-stopped/`, `legs.log`.
- `arms/judge2/`: `analysis-full.json` (this report), `analysis-config.json`, `shim/`, `judge2-run.mjs`, `judge2-analysis.mjs`, `selftest.json`, `analysis-legA-partial.json`, `inputs.sha256`, `gates.txt`.
## UNKNOWN
- Why the leniency happens: Gemma gives BOAR correctness 4–5 where Opus gives 3, and it does so on both legs. A calibration offset of about −0.11 seems to hold across two systems, but two systems are not enough to call it a constant.
- How JUDGE2 behaves on v0.2/v0.3. This run was v0.1 dev only, and blind sets were not touched.
