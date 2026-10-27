# DENSECHUNK-ST: does a two-stage chunk-level semantic path in format-2 packs bring the fact passage into the context, and does the shipped 4B then answer better, on the 180 public pack self-test items? (frozen 2026-10-13 08:4x, coordinator)

## Tags
Tags: none

## Question
Arm **X = packDense2** (engine setting, default off): for a format-2 pack that carries a `chunk_vecs` sidecar table (int8 bge-small vector per chunk, embedding text `title\nsection: text`, quantised like the builders), `WikiPack.searchDetailed` adds a semantic candidate list: stage 1 = the top-M articles by lead cosine (M = 50, from the existing `lead_vecs`), stage 2 = cosine over the chunk vectors of those articles only, top-K2 = 12 chunks at cos ≥ 0.55 (MIN_SEMANTIC_SIMILARITY), returned as "semantic" hits that enter `fuseRetrievalResults` (0.5/0.5) with the pack's keyword hits; named-title hits stay first. Packs without the sidecar are untouched; off = byte-identical. Control **C** = the same build with the setting off. Reader = the shipped 4B claim build (cut 7, kiln-local tree, greedy), kit = claim kit + the item's pack. Why this set: the 180 self-test items (20 per published pack, 9 packs, public, agent-written, dev) are pack-matched by construction — the fact's article and chunk are known per item (`in_pack_facts[].chunk_index`, `source.article_id`) — so the retrieval stage can be measured at the chunk level with n 180 and the quality stage with the local judge at 0 paid calls. DENSECHUNK D0 (10-12) showed the fact chunk in the pack's dense top-12 on 23/32 v0.2 in-pack items vs 17 lexical; the v0.2 subset was too small to decide.

## Fixed inputs
- Items: rnd/research/packs/selftest/<pack>.jsonl for the 9 published packs (180 items; public). Fact chunk per item = the pack chunk(s) named in `in_pack_facts` (article + chunk_index); fact article = `source.article_id`.
- Packs: the published wave-1/wave-2 files (sha256 as in their .sqlite.json) + a sidecar `chunk_vecs(chunk_id, scale, vec)` added to COPIES under shared-data/packs/v3proto/ (the published files are not modified). The claim kit's packs (boar-crypto, boar-wikivoyage-en) get the sidecar too from the DENSECHUNK D0 caches (shared-data/packs/work/densechunk/*.i8) so the no-harm check is meaningful.
- Engine: worktree wt/packs (T-K2 patch) + the packDense2 patch (differential test: off = identical hits on the 5 public v0.1 queries and the wave-1 check queries).
- Replay: the replay-crowd/replay-p4b pattern (engine retrieval, no LLM) on the 180 items with kit + the item's pack, OFF and ON; no-harm replays on v0.1 public (60) and v0.2 (110, script-only on blind) with the kit only (sidecars on crypto/wikivoyage).
- Judge for stage 2: local judge.v1 via the JUDGE2 shim (BOAR_EVAL_LIB) on the mini's llama-server with Qwen3.6-35B-A3B UD-Q2_K_XL, both orders; calibrated on qa-travel-se's 20 items against the existing Haiku rows (arms/packs/selftest-runs/st-qa-travel-se-cut7-s42.judgments.haiku55-low.jsonl): report the winner agreement and the ratio delta; Haiku re-score after the 10-19 reset if the verdict is LEVER.

## Power
expected_delta: +0.05 raw ratio on the 180 items (source: DENSECHUNK D0 chunk reach 23/32 vs 17 lexical ≈ +19 pp article reach; T-K4c: fact article in raw 13/20, kept 6/20 on qa-travel-se; SECTIONHIT: a shown fact is used right ≈ 4/7 → +6 pp of items answered right ≈ +0.03–0.06 raw)
n: 180 (9 packs × 20; per-pack n 20 reported as descriptive only)
seeds: 1 (the 4B desktop run is greedy/deterministic; the local judge is the noise source — calibration on 20 items vs Haiku)
mde: ≈ 0.03 raw at n 180 paired (item SD of the 4B on self-tests ≈ 0.20 → SE 0.015); the local judge's extra noise is measured by the calibration, not assumed
slice: n/a (the whole 180 is the slice; no judge call before the retrieval gate passes)
l1_futility: n/a (local judge is free; both orders on all 180 OFF and ON = 720 local calls)
reopen: CLOSED R30 DEEPRERANK (rerank of the pool) and the parked DENSECHUNK (pack format +213 MB): this arm adds candidates from a chunk-level sidecar through a two-stage path (lead top-50 → chunks) on the pack-matched set where the earlier arm had no power; it does not rerank the pool.
split: paired Δ by pack family (SE Q&A packs vs topic packs) — declared here; expected: larger on topic packs (long articles, fact outside the lead), smaller on SE packs (short question-shaped docs)

## Stages and rules
0. **Step 0, 0 judge calls (MacBook + mini embeddings only).** Build the sidecars (9 packs + 2 kit packs). D0: per item, the fact chunk's dense rank within its pack (full scan and within the two-stage candidate set) and the OFF baseline (fact chunk / fact article in raw top-6 and in kept, from a replay). Gate replay ON vs OFF on the 180:
   - **G1 reach:** items with a fact chunk in raw top-6 rise by **≥ 25 % relative** (e.g. OFF 90 → ON ≥ 113) AND items with the fact article in kept do not fall.
   - **G2 no-harm:** v0.1 public gold-in-kept and v0.2 resolvable gold-in-raw6/kept not lower with the sidecars on the kit packs; empty-kept not up; churn reported.
   - **G3 cost:** retrieval p50 ≤ 2 × OFF on the MacBook; the two-stage scan ≤ 300 ms per query on the largest pack (simplewiki 622k chunks) in node.
   All pass → stage 1; any FAIL → FAIL at step 0 (one declared variant: M 50 / K2 12 / floor 0.55).
1. Generation: 4B cut 7 on the MacBook, 180 items ON (OFF traces exist for the 7 wave-1 packs; wave-2 OFF generated too), kit + pack.
2. Local judge both orders on OFF and ON (720 calls on the mini); calibration on qa-travel-se vs Haiku first (winner agreement ≥ 0.75 on 20 items required to trust the sign; else the quality stage is "not decided locally" and waits for Haiku).
3. Verdict on the paired Δ raw (and above_min) over the 180: **LEVER** CI low > 0 and Δ ≥ +0.03; **SMALL** CI low > 0, Δ < 0.03; **NO** otherwise; "not decided at MDE 0.03" when |Δ| < 0.03 with CI through 0. LEVER → Haiku re-score after the 10-19 reset (360 calls) before any adoption statement; the pack-format decision (ship chunk_vecs: +~60 % size) goes to r4to with the measured numbers.

## Stop rules and budget
0 paid API calls. Haiku 0 until the reset. MacBook disk ≥ 8 GiB (sidecars ≈ 0.5 GB int8 for 1.3 M chunks; f32 caches deleted after quantisation); mini disk ≥ 25 GiB; the mini runs only the judge server (never two LLM servers); never restart Docker; never stop :8094.

## Outputs and exposure
arms/densechunk-st/{D0.md, GATE.md, DENSECHUNK-ST.md (verdict, cites this sha), tools/, aggregates/, packdense2.vs-dt512.patch + .sha256}; traces/judgments under arms/densechunk-st/runs/ (public items) and, for the v0.2 no-harm replay, under blind/bench-v02/runs-packs/ (script-only; one EXPOSURES row). QUEUE rows per stage.
