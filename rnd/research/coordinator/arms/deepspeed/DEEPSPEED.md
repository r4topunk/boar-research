# DEEPSPEED result: bmoe v0.28.0 output-preserving speed knobs (deep tier): **no ADOPT, P0 flags unchanged**

Criterion: `DEEPSPEED-criterion.md` sha256 `c2e101d35127055b65e7aee54c75e4b161a007d6c2ea70d53be96a22e05f6896` (verified 23:32 before start, not edited). Runner: Kiln, 2026-10-07 23:32 to 2026-10-08 00:15. 0 judge, 0 `claude -p`, 0 API calls, nothing downloaded.

**Pre-checks (mini 23:32):** free 36 GiB (≥ 25 ok), swap used 1062 MB / 2048, load 1.33. No llama/bmoe process (only `ollama serve`, idle). Binary `<runner>/spikes/bmoe-v028/out/host/bmoe-cli` sha256 `7d5f12e8…f94e` = criterion. GGUF sha256 `96b9c0af…a70dad7` = expected. Prompts: the 10 DEEPPAR rendered strings copied to `<runner>/kiln/deepspeed/prompts/`, `shasum -c rendered-sha256.txt` 10/10 OK. `bmoe-cli --help` confirms the spellings `--ngram`, `--draft N` (default 3, max 8) and `--prefetch K`.
**Run:** `<runner>/bin/run-heavy kiln-deepspeed` (waited 0 s) under nohup, driven by `tools/run_deepspeed.py`. Base flags `-n 128 -c 4096 -t 4 --ubatch 512 --moe-stream --overlap --dense-weights anon --cache-mb 1500 --io-threads 4 --csv`, prompt via `-p <rendered>` (no `--chatml` or `--no-think`), greedy. For each item, K0..K4 ran back to back as fresh processes under `/usr/bin/time -l`. 50/50 runs exited rc 0, with no retries. Generated text = stdout minus the echoed prompt, cut at the `\n\ngeneration:` trailer, rstripped.

**Medians over 10 items** (decode tok/s and prefill s from the CSV `# summary`, total = `time -l` real, footprint = `time -l` peak memory footprint; drafted/accepted summed from stdout `ngram: A/D drafts accepted`):

| config | decode tok/s | prefill s | total s | footprint GiB | cache hit % | identical to K0 | drafted / accepted (rate) | verdict |
|---|---|---|---|---|---|---|---|---|
| K0 base | 8.69 (1.00x) | 20.74 | 38.4 | 10.25 | 40.0 | (control) | - | control |
| K1 `--ngram` | 7.36 (0.85x) | 21.24 | 40.9 | 10.44 | 39.1 | **2/10** | 210 / 70 (33.3 %) | **BROKEN** |
| K2 `--ngram --draft 6` | 5.89 (0.68x) | 21.45 | 43.4 | 10.63 | 36.4 | **2/10** | 366 / 79 (21.6 %) | **BROKEN** |
| K3 `--prefetch 2` | 8.18 (0.94x) | 20.80 | 38.7 | 10.25 | 40.8 | 10/10 | - | **IDENTICAL-NO-GAIN** |
| K4 `--ngram --prefetch 2` | 6.96 (0.80x) | 21.03 | 41.2 | 10.43 | 39.8 | **2/10** | 210 / 70 (33.3 %) | **BROKEN** |

**Identity detail (ngram configs):** K1, K2 and K4 differ from K0 on 8/10 items (only 07 and 08 match). On every item the K1, K2 and K4 texts are byte-identical to one another, even though the draft width differs (3 vs 6). First-diff char index vs K0: 00 @353, 01 @125, 02 @178, 03 @96, 04 @34, 05 @88, 06 @237, 09 @90. Examples: 04 K0 `built in 1961 [2]. It came down` vs ngram `built in 1961 and came down in 1989 [2]`; 05 K0 `resulted in the abolition of slavery` vs ngram `resulted in the defeat of the Confederate`. Item 05 drafted on only 1 of its decode steps and still diverged. Reading (inference, not tested): the divergence comes from the wider verify-batch numerics of the `--ngram` path (a batched decode ≠ a single-token decode on this CPU/fork), not from accepting wrong drafts. The engine's "token-identical" promise fails here. **Note for the upstream bmoe repo** (no public posting without r4to's OK). On items 03 and 04 the ngram text happens to match llama-server b11010's DEEPPAR wording more closely than K0 does (03 `blocks and receipts older`, 04 `1961 and`), which is consistent with a batched-kernel numeric path.
**Draft stats (K1):** ngram drafted on 1.5–28 % of decode steps (median about 12 %). Acceptance was 33.3 % at draft width 3 and 21.6 % at width 6, with about 1.09 tokens per verify decode on item 00. That is too few to pay for the verify batch, so decode is slower in every ngram config.
**K3 `--prefetch 2`:** text identical 10/10. Decode 0.94x K0 (bar ≥ 1.15x fails), prefill 1.00x, footprint +0.00 GiB.

**Verdict rule (quoted):** "ADOPT if: text identical to K0 on 10/10 items AND median decode tok/s ≥ 1.15 × K0's median AND median prefill s ≤ 1.10 × K0's AND median peak footprint ≤ K0's + 0.3 GiB. IDENTICAL-NO-GAIN if text identical 10/10 but a speed/footprint bar fails (log; not adopted). BROKEN if text differs from K0 on any item (… never adopt; report the item and first-diff index, and note it for the upstream repo; no public posting). … If none ADOPT: 'P0 flags unchanged', and the ngram acceptance rate is still reported."
- K1 BROKEN (8/10 items differ), K2 BROKEN (8/10), K3 IDENTICAL-NO-GAIN (0.94x), K4 BROKEN (8/10).
- **Recommended flag set: P0 flags unchanged.** ngram acceptance on this deep-tier RAG workload: 33.3 % (draft 3) and 21.6 % (draft 6).

**Caveat:** mini SSD ≠ phone UFS. The tok/s gains measured here are indicative; the acceptance rates and the identity results are the transferable facts.
**Stop-rule events:** none. The watchdog (every 5 s) never fired. Free disk min 32.6 GiB, swap used peak 5436 MB (< 8 GB; total swap grew 2 → 6 GB). No other engine was running at start (the driver checks `pgrep`). Docker untouched.
**Mini after (00:07):** free 32 GiB, swap used 4.75 GB / 6.1 GB, only `ollama serve`.
**Time:** heavy run 23:33:47–00:07:23 (33.6 min, 50 runs at about 40 s each). Budget 1.5 h.

Files: `items.csv` (config, item, identical, first_diff_idx, decode_tok_s, prefill_s, total_s, footprint_gib, cache_hit_pct, drafted, accepted, tokens). `raw/` (848 KB): `<item>__<K>.gen.txt` generated text, `.csv-summary.txt` CSV `#` lines, `.stderr.txt` stderr head 30 + tail 40 (includes the `time -l` block), plus `run.log` and `driver.out`. `tools/run_deepspeed.py` and `tools/compare.py`. Mini copies are in `<runner>/kiln/deepspeed/`, with full outputs in `out/`.
