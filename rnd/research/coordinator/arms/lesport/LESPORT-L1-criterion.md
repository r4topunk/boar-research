# LESPORT-L1: judged parity of the OpenBMB llama.cpp-omni fork (LES expert streaming) vs llama-server b11010 on deep35 R450 (frozen 2026-10-16 19:4x, coordinator)

## Tags
Tags: none
Ruleset: 30

## Question
Replay of DEEPPAR-L1 (sha 1d974587…, verdict TRANSFER for bmoe) with the LES fork as the candidate: the fork's base build differs from b11010 on 9/10 greedy texts (LESPORT S0); at the judged level, are its answers of the same quality on identical R450 contexts? Used for: whether llama-server deep-tier numbers may be quoted for an LES device plan.

## Fixed inputs
- Control A (deep): arms/deepread/deep35-R450.traces.jsonl (sha12 05710eee2f92) and .judgments.jsonl (Opus judge.v1, 114 rows, 57 items). Control B (4B): as in DEEPPAR-L1 (ratio 0.606).
- Prompts: the 57 rendered strings of DEEPPAR-L1 (arms/deeppar/raw/l1/*.rendered.txt, sha list raw/l1/rendered-sha256.txt); no re-rendering.
- Model: Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf (sha256 96b9c0af…) as stripped.gguf + experts/ (expert-major, LESPORT S1 step A) on the mini.
- Candidate engine: <runner>/spikes/llama-omni (main 0b74404c) CPU build, LES bank 1280, LLAMA_MOE_LOOKAHEAD_PREFETCH=1 (S1's best lossless config), -t 4 -c 4096.
- Sampler: --temp 0.7 --top-k 40 --top-p 0.95 --min-p 0.05 --seed 42 -n 512 (the control's sampler; one seed).
- Traces: arms/lesport/les-R450.traces.jsonl = the 57 control-A rows with answer.text replaced by the fork's text (strip trailing whitespace; strip and count any <think> block), runtime fields set to the fork; splice via arms/deeppar/tools/splice.py.
- Judge: node harness/judge.mjs --traces <les traces> --out arms/lesport/les-R450.judgments.jsonl --seed 7 --system oracle-R450-les (Opus judge.v1 default, both orders, N = 4 shards allowed per OPUSSHARD).
- Analysis: arms/deeppar/tools/analyze_l1.mjs conventions (paired Δ, 2000 boots).

## Power
expected_delta: -0.01 (source: DEEPPAR-L1 bmoe vs A -0.012; the fork base differs from b11010 at the token level like bmoe did)
n: 57
seeds: 1
mde: 0.05 (DEEPPAR-L1 noise floor at n 57, temperature 0.7)
slice: n/a (full 57 only; parity arm)
l1_futility: n/a (parity clause; Opus directly, as DEEPPAR-L1)
reopen: n/a
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (parity arm)
bar_ceiling: n/a
launch: parity clause; 114 Opus calls = the same budget DEEPPAR-L1 used
transfer: n/a

## Budget (RULE 29)
wall_cap: 2 h mini generation (57 x ~60 s at 15 tok/s) + 40 min judge
calls_cap: Haiku 0 / Opus 114; 0 paid
smoke: first 3 items (load, 512 tokens, s/item); projected wall logged in the result
kill_if: > 3 items without an answer; swap used > 8 GB; disk < 25 GiB; another engine process; projected wall > 3 h
checkpoint: after 10 items (s/item)
subset_step0: n/a

## Precheck
token_projection: n/a / token_budget: n/a
disk_peak_gib: 0.1
off_baseline: deep35-R450 (control A rows)
call_pattern: Opus judge.v1 both orders on the 57 LES traces, N = 4 shards
lane: mini-long then judge
opus_clause: parity (TRANSFER / OWN-NUMBER / FAIL as DEEPPAR-L1)
wall_cap_h: 3
parallelism: 1
run_type: deep

## Verdict rule (read strictly; one generation run, one judge pass; no post-hoc rescue)
- TRANSFER: paired Δ(LES − A) point ≥ −0.030 AND its 95 % CI includes 0 → llama-server deep-tier numbers may be quoted for an LES device plan with the caveat "judged parity on 57 dev items, 1 seed, temperature 0.7 (noise floor ≈ 0.05)".
- OWN-NUMBER: not TRANSFER but LES ratio ≥ 0.606 → the LES path keeps its own number; llama-server numbers not quoted for it.
- FAIL: LES ratio < 0.606 → the fork degrades the model below the 4B; LES device planning stops until the fork base is updated.
- FAIL-INCOMPLETE: > 3 missing answers, a stop rule, or the judge not finished within budget.
