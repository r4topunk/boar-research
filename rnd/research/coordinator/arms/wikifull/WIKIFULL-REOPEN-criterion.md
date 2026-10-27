# WIKIFULL-REOPEN (T2 stages A/B): are the deep tier's absent V-para facts anywhere in English Wikipedia? (frozen 2026-10-12 23:0x, coordinator; r4to's download OK 2026-10-12 22:5x)

## Tags
Tags: blocker
<!-- 0-call jev gate over downloaded shards; no judge calls, no mini generation. `blocker` because it unblocks the kit-content decision (more Wikipedia vs other corpora) for the pack catalogue. -->

## Question
CLOSED R39 (WIKISECTION H5/H5b) closed "Wikipedia sections for on-topic absent items" on the top-100k pack and kept-source items only. T2 asks the full question: over all 34 V-para items whose primary LOSSMAP bucket is absent knowledge (arm H, dt512, s42), is the missing fact present, in its own words, anywhere in English Wikipedia (FineWiki Aug-2025, 15 shards boar-wiki-en-00…14 = the full article set; stage B = the 2026-10-01 dump for articles outside FineWiki)? Used for: reopening (or closing) Wikipedia as kit content for the bounty-style set, before any non-Wikipedia corpus is built.

## Fixed inputs
- Items: the 34 V-para absent items and, for context (dev), the 78 v0.2 absent items — as defined by `arms/wikifull/tools/wikifull_gate.py` (same item selection as A0).
- Gate tool: `wikifull_gate.py` with `--shard <path>` (A0 logic unchanged: q1 12-term OR, q2 kept title + 6 terms or top-4 AND, table chunks of the top-5 hit articles, Σ-idf rescore, top 40, jev has_fact ≥ 0.7, then jev quote_supports on p ≥ 0.7 = **verified**). Caches under blind/<set>/runs-dt512{,v02}/wikifull-cache.
- Shards: boar-wiki-en-00…14 from the HF dataset r4topunk/boar-packs (wiki/en/), sha256 per shared-data/packs/boar-wiki-en-XX.sqlite.json; downloaded one at a time to the MacBook (≈ 1.2 GB each; free ≥ 8 GiB kept), verified by sha, gated, deleted. Shard 07 = A0 (already counted).
- Pooling: an item counts once if any shard gives a verified hit (p ≥ 0.7 and quote_supports true); also report hits at ≥ 0.6 / ≥ 0.7 unverified and the "outside the top-100k pack" share.
- Script-only on blind; one EXPOSURES row for stage A (and one for B).

## Power
expected_delta: n/a (0-call deterministic gate; the decision is a count over 34 items; source of the thresholds: HANDOFF-2026-10-12 §4.3 and DEEP-RESEARCH-2026-10-12 T2)
n: 34 (V-para absent items; v0.2 78 reported as dev context)
seeds: n/a (jev is deterministic at temperature 0; cached)
mde: n/a — thresholds below are the rule
slice: n/a
l1_futility: n/a
reopen: CLOSED R39 WIKISECTION: new scope = ALL absent items (kept or not) over ALL of English Wikipedia (15 shards + the 2026-10-01 dump), not the top-100k pack and kept-source items only
split: by LOSSMAP group of the item (on-topic kept / off-topic kept / no kept source) — declared here; reported, never a rescue

## Stages and rules
A. Stage A (14 remaining shards, sequential on the MacBook; jev [usage detail removed] per shard per set; cap [usage detail removed] total): pooled verified hits over the 15 shards on the 34 V-para items:
   - **REOPEN ≥ 14/34**: Wikipedia content is reopened as kit content for the bounty-style set → a WIKI-ALL arm criterion (device-sized packaging question first: which articles, DEEPWIKI crowding rule).
   - **MARGINAL 7–13**: reported; stage B runs (articles outside FineWiki); no arm unless B lifts the pooled count to ≥ 14.
   - **CLOSE ≤ 6**: Wikipedia closed as kit content for V-para (CLOSED row); the pack catalogue goes to non-Wikipedia corpora first.
   The same counts on v0.2 (78) are reported for the pack catalogue (dev), never decided on.
B. Stage B (only if A is MARGINAL, or if r4to asks): enwiki 2026-10-01 dump streamed; the same gate over articles absent from FineWiki Aug-2025 (new or renamed pages); pooled with A under the same thresholds.
C. No judge calls at any stage. Thresholds are frozen; partial results (fewer than 15 shards) are not a verdict.

## Stop rules and budget
MacBook disk ≥ 8 GiB free at all times (one shard on disk at a time; delete after the gate); [usage detail removed]; no mini jobs. If a shard download fails its sha check, retry once, then skip and report the shard as missing (the verdict then names the covered shards).

## Outputs and exposure
`arms/wikifull/STAGE-A.md` (pooled table by shard and by LOSSMAP group; verdict), `aggregates/stageA-<set>-<shard>.json` (ids/titles/probabilities/counts only), `tools/stageA.sh` (download → sha → gate → delete loop); EXPOSURES row + QUEUE entry.
