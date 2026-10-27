# DEEPTHINK-V02 result (runner agent for generation, coordinator for L1; 2026-10-08 23:05 – 2026-10-09 02:32). Criterion DEEPTHINKV02-criterion.md sha256 265ea559… (`.sha256`; not edited)
**L1: NO by the frozen rule.** Haiku paired Δ TV − D = **+0.027** (CI +0.002…+0.054) vs the +0.03 clause (deduplicated 220 rows; the raw 266-row file gives +0.029, same verdict); wins-vs-ref 0 vs 0 (needs +3). Read strictly (no post-hoc rescue): the thinking arm is not promoted on v0.2, no Opus run, no seed 43, no claim number. The sign agrees with V-para (DEEPTHINK +0.046 Haiku, +0.075 Opus): thinking helps the deep tier on v0.2 too, but by less than the triage threshold on this seed.

## Parametrisation (aggregates/parametrisation.txt)
DEEPTHINK-2 ended NOT PROMOTED (Δ +0.010) → budget **1024**, tree `be-0cfd4a77-deepthink` (cut 6 PATCH_SHA256 824e0b35… + deepthink patch eb3f464b…), be-repo/adapter.ts 7a0282ae… (ctx 4096, BOAR_SERVER_CTX unset), runner `deepthink-remote-run.sh` 9d86a83f… (= arms/deepthink/tools/remote-run.sh), args `dtv-TV-v02-s42 D noplaces`, `--timeout-ms 600000`. Requests s42 sha 2d9770a41168 (items 0e664600cb7b = DEEPVPARA D's); s43 prepared (03522ff5f224), not run. Pre-checks 23:04: free 34 GiB, swap 1.0 GB, detector :8094 up, no 35B server, heavy lock free.

## Generation (v0.2, 110 items, seed 42; desktop proxy, mini M4 CPU `-t 4`)
| run | n / errors | deep routed | deep-thinking | reasoning tok p50 (p10/p90/max) | budget hits | answer tok p50 | total p50 (p90) | D total p50 | mini wall |
|---|---|---|---|---|---|---|---|---|---|
| dtv-TV-v02-s42 | 110 / 0 | 109 (tier deep 107, instant 3) | 109 | 1034 (0 / 1034 / 1034) | **58 / 91 generated** (`thinkingBudgetExceeded`) | 69 | **132.6 s** (158.2) | ≈ 33 s (DEEPVPARA) | 3.31 h (23:05–02:24, rc 0) |
The 19 "deep-thinking" items with 0 reasoning tokens made **no generation at all** (0 generation events, answer 0 tokens, total ≈ 0.28 s): 18 are `detector:fire` items (danger/health card path) + 1 other deterministic path, exactly as in D. Among the 91 items that generated, 58 hit the 1024 budget (64 %; V-para 36/51 = 71 %). Detector consulted 110/110, never stopped; disk 34 GiB throughout; traces sha b69323e0a5f3; adapter desktop-node@155b8bafa87c, backend llama-server, deep model sha 96b9c0af5c77.

## L1 (Haiku 5.5-low, judge.v1-low, sharded N = 4, both orders, 110 ids, refs 1e2668c488a1 / questions c883053b0595, `--system deepthinkv02-TV-haiku55-low`)
| arm | ratio (CI) | floor-adj | wins vs ref | ties | h2h TV>D / = / TV<D |
|---|---|---|---|---|---|
| TV (deep + thinking 1024) | **0.534 (0.504–0.563)** | 0.413 | 0 / 110 | 1 | 51 / 19 / 40 |
| D (deep, no thinking; DEEPVPARA Haiku rows s42) | 0.507 (0.474–0.541) | 0.377 | 0 / 110 | 2 | |
Paired (n = 110): Δ ratio **+0.027 (+0.002…+0.054)**, Δ floor-adj +0.035 (+0.004…+0.070). Rule: "wins TV ≥ D + 3" 0 ≥ 3 FAIL; "Δ ≥ +0.03" 0.027 FAIL → **NO** (raw 266-row file: +0.029, also NO). Judge: 0 failures.
**Deviation (process):** the runner agent's background poll and the coordinator both ran `l1.sh 42` at 02:2x–02:3x (the runner task had shown as completed), both writing the same shard files: 266 rows for 220 (id, order) keys, 46 keys judged twice; the runner kept the earliest row per key (`.raw266.jsonl` kept beside the deduplicated file), the coordinator recomputed paired.mjs on the 220 rows (numbers above). Haiku spend 266 calls, over the 240 cap because of the collision. Earlier deviation (runner): the first launch failed before the first token on the requests' arm label (`deepthinkv02` vs the tree's `deepthink`); relabelled and relaunched once, as the criterion allows.

## Reading
- On v0.2 (development data) thinking adds about +0.03 Haiku-scale on one seed, CI above 0, head-to-head 55/40; on V-para it added +0.046 Haiku / +0.075 Opus. Haiku compresses gaps (L1-PROTOCOL), so the Opus-scale effect on v0.2 is likely larger, but by the frozen rule it is not measured. The bar question ("does deep + thinking cross 0.50 floor-adjusted on v0.2") stays unanswered on Opus; on the Haiku scale TV's floor-adj is 0.414.
- Cost is the same as on V-para: p50 133 s vs ≈ 33 s (×4), budget hit on 2/3 of generated items.
- Time-to-first-visible is the whole thinking time (p50 130 s): the deep tier shows nothing while thinking in this runner; a product would stream the reasoning or an interim answer.
- Optional follow-up if the deep tier ever enters the claim: Opus N = 4 on TV s42 (220 calls) + seed 43 to size the v0.2 effect on the claim scale; not run (rule).

## Exposures (script-only; no blind content in any context)
v0.2 (blind/bench-v02): 1 generation run `runs-deepthinkv02/dtv-TV-v02-s42` (110); Haiku judging 110 ids (220 calls); D Haiku rows re-read by paired.mjs. Requests for s43 written, not run. Outputs: `blind/bench-v02/runs-deepthinkv02/` (traces, judgments + shards, think per-item, paired JSON); aggregates in `aggregates/` (no per-item).
Cost: Haiku 266 (cap 240; collision, see deviation), Opus 0, mini 3.3 h. Per-category Haiku Δ (aggregates/percat-TVvsD-s42.haiku55-low.json, descriptive): comparison +0.106 is the only clear gain; crypto +0.041; danger −0.011, health −0.008. Tools: tools/{dtv.sh,l1.sh,l2.sh,paired.mjs,percat.mjs,shard_judge.sh,wait-run.sh,wait-dt2.sh}.

## Addendum 1 result (claim-scale measurement, 2026-10-09 08:2x–15:51; DEEPTHINKV02-L2-addendum.md sha 92121156…; the L1 NO stands)
| arm (v0.2, 110, dev data; Opus judge.v1 N = 4; floor_metrics with questions.v02-new strata, D_decl 0.306) | raw (CI) | floor-adj (CI) | above-decline (CI) | win-rate |
|---|---|---|---|---|
| **TV deep + thinking 1024 (s42+s43)** | **0.612 (0.581–0.644)** | **0.514 (0.475–0.554)** | 0.442 (0.397–0.487) | 0/110 ×2 |
| D deep, no thinking (DEEPVPARA) | 0.568 (0.536–0.602) | 0.457 (0.417–0.500) | 0.377 (0.331–0.426) | 0/110 ×2 |
| K 4B claim run (cut 6) | 0.512 (0.478–0.549) | 0.388 (0.346–0.434) | 0.297 (0.248–0.350) | 0/110 ×2 |
Paired two-level (aggregates/paired_gap-TVvs{D,K}-2seed.txt): TV − D raw **+0.045 (+0.022…+0.070)**, floor-adj +0.056 (+0.027…+0.088); TV − K raw **+0.100 (+0.070…+0.132)**, floor-adj +0.125 (+0.088…+0.166). Per seed vs K: s42 +0.094, s43 +0.107; h2h 49/38/23 and 53/35/22. Per category vs K (s42, descriptive): honesty +0.30, comparison +0.12, crypto +0.11, reasoning +0.10, health +0.05, danger 0, explanation −0.01, synthesis −0.01.
**Bar reading:** "floor-adjusted CI low > 0.50 and win-rate > 0" is NOT met (CI low 0.475; win-rate 0). The point estimate 0.514 is above 0.50: "point above, CI straddles" on a burnt/development set; not claim evidence, the final number needs v0.3.
Generation s43: the run launched 08:54 completed 12:10 but was overwritten by a duplicate launcher at 12:11 (QUEUE deviation); the rerun (same requests f219654e, seed 43) ran 12:11–15:4x and is the s43 used here. Cost of the addendum: Opus 440, mini 2 × 3.3 h (one lost).
