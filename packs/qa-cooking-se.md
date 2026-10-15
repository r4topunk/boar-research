# qa-cooking-se (Seasoned Advice, cooking Stack Exchange Q&A)
TL;DR: one doc per cooking.stackexchange.com (Seasoned Advice) question, with up to 5 kept answers, from the archive.org 2024-04-02 dump; format 2 with per-row author attribution; built 2026-10-13 (wave 3); not in any kit; default-eligible (crowding probe 2026-10-13); self-test scored 2026-10-13.

## What it is
- Source: cooking.stackexchange.com (`cooking.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 87,555,311 B, sha256 de98b85f9807a23dfc8c91006f8b59b2149089e94ea9d54676d215ea156a9ac6). Domain: home cooking technique, food safety and storage, ingredients and substitutions, equipment.
- Converter: the pack converter (`convert.mjs stackexchange`) with the wave-1 defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 27,325; skipped without a kept answer 1,615; too short 8; dropped after conversion for an empty title (deleted question bodies) 4; kept 25,698.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 2.5 2,567; CC BY-SA 3.0 15,244; CC BY-SA 4.0 7,887 (the site opened in 2010, so posts from before 2011-04-08 keep CC BY-SA 2.5). Rows whose answers carry a different licence than the question: 2,827 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 607. Share-alike: redistributions must stay CC BY-SA.
- Attribution (per row in `article_meta.attribution`, present on all 25,698 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example: top keyword (FTS) hit for "tallow room temperature store" = "Stack Exchange: Can I store suet or home-rendered tallow at room temperature for a year?" (https://cooking.stackexchange.com/questions/12532, CC BY-SA 4.0), shown with its per-post author line.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 25,698; chunks 98,477; indexed 98,477 (100 %); lead_vecs 25,698 (= articles); redirects 0; views = question ViewCount.
- Size: 88,973,312 B (84.9 MiB). sha256 81990fa938ecf7d467a31efacdd58cd6f98392261e5e06ba92fcd0174b3dba35.
## Build (reference)
- Kit entry: {"id":"qa-cooking-se","sha256":"81990fa938ecf7d467a31efacdd58cd6f98392261e5e06ba92fcd0174b3dba35"}. The "Stack Exchange" source label and the per-post attribution need the BOAR app update that adds the Stack Exchange source code; without it the shipped app labels the rows as Wikipedia.
- Build (build host Apple M4, Metal embeddings, wall 119 s): `scripts/se-wave3.sh cooking` = `scripts/conv-se.sh cooking qa-cooking-se` (convert + validate) → `drop-empty-title.mjs` (4 rows) → `scripts/build.sh qa-cooking-se "Seasoned Advice (cooking) Stack Exchange Q&A" work/qa-cooking-se/manifest.json work/qa-cooking-se/*.jsonl`; build.sh = `BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the BOAR pack builder.
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (max p 0.15) (coverage probe 2026-10-13: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42). The bounty-style set has no cooking questions; the union of the 11 published packs stays 2/34 (6/34 with the claim kit).
## Crowding
- Crowding probe (2026-10-13; deep-tier retrieval replay, k 6, pool 20, claim kit + this pack as a peer): kept-slot share v0.2 0.022 (3/138) / v0.1 0.018 (2/109), kit gold unchanged (raw6/kept 18/15 and 16/14), retrieval p50 +12 / +26 ms → **default-eligible** by rule. It takes almost no slots anywhere (2 of 52 kept slots on its matching v0.2 categories: local food, health, explanation), so it passes by absence rather than by proven in-topic benefit on these sets.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.46** (0.39–0.53), above_min 0.32 / without pack raw **0.45** (0.39–0.52), above_min 0.30; paired Δ +0.010 raw (95 % CI -0.039…+0.065), +0.013 above_min; items better/worse with the pack 8/8; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 11/20 items (30/32 kept passages); the fact's source article reached raw retrieval on 9/20 and was kept on 5/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers. One drafted item (Bacillus cereus in baked goods) was replaced by another drawn candidate before the with-pack run because the judge model refused it under its usage filter.
## Category gaps
- North-American home-cooking focus (Fahrenheit, US food-safety guidance); many recipe-specific and troubleshooting threads; food-safety answers range from cited guidance to anecdote; 2024-04 snapshot.
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Community answers are not reviewed; food-safety answers keep the "AI-reviewed, not clinically reviewed" caveat and should rank below public-health sources.

## Published
- 2026-10-13: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-cooking-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; pack commit fb65798e; root README "Wave 3 (2026-10-13)" section, commit ec0fa52c).
