# boar-crypto (Ethereum and cryptography)
TL;DR: curated format-2 pack of EIPs, BIPs, Ethereum specs, ethereum.org docs and 1,369 Wikipedia articles; in the shipped kit (config.kit[0]); the best-covered domain on the dev sets.

## What it is
- Source: eips 1,208, bips 180, ethspecs 156, ethereumorg 228, enwiki 1,369 (articles 3,141 total). Built 2026-09-27 (meta builtAt 2026-09-27T00:06Z).
- Licence (meta): CC0 1.0; BSD-2/3-Clause; PD; MIT; CC-BY-4.0; FSFAP variants; CC BY-SA 4.0 (Wikipedia, 27 ethspecs). Mixed; per-source map is in meta `sources`.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da...f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. Tables: articles, articles_title, chunks, chunks_article, blocks (zstd text), redirects, df, lead_vecs (3,141, int8), contentless FTS5 (fts_*), article_meta. FTS yes.
- Counts: chunks 54,998; indexed 53,680 (97.6 %). Tables-in-FTS caveat: chunks that are mostly tables/numbers are not indexed (1,318 here, small).
- Size: 36,093,952 B (35 MB). sha256 ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb (the valid one; boar-crypto.OLD-b309ba9.sqlite, 35,962,880 B, is rejected by the app catalog). Note: boar-crypto.sqlite.json next to it still records the OLD build (sha 9ac8ad1c..., 35,962,880 B).
## Kit entry and build
- config.kit: {"id":"boar-crypto","sha256":"ae9fbd2c..."} (boar-eval/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json). Published on HF r4topunk/boar-packs (topics/boar-crypto.sqlite), see shared-data/crypto/README.md.
- Build: boar-app/scripts/build-wiki-pack.mjs (sources in shared-data/crypto/src, build/ shards, build.log: 3 s text step). Query vectors: questions.crypto.v1.qvecs.json.
## Measured coverage (PACKCOND P1, arm H deep+think 512 / K 4B cut 6; F0 = jev fact-in-text >= 0.7, dev data, 1 seed)
- V-para (51): F0 4 (H) / 3 (K), of 5 crypto items (H 4/5). v0.2 (110): F0 5 (H) / 3 (K), of 13 crypto items.
- Crypto category is the only one where this pack carries the rubric facts; elsewhere F0 is ~0.
## Measured quality effects
- Part of the curated kit: DEEPNORAG (no packs vs kit, deep tier) = -0.045 without packs (CI -0.083...-0.011), so the curated kit adds about +0.045. Not isolated per pack.
- Bucket pooled (all kit packs, n=64 F0 cells): retrieved-not-used 18, dropped 15, used-wrong 11, used-right 10, not-retrieved 10.
## Known gaps
- Covers 5/13 v0.2 and 4/5 V-para crypto items at best; misses on non-Ethereum crypto (Bitcoin economics, DeFi prose beyond Wikipedia), and every non-crypto category. No crowding measured (small pack, peer to wikivoyage in the kit).
## Community curation notes
- Card fields: id, name, domain, source + snapshot date, licence line per source (meta `sources`/`license`), counts, sha256, build command, kit entry `{id, sha256}`, known gaps.
- Self-test set (PACKCOND O4, P5, needs the maintainer): 20 public questions written by a curator (not Claude) whose answers are in the pack; scored by the same pipeline (F0 gate, then judge.v1 ratio); ship the per-pack number on the card.
- Licence: keep the per-source licence map from meta and a one-line attribution; CC BY-SA 4.0 and ODbL 1.0 are share-alike (card must say so).
- Self-test candidates: EIP/BIP number lookups (EIP-1559, BIP-39), ethspecs terms.
