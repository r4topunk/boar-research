# exp notes-first (Anvil, 2026-10-01 cycle 6)

Offline replay for card `../../cards/notes-first-capped-reasoning.md`.
- `run.mjs <N0|N1> <temp> <seed> <out>`: Kiln exp-01 `capture/lantern52.jsonl` rows with sources (40) on `shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf` via node-llama-cpp 3.21.1 (boar-app/node_modules, read-only), Metal on M1 Ultra.
- N1 inserts a capped "Notes:" instruction before `Context:`; only the text after `Answer:` is graded.
- Graded with `rnd/lantern/tools/precheck.py` (v2.2); outputs in `runs/`.
