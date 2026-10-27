# DEEPPAR result: bmoe v0.28.0 vs llama-server b11010, D4 (a)+(b) — **FAIL**

Criterion: `DEEPPAR-criterion.md` sha256 `98028c0dcd84e4c63abbdb61d280c92fe866b52b8ddef9526ed7d4c08322ce18` (verified 21:17 before start). Runner: Kiln, 2026-10-07 21:17–21:45. 0 judge / 0 `claude -p` / 0 API calls.

**Pre-checks (mini 21:18):** free 48 GiB (≥ 35 ok), swap used 1048 MB / 2048, load 1.77, no llama/bmoe process (only ollama serve idle). `<runner>/bin/run-heavy` used for build and run (both waited 0 s).
**Build:** `<runner>/spikes/bmoe-v028` via `build-bmoe.sh host` (pins checked: bmoe `374f562c920e2209b093f3349dad8ecbae439956` tag v0.28.0, llama.cpp `dce9698510b76746db625b644ef2af899517d0ad`, clean tree; flags COMMON + `-DGGML_METAL=OFF -DGGML_BLAS=OFF`), 33 s. `out/host/bmoe-cli` sha256 `7d5f12e8021d5ebc18a6589ab32b1a94c16dafaf3f3e128e71c70800d04df94e`; `--version` prints **`0.27.0`** (upstream CMakeLists `project(... VERSION 0.27.0)` not bumped at the v0.28.0 tag; source is the pinned commit). BUILD.json on the mini.
**Model:** re-downloaded 21:21–21:27 (generic UA `curl/8`), sha256 `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` = expected; 12,290,628,576 B. Free after: 36 GiB (≥ 25 ok).
**Prompts:** `boar-eval/runs/night-2026-10-01/deep35/and-deep35-s42.prompts.jsonl` sha256 `38df93c3ef2d85f575d1f254d178251c1c7a452ac60d08193eb36bf836a9973c` (59 lines; 1 row per item id, system+user).
**Reference:** `llama-b11010/build-cpu/bin/llama-server` (0.4.1-dev build 1, 4bc272f), exact criterion flags, port 18093, healthy after 14 s; stopped with SIGTERM rc 0, `pgrep llama-server` = none, before bmoe started.

| id | rendered sha12 | tail (last 120 chars, all 10 identical except 08) |
|---|---|---|
| 00-lan-exp-001 | d8b3126fc238 | `…it short: 2-3 sentences. No lists unless the question asks for one.)<\|im_end\|>\n<\|im_start\|>assistant\n<think>\n\n</think>\n\n` |
| 01-vit-cry-001 | a9ac59124098 | same |
| 02-vit-cry-004 | fa1270edf54b | same |
| 03-vit-cry-003 | 42b3909fd0e7 | same |
| 04-lan-rsn-007 | 5e0978c1ca8d | same |
| 05-lan-ref-002 | 155ca3b1348a | same |
| 06-lan-cmp-001 | 4d0c5874621a | same |
| 07-trv-004 | 4cbf95c27528 | same |
| 08-lan-exp-007 | 139c936c07f5 | `…asks for one.\nToday is Friday, 2 October 2026 (this device's date).)<\|im_end\|>\n<\|im_start\|>assistant\n<think>\n\n</think>\n\n` |
| 09-vit-cry-009 | 673308b237a3 | same as 00 |
Full sha256 in `raw/rendered-sha256.txt`.

**(a) prompt tokens and (b) greedy 64 tokens** (server `timings.prompt_n` = `tokens_evaluated`; bmoe `n_prompt` from the CSV `# summary`; texts rstripped; % = first_diff_idx / shorter text length):

