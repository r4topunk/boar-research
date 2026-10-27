# REPACK16 criterion (frozen 2026-10-21, before any repack, replay or device step)

Question: does repacking the knowledge-pack zstd blocks from 64 KB to 16 KB (articles never split) cut decoded bytes per pack search by at least half on the desktop replay, with identical retrieval, at an acceptable size cost? 0 LLM, 0 judge, 0 paid; boar-app/ and bench-app/engine untouched (scratch tree only); no publish.

## Packs (built before measuring)
- Builder fact (mini, kiln/packs/builder-cf/scripts/build-wiki-pack.mjs): `--block-kb N` already exists (default 64); `add()` appends each article (UTF-8) to the open block in article-id order and `flushBlock()` closes it once blockLen >= N*1024 (zstd level `--zlevel`, default 12). No builder change is needed.
- Repack = tools/repack.mjs: copy of an existing pack file; `blocks` and `articles(block_id, off, len)` rewritten with exactly that rule (same article order, same level 12, node:zlib zstd) and every other table untouched; VACUUM. A full builder rebuild from the dump would also change article text (convert-fix lib, dump date) and embeddings, so it cannot isolate block size.
- Tool check (must pass before any replay, else stop and fix): repack at N = 64 reproduces the original `articles(block_id, off, len)` for 100 % of articles and the decompressed text of every article byte-identical at 16/32/64.
- Inputs: wikivoyage = A-union file ff8595e3 (persona-a-union); simplewiki = r2 candidate e14bdff1 (candidates/boar-simplewiki-en-convfix). Outputs to scratch dirs, never over the originals; device-day kit dirs untouched.

## Replay (MacBook, boar-eval replay-retrieval.sh, --gate rules)
- Tree: scratch copy of bench-app/engine (parsearch 8ad2c4b0) + arms/blockcache/tools/blockcache-instrument.patch (BOAR_BLOCK_CACHE slots per pack; each miss logged with pack, block id, decompressed bytes; a marker per searchWikiPacks call).
- Kit A (primary, the device kit): the 6 A-union files, wikivoyage at 64 (original) / 32 / 16 KB, the other 5 unchanged. Kit A+SW (secondary, for simplewiki): kit A + simplewiki r2, wikivoyage and simplewiki both at 64 / 32 / 16.
- Orders: S = aunion73-a request order (73 incl. warmup); M = MAIN 97 in the order of gemma4-e2b-vs4b-K0-main-s42 requests. One process per (kit, order, block size, cache), cache = 16 and 64 slots per pack.
- Decoded bytes per search = sum of logged miss bytes / number of search markers, whole session (cold start included).

## Decision (all clauses)
- ADOPT-FOR-DEVICE-A/B iff:
  1. Kit A, cache 64: decoded bytes per search at 16 KB <= 0.50 x the 64 KB run, in BOTH S and M;
  2. Parity: for every kit, order and cache, the 16 KB and 32 KB runs have ordered raw lists (title, section, source) and kept `sources` identical to the 64 KB run for 100 % of items;
  3. Size: each repacked 16 KB file <= 1.08 x its 64 KB original (bytes on disk after VACUUM).
- Else KILL.
- Descriptive only (no decision): cache 16, 32 KB, memory-equal slots (256 at 16 KB), peak held bytes, MacBook fzstd decode time per search (the logged miss sequences replayed through fzstd 0.1.1, median of 5 reps).

## If ADOPT
Arm F on DEVICE-DAY-2026-10-22: blockcache64 APK (arm E, no new APK) + the 16 KB wikivoyage in a separate kit dir; prediction written before the device run from the replay of the e1par order. The device adopt rule is arm F's own, frozen in the runsheet.
