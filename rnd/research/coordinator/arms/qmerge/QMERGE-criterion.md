# QMERGE step 0: does merging the engine query's and the 4B-rewritten query's retrieval results before the keep step put the fact chunk in the KEPT sources more often on the 180 public self-tests, without displacing kept facts? (frozen 2026-10-16 before any patch run or replay; 0 judge / 0 paid; public items only)

## Tags
Tags: probe
Ruleset: 30

## Question
Reopen named by QWRITE (arms/qwrite/QWRITE-STEP0.md, CLOSED R95): the rewritten query alone loses reach (top-8 69 -> 67) but OFF top-8 OR QW top-8 = 87/180 (+18). If the engine runs retrieve() for both queries and merges the two candidate lists before the keep step, is the fact chunk kept more often? PASS -> the judged stage below is declared for the next tick (not run here). FAIL -> close (CLOSED row, "step 0 FAIL").

## Fixed inputs
- Engine tree = kiln-local/be-cut7-qmerge = wt/pr1 HEAD 8ac9eb7a (git archive: src, assets, locales, modules, package.json, tsconfig.json) + tools/qmerge.patch (sha in tools/qmerge.patch.sha256). ARM pr1+qmerge.
- Patch (answer.ts only): optional deps.queryMerge = { rewrite(question: string): Promise<string | null> }. Absent -> code path untouched (OFF byte-identical). Present, on the single-pass retrieve (not multipass, not reuseSources): rw = await rewrite(req.query); if rw is empty or equals searchQuery (trim + lower-case + collapsed whitespace) nothing changes; else raw2 = deps.retrieve(rw, same k) and raw = [...raw, ...raw2 not already in raw], de-duplicated by chunkId and then by dedupeArticleCopies (src/rag/dedupe.ts). No truncation: each retrieve keeps its own k; the existing keep step (isSubstantive, pinned identifiers, compressContext(matchQuery, raw, same work budget), grounding / health-strict filter) decides what is kept, ranking against the engine's own matchQuery. A failing rewrite or second retrieve = OFF. Reason codes qmerge:candidates:<n> (merged list length) and qmerge:kept-from-rewrite:<m> (kept sources that came only from the rewrite list).
- Rewrites (180) = arms/qwrite/runs/qmap.json as frozen in QWRITE (177 items; the 3 gate fallbacks are absent = the rewrite is skipped, item byte-identical). No new generation for the 180.
- Rewrites (v0.1 60) = generated once with the QWRITE writer exactly (Qwen3-4B-Instruct-2507-Q4_K_M, llama-server b11010 CPU, MacBook, seed 42, temperature 0, max_tokens 24, the QWRITE prompt and cleaning). Gate per item: non-empty, <= 12 words, no number token in the query that occurs in the item's rubric / reference text and not in the question. Failing items fall back (absent). Kill if > 6/60 fail.
- Replay = tools/replay-qm.ts = arms/qwrite/tools/replay-qw.ts + (a) mode "qm" sets deps.queryMerge with rewrite = the item's map entry (absent -> null); the replay does not touch the query itself; (b) deps.emergencyScore = the adapter's mmbert detector client against the running :8094 detector (head sonar-mmbert-small-emergency-v3b.head.json, threshold EH.DETECTOR_THRESHOLD; never restarted); (c) deps.healthgap = true (the HEALTHGAP r2 replays' setting); numguard / warn unset. 0 LLM, generation stubbed. Modes off,qm,off. --gate search --k 6 --pool 8; packs as QWRITE run_replay.sh (claim kit + the item's published pack); v0.1 = claim kit only.
- Reach definitions = arms/qwrite/tools/compare_qw.py (fact chunks = in_pack_facts chunk_index over the article's chunks by start, item pack only); kept = fact chunk among the engine's kept sources (sources event); article kept = any kept chunk from the fact article.

## Gate (0 calls)
- G0 identity: off vs off2 byte-identical (raw, kept, promptSha, task, query, k, pool) on 180/180 and 60/60; ON byte-identical to OFF on every item where the rewrite was skipped (absent or equal to searchQuery). OFF kept-fact count on this tree is reported against the tk2off reference 35 (drift reported, not gating); the gates below use this tree's OFF.
- G1 fact chunk KEPT: kept(qm) >= kept(off) + 10.
- G2 fact article kept: art_kept(qm) >= art_kept(off).
- G3 displaced: items where OFF keeps a fact chunk and QM does not <= 3 (ids listed).
- G4 v0.1 (no fact labels): kept list identical where the rewrite is skipped (G0); gold-kept items (>= 1 gold source title of gold/sources.json among kept) qm >= off, and items losing gold-kept <= 1. Kept-diff share reported.
- Verdict: G0-G4 all pass -> "step 0 PASS"; else "step 0 FAIL" and the reopen closes.
- Reported, not gating: per pack, SE/topic, raw/merged candidates p50, kept slots, kept tokens, qmerge:kept-from-rewrite counts, empty kept, health-strict items, retrieval ms (two retrieves), gained/lost kept ids.

## Judged stage (declared, NOT run in this step; lane mac-gen)
In-engine rewrite (the 4B writer call before retrieve, same prompt, seed 42, temp 0) + queryMerge ON vs OFF on the 4B cut-7/pr1 path: random20 (seed 4242 over the 180) x 2 arms = Haiku 5.5-low 40 calls; continue to the 180 (Haiku, N = 4 shards) only if the random20 Δ >= 0; LEVER if the 180 ratio Δ >= +0.03 with CI low > 0; Opus only to confirm.

## Power
expected_delta: kept +5...+15 (union bound +18 in top-8; the keep budget cuts part of it)
n: 180 (+ 60 v0.1)
seeds: 1 (deterministic replay; writer temp 0)
mde: n/a (0-call gate, counts)
slice: all
l1_futility: n/a
reopen: a different merge rule (RRF interleave capped at k) only with a new criterion
split (declared): per pack; SE (100) / topic (80)

## Ceiling (RULE 29; 0 calls)
ceiling: HEADPASS split "fact newly present" +0.119 per item (Opus); 10 items ~ +0.007 pooled raw
bar_ceiling: below the bar alone; retrieval reach lever
launch: QWRITE reopen (CLOSED R95), coordinator 2026-10-16
transfer: engine option deps.queryMerge + an app-side 4B rewrite call (~0.6 s) if the judged stage passes

## Budget (RULE 29)
wall_cap: 1 h
calls_cap: Haiku 0 / Opus 0 in this step; paid 0
disk: floor 5 GiB free on the MacBook
kill_if: busy.sh busy, detector :8094 down, replay errors, missing rows, > 6 v0.1 writer fallbacks, tsc errors in the patched files, disk < 5 GiB
