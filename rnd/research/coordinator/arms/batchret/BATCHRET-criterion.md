# BATCHRET criterion (frozen 2026-10-20, before any engine change)

Arm: batch or cache the format-2 pack (wikiPack.ts) SQL lookups so retrieval returns byte-identical results with far fewer SQL round trips. Motivation: LITELAT (arms/litelat/LITELAT.md): on a Pixel 8a about 435 serial one-row SQL calls per question (7-9 ms each, 3.65 s summed) are most of the 5.3 s retrieval inside the 1.7B's 9.4 s TTFT.

Base: wt/pr1 at b546706c (branch pr/cut7-engine, the PR UPSTREAM_REPO/boar-app#85 engine = cut 7 engine). Candidate: branch `batchret` in wt/batchret, off b546706c; the only engine source change is src/rag/wikiPack.ts (+ its tests). 0 LLM calls, 0 judge calls, 0 paid. MacBook (desktop node:sqlite).

## Harness (fixed before the change)
- tools/parity-replay.ts: copy of boar-eval/adapters/desktop-node/tools/replay-retrieval.ts (the engine's own createAnswerer().answer() with a stubbed LLM, so query rewrite, k and skip rules are the engine's), plus: a per-statement SQL log (tools/expo-sqlite-log.mjs, a copy of the adapter's expo-sqlite shim), every retrieve() call reported with its full chunks (all fields, text included) and sha256, receipt reasonCodes and the full `sources` event.
- tools/run_parity.sh <tag> <tree> <pass>: `--gate search`, no detector, default k.
- tools/compare_parity.py <base dir> <new dir>.

## Sets (public dev only; never blind/, never bench/v0.4)
| set | items | packs |
|---|---|---|
| v01 | bench/v0.1/questions.public.jsonl, 60 (venue items included) | claim kit: boar-crypto + boar-wikivoyage-en |
| st180 | the 9 pack self-tests x 20 (qa-travel-se, qa-ethereum-se, qa-bitcoin-se, qa-health-se, qa-outdoors-se, boar-firstaid-en, boar-medlineplus-en, boar-factbook, boar-simplewiki-en) | kit + the item's pack (as HEADPASS-X2 identity) |
| cw150 | bench/slices/chainwhen-v1/questions.jsonl, 150 | kit + the item's selftest.pack |

Total 390 item replays per tree.

## Rule
Run order: base pass 1, candidate pass 1, base pass 2, candidate pass 2 (same session, same machine).

PASS iff all of:
- (a) Parity: on every one of the 390 items, candidate pass 1 equals base pass 1 on every field except timing and SQL counts (task, tier, query, k, raw titles/sections/sources/similarity/via, sources, reasonCodes, the full sources event, and for each retrieve() call its query, k and full chunk objects incl. text, score, similarity, action, ordering). Base pass 1 vs base pass 2 must also be identical on all 390 (else the harness is not deterministic and the arm is INVALID, not PASS).
- (b) The full engine test suite (`npx vitest run` in the candidate tree) passes, and `tsc --noEmit` reports no new error versus the base tree.
- (c) SQL calls per retrieve() call (all databases, mean over the pooled retrieve calls of the 390 items, pass 1) drop by >= 80 % versus base; and desktop retrieve() wall time p50 over the pooled retrieve calls of pass 2 is lower for the candidate than for the base. Numbers are reported per set, with p90 and per statement kind.

Otherwise FAIL. Phone timing is out of scope (coordinator, later); the report gives a projection from LITELAT's per-call cost only, labelled as a projection.
