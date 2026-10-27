# QWRITE step 0: a 4B-written search query does not put the fact chunk into raw top-8 more often (69 -> 67, gate +15): FAIL, row 11 closes (2026-10-16 14:2x; 0 judge, 0 paid)

**Verdict: step 0 FAIL.** With Qwen3-4B-Instruct writing a 3-8 word query in place of the engine's own search query, the fact chunk is in raw top-8 on 67/180 vs 69 (net -2; gate >= +15). It is gained on 18 items and lost on 20 (rule <= 5). The writer reshuffles retrieval; it adds no reach. The judged stage (random20, Haiku 40) is not eligible.

## Frozen inputs
- Criterion QWRITE-criterion.md sha 80695f6a... (Ruleset 30), frozen 14:08 before any generation or replay.
- Writer: Qwen3-4B-Instruct-2507-Q4_K_M, llama-server b11010 CPU build, MacBook, :8097, seed 42, temperature 0, max 24 tokens. Prompt: "Rewrite as a 3-8 word search query naming the entity and the fact asked. Output only the query." followed by the question.
- Replay: tools/replay-qw.ts, a copy of h8st replay-h8.ts plus --qmap; mode qw replaces only the query of the first retrieve() call (and the pool-8 call). Tree kiln-local/be-0cfd4a77-cut7-tk2off with the published packs (claim kit + the item's pack), --gate search --k 6 --pool 8. Modes off,qw,off. Reach definitions from compare_h8.py.

## Generation (tools/gen_qw.py, run_gen.sh)
- 180 queries in 116 s wall, p50 0.62 s per item, p50 7 words.
- Gate: 177 pass, 3 fall back to the engine query. bitcoin-017 leaks "prune=1", bitcoin-018 leaks "BIP44", firstaid-005 is over 12 words. Kill threshold was 18.
- factbook-018: the engine makes no retrieve call in either mode, so the qmap is unused there (176 lines use it).

## Reach on the 180 (aggregates/compare.json)
| cell | chunk raw6 | chunk top-8 | chunk kept | article raw6 | article kept | empty kept | kept slots |
|---|---|---|---|---|---|---|---|
| OFF (engine query) | 55 | **69** | 35 | 93 | 61 | 42 | 285 |
| QW (4B query) | 47 | **67** | 33 | 86 | 58 | 47 | 274 |
| SE 100 OFF -> QW | 24 -> 17 | 31 -> 31 | 10 -> 9 | 54 -> 45 | 30 -> 26 | 29 -> 33 | - |
| topic 80 OFF -> QW | 31 -> 30 | 38 -> 36 | 25 -> 24 | 39 -> 41 | 31 -> 32 | 13 -> 14 | - |

Per pack, top-8 OFF -> QW: travel 8->7, ethereum 5->4, bitcoin 3->3, health-se 5->8, outdoors 10->9, firstaid 1->2, medlineplus 15->12, factbook 6->6, simplewiki 16->16.
- Top-8: gained 18, lost 20. Kept: gained 9, lost 11. Raw list unchanged on 23/180 items, kept list unchanged on 60/180.
- G0 identity: OFF vs the repeat OFF is byte-identical on 180/180, and OFF top-8 is 69, the H8-ST OFF count. PASS.

## Reading
- The short query loses the question's own content words. The engine's BM25 over the full question already matches these pack chunks. Raw-6 fact hits fall 55 -> 47, mostly on SE packs (24 -> 17); consistent with the long question sharing more terms with the SE answer chunk than a 7-word query does.
- Gains appear where the question is conversational: health-se +3 ("120 over 80" -> blood pressure; "snakebite snake bite" -> first aid steps).
- Union bound: OFF or QW top-8 = 87/180. A two-query pool (engine query + 4B query, merged) would bound at +18 top-8. That is a new arm (two retrieves plus a merge rule), not this one. It is listed in the CLOSED row as the only reopen.
- The prior holds: small-model query rewriting is about neutral here (query2doc/HyDE; DEEPITER 35B NO).

## Files
QWRITE-criterion.md + .sha256; tools/{gen_qw.py, run_gen.sh, replay-qw.ts, replay-qw.sh, run_replay.sh, compare_qw.py}; runs/{qw-raw.jsonl, qmap.json, st-*.qw.jsonl, changed.jsonl, server.log}; aggregates/compare.json.
Cost: 0 judge, 0 paid, about 3 min of compute (generation 2 min, replay 72 s). The writer server was stopped. The :8094 detector was untouched. Nothing was read from blind/ or rnd/veil/.
