# boar-medlineplus-en (MedlinePlus health topics)
TL;DR: the 1,016 English MedlinePlus health-topic summaries (NLM public-domain text only), one doc per topic with aliases as redirects; 4.3 MB; built 2026-10-12 (T-K3); NOT in any kit; coverage/crowding pending T-K4; self-test scored 2026-10-13.

## What it is
- Source: MedlinePlus Health Topics XML, `mplus_topics_compressed_2026-10-10.zip` (4,775,535 B, sha256 807bd8bc4dbc8e96a3c0c9c7dc8c8c5bb5d2a130122c227e5e167c5aa3df5c8c; XML snapshot "10/10/2026 02:30:38"). 2,033 topics in the file, 1,016 English kept (1 without a summary).
- Converter: `convert.mjs medlineplus` (T-K1): text = `<full-summary>` + "Also called" + "See also" + "Topic groups". A.D.A.M. encyclopedia, ASHP drug pages and external `<site>` links are never read (validate.mjs fails any row mentioning them).
- Licence (meta and every row): "Public domain (NLM); courtesy of MedlinePlus from the National Library of Medicine". Attribution on every row: "Courtesy of MedlinePlus from the National Library of Medicine; <topic url>" (the NLM credit line).
- Example citation string (engine, query "what are the symptoms of a stroke"): `MedlinePlus — https://medlineplus.gov/stroke.html (Public domain (NLM); courtesy of MedlinePlus from the National Library of Medicine) — Courtesy of MedlinePlus from the National Library of Medicine; https://medlineplus.gov/stroke.html`.
## Format
- formatVersion 2, dims 384, embeddingModelSha256 ec38e8da…f514. Params: leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, fullTop 1000000, embedTop 0. `articles.source` = 10 (medlineplus) on every row.
- Counts: articles 1,016; chunks 3,042; indexed 3,042 (100 %); lead_vecs 1,016; redirects 1,988 (also-called + see-reference names); views 0 (no popularity prior).
- Size: 4,268,032 B (4.1 MiB). sha256 c9ac4dcfdae367d4502c3360bf0ffc9596d55290c0a49e0835aeedf990ba227a.
- meta keys: format, formatVersion, dims, embeddingModelSha256, sources, license, manifestSha256, name, articles, chunks, indexedChunks, dfMin, params, builtAt.
## Kit entry and build
- Not in any kit. Kit entry would be {"id":"boar-medlineplus-en","sha256":"c9ac4dcf…"}. Label "MedlinePlus" needs the T-K2 engine patch. Whether `medlineplus` joins `LAY_SOURCES` (ranking) is open (needs its own arm).
- Files: `$RUNNER_ROOT/shared-data/packs/wave1/` on the build host.
- Build (build host, Apple M4, wall 6 s; scripts in rnd/runner/packs/wave1-scripts/):
  ```sh
  node rnd/runner/packs/convert/convert.mjs medlineplus mplus_topics_compressed_2026-10-10.zip --out work/medlineplus-topics   # MacBook, T-K1
  bash scripts/build.sh boar-medlineplus-en "MedlinePlus health topics" work/medlineplus-topics/manifest.json work/medlineplus-topics/medlineplus-topics.jsonl
  ```
## Measured coverage
- V-para 34 absent items: verified 0/34, >=0.7 0, >=0.6 0 (coverage probe 2026-10-12: jev fact-in-text over 20 candidate chunks per item, deep-tier run s42).
- pending T-K4.
## Crowding
- T-K4a (2026-10-12, arms/packs/T-K4a.md): share v0.2 0.043 / v0.1 0.026, gold unchanged, p50 +9 ms → **default-eligible**.
## Quality
- Self-test score (2026-10-13; the 20 public self-test questions written from this pack's text; Haiku 5.5-low L1 judge, both answer orders; 4B claim build; dev): with pack raw **0.51** (0.44–0.57), above_min 0.38 / without pack raw **0.51** (0.44–0.57), above_min 0.38; paired Δ +0.002 raw (95 % CI -0.055…+0.044), +0.002 above_min; items better/worse with the pack 10/7; win/tie/loss vs the gold answer 0/0/20. Pack passages kept on 12/20 items (25/33 kept passages); the fact's source article kept on 11/20. Gold answers are agent-written from the same text: a development check, not comparable with benchmark numbers.
- Self-test, deep tier (Qwen3.6-35B-A3B + thinking 512, desktop, Haiku 5.5-low N=4 both orders, 2026-10-13): with pack 0.523 vs without 0.572, Δ −0.049 (−0.104…−0.002); deep with pack vs 4B with pack +0.016 (−0.032…+0.068); pack passages kept on 13/20 items; win 0/20. Dev numbers, agent-written gold; the pack lowers the deep tier's score (−0.049, CI below 0; n 20).
## Category gaps
- Summaries are short overviews (≈ 3 chunks per topic): little dosing, first-aid steps or numbers; the detailed A.D.A.M. pages are excluded by licence (D-K5). English only (the Spanish half of the XML is skipped).
## Curation notes
- The topic URL appears twice in the citation (label part + credit line); the credit line itself is required.
- Some summaries end with the NIH institute name as its own paragraph (kept).
- Rebuild monthly-ish from the newest XML; keep the "AI-reviewed, not clinically reviewed" caveat.

## Published
- 2026-10-13 00:01: https://huggingface.co/datasets/r4topunk/boar-packs/tree/main/topics/boar-medlineplus-en (sqlite + .sqlite.json + README + LICENSE + selftest.jsonl; root README "Wave 1" section, commit 103f7bfa).
