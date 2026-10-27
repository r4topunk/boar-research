# SOURCEGROUP: one source entry per page in the engine output (2026-10-16 11:2x, MacBook, 0 judge calls, 0 generation, 0 paid)

TL;DR: duplicate pages are common: 36–50 % of answers with sources on the cut 7 / pr1 paths, and **90 %** once X2b appends neighbour chunks. The engine fix `deps.groupSources` (off by default) groups the final sources by page. It renumbers the [n] markers and keeps every passage under its group. Replayed post hoc on 572 public traces: 0 duplicates after grouping, 0 marker errors, the text otherwise identical, and byte-identical text whenever no page repeats.
Source: PHONEFAIL failure 4. Each passage is its own numbered source, and SourceFootnotes.tsx:36 draws one chip per passage.

## Step 1: baseline (tools/baseline.py, aggregates/sourcegroup-baseline.json)
Page key: the URL in the source label, else the title (trimmed, lowercased). Phone and native rows carry titles only.
| set | traces | with sources | with ≥ 1 dup | share | extra entries | mean entries before → after | dup + cited (shown in app) | answer cites 2 passages of 1 page |
|---|---|---|---|---|---|---|---|---|
| PHONEFAIL 27 (pr1, desktop) | 27 | 22 | 8 | 0.36 | 13 | 2.68 → 2.09 | 4 | 1 |
| v0.1 cut 7 (stack-off s42) | 60 | 32 | 15 | 0.47 | 23 | 2.44 → 1.72 | 9 | 2 |
| X6 phone cut 7 | 73 | 37 | 15 | 0.41 | 23 | 2.38 → 1.76 | 10 | 3 |
| X6 native app | 73 | 38 | 19 | 0.50 | 21 | 2.89 → 2.34 | 19 (markers) | 3 |
| 180 self-tests, 1.7B plain | 180 | 129 | 59 | 0.46 | 63 | 2.12 → 1.63 | 34 | 3 |
| 180 self-tests, 1.7B + X2b | 180 | 157 | 142 | 0.90 | 281 | 4.22 → 2.43 | 77 | 10 |
| 180 self-tests, 4B + X2b | 180 | 157 | 142 | 0.90 | 281 | 4.22 → 2.43 | 99 | 21 |
These match PHONEFAIL's counts (8/27, 13 extra; 15/37; 19/38). The worst case is st-qa-ethereum-se-006: 7 entries, 2 pages. **X2b, the pack line's lever, makes the problem worse**, because it appends chunks from the same article on purpose. Grouping should ship before X2b or together with it.

## Step 2: patch (tools/sourcegroup.patch, sha256 c274ab6cc94c1026704aa6aa071b35d51fa227ac447fb1dc02a40b5aaeafcf06)
Base: wt/pr1 8ac9eb7a src. `git apply --check` is clean on wt/pr1, and wt/pr1 itself is untouched. Tree: kiln-local/be-cut7-sourcegroup (ARM pr1+sourcegroup, 18 MB; adapter files are the be-cut7-warn ones, with no groupSources switch, because nothing here generates).
- New src/routing/sourceGroups.ts, pure: `pageKey`, `groupSources(text, sources, citedPassages?)` → {groups, text, cited, map, before, after}. Groups are numbered by the page's first appearance in the source list, so rank order is kept. Each in-range [k] becomes [map[k]]. Adjacent repeats ([1][1], [1] [1]) collapse into one marker, using the engine's dedupeCitations. Markers out of range stay as they are. When no page repeats, the text is returned untouched.
- answer.ts finish(): with `deps.groupSources === true` and ≥ 1 source, done and the result carry `sourceGroups`. When a page repeats, the code `sources:grouped:<before>-><after>` is added, the text is rewritten (finalText is set), and cited moves to group numbers. The instant excerpt's citedOverride is mapped too. The sources event and result.sources stay per passage, so deepen() still reuses every passage.
- events.ts: `done.sourceGroups?` and `AnswerResult.sourceGroups?`. answerReducer.ts: `state.sourceGroups` (taken from the tier that finished).
- Checks: tsc 0 errors. vitest src/routing **31 files / 720 green** (709 + 11 new). Full suite **121 / 1,495 green** (logs in patch/). New tests: 6 unit tests (sourceGroups.test.ts: URL dedupe; URL over title; title fallback; [1][3] → [1][2] and [1][2] → [1]; no-citation and no-repeat identity; excerpt citation mapping). 5 tests through answer() (answer.test.ts: OFF byte-identical to an absent flag, events and result; ON single pass with the receipt code, done and the reducer; uncited answer unchanged; no repeat → codes, text and cited identical; multi-pass deepen [1] [3] [2] → [1] [1] [2]).

## Step 3: post-hoc replay (tools/replay.mts over the tree's sourceGroups.ts; aggregates/sourcegroup-replay.json)
572 traces with ≥ 1 source (all 7 sets above; input aggregates/replay-input.jsonl). Results:
- 0 failures on every check. Duplicates after grouping: 0, and the group count equals the distinct pages.
- Every in-range marker maps to a group that holds the passage it cited: 0 bad of 461. The marker sequence is unchanged apart from renumbering, with 1 adjacent collapse (4B X2b).
- Text with the markers removed: identical in 572/572 traces.
- No page repeats → byte-identical text: 0 violations. That includes all 17 such v0.1 traces.
- Text changed in 164 traces, all of them renumbering only. Entries shown drop from 1,933 to 1,229 (−36 %).

## Reading
- Cosmetic for scores: 0 judge calls, and answer content does not change. It is a product fix that every renderer gets from one place. The renderer contract and the port spec are in PR-NOTE-sourcegroup.md.
- Not yet adopted. Adoption needs the wiring PR: the bridge passes `sourceGroups` to SourceFootnotes. Until then the flag stays off, because a renderer that reads the per-passage `sources` together with grouped [n] would mislabel chips.
- UNKNOWN: whether native numbers its markers into retrievedTitles. The replay assumes it does, and 54/54 native markers were in range. The eval adapter (trace.ts) maps cited onto sources and needs the same switch before an ON eval run.
Files: tools/{sets.py, baseline.py, dump.py, replay.mts, sourcegroup.patch(+.sha256)}, aggregates/{sourcegroup-baseline.json, sourcegroup-replay.json, replay-input.jsonl}, patch/{tsc.log, vitest-routing.log, vitest-full.log}, PR-NOTE-sourcegroup.md. Public sets only: no blind/, no veil, no held-out set read.
