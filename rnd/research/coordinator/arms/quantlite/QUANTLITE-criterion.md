# QUANTLITE: does Qwen3-1.7B at Q8_0 beat the Q4_K_M with HEADPASS-X2b on selftest20? (frozen v2 2026-10-16 09:5x by the QUANTLITE agent; Haiku, dev)

Frozen after the 5-item Q8 smoke (runs/smoke/quantlite-q8-smoke-*, mini, 0 judge), before any judged run.
Inputs: LITE5 (LITE5-criterion v2 9ba8bbf3…, LITE5.md c9adaaca…: the Q4 + X2b st20 traces + Haiku rows lite5/runs/lite5-on-st20-s42), LITE5-180 (LITE5-180.md 8a79c858…), LITE6 (LITE6.md dc9b71b2…: residual loss to the 4B + X2b −0.065 = thin 53 % / not_read 22 % / invented 17 %), LITE2 (selftest20.ids abc23353…, bench-st20, 4B plain rows c4b-st20-s42, mini Q4 OFF speed/RSS, kit rows l-kit-v02-s42-slice).

## Tags
Tags: none
Ruleset: 30

## Question
Small models lose more to 4-bit quantisation than large ones. Arm Q8 = cut 7 + X2b + Qwen3-1.7B **Q8_0**; control Q4 = the same requests with Qwen3-1.7B **Q4_K_M** (LITE5 rows, reused). 0 engine change: the model file is the only difference. Use: lite-tier model file choice (≈ +0.7 GB download).

## Fixed inputs
- Q8: requests quantlite-q8-st20-<pack>-s42 (9 per-pack files, tools/mkreq_q.py) = LITE5's lite5-on-st20-<pack>-s42 requests with only runId and config.modelId (qwen3-1.7b-q8_0) changed; the script asserts every other byte equal. Model **unsloth/Qwen3-1.7B-GGUF @ d7f544eead698dbd1f15126ef60b45a1e1933222, Qwen3-1.7B-Q8_0.gguf, 1,834,426,944 B, sha 0becaa825564295d82e9af4d008bca5f8b7f5f73bf1c6a0b58f7c53ef26b47fd (= HF LFS oid, verified on the mini)**: same repo and revision as the Q4_K_M, so producer, chat template and tokenizer metadata are shared and quantisation is the only variable (the official Qwen/Qwen3-1.7B-GGUF @ 90862c4b Q8_0, oid 061b54da…, would add a template/producer difference; recipe recorded, not used).
- Tree: mini <runner>/kiln/be-0cfd4a77-cut7-headpass-x2 = rsync of kiln-local/be-0cfd4a77-cut7-headpass-x2 (PATCH_SHA256 0fba26b8…, HEADPASS_X2B be413d7d…, ARM cut7-headpass-x2) minus be/.cache and be/node_modules; node_modules re-linked to the mini's same-version packages (node-llama-cpp 3.21.1, tsx 4.23.15, fzstd 0.1.1, @noble/hashes 2.4.0, @boar-eval/protocol copied). Adapter be/adapter-quantlite.ts 89e31b5eec75e54c3b162f9d0b5bf3d89ae536f3b38e3ff987cd45d2e9c2ebf5 = adapter-lite5.ts 5785ffc4… + the qwen3-1.7b-q8_0 MODELS/ADAPTER_CATALOG entries (tools/adapter-quantlite.vs-lite5.patch 418acc97…). Packs: the mini's v3proto sidecar copies (kit shas in the requests are checked by the adapter). b11010 build-cpu llama-server, `--reasoning off`, -t 4, ctx 4096, seed 42, no places, :8094 detector. Runner tools/quantlite-remote-run.sh + quantlite-batch.sh (one llama-server at a time, disk floor 25 GiB per run).
- Control Q4 (REUSED, not regenerated for judging): lite5/runs/lite5-on-st20-s42 traces + Haiku 5.5-low rows (MacBook). References: 4B plain = lite2/runs/c4b-st20-s42 Haiku rows; 4B X2b = lite5/runs/x2b4b-st20.judgments.haiku55-low.jsonl.
- **Host caveat (declared):** Q8 runs on the mini (M4), Q4 rows are MacBook (M1 Pro). LITE5 hostid: same inputs re-generated on the other host keep kept/promptTokens 20/20 but answer text 5/20 → Δ includes one host re-sample (seed-like). Same-host anchor (0 judge): Q4 + X2b re-generated on the mini on the same 20 requests after the Q8 run (Q4 copied back from the MacBook, sha b139949c…, deleted right after), used for the speed clause and an answer-identity count only; if the disk floor forbids it, the speed reference falls back to LITE2's mini Q4 OFF numbers (decode p50 53.69 tok/s, RSS max 2,712,176 KiB), declared.

