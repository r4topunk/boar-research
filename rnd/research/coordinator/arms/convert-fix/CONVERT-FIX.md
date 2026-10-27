# CONVERT-FIX: simplewiki converter drops {{convert}} values, 2026-10-21

TL;DR: the pack builder's shared template stripper (`wiki-pack-lib.mjs`, `renderTemplate`) returns "" for every non-listing template, so `{{convert|N|unit|..}}` loses its number AND unit. Fix = 17 lines; test rebuild on the mini (935 s build, 0 LLM) restores the values. Nothing in the published pack files, boar-app or any kit was changed.

## 1. Damage (0 LLM; scans in `tools/out/`)
| pack | converter | chunks scanned | chunks with artefact (`stretches .`, `is|was|measures|about|of .`) | broad regex (+ long/tall/high/wide/deep `.`) |
|---|---|---|---|---|
| boar-simplewiki-en (published) | shared lib (cleanWikivoyage) | 621,682 | **3,176** (2,826 articles) | 4,432 |
| boar-wikivoyage-en (published) | shared lib | 548,051 | 877 (717 articles) | 2,180 |
| boar-factbook | convert.mjs factbook (structured JSON) | 10,543 | 0 | 0 |
| boar-wiki-en-top100k (every 10th article, 405,919 chunks) | FineWiki HTML text (templates already rendered) | | 0 | 5 |
| boar-wiki-en-07 | same FineWiki source as top100k, not scanned | | n/a | n/a |
- Dump `simplewiki-20261001-pages-articles-multistream.xml.bz2` was NOT on disk; re-downloaded on the mini (388 MB, sha1 8a12322b... = card). Source counts (`tools/out/dump-count.json`): 285,478 ns-0 non-redirect pages, **13,006 with {{convert|cvt}}**, 47,615 templates.
- Converter output control (unpatched lib, reproduces the pack: 208,628 rows) vs patched: **8,074 articles change**, +89 rows (bodies that were < 200 chars now pass), articles with the artefact regex 3,869 -> 779 (the rest are other dropped templates: dates, coordinates, ...).
- **Converter shared?** Yes for simplewiki + Wikivoyage (both call `cleanWikivoyage`). Wikivoyage candidate v2 (WIKIVOYAGE-REBUILD) already has a convert rule inside a 76-template whitelist; this patch is the minimal convert-only subset. enwiki packs (FineWiki HTML) and factbook are not affected. wiki-vital5 not scanned (schema mismatch in the scan script, enwiki-derived).

## 2. Fix
- `tools/convert-fix.patch` (sha256 65430d07bfeb5012c490648d74a4ec0d214bdafd0e39123de8f83ce8b1608a48; `patch -p1` in a builder tree, base lib md5 04776e53...): `renderTemplate` -> for `convert`/`cvt` emits first value + connectors (`to`, `-`, `and`, `x`...) + first unit; named params (`abbr=on`, `sigfig=5`, `disp=..`) skipped; nested templates cleaned; unit map c/f -> °C/°F, km2 -> km², mi2/sqmi -> sq mi, m2/m3, acre -> acres. Everything else still drops.
- Output form: `{{convert|21196.18|km|mi}}` -> `21196.18 km` (no second unit, no brackets).
- Not done: units rendered as the dump spells them (`mi2` mapped, `NM`, `Gm`, `mSv/yr` verbatim); two-unit forms like `|km mi` keep only the first.

## 3. Tests
`tools/convert-fix.test.mjs` (`node --test`; `LIB=<dir>` picks the lib): 10 strings taken verbatim from the dump (ranges `3|to|12|m`, `3|-|6|cm`, `abbr=off|251,826|mi2` with a leading named param, `2,220,930|km2|sqmi|abbr=on|sigfig=5`, `40.5|C|F`, `-52.6|C|F`, `30|km/s|mi/s|abbr=on|lk=on`, newline after the pipe, ...) + 1 "other templates still drop": **11/11 on the patched lib, 1/11 on the original.**

## 4. Test rebuild (scratch, mini)
- `tools/rebuild.sh` (resumable; control convert 60 s, patched convert 60 s, build): **build wall 935 s (15.6 min, <= 30)**, embeddings local Metal, disk stayed 26-27 GiB (floor 25, `--min-free-gb 25`), 0 LLM, no Docker/ollama/:8094 touched.
- Candidate: mini `<runner>/kiln/packs/work/convert-fix/work/boar-simplewiki-en.sqlite` (+ .json), **481,017,856 B (+483,328 B, +0.10 %), sha256 e14bdff1a56dabb2df8ef0ce0c817467f856473febbc0bf9c1d2021b2b68b14b**; format ok, integrity_check ok; articles 208,711 (+89), chunks 621,906 (+224), indexed 586,503, textBytes 343,995,937 (+0.05 %). Published: 480,534,528 B, sha c751768b...
- Artefact chunks **3,176 -> 524** (-84 %), articles 2,826 -> 518. Remaining ones are other dropped templates (not touched).
- **lan-rsn-001: Great Wall chunk now reads "In total, the wall stretches 21196.18 km."** (was "stretches ."). Also Everest "about 8848 m high", Afghanistan "around 251,826 sq mi", Austria "was 40.5 °C".
- Caveats: the candidate differs from the published pack only by this fix plus a post-10-13 lib (not isolated at chunk level; article-level diff vs control is clean: `tools/out/diff-convert.json`). Not swapped into any kit; not published (publishing needs its own QUEUE row). No retrieval replay / judge run: UNKNOWN whether answers move beyond lan-rsn-001.

## 5. Next (coordinator)
- To publish: copy the candidate to `shared-data/packs/wave2/`, update the pack card (sizes, sha, counts) and re-run the self-test; repeat for Wikivoyage with candidate v2 (already contains the same rule) if desired.
- Rebuild command: `bash tools/rebuild.sh` on the mini (after copying `convert-fix.patch` and the script to `<runner>/kiln/packs/work/convert-fix/`).
