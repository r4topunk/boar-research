# NOTES35: a pack of 35B-written encyclopedic notes for the 4B — NO at step 0 (gate A failed; criterion NOTES35-criterion.md sha ae4a50be…; 2026-10-11)

TL;DR: 300 notes (first 300 titles of the breadth-first Vital-Articles-Level-3 order, 11 sections × 27–28) written by Qwen3.6-35B on the mini (thinking off; 287 words median, 37.5 s/note, 3.1 h) and packed as a format-2 kit pack (300 articles, 765 chunks, 1.28 MB, sha 232ce924…). Replay of the 4B cut 7 retrieval on the 110 v0.2 ids with the curated kit + notes: a note chunk reaches the engine's **kept sources on 3/110 items (2.7 %)** and the raw candidates on 10/110 (9.1 %); control without the pack 0/0. **Gate A (≥ 5 % kept, ≥ 15 % raw) failed** → NO at step 0: breadth-first general-knowledge notes do not reach the 4B's context on bounty-style questions; a linear extrapolation to 1,002 notes gives ≈ 9 % kept / 30 % raw, still under the 15 % kept bar, and the curated chunks keep winning the slots when a note is retrieved (10 raw → 3 kept). No judge call made. The 4B side stays closed.

| | notes300 + curated kit | curated kit only |
|---|---|---|
| items (110) retrieving | 89 | 89 |
| items with a note in raw candidates | 10 (9.1 %) | 0 |
| items with a note in kept sources | 3 (2.7 %) | 0 |
| note chunks in raw / all raw chunks | 14 / 297 | 0 / 284 |

Method: `tools/topics.mjs` (Vital Level 3, revid 1379525978, 1,002 titles, sha 6e36bbfe…; order 7a617aa7…), `tools/gen_notes_mini.sh 300` on the mini (llama-server b11010, 35B UD-Q2_K_XL sha-checked, :8097, temp 0.3, max 450 tokens; STATUS DONE; notes sha 616088eb…), `tools/build_notes_pack.mjs` (cut 7's build-wiki-pack.mjs, format 2, source 0; manifest `run-a/pack-manifest-n300.json`), `replay-retrieval.sh --tree wt/cut7` with/without the pack on the 110 ids (outputs under `blind/bench-v02/runs-notes35/`, query text never copied into rnd), `tools/hitrate.py` (notes identified by their notes35.boar.invalid URL). Aggregates: `run-a/hitrate-v02-n300.json`.

Caveats: 4B retrieval settings in the replay (k 4, gate "search", lexical detector); notes stored as "Wikipedia" source (a shipping version needs a source label); the 300-note pack's term statistics differ from a 1,000-note pack, but the kept-slot competition is the binding constraint, not recall. What would reopen it: question-shaped notes (topics derived from a question distribution that is NOT a bench set, e.g. the public v0.1 taxonomy) — a different mechanism, not in HANDOFF §2.

Cost: 0 judge calls; mini 3.1 h generation; MacBook 2 min replay. Exposure: retrieval-only replay over the 110 v0.2 ids (script-only; ids + titles read by the coordinator's scripts).
