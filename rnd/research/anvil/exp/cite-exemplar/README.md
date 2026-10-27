# exp cite-exemplar (Anvil, 2026-10-01)

Offline replay for card `../../cards/citation-exemplar-prompt.md`.

- `gate.mjs`: JS port of boar-app 0cfd4a77 `src/routing/citations.ts` + compact citation-gate branches of `answer.ts`.
- `run.mjs <A0|A1|A2> <temp> <seed> <out>`: replays Kiln exp-01 `capture/lantern52.jsonl` rows with sources (40) on `shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf` (node-llama-cpp from boar-app/node_modules, read-only).
- `runs/`: outputs; `*-raw|gated.precheck.json` = Lantern precheck v2.2 (`rnd/lantern/tools/precheck.py`).

Reproduce: `node run.mjs A0 0 42 runs/A0-t0.jsonl` then `python3 rnd/lantern/tools/precheck.py <file> --json <out>`.
