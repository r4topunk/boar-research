# TK2-FIX step 0: PASS (2026-10-16 02:5x; 0 LLM / 0 judge / 0 paid; public items; mac-cpu)

Criterion TK2FIX-step0-criterion.md sha f7193cc4… (frozen before the v2 replay). v2 = the T-K2 sources patch + one change in src/rag/packs.ts: the four T-K2 sources (stackexchange, medlineplus, factbook, simplewiki) keep the **bare title** in `RetrievedChunk.title` (what cut 7 read, since it mapped codes 9–12 to enwiki); the label ("Stack Exchange — url (licence) — credit") stays in `source` only. The title-lookup rule (codes 10–12 in topicSources; Stack Exchange excluded) is kept as T-K2 wrote it.

| cell (180 self-tests) | fact chunk kept | fact article kept | fact chunk raw6 | empty-kept | kept slots | own-pack slots | kept = cut 7 | prompt = cut 7 |
|---|---|---|---|---|---|---|---|---|
| cut 7 | 35 | 61 | 55 | 42 | 285 | 205 | — | — |
| tk2 (10-13 patch) | 42 | 67 | 66 | 47 | 280 | 214 | 128 | 77 |
| **tk2fix (v2)** | **44 (+9/−0)** | **71 (+10/−0)** | 66 | **42** | 305 | 239 | 146 | 147 |

Per pack, tk2fix vs cut 7 (fact chunk kept, kept slots): factbook 3 → 9, 34 → 44; simplewiki 11 → 13, 43 → 52; medlineplus 10 → 11, 33 → 34; the five SE packs and firstaid **identical to cut 7 (kept 100/100 items; bitcoin slots 34 = 34, the tk2 drop to 24 is gone)**.

**Gate (all PASS):**
- G0 infra: 3 cells × (180 + 60), repeat identity 180/180 and 60/60 each, 0 errors; the tk2 cell reproduces the 10-13 TK2-REPLAY ON kept lists 360/360 rows.
- G1 reach: fact chunk kept 44 ≥ 35 + 5.
- G2 own-pack drops with an unchanged raw list (the prefix mechanism): **0** (tk2: 17). Descriptive: 10 items lose ≥ 1 own-pack chunk vs cut 7, all on changed raw lists (title lookup replaced the candidate), all in medlineplus (018), factbook (009, 019), simplewiki (003, 006, 007, 009, 015, 019, 020); 0 of them lose the fact chunk; simplewiki-006 goes kept 1 → 0 (empty-kept total unchanged 42 → 42).
- G3 v0.1 no-harm (RULE 26): affected ids = none (route, k, codes identical 60/60); kept identical 60/60, prompt identical 60/60, gold kept 8 = 8, harm 0.
- **v0.2 kit no-harm SKIPPED**: its plaintext lives under blind/, off-limits to this runner (coordinator-only, scoped exception needed).

**Reading.** The 17 prefix drops were all mechanism 1; the bare title removes them without losing any of the title-lookup gain (and v2 reaches +2 fact chunks / +4 articles more than tk2, plausibly the same prefix effect on factbook/simplewiki pages; not traced item by item). The remaining retrieval change is the title-lookup rule only, confined to factbook / simplewiki / medlineplus (34 items differ in kept). Prompts change only where kept changes (147/180 identical; the `[n]` line stays the bare title). Reach is not quality: the HEADPASS conversion (0.11–0.17 per newly present chunk) projects ≈ +0.005…+0.008 on the 180 mean, so the next step is the judged re-score.

**Next (BACKLOG row 4):** smoke + Haiku L1 re-score of the 180 (tk2fix vs the cut 7 S rows; ≤ 360 Haiku, only the 34 changed-kept items need new generations) at the next META; cards' lines only if the engine ships v2. Related: the keep-rule quota callback fix (HEADPASS-ST) is independent; this replay ran the shipped keep step as is.

**Files:** tools/tk2.patch (+ .sha256 eb6072c2…; recovered by diffing kiln-local/be-0cfd4a77-cut7-tk2 vs -tk2off src, hunks identical to tk2-replay/tk2.vs-cut7.patch d2d09813…), tools/tk2fix.vs-tk2.patch 60156bcc…, tools/tk2fix.vs-cut7.patch 6cd09ca6… (tk2fix.patches.sha256), tools/run_fix.sh, tools/compare_fix.py; runs/{st-<pack>,v01-kit}.{cut7,tk2,tk2fix}.jsonl, runs/diff-items.jsonl, runs/run.log; aggregates/tk2fix-step0.json. Tree kiln-local/be-0cfd4a77-cut7-tk2fix (17 MB, node_modules symlinked). Precheck disk said 0.1 GiB; the 20 new replay cache keys took ≈ 0.5 GiB and were removed after the run (MacBook free 6.5 GiB). Not typechecked/vitest-run (one-line change in packHitToChunk; the replay executes it); do that before a PR.