## Power
expected_delta: +0.00…+0.02 raw ratio (source: llama.cpp Q4_K_M vs Q8_0 perplexity gap ≈ 1–5 % on 1–3B models; LITE6: the buckets a better-quantised model could touch, not_read + invented, are 39 % of the 0.065 gap ≈ 0.025)
n: 20 (selftest20, judged)
seeds: 1
mde: ≈ 0.04–0.05 raw at n = 20 (LITE2/LITE5, Haiku) plus host re-sample noise. expected_delta < mde: at n = 20 the arm can only see a large (≥ 0.04) quant effect; a DIRECTION-POSITIVE result does not decide anything. Declared, run anyway as a cheap screen per the coordinator brief (40 calls).
slice: lite2/selftest20.ids (abc23353…)
l1_futility: Δ ≤ 0 → close (FLAT/NEGATIVE, delete the Q8 from the mini)
reopen: CLOSED R37 (QUANTCEIL, 10-12) closed deep-tier precision (35B, 2-bit → 3-bit): new here = the 1.7B lite model, 4-bit → 8-bit, where small-model quant loss is expected to be larger
split (declared): by LITE6 bucket of the Q4 item where the 20 ids are in the LITE6 below-4B set (thin / not_read / invented / other), descriptive only.

## Ceiling (RULE 29; 0 calls)
ceiling: ≤ +0.065 (the whole Q4 + X2b gap to the 4B + X2b on the 180, LITE5-180); realistic ≈ +0.025 (not_read + invented share)
bar_ceiling: n/a (pack self-tests, lite tier)
launch: coordinator brief 2026-10-16 (mini idle)
transfer: kit slice random20-v02 (stage 6) only if LEVER-shaped

