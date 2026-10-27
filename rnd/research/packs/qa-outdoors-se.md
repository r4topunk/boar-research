# qa-outdoors-se (The Great Outdoors Stack Exchange Q&A)
TL;DR: one doc per outdoors.stackexchange.com question (question + up to 5 kept answers) from the archive.org 2024-04-02 dump; format 2 with per-row author attribution (T-K2); built 2026-10-12 (T-K3); NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Source: outdoors.stackexchange.com (`outdoors.stackexchange.com.7z`, archive.org item `stackexchange`, dump 2024-04-02; 31,445,654 B, sha256 f45a642dcedcfc9642002aaf297426121aa2a0fa62799592ca2819d265f01a05). Domain: hiking, camping, wilderness skills and safety.
- Converter: `rnd/kiln/packs/convert/convert.mjs stackexchange` (T-K1) with defaults: min answer score 1 (accepted answers always kept), max 5 answers (accepted first, then by score), unanswered questions skipped. Questions in the dump 6,168; skipped without a kept answer 296; too short 0; dropped after conversion for an empty title (deleted question bodies) 0; kept 5,872.
- Licence: CC BY-SA per post, from each post's `ContentLicense` (latest revision). Rows: CC BY-SA 3.0 3,900; CC BY-SA 4.0 1,972 (no 2.5 rows: the attribute reflects the latest revision). Rows whose answers carry a different licence than the question: 612 (the attribution says "answers also under CC BY-SA x"). Attribute vs date-rule mismatches: 144. Share-alike: redistributions must stay CC BY-SA.
- Attribution (D-K2, per row in `article_meta.attribution`, present on all 5,872 rows): `Q by <name> (<profile url>); A by <name> (<profile url>); …; <question url>`. Example citation string (engine `packHitToChunk`, query "how to store food away from bears when camping"): top hit "Stack Exchange: What are the proper precautions/protocols for storing food while car camping in an area with bears?".
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514 (bge-small-en-v1.5 q8_0). Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 9 (stackexchange) on every row.
- Counts: articles 5,872; chunks 31,378; indexed 31,378 (100 %); lead_vecs 5,872 (= articles); redirects 0; views = question ViewCount (all > 0).
- Size: 31,555,584 B (30.1 MiB). sha256 ff733e4f587c2e16f802b8213de21b986924dd76c22e29d61e494b2587e6272a.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"qa-outdoors-se","sha256":"ff733e4f…"}. Needs the T-K2 engine patch for the "Stack Exchange" label and attribution (without it the shipped app falls back to "enwiki" labels).
- Files: mini `<runner>/shared-data/packs/wave1/qa-outdoors-se.sqlite(.json)`; MacBook `shared-data/packs/wave1/`.
- Build (mini M4, Metal embeddings, wall 29 s):
  ```sh
  cd <runner>/kiln/packs && bash scripts/conv-se.sh outdoors qa-outdoors-se      # convert + validate
  # (no empty-title rows)
  bash scripts/build.sh qa-outdoors-se "The Great Outdoors Stack Exchange Q&A" work/qa-outdoors-se/manifest.json work/qa-outdoors-se/*.jsonl
  ```
  Scripts: rnd/kiln/packs/wave1-scripts/ (copied to the mini as <runner>/kiln/packs/scripts/). build.sh = `cd <runner>/kiln/packs/builder && BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out <id>.sqlite --manifest <manifest> --name "<name>" --shards <jsonl...>` with the T-K2 builder (scripts sha = wt/packs).
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4 (jev F0 on V-para 34 absent items + v0.2 by category).
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): share v0.2 0.116 / v0.1 0.046, gold unchanged → **default-eligible** by rule; but 0 slots on its matching v0.2 items (danger*/travel-practical) and 17 elsewhere: passes without bringing in-topic content on these sets.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.52** (0.46–0.57), above_min 0.38 / without pack raw **0.48** (0.42–0.54), above_min 0.34; paired Δ +0.035 raw (95 % CI -0.021…+0.099), +0.045 above_min; items better/worse with the pack 10/6; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 11/20 items (23/25 kept passages); the fact's source article kept on 9/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.565 vs without 0.528, Δ +0.036 (−0.018…+0.096); deep with pack vs 4B with pack +0.046 (+0.002…+0.088); pack passages kept on 13/20 items; win 0/20. Dev numbers, agent-written gold; the pack's effect on the deep tier is not decided (CI through 0).
## Category gaps
- North-America/Europe-centred gear and regulation answers; first-aid answers are lay advice (pair with boar-firstaid-en); 2024-04 snapshot.
## Curation notes
- Citation string repeats the question URL (in the label part and at the end of the attribution); long threads list up to 6 authors. Harmless, but a UI could shorten it.
- Fresher alternative: Kiwix 2026 ZIMs (O-K1) if the pack proves useful.
- Community answers are not reviewed; health/safety answers keep the "AI-reviewed, not clinically reviewed" caveat and should rank below PD/clinical sources.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/qa/qa-outdoors-se (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
