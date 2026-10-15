# T-K2 — new pack source codes + per-row attribution (2026-10-12)
Worktree `wt/packs` @ 979187fa (dt512), uncommitted. Patch `packs-sources.vs-dt512.patch` (sha256 in `.sha256`, 6 files, +211/−19). `wt/packs/node_modules` is a symlink to packcond's (gitignored, not in the patch).

## What changed (file:line in wt/packs)
- `scripts/build-wiki-pack.mjs:79-83` SOURCE map appends `stackexchange 9, medlineplus 10, factbook 11, simplewiki 12` (0–8 unchanged). `:202-218` `addMeta(id,url,license,attribution)`: 3-column `article_meta` as before; on the first row with attribution, `ALTER TABLE article_meta ADD COLUMN attribution TEXT` (works whatever the row order). `:296/:300` row → `addMeta` also when only `attribution` is set. `:22-23, :46-50` header + usage document the JSONL fields. Right builder confirmed: fetch-* JSONL → `build-wiki-pack.mjs --shards *.jsonl` (local-inventory §3).
- `src/rag/wikiPack.ts:35-37` `PackSource` +4; `:113-127` `SOURCES` (now exported) +4 at ids 9–12, `NOT_NAME_SOURCES = {enwiki, enwikivoyage, stackexchange}`; `:57-58, :82-83` `attribution?` on `Article`/`PackHit`; `:457-459` ctor flag `hasAttribution`; `:480-486` topicSources filter + one `PRAGMA table_info(article_meta)` at open; `:533-546` article() selects `attribution` only when the column exists; `:625` hit carries it.
- `src/rag/packs.ts:184-187` SOURCE_LABEL ("Stack Exchange", "MedlinePlus", "CIA World Factbook (archive)", "Simple English Wikipedia"); `:207-211` simplewiki → simple.wikipedia.org; `:223-224` citation = `${label} — ${url}${license ? ` (${license})` : ""}${attribution ? ` — ${attribution}` : ""}`.
- `src/rag/passages.types.ts:6-8, :28` + `passages.ts:61`: tsc required `PassageSourceKind` to include the 4 codes (passage path takes `h.source`); `attribution?` passed through there too.
- Topic sources (point 3): stackexchange titles are question sentences, not entity names → excluded from `topicSources` (still found by BM25); factbook/medlineplus/simplewiki count as names. Comment at wikiPack.ts:119-127.

## JSONL field (builder input, one doc per line)
`"attribution": "<author> (<profile url>), <question url>"` (free text, optional), next to `"source": "stackexchange"`, `"url"`, `"license": "CC BY-SA 4.0"` (2.5/3.0/4.0 by post date). Absent/empty → no column, citation unchanged.

## Tests
- New `src/rag/wikiPack.attribution.test.ts` (9 tests): ids 0–8 stable + 9–12 appended; articleUrl/labels for the 4 codes; packHitToChunk byte-identical without attribution, credit appended with it; builder fixture (factbook first, then SE with attribution → ALTER path) has 4 columns, same rows without attribution → 3 columns; WikiPack round-trips sources, topicSources = {factbook, medlineplus, simplewiki}; SE hit carries attribution into the citation; column-less pack gives the same hits minus attribution.
- `npx vitest run src/rag`: 31 files / 214 tests pass (baseline 979187fa: 30/205 + the new file). `scripts/lib`: 10/68 pass. `npx tsc --noEmit`: clean.
- Full `npx vitest run`: 1319 pass, 2 fail (`routing/answer.test.ts` deep tier verifier, `routing/depth.test.ts` deep one-pass) — the same 2 fail on clean 979187fa (pre-existing, dt512 deep-tier tests), not this patch.

## Differential (0 LLM calls)
- Shipped packs `boar-crypto.sqlite` + `boar-wikivoyage-en.sqlite` opened with node:sqlite + fzstd through 979187fa's and the patched `WikiPack`/`packHitToChunk` (vitest harness in scratchpad): 5 public v0.1 queries (vit-cry-002/005/007, vit-trv-003, trv-002) × 2 packs → 41 hits, `JSON.stringify(hits)` identical and titles/sections/scores/source strings identical; topicSources identical.
- Builder: same 3-doc JSONL (eips + enwiki + appropedia) built with the 979187fa and patched builders → `sqlite3 .dump` identical except builtAt/buildSeconds.

## Maintainer PR (at the end, to the upstream maintainer)
The 6 files of the patch as one commit: builder SOURCE ids 9–12 + optional `attribution` column, engine SOURCES/labels/URL host/topicSources rule, citation suffix, passage kind types, the new test file. Not included / open: whether `medlineplus` joins `LAY_SOURCES` (changes ranking: needs its own arm); the UI shows `source` as-is, so no UI change is needed.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
