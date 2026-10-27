# MINI-BASELINE (2026-10-21): same-host K1 baseline on the Mac mini (0 LLM, 0 Opus, 0 paid, 100 generations, 0 phone)

TL;DR: the mini does not reproduce the MacBook LITEPACKS K1 text (30/97 MAIN rows byte-identical), but **retrieval, kept sources and prompt tokens are identical on 100/100**.
Every future mini arm must be paired with a mini baseline, never the MacBook traces.

## What ran
- Unpatched tree `the mini:<runner>/kiln/be-0cfd4a77-cut7-litepacks` (ARM cut7-headpass-x2+litepacks, answer.ts 0d1ac07d, adapter-litedecline.ts d53c1487), APFS clone per job.
  Tree hash check: all 385 files of the MacBook tree (kiln-local/..., hash 33f3c7ee) are byte-identical on the mini; the mini has 7 extra unused files (be/adapter-quantlite.ts, be/vendor-protocol/*; mini hash 33244341).
- Requests: the MacBook LITEPACKS request files unchanged (runs/req/lp-K1-{cm,v01}-s42.requests.jsonl, runId lp-K1-*, 40 + 60 rows; MAIN 97 = cm 40 + 57 of the 60 v01 rows). Qwen3-1.7B Q4_K_M, K1 kit, seed 42, LITEDECLINE_OFF=5, --reasoning off.
- Host: mini M4, llama-server b11010 build-cpu (-t 4), the 2-slot guard (tools/mini_gen.sh.used = lp-screens/tools/mini_gen.sh), gen1 + gen2 in parallel, detector :8094 used not touched, disk 26 GiB before and after.
- Traces: `traces/mini/lp-K1-{cm,v01}-s42.mini.traces.jsonl` (844 KB total), sha256 in `traces/mini/SHA256SUMS`:
  cm e05a4b47fbce46b062fd2ee9853d47a0a56f82578e5addc31594e0d73ce464f0, v01 2abf0e4705e50027a931bcc2e8ee73088c6df342ed83d70e178de6da4336ea7d. Status logs in runs/mini/.
- Diff: `python3 -I tools/mini_vs_macbook.py --json runs/mini/mini_vs_macbook.json` (0 LLM; output runs/mini/mini_vs_macbook.txt).

## Identity, mini vs MacBook (per item)
| set | n | text byte-identical | first 32 words identical | kept sources | raw candidates | prompt tokens | route core (outcome, tier, declined, pre-generation codes) |
|---|---|---|---|---|---|---|---|
| MAIN 97 | 97 | 30 (31 %) | 42 (43 %) | 97 | 97 | 97 | 97 |
| cm | 40 | 9 (23 %) | 15 (38 %) | 40 | 40 | 40 | 40 |
| v01 | 60 | 24 (40 %) | 30 (50 %) | 60 | 60 | 60 | 60 |
- **Retrieval identity: 100/100** (kept, raw, dropped, answer.shown, promptTokens). No kept-source difference, so no retrieval finding.
- Full reasonCodes list is identical on only 75/100: the other 25 differ only in post-generation codes (citations:removed/added, verdict-guard, grounding:uncited/compact-decline-released), which follow the answer text.
- Reading: the text divergence is decoding (temperature 0.7, M4 vs M1 Pro CPU kernels) on identical contexts, so mini-vs-MacBook deltas are host noise of about 70 % of rows.
- Mini determinism: vs the older mini control (lp-screens/control lpctl-K1-main) 95/97 byte-identical; 2 rows differ (parallel load or a build detail), so a mini arm on an unchanged row will occasionally differ even with no change.
- Wall: job cm 207 s, v01 298 s (2 jobs in parallel, 100 items); sum of per-item totalMs mini 432 s vs MacBook 464 s; p50 per item ~5 s; 0 errors.

## How future screens must pair
1. Generate arm and baseline on the mini with the same tree, same request bytes (only runId and config.arm may change) and the same concurrency; judge both with the same judge run.
2. Baseline = these traces (identical requests) or lp-screens/control/traces/lpctl-K1-main-s42 (same system, 95/97 identical to these); never the MacBook LITEPACKS traces.
3. Rows whose arm text equals the mini baseline text are unchanged (reuse the judgment); 2/97 baseline-vs-baseline flips are the floor for "changed by noise".
4. Retrieval-only arms can still be checked with the 0-LLM replay on the MacBook, since kept sources and tokens match the mini exactly.

## CPU features, MacBook vs mini (web log 23.1a, 0 LLM, 2026-10-21)
Captured with `llama-server -lv 4 -m Qwen3-1.7B-Q4_K_M.gguf -t 4 -c 512 --port 18971` (free port, killed after load, no request served); same release b11010 (commit 4bc272f), both AppleClang 17 but different builds.
| | MacBook (M1 Pro, spikes/llama-b11010-cpu) | mini (M4, <runner>/spikes/llama-b11010/build-cpu) |
|---|---|---|
| system_info CPU | NEON, ARM_FMA, FP16_VA, DOTPROD, LLAMAFILE, ACCELERATE, REPACK (8 hw threads) | NEON, ARM_FMA, FP16_VA, **MATMUL_INT8 (I8MM)**, DOTPROD, **SME**, ACCELERATE, REPACK (10 hw threads); no LLAMAFILE flag |
| hw features (sysctl) | FEAT_I8MM 0, SME 0, BF16 0 | FEAT_I8MM 1, SME/SME2 1, BF16 1 |
| BLAS | Accelerate | Accelerate |
| KLEIDIAI / OpenMP / SVE | off (CMake KLEIDIAI OFF; OpenMP option ON but ENABLED=OFF on the mini, ggml uses its own pthread pool; SVE absent on both) | same |
| libggml-cpu sha256 | 04bbc13b... | 21bc8ad3... (GGML_NATIVE=ON, CPU_ALL_VARIANTS OFF: each host runs a kernel set compiled for its own core) |
- Differences that plausibly change float summation order: (1) I8MM (smmla) on the mini vs DOTPROD (sdot) on the MacBook for the Q4_K/Q8 dots and the REPACK interleaved layouts (different int32 partial-sum grouping, then scaled); (2) SME present on the mini (repack/gemm kernels may use it); (3) the Accelerate sgemm path (prompt batches of >= 32 tokens, AMX) differs per chip; (4) the LLAMAFILE sgemm is flagged only on the MacBook. OpenMP and KleidiAI are inert on both. These explain why mini vs MacBook text differs on ~70 % of rows with identical contexts (see above) and mean no cross-host bit-identity can be forced.
- Thread-count check (MacBook binary, greedy temp 0, seed 1, 96 tokens, top-2 token probs hashed): short prompts (< 32 tokens, no BLAS batch) are bit-identical for -t 1/4 and across repeats; a ~600-token prompt (BLAS prefill path) gives the same text but different probability digits for -t 1 / 4 / 8, and identical digits on repeat at the same -t. So `--threads 1` is not a universal bit-for-bit check; the usable determinism check is **same host, same binary, same -t** (repeat = bit-identical, tested 2x on the MacBook), and OMP_NUM_THREADS has no effect here (no OpenMP in the build). For a future 10-id replay: pin -t 4 on both runs of a pair and do not compare across hosts; a -t 1 pair is an optional tighter check on short-prompt rows only. The 10-id replay was not run.
