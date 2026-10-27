# qa-bitcoin-se (Bitcoin Stack Exchange Q&A)
TL;DR: one doc per bitcoin.stackexchange.com question (question + up to 5 kept answers) from the archive.org 2024-04-02 dump; format 2 with per-row author attribution (T-K2); built 2026-10-12 (T-K3); NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Source: bitcoin.stackexchange.com (`bitcoin.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 73,805,258 B, sha256 90568a63d7fce4857371e4e84772bdfe059c4c578fbc52b57e84246a2892e8c1). Domain: Bitcoin protocol, wallets, mining, Lightning.
- Converter: `rnd/kiln/packs/convert/convert.mjs stackexchange` (T-K1) with defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 30,992; skipped without a kept answer 4,941; too short 8; dropped after conversion for an empty title (deleted question bodies) 1; kept 26,042.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 3.0 15,929; CC BY-SA 4.0 10,113 (no 2.5 rows: the attribute reflects the latest revision). Rows whose answers carry a different licence than the question: 1,233 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 274. Share-alike: redistributions must stay CC BY-SA.
- Attribution (D-K2, per row in `article_meta.attribution`, present on all 26,042 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example citation string (engine `packHitToChunk`, query "how does segwit fix transaction malleability"): top hit "Stack Exchange: Are non-SegWit transactions still malleable? (answers by Pieter Wuille, Ava Chow)".
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 26,042; chunks 84,399; indexed 84,399 (100 %); lead_vecs 26,042 (= articles); redirects 0; views = question ViewCount (all > 0).
- Size: 77,889,536 B (74.3 MiB). sha256 35b7a3ce3cdd7d31a20e968337a530e8679c1702ca0dbc0538e7a30bad2342c8.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"qa-bitcoin-se","sha256":"35b7a3ce…"}. Needs the T-K2 engine patch for the "Stack Exchange" label and attribution (without it the shipped app falls back to "enwiki" labels).
- Files: mini `<runner>/shared-data/packs/wave1/qa-bitcoin-se.sqlite(.json)`; MacBook `shared-data/packs/wave1/`.
- Build (mini M4, Metal embeddings, wall 130 s):
  ```sh
  cd <runner>/kiln/packs && bash scripts/conv-se.sh bitcoin qa-bitcoin-se      # convert + validate
  node scripts/drop-empty-title.mjs work/qa-bitcoin-se                       # drops deleted-question rows (validate.mjs 'empty title')
  bash scripts/build.sh qa-bitcoin-se "Bitcoin Stack Exchange Q&A" work/qa-bitcoin-se/manifest.json work/qa-bitcoin-se/*.jsonl
  ```
  Scripts: rnd/kiln/packs/wave1-scripts/ (copied to the mini as <runner>/kiln/packs/scripts/). build.sh = `cd <runner>/kiln/packs/builder && BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the T-K2 builder (scripts sha = wt/packs).
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 1 (reasoning, on-topic, quote 0.61 < 0.7), >=0.6 1 (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4 (jev F0 on V-para 34 absent items + v0.2 by category).
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): share v0.2 0.146 / v0.1 0.079, slots mostly on crypto items, but kit gold lower (v0.2 18/15 → 14/12 on the same 4 crypto items as ethereum-se; v0.1 16/14 → 15/13) → **user-selected only, not default**.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.47** (0.38–0.56), above_min 0.32 / without pack raw **0.41** (0.34–0.50), above_min 0.25; paired Δ +0.054 raw (95 % CI +0.017…+0.094), +0.070 above_min; items better/worse with the pack 10/4; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 16/20 items (32/34 kept passages); the fact's source article kept on 2/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.545 vs without 0.578, Δ −0.034 (−0.083…+0.009); deep with pack vs 4B with pack +0.076 (+0.028…+0.131); pack passages kept on 18/20 items; win 0/20 (1 tie). Dev numbers, agent-written gold; the deep tier gains nothing measurable from this pack.
## Category gaps
- Many answers are dated (2011–2016 wallet/software specifics, fee levels, exchange names); no post-2024-04 content (no recent soft-fork proposals beyond that); price/market questions are off-topic on the site.
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Fresher alternative: Kiwix 2026 ZIMs (O-K1) if the pack proves useful.
- Community answers are not reviewed; health/safety answers keep the "AI-reviewed, not clinically reviewed" caveat and should rank below PD/clinical sources.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-bitcoin-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
