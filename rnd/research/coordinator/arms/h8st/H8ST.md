# H8-ST step 0 — contextual chunk headers in the lexical index (2026-10-13 23:25; criterion H8ST-criterion.md sha 3765405d…; opus/high runner, text saved by the coordinator; a parallel session)

**Verdict: FAIL at step 0 — H8 (a) "contextual chunk headers" closes.** The published packs ALREADY index title and section path on every chunk: the FTS table is `fts(title, section, body)` (builder wt/packs/scripts/build-wiki-pack.mjs:245, :266-278 = boar-app/scripts/build-wiki-pack.mjs:227, :248-262 — the full heading path "A > B" on every chunk), and the engine queries `bm25(fts, 2, 1, 1)` over all columns (title weight 2, section 1; wikiPack.ts:421, :668). Title filled on 100 % of rows across the 11 packs; section on most (medlineplus 0 %: no headings). So X as specified would reproduce the existing index; the agent measured the only missing part, X2's **article first sentence** as a fourth column (`fts_h8(title, section, body, lead)`, lead weight 1, fixed before any run; title/section/body rebuilt exactly as the builder — token counts match on 1,633,374 / 1,633,374 rows; term choice and idf from the original index). 0 LLM, 0 judge, 0 paid.

## Stage 0 — OFF byte-identical
h8 tree with the setting off on the pack copies = the tk2off reference on the published packs: raw list, kept list, prompt sha, task, query, k identical on 180/180 self-test and 60/60 v0.1; off→off repeat identical. The fresh OFF reproduces TK2-REPLAY's OFF numbers (55 / 35 / 61 / 42).

## Reach (OFF → lead index)
| set | chunk in raw6 | chunk in top-8 | chunk kept | article kept | empty-kept | kept same / raw same as OFF |
|---|---|---|---|---|---|---|
| **180 pooled** | 55 → 58 | 69 → 75 | 35 → 37 | 61 → 64 | 42 → 41 | 132 / 66 |
| SE (100) | 24 → 28 | 31 → 36 | 10 → 12 | 30 → 31 | 29 → 28 | 72 / 30 |
| topic (80) | 31 → 30 | 38 → 39 | 25 → 25 | 31 → 33 | 13 → 13 | 60 / 36 |
| travel / ethereum / bitcoin / health / outdoors | 8→6 / 3→5 / 1→4 / 4→5 / 8→8 | 8→7 / 5→8 / 3→5 / 5→5 / 10→11 | 1→1 / 2→2 / 1→3 / 1→1 / 5→5 | 6→6 / 7→6 / 2→5 / 5→4 / 10→10 | 6→6 / 4→3 / 2→2 / 10→10 / 7→7 | — |
| firstaid / medlineplus / factbook / simplewiki | 1→0 / 13→14 / 4→4 / 13→12 | 1→0 / 15→15 / 6→7 / 16→17 | 1→0 / 10→11 / 3→4 / 11→10 | 3→2 / 11→11 / 5→7 / 12→13 | 5→5 / 4→4 / 1→1 / 3→3 | — |
| v0.1 (60, kit only) | gold in raw6 9 → 9 | — | gold kept 8 → **7** | — | 10 → 10 | 54 / 38 |

Raw has k ≤ 6, so "raw top-6" = the whole raw list; "top-8" = an extra retrieve(query, 8) pool the engine never sees. **G1 FAIL** (top-8 75 < 90; kept +2 < +15). **G2 FAIL** (v0.1 gold-kept 8 → 7: lan-exp-004 kept [Kyoto, Kyoto/Higashiyama] → [Kyoto (prefecture)]; empty-kept flat; kit lost-context 0). Not PARTIAL: the small gain is on SE packs, the opposite of the declared split (topic raw6 31 → 30). **G3 PASS**: retrieval p50 167.6 → 151.6 ms on the 180, 121.2 → 110.7 ms v0.1 (warm-cache order, not a speed-up); index growth if a lead column were added to the real packs +2.7 % (medlineplus) … +11.5 % (crypto), all < 25 % (the prototype copies are +50–75 % because they hold a full second index).

## Item changes and why
Newly in raw6: ethereum-008/009, bitcoin-008/011/019, health-se-017, medlineplus-019, factbook-017; newly kept: bitcoin-011/019, medlineplus-019, factbook-017; top-8 only: ethereum-019, bitcoin-002, outdoors-017, factbook-001, simplewiki-008. Lost: travel-010/012 (raw6), firstaid-007 (raw became empty), factbook-016 (raw6), simplewiki-007 (raw6 and kept). Helped: "Do faucets actually work?" (bitcoin-019) — the first sentence + tags carry the asker's wording the short title lacks. Neutral/harmful: "Lindisfarne" (simplewiki-007) — the same first sentence is stamped on every chunk of an article, lifting sibling/neighbour articles as much as the fact section; it does not pick the right section. Harmful: "Outdoor Survival/Water" (firstaid-007) — raw went from one hit to empty (unchecked guess: term counts / pool shift under the relevance gate).

## Reading
The lexical index already carries the "contextual header"; the lever H8 (a) assumed does not exist in this engine. What ORACLE-ST's +0.095 headroom needs is a different candidate set for the 137 unreached items — question-shaped text per chunk (doc2query, ≈ 14 h of 4B generation per 55k chunks on the mini) or a dense sidecar that does not displace (R46: +0.017, not decided) — and a keep step that lets the chunk through (R47 ceiling 54). **Per the criterion, (b) doc2query becomes the H8-ST step 0** (mini time, after SFT4B stage 1). Untested variants (unlikely to pass given 75 vs 90 and +2 vs +15): lead weight 2; lead in the section column; X as one merged column (same terms, different weighting/length normalisation).

## Files
tools/{build_h8.mjs, build_all.sh, replay-h8.ts, replay-h8.sh, run_h8.sh, compare_h8.py}; runs/{st-<pack>.{ref,h8}.jsonl ×18, v01-kit.{ref,h8}.jsonl, stage0.{ref,h8}.jsonl, newly.jsonl}; aggregates/compare.json; logs/ (build, run, compare, index-sizes.txt, h8proto.sha256 = h8proto.after.sha256, published-src.sha256 11/11 OK); h8st.vs-cut7.patch + .sha256 (d53d8b62…; 40 lines; setting `BOAR_H8_INDEX=lead`, inert when unset or table missing); engine tree kiln-local/be-0cfd4a77-cut7-h8. Pack copies shared-data/packs/h8proto/ (11, 2.0 GB) deleted after the verdict (class B, rebuildable with tools/build_all.sh; DISK-LOG). Public items only → no EXPOSURES row.
