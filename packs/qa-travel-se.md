# qa-travel-se (Travel Stack Exchange Q&A)
TL;DR: one doc per travel.stackexchange.com question (question + up to 5 kept answers) from the archive.org 2024-04-02 dump; format 2 with per-row author attribution (T-K2); built 2026-10-12 (T-K3); NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Source: travel.stackexchange.com (`travel.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 156,149,761 B, sha256 4c33527edc970cc32a159607372ba652d4328fa007e1214f3510595f55629169). Domain: visas, border rules, airlines, practical local travel.
- Converter: `rnd/runner/packs/convert/convert.mjs stackexchange` (T-K1) with defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 48,768; skipped without a kept answer 6,455; too short 3; dropped after conversion for an empty title (deleted question bodies) 3; kept 42,307.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 3.0 25,452; CC BY-SA 4.0 16,855 (no 2.5 rows: the attribute reflects the latest revision). Rows whose answers carry a different licence than the question: 2,435 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 814. Share-alike: redistributions must stay CC BY-SA.
- Attribution (D-K2, per row in `article_meta.attribution`, present on all 42,307 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example citation string (engine `packHitToChunk`, query "what vaccinations do I need for Thailand"): top hit "Stack Exchange: Should I still try to get vaccinated for Thailand?".
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 42,307; chunks 155,315; indexed 155,315 (100 %); lead_vecs 42,307 (= articles); redirects 0; views = question ViewCount (all > 0).
- Size: 148,324,352 B (141.5 MiB). sha256 a85521ceaa30b176116f2a827d8652fddc6c0cf704da9874c138eff7d5217427.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"qa-travel-se","sha256":"a85521ce…"}. Needs the T-K2 engine patch for the "Stack Exchange" label and attribution (without it the shipped app falls back to "enwiki" labels).
- Files: `$RUNNER_ROOT/shared-data/packs/wave1/qa-travel-se.sqlite(.json)` on the build host.
- Build (build host, Apple M4, Metal embeddings, wall 205 s):
  ```sh
  cd $RUNNER_ROOT/runner/packs && bash scripts/conv-se.sh travel qa-travel-se      # convert + validate
  node scripts/drop-empty-title.mjs work/qa-travel-se                       # drops deleted-question rows (validate.mjs 'empty title')
  bash scripts/build.sh qa-travel-se "Travel Stack Exchange Q&A" work/qa-travel-se/manifest.json work/qa-travel-se/*.jsonl
  ```
  Scripts: rnd/runner/packs/wave1-scripts/ (copied to the mini as $RUNNER_ROOT/runner/packs/scripts/). build.sh = `cd $RUNNER_ROOT/runner/packs/builder && BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the T-K2 builder (scripts sha = wt/packs).
## Measured coverage
- V-para 34 absent items: verified 1/34 (travel-practical, on-topic group), >=0.7 1, >=0.6 3 (2 travel-local/practical leads); the only wave-1 pack with a verified V-para hit (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4 (jev F0 on V-para 34 absent items + v0.2 by category).
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): kit + pack, deep k 6: kept-slot share v0.2 0.316 / v0.1 0.196 (≤ 0.40) but kit gold lower (v0.2 raw6/kept 18/15 → 13/11, v0.1 16/14 → 11/9; 4+4 items) and 81 % of its v0.2 slots on non-travel items → **user-selected only, not default**.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.42** (0.36–0.48), above_min 0.26 / without pack raw **0.39** (0.33–0.46), above_min 0.22; paired Δ +0.029 raw (95 % CI -0.022…+0.077), +0.040 above_min; items better/worse with the pack 11/2; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 9/20 items (15/28 kept passages); the fact's source article kept on 6/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.548 vs without 0.555, Δ −0.007 (−0.071…+0.048); deep with pack vs 4B with pack +0.125 (+0.058…+0.197); pack passages kept on 12/20 items; win 0/20. Dev numbers, agent-written gold; the deep tier gains nothing measurable from this pack.
## Category gaps
- Visa/entry rules and prices go stale fast (snapshot 2024-04-02; many answers older); Schengen/UK/US visa questions dominate; BM25 can surface topical-but-wrong threads ("is tap water safe to drink in Mexico" -> "Washing cuts in Mexico").
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Fresher alternative: Kiwix 2026 ZIMs (O-K1) if the pack proves useful.
- Community answers are not reviewed; health/safety answers keep the "AI-reviewed, not clinically reviewed" caveat and should rank below PD/clinical sources.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-travel-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
