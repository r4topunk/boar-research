# exp persona-length (Anvil, 2026-10-02 cycle 7)

Offline replay for card `../../cards/complete-paragraph-persona.md`.
- `run.mjs <P0|P1|P2> <temp> <seed> <out>`: Kiln exp-01 `capture/lantern52.jsonl` rows with sources (40) on `shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf`, node-llama-cpp 3.21.1 (Metal, M1 Ultra), greedy, maxTokens 512.
- P0 = succinct (0cfd4a77 default), P1 = the app's "detailed" persona, P2 = new "complete paragraph" wording (in run.mjs).
- Graded with `rnd/lantern/tools/precheck.py` v2.2 (correctness and confident-wrong only; no judge, so no quality ratio).
