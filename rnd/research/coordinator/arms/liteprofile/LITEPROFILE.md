# LITEPROFILE: the post-10-20 lite profile as one patch series on the PR branch (2026-10-16, MacBook mac-cpu, 0 judge calls, 0 generation, 0 paid)

TL;DR: HEADPASS-X2b → SOURCEGROUP → WARN apply as one series on wt/pr1 8ac9eb7a (cut 7 + NUMGUARD r3 + HEALTHGAP r2). Every flag is off by default. tsc is clean, vitest src/routing 33 files / 787 green, the full suite 127 files / 1,578 green, and `git apply --check` of the combined patch on wt/pr1 is clean. With every flag off, the 0-LLM route replay matches wt/pr1 on 304/304 traces (64 probes + v0.1 60 + the 180 self-tests), with HEALTHGAP on and off. The engine has no "lite" switch. The profile = engine options + the app's existing answer-model choice + a catalog entry for the 1.7B.

## Series (tools/liteprofile.series/, SHA256SUMS; combined tools/liteprofile.patch e7e5f156…)
| # | piece | source patch | rebased file | changed lines vs source |
|---|---|---|---|---|
| 01 | HEADPASS-X2b | headpass-st/headpass-x2b.vs-cut7.patch be413d7d | 01-headpass-x2b.patch 599491f1 | eval-only BOAR_PROMPT_DUMP hook removed (2 hunks in answer.ts, 2026-10-16 13:00); otherwise offsets only |
| 02 | SOURCEGROUP | sourcegroup/tools/sourcegroup.patch c274ab6c | 02-sourcegroup.patch d8e8f1be | 0 (offsets +2/+8 in answer.ts) |
| 03 | WARN v2 | warnspec/tools/warn.patch 11294894 | 03-warn.patch c39df3ba | 1 hunk (below) |
| 04 | lite model | new | 04-lite-model.patch 466ce13c | catalog entry qwen3-1.7b-q4km (tier default) + 3 tests; updates one manifest test |
Tree: kiln-local/be-cut7-liteprofile (ARM pr1+liteprofile; git archive 8ac9eb7a + a local git with one commit per piece, patch/tree-log.txt; node_modules → wt/pr1/node_modules; be/ = the warn tree's eval adapter 55adc5ff, unchanged).

## Conflicts resolved (warn on top of sourcegroup; git apply --3way, tools/resolve_lp*.py)
- answer.ts import block: keep both imports (sourceGroups, then warn). Position only.
- answer.ts AnswerDeps: keep both fields, groupSources then warn. The shared `/**` opener went to the first block, so the warn block got its own `/**` back (tsc caught the missing opener).
- answer.ts finish() done event: warn's multi-line emit plus SOURCEGROUP's `...(sourceGroups ? { sourceGroups } : {})` after finalText. This is the only changed line vs warn.patch. warnOf() runs after grouping and reads the grouped text/cited. The tier depends only on whether sentences are cited, and renumbering keeps that, so the tier does not change.
- answerReducer.ts: AnswerState gets both fields (sourceGroups, warn), and the done case sets sourceGroups and then settles warn. Independent.
- answer.test.ts: both new describe blocks appended (SOURCEGROUP, then WARN). The shared closing `});` pair was restored between them.
- adapter-forward-opts.patch: already in the pr1 eval adapter (retrieve(q, k, o?) forwards options), so no action.

## Identity (0 LLM; tools/run_lp_replay.sh + compare_lp.py; aggregates/lp-identity.json)
- Stub engine (healthgap/tools/mk_replay_stub.py), live detector :8094 (not restarted), no llama-server started. Pristine wt/pr1 = the scratch pr1tree (src = wt/pr1).
- Flags off, liteprofile vs pr1: probes 64/64, v0.1 60/60, 180 self-tests 180/180, with HEALTHGAP=1 and with it unset. The whole trace matches once run/time fields are dropped. 0 warn:/sources:grouped/headpass: codes. The pr1 reference also matches the warnspec pr1 traces from 02:38 (304/304), so there was no drift.
- Composition smoke, WARN=1 on this tree vs the warn tree's ON traces: probes 64/64 and v0.1 60/60 identical (h21, n12, vit-hlt-003; lan-hlt-002/003, vit-sci-001, vit-hlt-003), so warn is unchanged by the stack under it. aggregates/lp-warnon-vs-warntree.json.

## Profile table
| piece | flag (default) | what it changes when on | what the app/wiring PR must do | measured (dev data) |
|---|---|---|---|---|
| X2b | settings.packHeadPass "a2" + settings.packDense2 "append-budget" (both absent = off) | appends the retrieved article's neighbour chunks + dense chunk-vector candidates after the keep step, within HEADPASS_BUDGET_TOKENS 600 | packs in format v3 with the chunk_vecs sidecar (+≈ 60 % pack size; the published packs lack it, only shared-data/packs/v3proto has it); the app's embeddingEngine for the query; a prompt budget the device can prefill; turn on both settings for the lite tier | 4B: +0.066 (+0.043…+0.091) Opus vs S on the 180, fact in context 35 → 102. 1.7B (LITE5-180, Haiku): +0.071 (+0.048…+0.094), 1.7B+X2b vs 4B plain −0.007 (−0.031…+0.018); +413 prompt tokens p50 |
| SOURCEGROUP | deps.groupSources (off) | one source entry per page; [n] and cited renumbered; done/result.sourceGroups; code sources:grouped:a->b | the renderer: answerBridge passes done.sourceGroups to SourceFootnotes (one chip per group, passages in the expand); the eval adapter switch + trace.ts cited→titles before any ON run; native port spec in sourcegroup/PR-NOTE | duplicates in 36–50 % of answers with sources (cut 7), 90 % with X2b; replay on 572 traces: 0 duplicates after, 0 marker errors |
| WARN | deps.warn (off) | health caution in 3 tiers (no-source, beyond-source, sourced): warn event, done.warn, warn:<tier>; on that turn it holds back weak_sources and the uncited preface | a warn renderer first (Android drops the event today; on, the preface is the only notice it would remove); a strict native decoder must skip unknown events; the eval adapter has WARN=1 | goldens 676/676; probes 3, v0.1 4, the 180 36/model; LITESAFETY 1.7B: 6/7 health-shaped model answers warned |
| 1.7B fast tier | none in the engine: the active model (deps.getActiveModelId) or pickDefaultAnswerModel by catalog answerTier (default/compact; same rule in boar-ios DefaultModel.swift) | which GGUF answers | catalog entry now in 04 (answerTier "default"); the setup/model-list choice; the lite-tier question (see risks) | LITE2: 1.7B vs 4B −0.111 kit / −0.088 st20 plain; ≈ 2.5× faster, 56 tok/s decode, ≈ 2.3 GB RSS |
Eval-side only (boar-eval, not engine): lite2/tools/adapter-lite2.patch 6f53bc17 adds qwen3-1.7b-q4km to the adapter's model file table (lite/Qwen3-1.7B-Q4_K_M.gguf, sha b139949c…) and catalog (roles general + fast, answerTier "default"). The runs need BOAR_SERVER_EXTRA_ARGS="--reasoning off".

## Open risks
- X2b device cost is not measured: +413 prompt tokens p50 ≈ +8.7 s TTFT on the 4B at the X6's 47.6 tok/s prefill. On the 1.7B it is ≤ +5.8 s only under the assumed ≥ 1.5× prefill rate (LITE6). The budget clause needs a phone timing (BACKLOG row 15).
- RESOLVED (2026-10-16): the eval-only BOAR_PROMPT_DUMP hook (node:fs dynamic import) is stripped from 01. Nothing in src reads it. Eval tooling that sets BOAR_PROMPT_DUMP (headpass-st gen_chain*.sh, run_*_gen.sh, lite7) keeps working only on its old trees; on this tree use the adapter's `--dump-prompts` (EXTRA arg of the runner; format {itemId, messages|prompt, nPredict, enableThinking}). The dump is not consumed by any aggregate script in arms/ that I found, only written.
- The WARN lexicon and the p ≥ 0.05 line were fitted in-sample (probes, v0.1, the 180). Default-on waits for an out-of-sample set.
- SOURCEGROUP renumbering contract: grouped [n] index sourceGroups, not the per-passage sources event. A renderer that mixes the two mislabels chips, so turn on the flag only together with the renderer change, on both Android and native.
- 1.7B tier (PARTLY RESOLVED, 04): the catalog entry exists with answerTier "default", so isCompactModel() is false (the compact declines are off, as measured in LITE2–LITE7; test pins it). Remaining: (a) the entry is a second default-tier card in the setup wizard (ANSWER_MODELS), and rankAnswerModels() takes the first installed "default" candidate, so with both the 4B and the 1.7B installed the pick depends on candidate order; (b) on a <= 4.5 GB phone a "default"-tier model is held back like the 4B (tooBigForAutoPick/tooBigForLowRam), so the 1.7B is not auto-picked on 4 GB phones, where it would help most; a separate "lite" tier with its own RAM rule is the fix and is not measured; (c) the existing manifest test that pinned exactly one default was changed to list the 1.7B.
- Not measured together: all three ON at once on the 1.7B, judged. Only the pieces and the WARN-on composition were checked.

Files: tools/{liteprofile.series/ (01–04), liteprofile.patch(.sha256), run_lp_replay.sh, compare_lp.py, resolve_lp.py, resolve_lp2.py}; patch/{tsc, vitest-routing, vitest-full, apply-check-pr1, tree-log}.txt; runs/ (requests + traces); aggregates/{lp-identity, lp-warnon-vs-warntree}.json; PR-NOTE-liteprofile.md.
