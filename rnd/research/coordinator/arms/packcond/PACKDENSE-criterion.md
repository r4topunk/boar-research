# PACKDENSE (PACKCOND P4b): does a dense article router inside the installed pack bring the fact's article into the raw top-6, and does the deep tier then score higher on the in-pack subset? (frozen 2026-10-12 20:5x, coordinator)

## Tags
Tags: none

## Question
Arm **X = packDense**: for format-2 packs (`src/rag/wikiPack.ts` `searchDetailed`), a dense candidate path at the article level: the lead vector of every article of the pack (`lead_vecs`, 100 % coverage in boar-wikivoyage-en and boar-crypto, int8 bge-small, same model as the app) is compared with the question vector; the top-M articles with lead cosine >= floor that the named-title path did not already return contribute their best passage(s) for the question's stems (`articlePassages`), placed after the named hits and before the BM25 hits (M, floor and the passage count are fixed by D0 before the gate replay and written in P4B-DIAG.md; one declared variant runs the gate). Control **C = H** (dt512 tree: cut 6 + Qwen3.6-35B UD-Q2_K_XL + thinking 512; packGround off). Used for: the PACKCOND line's primary metric (D1, in-pack conditional ratio) on the v0.2 in-pack subset; the retrieval diagnosis of P4 step 0 says the loss is upstream of grounding (fact article outside the top-20 pool on 14/15 misses), and the format-2 search has no semantic candidate path (BM25 pool 80 + exact titles only; lead vectors are used only to keep BM25 candidates at cos >= 0.7).

## Fixed inputs
- Tree `wt/packcond` (979187fa + packground.vs-dt512.patch cb7f239a..., default off). The packDense patch adds `settings.packDense` (default off; off = byte-identical retrieval to dt512, differential test required) and the reason code `packdense:added-N` / `packdense:none`.
- Packs: boar-crypto ae9fbd2c..., boar-wikivoyage-en ff8595e3... (config.kit of the claim build).
- Replay: `arms/packcond/tools/replay-pg.ts` pattern (`--deep --gate rules --k 6 --pool 20 --tasks-from` the H v0.2 s42 traces); per-item outputs with query text stay under `blind/bench-v02/runs-packcond/` (v0.2) and `arms/packcond/replay/` (v0.1 public).
- Targets: the F0 article(s) per item from `aggregates/p4-diag.json` (H, n 32, field `f0_articles`), ids in `inpack-H-v02.ids`; control ids `arms/random20-v02.ids`; gold `boar-eval/bench/v0.2/gold/sources.json` (86 items) and `boar-eval/bench/v0.1/gold/sources.json` (39 items).
- Judge-stage control rows: H v0.2 s42 (Opus L2-H-1seed + Haiku); H s43 control rows (64 Opus) are generated when stage 3 runs at two seeds.
- Blind sets script-only (coordinator scripts and subagent scripts; never head/cat/tail/grep/sed/jq on blind files); one EXPOSURES.md row per replay pass and per judge pass.

## Power
expected_delta: +0.05 conditional floor-adj on the in-pack subset (source: P1 buckets pooled H+K: not-retrieved 10/64, dropped-by-grounding 15/64; P4-GATE: 15/32 H items with the F0 article outside raw, 14 outside the top-20 pool; a recovered and kept article moves an item from the absent/wrong ratio ~0.40 toward used-right ~0.70: 5 items x 0.3 / 32 ~ +0.05. Unconditional on the 110 ~ +0.015, below the MDE: the unconditional number is reported, not decided)
n: 32 (in-pack H v0.2 subset; generation on all 110 so `arm.sh precheck` and the unconditional ratio are reported)
seeds: 2 (s42 + s43; the s43 control needs 64 Opus calls)
mde: ~0.046 at n 32, one seed (0.025 x sqrt(110/32)); ~0.033 at two seeds. The arm decides only at two seeds; a one-seed conditional delta < 0.046 is not a result.
slice: random20-v02.ids (6 of its 20 ids are in-pack: the slice is the no-harm and precheck stage, never the decision)
l1_futility: stop only if Haiku delta <= 0 AND h2h <= control; any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: CLOSED R3 NAMEDSLOT (4B; reorders the pool), R30 DEEPRERANK (reranks the pool), R31 DEEPITER (second query after thinking), R32 DEEPCOV-FB (another pack as fallback). New mechanism: candidates are ADDED to the pool from the installed pack through a path the format-2 search does not have (dense, article level, 0 LLM); nothing is reordered, reranked, re-queried, and no pack is added.
split: paired delta by the P1 stage bucket of the control item (not-retrieved | dropped-by-grounding | retrieved-not-used | used-wrong | used-right); expected: the gain sits on not-retrieved, ~0 on used-right and used-wrong.

