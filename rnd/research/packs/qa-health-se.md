# qa-health-se (Medical Sciences Stack Exchange Q&A)
TL;DR: one doc per medicalsciences.stackexchange.com question (question + up to 5 kept answers) from the archive.org 2024-04-02 dump; format 2 with per-row author attribution (T-K2); built 2026-10-12 (T-K3); NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Source: medicalsciences.stackexchange.com (`health.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 22,447,982 B, sha256 640567b3dc94910db67fb776f371069e9f5786dee8239473e3240036b072abfb). Domain: health / medical explanation questions.
- Converter: `rnd/kiln/packs/convert/convert.mjs stackexchange` (T-K1) with defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 7,930; skipped without a kept answer 2,882; too short 0; dropped after conversion for an empty title (deleted question bodies) 0; kept 5,048.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 3.0 2,806; CC BY-SA 4.0 2,242 (no 2.5 rows: the attribute reflects the latest revision). Rows whose answers carry a different licence than the question: 338 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 128. Share-alike: redistributions must stay CC BY-SA.
- Attribution (D-K2, per row in `article_meta.attribution`, present on all 5,048 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example citation string (engine `packHitToChunk`, query "how to treat a snake bite"): top hit "Stack Exchange: First aid measures for a snake bite (Answers > Answer (score 9))".
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 5,048; chunks 20,656; indexed 20,656 (100 %); lead_vecs 5,048 (= articles); redirects 0; views = question ViewCount (all > 0).
- Size: 23,797,760 B (22.7 MiB). sha256 687e4994de254704d49c1433821febf043b05e17d111c618f3134497dcbde930.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"qa-health-se","sha256":"687e4994…"}. Needs the T-K2 engine patch for the "Stack Exchange" label and attribution (without it the shipped app falls back to "enwiki" labels).
- Files: mini `<runner>/shared-data/packs/wave1/qa-health-se.sqlite(.json)`; MacBook `shared-data/packs/wave1/`.
- Build (mini M4, Metal embeddings, wall 25 s):
  ```sh
  cd <runner>/kiln/packs && bash scripts/conv-se.sh health qa-health-se      # convert + validate
  # (no empty-title rows)
  bash scripts/build.sh qa-health-se "Medical Sciences Stack Exchange Q&A" work/qa-health-se/manifest.json work/qa-health-se/*.jsonl
  ```
  Scripts: rnd/kiln/packs/wave1-scripts/ (copied to the mini as <runner>/kiln/packs/scripts/). build.sh = `cd <runner>/kiln/packs/builder && BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the T-K2 builder (scripts sha = wt/packs).
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (V-para has no health category) (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4 (jev F0 on V-para 34 absent items + v0.2 by category).
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): share v0.2 0.108 / v0.1 0.061, 14/16 v0.2 slots on health/danger items, gold unchanged (18/15, 16/14), p50 +18 ms → **default-eligible**.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.53** (0.46–0.59), above_min 0.39 / without pack raw **0.51** (0.45–0.56), above_min 0.37; paired Δ +0.016 raw (95 % CI -0.014…+0.046), +0.019 above_min; items better/worse with the pack 9/7; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 10/20 items (19/23 kept passages); the fact's source article kept on 5/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.526 vs without 0.541, Δ −0.016 (−0.058…+0.026); deep with pack vs 4B with pack +0.001 (−0.034…+0.039); pack passages kept on 10/20 items; win 0/20. Dev numbers, agent-written gold; the deep tier gains nothing measurable from this pack.
## Category gaps
- Small site with many unanswered questions (2,882 of 7,930 had no answer at score >= 1 and were skipped); answers are lay explanations with variable sourcing, not clinical guidance; the site closes personal medical-advice questions, so expect few individual treatment threads (not measured).
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Fresher alternative: Kiwix 2026 ZIMs (O-K1) if the pack proves useful.
- Community answers are not reviewed; health/safety answers keep the "AI-reviewed, not clinically reviewed" caveat and should rank below PD/clinical sources.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-health-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
