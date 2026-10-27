# DEEPSPEED: output-preserving speed knobs of bmoe v0.28.0 for the deep tier (frozen 2026-10-07 23:4x, coordinator)

Question: which bmoe knobs that promise unchanged output (`--ngram` self-speculation with greedy verification; `--prefetch K` expert prefetch) actually keep the text identical and speed up decode, so they can enter the recommended device flags (deep/RESUME.md "P0 flags") before a device day. `--mtp` is out: the GGUF has no nextn block (header scan 2026-10-07: 0 `blk.N.nextn` tensors). `--n-expert-used`, `--drop-cold-experts`, `--substitute*` are out (they change the output by design).

## Fixed inputs
- Engine: `<runner>/spikes/bmoe-v028/out/host/bmoe-cli` (v0.28.0 `374f562c`, prints 0.27.0, sha256 `7d5f12e8021d5ebc18a6589ab32b1a94c16dafaf3f3e128e71c70800d04df94e`, CPU only). Model: `<runner>/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` (sha `96b9c0af…dad7`, verify). Mac mini M4 16 GB.
- Prompts: the 10 DEEPPAR rendered strings `arms/deeppar/raw/NN-<id>.rendered.txt` (sha256 list in `arms/deeppar/raw/rendered-sha256.txt`; verify before use), sent raw (`-p`, no `--chatml`, no `--no-think`).
- Base flags (all configs): greedy (no `--temp`), `-n 128 -c 4096 -t 4 --ubatch 512 --moe-stream --overlap --dense-weights anon --cache-mb 1500 --io-threads 4 --csv <out>.csv`, one fresh process per (config, item) under `/usr/bin/time -l`.
- Configs: **K0** base (control); **K1** `--ngram`; **K2** `--ngram --draft 6`; **K3** `--prefetch 2`; **K4** `--ngram --prefetch 2`. Order of execution: for each item, K0..K4 back to back (so page-cache state is comparable across configs within an item; the model file is read O_DIRECT so this matters little).
- Measures per (config, item): generated text (rstripped), decode tok/s, prefill s, total wall s, peak memory footprint (`time -l`), cache hit %, and for K1/K2/K4 any draft statistics the engine reports (drafted, accepted; from the CSV summary or stderr). Medians over the 10 items per config.

## Verdict rule (per config, read strictly; one run each; no rerun except an infrastructure error logged before the first token)
- **ADOPT** if: text identical to K0 on 10/10 items AND median decode tok/s ≥ 1.15 × K0's median AND median prefill s ≤ 1.10 × K0's AND median peak footprint ≤ K0's + 0.3 GiB.
- **IDENTICAL-NO-GAIN** if text identical 10/10 but a speed/footprint bar fails (log; not adopted).
- **BROKEN** if text differs from K0 on any item (the engine's "token-identical" promise fails; never adopt; report the item and first-diff index, and note it for the upstream repo; no public posting).
- Recommended flag set = the ADOPTed config with the highest median decode tok/s (ties: fewer knobs). If none ADOPT: "P0 flags unchanged", and the ngram acceptance rate is still reported (it transfers to a phone better than tok/s).
- Caveat written into the result: mini SSD ≠ phone UFS; tok/s gains measured here are indicative, acceptance rates and identity are the transferable facts.

## Stop rules and budget
Mini free disk ≥ 25 GiB (now 36), `vm.swapusage` used > 8 GB → stop; no other llama/bmoe process; `<runner>/bin/run-heavy`; ≤ 1.5 h wall (expected 50 runs × ≈ 45 s ≈ 40 min); 0 judge / 0 API calls; nothing downloaded.

## Outputs
`arms/deepspeed/DEEPSPEED.md` (≤ 60 lines, cites this sha), `items.csv` (config, item, identical, first_diff_idx, decode_tok_s, prefill_s, total_s, footprint_gib, cache_hit_pct, drafted, accepted), `raw/` (texts, csv summaries, time -l tails; ≤ 2 MB), `tools/`. QUEUE entry by the coordinator. If a config ADOPTs, the coordinator updates deep/RESUME.md P0 flags.
