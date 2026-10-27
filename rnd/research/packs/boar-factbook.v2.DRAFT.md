# boar-factbook v2 (CIA World Factbook, CC0 archive, shaped) — DRAFT, not published
TL;DR: same 261 Factbook entries and the same CC0 source as v1, re-chunked into short self-contained sentences that name the country ("Kyrgyzstan's capital is Bishkek."). 32,056 chunks, 23.5 MB. On the 20 self-tests the 1.7B answers right 0.50 vs 0.25 with v1 (Haiku, 2 seeds) and Opus U rises +0.12 (+0.03..+0.22). Status: **user-selected only** (not default-eligible). Upload needs r4to's OK (D-K4).

## What changed vs v1
- Source unchanged: github.com/factbook/factbook.json commit 144d6977 (snapshot 2026-09-11), the same 261 entries, aliases (774 redirects), page ids, urls and per-row attribution. Text read from the v1 build input (v3proto), not re-downloaded.
- Chunking rules (rule-based shaper, 0 LLM): R1 lead = one-line summary from the Key facts fields; R2 the Key facts block becomes 4 groups (capital/population/area; languages/religions/people; government/currency/economy; climate/internet code); R3 one chunk per Factbook field, fields under 12 words merged (at most 3 fields, 60 words); R4 each line becomes "<Country>'s <label> is <value>.", a yearly series becomes one sentence; R5 Background sentences without the country name get "<Country>: "; R6 section heading "<Country>: <group>", at most 120 words / 950 chars per chunk.
- No new facts (wording check): a fact checker over all 261 articles found 0 articles with a number or word not present in v1's text (part labels "(2)" excluded). The unshaped text through the same builder reproduces v1's chunks 10,543/10,543.
- Format: formatVersion 2, dims 384 (same embedding model ec38e8da...), plus a chunk_vecs sidecar (bge-small-int8-v1).
## Format and size
| | v1 (published) | v2 (shaped) |
|---|---|---|
| bytes | 11,624,448 (c5854353...; v3proto build 11,829,248) | 23,461,888 (+98 %; text 14.46 MB, chunk_vecs 12.44 MB) |
| sha256 | c585435354a413d04790882c4e2263f725b1024c067febad3f2a99783e663447 | 981f7b4bbfa4ddf38bd7e09a037be6f065e252a5ce9e23f2ea07e4ee3f422eaa |
| chunks | 10,543 | 32,056 (median 32 words, max 120) |
| articles / redirects | 261 / 774 | 261 / 774 |
meta name "CIA World Factbook (CC0 archive, data as of 2026-09-11), shaped (PACKSHAPE)", manifestSha256 f140835d..., builtAt 2026-10-23. Build: shaper 3 s + builder 3 s + chunk_vecs 181 s on a MacBook M1 Pro.
## Retrieval funnel (20 self-tests, SEFIX-124 search, kit K13; 0 LLM replays)
| | v1 | v2 |
|---|---|---|
| own article kept | 8/20 | **18/20** |
| fact chunk kept | 7/20 | **15/20** |
| quoted facts delivered | 11/58 | 27/58 |
Other packs' 120 self-tests: own article kept 74 = 74. Benchmark (MAIN 92 keyed): 42 facts delivered, 0 lost; factbook share of kept slots 0.5 to 2.3 %; 0 health losses.
## Self-test quality (Qwen3-1.7B Succinct, dev; gold agent-written from this pack's text)
| judge | v1 | v2 seed 42 | v2 seed 43 | v2 pooled |
|---|---|---|---|---|
| Haiku 5.5-low, correct-any | 5/20 (0.25) | 10/20 | 10/20 | **0.50** |
| Haiku, read right when the fact chunk is delivered | 4/7 | 9/15 | 10/15 | **19/30 (0.63)** |
| Opus judge.v1, U (both orders) | 0.316 | 0.421 | 0.451 | **0.436**; dU +0.121 (+0.030..+0.221) |
| Opus, correct (corr >= 4) per 100 | 25 | 55 | 45 | 50 |
| Opus, confident errors per 100 (unwarned) | 25 (4) | 15 (1) | 5 (0) | |
Opus better/tie/worse vs v1 (pooled) 10/8/2. One item (Austria vs Ireland) becomes a confident error at both seeds: same warned wrong claim as v1, fact not delivered in either version; the strict "no new confident error" clause therefore failed and the Opus confirmation reads NOT-CONFIRMED by rule while the quality clause passed (arms/packshape/V2-CONFIRM.md, criterion f17179a5).
## Default-eligible status
**User-selected only.** PACKPROOF rule: default-eligible by proof needs correct-any ON >= 0.60 (PROVES >= 0.75). v2 reaches 0.50 on Haiku (pooled, 40 answers) and 0.50 on Opus correct per 100: below 0.60 under both judges. v1's crowding flag (user-selected) also still applies until a crowding probe is re-run on v2.
## Licence
Unchanged from v1. LICENSE.md line: "Pack contents: CC0 1.0 (no rights reserved). No attribution is legally required; a courtesy note "Source: CIA World Factbook (archive)" is appreciated." Content is a US federal government work (public domain in the US, 17 U.S.C. §105) via the CC0 1.0 archive; pack format, build scripts and self-test questions CC BY 4.0 (BOAR). Per-row licence and attribution in article_meta, identical to v1.
## Publish (NOT run; needs r4to's explicit OK)
Staging first: copy the sqlite to a pack dir with its manifest (`boar-factbook.sqlite.json`, not written yet), and put this card's text in `rnd/research/packs/boar-factbook.md` (the script reads the card by id and checks sha + size). Publish as a new revision so the v1 files pinned by kits are never overwritten:
```sh
cd <workspace>/rnd/kiln/packs
.venv-hf/bin/python publish_pack.py boar-factbook --family topics --pack-dir <staging dir> --subdir v2 \
  --release-note "v2: same CC0 source, re-chunked into short country-named sentences; self-test right 0.50 vs 0.25 (1.7B)"     # dry run
# then the same command with --go, only after r4to's OK and a fresh dry run
```
## Caveats
One v1 seed; self-tests agent-written from the pack (dev, retrieval-favoured, never claim items); v1 run on the MacBook, v2 on the mini; n 20.
