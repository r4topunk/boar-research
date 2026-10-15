# qa-ethereum-se (Ethereum Stack Exchange Q&A)
TL;DR: one doc per ethereum.stackexchange.com question (question + up to 5 kept answers) from the archive.org 2024-04-02 dump; format 2 with per-row author attribution (T-K2); built 2026-10-12 (T-K3); NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Source: ethereum.stackexchange.com (`ethereum.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 107,238,652 B, sha256 e9dc40cbcec3ce45c79f19841419851fd79b8224df85e1fc486f25f317d9dcfb). Domain: Ethereum development (Solidity, web3 libraries, clients), EIPs, wallets.
- Converter: `rnd/runner/packs/convert/convert.mjs stackexchange` (T-K1) with defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 53,463; skipped without a kept answer 18,868; too short 5; dropped after conversion for an empty title (deleted question bodies) 2; kept 34,588.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 3.0 12,497; CC BY-SA 4.0 22,091 (no 2.5 rows: the attribute reflects the latest revision). Rows whose answers carry a different licence than the question: 2,102 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 599. Share-alike: redistributions must stay CC BY-SA.
- Attribution (D-K2, per row in `article_meta.attribution`, present on all 34,588 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example citation string (engine `packHitToChunk`, query "how does EIP-1559 change gas fees"): top hit "Stack Exchange: Why can transactions use legacy gas fee model instead of EIP 1559?".
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 34,588; chunks 118,560; indexed 118,560 (100 %); lead_vecs 34,588 (= articles); redirects 0; views = question ViewCount (all > 0).
- Size: 102,473,728 B (97.7 MiB). sha256 f16b258f87c0f4253360b45d86de2a94c7f9fba45f91571aec2c97588f858d56.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"qa-ethereum-se","sha256":"f16b258f…"}. Needs the T-K2 engine patch for the "Stack Exchange" label and attribution (without it the shipped app falls back to "enwiki" labels).
- Files: `$RUNNER_ROOT/shared-data/packs/wave1/qa-ethereum-se.sqlite(.json)` on the build host.
- Build (build host, Apple M4, Metal embeddings, wall 195 s):
  ```sh
  cd $RUNNER_ROOT/runner/packs && bash scripts/conv-se.sh ethereum qa-ethereum-se      # convert + validate
  node scripts/drop-empty-title.mjs work/qa-ethereum-se                       # drops deleted-question rows (validate.mjs 'empty title')
  bash scripts/build.sh qa-ethereum-se "Ethereum Stack Exchange Q&A" work/qa-ethereum-se/manifest.json work/qa-ethereum-se/*.jsonl
  ```
  Scripts: rnd/runner/packs/wave1-scripts/ (copied to the mini as $RUNNER_ROOT/runner/packs/scripts/). build.sh = `cd $RUNNER_ROOT/runner/packs/builder && BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the T-K2 builder (scripts sha = wt/packs).
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (crypto items already covered by the kit) (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4 (jev F0 on V-para 34 absent items + v0.2 by category).
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): share v0.2 0.110 / v0.1 0.088, slots stay on crypto items, but kit gold lower on v0.2 (18/15 → 14/12, 4 crypto items; v0.1 unchanged) → **user-selected only, not default**.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.52** (0.45–0.58), above_min 0.38 / without pack raw **0.44** (0.38–0.51), above_min 0.28; paired Δ +0.074 raw (95 % CI +0.016…+0.133), +0.097 above_min; items better/worse with the pack 12/5; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 16/20 items (31/36 kept passages); the fact's source article kept on 7/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.582 vs without 0.575, Δ +0.007 (−0.067…+0.089); deep with pack vs 4B with pack +0.066 (−0.009…+0.135); pack passages kept on 15/20 items; win 0/20. Dev numbers, agent-written gold; the deep tier gains nothing measurable from this pack.
## Category gaps
- Developer-heavy (Solidity/web3.js/Truffle code questions dominate; many tied to deprecated tooling); 35 % of questions skipped as unanswered; pre-merge (PoW) answers not marked as outdated; snapshot 2024-04 (no Pectra-era content).
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Fresher alternative: Kiwix 2026 ZIMs (O-K1) if the pack proves useful.
- Community answers are not reviewed; health/safety answers keep the "AI-reviewed, not clinically reviewed" caveat and should rank below PD/clinical sources.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-ethereum-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
