# VITALPACK-ADD engine patch (wt/vitaladd = 6d0b93b1 cut 7 + uncommitted diff; 2026-10-11)
Patch `vitaladd.vs-cut7.patch` (sha256 78b94478dd65452a097b7719eb8269c1b0603386ddb8fa185d3c2e89a15ac37b; 5 files, +75/-14). Default OFF: nothing changes unless `settings.addPack` is set.
- `src/models/settings.ts`: `AnswerSettings.addPack?: {id, k, pool?}` (eval-only; the app never sets it).
- `src/rag/packs.ts`: `PackFilter {only?, exclude?, source?}` by pack id (a `local-<name>` file also answers to `<name>`), honoured by `searchPacks`/`searchWikiPacks`; `source: true` carries a format-1 pack's `source` column to the chunk (only on the add call; curated chunks keep `source` null as before).
- `src/rag/retrieve.ts`: optional `opts.packs` passed through both searches; `only` skips the built-in knowledge base.
- `src/routing/answer.ts`: `deps.retrieve(q, k, opts?)`. Deep branch only (genTier deep, not multipass, no reused sources): the curated call excludes the pack; after onSubject / health-strict grounding a second call `retrieve(q, pool, {only:[id]})` runs; candidates are compressed on their own budget (ADD_PACK_TOKENS 150 each, so the 400-token deep cap of the curated set is untouched), filtered by the SAME grounding (onSubject, or onHealthTopic on health), and the first k are appended. reasonCodes `addpack:kept-N` / `addpack:none` / `addpack:dropped-N`. `src/routing/answerService.ts` forwards opts.
- Enable in requests: `config.settings.addPack = {"id": "wiki-vital5", "k": 1, "pool": 6}` with `wiki-vital5` (sha d3b87d56…) in `config.kit`. **Caveat: boar-eval adapter.ts l.767 wraps `retrieve: (q, k) => Rt.retrieve(q, k)` and drops opts; it must forward the third argument (`(q, k, o) => Rt.retrieve(q, k, o)`) before any generation run, or the pack silently acts as a plain peer.**
- Enable in the replay: `tools/replay-add.sh … --add-pack wiki-vital5:1[:6]` (copy of deepcovfb/tools/replay-deep.ts, lines marked VITALADD; records the add call as `add`/`addMs`).

## Fidelity, bench v0.1 (60 public items, 46 retrieving; `tools/addcmp.py`, `aggregates/replay-add-*.json`)
| config | kept' = simulation (q = 1) | pack share of kept slots | items with pack chunk | gold enters / leaves | empty kept (base 13) | retrieve p50 ms curated + add = total (base 114.7) |
|---|---|---|---|---|---|---|
| default off, no vital pack | kept, raw, codes identical **60/60** (`replay-off-v01.jsonl`) | 0 | 0 | — | 13 | — |
| `wiki-vital5:1` (pool = k = 1, literal spec) | **52/60** | 0.191 (21/110) | 20 | 7 / 0 (sim 6) | 9 | 132.6 + 57.8 = 193.9 |
| `wiki-vital5:1:6` (pool 6, **recommended**) | **57/60** | 0.205 (23/112) | 22 | **6 / 0 = sim's 6 ids exactly** | 8 | 124.0 + 49.2 = 183.4 |
- pool 1 diffs (8): 4 a different pack chunk (retrieval top-1 vs the simulation's compression-ranked first: vit-hum-005, lan-cmp-002, lan-ref-002, lan-exp-007); 2 top-1 dropped by grounding where the sim kept a lower one (vit-sci-002, lan-rsn-005; vit-sci-002 loses its gold); 2 below.
- pool 6 diffs (3): vit-hlt-003 and dng-002 get a pack chunk the simulation cannot have (the peer run's compression/top-6 crowded it out: the additive path is what the sim approximates); lan-ref-002 compression ranks "American Civil War" over the sim's "Civil war".
- Caveats: one MacBook run each (ms noisy); dng-002 is a health item: the added Hypothermia chunk passed the health-strict filter, nothing bypassed. Not run on V-para / v0.2 (blind). Nothing committed in boar-app or wt/.
