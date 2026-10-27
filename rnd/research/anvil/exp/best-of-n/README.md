# exp best-of-n (Anvil, 2026-10-02 evening; new-direction cycle 1)

- `run.mjs N out`: Kiln exp-01 `capture/lantern52.jsonl` (40 prompts with sources), Qwen3-4B-Instruct-2507 Q4_K_M (node-llama-cpp, Metal), N samples per item at temp 0.7 / top_k 40 / top_p 0.95 / min_p 0.05, seeds 1..N.
- `bon_select.py runs/q4b-n4.jsonl`: selectors s1 (first sample), medoid (MBR by content-word Jaccard), support (key-term overlap with the prompt's sources), oracle (best by precheck; upper bound); grades every selection with `rnd/lantern/tools/precheck.py` v2.2.
- Companion: `../batched-decode/bench.mjs` (CPU-only decode throughput with 1/2/4 parallel sequences).
