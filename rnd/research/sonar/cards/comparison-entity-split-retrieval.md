# Comparison entity split: one retrieval per side, a guaranteed slot per side
TL;DR: Detect two-entity comparisons ("X or Y", "X vs Y", "X than Y", PT "X ou Y") deterministically, retrieve each side with its own sub-query (plus an exact-title preference), and reserve at least one context slot per side; on the real vital5 pack this recovers the missing side of a comparison that today's single-query search drops, which shows up on the phone as "The passages found don't support this answer".
Lane: Sonar · Status: tested; v2.1 passes the retrieval criteria + gate, judged quality Δ −0.0015 (−0.023…+0.021, 2×2 seeds; QUEUE #3b) · Priority: B (adoption = coordinator's call: no harm, no measurable quality)
Axes moved: retrieval ↑↑ (both sides in context: full-query replay 8/14 sides → per-entity 12/14 on 7 items, see exp-01b); quality ↑ on comparison/reasoning items (7 `comparison` + several `reasoning` items in bench-60; held-out O2 set is comparison-heavy); truthfulness ↑ (fewer memory answers about the missing side, which the citation check then strips → decline or cw); latency ≈ (+1 query embedding and 1–2 FTS queries per comparison, est. +100–300 ms on device, UNKNOWN; context budget unchanged because slots are reassigned, not added); resources 0; safety 0 (health route untouched: skip the split when `isHealthQuestion`).
Fits BOAR? Yes. Pure TypeScript in `src/rag/retrieve.ts` (no model, no native change, no download). Uses the bge-small already loaded and the packs already installed. Works offline, same cost on the 4 GB iPhone and Android. Format-2 packs already have a named-article round-robin "so each side of a comparison shows up" (`wikiPack.ts` `searchDetailed`), but it is gated by `namedMinShare = 0.5`, which by construction a side of a two-entity comparison rarely reaches; format-1 packs (wiki-vital5) have no named-article path at all.
Evidence:
- **Own replay, 2026-10-01** (`sonar/exp/01-comparison-entity-gate/`, read-only on `shared-data/packs/wiki-vital5.sqlite` sha `d3b87d56…`, app's bge-small sha `ec38e8da…`, the app's own `pure.ts` from build 611a4b9). It replays `searchPacks` (400 BM25 candidates → lexical top-12 with term coverage, semantic top-12 ≥ 0.55) → `gateByRelevance` ≥ 0.70 → `fuseRetrievalResults` top-6 on vital5 alone:
  - Every missing side **is in the pack** (Rhinoceros, Tiger, African elephant, Japan, Confucianism, Aconcagua, Quito…). It is a ranking problem, not coverage.
  - Full query: 8/14 sides reach the fused top-6. Lost: Rhinoceros (crowded out by Sumatran/Indian rhinoceros, Proboscidea), Tiger (Sea lion takes the slot), African elephant (5 rhinoceros chunks fill top-6), Japan (Tokyo instead), Confucianism (not even in the 400-candidate BM25 pool), Ethereum (not a vital5 article; crypto pack's job).
  - Lexical top-12 almost never contains either side: comparison words ("heavier", "densely populated") fail term coverage, so these questions run on the semantic list alone.
  - Per-entity sub-queries, union of top-3 per side: 12/14 sides. Remaining misses are fixable by the exact-title rule: "Germany" sub-query ranks Politics of/West/East Germany above Germany; "Mozi universal love" was a bad sub-query (plain "Mozi" works, cos 0.74).
  - Cosine of each side's lead vs the full question vs the side alone (`result.txt`): full query below the 0.70 gate for 5/18 sides, side-only sub-query below it for 1/18.
- **Device symptom** (`rnd/plumb/data/d10-611a4b9-…-o2off-o2ab82.jsonl`, iPhone 13, kit A): of 29 declines by the citation checks, ≥ 9 are two-entity comparisons whose `retrievedTitles` lack one side (vit-fa-005 only Elephant; vit-fa-021 only Lion; vit-fa-022 only Wikivoyage parks; vit-sci-002 Germany only; vit-o2b-029 Wikivoyage: Brazil only; vit-o2b-015 Pico da Neblina only; vit-hum-002 Mozi only; vit-o2b-026 no Ethereum; vit-o2b-030 no Lagoa dos Patos).
- Literature: decomposing comparison questions into single-entity sub-questions is the standard fix in multi-hop QA: DecompRC (Min, Zhong, Zettlemoyer, Hajishirzi, ACL 2019, https://arxiv.org/abs/1906.02916) treats "comparison" as its own decomposition type with one sub-question per entity; HotpotQA (Yang et al., EMNLP 2018, https://arxiv.org/abs/1809.09600) defines comparison questions as needing both entities' paragraphs. the post author's own fork does "LLM keyword expansion (dual seeds)" (`rnd/lantern/vitalik-thesis.md`, commit 337d334545), an LLM-side cousin of this. Our version needs no LLM call.
Test in boar-eval: arm `cmp-split` vs `main`, desktop-node adapter, greedy.
- Patch idea (in `retrieve.ts`):
  1. `comparisonSides(query)`: deterministic; returns 2 (max 3) noun phrases for patterns `A or B`, `A vs/versus B`, `A than B` (with a comparative before `than`), `difference(s) between A and B`, `compare A (and|with|to) B`, PT `A ou B`, `entre A e B`, `mais … que`. Strip articles/determiners. PT sides go through the existing `englishNamesIn` lexicon first. Return null when not confident (no split).
  2. If sides: run `retrieveOne(side, 3, …)` for each side (format-2 packs get `titles: [side]`, so the named path fires regardless of `namedMinShare`); in format-1/bundled results put a chunk whose title equals the side (or its singular / redirect) first.
  3. Merge: the best chunk of each side first, in question order, then the main query's fused list; dedupe; cut at the usual top-K. Context budget unchanged.
  4. Skip when `isHealthQuestion` (health keeps its strict route).
- Mode: **gate first** (deterministic, no judge), then full ×2 runs.
- Primary metric (deterministic, so not hit by the 0.031 run noise): **both-sides-in-context rate** = share of comparison items where the final prompt's sources include ≥ 1 chunk titled with each side (gold sides listed per item before the run; I can supply them for the bench-60 comparison items + the 30 o2b comparisons, which stay internal).
- Success criterion (frozen before any run):
  - (a) both-sides-in-context on comparison items rises by ≥ 30 pp vs main (replay predicts ~57% → ~85% of sides);
  - (b) on the deterministic desktop run of bench-60, citation-check declines (`all-citations-removed` + `uncited-with-sources`) on comparison items fall by ≥ 3 items;
  - (c) no non-comparison item changes its retrieved sources (the splitter must not fire on them: check on all 60; ≤ 1 false fire allowed, hand-checked);
  - (d) confident-wrong (judge+Jev band) on comparison items does not rise; safety unchanged;
  - (e) desktop retrieval time p50 +≤ 50 ms on comparison items.
  - Fail (a) or (c) → stop. Pass → device full mode ×2 (coordinator schedules).
Cost to try: ~4–6 h (splitter + merge in the adapter's engine copy, gold side lists, one gate run, bench-60 desktop ×2). No downloads. Risk: low; the change is confined to comparison-shaped questions.

## v2.1 judged (Kiln, 2026-10-02 02:20)

- Quality Δ −0.0015 vs main (MDE 0.038). That is consistent with the lane's exchange rate (RADAR: ≈ +0.003 per item whose key enters the prompt; v2.1 moved 2 items).
- The value is retrieval correctness (both sides shown 5/6 vs 3/6) with no harm. Judge it on that, or bundle it with larger knowledge changes.

## v1 result and v2 (2026-10-02, Sonar's reading of Kiln's runs; not the official verdict)

Runs: `boar-eval/runs/night-2026-10-01/ios-main-v5-t0` vs `ios-cmpsplit-v5-t0`. Both use kit A with vital5, temperature 0, desktop adapter on shared engine 0cfd4a77 (dirty).
- **Retrieval improved.** Two-sided comparisons (6 of the 7 `comparison` items; lan-cmp-003 has one side) with both sides in `retrieval.raw`: main **4/6 → cmpsplit 5/6**. Recovered: Grizzly bear, Japan and Germany (as Wikivoyage guides), Saltwater crocodile ranked first. Mozi vs Confucianism still misses: "Filial piety" came back instead of Confucianism.
- **The prompt did not improve.** Both sides in the sources shown before the answer: main **3/6 → cmpsplit 2/6**. cmpsplit lost Russia on lan-cmp-001, which main kept. Germany and Saltwater crocodile were retrieved and then dropped.
- **Mechanism** (trace reason codes + `compress.ts` @0cfd4a77):
  - A comparison is classified `task:lookup`, which gives retrieval k = 3 and `FAST_CONTEXT_TOKENS.lookup = 450`.
  - `compressContext` then drops any chunk whose best sentence scores below `RELATIVE_RELEVANCE_FLOOR = 0.5` × the top chunk's ("a distractor"). The second side's passage shares fewer words with the question, so it is cut.
  - Examples: vit-sci-002 `context:624->161` keeps only Wikivoyage: Japan; lan-cmp-001 `context:398->235` drops Wikivoyage: Russia.
  - `onSubject` adds `grounding:off-topic-dropped-1` on lan-cmp-005.
- key-in-context (`tools/key_in_context.py`): identical at raw and pre (31 / 24), 0 paired changes on the 52 keyed items. None of the comparison items' answer keys moved.
- So v1 fixed retrieval and then lost the gain in context assembly. Criterion (a), both sides in the prompt +30 pp, **fails**.

**v2 (small, same arm name + `-pin`):**
1. Pin the best chunk of each detected side through the existing `pinned` set in `answer.ts`. It is already used for identifier pages: `compressContext(matchQuery, raw, { tokenBudget, pinned })`, and pinned chunks bypass the relative floor and go first. A comparison then always keeps one passage per side within the 450-work budget.
2. Make sure `onSubject` keeps a chunk whose title equals a detected side.
3. For a non-travel comparison, resolve the side to the Wikipedia/vital5 article before the Wikivoyage guide: v1 put "Wikivoyage: Japan" / "Wikivoyage: Germany" ahead of vital5's Japan / Germany leads (the format-2 named path wins). This is consistent with `wikivoyage-lead-gate`.
4. Optional: raise the comparison's k from 3 to 4 (one per side + one shared), or the lookup budget only for comparisons. Measure the TTFT cost.

v2 criterion (frozen now, before any v2 run), on the same pair design (`-v5-t0`, deterministic):
- (a') both sides in the shown pre-answer sources on the 6 two-sided comparison items: ≥ 5/6 (main 3/6);
- (b) unchanged from v1;
- (c') key-in-context at `pre` on non-comparison items unchanged (0 lost);
- (d) unchanged from v1: confident-wrong not up, safety unchanged;
- (e') prompt tokens on comparison items within +150 of main.
- Kiln's v1 report (`boar-eval/reports/night-2026-10-01/cmpsplit.md`) also FAILS (e) latency: retrieval p50 +60 to +97 ms on the M4 for the 2 extra embeddings + searches. For v2, embed the two sides in one batch call, and search format-1 packs once with the union of the side vectors' candidates, to stay ≤ +50 ms.
- Added by the coordinator at queueing (QUEUE #3b, after #5): the slice is only 6 items, so the deterministic t0 pair decides, and the full boar-eval gate on all 72 items must also PASS.

## Engine note (2026-10-01, after queueing)

Queued as QUEUE.md #3, to run on the shared engine `upstream/main` 0cfd4a77, not 611a4b9. Checked read-only: `git diff 611a4b9 0cfd4a77` on `src/rag/{retrieve,pure,packs,wikiPack}.ts` only adds `dedupeArticleCopies` (cross-library copies) and a cache of rejected packs. `ANSWER_MIN_SIMILARITY` 0.70, `MAX_CHUNKS_PER_ARTICLE` 2, `NAMED_MIN_SHARE` 0.5, `semanticWeight` 0 and the fusion are unchanged, so the mechanism and the replay apply as written. Dedupe removes copies of the *same* article across libraries; it does not touch the subspecies crowding seen here (different titles).

## Details

Why the current pipeline loses a side:
1. One embedding for "Are rhinos bigger than elephants?" sits between the two topics and close to their *intersection* (subspecies, Proboscidea, mammoths). Near-duplicates of one side fill the semantic top-12, then `MAX_CHUNKS_PER_ARTICLE = 2` only caps per *title*, and subspecies have different titles.
2. The lexical list is empty for most comparisons: the comparative word ("heavier", "deeper", "densely populated") counts as a content term, so few lead paragraphs cover the required majority of terms.
3. Fusion normalizes to each list's max, so whatever topic dominates the semantic list dominates the fused top-6.
4. Format-2 named articles need ≥ 50% of the question's idf mass. In "X or Y + comparative", each side has roughly a third to a half. Lowering the share globally would re-open #34-style false names ("Darwin, Australia"), so the split should only relax it for detected sides.

Interactions:
- `tiny-cross-encoder-rerank` (B) reorders but cannot add a side that isn't in the candidate list; this card fixes recall first. If both are tried, run this one first.
- O2 (off-subject decline, NOT VALIDATED) failed partly on "one-sided comparatives". With both sides retrieved, an O2-like gate has a cleaner signal ("no source for side B" → say so for B only). Note for Compass.
- Format-2 duplicate chunks (Tornado Cash ×4, Bitcoin ×4, EIP-7251 ×3 in D10 `retrievedTitles`) are a separate issue: per-title cap vs section chunks. Candidate for a separate card (dedupe/diversity, MMR).

What would make it fail:
- The 1.5B still fails to compare even with both leads in context (then retrieval is fixed but quality doesn't move; the deterministic metric (a) still records the retrieval gain, and Anvil's prompt work takes over).
- The leads lack the compared attribute (weight of a tiger is in the body, not the vital5 intro). vital5 is intros only; for "how much heavier" the number may be missing. Check: the item-level outcome splits into "both sides retrieved, attribute present / absent".
- Splitter false fires on non-comparisons ("rock or roll", "either… or" in instructions, "more than 20 years"). Criterion (c) catches it.
- PT comparisons where the lexicon has no English name for a side (Lagoa dos Patos).

UNKNOWN:
- Device latency of 2 extra embeddings + FTS queries (bge-small query embed on iPhone 13 not measured separately; total retrievalMs is already ~1.0–1.5 s p50).
- The replay used vital5 alone; on the phone the bundled corpus and format-2 packs also compete for slots, so the real loss rate may differ (the device rows above show it's at least as bad).
