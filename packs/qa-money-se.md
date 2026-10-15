# qa-money-se (Personal Finance & Money Stack Exchange Q&A)
TL;DR: one doc per money.stackexchange.com (Personal Finance & Money) question, with up to 5 kept answers, from the archive.org 2024-04-02 dump; format 2 with per-row author attribution; built 2026-10-13 (wave 3); not in any kit; user-selected only (crowding probe 2026-10-13); self-test scored 2026-10-13.

## What it is
- Source: money.stackexchange.com (`money.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 132,623,554 B, sha256 ef2621a7c4f0ad5e52a1daef8b53e34033cd805f944787328ce47b6fd3839cc2). Domain: personal finance: credit and debt, banking, taxes, retirement accounts, investing, insurance, housing, scams.
- Converter: the pack converter (`convert.mjs stackexchange`) with the wave-1 defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 38,860; skipped without a kept answer 3,755; too short 3; dropped after conversion for an empty title 0; kept 35,102.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 2.5 1,449; CC BY-SA 3.0 18,087; CC BY-SA 4.0 15,566 (the site opened in 2009, so posts from before 2011-04-08 keep CC BY-SA 2.5). Rows whose answers carry a different licence than the question: 1,779 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 566. Share-alike: redistributions must stay CC BY-SA.
- Attribution (per row in `article_meta.attribution`, present on all 35,102 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example: top keyword (FTS) hit for "hard inquiry credit score" = "Stack Exchange: How is an inquiry on the credit report different from checking credit score?" (https://money.stackexchange.com/questions/71706, CC BY-SA 3.0), shown with its per-post author line.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 35,102; chunks 143,397; indexed 143,397 (100 %); lead_vecs 35,102 (= articles); redirects 0; views = question ViewCount.
- Size: 137,240,576 B (130.9 MiB). sha256 374112341f2aa92f136b37fd3855d90710936cd158fb46f0f639de7b33ed5a88.
## Build (reference)
- Kit entry: {"id":"qa-money-se","sha256":"374112341f2aa92f136b37fd3855d90710936cd158fb46f0f639de7b33ed5a88"}. The "Stack Exchange" source label and the per-post attribution need the BOAR app update that adds the Stack Exchange source code; without it the shipped app labels the rows as Wikipedia.
- Build (build host Apple M4, Metal embeddings, wall 183 s): `scripts/se-wave3.sh money` = `scripts/conv-se.sh money qa-money-se` (convert + validate) → `drop-empty-title.mjs` (0 rows) → `scripts/build.sh qa-money-se "Personal Finance & Money Stack Exchange Q&A" work/qa-money-se/manifest.json work/qa-money-se/*.jsonl`; build.sh = `BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the BOAR pack builder.
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (max p 0.38) (coverage probe 2026-10-13: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42). The union of the 11 published packs stays 2/34 (6/34 with the claim kit).
## Crowding
- Crowding probe (2026-10-13; deep-tier retrieval replay, k 6, pool 20, claim kit + this pack as a peer): kept-slot share v0.2 0.088 (12/136) / v0.1 0.038 (4/105), but the kit's gold is lower: raw6/kept v0.2 18/15 → 16/13 (2 items), v0.1 16/14 → 14/12 (1 item); 7 of its 12 v0.2 slots land outside its matching categories (reasoning, comparison, crypto, travel-practical); retrieval p50 +11 / +19 ms → **user-selected only, not default**.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.46** (0.39–0.52), above_min 0.30 / without pack raw **0.43** (0.38–0.47), above_min 0.26; paired Δ +0.030 raw (95 % CI -0.007…+0.072), +0.039 above_min; items better/worse with the pack 10/5; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 11/20 items (30/31 kept passages), but the fact's own thread reached raw retrieval on 0/20: the kept passages are other threads on the same topic. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
## Category gaps
- US-centred (401(k)/IRA/HSA, FDIC, US tax forms) with a UK/India/Canada minority; tax figures, contribution limits and rates are as of each post (2009–2024) and many are out of date; investing answers mix facts with opinion; 2024-04 snapshot.
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Community answers are not reviewed and are not financial, tax or legal advice; year-specific numbers should be shown with the post date and rank below official sources.

## Published
- 2026-10-13: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-money-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; pack commit a66a5c33; root README "Wave 3 (2026-10-13)" section, commit ec0fa52c).
