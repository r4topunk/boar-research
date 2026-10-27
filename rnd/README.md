# boar-rnd (private)

R&D workspace for BOAR's offline research app (poidh bounty #31): decision queue, researcher cards and radars,
Summit memos, Kiln/Plumb/Lantern experiment notes, and Veil's blind sets.

- `research/QUEUE.md` — single test queue with every verdict (start here).
- `research/{sonar,anvil,compass}/` — researcher cards, radars, experiments.
- `research/summit/` — high-level strategy memos.
- `veil/` — frozen blind sets (sha256 manifests). Researchers do not read `veil/` (blindness rule).
- The harness and benchmark live in the separate private repo `BENCH_REPO_LINK`.

Large or regenerable artifacts (GGUF models, SQLite packs/vectors) are not versioned.
