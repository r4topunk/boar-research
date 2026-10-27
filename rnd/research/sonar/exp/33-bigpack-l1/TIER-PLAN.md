# Full-English-Wikipedia title-lookup tier: plan (Sonar, 2026-10-03; ready to execute if the L1 says GO)

TL;DR:
- **What:** the whole English Wikipedia (6.12 M articles) as a second tier that answers only for articles the question NAMES (title or redirect n-grams), never with whole-index keyword hits.
  - Kit packs keep full search. The tier adds named article bodies (Mozi, Gríma Wormtongue, Saruman, ML-KEM, SPHINCS+, Climate of Japan…) without the displacement and 2× latency of the #17 full-search test.
- **Size ≈ 8.3 GB** instead of 18.0 GB: drop the body FTS index (9.6 GB of the 15 shards). Keep text blocks, chunks, titles, redirects and lead vectors.
- **Build: minutes, measured.** `slim-wiki-pack.mjs` on the 1.56 GB sample pack gave 0.70 GB (−55%) in 14 s on the MacBook, with identical article/chunk/redirect counts. 15 shards ≈ a few minutes of I/O, plus hashing. Local only; publishing needs r4to's OK.
- **Engine: done in `bounty3`** (`bounty3-engine.patch`; delta `bounty3-on-bounty2.patch`):
  - `namedOnly` packs (bounty2);
  - FTS-less shards: no fts5vocab view, no fuzzy title search, no BM25, and a term missing from `df` counts as rare (doc = 1), so rare names ("mozi", "gríma") keep their weight;
  - unit test: the mini-wiki fixture with its FTS dropped resolves "Black hole" and the rare multi-word "Kuala Kubu Bharu", and returns nothing for an unnamed question;
  - slim sample probe (desktop): named lookups 1–21 ms ("Tell me about Japan" → Japan).
  - Optional later: one merged title index, so a question does 1 lookup, not 15.
- **Gate:** the L1 in `L1-criterion.md` (arm C = top100k as a tier). GO → build; KILL → park.

## Sizes (measured from the 15 shard manifests `shared-data/packs/boar-wiki-en-*.sqlite.json`)
| Table | Size | In the tier? |
|---|---|---|
| fts_data + fts_docsize + fts_idx (body full-text index) | 9.61 GB | **no** |
| blocks (zstd article text) | 6.45 GB | yes |
| chunks | 0.52 GB | yes |
| redirects | 0.35 GB | yes |
| chunks_article | 0.34 GB | yes |
| articles (titles, views, sections) | 0.29 GB | yes |
| lead_vecs (bge-small, top ~50k per shard) | 0.21 GB | yes (keeps the semantic checks) |
| articles_title | 0.18 GB | yes |
| **Tier total** | **≈ 8.34 GB** (vs 18.03 GB full) | |
| optional title-only FTS (fuzzy titles: "dilithium signature" → "ML-DSA") | ESTIMATE ~0.3–0.5 GB | later, if exact + redirect misses too much |

- **Budget** (B-pack-budget.md S1 ≈ 24.6 GB with the full 18.4 GB pack): with the tier instead, ≈ 14.5 GB total. That leaves ~35 GB for models: the 35B-A3B 12.3 GB deep tier fits with room to spare.

## Build (mini; Kiln or Sonar; ≈ 1 h)
1. For each `boar-wiki-en-NN.sqlite`: `sqlite3 out.sqlite`, then ATTACH the source and `CREATE TABLE … AS SELECT` every table except `fts*`, plus the same indexes. Then copy `meta` and set `meta.tier = named`, `VACUUM`. Alternatively, a `--no-body-fts` flag in `scripts/build-wiki-pack.mjs` for a clean rebuild.
2. Verify per shard: the article and redirect counts equal the source's; 1,000 random titles resolve to the same article id and the same decompressed text.
3. Hash (SHA256SUMS) and keep the shards LOCAL (mini + MacBook) as `boar-wiki-en-names-NN`. **No upload to Hugging Face or anywhere public without r4to's explicit OK** (publishing is his call). A catalog entry is drafted but not published.

## Engine (on top of bounty2)
- `namedOnly` for `^boar-wiki-en-(top\d+k|\d{2}|names-\d{2})$`: only `titlesInQuestion` + `titles` hits; no BM25, no action pool, no expansion. **Done in bounty2.**
- Shards without an FTS table: `resolveTitle` skips the fuzzy step (it uses the FTS title column) and `bm25Candidates` is never called. Detect it via `sqlite_schema` at open. **To do** (~20 lines + a test).
- Ordering against the kit: tier hits go after kit hits for the same article title (the kit's richer chunks win), and a named tier article goes ahead of unrelated kit keyword hits. Today's `searchWikiPacks` concatenation + compression already favours the named title (titleSegmentNamed in onTopic). The L1 checks it.
- Gates: a named article passes `onSubject` by construction (title named in the question). The crypto, health and instant guards are unchanged. The health route never reads it (health-strict topic filter).
- Phone cost: 15 shard files → 15 small title/redirect lookups per question (P-8 batching: one `IN` query per shard). If the device timer shows > 50 ms, merge one `titles.sqlite` (normalized title/redirect → shard, article id; ESTIMATE 0.5–0.7 GB) so it is 1 lookup.

## What it can and can't fix (EN)
- **Can:** named-entity questions whose article is outside the kit. the post author's titles: 30/32 in the top 1M (B §1); V-exact Gríma, Japan (body), Mozi (rank 176k).
- **Can't:** unnamed questions ("which signatures resist quantum attacks?" → no title named; the kit and crypto pack handle those); questions needing synthesis across many articles; anything absent from Wikipedia.
- **Risks:**
  - wrong entity on ambiguous names ("Mercury"); the views prior and the disambiguation check exist;
  - long-article sections ranked by question stems only (no body FTS): `titleHits` already ranks sections by stems;
  - storage I/O for 15 files on the phone (Forge measures);
  - CC BY-SA attribution: the sources UI already shows the Wikipedia URL.

## UNKNOWN
- Device lookup latency with 15 files; how often V-para questions name their entity; the gain on v0.2 out-of-kit items (72% out of kit, per coordinator); whether exact + redirect without fuzzy misses common phrasings.