| item | prompt server/bmoe | (a) | (b) | first diff idx (%) | server window | bmoe window |
|---|---|---|---|---|---|---|
| 00 | 616/616 | = | no | 112 (36 %) | `ned independence on 9 August 1965 after ` | `ned independence on August 9, 1965, afte` |
| 01 | 637/637 | = | no | 9 (3 %) | `Ethereum plans to use account` | `Ethereum currently relies on ` |
| 02 | 650/650 | = | no | 260 (81 %) | `ographic mechanisms to allow each node t` | `ographic mechanisms for uniform random d` |
| 03 | 679/679 | = | no | 96 (33 %) | `ing historical blocks and receipts older` | `ing historical block data older than the` |
| 04 | 667/667 | = | no | 34 (24 %) | `l was built in 1961 and fell in 1989 [2]` | `l was built in 1961 [2]. It came down in` |
| 05 | 622/622 | = | no | 57 (33 %) | `e American Civil War [2]. This victory r` | `e American Civil War. This victory resul` |
| 06 | 627/627 | = | no | 82 (35 %) | `he provided context only mentions their ` | `he provided context does not list popula` |
| 07 | 664/664 | = | no | 34 (13 %) | `nient option is the metro, where the Red` | `nient option is the Metro, where the Red` |
| 08 | 599/599 | = | no | 68 (23 %) | `Kingdom of Denmark, with its capital and` | `Kingdom of Denmark, governed by its own ` |
| 09 | 629/629 | = | no | 44 (23 %) | `ded 312 validators (312 * 32 ETH = 10,00` | `ded 312 validators (10,000 ETH / 32 ETH ` |

(a) **10/10 equal**. (b) **0/10 identical**; 5 divergences start < 25 % of the shorter text (01 at the first token). Both engines ended every run rc 0; no crash, no retry. Server stopped at EOS on 04/05/06 (46/44/47 tokens), bmoe on 03/04/05/06 (59/40/35/49).

**Descriptive (min / median / max over 10, no verdict):**

| engine | prefill s | decode tok/s | peak footprint (`time -l`) |
|---|---|---|---|
| llama-server b11010 (-t 4, mmap) | 32.6 / 35.2 / 38.0 (16.2–18.8 tok/s) | 7.45 / 8.62 / 9.97 | not measured (criterion: timings only) |
| bmoe `--moe-stream --cache-mb 1500` | 19.8 / 20.9 / 21.9 (~30 tok/s) | 7.53 / 8.81 / 10.43 | 9.98 / 10.23 / 10.32 GiB (max RSS 7.8–11.0 GiB) |
bmoe also: model load ~8 s, TTFT ~28 s, cache hit ~39 %, ~111 MiB read/token (item 00).

**Side question (item 00, `--chatml --no-think -p <probe-prompts/00-lan-exp-001.txt>`, -n 1, same knobs):** bmoe `n_prompt` = **612** vs jinja-rendered 616 → **not equal, −4 tokens** (the P0-style render is 4 tokens shorter than the `/apply-template` render; the probe text equals system + "\n\n" + user byte-for-byte).

**Verdict rule (quoted):** "PASS: (a) 10/10 equal AND (b) 10/10 identical. … NEEDS-L1: (a) 10/10 equal AND (b) identical on 7–9 of 10, every divergence starting at character index ≥ 25 % of the shorter text. … FAIL: anything else (any (a) mismatch, or (b) identical on ≤ 6 of 10, or an early divergence)."
→ (b) identical on 0 of 10 (≤ 6) and 5 early divergences → **FAIL**. Per the criterion: deep-tier llama-server numbers (deep35 0.596, DEEPROUTE) must not be quoted for a bmoe-based device plan until (c) is run or the fork is updated. Tokenization is identical (a), so the divergence is numeric (fork kernels / streaming path vs b11010), not prompt formatting.

**Stop-rule events:** none (watchdog every 5 s; watchdog never fired; at end free 33.4 GiB, swap used 4.19 GB < 8 GB; peak not logged). Never both engines resident. Docker untouched.
**Mini after (21:42):** free 33 GiB, swap used 3.8 GB / 5.1 GB total, load 3.0. GGUF **kept** (free ≥ 25 GiB), MODELS.md l.15 updated.
**Time:** 21:17–21:45 (~28 min wall; heavy run 835 s: server leg 7 min, bmoe leg 6 min, side 30 s). Budget 3 h.

Files: `items.csv`; `raw/` (488 KB: rendered prompts, server JSONs, bmoe stdout/CSV, stderr truncated to head 40 + tail 60, server.log, run.log, compare.out); `tools/run_deeppar.py`, `tools/compare.py` (mini copies in `<runner>/kiln/deeppar/`, full outputs in `<runner>/kiln/deeppar/out/`).
