# PK-4 PACK-PRUNE (2026-10-21): KILL. Under A-union on the desktop replay, every one of the 6 packs reaches the kept context on 18 or more dev items. medlineplus is not inert there: 26 items, and the fact chunk on 2 real health items. Prune nothing. The phone's "medlineplus 0" is an engine-path gap.

TL;DR (criterion `PK34-criterion.md`, sha 0f78d13f..., commit 438d315a, frozen before the replay; 0 LLM, 0 generation, 0 judge, 0 paid)
- **Replay setup.**
  - Funnel tree (FACTPRESENT tree + apply_funnel.py) with the A-union KA requests (coverage-matrix req), 280 items.
  - Stub llama-server on the MacBook, visa from wave4.
  - Parity vs the judged KA traces: kept titles 177/177 identical.
- **Kept-chunk contribution per pack.** Dev = v0.1 57 + MAIN-cm 40 + the 180 self-tests minus the pack's own items.

  | pack | dev n | items w/ raw hit | items w/ kept chunk (v0.1 / cm / self-tests) | kept chunks | fact chunk kept (real) | Pixel SQL s per question |
  |---|---|---|---|---|---|---|
  | firstaid | 257 | 38 | **108** (25 / 14 / 69) | 228 | 1 | 0.172 |
  | wikivoyage | 277 | 137 | **68** (22 / 2 / 44) | 122 | 0 | 0.246 |
  | factbook | 257 | 12 | **36** (16 / 1 / 19) | 64 | 4 | 0.166 |
  | crypto | 277 | 52 | **33** (10 / 0 / 23) | 67 | 4 | 0.226 |
  | medlineplus | 257 | 25 | **26** (6 / 2 / 18) | 51 | 2 (lan-hlt-002, vit-hlt-003) | 0.151 |
  | visa | 277 | 25 | **18** (2 / 3 / 13) | 37 | 0 (no visa gold exists) | 0.147 |

- **Verdict: KILL.** Every pack has kept chunks on >= 3 dev items, and no pack has <= 2, so there is no candidate. The default set stays at 6, and the cost question moves to PK-5 (merged pack / parallel search).
- **Post-hoc, not in the verdict.** Replay KA minus each of the two suspects:
  - minus medlineplus: Context bytes change on **42/280 (15.0 %)**;
  - minus visa: Context bytes change on **18/280 (6.4 %)**.
  - Both are far above the 2 % byte-identity bar, so neither pack can be dropped without changing what the model reads.
- **medlineplus probe ("no content" vs "outranked").**
  - It holds the real fact for lan-hlt-002: gold chunk 1520 is at bm25 rank 3 in its own list, and it is kept. Same for vit-hlt-003: chunk 796, rank 1, kept.
  - On its own 20 self-tests it keeps a chunk on 14 and the fact chunk on 14.
  - Most of its desktop reach comes through the two-stage dense candidates: 157 items have medlineplus dense candidates vs 25 with a raw lexical hit, and 18 of its 26 kept items also have a raw hit.
  - So on the desktop it has content and wins slots.
- **Why the phone shows medlineplus 0 (and factbook 2, firstaid 7). Same 57 v0.1 items:**

  | | desktop KA | phone aunion73-a |
  |---|---|---|
  | items that retrieve | 46 | 32 |
  | factbook kept / hit | 16 (4 via a raw hit) | 2 |
  | firstaid kept / hit | 25 (4 via raw) | 7 |
  | medlineplus kept / hit | 6 (4 via raw) | 0 |
  | visa kept / hit | 2 | 0 |
  | crypto kept / hit | 10 | 10 |
  | wikivoyage kept / hit | 22 | 26 |

  - On the phone, lan-hlt-001, lan-hlt-002, vit-hlt-001 and vit-hlt-002 ran no retrieval at all. vit-hlt-003 retrieved only Wikivoyage.
  - The gap is the phone path: its router skips retrieval on health items, and it has no desktop-style dense / head-pass append for the topical packs, only serial lexical fusion cut to topK. PackSource code 10 may add a label issue on top.
  - It is not missing pack content.
- **Visa reads as a distractor more than a source.** Of its 18 kept items, 12 are off-topic: bitcoin, ethereum, cooking, factbook, simplewiki, medlineplus self-tests. Only travel-se 002/004/020 and lan-rsn-004 are plausibly on topic. No visa gold exists, so its value is unmeasured. This is a quality lead (MATRIX: CE-unwarned 7 -> 12 under KA), not a pruning result.

## Maintainer note (proposed text)
"Keep all six A-union packs. On the desktop pipeline each one puts chunks into the answer context: medlineplus on 26 of 257 dev questions, including the key fact for two real health questions. On the phone build, medlineplus and visa never surfaced in 73 questions. That is because the phone router skipped retrieval on most health questions, and the phone engine has no dense second-stage pick for the topical packs. The pack content is fine. Removing a pack does not save time cheaply without changing answers: each pack costs about 0.15 s per question only because packs are searched one after another. Search them in parallel or merge them into one file (PK-5) instead. Also map PackSource codes 10 (MedlinePlus) and 11 (Factbook) to their own labels."

## Caveats
- **The desktop LITEPACKS adapter is not the phone engine.** It differs in its head pass, dense two-stage candidates, kit per request and router. "Contributes on the desktop" is not "contributes on the APK". The phone 73 numbers are quoted from AUNION-PIXEL, not re-run.
- "Kept" is not "helpful": no judge here. Fact-chunk counts exist only where a gold exists: oracle-facts for the self-tests, gold-labels Y/P for real items.
- Latency per pack = AUNION-PIXEL SQL ms / 73 questions, one warm run.

## Files
- `PK4-PACK-PRUNE-2026-10-21.json` (sha256 aedaa57815a2032d81f4089831bd54be631d933c9826c1c6718308e72c5ccd4f). It holds per item x pack raw / dense / kept / fact counts, the per-pack table, the variant diffs, the medlineplus probe and the replay file shas.
- `tools/pk4_replay.sh` (sha256 894a0ef1...) and `tools/pk4_prune.py` (sha256 db053841...).
- Replay outputs (pack text) stay out of git and are reproducible.

Rerun:
```
bash tools/pk4_replay.sh <job: req/KA-{V01,CM,ST}.requests.jsonl (= coverage-matrix req lp-KA-*) [+ KA-minus-<pack>-* variants] + stub_server.py> <funnel tree>   # MacBook, ~2 min per 280, detector :8094 up
python3 -I tools/pk4_prune.py <job>/out PK4-PACK-PRUNE-2026-10-21.json
```
