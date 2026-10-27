# COVERAGE-MATRIX criterion (frozen 2026-10-21 before any generation; MEASUREMENT, no pass/fail clause)

TL;DR: the knowledge-pack thesis "coverage x quality" as one table: tier (Qwen3-1.7B, Gemma 4 E2B engine sampler, Qwen3-4B-Instruct-2507 Q4_K_M) x pack set (K0, K3, KA = A-union) on the 80 candidate-pack self-tests, plus a no-harm check of KA vs K0 for the 1.7B on MAIN 97. Reuses every existing trace and judgment; generates only the 6 missing cells. Changes no verdict, product default or persona-map decision by itself.

## 1. Sets (dev only)
- cand80.ids (sha256 3e9f9beb10c5d801e73e7618d118e0d92b09d976cca83a85ea46f1ced91a1376) = gemma4-e2b/packs/cand80.ids: the 80 st-boar-{simplewiki-en,factbook,medlineplus-en,firstaid-en} self-tests (selftest-180, dev). They are written from the packs, so every in-pack number is an UPPER BOUND for on-topic use, not casual traffic.
- main-97.ids (sha256 9664d81fdf182603617d31d75b34eaa8fcb1eeb5f0fa87e68352e1fe09d2a462) = lp-screens/main-97.ids (v0.1 57 + cooking-se 20 + money-se 20, dev). Never bench/v0.4, blind/ or rnd/veil.

## 2. Pack sets (pinned in the requests' config.kit; seed 42 in every request)
- K0 = claim kit (boar-crypto ae9fbd2c, boar-wikivoyage-en ff8595e3). K3 = K0 + boar-simplewiki-en 99bcec30, boar-factbook 4ce447e8, boar-medlineplus-en e805ccea, boar-firstaid-en 0a7dffa6 (v3proto files with chunk_vecs sidecars, as LITEPACKS).
- **KA (A-union, PERSONA-MAP-v1-draft §A∪)** = K3 with boar-simplewiki-en replaced in place by boar-visa-en (wave4, d1dd0ffb58a8e4f9b50a6a21cb164bdb314a7181eb2803c952db21e21359ad20): crypto, wikivoyage, visa, factbook, medlineplus, firstaid. NIST excluded. Built by tools/mk_ka_req.py (sha256 47cab4c216899bdf6caa3894a320e6abbf9b5858020e7aa3faef8035dc2b9e4f) from the LITEPACKS K3 requests (only runId and the one kit entry change): req/lp-KA-v01 a06554b596b965b2, lp-KA-cm b7d9ce31a85a54d2, lp-KA-st 80dab49fbe230d16.
- Deviation (logged): the persona-a-union candidate MANIFEST pins the wave1/wave2 files of factbook, medlineplus and firstaid (same content, no chunk_vecs sidecar); KA uses the v3proto files K3 uses, so KA - K3 isolates composition (simplewiki out, visa in) and not file format. visa, like wikivoyage and crypto, has no chunk_vecs sidecar. No area tiles (the self-tests and MAIN carry no device location).
- boar-visa-en lives only in shared-data/packs/wave4, which the runner's BOAR_EVAL_PACK_DIRS does not list: kadirs.patch (sha256 130b43428dbc5d25122201cf73b793b670e8ddf7238f88b98333176833cfcf39) appends wave4 LAST to the adapter's PACK_DIRS (every other pack resolves exactly as before; sha-checked by the adapter).

## 3. Cells (U = agg_run U; tools/matrix_report.py)
Existing (0 calls): 1.7B K0 mini = null-cal/control poolctl-K0-st180-s42 (deterministic mini control); 1.7B K0/K3 MacBook = LITEPACKS (gemma4-e2b/packs/aggregates/q17-lp-K{0,3}-cand80.json); Gemma K0/K3 = GEMMA-PACKS; MAIN 1.7B K0 = lp-screens/control lpctl-K0-main-s42 (mini).
New (mini only, tools/run_cell.sh via tools/run_matrix.sh, OUT_BASE=coverage-matrix):
| # | cell | arm dir | patch (sha256) |
|---|---|---|---|
| 1 | 1.7B KA cand80 | q17 | kadirs.patch |
| 2 | 1.7B KA MAIN 97 | q17 | kadirs.patch |
| 3 | Gemma KA cand80 | gemma | gemma-ka.patch = gemma4-e2b-engsamp.patch + kadirs.patch (06232d840045e27e001db3b20d87525b7e3194dba0a8f42aadf486c16a974b4c) |
| 4 | 4B K0 cand80 | q4b | gemma4-e2b/vs4b-engsamp.patch (485feceaec4b37d2aa21d64129c1e92716a4e479c97f4f82e235e954213c1c7b) |
| 5 | 4B K3 cand80 | q4b | vs4b-engsamp.patch |
| 6 | 4B KA cand80 | q4b | q4b-ka.patch = vs4b-engsamp.patch + kadirs.patch (7119badde980210d48f10cc0746cd136cdf096143ba2f90eac6297c78fc748e4) |
The 4B and Gemma are weight-only swaps behind the 1.7B id (compact tier, prompts and declines stay at the lite tier), as GEMMA-VS-4B / GEMMA-PACKS. Base tree <runner>/kiln/be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d, adapter d53c1487), llama-server b11010 CPU -t 4, --reasoning off, LITEDECLINE_OFF=5, mini slot lock (2 jobs).
Tools: run_cell.sh d8fa6b6fd7fc2073 (= gemma4-e2b/tools/run_pool_k.sh + KA, mkreq_cm.py, GEN_ONLY, reuse built after generation, cell-level cap), mkreq_cm.py b3e4ab422fad8359, merge_reuse.py aff4e359d276942a, reuse_pool.txt 02bc1200d91638a6, run_matrix.sh 951c90f66a44d200, matrix_report.py 230b7b58d86da686.

