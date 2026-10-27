# PR note: the lite profile (X2b + SOURCEGROUP + WARN), for the wiring PR after 10-20

Base: the PR branch wt/pr1 8ac9eb7a (cut 7 + NUMGUARD r3 + HEALTHGAP r2). Apply arms/liteprofile/tools/liteprofile.series/ in order, one commit per patch, or apply tools/liteprofile.patch e7e5f156… as one diff. Every behaviour is off by default, and with every flag off the engine output is byte-identical to the branch.

## Order
1. `01-headpass-x2b.patch` (599491f1): src/models/settings.ts, src/rag/{denseCandidates.ts (new), packs.ts, retrieve.ts, wikiPack.ts} + 4 rag tests, src/routing/{answer.ts, answerService.ts, answer.headpassx2.test.ts (new)}
2. `02-sourcegroup.patch` (d8e8f1be): src/routing/{sourceGroups.ts (new), sourceGroups.test.ts (new), answer.ts, events.ts, answerReducer.ts, answer.test.ts}
3. `03-warn.patch` (c39df3ba): src/routing/{warn.ts (new), warn.test.ts (new), testing/warn-goldens.json (new), answer.ts, events.ts, answerReducer.ts, answer.test.ts}. The done event also carries sourceGroups (the one line merged with 02).
4. `04-lite-model.patch` (466ce13c): src/models/{manifest.ts, manifest.test.ts}, src/routing/defaultModel.test.ts. One catalog entry plus 3 tests; no logic change.

## Commit paragraphs
**1. rag: append the retrieved pack article's neighbour chunks and budgeted dense candidates (settings.packHeadPass "a2" + packDense2 "append-budget", off by default)**
A user-installed pack often holds the fact one chunk away from the passage that retrieval found, or in a chunk that keyword search misses. With packHeadPass "a2", the answer appends the neighbour chunks of the first retrieved pack passage after the keep step. With packDense2 "append-budget", it also appends the pack's two-stage chunk-vector candidates, when the pack carries a chunk_vecs sidecar. Appended chunks go in order (neighbours first, then dense) and are kept only while the added prompt stays within HEADPASS_BUDGET_TOKENS (600). The retrieved list, the keep step and kit-only questions are unchanged, and a pack without chunk_vecs runs the neighbour pass only. Measured on the 180 pack self-tests (dev): the fact chunk reaches the context on 102/180 instead of 35, +0.066 (+0.043…+0.091) on the 4B (Opus), and +0.071 (+0.048…+0.094) on Qwen3-1.7B (Haiku), at +413 prompt tokens p50. Both settings absent = the current path. Strip the eval-only BOAR_PROMPT_DUMP hook in answer.ts (dumpPrompt, `import("node:fs")`) before upstreaming.

**2. routing: group the final answer's sources by page (deps.groupSources, off by default)**
Retrieval numbers sources per passage, so one page often shows two or three times in the sources card. This happens in 36–50 % of answers with sources, and in 90 % once X2b appends neighbour chunks. sourceGroups.ts groups the final sources by page (the URL in the label, else the title), numbered by first appearance. It rewrites every [n] to its group's number. done and the result carry sourceGroups, with each group's passages, and the receipt adds sources:grouped:<before>-><after>. The sources event and result.sources stay per passage. Off = byte-identical. Full text, renderer contract and native port spec: arms/sourcegroup/PR-NOTE-sourcegroup.md.

**3. routing: show a health caution on health-shaped answers a model wrote (deps.warn, off by default)**
A model answer about health gets one caution in three tiers by grounding: no-source, beyond-source or sourced. It shows a warn event before generation and is settled by done.warn and warn:<tier>. On that turn the caution replaces the weak_sources warning and the uncited preface, and a turn that ends without a caution gets back the notice it held. Deterministic, card, decline, FACTS and calculator answers are never warned. Off = byte-identical. Full text, port lines and goldens: arms/warnspec/PR-NOTE-warn.md.

**4. models: catalog entry for Qwen3-1.7B Q4_K_M, the lite answer model (answerTier "default")**
Adds qwen3-1.7b-q4km (unsloth/Qwen3-1.7B-GGUF @ d7f544ee, 1,107,409,472 B, sha256 b139949c…, Apache-2.0, roles general + fast, chat template) after the 4B, so DEFAULT_ANSWER_MODEL stays the 4B and the setup set is unchanged. It is tiered "default" because that is how every lite run measured it: not compact, so no compact declines. Side effects to know: the setup wizard lists it as a second default-tier card; on a phone with <= 4.5 GB RAM it is held back like the 4B. Needs llama.cpp `--reasoning off` (hybrid-thinking model). The old test that pinned exactly one default is updated; 3 tests added (entry present and not required; a 1.11 GB model with the entry is not compact, without it it would be; low-RAM behaviour pinned).

## Turning the profile on (app side, in this order)
1. Renderers first: the warn event and done.warn (Android answerBridge and ChatAnswerOutcome have no warn field yet), and done.sourceGroups → SourceFootnotes. Then set deps.warn and deps.groupSources.
2. Lite model: the catalog entry is in 04 (answerTier "default", as measured). Choose it through the existing active-model pick or the setup answer-model step; start the engine with thinking off. A separate "lite" tier with its own RAM rule is still open (LITEPROFILE.md risks).
3. X2b: ship the packs in format v3 with chunk_vecs, then set packHeadPass "a2" + packDense2 "append-budget" for the lite tier once a phone prefill timing prices the +413 tokens.

## Verification (arms/liteprofile/patch/)
- tsc --noEmit clean (be/ and supabase/functions excluded, as on the branch). vitest src/routing: 33 files / 787 green. Full suite: 127 files / 1,578 green (before 04: 785 / 1,575; 04 adds 3 tests).
- `git apply --check tools/liteprofile.patch` clean on wt/pr1. The four series patches apply in order on a fresh git archive of 8ac9eb7a, and the result matches the tree's src.
- 0-LLM route replay with every flag off: 304/304 traces identical to wt/pr1 (64 probes, v0.1 60, 180 self-tests), with HEALTHGAP on and off. WARN on: 124/124 identical to the warn tree's ON traces.

- The eval-only BOAR_PROMPT_DUMP hook (dynamic import of node:fs) is no longer in 01 or anywhere in src. Prompt dumps in eval runs: the adapter's `--dump-prompts f.jsonl` (boar-eval adapters/desktop-node/runner/adapter.ts, wraps engine.generate; lines {itemId, messages|prompt, nPredict, enableThinking}; the old hook wrote {query, prompt}). The 0-LLM replay with flags off was not re-run after the hook removal (it was inert with the env unset).