## Stages and rules
0. **Step 0, 0 judge calls, MacBook only.**
   - D0 diagnostic (no pass/fail): per target article of the 32 in-pack items, the 20 control items and the gold items whose title resolves in an installed pack: named by the question (titlesInQuestion share), BM25 rank of its best chunk at pool 80 / 400 / 2000 (perArticle 1), best-chunk coverage vs the question stems, lead cosine and its rank among all articles of the pack, in raw top-6 (engine), in pool-20. Headroom table for the 15 class-(a) items: how many would enter with M = 1 / 3 / 5 at floors 0.50 / 0.55 / 0.60, and how many gold articles already in raw would be displaced. D0 fixes M, floor and passages-per-article; they are written in P4B-DIAG.md before the gate replay.
   - Gate replay (the declared variant, once; packGround off):
     - **G1 recall:** F0 article in the engine's raw top-6 on **>= 22/32** in-pack H items (baseline 17/32, same replay with the setting off).
     - **G2 kept:** F0 article in the kept sources (after compressContext + grounding) on **>= 14/32** (baseline 11/32). G1 pass with G2 fail = retrieval-only lever: reported, no judge stage; a grounding follow-up needs its own criterion.
     - **G3 no-harm:** v0.2 gold (86): gold article in raw top-6 >= baseline and in kept >= baseline - 1; v0.1 public gold (39): gold in kept >= baseline - 1; empty kept over the 110 v0.2 items <= baseline; random20-v02 kept lists changed <= 10/20 (churn is reported; harm is measured by the gold rules).
     - **G4 cost:** replay retrieve() p50 <= 2 x baseline on the MacBook; the full lead scan <= 150 ms per pack (34k articles, node).
   - All four pass -> stage 1. Any FAIL -> **FAIL at step 0** (no second variant after the declaration).
1. Smoke on the mini (3 in-pack ids, s42): infra gate (deep-thinking on 3/3, 0 errors, non-empty answers, `packdense:added-N` on >= 1/3, RSS unchanged). Stop on FAIL-INFRA.
2. L1 slice random20-v02 (Haiku 5.5-low N=4, both orders) vs the H s42 Haiku rows, after `arm.sh precheck` >= 20 % changed input on the 110 (kept titles or `packdense:` marker). Rule above.
3. Full 110 at s42 and s43 (Haiku vs H on the 110); L2 Opus N=4 on the 32 in-pack ids at both seeds (+ the s43 control rows); conditional metric per D1 with CIs (common-mode 0.010); unconditional delta on the 110 reported next to it.
4. Verdict (strict, on the two-seed conditional paired delta): **LEVER** CI low > 0 and delta >= +0.03; **SMALL** CI low > 0 and delta < +0.03; **NO** otherwise; "not decided at MDE 0.033 (32, 2 seeds)" when |delta| < 0.033 with the CI through 0. One generation per seed and stage; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Step 0: MacBook only, 0 judge calls, no mini. Stages 1-3: one deep arm on the mini at a time; disk >= 25 GiB; swap <= 8 GB; never restart Docker; never stop the detector :8094. Judge calls: Haiku <= 40 (slice) + 220 (full); Opus <= 40 (slice) + 128 (32 ids x 2 seeds x 2 orders) + 64 (s43 control) = 232; the week of 10-12 has 56 Opus left, so L2 waits for Mon 10-19 unless the loop's ledger says otherwise.

## Outputs and exposure
`arms/packcond/P4B-DIAG.md` (D0; declares M / floor / passages), `P4B-GATE.md` (G1-G4), `PACKDENSE.md` (verdict, cites this sha), `aggregates/p4b-*.json`, `tools/`, `packdense.vs-dt512.patch` + `.sha256`; traces and judgments under the blind runs dir; one EXPOSURES.md row per pass plus the QUEUE entry.
