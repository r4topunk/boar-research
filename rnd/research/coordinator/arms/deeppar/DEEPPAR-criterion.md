# DEEPPAR: deep-tier D4 desktop parity, bmoe v0.28.0 vs llama-server b11010 (frozen 2026-10-07 21:3x, coordinator)

Question: do the deep-tier numbers measured with llama-server (MOESCREEN deep35 0.596, DEEPROUTE +0.057 / R2 rule) transfer to the engine that would ship on a 12 GB phone (BigMoeOnEdge `bmoe-cli` v0.28.0 `374f562c`, the D1 pinned build)? Plan: rnd/research/forge/DEEP-TIER-PLAN.md row D4 (a) prompt tokens identical, (b) greedy first 64 tokens identical on 10 prompts, else (c) judged L1. This criterion decides (a) and (b). (c) is a separate criterion, written only if this one ends NEEDS-L1.

## Fixed inputs
- Model: `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf`, sha256 `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` (rnd/kiln/MODELS.md l.15; re-download from the recorded URL, generic UA, verify sha before any run).
- Reference engine: `<runner>/spikes/llama-b11010/build-cpu/bin/llama-server` (version 0.4.1-dev build 1, commit 4bc272f = the deep35 run's binary), launched exactly as the deep35 run: `-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --host 127.0.0.1 --port <free>`.
- Candidate engine: `bmoe-cli` built from the MacBook checkout `deep/bmoe` (v0.28.0 `374f562c920e2209b093f3349dad8ecbae439956`, llama.cpp fork `dce96985`) with the D1 host flags `-DCMAKE_BUILD_TYPE=Release -DBMOE_BUILD_TESTS=OFF -DGGML_NATIVE=OFF -DGGML_OPENMP=OFF -DLLAMA_CURL=OFF` plus `-DGGML_METAL=OFF` (CPU only, like Android). Record the built binary's sha256 and `--version` output. `<runner>/spikes/bmoe/build-cpu/cli/bmoe-cli` (74ba18f, v0.24) is NOT the candidate.
- Prompts: the 10 deep35 probe items, ids = the `NN-<itemId>.txt` names in `boar-eval/runs/night-2026-10-01/deep35/probe-prompts/` (lan-exp-001, vit-cry-001, vit-cry-004, vit-cry-003, lan-rsn-007, lan-ref-002, lan-cmp-001, trv-004, lan-exp-007, vit-cry-009). Messages = the `messages` field for those itemIds in `boar-eval/runs/night-2026-10-01/deep35/and-deep35-s42.prompts.jsonl` (system + user; v0.1 dev items, no blind exposure). sha256 of that file recorded in the result.
- Rendering: ONE rendered prompt string per item, produced by llama-server `POST /apply-template` with the item's messages and `chat_template_kwargs: {"enable_thinking": false}`, `add_generation_prompt` default. The same string is sent raw to both engines (llama-server `/completion` with `prompt: <string>`; bmoe `-p <string>` WITHOUT `--chatml` and WITHOUT `--no-think`). Record each rendered string's sha256 and its tail (last 120 chars) in the result.
- Decoding: greedy on both. llama-server: `temperature 0, n_predict 64, cache_prompt false, return_tokens true, n_probs 0`. bmoe: default sampling (greedy, `--temp` unset), `-n 64 -c 4096 -t 4 --ubatch 512 --moe-stream --overlap --dense-weights anon --cache-mb 1500 --io-threads 4` (the P0 Android knobs minus `--chatml --no-think`). No `--n-expert-used`, no `--ngram`, no `--mtp`, no `--prefetch`.
- Machine: Mac mini M4 16 GB, CPU only, one engine resident at a time, under `<runner>/bin/run-heavy` (one heavy job). No other heavy job running at start (`uptime` 1-min load < 4).

## Measures
- (a) prompt tokens: llama-server `timings.prompt_n` (or `tokens_evaluated`) vs bmoe's reported prompt token count (`n_prompt` in `BMOE_DONE`/log/csv). Equal or not, per item.
- (b) generation: llama-server `content` vs bmoe's generated text (stdout text after the prompt, stripped of engine banners), both trimmed of trailing whitespace. Identical or not, per item; if not, the character index of the first difference and the two 40-char windows around it.
- Descriptive only (no verdict): bmoe prefill s, decode tok/s, macOS peak footprint (`/usr/bin/time -l`) at `--cache-mb 1500`; llama-server `timings` per item.
- Side question (descriptive, resolves the plan's UNKNOWN "`--chatml --no-think` = jinja?"): for item 00 only, bmoe's prompt token count with `--chatml --no-think -p "<system>\n\n<user>"` (the P0 style, probe-prompts/00-*.txt) vs the jinja count from (a). Equal = the P0 memory numbers used the same prompt length as the engine; not equal = report the difference.

## Verdict rule (read strictly; no post-hoc rescue)
- **PASS:** (a) 10/10 equal AND (b) 10/10 identical. Deep-tier llama-server numbers are taken to transfer to bmoe; D4 closed, deep tier waits only for a device (D5).
- **NEEDS-L1:** (a) 10/10 equal AND (b) identical on 7–9 of 10, every divergence starting at character index ≥ 25 % of the shorter text. The fork's numerics differ slightly; write the (c) criterion (judged L1, Haiku 5.5-low paired vs the deep35 desktop traces on the EN slice) before any judged run. Not run under this criterion.
- **FAIL:** anything else (any (a) mismatch, or (b) identical on ≤ 6 of 10, or an early divergence). bmoe is a different engine from the one measured; the deep-tier numbers must not be quoted for a bmoe-based device plan until (c) is run or the fork is updated.
- One run per engine per item. A crash or a missing output on either engine for an item counts as NOT identical for that item (no rerun, except one retry if the cause is an infrastructure error logged before the model produced any token, e.g. port in use; log it).

## Stop rules
- Before download: mini free disk ≥ 35 GiB (pre-load gate incl. swap allowance); after download ≥ 25 GiB or stop and delete.
- During runs: if free disk < 25 GiB or `vm.swapusage` used > 8 GB, stop the run, kill the engine, record partial results as FAIL-INCOMPLETE (not a verdict).
- Budget: ≤ 3 h wall on the mini, 0 judge calls, 0 Opus/Haiku/Sonnet calls, no downloads other than the one GGUF.
- Never run llama-server and bmoe at the same time. Never restart Docker on the mini.
- Keep the GGUF after the run if free disk ≥ 25 GiB (a later (c) run or device prep needs it); update rnd/kiln/MODELS.md l.15 either way.

## Outputs
`arms/deeppar/DEEPPAR.md` (result, ≤ 60 lines, numbers not adjectives, cites this file's sha256), `arms/deeppar/items.csv` (item, prompt_n_server, prompt_n_bmoe, identical, first_diff_idx, server_tok_s, bmoe_tok_s, bmoe_prefill_s, bmoe_footprint_gib), raw per-item outputs under `<runner>/kiln/deeppar/out/` on the mini (copied to `arms/deeppar/raw/`, ≤ 2 MB). QUEUE entry by the coordinator.
