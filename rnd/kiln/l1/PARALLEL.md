# L1 parallel mode: measured, closed, N = 1 stays (Kiln, 2026-10-02)

TL;DR: **recommended N = 1.**
- Batching on one llama-server (`-np N`) cuts L1 wall time by only ~1.09× (N=2/3) to 1.17× (N=4) against the N=1 mean; N=1 itself varies ±3%.
- It changes the answer text on 67–88% of items at the same seed. Sources are identical; route codes differ on 4/24 items.
- The ceiling is low because L1 time is 65% prompt prefill, which is compute-bound. Batching only helps decode.
- The real levers are CPU contention on the mini and the thread count:
  - `smbd` uses ~5.5 cores and three headless Chromium processes ~2.5 more, continuously, on a 10-core machine.
  - The thread test below measures how much a higher thread count helps.

## What was built (boar-eval, uncommitted, for review)

| Piece | What |
|---|---|
| `run.sh --parallel N` | L1 only, needs `--backend server`. Without the flag the command is byte-for-byte the old one, so L2/L3 are unchanged |
| `runner/parallel.sh` | Starts one `llama-server -np N -c 4096·N` (4096 context per slot, `n_slots = N` verified in the server log) and N adapter shards, then merges the traces back into request order (`runner/merge-shards.mjs`) |
| `adapter.ts --shard i/N --server-url URL` | A shard runs requests k with k % N == i against the shared server. The server is guarded: `/props` must report this run's GGUF. Each shard gets its own app dir (no shared SQLite/symlink races). `--print-model` gives parallel.sh the GGUF path |
| Latency flagged invalid | With N > 1, every latency field (ttft, total, retrieval, prefill, decode tok/s, firstVisible, reasoning) is **null**. The raw values sit in one `other/timing-raw` event with `valid: false`. Each trace also carries warning `adapter:parallel-timing-invalid` and `versions.parallel` / `parallel.timing`. Token counts stay |
| Tests | `trace.test.ts` +2 (`parseShard`, `invalidateTiming`): desktop-node 30/30, `tsc` clean |

## Measurement

Slice retrieval-inkit (24 items), Android 12 GB profile, qwen3-4b-instruct-2507-q4km, engine 0cfd4a77 main, seed 42, llama-server b11010 (`4bc272f`), `-t 4`, temperature = the engine's default. Runs were back to back in one window (22:14–22:37), app dirs pre-warmed. Wall time = the heavy-lock job time (`ran=`). Identity is against N=1 (`par-compare.py`).

| Run | Wall (s) | Speedup vs N=1 | Load 1-min before | Identical answer text | Route identical | Sources identical (raw, kept, shown) | Errors |
|---|---|---|---|---|---|---|---|
| N=1 (`--parallel 1`) | 242 | 1.00 | 17.3 | reference | reference | reference | 0 |
| N=1 repeat | 227 | 1.07 | 21.7 | **24/24** | 24/24 | 24/24 | 0 |
| standard server path (no `--parallel`) | 228 | 1.06 | 21.1 | **24/24** | 24/24 | 24/24 | 0 |
| N=2 | 213 | 1.14 | 19.9 | 8/24 | 20/24 | 24/24 | 0 |
| N=3 | 214 | 1.13 | 21.7 | 6/24 | 20/24 | 24/24 | 0 |
| N=4 | 198 | 1.22 | 25.9 | 3/24 | 20/24 | 24/24 | 0 |

- **Wall-time noise:** the three N=1-equivalent runs span 227–242 s (~6%). Against their mean (232 s), N=2/3 are 1.09× and N=4 is 1.17×. Only N=4 is clearly above the noise, and it ran at the highest load.
- **Determinism and parity:** at N=1 the parallel path is deterministic and identical to the standard server path, so the shard/merge/external-server plumbing itself changes nothing.
- **Batching perturbs logits:**
  - From N=2, most texts diverge after a shared prefix (first differing character at 13–300; a few at 0).
  - Route codes differ on 4/24, which are post-generation codes such as citation checks; retrieval is untouched.
  - So an L1 read in parallel mode isn't comparable item by item with an N=1 base, and both sides would have to run at the same N.
  - Even then, sampling noise rises: a different N in the base and the arm is a confound.
- **Why the speedup is small:**
  - At N=1 the summed item time is 234 s: prefill 151 s (65%), decode ~78 s, retrieval 5 s.
  - That's 11,098 prompt tokens at ~73 tok/s.
  - Continuous batching shares decode steps but not prefill compute, so the bound is about 1/(0.65 + 0.35/N): 1.37× at N=4. Measured: 1.22×.
- **Memory** was fine (one model copy); the cost is answer identity, not RAM.

## Recommendation

1. **N = 1 for L1** (and L2/L3 as today). Keep `--parallel` in the code only if the coordinator wants it for throughput-only jobs where identity doesn't matter (e.g. generating candidate pools). Otherwise drop it before the commit.
2. **Free the mini's CPU first.** `smbd` (file sharing) has used ~550% CPU for days, and 3 headless Chromium processes (Playwright, up 6 days) ~85% each. Neither is Kiln's, so this needs r4to. Prefill is compute-bound, so this is likely the largest L1 speedup available.
3. **Thread count:** see the next section.

## Thread count (node backend, the L1/L2 default)

Not run: the front was closed by the coordinator (2026-10-02 ~22:50, N = 1 stays) before the test reached the queue. The script is kept (`thread-bench.sh`) if the question reopens.

## Decision (coordinator, 2026-10-02 ~22:50)

- **Closed: N = 1 stays** for L1/L2/L3. The `--parallel` code is uncommitted in boar-eval, for the coordinator's review.
- **CPU hogs** identified by the coordinator: r4to's other project (idledex: two `node run.js` runners with headless Chromium, up ~6–7 days) plus `smbd`. r4to has been asked; Kiln does not touch them.
- **Until that is resolved, every L1/L2 latency field from the mini is invalid**; quality numbers are fine.

## Files

- Runs: `boar-eval/runs/kiln/l1/par-{smoke,warm,n1,n1rep,std,n2,n3,n4}-retrieval-inkit-s42/`
- Scripts: `rnd/kiln/l1/par-bench.sh`, `par-bench.times.tsv`, `par-compare.py`, `thread-bench.sh`
