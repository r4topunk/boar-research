# PR note: SOURCEGROUP (deps.groupSources), for the wiring PR after 10-20

Patch: arms/sourcegroup/tools/sourcegroup.patch, sha256 c274ab6c…cf06, against wt/pr1 8ac9eb7a. It touches src/routing/{sourceGroups.ts (new), sourceGroups.test.ts (new), answer.ts, events.ts, answerReducer.ts, answer.test.ts}.

## Commit paragraph
routing: group the final answer's sources by page (deps.groupSources, off by default)

Retrieval numbers sources per passage, so one page often shows up two or three times in the sources card ("Choking" ×3). This happened in 36–50 % of answers with sources on the cut 7 paths and in 90 % once neighbour chunks are appended (PHONEFAIL failure 4). The new src/routing/sourceGroups.ts groups the final sources by page: the URL in the source label, else the title. Groups are numbered by first appearance in the source list. Every [n] in the answer is rewritten to its group's number ([1][3] → [1][2]; [1][2] of one page → [1]), and each group keeps its passages. Nothing else in the text changes. When no page repeats, the text is untouched. With deps.groupSources = true, done and the result carry sourceGroups, and cited and finalText use the group numbers. The receipt adds sources:grouped:<before>-><after> when a page repeats. The sources event and result.sources stay per passage, so deepen() still gets every passage. Default off: the output is byte-identical to before.

## Renderer contract
- `done.sourceGroups` absent: as today. [n] and cited index the last `sources` event (one entry per passage).
- `done.sourceGroups` present: [n] in `finalText` (or the streamed text when there is no finalText) and `cited` index `sourceGroups[n-1]`. Draw one chip per group. `group.n` = its number. `title`, `source` and `docId` come from the page. `similarity` and `relevance` = the best of its passages.
- Chip-per-passage view: `group.passages[]` holds the full chunks in source-list order, with `sourceIndex` = the 0-based place in the sources event (body, chunkId, similarity).
- Android bridge (answerBridge.ts:224): `citations` = `d.sourceGroups` when present. SourceFootnotes.tsx draws `group.title`, the count badge = groups.length, and the expand lists `group.passages` bodies. The reducer keeps `state.sourceGroups`.
- Never mix: grouped [n] with the per-passage `sources` list mislabels chips. Turn on the flag only with the renderer change. The eval adapter (trace.ts, cited → titles) also needs it before an ON run.

## Native port spec (android-native, then boar-ios via the goldens)
1. Port sourceGroups.ts as a pure function (e.g. engine/answer/SourceGroups.kt). The page key = the first `https?://` URL in Chunk.source, else `title.trim()` with spaces collapsed and lowercased. Groups are numbered by first appearance in the source list.
2. Apply it once after the answer is final, after CT-1 / cleanCitations and before the UI copy: in ChatViewModel.kt:310, where `shown = sources.map { Source(...) }`. Rewrite each in-range [k] to [map[k]], collapse adjacent repeats, and leave out-of-range markers.
3. ChatScreen.kt:410 `cleanCitations(text, m.sources.size)` must get the group count once the text is renumbered. Otherwise markers past the old passage count survive, or valid ones get dropped.
4. Persist the groups (metaOf/sourcesFromMeta, ChatViewModel.kt:420-427) with their passages, so a reopened chat keeps the same numbers. SourceFootnotes(m.sources) then draws one chip per page.
5. Parity: add the 11 TS cases as goldens (URL dedupe, title fallback, [1][3] → [1][2], [1][2] → [1], no-citation and no-repeat identity, excerpt mapping, multi-pass). The native X6 run had duplicates in 19/38 answers with sources, and the post-hoc replay is clean (arms/sourcegroup/aggregates/sourcegroup-replay.json).
