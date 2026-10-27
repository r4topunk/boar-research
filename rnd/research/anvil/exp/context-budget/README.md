# exp context-budget (Anvil, 2026-10-02 cycle 15)

k-sweep of answer-key coverage in the passages the engine's `WikiPack.searchDetailed` returns (engine copy @0cfd4a77, imported read-only from Sonar's `exp/11-passage-selection/src`), 52 keyed bench-v0.1 items, bge-small query vectors.
- `run-k.mts` = Sonar's `run-k.mts` (Wikivoyage + crypto packs) with an output-name fix and a passage-size print; `run-k-wikisample.mts` = the same on `boar-wiki-sample` (1 FineWiki shard, full articles).
- Run: `K=<k> node --experimental-transform-types run-k.mts`.
- Outputs: `rows-k<k>.json`, `rows-wikisample-k<k>.json`.