## 4. Judge and budget
Haiku 5.5-low (judge.v1-low) via deepthink/tools/shard_judge.sh, N = 4 shards, both orders; only answers not byte-identical to an already judged answer of the same item (reuse pool tools/reuse_pool.txt, then the matrix's own aggregates). Judging is serialized in the priority order 1..6 of §3; a cell is judged in full or not at all: if spent + its planned calls > cap it is not judged and reported pending (no subsetting); later cells are still tried.
calls_cap: Haiku 700 / Opus 0
opus_clause: none
0 paid API, 0 Opus, no phone, no maintainer contact.

## 5. Sanity (a cell is void and rerun once if violated)
rows = ids (80 or 97), 0 error rows; model.sha256 per tier (1.7B b139949c, Gemma 740185b2, 4B 3605803b) on every live trace; 0 reasoning tokens; KA traces carry the 6-pack KA kit.

## 6. Reported (tools/matrix_report.py; B 2000, seed 11, paired item bootstrap, CI = sorted[50], sorted[1949])
Per cell on all80 and the slices simplewiki20, on60 (factbook + medlineplus + firstaid, the slice where K3 and KA hold the same pack), factbook20, medlineplus20, firstaid20: U with CI, CE-unwarned count and rate, CE, declines, warned, refused R, prompt tokens (mean, p50, live items), answer tokens, mini wall (totalMs mean, p50; host listed; 2-slot contention included). Thermal: no sensor on the mini path; wall is the only latency/heat proxy.
Deltas: dU per cell vs its tier's K0 (same host: 1.7B K3 vs MacBook K0, 1.7B KA vs mini K0); KA - K3 per tier; tier gaps at each pack set; pack-gain DiD vs the 1.7B; dCEu rate vs K0. MAIN: 1.7B KA - K0 dU and dCEu rate.

## 7. Reading rules (pre-registered)
1. dU per cell: CI low > 0 -> "the set helps tier T on the pack-matched self-tests (upper bound)"; CI high < 0 -> "hurts"; else "no measurable change".
2. A-union vs K3 per tier (all80): CI low > 0 -> "KA beats K3"; CI high < 0 -> "K3 beats KA"; else "no measurable difference". Expected mechanics stated before the run: KA lacks simplewiki, so the simplewiki20 slice is off-pack under KA; on60 is the like-for-like slice (crowding by simplewiki vs none). For the 1.7B the KA - K3 difference crosses hosts (KA mini, K3 MacBook; the mini vs MacBook 1.7B K0 gap on cand80 is -0.013, reported beside it) and is read with that caveat.
3. MAIN no-harm (1.7B KA - K0, 97, same host): CI high < 0 -> "harm"; CI low >= -0.03 -> "no harm shown"; else "inconclusive". dCEu reported beside it (LITEPACKS CE clause +0.02 quoted, not a gate).
4. Tier gaps and DiD are indicative (one seed; the SEEDVAR one-seed rule: a one-seed delta below 0.05 is not robust even with a CI excluding 0).
5. Every in-pack number is an upper bound (pack-written self-tests). One seed (42). Haiku-low compresses gaps (L1-PROTOCOL addendum).

## Budget
Amendment 1 (2026-10-21 03:46, format only, after generation of cells 1 and 5, before any judge call): the judge preflight (_lib/preflight.py) reads calls_cap only from a block headed "## Budget"; §4's cap is restated here unchanged. Original frozen text: sha256 dfc84677... (rnd ea5f8290).
calls_cap: Haiku 700 / Opus 0
opus_clause: none