## Budget (RULE 29)
wall_cap: 1 h (20 generations ≈ 6 s each + 9 server loads ≈ 40 s; judge ≈ 5 min)
calls_cap: Haiku 80 / Opus 0 (40 = selftest20 Q8; 40 only for the stage-6 kit slice). LEVER-shaped additionally licenses the 180 self-tests (another 360 Haiku, declared here; then a separate run under this sha)
smoke: 5 items (factbook-004, simplewiki-en-018, ethereum-se-002, outdoors-se-008, travel-se-001; Q8 + X2b, mini): 0 errors, 0 empty, 0 reasoning tokens, no `<think>`; headpass codes and kept lists = Q4 traces 5/5; promptTokens = Q4 5/5 (shared tokenizer); decode p50 33.96 tok/s (Q4 mini OFF ref 53.69, Q4 MacBook ON same 5 items 44.23); prefill p50 289 tok/s; total p50 6.09 s; RSS per-run max 3.41–3.76 GiB (Q4 LITE2 max 2.59 GiB → 1.45×); wall ≈ 40 s per pack run incl. load
kill_if: any error/empty answer, reasoning tokens > 0 or `<think>`, any 0-call gate FAIL (→ stop, 0 Haiku), projected wall > 1.5 h
checkpoint: the 0-call gate, before any judge call
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 959.8 (smoke mean timing.promptTokens: 937, 1013, 1145, 815, 889) / token_budget: 960 (= the Q4 + X2b traces on the same 5 items, 959.8, rounded up to the integer; identical tokenizer)
disk_peak_gib: 2.8 (Q8 1.71 GiB + transient Q4 anchor 1.03 GiB; mini floor 25 GiB checked before every run)
off_baseline: lite5-on-st20-s42 (LITE5 Q4 + X2b, MacBook)
call_pattern: Haiku 5.5-low N=4 shards, both orders, Q8 vs gold on selftest20 (40 calls); preflight live probe disabled (PREFLIGHT_PROBE_IDS=0); 0 Opus; 0 paid
lane: mini-long
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Smoke (done before the freeze): `arm.sh arm-st-Q8.conf smoke runs/smoke/quantlite-q8-smoke-s42.traces.jsonl --n-full 20 --marker headpass:` writes smoke.verdict.json for this sha.
2. Generate Q8 (mini, sequential): the 9 per-pack files, merged to runs/quantlite-q8-st20-s42.traces.jsonl.
3. **0-call gate (tools/gate_q.py):** G0 0 errors, 0 empty, 0 reasoning tokens, no `<think>`; G1 headpass:* codes and kept (title, section) lists identical to the Q4 traces 20/20; G2 promptTokens identical to the Q4 traces on every LLM item. FAIL → stop, 0 Haiku.
4. Gate PASS → Haiku 5.5-low N=4 both orders, Q8 vs gold on the 20 (40 calls; arm.sh l1 REPLAY=1, control = LITE5 Q4 rows). Paired Δ(Q8 − Q4) = deepvpara/tools/paired.mjs (items resampled jointly, 2000 boots). Also Q8 − 4B plain and Q8 − 4B X2b (same reference rows as LITE5), W/T/L vs gold, head to head, split above, p50 words.
5. **Verdict (frozen; Haiku, dev):** **LEVER-shaped** if paired Δ ratio ≥ +0.03 AND CI low > 0; **DIRECTION-POSITIVE** if Δ > 0 otherwise; **FLAT/NEGATIVE** if Δ ≤ 0. **Speed clause** (mini, Q8 vs the same-host Q4 anchor on the same 20 requests): decode p50 ≥ 0.7× the Q4's AND RSS max ≤ 2× the Q4's → PASS, else the Q8 is "quality-only" (a LEVER with a speed FAIL is not a default candidate without a device decode measurement). No adoption from this arm.
6. Only if LEVER-shaped: (a) kit slice random20-v02 under LITE2's scoped script-only exception (counts/ids only, EXPOSURES row): Q8 with the claim kit, 20 generations, Haiku 40 vs gold, paired vs LITE2's Q4 l-kit-v02-s42-slice rows (same mini host); (b) the 180 self-tests (360 Haiku) as a separate run.
- One generation per run. No rerun, except after an infrastructure error before the first token.
- Freeze history: a pre-edit draft bf67ad64… was replaced within the minute (reopen line only, 0 runs). v1 9e6cea89eb67452ccd3a479f93b5834ba13cb131ad13f09afaf4e60228940db0 (QUANTLITE-criterion.v1.md) set token_budget 959.8 = the smoke mean exactly; smoke-project.py read it as FAIL ("959.8 > 959.8", a float-vs-decimal equality artefact; smoke.verdict.v1-FAIL.json). Re-frozen as this v2 with token_budget 960, same smoke traces, before any Q8 st20 generation or judge call.

## Stop rules and budget
Mini disk ≥ 25 GiB before each run (runner refuses); never Docker, never :8094 (left up), never ollama; one llama-server at a time; none left running. Haiku ≤ 80 (40 unless stage 6), Opus 0, 0 paid. No git push; `git -C rnd commit` of the arm files allowed. The Q8 is deleted from the mini only on FLAT/NEGATIVE (DISK-LOG either way).

## Outputs and exposure
`arms/quantlite/QUANTLITE.md` (cites this sha), `aggregates/` (gate, speed, L1 JSON), `tools/`, traces under `runs/`. Self-tests are public; blind/ only for stage 6 (then one EXPOSURES row). rnd/veil/ is never read. QUEUE row (tools/qrow.sh, tag main), BACKLOG LITE-TIER row.
