# DEEPCOV-FB step 0: enwiki top-100k as an R2-only fallback, 0-call retrieval replay on bench v0.1 (60 items, public dev)

TL;DR: **gate FAILS, lever closed at step 0.** In the deep tier, the curated kit leaves the engine with no kept source (R2) on 13 of 46 retrieving items, and 9 of those have gold. Admitting the enwiki pack only on those items puts a gold source into the engine's kept sources on **1 item** (lan-exp-003) and empties 0. The gate needs at least 5. Even the uncapped "fallback-raw" variant, which skips onSubject, compressContext and the 400-token cap, reaches only 3. As a peer (the DEEPWIKI configuration), the pack adds gold on 7 items but removes it on 2, empties 1 item, and takes 70 of 113 kept slots.

## Setup
- Tree `wt/cut7` (6d0b93b1). Deep tier = the same wiring as `arms/deeprerank/tools/rerank-replay.ts`: 4B with roles ["fast"] plus a deep model `qwen3.6-35b-a3b-ud-q2kxl` with roles ["reasoning"], settings `{quickFirst: true, alwaysComplete: true, deepModelId}`. planAnswer takes its deep branch (k = 6, DEEP_CONTEXT_TOKENS 400). Generation is stubbed.
  - Gate `rules` (the deep runs' server backend has no gate). Detector: lexical predicate.
- Tool: `tools/replay-deep.ts`, a copy of `boar-eval/adapters/desktop-node/tools/replay-retrieval.ts` with only lines marked DEEPCOVFB changed. Those lines add `--deep`, `--pool 20` (an extra `retrieve(q,20)` that is recorded but never returned to the engine), and per item `kept` ({title, section, source} of the sources event) and `codes` (the receipt reasonCodes). boar-eval is unmodified.
- Fidelity: base raw recall@6 is 0.2564 over 39 gold items, equal to DEEPRERANK's k = 6 baseline. The engine asked for k = 6 on 46/46 retrieving items, and the cache key cb2f82a5073cde89 is the same.
- Packs: base = `boar-crypto` + `boar-wikivoyage-en` (+ essential seed corpus). Peer = base + `boar-wiki-en-top100k.sqlite`.
  - That pack is 2,542,215,168 bytes. **sha256 9123b3720abd847291e2502d7529419ca86c1fc4cf111e9b449a2be06fc694e7 = manifest `sha256`** (verified).
- Pack attribution: a kept or raw chunk counts as the new pack's if its source is labelled "Wikipedia" and its title is not an article of the curated crypto pack (the crypto pack also ships Wikipedia articles).

## R2 (baseline: retrieving item, empty pre-answer `sources`): 13 / 46
| reason (engine reasonCode) | items |
|---|---|
| `grounding:no-good-source` (onSubject dropped all) | vit-hum-001, vit-hum-006, lan-hlt-001, lan-hlt-002, lan-ref-003, lan-exp-003, lan-rsn-005 |
| `grounding:health-no-source` (health-strict topic filter) | vit-hlt-001, vit-hlt-002 |
| empty raw (`context:0->0`, retrieve returned nothing) | vit-hum-002, vit-hum-003, vit-sci-001, lan-rsn-004 |

Gold exists on 9 of the 13 R2 items, so the fallback ceiling on v0.1 is 9.

## Metrics (39 gold items; non-retrieving items count as 0; slot counts over the 46 retrieving items)
| arm | recall@kept | items with gold in kept | gold ENTERS vs base | gold LEAVES | empty kept | emptied vs base | pack slots / kept slots | items with a pack chunk |
|---|---|---|---|---|---|---|---|---|
| base (curated kit) | 0.205 | 8 | — | — | 13 | — | 0 / 90 | 0 |
| peer (DEEPWIKI config) | 0.308 | 13 | 7: vit-hum-004, lan-cmp-002, vit-cry-011, lan-exp-003, lan-exp-004, lan-cmp-005, lan-rsn-006 | 2: lan-exp-002, vit-trv-003 | 7 | 1: vit-sci-002 | 70 / 113 (62 %) | 30 |
| **fallback** (base, else peer kept[:8]) | 0.231 | 9 | **1: lan-exp-003** | 0 | 6 | **0** | 17 / 107 | 7 |
| fallback-raw (base, else pack chunks of peer top-20 pool, top 8) | 0.269 | 11 | 3: lan-rsn-004, lan-exp-003, lan-rsn-005 | 0 | 1 | 0 | 78 / 168 | 12 |
| fallback-raw6 (same, from peer raw top-6) | 0.269 | 11 | 3 (same) | 0 | 1 | 0 | 62 / 152 | 12 |

- Raw recall@6 (scorer's recall@k): base 0.256 vs peer 0.385.
- Latency of the engine's `retrieve(q,6)`: p50 115 ms (base) vs 250 ms (peer); p90 169 vs 381 ms. The MacBook was shared with the :8094 detector.
  - A fallback adds the peer cost only on R2 items: a second retrieve over the pack, at the same order as the peer p50.

## Gate verdict
Rule: gold enters the kept set on ≥ 5 items and 0 items are emptied.
- **fallback: 1 enters / 0 emptied → FAIL.**
- fallback-raw: 3 / 0 → also FAIL, and it bypasses the grounding gates, so it is not a shippable path anyway.
- Of the 13 R2 items, the fallback keeps a pack chunk on 7 (6 stay empty). Of the 9 R2 items with gold, gold enters on 1, and on 3 with the uncapped pool. Why the other 6 miss was not examined (no item text read).
- The peer gains (+7) sit on items where the curated kit already kept something. A fallback keyed on R2 cannot reach them by construction.
- No judged arm. Lever closed at step 0 on v0.1.

## Caveats
- "Kept" = the engine's pre-answer `sources` event as the replay reproduces it: compressContext under the deep 400-work budget, then onSubject or health-strict grounding. A fallback inside the engine would re-run that path; the "fallback" arm approximates it with the peer run's kept list, which is identical on R2 items because base kept nothing there. Slot cap 8 never binds (kept ≤ 6).
- Lexical detector only (the deep runs used detector v3b). Gate `rules`. Title-level gold (scorers/retrieval.py rule) on 39/60 items. v0.1 is small dev data.
- v0.2 has no gold sources, so this gate is v0.1-only.
- Pack attribution is title-based: a title that is in both the crypto pack and enwiki counts as curated.

## Files and commands (repo root)
```sh
rnd/research/coordinator/arms/deepcovfb/tools/run-replays.sh      # both replays (BOAR_REPLAY_CACHE=arms/deepcovfb/cache), ~1.5 min
python3 -I rnd/research/coordinator/arms/deepcovfb/tools/fallback.py   # recombination + metrics -> aggregates/replay-v01.json
```
`replay-base.jsonl`, `replay-peer.jsonl` (titles, sections, sources, codes, top-20 pool; no item text), `aggregates/replay-v01.json`, `tools/{replay-deep.ts,replay-deep.sh,run-replays.sh,fallback.py}`, `logs/` (stderr, `pack.sha256`), `cache/` (50 MB app dirs).

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate was pre-stated in HANDOFF-2026-10-11.md:60-61 — nothing to freeze (a sha now would fake a pre-registration).
